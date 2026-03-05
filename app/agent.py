"""
Agentic trip planner: parses user message, runs tools (flights, hotels, attractions, budget), and returns a structured plan.
"""

import json
import os
from openai import OpenAI

from app.tools import (
    search_flight_deals,
    search_hotels,
    get_attractions,
    estimate_trip_expenses,
)
from app.models import (
    PlanResponse,
    FlightDeal,
    HotelOption,
    Spot,
    ExpenseBreakdown,
)


SYSTEM_PROMPT = """You are a trip-planning assistant. Given a user message about a trip, you must output a single JSON object with exactly these keys (no other text):
- destination: string (e.g. "Norway", "Oslo")
- travelers: integer (number of people, including the user; default 1)
- days: integer (trip length in days; default 7)
- origin: string (departure city/country if mentioned, else "Unknown")
- interests: string or null (e.g. "nature, fjords, family")

Extract from natural language. Examples:
- "plan my Norway trip with my family of 3" -> destination: "Norway", travelers: 3, days: 7
- "5 days in Oslo with 2 kids" -> destination: "Oslo", travelers: 4, days: 5
Reply with ONLY the JSON object, no markdown or explanation."""


def _extract_params(message: str) -> dict:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        temperature=0,
    )
    text = (resp.choices[0].message.content or "").strip()
    # Remove markdown code block if present
    if text.startswith("```"):
        lines = text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = {}
    return {
        "destination": data.get("destination") or "Norway",
        "travelers": max(1, int(data.get("travelers", 1))),
        "days": max(1, int(data.get("days", 7))),
        "origin": data.get("origin") or "Unknown",
        "interests": data.get("interests"),
    }


def _build_plan_response(
    params: dict,
    flight_result: dict,
    hotel_result: dict,
    attractions_result: dict,
    budget_result: dict,
    summary_and_itinerary: str,
) -> PlanResponse:
    """Turn tool results and optional LLM summary into PlanResponse."""
    travelers = params["travelers"]
    days = params["days"]
    destination = params["destination"]

    # Parse summary and itinerary from LLM (format: "Summary: ... Itinerary: ..." or just one block)
    summary = f"{days}-day trip to {destination} for {travelers} traveler(s)."
    itinerary_summary = attractions_result.get("suggested_itinerary_outline") or []

    if summary_and_itinerary:
        lower = summary_and_itinerary.lower()
        if "summary:" in lower:
            parts = summary_and_itinerary.split("Summary:", 1)[-1].split("Itinerary:", 1)
            summary = (parts[0].strip() or summary).strip()
            if len(parts) > 1 and parts[1].strip():
                itinerary_summary = [p.strip() for p in parts[1].strip().split("\n") if p.strip()]
        else:
            summary = summary_and_itinerary.strip() or summary

    flight_deals = [
        FlightDeal(
            airline=d.get("airline", ""),
            outbound=d.get("outbound", ""),
            return_leg=d.get("return"),
            stops=d.get("stops", ""),
            price_per_person_usd=float(d.get("price_per_person_usd", 0)),
            total_usd=float(d.get("total_usd", 0)),
            note=d.get("note"),
        )
        for d in flight_result.get("flight_deals", [])
    ]
    hotels = [
        HotelOption(
            name=h.get("name", ""),
            location=h.get("location", ""),
            rating=float(h.get("rating", 0)),
            price_per_night_usd=float(h.get("price_per_night_usd", 0)),
            total_usd=float(h.get("total_usd", 0)),
            room_type=h.get("room_type", ""),
            family_friendly=h.get("family_friendly", True),
            highlights=h.get("highlights"),
        )
        for h in hotel_result.get("hotels", [])
    ]
    spots = [
        Spot(
            name=s.get("name", ""),
            location=s.get("location", ""),
            type=s.get("type", ""),
            best_for=s.get("best_for", ""),
            suggested_duration=s.get("suggested_duration", ""),
            tip=s.get("tip"),
        )
        for s in attractions_result.get("spots", [])
    ]
    b = budget_result.get("breakdown", {})
    expense_breakdown = ExpenseBreakdown(
        flights_usd=float(b.get("flights_usd", 0)),
        accommodation_usd=float(b.get("accommodation_usd", 0)),
        daily_spending_usd=float(b.get("daily_spending_usd", 0)),
        daily_per_person_usd=float(b.get("daily_per_person_usd", 0)),
        note=b.get("note"),
    )

    return PlanResponse(
        summary=summary,
        destination=destination,
        travelers=travelers,
        days=days,
        itinerary_summary=itinerary_summary,
        flight_deals=flight_deals,
        hotels=hotels,
        spots=spots,
        expense_estimate_usd=float(budget_result.get("total_estimate_usd", 0)),
        expense_breakdown=expense_breakdown,
        raw_agent_message=summary_and_itinerary or None,
    )


def plan_trip(message: str) -> PlanResponse:
    """
    Run the agent: extract params from message, call all tools, then build and return a structured plan.
    """
    params = _extract_params(message)
    destination = params["destination"]
    travelers = params["travelers"]
    days = params["days"]
    nights = max(0, days - 1)
    origin = params["origin"]
    interests = params.get("interests")

    # 1) Flights
    flight_result = search_flight_deals(
        origin=origin,
        destination=destination,
        travelers=travelers,
        trip_days=days,
    )
    best_flight_total = None
    for d in flight_result.get("flight_deals", []):
        t = d.get("total_usd")
        if t is not None and (best_flight_total is None or t < best_flight_total):
            best_flight_total = t
    if best_flight_total is None:
        best_flight_total = 0.0

    # 2) Hotels
    hotel_result = search_hotels(
        destination=destination,
        travelers=travelers,
        nights=nights,
        family_friendly=True,
    )
    best_hotel_total = None
    for h in hotel_result.get("hotels", []):
        t = h.get("total_usd")
        if t is not None and (best_hotel_total is None or t < best_hotel_total):
            best_hotel_total = t
    if best_hotel_total is None:
        best_hotel_total = 0.0

    # 3) Attractions
    attractions_result = get_attractions(
        destination=destination,
        interests=interests,
        days=days,
    )

    # 4) Budget
    budget_result = estimate_trip_expenses(
        travelers=travelers,
        nights=nights,
        destination=destination,
        flight_total_usd=best_flight_total,
        hotel_total_usd=best_hotel_total,
        daily_per_person_usd=140 if "norway" in destination.lower() else 120,
    )

    # 5) Optional: one LLM call to write a short summary and itinerary text
    summary_and_itinerary = ""
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        client = OpenAI(api_key=api_key)
        model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        prompt = f"""The user asked: "{message}"

We have prepared a trip plan with:
- Destination: {destination}, {travelers} travelers, {days} days.
- Flight deals: {json.dumps(flight_result.get('flight_deals', [])[:2])}
- Hotels: {json.dumps(hotel_result.get('hotels', [])[:2])}
- Spots: {[s.get('name') for s in attractions_result.get('spots', [])]}
- Total estimate: {budget_result.get('total_estimate_usd')} USD.

Write a short, friendly paragraph (2–4 sentences) as "Summary:" and then "Itinerary:" with a bullet or line-per-day outline. Keep it concise."""

        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            summary_and_itinerary = (resp.choices[0].message.content or "").strip()
        except Exception:
            pass

    return _build_plan_response(
        params,
        flight_result,
        hotel_result,
        attractions_result,
        budget_result,
        summary_and_itinerary,
    )

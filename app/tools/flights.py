"""
Flight deals tool backed by FlightsAPI (Google Flights).

Uses FlightsAPI for live prices when FLIGHTSAPI_API_KEY is set.
If configuration is missing or the API call fails, this function
returns an empty list of deals instead of fabricating prices.
"""

from __future__ import annotations

import datetime as _dt
import os
from typing import Any

import requests


FLIGHTS_API_ONE_WAY_URL = "https://api.flightsapi.io/flights/one-way"


def _normalize_airport_code(value: str | None) -> str | None:
    if not value:
        return None
    code = value.strip().upper()
    if len(code) != 3 or not code.isalpha():
        return None
    return code


def _call_flightsapi(
    origin_code: str,
    destination_code: str,
    travelers: int,
    api_key: str,
) -> list[dict[str, Any]]:
    """Call FlightsAPI one-way endpoint and return normalized deals."""
    today = _dt.date.today()
    # Simple heuristic: search roughly one week from today
    departure_date = today + _dt.timedelta(days=7)

    params = {
        "departure_airport": origin_code,
        "arrival_airport": destination_code,
        "departure_date": departure_date.strftime("%d-%m-%Y"),
        "stops": 0,
    }
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        resp = requests.get(
            FLIGHTS_API_ONE_WAY_URL,
            params=params,
            headers=headers,
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return []

    # FlightsAPI examples show a top-level JSON array; handle both array and {"data": [...]}.
    if isinstance(data, list):
        items = data
    else:
        items = data.get("data") or []

    deals: list[dict[str, Any]] = []
    for item in items[:5]:
        try:
            one_way_price = float(item.get("bestPrice") or item.get("price") or 0)
        except (TypeError, ValueError):
            one_way_price = 0
        if one_way_price <= 0:
            continue

        dep = item.get("departureAirport") or {}
        arr = item.get("arrivalAirport") or {}

        deals.append(
            {
                "airline": item.get("airline") or "Unknown",
                "outbound": f"{origin_code} → {destination_code} on {dep.get('date')} {dep.get('time')}",
                "return": None,
                "stops": "Unknown",
                "price_per_person_usd": one_way_price,
                "total_usd": one_way_price * max(1, travelers),
                "travelers": max(1, travelers),
                "note": "One-way live price from FlightsAPI (no return segment included).",
            }
        )

    return deals


def search_flight_deals(
    origin: str,
    destination: str,
    travelers: int,
    trip_days: int,
) -> dict[str, Any]:
    """Search for flight deals using FlightsAPI.

    NOTE: This expects origin and destination as IATA airport codes (e.g. 'LAX', 'JFK').
    If the configuration is missing or parameters are invalid, an empty list of deals
    is returned instead of mocked prices.
    """
    api_key = os.environ.get("FLIGHTSAPI_API_KEY")
    origin_code = _normalize_airport_code(origin)
    destination_code = _normalize_airport_code(destination)

    if not api_key or not origin_code or not destination_code:
        return {
            "destination_city": destination,
            "origin": origin,
            "travelers": travelers,
            "trip_days": trip_days,
            "flight_deals": [],
            "currency": "USD",
            "source": "none",
            "message": "Live flight prices unavailable: ensure FLIGHTSAPI_API_KEY is set and origin/destination are IATA airport codes.",
        }

    deals = _call_flightsapi(origin_code, destination_code, travelers, api_key)

    return {
        "destination_city": destination_code,
        "origin": origin_code,
        "travelers": travelers,
        "trip_days": trip_days,
        "flight_deals": deals,
        "currency": "USD",
        "source": "flightsapi",
    }

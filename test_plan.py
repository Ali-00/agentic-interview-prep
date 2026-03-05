"""
Test script for the Trip Planner API.
Run the server first: uvicorn app.main:app --reload
Then run: python test_plan.py
"""

import requests
import json

BASE = "http://127.0.0.1:8000"


def test_plan_trip(message: str) -> None:
    print("Request:", message)
    print("-" * 60)
    r = requests.post(
        f"{BASE}/plan-trip",
        json={"message": message},
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    print("Summary:", data.get("summary", ""))
    print("Destination:", data.get("destination"), "| Travelers:", data.get("travelers"), "| Days:", data.get("days"))
    print("\nItinerary:")
    for line in data.get("itinerary_summary", []):
        print(" ", line)
    print("\nFlight deals:", len(data.get("flight_deals", [])))
    for f in data.get("flight_deals", [])[:2]:
        print(f"  - {f.get('airline')}: {f.get('total_usd')} USD total")
    print("\nHotels:", len(data.get("hotels", [])))
    for h in data.get("hotels", [])[:2]:
        print(f"  - {h.get('name')} ({h.get('location')}): {h.get('total_usd')} USD")
    print("\nSpots:", len(data.get("spots", [])))
    for s in data.get("spots", [])[:3]:
        print(f"  - {s.get('name')} ({s.get('suggested_duration')})")
    b = data.get("expense_breakdown") or {}
    print("\nExpense estimate:", data.get("expense_estimate_usd"), "USD")
    print("  Flights:", b.get("flights_usd"), "| Hotels:", b.get("accommodation_usd"), "| Daily:", b.get("daily_spending_usd"))
    print("-" * 60)


if __name__ == "__main__":
    try:
        # Health check
        r = requests.get(BASE, timeout=5)
        r.raise_for_status()
    except requests.RequestException as e:
        print("Server not running. Start it with: uvicorn app.main:app --reload")
        print("Error:", e)
        exit(1)

    test_plan_trip(
        "Plan my Norway trip with my family consisting of 3 persons including me. "
        "We have 7 days and want nature and fjords."
    )

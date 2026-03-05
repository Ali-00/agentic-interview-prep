"""
Budget and expense estimation tool.
"""


def estimate_trip_expenses(
    travelers: int,
    nights: int,
    destination: str,
    flight_total_usd: float | None = None,
    hotel_total_usd: float | None = None,
    daily_per_person_usd: float = 120,
) -> dict:
    """Estimate total trip cost from flights, hotels, and daily spending.

    Args:
        travelers: Number of people.
        nights: Number of nights (days - 1 for one city, or as planned).
        destination: For context (e.g. Norway = higher daily cost).
        flight_total_usd: Total flight cost if already known; else estimated.
        hotel_total_usd: Total hotel cost if already known; else estimated.
        daily_per_person_usd: Food, activities, transport per person per day (default 120 USD).

    Returns:
        Dict with breakdown and total in USD.
    """
    dest = (destination or "").strip().lower()
    # Norway is expensive
    if "norway" in dest or dest in ("oslo", "bergen"):
        daily_per_person_usd = max(daily_per_person_usd, 140)

    days = nights + 1
    daily_total = daily_per_person_usd * travelers * days

    # Do not fabricate flight or hotel prices; treat missing values as zero.
    flight_total = float(flight_total_usd or 0)
    hotel_total = float(hotel_total_usd or 0)

    total = flight_total + hotel_total + daily_total

    return {
        "travelers": travelers,
        "nights": nights,
        "days": days,
        "destination": destination or "Unknown",
        "breakdown": {
            "flights_usd": round(flight_total, 2),
            "accommodation_usd": round(hotel_total, 2),
            "daily_spending_usd": round(daily_total, 2),
            "daily_per_person_usd": daily_per_person_usd,
            "note": "Daily = food, activities, local transport, small extras. Flights or hotels may be 0 if no live prices were available.",
        },
        "total_estimate_usd": round(total, 2),
        "currency": "USD",
    }

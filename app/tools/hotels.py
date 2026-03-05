"""
Hotel search tool. Replace with real API (Booking.com, Expedia, etc.) when ready.
"""


def search_hotels(
    destination: str,
    travelers: int,
    nights: int,
    family_friendly: bool = True,
) -> dict:
    """Search for hotels suited to the group size and trip length.

    Args:
        destination: City or region (e.g. 'Oslo', 'Bergen', 'Norway').
        travelers: Number of guests.
        nights: Number of nights (trip_days - 1 or split across cities).
        family_friendly: Prefer family-friendly options.

    Returns:
        Dict with hotels list and metadata.
    """
    dest = (destination or "Norway").strip()
    if dest.lower() in ("norway", "norway."):
        dest = "Oslo / Bergen"

    # Mock options: mix of Oslo and Bergen for a Norway trip
    hotels = [
        {
            "name": "Thon Hotel Opera",
            "location": "Oslo",
            "rating": 4.2,
            "price_per_night_usd": 145,
            "total_nights": nights,
            "total_usd": 145 * nights,
            "room_type": "Family room (2+2)",
            "family_friendly": True,
            "highlights": "Central, breakfast included, near opera house",
        },
        {
            "name": "Clarion Hotel Bergen",
            "location": "Bergen",
            "rating": 4.4,
            "price_per_night_usd": 165,
            "total_nights": nights,
            "total_usd": 165 * nights,
            "room_type": "Connecting rooms",
            "family_friendly": True,
            "highlights": "Harbour view, buffet breakfast, Bryggen nearby",
        },
        {
            "name": "Scandic Vulkan",
            "location": "Oslo",
            "rating": 4.0,
            "price_per_night_usd": 125,
            "total_nights": nights,
            "total_usd": 125 * nights,
            "room_type": "Family room",
            "family_friendly": True,
            "highlights": "Good value, kitchenette option, trendy area",
        },
    ]

    return {
        "destination": dest,
        "travelers": travelers,
        "nights": nights,
        "family_friendly": family_friendly,
        "hotels": hotels,
        "currency": "USD",
        "message": "Replace with Booking.com or similar API for real availability and prices.",
    }

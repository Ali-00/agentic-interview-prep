"""
Attractions and spots tool. Replace with Google Places, Tripadvisor, or tourism APIs when ready.
"""


def get_attractions(
    destination: str,
    interests: str | None = None,
    days: int = 7,
) -> dict:
    """Get top spots and activities for the destination.

    Args:
        destination: Country, region, or city (e.g. 'Norway', 'Oslo', 'Bergen').
        interests: Optional comma-separated interests (e.g. 'nature, fjords, family').
        days: Number of days to spread suggestions over.

    Returns:
        Dict with spots list and suggested day-by-day outline.
    """
    dest = (destination or "Norway").strip().lower()
    is_norway = "norway" in dest or dest in ("oslo", "bergen", "norway")

    if is_norway:
        spots = [
            {
                "name": "Norwegian Fjords (e.g. Nærøyfjord)",
                "location": "Western Norway",
                "type": "Nature / cruise",
                "best_for": "Family, nature",
                "suggested_duration": "Full day",
                "tip": "Book a fjord cruise from Flåm or Gudvangen",
            },
            {
                "name": "Flåm Railway",
                "location": "Flåm",
                "type": "Scenic train",
                "best_for": "Family, views",
                "suggested_duration": "Half day",
                "tip": "One of the world's most beautiful train journeys",
            },
            {
                "name": "Bryggen",
                "location": "Bergen",
                "type": "Culture / UNESCO",
                "best_for": "All ages",
                "suggested_duration": "2–3 hours",
                "tip": "Colorful wharf, museums, cafés",
            },
            {
                "name": "Vigeland Park",
                "location": "Oslo",
                "type": "Park / sculpture",
                "best_for": "Family, walking",
                "suggested_duration": "2–3 hours",
                "tip": "Free, iconic sculptures, picnic-friendly",
            },
            {
                "name": "Viking Ship Museum",
                "location": "Oslo",
                "type": "Museum",
                "best_for": "Family, history",
                "suggested_duration": "2 hours",
                "tip": "Closed for renovation until 2026 – check before visiting",
            },
            {
                "name": "Trolltunga or Preikestolen",
                "location": "Western Norway",
                "type": "Hiking / viewpoint",
                "best_for": "Active families (older kids)",
                "suggested_duration": "Full day",
                "tip": "Preikestolen is easier; Trolltunga is long and demanding",
            },
        ]
        suggested_outline = [
            "Day 1–2: Oslo (Vigeland, harbour, museums).",
            "Day 3: Train Oslo–Bergen or to Flåm.",
            "Day 4–5: Fjords (cruise, Flåm Railway).",
            "Day 6: Bergen (Bryggen, fish market, funicular).",
            "Day 7: Buffer / return travel.",
        ]
    else:
        spots = [
            {
                "name": "Main attractions",
                "location": destination,
                "type": "Various",
                "best_for": "All",
                "suggested_duration": "As needed",
                "tip": "Customize with a local tourism API.",
            },
        ]
        suggested_outline = [f"Day 1–{days}: Explore {destination}."]

    return {
        "destination": destination,
        "interests": interests,
        "days": days,
        "spots": spots,
        "suggested_itinerary_outline": suggested_outline,
        "message": "Replace with Google Places or tourism API for more spots and opening hours.",
    }

from pydantic import BaseModel, Field


class PlanRequest(BaseModel):
    """Single user message describing the trip they want."""

    message: str = Field(
        ...,
        description="Natural language request, e.g. 'Plan my Norway trip with my family of 3 for 7 days'",
        min_length=5,
    )


class FlightDeal(BaseModel):
    airline: str
    outbound: str
    return_leg: str | None = None
    stops: str
    price_per_person_usd: float
    total_usd: float
    note: str | None = None


class HotelOption(BaseModel):
    name: str
    location: str
    rating: float
    price_per_night_usd: float
    total_usd: float
    room_type: str
    family_friendly: bool = True
    highlights: str | None = None


class Spot(BaseModel):
    name: str
    location: str
    type: str
    best_for: str
    suggested_duration: str
    tip: str | None = None


class ExpenseBreakdown(BaseModel):
    flights_usd: float
    accommodation_usd: float
    daily_spending_usd: float
    daily_per_person_usd: float
    note: str | None = None


class PlanResponse(BaseModel):
    """Structured trip plan returned by the agent."""

    summary: str = Field(..., description="Short overview of the trip and who it's for")
    destination: str = Field(..., description="Main destination (e.g. Norway, Oslo)")
    travelers: int = Field(..., description="Number of people")
    days: int = Field(..., description="Trip length in days")
    itinerary_summary: list[str] = Field(default_factory=list, description="Day-by-day outline")
    flight_deals: list[FlightDeal] = Field(default_factory=list, description="Suggested flight options")
    hotels: list[HotelOption] = Field(default_factory=list, description="Suggested hotels")
    spots: list[Spot] = Field(default_factory=list, description="Recommended spots and activities")
    expense_estimate_usd: float = Field(..., description="Total estimated cost in USD")
    expense_breakdown: ExpenseBreakdown | None = Field(None, description="Cost breakdown")
    raw_agent_message: str | None = Field(None, description="Full narrative from the agent")

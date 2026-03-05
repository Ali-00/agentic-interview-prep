"""
Single endpoint: POST /plan-trip — user sends a message, agent returns a full trip plan.
"""

import os
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

from app.models import PlanRequest, PlanResponse
from app.agent import plan_trip

load_dotenv()

app = FastAPI(
    title="Agentic AI Trip Planner",
    description="Send a message like 'Plan my Norway trip with my family of 3' and get a full plan: itinerary, flight deals, hotels, spots, and expense estimate.",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "Agentic AI Trip Planner",
        "docs": "/docs",
        "plan_trip": "POST /plan-trip with body: {\"message\": \"Plan my Norway trip with my family of 3 for 7 days\"}",
    }


@app.post("/plan-trip", response_model=PlanResponse)
def create_plan(request: PlanRequest) -> PlanResponse:
    """
    Single endpoint: describe your trip in natural language and get a structured plan.

    - **Itinerary** — day-by-day outline and suggested spots
    - **Flight deals** — options with approximate prices (simulated; plug in Amadeus/Skyscanner for real data)
    - **Hotels** — family-friendly options (simulated; plug in Booking/Expedia for real data)
    - **Expense estimate** — total and breakdown (flights, accommodation, daily spending)
    """
    if not os.environ.get("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY is not set. Add it to .env to use the trip planner.",
        )
    try:
        return plan_trip(request.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trip planning failed: {str(e)}")

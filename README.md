# Agentic AI Trip Planner

A single-endpoint API where users describe their trip in natural language (e.g. *"Plan my Norway trip with my family of 3"*). An AI agent plans the itinerary, suggests spots, finds flight and hotel options, and estimates expenses.

## Quick start

1. Copy `.env.example` to `.env` and set:
   - `OPENAI_API_KEY` – your OpenAI key  
   - `FLIGHTSAPI_API_KEY` – your FlightsAPI key from `https://www.flightsapi.io/` (for live flight prices; optional but recommended)
2. Install and run:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

3. Open http://localhost:8000/docs and try:

**POST** `/plan-trip`  
Body (JSON):

```json
{
  "message": "Plan my Norway trip with my family consisting of 3 persons including me. We have 7 days and want nature and fjords."
}
```

You get back a structured trip plan: itinerary, flight deals, hotels, spots, and expense estimate.

## What the agent does

- **Understands** destination, number of travelers, duration, and preferences from your message.
- **Plans** day-by-day itinerary with suggested spots and activities.
- **Searches** flight deals (via external API) and family-friendly hotels.
- **Estimates** total cost (flights, hotels, activities, meals) for your group size.

## External providers

- **LLM & understanding:** OpenAI Chat Completions (config via `OPENAI_API_KEY`, `OPENAI_MODEL`)
- **Flights:** FlightsAPI (Google Flights data) via `FLIGHTSAPI_API_KEY` in `app/tools/flights.py`

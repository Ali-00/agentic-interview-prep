# Run the Agentic AI Trip Planner

1. **Create your env file**  
   Copy `.env.example` to `.env` and set your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-actual-key
   ```

2. **Install and run**  
   In this folder:
   ```bash
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

3. **Test**  
   - API docs: http://localhost:8000/docs  
   - POST `/plan-trip` with body: `{"message": "Plan my Norway trip with my family of 3 for 7 days"}`

That’s it. You can create `.env` and run on your own.

# InterviewPrepAI

InterviewPrepAI is a production-grade, agentic AI system that generates detailed, role-specific interview preparation study guides as PDF-ready documents.

## Features

- **Multi-agent architecture** orchestrated by a controller agent
- **Role- and experience-aware** topic planning and content depth
- **Resume and Job Description analysis** to derive a skill profile
- **Skill gap analysis** between user profile and role expectations
- **Topic planner** that creates a structured topic tree
- **Content generator** that produces deep explanations and example questions
- **Document formatter** that outputs Markdown and HTML suitable for PDF export
- **Optional PDF export** using `pdfkit`/`wkhtmltopdf`
- **Session memory** to refine study guides iteratively

## High-level Architecture

- `app/config.py` – configuration (API keys, model names, feature flags)
- `app/llm.py` – LLM client abstraction
- `app/models.py` – Pydantic models for inputs/outputs
- `app/agents/` – individual specialized agents
- `app/controller.py` – controller/orchestrator
- `app/api.py` – FastAPI app and HTTP endpoints

## Running the Service

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Ensure `wkhtmltopdf` is installed on your system if you want PDF export via `pdfkit`.
4. Set environment variables for your LLM provider (see `app/config.py`).
5. Start the API server:

```bash
uvicorn app.api:app --reload
```

## API Overview

The main endpoint is:

- `POST /generate-study-guide`

Request fields:

- `role` (string, required)
- `years_experience` (float, required)
- `resume` (file, optional)
- `job_description_text` (string, optional)
- `job_description_url` (string, optional)
- `study_plan_duration_days` (int, optional, e.g. 7, 14, 30)
- `session_id` (string, optional, to reuse context)

Response:

- Structured JSON containing:
  - Overview
  - Topic-wise deep dive
  - Skill gap and priority section
  - Optional study plan
  - Coverage checklist
  - Markdown and HTML suitable for PDF export
  - Optional generated PDF (base64) if requested

## Notes

- The LLM abstraction is intentionally simple so you can plug in OpenAI, Azure OpenAI, Anthropic, etc.
- For production, you can plug in your vector database and retrieval logic inside the `knowledge_base` hooks.


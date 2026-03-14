import os
from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "InterviewPrepAI"
    environment: str = os.getenv("ENVIRONMENT", "dev")

    # LLM / provider configuration
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4.1")
    llm_api_key: str | None = os.getenv("LLM_API_KEY")

    # PDF export
    enable_pdf_export: bool = os.getenv("ENABLE_PDF_EXPORT", "true").lower() == "true"

    # Session / memory
    enable_persistent_sessions: bool = (
        os.getenv("ENABLE_PERSISTENT_SESSIONS", "false").lower() == "true"
    )
    session_store_path: str = os.getenv(
        "SESSION_STORE_PATH", "data/session_store.json"
    )


settings = Settings()


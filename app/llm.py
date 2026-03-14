from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

from .config import settings


class LLMClient:
    """
    Simple LLM abstraction.

    This is intentionally minimal so you can swap in OpenAI, Azure OpenAI,
    Anthropic, or a self-hosted model behind a uniform interface.
    """

    def __init__(self) -> None:
        self.provider = settings.llm_provider
        self.model = settings.llm_model
        self.api_key = settings.llm_api_key

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        """
        Execute a chat completion call and return the model's reply text.

        For production you should:
        - Add retries, timeouts, logging, and error handling.
        - Implement provider-specific routing.
        """
        if not self.api_key:
            # Fallback stub for environments without an API key.
            # In production, raise an error instead.
            return "LLM API key not configured. Please configure LLM_API_KEY."

        # Example implementation placeholder for an OpenAI-compatible endpoint.
        # Adjust URL and payload structure for your provider.
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
        return data["choices"][0]["message"]["content"]


llm_client = LLMClient()


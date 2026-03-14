from __future__ import annotations

from typing import Optional

import httpx

from ..llm import llm_client
from ..models import RoleRequirements, UserInput


class JobDescriptionAnalyzerAgent:
    async def _fetch_jd_from_url(self, url: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                return resp.text[:10000]
        except Exception:
            return ""

    async def analyze(self, user_input: UserInput) -> RoleRequirements:
        """
        Analyze the job description (text and/or URL) to infer role requirements.
        """
        jd_text = user_input.job_description_text or ""
        if user_input.job_description_url and not jd_text:
            jd_text = await self._fetch_jd_from_url(str(user_input.job_description_url))

        base_prompt = (
            "You are an expert hiring manager.\n"
            "Given a target role, years of experience, and a job description (if provided),\n"
            "extract a structured view of the role requirements.\n\n"
            "Return STRICT JSON with keys:\n"
            "- seniority_level: string like 'junior', 'mid-level', 'senior', 'staff'\n"
            "- core_skills: list of core technical/behavioral skills\n"
            "- nice_to_have_skills: list\n"
            "- tools_and_tech: list of tools, frameworks, libraries, platforms\n"
            "- responsibilities: list of typical responsibilities\n"
            "- keywords: list of important words/phrases appearing in the JD\n"
            "- hidden_expectations: list of implicit expectations, soft skills, or signals\n"
        )

        jd_payload = {
            "role": user_input.role,
            "years_experience": user_input.years_experience,
            "job_description": jd_text[:8000],
        }

        messages = [
            {"role": "system", "content": base_prompt},
            {"role": "user", "content": f"JOB_INFO:\n```json\n{jd_payload}\n```"},
        ]

        raw = await llm_client.chat(messages)
        try:
            import json

            data = json.loads(raw)
        except Exception:
            return RoleRequirements(
                role=user_input.role,
                seniority_level="unspecified",
                core_skills=[],
                nice_to_have_skills=[],
                tools_and_tech=[],
                responsibilities=[],
                keywords=[],
                hidden_expectations=[],
            )

        return RoleRequirements(
            role=user_input.role,
            seniority_level=data.get("seniority_level", "unspecified"),
            core_skills=data.get("core_skills", []),
            nice_to_have_skills=data.get("nice_to_have_skills", []),
            tools_and_tech=data.get("tools_and_tech", []),
            responsibilities=data.get("responsibilities", []),
            keywords=data.get("keywords", []),
            hidden_expectations=data.get("hidden_expectations", []),
        )


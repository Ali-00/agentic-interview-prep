from __future__ import annotations

from typing import Optional

from ..llm import llm_client
from ..models import SkillProfile, UserInput


class ResumeAnalyzerAgent:
    async def analyze(self, user_input: UserInput) -> SkillProfile:
        """
        Parse the resume text (if any) and years of experience to build a skill profile.

        If no resume text is provided, we still infer a coarse profile from role and years.
        """
        base_prompt = (
            "You are an expert technical recruiter and hiring manager.\n"
            "Given the user's target role, years of experience, and optional resume text,\n"
            "produce a structured JSON skill profile with:\n"
            "- headline (1 sentence)\n"
            "- primary_skills (list of concise skill names)\n"
            "- secondary_skills (list)\n"
            "- tools_and_tech (list)\n"
            "- domains (list of domains/industries)\n"
            "- notable_projects (list of short project descriptions)\n\n"
            "Only output valid JSON."
        )

        resume_snippet = user_input.resume_text or ""
        user_desc = {
            "role": user_input.role,
            "years_experience": user_input.years_experience,
            "resume": resume_snippet[:6000],
        }

        messages = [
            {"role": "system", "content": base_prompt},
            {
                "role": "user",
                "content": f"USER_PROFILE:\n```json\n{user_desc}\n```",
            },
        ]

        raw = await llm_client.chat(messages)
        # In a production system, add robust JSON parsing & validation here.
        # For now, rely on model discipline and fall back to a minimal profile if parsing fails.
        try:
            import json

            data = json.loads(raw)
        except Exception:
            return SkillProfile(
                headline=f"{user_input.years_experience} years {user_input.role}",
                years_experience=user_input.years_experience,
                primary_skills=[],
                secondary_skills=[],
                tools_and_tech=[],
                domains=[],
                notable_projects=[],
            )

        return SkillProfile(
            headline=data.get("headline"),
            years_experience=user_input.years_experience,
            primary_skills=data.get("primary_skills", []),
            secondary_skills=data.get("secondary_skills", []),
            tools_and_tech=data.get("tools_and_tech", []),
            domains=data.get("domains", []),
            notable_projects=data.get("notable_projects", []),
        )


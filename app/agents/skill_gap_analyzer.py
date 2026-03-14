from __future__ import annotations

from ..llm import llm_client
from ..models import SkillProfile, RoleRequirements, SkillGapAnalysis


class SkillGapAnalyzerAgent:
    async def analyze(
        self, skill_profile: SkillProfile, role_requirements: RoleRequirements
    ) -> SkillGapAnalysis:
        """
        Compare user's skill profile with role requirements and prioritize gaps.
        """
        system_prompt = (
            "You are an expert technical interviewer.\n"
            "Compare the candidate's skill profile with the role requirements and\n"
            "produce a concise but insightful skill gap analysis.\n\n"
            "Return STRICT JSON with keys:\n"
            "- matched_skills (list)\n"
            "- missing_critical_skills (list)\n"
            "- missing_nice_to_have_skills (list)\n"
            "- commentary (short paragraph)\n"
            "- prioritized_focus_areas (list of high-impact topics/skills)\n"
        )

        payload = {
            "skill_profile": skill_profile.model_dump(),
            "role_requirements": role_requirements.model_dump(),
        }

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"DATA:\n```json\n{payload}\n```"},
        ]

        raw = await llm_client.chat(messages)
        try:
            import json

            data = json.loads(raw)
        except Exception:
            return SkillGapAnalysis(
                matched_skills=[],
                missing_critical_skills=[],
                missing_nice_to_have_skills=[],
                commentary="Unable to perform detailed analysis; using fallback.",
                prioritized_focus_areas=[],
            )

        return SkillGapAnalysis(
            matched_skills=data.get("matched_skills", []),
            missing_critical_skills=data.get("missing_critical_skills", []),
            missing_nice_to_have_skills=data.get("missing_nice_to_have_skills", []),
            commentary=data.get("commentary", ""),
            prioritized_focus_areas=data.get("prioritized_focus_areas", []),
        )


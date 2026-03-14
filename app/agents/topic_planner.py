from __future__ import annotations

from ..llm import llm_client
from ..models import TopicTree, TopicNode, SkillGapAnalysis, RoleRequirements, UserInput


class TopicPlannerAgent:
    async def plan_topics(
        self,
        user_input: UserInput,
        role_requirements: RoleRequirements,
        skill_gap: SkillGapAnalysis,
    ) -> TopicTree:
        """
        Produce a structured topic tree tailored to role and seniority.
        """
        system_prompt = (
            "You are designing a study syllabus for a candidate preparing for job interviews.\n"
            "Given the role, years of experience, role requirements, and skill gaps,\n"
            "produce a hierarchical topic tree.\n\n"
            "Return STRICT JSON with key 'nodes' which is a list of topic nodes.\n"
            "Each topic node must have:\n"
            "- name (string)\n"
            "- depth_level ('foundational' | 'intermediate' | 'advanced')\n"
            "- description (string)\n"
            "- children (list of child topic nodes with same structure)\n"
        )

        payload = {
            "role": user_input.role,
            "years_experience": user_input.years_experience,
            "role_requirements": role_requirements.model_dump(),
            "skill_gap": skill_gap.model_dump(),
        }

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"INPUT:\n```json\n{payload}\n```"},
        ]

        raw = await llm_client.chat(messages)
        try:
            import json

            data = json.loads(raw)
            raw_nodes = data.get("nodes", [])
        except Exception:
            raw_nodes = []

        def _build_node(d: dict) -> TopicNode:
            return TopicNode(
                name=d.get("name", "Unnamed Topic"),
                depth_level=d.get("depth_level", "intermediate"),
                description=d.get("description"),
                children=[_build_node(c) for c in d.get("children", [])],
            )

        nodes = [_build_node(n) for n in raw_nodes]
        return TopicTree(
            role=user_input.role,
            years_experience=user_input.years_experience,
            nodes=nodes,
        )


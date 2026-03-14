from __future__ import annotations

from typing import List

from ..llm import llm_client
from ..models import TopicTree, TopicContent, TopicNode, UserInput, SkillGapAnalysis


class ContentGeneratorAgent:
    async def generate_for_topic(
        self,
        user_input: UserInput,
        topic: TopicNode,
        path: List[str],
        skill_gap: SkillGapAnalysis,
    ) -> TopicContent:
        """
        Generate deep, interview-focused content for a single topic node.
        """
        system_prompt = (
            "You are an expert technical interviewer and educator.\n"
            "Write concise but deep, interview-focused study material for ONE topic.\n"
            "Tailor the depth to the candidate's experience level and whether it is a gap area.\n\n"
            "You must return STRICT JSON with keys:\n"
            "- concept_explanation (paragraphs)\n"
            "- why_it_matters (paragraphs)\n"
            "- likely_questions (list of 5–10 bullet strings)\n"
            "- tricky_scenarios (list)\n"
            "- common_mistakes (list)\n"
            "- real_world_examples (list)\n"
        )

        is_gap = any(
            kw.lower() in topic.name.lower()
            for kw in (skill_gap.missing_critical_skills + skill_gap.prioritized_focus_areas)
        )

        payload = {
            "role": user_input.role,
            "years_experience": user_input.years_experience,
            "topic": topic.model_dump(),
            "topic_path": path,
            "is_gap_area": is_gap,
        }

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"TOPIC_REQUEST:\n```json\n{payload}\n```"},
        ]

        raw = await llm_client.chat(messages, max_tokens=1800)
        try:
            import json

            data = json.loads(raw)
        except Exception:
            data = {}

        # Normalize fields to satisfy pydantic schema and be robust
        concept_explanation = data.get("concept_explanation", "Content could not be generated.")
        if isinstance(concept_explanation, list):
            concept_explanation = "\n\n".join(str(p) for p in concept_explanation)
        elif not isinstance(concept_explanation, str):
            concept_explanation = str(concept_explanation)

        why_it_matters = data.get("why_it_matters", "")
        if isinstance(why_it_matters, list):
            why_it_matters = "\n\n".join(str(p) for p in why_it_matters)
        elif not isinstance(why_it_matters, str):
            why_it_matters = str(why_it_matters)

        def ensure_list(value):
            if value is None:
                return []
            if isinstance(value, list):
                return value
            return [value]

        likely_questions = ensure_list(data.get("likely_questions", []))
        tricky_scenarios = ensure_list(data.get("tricky_scenarios", []))
        common_mistakes = ensure_list(data.get("common_mistakes", []))
        real_world_examples = ensure_list(data.get("real_world_examples", []))

        return TopicContent(
            topic_name=" / ".join(path + [topic.name]),
            depth_level=topic.depth_level,
            concept_explanation=concept_explanation,
            why_it_matters=why_it_matters,
            likely_questions=likely_questions,
            tricky_scenarios=tricky_scenarios,
            common_mistakes=common_mistakes,
            real_world_examples=real_world_examples,
        )

    async def generate_for_tree(
        self,
        user_input: UserInput,
        topic_tree: TopicTree,
        skill_gap: SkillGapAnalysis,
    ) -> List[TopicContent]:
        contents: List[TopicContent] = []

        async def _walk(node: TopicNode, path: List[str]):
            contents.append(
                await self.generate_for_topic(user_input, node, path, skill_gap)
            )
            for child in node.children:
                await _walk(child, path + [node.name])

        for root in topic_tree.nodes:
            await _walk(root, [])

        return contents


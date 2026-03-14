from __future__ import annotations

from typing import Dict, Any, Optional, List

from .models import (
    UserInput,
    StudyGuide,
    OverviewSection,
    StudyPlan,
    StudyPlanDay,
    CoverageMap,
    CoverageItem,
    GenerateStudyGuideResponse,
)
from .agents.resume_analyzer import ResumeAnalyzerAgent
from .agents.job_description_analyzer import JobDescriptionAnalyzerAgent
from .agents.skill_gap_analyzer import SkillGapAnalyzerAgent
from .agents.topic_planner import TopicPlannerAgent
from .agents.content_generator import ContentGeneratorAgent
from .agents.document_formatter import DocumentFormatterAgent
from .pdf_utils import html_to_pdf_b64


class SessionMemory:
    """
    Simple in-memory session store keyed by session_id.
    For production you would back this with Redis or a database.
    """

    def __init__(self) -> None:
        self._store: Dict[str, Dict[str, Any]] = {}

    def get(self, session_id: str) -> Dict[str, Any]:
        return self._store.get(session_id, {})

    def put(self, session_id: str, data: Dict[str, Any]) -> None:
        self._store[session_id] = data


class ControllerAgent:
    def __init__(self) -> None:
        self.resume_analyzer = ResumeAnalyzerAgent()
        self.jd_analyzer = JobDescriptionAnalyzerAgent()
        self.skill_gap_analyzer = SkillGapAnalyzerAgent()
        self.topic_planner = TopicPlannerAgent()
        self.content_generator = ContentGeneratorAgent()
        self.document_formatter = DocumentFormatterAgent()
        self.session_memory = SessionMemory()

    async def generate_study_guide(
        self, user_input: UserInput, include_pdf: bool = False
    ) -> GenerateStudyGuideResponse:
        # Load session context if present
        session_ctx: Dict[str, Any] = {}
        if user_input.session_id:
            session_ctx = self.session_memory.get(user_input.session_id)

        # 1. Analyze resume and JD
        skill_profile = await self.resume_analyzer.analyze(user_input)
        role_requirements = await self.jd_analyzer.analyze(user_input)

        # 2. Skill gap analysis
        skill_gap = await self.skill_gap_analyzer.analyze(
            skill_profile, role_requirements
        )

        # 3. Topic planning
        topic_tree = await self.topic_planner.plan_topics(
            user_input, role_requirements, skill_gap
        )

        # 4. Content generation
        topic_contents = await self.content_generator.generate_for_tree(
            user_input, topic_tree, skill_gap
        )

        # 5. Overview
        overview = self._build_overview(
            user_input=user_input,
            skill_profile_summary=skill_profile.headline or "",
            role_requirements_summary=role_requirements,
            topic_contents=topic_contents,
        )

        # 6. Study plan (optional)
        study_plan = None
        if user_input.study_plan_duration_days:
            study_plan = self._build_study_plan(
                duration_days=user_input.study_plan_duration_days,
                topic_contents=topic_contents,
                skill_gap_priorities=skill_gap.prioritized_focus_areas,
            )

        # 7. Coverage map
        coverage_map = self._build_coverage_map(topic_contents)

        study_guide = StudyGuide(
            overview=overview,
            topic_deep_dives=topic_contents,
            skill_gap_analysis=skill_gap,
            study_plan=study_plan,
            coverage_map=coverage_map,
            metadata={
                "role": user_input.role,
                "years_experience": user_input.years_experience,
                "session_id": user_input.session_id,
            },
        )

        document = self.document_formatter.build_document(study_guide)

        if include_pdf:
            pdf_b64 = html_to_pdf_b64(document.html)
            document.pdf_bytes_b64 = pdf_b64

        # Persist session snapshot
        if user_input.session_id:
            self.session_memory.put(
                user_input.session_id,
                {
                    "user_input": user_input.model_dump(),
                    "skill_profile": skill_profile.model_dump(),
                    "role_requirements": role_requirements.model_dump(),
                    "skill_gap": skill_gap.model_dump(),
                },
            )

        return GenerateStudyGuideResponse(document=document)

    def _build_overview(
        self,
        user_input: UserInput,
        skill_profile_summary: str,
        role_requirements_summary,
        topic_contents: list,
    ) -> OverviewSection:
        depth_level = self._infer_depth_level(
            user_input.years_experience, role_requirements_summary.seniority_level
        )
        key_topics = [t.topic_name for t in topic_contents[:10]]
        role_summary = (
            f"Role: {role_requirements_summary.role} "
            f"({role_requirements_summary.seniority_level}). "
            f"Core skills: {', '.join(role_requirements_summary.core_skills[:8])}."
        )
        user_summary = (
            skill_profile_summary
            or f"Candidate targeting {user_input.role} with ~{user_input.years_experience} years of experience."
        )
        return OverviewSection(
            user_profile_summary=user_summary,
            role_expectations_summary=role_summary,
            key_topics_summary=key_topics,
            depth_level=depth_level,
        )

    def _infer_depth_level(self, years: float, seniority: str) -> str:
        s = seniority.lower()
        if years < 2 or "junior" in s:
            return "foundational to intermediate"
        if years < 5 or "mid" in s:
            return "intermediate to advanced"
        return "advanced and system-level"

    def _build_study_plan(
        self,
        duration_days: int,
        topic_contents: list,
        skill_gap_priorities: list,
    ) -> StudyPlan:
        if duration_days <= 0:
            duration_days = 7

        topics_sorted = sorted(
            topic_contents,
            key=lambda t: any(
                p.lower() in t.topic_name.lower() for p in skill_gap_priorities
            ),
            reverse=True,
        )
        chunk_size = max(1, len(topics_sorted) // duration_days)

        days: list[StudyPlanDay] = []
        for i in range(duration_days):
            start = i * chunk_size
            end = (i + 1) * chunk_size
            slice_topics = topics_sorted[start:end]
            if not slice_topics:
                break
            focus_topics = [t.topic_name for t in slice_topics]
            objectives = [
                "Understand core concepts and definitions.",
                "Practice explaining the topic aloud using your own examples.",
                "Answer at least 5 practice questions per topic.",
            ]
            activities = [
                "Review this guide's explanations.",
                "Create flashcards for key terms and equations (if any).",
                "Solve coding/analysis problems related to the topic.",
                "Conduct a mock interview focusing on these topics.",
            ]
            days.append(
                StudyPlanDay(
                    day_number=i + 1,
                    focus_topics=focus_topics,
                    objectives=objectives,
                    recommended_activities=activities,
                )
            )

        return StudyPlan(total_days=len(days), days=days)

    def _build_coverage_map(self, topic_contents: list) -> CoverageMap:
        items: List[CoverageItem] = []
        for t in topic_contents:
            items.append(
                CoverageItem(
                    topic=t.topic_name,
                    covered=True,
                    notes=f"Depth: {t.depth_level}",
                )
            )
        estimated = 80 if len(items) > 0 else 0
        return CoverageMap(
            target_coverage_percent=80,
            estimated_coverage_percent=estimated,
            items=items,
        )


controller_agent = ControllerAgent()


from __future__ import annotations

from typing import List, Optional, Dict, Any

from pydantic import BaseModel, HttpUrl, Field


class UserInput(BaseModel):
    role: str = Field(..., description="Target job role, e.g. 'Data Scientist'")
    years_experience: float = Field(..., ge=0, description="Years of total experience")
    resume_text: Optional[str] = Field(
        None, description="Resume contents as plain text"
    )
    job_description_text: Optional[str] = Field(
        None, description="Job description as plain text"
    )
    job_description_url: Optional[HttpUrl] = Field(
        None, description="URL pointing to the job description"
    )
    study_plan_duration_days: Optional[int] = Field(
        None, description="Optional plan duration (e.g. 7, 14, 30)"
    )
    session_id: Optional[str] = Field(
        None, description="Session identifier for iterative refinement"
    )


class SkillProfile(BaseModel):
    headline: Optional[str] = None
    years_experience: float
    primary_skills: List[str] = []
    secondary_skills: List[str] = []
    tools_and_tech: List[str] = []
    domains: List[str] = []
    notable_projects: List[str] = []


class RoleRequirements(BaseModel):
    role: str
    seniority_level: str
    core_skills: List[str]
    nice_to_have_skills: List[str] = []
    tools_and_tech: List[str] = []
    responsibilities: List[str] = []
    keywords: List[str] = []
    hidden_expectations: List[str] = []


class SkillGapAnalysis(BaseModel):
    matched_skills: List[str]
    missing_critical_skills: List[str]
    missing_nice_to_have_skills: List[str]
    commentary: str
    prioritized_focus_areas: List[str]


class TopicNode(BaseModel):
    name: str
    depth_level: str  # e.g. "foundational", "intermediate", "advanced"
    description: Optional[str] = None
    children: List["TopicNode"] = []


TopicNode.model_rebuild()


class TopicTree(BaseModel):
    role: str
    years_experience: float
    nodes: List[TopicNode]


class TopicContent(BaseModel):
    topic_name: str
    depth_level: str
    concept_explanation: str
    why_it_matters: str
    likely_questions: List[str]
    tricky_scenarios: List[str]
    common_mistakes: List[str]
    real_world_examples: List[str]


class StudyPlanDay(BaseModel):
    day_number: int
    focus_topics: List[str]
    objectives: List[str]
    recommended_activities: List[str]


class StudyPlan(BaseModel):
    total_days: int
    days: List[StudyPlanDay]


class CoverageItem(BaseModel):
    topic: str
    covered: bool
    notes: Optional[str] = None


class CoverageMap(BaseModel):
    target_coverage_percent: int = 80
    estimated_coverage_percent: int
    items: List[CoverageItem]


class OverviewSection(BaseModel):
    user_profile_summary: str
    role_expectations_summary: str
    key_topics_summary: List[str]
    depth_level: str


class StudyGuide(BaseModel):
    overview: OverviewSection
    topic_deep_dives: List[TopicContent]
    skill_gap_analysis: SkillGapAnalysis
    study_plan: Optional[StudyPlan] = None
    coverage_map: CoverageMap
    metadata: Dict[str, Any] = {}


class StudyGuideDocument(BaseModel):
    """Final document in multiple formats."""

    study_guide: StudyGuide
    markdown: str
    html: str
    pdf_bytes_b64: Optional[str] = None


class GenerateStudyGuideResponse(BaseModel):
    document: StudyGuideDocument


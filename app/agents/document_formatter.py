from __future__ import annotations

from typing import List

from jinja2 import Environment, BaseLoader, select_autoescape

from ..models import (
    StudyGuide,
    StudyGuideDocument,
    TopicContent,
    StudyPlan,
    CoverageMap,
)


MD_TEMPLATE = """
## Overview

{{ overview.user_profile_summary }}

**Role expectations:** {{ overview.role_expectations_summary }}

**Depth level:** {{ overview.depth_level }}

**Key topics:**

{% for t in overview.key_topics_summary -%}
- {{ t }}
{% endfor %}

---

## Topic-wise Deep Dive

{% for topic in topic_deep_dives %}
### {{ loop.index }}. {{ topic.topic_name }} ({{ topic.depth_level|capitalize }})

**Concept explanation**

{{ topic.concept_explanation }}

**Why it matters in interviews**

{{ topic.why_it_matters }}

**Likely questions**

{% for q in topic.likely_questions -%}
- {{ q }}
{% endfor %}

**Tricky or edge-case scenarios**

{% for s in topic.tricky_scenarios -%}
- {{ s }}
{% endfor %}

**Common mistakes**

{% for m in topic.common_mistakes -%}
- {{ m }}
{% endfor %}

**Real-world examples**

{% for ex in topic.real_world_examples -%}
- {{ ex }}
{% endfor %}

---

{% endfor %}

## Skill Gap & Priority

**Matched skills**

{% for s in skill_gap.matched_skills -%}
- {{ s }}
{% endfor %}

**Missing critical skills**

{% for s in skill_gap.missing_critical_skills -%}
- {{ s }}
{% endfor %}

**Missing nice-to-have skills**

{% for s in skill_gap.missing_nice_to_have_skills -%}
- {{ s }}
{% endfor %}

**Commentary**

{{ skill_gap.commentary }}

**Prioritized focus areas**

{% for s in skill_gap.prioritized_focus_areas -%}
- {{ s }}
{% endfor %}

---

{% if study_plan %}
## Suggested Study Plan ({{ study_plan.total_days }} days)

{% for day in study_plan.days %}
### Day {{ day.day_number }}

**Focus topics**

{% for t in day.focus_topics -%}
- {{ t }}
{% endfor %}

**Objectives**

{% for o in day.objectives -%}
- {{ o }}
{% endfor %}

**Recommended activities**

{% for a in day.recommended_activities -%}
- {{ a }}
{% endfor %}

---

{% endfor %}
{% endif %}

## Coverage Map

**Target coverage:** {{ coverage_map.target_coverage_percent }}%

**Estimated coverage:** {{ coverage_map.estimated_coverage_percent }}%

**Checklist**

{% for item in coverage_map.items -%}
- [{{ "x" if item.covered else " " }}] {{ item.topic }} {% if item.notes %}- {{ item.notes }}{% endif %}
{% endfor %}
"""


HTML_WRAPPER = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>InterviewPrepAI Study Guide</title>
  <style>
    body { font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; line-height: 1.6; margin: 2rem; }
    h2, h3, h4 { color: #1f2933; }
    hr { border: none; border-top: 1px solid #e5e7eb; margin: 2rem 0; }
    ul { margin-left: 1.25rem; }
    code { background: #f3f4f6; padding: 0.1rem 0.2rem; border-radius: 3px; }
  </style>
</head>
<body>
{{ body }}
</body>
</html>
"""


class DocumentFormatterAgent:
    def __init__(self) -> None:
        self.env = Environment(
            loader=BaseLoader(),
            autoescape=select_autoescape(enabled_extensions=("html",)),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.md_template = self.env.from_string(MD_TEMPLATE)
        self.html_wrapper = self.env.from_string(HTML_WRAPPER)

    def render_markdown(self, study_guide: StudyGuide) -> str:
        return self.md_template.render(
            overview=study_guide.overview,
            topic_deep_dives=study_guide.topic_deep_dives,
            skill_gap=study_guide.skill_gap_analysis,
            study_plan=study_guide.study_plan,
            coverage_map=study_guide.coverage_map,
        )

    def render_html(self, markdown: str) -> str:
        # For simplicity, we treat markdown as pre-formatted text inside HTML template.
        # In production you may run it through a Markdown-to-HTML converter.
        body = "<pre>" + markdown.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") + "</pre>"
        return self.html_wrapper.render(body=body)

    def build_document(self, study_guide: StudyGuide) -> StudyGuideDocument:
        md = self.render_markdown(study_guide)
        html = self.render_html(md)
        return StudyGuideDocument(study_guide=study_guide, markdown=md, html=html)


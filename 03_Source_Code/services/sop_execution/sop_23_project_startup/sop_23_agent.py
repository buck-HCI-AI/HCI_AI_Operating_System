"""SOP 23 — Layer 3: Project Startup AI Agent."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "api"))

from base import BaseIntelligenceService
from sop_23_project_startup.sop_23_templates import STARTUP_CATEGORIES

SYSTEM_PROMPT = """You are HCI's Project Startup AI (SOP 23).
Generate startup checklists, identify pre-construction risks, and ensure the project is ready to build.
RULES:
- Return only structured JSON
- Safety checklist items are MANDATORY and cannot be waived without PM+Principal approval
- Personnel assignments must be confirmed before construction start
- Site setup must be complete before any subcontractor mobilizes
"""


class SOP23Agent(BaseIntelligenceService):
    SERVICE_NAME = "sop_23_agent"
    STATUS = "active"

    @classmethod
    def generate_startup_checklist(cls, project_type: str, project_name: str,
                                    superintendent_name: str, construction_start: str) -> dict:
        results = cls.search(
            f"{project_type} project startup checklist mobilization",
            collection="lessons_learned", limit=5,
        )
        lessons = "\n".join(r.get("payload", {}).get("text", "") for r in results) or "No lessons learned found."

        prompt = f"""Generate a project startup checklist.

PROJECT: {project_name}
TYPE: {project_type}
SUPERINTENDENT: {superintendent_name}
START DATE: {construction_start}
CATEGORIES: {STARTUP_CATEGORIES}
LESSONS LEARNED: {lessons}

Return JSON:
{{
  "checklist_items": [
    {{
      "item_code": "STR-001",
      "category": "<category>",
      "description": "<what must be done>",
      "responsible_party": "PM|Superintendent|Estimator|Principal",
      "due_by": "<before construction start or specific date>",
      "mandatory": <true|false>
    }}
  ],
  "mandatory_count": <int>,
  "ready_to_build_criteria": ["<criterion>"],
  "ai_note": "AI STARTUP CHECKLIST — PM TO ASSIGN AND TRACK COMPLETION"
}}
Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1500)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "checklist_items": [], "ai_note": "AI startup checklist failed — build manually"}

    @classmethod
    def identify_startup_risks(cls, project_type: str, scope_summary: str,
                                site_conditions: str = "") -> dict:
        prompt = f"""Identify project startup risks for this project.

TYPE: {project_type}
SCOPE: {scope_summary}
SITE CONDITIONS: {site_conditions or 'Not specified'}

Return JSON:
{{
  "startup_risks": [{{"description": "<risk>", "severity": "LOW|MEDIUM|HIGH", "mitigation": "<action>"}}],
  "critical_path_startup_items": ["<item that must be done first>"],
  "recommended_kickoff_agenda": ["<agenda item>"],
  "ai_note": "AI STARTUP RISK REVIEW — PM TO ACTION"
}}
Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1024)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "startup_risks": []}

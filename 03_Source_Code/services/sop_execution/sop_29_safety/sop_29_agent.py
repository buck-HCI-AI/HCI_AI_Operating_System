"""SOP 29 — Layer 3: Safety AI Agent."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "api"))

from base import BaseIntelligenceService
from sop_29_safety.sop_29_templates import HAZARD_CATEGORIES

SYSTEM_PROMPT = """You are HCI's Safety AI (SOP 29).
Identify hazards, generate safety plans, and flag uncontrolled CRITICAL risks.
RULES:
- Return only structured JSON
- CRITICAL uncontrolled hazards = work stops immediately
- Cal/OSHA standards apply unless otherwise specified
- Safety is non-negotiable — never minimize risks
"""


class SOP29Agent(BaseIntelligenceService):
    SERVICE_NAME = "sop_29_agent"
    STATUS = "active"

    @classmethod
    def generate_safety_plan(cls, project_type: str, project_name: str,
                              scope_summary: str, site_conditions: str = "") -> dict:
        results = cls.search(
            f"{project_type} safety hazard OSHA construction",
            collection="lessons_learned", limit=5,
        )
        lessons = "\n".join(r.get("payload", {}).get("text", "") for r in results) or "No safety history."

        prompt = f"""Generate a site safety hazard identification plan.

PROJECT: {project_name}
TYPE: {project_type}
SCOPE: {scope_summary}
SITE CONDITIONS: {site_conditions or 'Standard commercial site'}
HAZARD CATEGORIES: {HAZARD_CATEGORIES}
LESSONS LEARNED: {lessons}

Return JSON:
{{
  "hazards": [
    {{
      "hazard_code": "SAF-001",
      "category": "<category>",
      "description": "<hazard description>",
      "location": "<where on site>",
      "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
      "controls": ["<control measure 1>"],
      "regulatory_ref": "<Cal/OSHA section if applicable>"
    }}
  ],
  "critical_hazard_count": <int>,
  "ppe_requirements": ["<PPE item>"],
  "toolbox_talk_topics": ["<topic>"],
  "ai_note": "AI SAFETY PLAN — SUPERINTENDENT AND PM TO REVIEW; CRITICAL ITEMS REQUIRE IMMEDIATE CONTROL"
}}
Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1500)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "hazards": [], "ai_note": "AI safety plan failed — conduct manual JHA"}

    @classmethod
    def flag_uncontrolled_critical(cls, hazards: list[dict]) -> dict:
        critical_open = [h for h in hazards
                         if h.get("risk_level") == "CRITICAL" and h.get("status") == "IDENTIFIED"]
        return {
            "work_stop_required": len(critical_open) > 0,
            "critical_uncontrolled": critical_open,
            "immediate_actions": [
                f"Control {h.get('hazard_code')} — {h.get('description')}"
                for h in critical_open
            ],
            "ai_note": "SAFETY STOP CONDITION — DO NOT PROCEED UNTIL HAZARDS CONTROLLED",
        }

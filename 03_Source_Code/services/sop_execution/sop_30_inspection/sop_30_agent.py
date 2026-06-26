"""SOP 30 — Layer 3: Inspection AI Agent."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "api"))

from base import BaseIntelligenceService
from sop_30_inspection.sop_30_templates import INSPECTION_TYPES

SYSTEM_PROMPT = """You are HCI's Inspection AI (SOP 30).
Prepare inspection checklists, track AHJ inspection results, and flag correction notices.
RULES:
- Return only structured JSON
- Inspection failures block construction advance until corrections made and re-inspection passed
- Never confirm an inspection result — that is the AHJ inspector's authority
- Reference permit number and inspection type in all records
"""


class SOP30Agent(BaseIntelligenceService):
    SERVICE_NAME = "sop_30_agent"
    STATUS = "active"

    @classmethod
    def prepare_inspection_checklist(cls, inspection_type: str, project_type: str,
                                      jurisdiction: str, permit_number: str) -> dict:
        results = cls.search(
            f"{inspection_type} inspection checklist {jurisdiction} {project_type}",
            collection="lessons_learned", limit=3,
        )
        lessons = "\n".join(r.get("payload", {}).get("text", "") for r in results) or "No inspection history."

        prompt = f"""Generate a pre-inspection preparation checklist.

INSPECTION TYPE: {inspection_type}
PROJECT TYPE: {project_type}
JURISDICTION: {jurisdiction}
PERMIT NUMBER: {permit_number}
LESSONS LEARNED: {lessons}

Return JSON:
{{
  "pre_inspection_items": ["<what must be ready before calling for inspection>"],
  "common_failure_points": ["<what inspectors typically flag for this inspection type>"],
  "documentation_required": ["<doc to have on site>"],
  "notification_timeline": "<how far in advance to call for inspection>",
  "pass_criteria_summary": "<what pass looks like>",
  "ai_note": "AI INSPECTION PREP — SUPERINTENDENT TO VERIFY READINESS"
}}
Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1024)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "pre_inspection_items": [], "ai_note": "AI prep failed — review AHJ requirements manually"}

    @classmethod
    def analyze_correction_notice(cls, inspection_type: str,
                                   correction_items: list[str]) -> dict:
        prompt = f"""Analyze inspection correction notice and generate remediation plan.

INSPECTION TYPE: {inspection_type}
CORRECTION ITEMS: {correction_items}

Return JSON:
{{
  "corrections": [
    {{
      "item": "<correction item>",
      "urgency": "IMMEDIATE|THIS_WEEK|BEFORE_NEXT_PHASE",
      "responsible_trade": "<who fixes it>",
      "resolution": "<how to fix>"
    }}
  ],
  "re_inspection_timeline": "<when to call for re-inspection>",
  "scope_impact": "<any scope or cost implications>",
  "ai_note": "AI CORRECTION ANALYSIS — PM TO DIRECT REMEDIATION"
}}
Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1024)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "corrections": [{"item": c, "urgency": "THIS_WEEK"} for c in correction_items]}

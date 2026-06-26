"""SOP 27 — Layer 3: Quality Control AI Agent."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "api"))

from base import BaseIntelligenceService
from sop_27_quality_control.sop_27_templates import QC_CATEGORIES

SYSTEM_PROMPT = """You are HCI's Quality Control AI (SOP 27).
Generate QC inspection checklists, analyze failures, and flag critical deficiencies requiring rework.
RULES:
- Return only structured JSON
- CRITICAL failures stop work until corrected
- Reference specification sections where applicable
- All QC conclusions require superintendent or PM confirmation
"""


class SOP27Agent(BaseIntelligenceService):
    SERVICE_NAME = "sop_27_agent"
    STATUS = "active"

    @classmethod
    def generate_qc_checklist(cls, project_type: str, trade_code: str,
                               category: str, spec_section: str = "") -> dict:
        results = cls.search(
            f"quality control {category} {trade_code} inspection checklist",
            collection="lessons_learned", limit=5,
        )
        lessons = "\n".join(r.get("payload", {}).get("text", "") for r in results) or "No QC history."

        prompt = f"""Generate a QC inspection checklist.

PROJECT TYPE: {project_type}
TRADE CODE: {trade_code}
CATEGORY: {category}
SPEC SECTION: {spec_section or 'Not specified'}
QC LESSONS LEARNED: {lessons}

Return JSON:
{{
  "inspection_items": [
    {{
      "item_code": "QC-{category[:3].upper()}-001",
      "description": "<what to inspect>",
      "specification_ref": "<spec section if known>",
      "acceptance_criteria": "<pass/fail criteria>",
      "inspection_method": "Visual|Measurement|Test|Document",
      "critical": <true|false>
    }}
  ],
  "pre_inspection_checklist": ["<prerequisite>"],
  "common_deficiencies": ["<common failure for this trade>"],
  "ai_note": "AI QC CHECKLIST — SUPERINTENDENT TO USE AS FIELD GUIDE"
}}
Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1500)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "inspection_items": [], "ai_note": "AI checklist failed"}

    @classmethod
    def analyze_failures(cls, failures: list[dict], project_type: str) -> dict:
        critical = [f for f in failures if f.get("severity") == "CRITICAL"]
        prompt = f"""Analyze QC failures and recommend corrective actions.

PROJECT TYPE: {project_type}
TOTAL FAILURES: {len(failures)}
CRITICAL FAILURES: {len(critical)}
FAILURES: {[{"item": f.get("description"), "severity": f.get("severity"), "category": f.get("category")} for f in failures[:10]]}

Return JSON:
{{
  "work_stop_required": <true|false>,
  "corrective_actions": [{{"item_code": "<code>", "action": "<corrective action>", "timeline": "<urgency>"}}],
  "pattern_analysis": "<are there systemic quality issues>",
  "subcontractor_notification_required": <true|false>,
  "ai_note": "AI QC FAILURE ANALYSIS — PM TO DIRECT CORRECTIVE WORK"
}}
Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1024)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "work_stop_required": len(critical) > 0}

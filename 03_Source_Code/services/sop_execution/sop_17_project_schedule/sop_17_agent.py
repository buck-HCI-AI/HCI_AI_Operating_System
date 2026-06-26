"""SOP 17 — Layer 3: Project Schedule AI Agent."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "api"))

from base import BaseIntelligenceService
from sop_17_project_schedule.sop_17_templates import SCHEDULE_PHASES

SYSTEM_PROMPT = """You are HCI's Project Schedule AI (SOP 17).
Generate construction schedule outlines, identify critical path milestones, and flag scheduling risks.
RULES:
- Return only structured JSON
- All schedules are DRAFTS requiring PM review
- Flag trades that are likely to overlap or conflict
- Identify long-lead procurement items that affect schedule
"""


class SOP17Agent(BaseIntelligenceService):
    SERVICE_NAME = "sop_17_agent"
    STATUS = "active"

    @classmethod
    def generate_schedule_outline(cls, project_type: str, construction_start: str,
                                   substantial_completion: str, project_name: str,
                                   narrative_summary: str = "") -> dict:
        results = cls.search(
            f"{project_type} construction schedule milestones duration",
            collection="hci_historical_costs", limit=5,
        )
        history = "\n".join(r.get("payload", {}).get("text", "") for r in results) or "No schedule history found."

        prompt = f"""Generate a construction schedule milestone outline.

PROJECT: {project_name}
TYPE: {project_type}
START: {construction_start}
SUBSTANTIAL COMPLETION: {substantial_completion}
SCOPE SUMMARY: {narrative_summary or 'Not provided'}
HISTORICAL DATA: {history}

Generate milestones for each applicable phase: {SCHEDULE_PHASES}

Return JSON:
{{
  "milestones": [
    {{
      "milestone_code": "M-001",
      "phase": "<phase>",
      "description": "<milestone description>",
      "planned_start": "YYYY-MM-DD",
      "planned_finish": "YYYY-MM-DD",
      "duration_days": <int>,
      "float_days": <int>,
      "critical_path": <true|false>,
      "predecessor_codes": ["M-XXX"],
      "trade_codes": ["<CSI code>"]
    }}
  ],
  "total_duration_days": <int>,
  "critical_path_summary": "<brief description>",
  "schedule_risks": ["<risk 1>"],
  "ai_note": "AI DRAFT SCHEDULE — PM TO REVIEW AND CONFIRM"
}}
Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=2000)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "milestones": [], "ai_note": "AI schedule generation failed — build manually"}

    @classmethod
    def analyze_schedule_risk(cls, milestones: list[dict], project_type: str) -> dict:
        cp_count = sum(1 for m in milestones if m.get("critical_path"))
        float_zero = [m["description"] for m in milestones if m.get("float_days", 1) == 0]
        prompt = f"""Analyze this construction schedule for risk.

PROJECT TYPE: {project_type}
TOTAL MILESTONES: {len(milestones)}
CRITICAL PATH ITEMS: {cp_count}
ZERO-FLOAT MILESTONES: {float_zero[:10]}

Return JSON:
{{
  "overall_risk": "LOW|MEDIUM|HIGH",
  "schedule_risks": [{{"description": "<risk>", "severity": "LOW|MEDIUM|HIGH", "mitigation": "<action>"}}],
  "bottlenecks": ["<milestone description>"],
  "recommendation": "<PM action>",
  "ai_note": "AI SCHEDULE RISK ANALYSIS — PM TO REVIEW"
}}
Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1024)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "overall_risk": "MEDIUM"}

    @classmethod
    def identify_long_lead_handoff(cls, milestones: list[dict], project_type: str) -> dict:
        prompt = f"""Review this schedule and identify items that require long-lead procurement.

PROJECT TYPE: {project_type}
PHASES IN SCHEDULE: {list(set(m.get("phase") for m in milestones))}

Return JSON:
{{
  "long_lead_items": [
    {{"description": "<item>", "typical_lead_weeks": <int>, "order_by_milestone": "<milestone_code>", "risk": "LOW|MEDIUM|HIGH"}}
  ],
  "critical_procurement_items": ["<item requiring immediate action>"],
  "ai_note": "AI LONG-LEAD IDENTIFICATION — HAND OFF TO SOP 18"
}}
Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1024)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "long_lead_items": []}

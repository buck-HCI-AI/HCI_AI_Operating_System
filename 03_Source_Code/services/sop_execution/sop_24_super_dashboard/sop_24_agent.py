"""SOP 24 — Layer 3: Superintendent Daily Dashboard AI Agent."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "api"))

from base import BaseIntelligenceService

SYSTEM_PROMPT = """You are HCI's Superintendent Dashboard AI (SOP 24).
Generate daily field briefs, analyze metrics, and surface actionable alerts for the superintendent.
RULES:
- Return only structured JSON
- Safety RED alerts require immediate escalation to PM
- Terse, field-oriented language — superintendents are on site
- Focus on what needs action today, not history
"""


class SOP24Agent(BaseIntelligenceService):
    SERVICE_NAME = "sop_24_agent"
    STATUS = "active"

    @classmethod
    def generate_daily_brief(cls, project_name: str, date: str,
                              metrics: list[dict], recent_log_summary: str = "") -> dict:
        red = [m for m in metrics if m.get("alert_level") == "RED"]
        yellow = [m for m in metrics if m.get("alert_level") == "YELLOW"]

        prompt = f"""Generate a field daily brief for the superintendent.

PROJECT: {project_name}
DATE: {date}
RED ALERTS: {len(red)} — {[m.get("label") for m in red]}
YELLOW ALERTS: {len(yellow)} — {[m.get("label") for m in yellow]}
RECENT LOG: {recent_log_summary or 'No prior log'}

Return JSON:
{{
  "brief_text": "<concise field brief — 3-5 sentences, plain language>",
  "priority_actions": ["<action 1>", "<action 2>"],
  "alerts": ["<alert text>"],
  "safety_flag": <true|false>,
  "ai_note": "AI DAILY BRIEF — SUPERINTENDENT TO VERIFY CONDITIONS"
}}
Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=768)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "brief_text": "AI brief failed — review manually", "priority_actions": []}

    @classmethod
    def flag_field_alerts(cls, metrics: list[dict]) -> list[dict]:
        alerts = []
        for m in metrics:
            if m.get("alert_level") in ("YELLOW", "RED"):
                alerts.append({
                    "category": m.get("category"),
                    "label": m.get("label"),
                    "value": m.get("value"),
                    "alert_level": m.get("alert_level"),
                    "action": f"Review {m.get('category')} status — {m.get('label')} at {m.get('value')}",
                })
        return alerts

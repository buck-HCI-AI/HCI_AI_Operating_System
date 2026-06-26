"""SOP 25 — Layer 3: Daily Log AI Agent."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "api"))

from base import BaseIntelligenceService

SYSTEM_PROMPT = """You are HCI's Daily Log AI (SOP 25).
Analyze daily log entries, surface risks, and flag items that need PM or scheduling attention.
RULES:
- Return only structured JSON
- Any delay must be flagged with cause and potential schedule impact
- Any safety incident requires immediate escalation flag
- Terse, factual, field-oriented language
"""


class SOP25Agent(BaseIntelligenceService):
    SERVICE_NAME = "sop_25_agent"
    STATUS = "active"

    @classmethod
    def analyze_log_entry(cls, log_date: str, weather: str, work_performed: list[str],
                           delays: list[dict], incidents: list[dict],
                           total_workers: int) -> dict:
        prompt = f"""Analyze this daily log entry for risks and action items.

DATE: {log_date}
WEATHER: {weather}
WORKERS ON SITE: {total_workers}
WORK PERFORMED: {work_performed[:10]}
DELAYS: {delays}
INCIDENTS: {incidents}

Return JSON:
{{
  "risk_flags": ["<flag 1>"],
  "schedule_risk": <true|false>,
  "safety_flag": <true|false>,
  "pm_notification_required": <true|false>,
  "action_items": ["<action>"],
  "delay_cause_codes": ["<code: WEATHER|MATERIAL|LABOR|DESIGN|OWNER|SUBCONTRACTOR|OTHER>"],
  "ai_note": "AI LOG ANALYSIS — SUPERINTENDENT TO REVIEW"
}}
Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=768)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "risk_flags": [], "safety_flag": len(incidents) > 0}

    @classmethod
    def generate_weekly_summary(cls, log_entries: list[dict], project_name: str) -> dict:
        total_workers = sum(e.get("total_workers", 0) for e in log_entries)
        delay_days = sum(1 for e in log_entries if e.get("delays"))
        weather_days = sum(1 for e in log_entries if e.get("weather") in ("rain", "heavy_rain", "snow"))

        prompt = f"""Generate a weekly field summary from daily log data.

PROJECT: {project_name}
DAYS LOGGED: {len(log_entries)}
TOTAL WORKER-DAYS: {total_workers}
DAYS WITH DELAYS: {delay_days}
WEATHER IMPACT DAYS: {weather_days}

Return JSON:
{{
  "week_summary": "<2-3 sentence summary of field progress>",
  "productivity_assessment": "ON_TRACK|SLIGHTLY_BEHIND|BEHIND|CRITICAL",
  "key_accomplishments": ["<accomplishment>"],
  "open_issues": ["<issue>"],
  "pm_report_items": ["<item for weekly PM report>"],
  "ai_note": "AI WEEKLY SUMMARY — PM TO REVIEW AND DISTRIBUTE"
}}
Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1024)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "week_summary": "AI summary failed — compile manually"}

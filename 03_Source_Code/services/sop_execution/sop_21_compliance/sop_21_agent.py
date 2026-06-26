"""SOP 21 — Layer 3: Compliance AI Agent."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "api"))

from base import BaseIntelligenceService
from sop_21_compliance.sop_21_templates import COMPLIANCE_CATEGORIES

SYSTEM_PROMPT = """You are HCI's Compliance AI (SOP 21).
Identify permit and regulatory requirements, flag compliance risks, and ensure clear-to-build status.
RULES:
- Return only structured JSON
- Never confirm permit approval — that requires AHJ verification
- Flag any missing permit that would stop construction
- California construction compliance context by default
"""


class SOP21Agent(BaseIntelligenceService):
    SERVICE_NAME = "sop_21_agent"
    STATUS = "active"

    @classmethod
    def identify_compliance_requirements(cls, project_type: str, jurisdiction: str,
                                          scope_summary: str, contract_value: float) -> dict:
        results = cls.search(
            f"{project_type} permits compliance {jurisdiction}",
            collection="lessons_learned", limit=5,
        )
        history = "\n".join(r.get("payload", {}).get("text", "") for r in results) or "No compliance history."

        prompt = f"""Identify all compliance requirements for this construction project.

PROJECT TYPE: {project_type}
JURISDICTION: {jurisdiction}
CONTRACT VALUE: ${contract_value:,.2f}
SCOPE: {scope_summary or 'General construction'}
COMPLIANCE CATEGORIES: {COMPLIANCE_CATEGORIES}
HISTORICAL DATA: {history}

Return JSON:
{{
  "requirements": [
    {{
      "item_code": "CMP-001",
      "category": "<category>",
      "description": "<what is required>",
      "issuing_authority": "<agency name>",
      "required_by_date": "<before what milestone>",
      "responsible_party": "PM|Superintendent|Principal",
      "priority": "CRITICAL|HIGH|MEDIUM|LOW"
    }}
  ],
  "critical_path_permits": ["<item_code>"],
  "prevailing_wage_required": <true|false>,
  "dir_registration_required": <true|false>,
  "ai_note": "AI COMPLIANCE IDENTIFICATION — PM TO VERIFY WITH AHJ AND LEGAL"
}}
Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1500)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "requirements": [], "ai_note": "AI identification failed — review manually"}

    @classmethod
    def flag_compliance_risks(cls, items: list[dict], construction_start: str) -> dict:
        overdue = [i for i in items
                   if i.get("status") == "REQUIRED" and i.get("required_by_date", "9999") < construction_start]
        prompt = f"""Flag compliance risks for this project.

CONSTRUCTION START: {construction_start}
TOTAL REQUIREMENTS: {len(items)}
POTENTIALLY OVERDUE: {len(overdue)}

Return JSON:
{{
  "clear_to_build": <true|false>,
  "blocking_items": ["<description of item blocking construction>"],
  "at_risk_items": [{{"description": "<item>", "risk": "<specific risk>", "action": "<required action>"}}],
  "ai_note": "AI COMPLIANCE RISK FLAG — PM TO RESOLVE BEFORE CONSTRUCTION START"
}}
Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=768)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "clear_to_build": False}

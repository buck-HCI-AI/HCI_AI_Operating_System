"""SOP 20 — Layer 3: Contract Setup AI Agent."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "api"))

from base import BaseIntelligenceService
from sop_20_contract_setup.sop_20_templates import SETUP_ITEM_CATEGORIES

SYSTEM_PROMPT = """You are HCI's Contract Setup AI (SOP 20).
Review contract documents, generate setup checklists, and flag contract risks before project execution.
RULES:
- Return only structured JSON
- Flag any non-standard contract terms that deviate from HCI norms
- Never approve or sign contracts — human authority required
- Flag ambiguous scope, unusual payment terms, or missing provisions
"""


class SOP20Agent(BaseIntelligenceService):
    SERVICE_NAME = "sop_20_agent"
    STATUS = "active"

    @classmethod
    def generate_setup_checklist(cls, contract_type: str, project_type: str,
                                  contract_value: float, owner_name: str) -> dict:
        prompt = f"""Generate a contract setup checklist for this project.

CONTRACT TYPE: {contract_type}
PROJECT TYPE: {project_type}
CONTRACT VALUE: ${contract_value:,.2f}
OWNER: {owner_name}
CATEGORIES: {SETUP_ITEM_CATEGORIES}

Return JSON:
{{
  "checklist_items": [
    {{
      "item_code": "CS-001",
      "category": "<category>",
      "description": "<what needs to be done>",
      "responsible_party": "PM|Principal|Accounting",
      "due_date_offset": "<e.g. 'Before NTP' or 'Within 5 days of execution'>",
      "priority": "HIGH|MEDIUM|LOW"
    }}
  ],
  "critical_items": ["<item_code of critical items>"],
  "ai_note": "AI CONTRACT SETUP CHECKLIST — PM TO REVIEW AND ASSIGN"
}}
Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1500)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "checklist_items": [], "ai_note": "AI checklist failed — build manually"}

    @classmethod
    def review_contract_terms(cls, contract_type: str, contract_value: float,
                               scope_summary: str, special_conditions: str = "") -> dict:
        prompt = f"""Review this prime contract for risks and non-standard terms.

CONTRACT TYPE: {contract_type}
VALUE: ${contract_value:,.2f}
SCOPE: {scope_summary}
SPECIAL CONDITIONS: {special_conditions or 'None noted'}

Flag any risks HCI should be aware of before executing this contract.

Return JSON:
{{
  "risk_level": "LOW|MEDIUM|HIGH",
  "flagged_items": [{{"item": "<description>", "severity": "LOW|MEDIUM|HIGH", "recommendation": "<action>"}}],
  "missing_provisions": ["<provision that should be in the contract>"],
  "owner_unusual_requirements": ["<unusual owner requirement>"],
  "ai_note": "AI CONTRACT REVIEW — PM AND PRINCIPAL TO CONFIRM BEFORE EXECUTION"
}}
Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1024)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "risk_level": "MEDIUM"}

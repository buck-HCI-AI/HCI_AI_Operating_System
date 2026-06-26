"""SOP 18 — Layer 3: Long-Lead Procurement AI Agent."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "api"))

from base import BaseIntelligenceService
from sop_18_long_lead.sop_18_templates import TYPICAL_LONG_LEAD_ITEMS

SYSTEM_PROMPT = """You are HCI's Long-Lead Procurement AI (SOP 18).
Identify long-lead items, estimate lead times, flag procurement risks, and suggest suppliers.
RULES:
- Return only structured JSON
- Base lead times on real construction procurement experience
- Flag any item with lead time > 16 weeks as CRITICAL
- Always recommend 10-20% buffer on stated lead times
"""


class SOP18Agent(BaseIntelligenceService):
    SERVICE_NAME = "sop_18_agent"
    STATUS = "active"

    @classmethod
    def identify_long_lead_items(cls, project_type: str, narrative_summary: str,
                                  construction_start: str) -> dict:
        results = cls.search(
            f"{project_type} long lead procurement equipment",
            collection="hci_historical_costs", limit=5,
        )
        history = "\n".join(r.get("payload", {}).get("text", "") for r in results) or "No procurement history."

        prompt = f"""Identify long-lead procurement items for this construction project.

PROJECT TYPE: {project_type}
CONSTRUCTION START: {construction_start}
SCOPE: {narrative_summary or 'General construction'}
KNOWN LONG-LEAD CATEGORIES: {TYPICAL_LONG_LEAD_ITEMS}
HISTORICAL DATA: {history}

Return JSON:
{{
  "items": [
    {{
      "description": "<item description>",
      "trade_code": "<CSI code>",
      "lead_time_weeks": <int>,
      "order_by_date": "YYYY-MM-DD",
      "required_on_site": "YYYY-MM-DD",
      "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
      "suggested_suppliers": ["<supplier name>"],
      "notes": "<procurement note>"
    }}
  ],
  "critical_count": <int>,
  "immediate_action_items": ["<item needing order this week>"],
  "ai_note": "AI LONG-LEAD IDENTIFICATION — PM TO CONFIRM AND INITIATE RFQs"
}}
Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1500)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "items": [], "ai_note": "AI identification failed — review manually"}

    @classmethod
    def flag_procurement_risks(cls, items: list[dict], construction_start: str) -> dict:
        critical = [i for i in items if i.get("risk_level") in ("HIGH", "CRITICAL")]
        prompt = f"""Flag procurement risks for these long-lead items.

CONSTRUCTION START: {construction_start}
TOTAL ITEMS: {len(items)}
HIGH/CRITICAL ITEMS: {len(critical)}
ITEMS SUMMARY:
{chr(10).join(f"- {i.get('description')} | {i.get('lead_time_weeks')}wks | {i.get('risk_level')}" for i in items[:15])}

Return JSON:
{{
  "procurement_risk": "LOW|MEDIUM|HIGH|CRITICAL",
  "at_risk_items": [{{"description": "<item>", "risk": "<specific risk>", "mitigation": "<action>"}}],
  "schedule_impact_warning": "<warning if items may delay construction start>",
  "recommended_actions": ["<action 1>"],
  "ai_note": "AI PROCUREMENT RISK ASSESSMENT — PM TO ACTION"
}}
Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1024)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "procurement_risk": "MEDIUM"}

    @classmethod
    def suggest_suppliers(cls, item_description: str, trade_code: str) -> dict:
        results = cls.search(
            f"{item_description} {trade_code} supplier vendor",
            collection="vendor_memory", limit=5,
        )
        known = [r.get("payload", {}).get("company_name", "") for r in results if r.get("payload", {}).get("company_name")]
        return {
            "item": item_description,
            "known_suppliers": known,
            "ai_note": "Supplier list from vendor intelligence — PM to confirm and solicit quotes",
        }

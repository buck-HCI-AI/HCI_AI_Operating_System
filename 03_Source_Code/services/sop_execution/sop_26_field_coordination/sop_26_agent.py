"""SOP 26 — Layer 3: Field Coordination AI Agent."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "api"))

from base import BaseIntelligenceService
from sop_26_field_coordination.sop_26_templates import COORD_TYPES

SYSTEM_PROMPT = """You are HCI's Field Coordination AI (SOP 26).
Prioritize RFIs, submittals, and coordination issues. Draft responses and flag items with cost or schedule impact.
RULES:
- Return only structured JSON
- CRITICAL items require same-day PM notification
- Always flag cost and schedule impact potential
- Draft responses are for PM review — never send directly
"""


class SOP26Agent(BaseIntelligenceService):
    SERVICE_NAME = "sop_26_agent"
    STATUS = "active"

    @classmethod
    def prioritize_coordination_items(cls, items: list[dict]) -> dict:
        critical = [i for i in items if i.get("priority") == "CRITICAL"]
        cost_impact = [i for i in items if i.get("cost_impact")]
        schedule_impact = [i for i in items if i.get("schedule_impact")]

        prompt = f"""Prioritize these field coordination items.

TOTAL OPEN ITEMS: {len(items)}
CRITICAL: {len(critical)}
COST IMPACT: {len(cost_impact)}
SCHEDULE IMPACT: {len(schedule_impact)}

ITEM SUMMARY:
{chr(10).join(f"- [{i.get('item_code')}] {i.get('coord_type')}: {i.get('description')[:80]} | Priority: {i.get('priority')}" for i in items[:15])}

Return JSON:
{{
  "priority_order": ["<item_code>"],
  "escalation_required": ["<item_code of items needing PM today>"],
  "cost_impact_items": ["<item_code>"],
  "schedule_impact_items": ["<item_code>"],
  "recommended_actions": [{{"item_code": "<code>", "action": "<what to do>", "deadline": "<timeframe>"}}],
  "ai_note": "AI PRIORITIZATION — PM TO REVIEW AND ACTION"
}}
Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1024)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "priority_order": [], "escalation_required": [c.get("item_code") for c in critical]}

    @classmethod
    def draft_rfi_response(cls, item_code: str, description: str,
                            drawing_refs: list[str], spec_refs: list[str],
                            project_type: str) -> dict:
        results = cls.search(
            f"RFI response {description[:60]} {project_type}",
            collection="lessons_learned", limit=3,
        )
        history = "\n".join(r.get("payload", {}).get("text", "") for r in results) or "No similar RFI history."

        prompt = f"""Draft a response to this RFI.

RFI CODE: {item_code}
QUESTION: {description}
DRAWING REFS: {drawing_refs}
SPEC REFS: {spec_refs}
SIMILAR RFI HISTORY: {history}

Return JSON:
{{
  "draft_response": "<professional RFI response text — factual, references specs/drawings>",
  "cost_impact": <true|false>,
  "schedule_impact": <true|false>,
  "follow_up_required": <true|false>,
  "referenced_documents": ["<doc ref>"],
  "ai_note": "AI DRAFT RESPONSE — PM OR A/E TO REVIEW AND ISSUE"
}}
Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1024)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "draft_response": "AI draft failed — write manually"}

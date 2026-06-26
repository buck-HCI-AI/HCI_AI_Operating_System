"""SOP 28 — Layer 3: QC Detail Card AI Agent."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "api"))

from base import BaseIntelligenceService

SYSTEM_PROMPT = """You are HCI's QC Detail Card AI (SOP 28).
Draft trade-specific QC detail cards with work items, hold points, acceptance criteria, and specification references.
RULES:
- Return only structured JSON
- Hold points MUST be cleared by inspector before work proceeds
- Reference specific specification sections
- Cards are per-trade and used by the superintendent in the field
"""


class SOP28Agent(BaseIntelligenceService):
    SERVICE_NAME = "sop_28_agent"
    STATUS = "active"

    @classmethod
    def draft_detail_card(cls, trade_code: str, trade_name: str,
                           project_type: str, spec_sections: list[str]) -> dict:
        results = cls.search(
            f"{trade_name} {trade_code} quality detail card specification",
            collection="lessons_learned", limit=3,
        )
        lessons = "\n".join(r.get("payload", {}).get("text", "") for r in results) or "No detail card history."

        prompt = f"""Draft a QC detail card for this trade.

TRADE: {trade_name} (CSI {trade_code})
PROJECT TYPE: {project_type}
SPEC SECTIONS: {spec_sections or ['Not specified']}
LESSONS LEARNED: {lessons}

Return JSON:
{{
  "trade_code": "{trade_code}",
  "trade_name": "{trade_name}",
  "specification_sections": {spec_sections or []},
  "work_items": [
    {{
      "work_item_code": "{trade_code[:4]}-WI-001",
      "description": "<work item to inspect>",
      "specification_ref": "<spec section>",
      "acceptance_criteria": "<pass criteria>",
      "hold_point": <true|false>,
      "inspection_method": "Visual|Measurement|Test",
      "frequency": "Each pour|Per floor|Final|etc.",
      "responsible_party": "Superintendent|Inspector|Engineer"
    }}
  ],
  "ai_note": "AI QC DETAIL CARD DRAFT — PM AND SUPERINTENDENT TO REVIEW"
}}
Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1500)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "work_items": [], "ai_note": "AI card draft failed"}

    @classmethod
    def validate_specification_compliance(cls, work_items: list[dict],
                                           trade_name: str) -> dict:
        missing_spec = [w for w in work_items if not w.get("specification_ref")]
        prompt = f"""Validate this QC detail card for specification compliance.

TRADE: {trade_name}
TOTAL WORK ITEMS: {len(work_items)}
ITEMS WITHOUT SPEC REFS: {len(missing_spec)}

Return JSON:
{{
  "compliance_status": "COMPLETE|INCOMPLETE|GAPS_FOUND",
  "gaps": ["<work item missing specification reference>"],
  "recommendations": ["<how to improve the card>"],
  "ai_note": "AI SPEC COMPLIANCE CHECK — PM TO RESOLVE GAPS"
}}
Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=768)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "compliance_status": "INCOMPLETE"}

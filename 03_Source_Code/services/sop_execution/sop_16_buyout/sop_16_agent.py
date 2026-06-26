"""SOP 16 — Layer 3: Buyout AI Agent."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "api"))

from base import BaseIntelligenceService


SYSTEM_PROMPT = """You are HCI's Preconstruction AI for Buyout (SOP 16).

Your job is to draft award memos and verify scope alignment between what was leveled
in SOP 15 and what the awarded sub understands they are responsible for.

RULES:
- Return only structured JSON
- Never issue a commitment, send a subcontract, or contact a sub directly
- Never confirm an award — only Buck can authorize awards
- Flag any scope discrepancy between the leveled scope and the sub's stated scope
- All award memos are DRAFTS requiring PM review and Buck authorization before issuance
- Note any contract conditions or waivers that came out of the leveling process
"""


class SOP16Agent(BaseIntelligenceService):
    SERVICE_NAME = "sop_16_agent"
    STATUS = "active"

    @classmethod
    def draft_award_memo(cls, awarded_sub: str, trade_name: str, trade_code: str,
                         award_amount: float, scope_basis: str,
                         subcontract_type: str = "lump_sum",
                         conditions: str = "", rationale: str = "") -> dict:
        """Draft an award memo for PM review and Buck authorization."""
        # Search vendor history for any prior relationship notes
        vendor_results = cls.search(
            f"{awarded_sub} {trade_name} performance history",
            collection="vendor_memory",
            limit=3,
        )
        vendor_context = "\n".join(
            r.get("payload", {}).get("text", "") for r in vendor_results
        ) or "No prior vendor history found."

        prompt = f"""Draft an award memo for a subcontractor award decision.

AWARDED SUB: {awarded_sub}
TRADE: {trade_name} (CSI: {trade_code})
AWARD AMOUNT: ${award_amount:,.2f}
CONTRACT TYPE: {subcontract_type}
SCOPE BASIS: {scope_basis}
CONDITIONS / WAIVERS: {conditions or 'None'}
AWARD RATIONALE: {rationale or 'Best value — confirmed by bid leveling (SOP 15)'}

VENDOR HISTORY:
{vendor_context}

Return JSON:
{{
  "memo_title": "AWARD MEMO — {trade_name}",
  "memo_body": "<formal award memo text, 200-300 words — professional construction industry tone>",
  "key_terms": [
    {{"term": "<contract term>", "value": "<value or description>"}}
  ],
  "scope_inclusions": ["<item included in scope>"],
  "scope_exclusions_to_confirm": ["<item excluded — must be confirmed before subcontract>"],
  "open_items": ["<any items not yet resolved>"],
  "conditions_precedent": ["<conditions that must be met before award is final>"],
  "ai_note": "AI DRAFT — PM TO REVIEW, BUCK TO AUTHORIZE BEFORE ISSUANCE"
}}

Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=2000)
            result = cls.parse_json_response(raw)
            result.update({
                "awarded_sub": awarded_sub,
                "award_amount": award_amount,
                "subcontract_type": subcontract_type,
            })
            return result
        except Exception as e:
            return {"error": str(e), "awarded_sub": awarded_sub,
                    "ai_note": "AI draft failed — compose award memo manually"}

    @classmethod
    def check_scope_alignment(cls, leveled_scope: str, sub_scope_statement: str,
                              trade_name: str) -> dict:
        """Compare the leveled scope basis with the sub's scope statement for discrepancies."""
        prompt = f"""Compare these two scope statements for a {trade_name} subcontract.

LEVELED SCOPE (from SOP 15 bid leveling):
{leveled_scope}

SUB'S SCOPE STATEMENT (from their bid or pre-award clarification):
{sub_scope_statement}

Identify any discrepancies, gaps, or items one party includes that the other excludes.

Return JSON:
{{
  "aligned": <true if no material discrepancies>,
  "discrepancies": [
    {{
      "item": "<scope item in question>",
      "leveled_includes": <true|false>,
      "sub_includes": <true|false>,
      "severity": "HIGH|MEDIUM|LOW",
      "resolution_required": "<what needs to happen before subcontract is signed>"
    }}
  ],
  "missing_items": ["<item in leveled scope not addressed by sub>"],
  "extra_items_sub_claims": ["<item sub claims but was not in leveled scope>"],
  "confidence": "HIGH|MEDIUM|LOW",
  "ai_note": "AI SCOPE COMPARISON — PM MUST CONFIRM WITH SUB BEFORE EXECUTING SUBCONTRACT"
}}

Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1500)
            result = cls.parse_json_response(raw)
            result["trade_name"] = trade_name
            return result
        except Exception as e:
            return {"error": str(e), "aligned": False, "trade_name": trade_name,
                    "ai_note": "AI scope check failed — perform manual comparison"}

"""SOP 14 — Layer 3: Bid Follow-Up AI Agent."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "api"))

from base import BaseIntelligenceService


SYSTEM_PROMPT = """You are HCI's Preconstruction AI for Bid Follow-Up (SOP 14).

Your job is to assist the PM in tracking subcontractor responses, drafting follow-up
messages, and ensuring enough responsive subs are confirmed before bid close.

RULES:
- Return only structured JSON
- Never contact a sub directly — draft follow-up content only; PM sends
- Never accept a late bid without PM authorization
- Never include a declined sub in the responsive count
- Flag when confirmed bidders + received bids < 3 before bid due date
"""


class SOP14Agent(BaseIntelligenceService):
    SERVICE_NAME = "sop_14_agent"
    STATUS = "active"

    @classmethod
    def draft_follow_up_message(cls, sub_name: str, trade_name: str,
                                bid_due_date: str, days_until_due: int,
                                contact_name: str = "") -> dict:
        """Draft a follow-up message for a non-responsive sub."""
        urgency = "urgent" if days_until_due <= 3 else "standard"
        prompt = f"""Draft a follow-up message for a subcontractor who has not yet confirmed bidding intent.

SUB NAME: {sub_name}
TRADE: {trade_name}
BID DUE DATE: {bid_due_date}
DAYS UNTIL DUE: {days_until_due}
URGENCY: {urgency}
CONTACT: {contact_name or 'Estimating Team'}

Return JSON:
{{
  "subject_line": "<email subject>",
  "message_body": "<professional follow-up message, 80-120 words>",
  "call_to_action": "<specific ask — confirm by date, call PM, etc.>",
  "urgency_level": "standard|urgent",
  "ai_note": "AI DRAFT — PM TO REVIEW BEFORE SENDING"
}}

Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=512)
            result = cls.parse_json_response(raw)
            result["sub_name"] = sub_name
            result["days_until_due"] = days_until_due
            return result
        except Exception as e:
            return {"error": str(e), "sub_name": sub_name,
                    "ai_note": "AI draft failed — compose manually"}

    @classmethod
    def summarize_response_status(cls, follow_up_records: list[dict],
                                  trade_name: str, bid_due_date: str) -> dict:
        """Produce a summary of current bid response status for PM review."""
        confirmed = [r for r in follow_up_records
                     if r.get("response_status") in ("confirmed", "bid_received")]
        declined = [r for r in follow_up_records
                    if r.get("response_status") == "declined"]
        no_response = [r for r in follow_up_records
                       if r.get("response_status") in ("pending", "contacted", "no_response")]

        ready = len(confirmed) >= 3
        prompt = f"""Summarize the bid follow-up status for PM review.

TRADE: {trade_name}
BID DUE DATE: {bid_due_date}
CONFIRMED BIDDING: {len(confirmed)} subs — {[r['sub_name'] for r in confirmed]}
DECLINED: {len(declined)} subs
NO RESPONSE YET: {len(no_response)} subs — {[r['sub_name'] for r in no_response]}
MINIMUM REQUIRED: 3 responsive subs

Return JSON:
{{
  "status_summary": "<2-3 sentence summary of where things stand>",
  "ready_for_close": {str(ready).lower()},
  "action_items": ["<action 1>", "<action 2>"],
  "risk_level": "LOW|MEDIUM|HIGH",
  "ai_note": "AI SUMMARY — PM TO CONFIRM"
}}

Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=512)
            result = cls.parse_json_response(raw)
            result.update({
                "confirmed_count": len(confirmed),
                "declined_count": len(declined),
                "no_response_count": len(no_response),
            })
            return result
        except Exception as e:
            return {
                "error": str(e),
                "confirmed_count": len(confirmed),
                "ready_for_close": ready,
            }

    @classmethod
    def flag_minimum_bid_risk(cls, confirmed_count: int, days_until_due: int,
                              trade_name: str) -> dict | None:
        """Return a risk flag if minimum bids are at risk before close."""
        if confirmed_count >= 3:
            return None
        gap = 3 - confirmed_count
        return {
            "risk_type": "MINIMUM_BID_COVERAGE",
            "trade": trade_name,
            "confirmed_bidders": confirmed_count,
            "minimum_required": 3,
            "gap": gap,
            "days_until_close": days_until_due,
            "severity": "HIGH" if days_until_due <= 3 else "MEDIUM",
            "action_required": (
                f"Confirm {gap} additional bidder(s) for {trade_name} before bid close, "
                "or notify PM and Buck to authorize MIN_BIDDERS exception."
            ),
        }

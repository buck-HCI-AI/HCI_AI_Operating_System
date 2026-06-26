"""SOP 13 — Layer 3: Bid Distribution AI Agent."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "api"))

from base import BaseIntelligenceService


SYSTEM_PROMPT = """You are HCI's Preconstruction AI for Bid Distribution (SOP 13).

Your job is to draft subcontractor outreach emails and confirm that the bid distribution
list is complete and correct before the package goes out.

RULES:
- Return only structured JSON
- Never send emails directly — draft only; PM distributes
- Never modify the scope or bid package content
- Flag any sub on the list with a prior disqualification or known performance issue
- Mark all drafted content as requiring PM review before sending
"""


class SOP13Agent(BaseIntelligenceService):
    SERVICE_NAME = "sop_13_agent"
    STATUS = "active"

    @classmethod
    def draft_outreach_email(cls, project_name: str, trade_name: str,
                             bid_due_date: str, scope_summary: str,
                             contact_name: str = "") -> dict:
        """Draft an outreach email to send with the bid package."""
        greeting = f"Dear {contact_name}" if contact_name else "Dear Estimating Team"
        prompt = f"""Draft a professional bid invitation email for a subcontractor.

PROJECT: {project_name}
TRADE: {trade_name}
BID DUE DATE: {bid_due_date}
SCOPE SUMMARY: {scope_summary}
RECIPIENT GREETING: {greeting}

Return JSON:
{{
  "subject_line": "<email subject>",
  "body_text": "<plain text email body — professional, concise, 150-200 words>",
  "required_attachments": ["<attachment 1>", "<attachment 2>"],
  "response_instructions": "<how sub should submit bid>",
  "ai_note": "AI DRAFT — PM TO REVIEW AND PERSONALIZE BEFORE SENDING"
}}

Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1024)
            result = cls.parse_json_response(raw)
            result["trade_name"] = trade_name
            result["bid_due_date"] = bid_due_date
            return result
        except Exception as e:
            return {"error": str(e), "trade_name": trade_name,
                    "ai_note": "AI draft failed — compose manually"}

    @classmethod
    def check_distribution_coverage(cls, distribution_records: list[dict],
                                    required_trades: list[str]) -> dict:
        """Check that all required trades have ≥ 3 subs on the distribution list."""
        trade_counts: dict[str, int] = {}
        for rec in distribution_records:
            tc = rec.get("trade_code", "")
            trade_counts[tc] = trade_counts.get(tc, 0) + 1

        gaps = []
        for trade in required_trades:
            count = trade_counts.get(trade, 0)
            if count < 3:
                gaps.append({
                    "trade_code": trade,
                    "subs_on_list": count,
                    "minimum_required": 3,
                    "gap": 3 - count,
                })

        return {
            "trade_counts": trade_counts,
            "gaps": gaps,
            "coverage_complete": len(gaps) == 0,
            "ai_note": "Distribution coverage check — operating rule MIN_BIDDERS applies",
        }

    @classmethod
    def flag_sub_risks(cls, sub_list: list[dict], trade_name: str) -> dict:
        """Flag any subs with known performance issues based on vendor intelligence."""
        # Query vendor memory for any negative signals
        results = cls.search(
            f"performance issue complaint disqualified {trade_name}",
            collection="vendor_memory",
            limit=5,
        )
        flagged = []
        for r in results:
            payload = r.get("payload", {})
            sub_name = payload.get("company_name", "")
            if sub_name and any(
                s.get("sub_name", "").lower() == sub_name.lower()
                for s in sub_list
            ):
                flagged.append({
                    "sub_name": sub_name,
                    "signal": payload.get("note", "Performance flag from vendor intelligence"),
                    "severity": "REVIEW",
                })
        return {
            "flagged_subs": flagged,
            "ai_note": "AI risk check — PM to review flagged subs before distribution",
        }

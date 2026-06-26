"""SOP 12 — Layer 3: Subcontractor CRM AI Agent."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "api"))

from base import BaseIntelligenceService


SYSTEM_PROMPT = """You are HCI's Subcontractor CRM AI (SOP 12).

Your job is to help identify qualified subcontractors for each trade, surface
performance history, and ensure the bid list meets HCI's minimum bidder rule (3 per trade).

RULES:
- Return only structured JSON
- Never contact a sub directly
- Never add a sub to a bid list without PM confirmation
- Flag any sub with a DO_NOT_USE or CONDITIONAL rating
- Recommend PREFERRED and QUALIFIED subs first; flag CONDITIONAL subs for PM review
- The MIN_BIDDERS rule (minimum 3 per trade) is an operating rule — flag if not met
"""


class SOP12Agent(BaseIntelligenceService):
    SERVICE_NAME = "sop_12_agent"
    STATUS = "active"

    @classmethod
    def research_sub_candidates(cls, trade_code: str, trade_name: str,
                                 project_type: str = "") -> dict:
        """Search vendor intelligence for qualified subs in a given trade."""
        results = cls.search(
            f"{trade_name} {trade_code} subcontractor qualified performance",
            collection="vendor_memory",
            limit=10,
        )
        candidates = []
        for r in results:
            payload = r.get("payload", {})
            if payload.get("company_name"):
                candidates.append({
                    "sub_name": payload.get("company_name"),
                    "trade_code": trade_code,
                    "performance_rating": payload.get("performance_rating", "QUALIFIED"),
                    "last_hci_project": payload.get("last_project", ""),
                    "contact_email": payload.get("email", ""),
                    "ai_risk_flag": payload.get("risk_flag", ""),
                    "notes": payload.get("notes", ""),
                })

        prompt = f"""Review this list of subcontractor candidates for {trade_name} (CSI {trade_code}).

PROJECT TYPE: {project_type or 'commercial'}
CANDIDATES FROM VENDOR DATABASE: {len(candidates)} found

{chr(10).join(f"- {c['sub_name']} (rating: {c.get('performance_rating','?')}, risk: {c.get('ai_risk_flag','none')})" for c in candidates) or "No candidates found in vendor database."}

Return JSON:
{{
  "recommended": [
    {{
      "sub_name": "<name>",
      "reason": "<why this sub is recommended>",
      "rating": "PREFERRED|QUALIFIED|CONDITIONAL"
    }}
  ],
  "flagged": [
    {{
      "sub_name": "<name>",
      "flag": "<reason for flag>",
      "severity": "HIGH|MEDIUM"
    }}
  ],
  "coverage_adequate": <true if >= 3 qualified subs>,
  "gap_action": "<what to do if < 3 qualified subs>",
  "ai_note": "AI RECOMMENDATION — PM TO CONFIRM BID LIST"
}}

Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1024)
            result = cls.parse_json_response(raw)
            result["raw_candidates"] = candidates
            result["candidate_count"] = len(candidates)
            return result
        except Exception as e:
            return {"error": str(e), "raw_candidates": candidates,
                    "coverage_adequate": len(candidates) >= 3,
                    "ai_note": "AI research failed — review vendor list manually"}

    @classmethod
    def assess_sub_qualification(cls, sub_name: str, trade_code: str,
                                  bonded: bool, insured: bool,
                                  license_number: str = "") -> dict:
        """AI assesses a specific sub's qualification for HCI bid lists."""
        results = cls.search(
            f"{sub_name} {trade_code} performance history",
            collection="vendor_memory",
            limit=5,
        )
        history = "\n".join(
            r.get("payload", {}).get("text", "") for r in results
        ) or "No prior history found in vendor intelligence."

        prompt = f"""Assess this subcontractor's qualification for an HCI bid list.

SUB NAME: {sub_name}
TRADE CODE: {trade_code}
BONDED: {bonded}
INSURED: {insured}
LICENSE NUMBER: {license_number or 'not provided'}

VENDOR HISTORY:
{history}

Return JSON:
{{
  "sub_name": "{sub_name}",
  "recommended_rating": "PREFERRED|QUALIFIED|CONDITIONAL|DO_NOT_USE",
  "qualification_status": "QUALIFIED|CONDITIONAL|DISQUALIFIED",
  "issues": ["<issue 1 if any>"],
  "strengths": ["<strength 1>"],
  "risk_flag": "<brief flag or empty string if clean>",
  "ai_note": "AI QUALIFICATION ASSESSMENT — PM TO CONFIRM"
}}

Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=768)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "sub_name": sub_name,
                    "qualification_status": "CONDITIONAL",
                    "ai_note": "AI assessment failed — review manually"}

    @classmethod
    def assess_bid_list_quality(cls, approved_subs: list[dict],
                                 trade_name: str) -> dict:
        """Final quality check: is the bid list ready to hand to SOP 13?"""
        count = len(approved_subs)
        if count < 3:
            return {
                "ready": False,
                "reason": f"Only {count} approved subs for {trade_name} — minimum 3 required (MIN_BIDDERS rule)",
                "gap": 3 - count,
                "ai_note": "MIN_BIDDERS operating rule enforcement — PM must add subs or obtain exception",
            }
        flagged = [s for s in approved_subs if s.get("ai_risk_flag")]
        conditional = [s for s in approved_subs if s.get("performance_rating") == "CONDITIONAL"]
        return {
            "ready": True,
            "approved_count": count,
            "flagged_subs": flagged,
            "conditional_subs": conditional,
            "recommendation": (
                "PROCEED — list meets minimum bidder requirement."
                if not flagged and not conditional
                else "PROCEED WITH CAUTION — flagged/conditional subs on list. PM to review."
            ),
            "ai_note": "AI BID LIST QUALITY CHECK — PM TO CONFIRM",
        }

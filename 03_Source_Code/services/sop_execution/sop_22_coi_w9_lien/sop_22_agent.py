"""SOP 22 — Layer 3: COI / W-9 / Lien Waiver AI Agent."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "api"))

from base import BaseIntelligenceService
from sop_22_coi_w9_lien.sop_22_templates import HCI_COI_MINIMUMS, DOC_TYPES

SYSTEM_PROMPT = """You are HCI's Compliance Document AI (SOP 22).
Verify COIs, W-9s, and lien waivers. Flag deficiencies before any sub starts work or payment is released.
RULES:
- Return only structured JSON
- A sub may not start work without a verified COI meeting HCI minimums
- Payment must not be released without conditional lien waivers
- Final payment requires unconditional lien waivers
"""


class SOP22Agent(BaseIntelligenceService):
    SERVICE_NAME = "sop_22_agent"
    STATUS = "active"

    @classmethod
    def generate_doc_checklist(cls, subs: list[str], project_type: str) -> dict:
        """Generate the compliance doc collection checklist for all subs."""
        items = []
        for i, sub in enumerate(subs, 1):
            for doc_type in DOC_TYPES:
                items.append({
                    "doc_code": f"DOC-{i:02d}-{doc_type[:3]}",
                    "doc_type": doc_type,
                    "party_name": sub,
                    "party_role": "subcontractor",
                    "status": "REQUESTED",
                    "priority": "HIGH" if doc_type == "COI" else "MEDIUM",
                })
        return {
            "checklist": items,
            "total_docs_required": len(items),
            "ai_note": "AI DOC CHECKLIST — PM TO COLLECT AND VERIFY BEFORE WORK STARTS",
        }

    @classmethod
    def verify_coi_coverage(cls, sub_name: str, provided_limits: dict) -> dict:
        """Check COI against HCI minimums."""
        flags = []
        for coverage, min_val in HCI_COI_MINIMUMS.items():
            provided = provided_limits.get(coverage, 0)
            if provided < min_val:
                flags.append({
                    "coverage": coverage,
                    "required": min_val,
                    "provided": provided,
                    "shortfall": min_val - provided,
                    "severity": "HIGH",
                })
        return {
            "sub_name": sub_name,
            "meets_minimums": len(flags) == 0,
            "deficiencies": flags,
            "work_authorization": "HOLD — COI deficiencies must be resolved" if flags else "CLEAR — COI meets HCI minimums",
            "ai_note": "AI COI VERIFICATION — PM TO CONFIRM CERTIFICATES ON FILE",
        }

    @classmethod
    def flag_expiring_docs(cls, docs: list[dict], days_ahead: int = 30) -> dict:
        """Flag COIs and other time-sensitive docs expiring soon."""
        from datetime import date, timedelta
        today = date.today()
        warning_date = (today + timedelta(days=days_ahead)).isoformat()
        expiring = [
            d for d in docs
            if d.get("expiry_date") and d["expiry_date"] <= warning_date
            and d.get("status") == "VERIFIED"
        ]
        return {
            "expiring_count": len(expiring),
            "expiring_docs": expiring,
            "action_required": len(expiring) > 0,
            "ai_note": f"Docs expiring within {days_ahead} days — PM to request renewals",
        }

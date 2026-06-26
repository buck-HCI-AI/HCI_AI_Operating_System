"""SOP 19 — Layer 3: Subcontract Agreement AI Agent."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "api"))

from base import BaseIntelligenceService
from sop_19_subcontract_agreement.sop_19_templates import HCI_INSURANCE_MINIMUMS, CONTRACT_SECTIONS


SYSTEM_PROMPT = """You are HCI's Subcontract Agreement AI (SOP 19).

Your job is to draft subcontract sections and flag issues before PM review and execution.

RULES:
- Return only structured JSON
- All drafted content is a DRAFT requiring PM review and principal/PM signature before execution
- Never represent content as legally binding — that requires human execution
- Flag any scope language that conflicts with the award memo or bid leveling record
- Insurance requirements must meet HCI minimums — flag if not
- No subcontract may be executed without Gate 19-C (principal or authorized PM signature)
"""


class SOP19Agent(BaseIntelligenceService):
    SERVICE_NAME = "sop_19_agent"
    STATUS = "active"

    @classmethod
    def draft_scope_section(cls, awarded_sub: str, trade_name: str,
                             trade_code: str, scope_basis: str,
                             award_amount: float,
                             conditions: str = "") -> dict:
        """AI drafts the scope of work section for a subcontract."""
        prompt = f"""Draft a scope of work section for a subcontract agreement.

SUBCONTRACTOR: {awarded_sub}
TRADE: {trade_name} (CSI: {trade_code})
CONTRACT SUM: ${award_amount:,.2f}
SCOPE BASIS: {scope_basis}
CONDITIONS / QUALIFICATIONS: {conditions or 'None noted'}

Draft a clear, unambiguous scope of work section that:
- Defines what is included in the contract sum
- Lists specific exclusions
- References applicable drawings and specifications
- Notes any allowances or unit prices if applicable

Return JSON:
{{
  "section_type": "scope_of_work",
  "content": "<full scope of work text, 200-400 words, professional construction contract language>",
  "inclusions_summary": ["<key included item 1>", "<item 2>"],
  "exclusions_summary": ["<key excluded item 1>"],
  "issues_flagged": ["<any ambiguity or gap that needs resolution>"],
  "ai_note": "AI DRAFT — PM TO REVIEW; PRINCIPAL/PM TO EXECUTE"
}}

Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1500)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "section_type": "scope_of_work",
                    "ai_note": "AI draft failed — write scope manually"}

    @classmethod
    def draft_contract_section(cls, section_type: str, awarded_sub: str,
                                trade_name: str, award_amount: float,
                                project_context: dict | None = None) -> dict:
        """AI drafts a standard contract section (payment terms, schedule, insurance, etc.)."""
        ctx = project_context or {}
        contract_sum_text = f"${award_amount:,.2f}"
        insurance_mins = (
            f"GL: ${HCI_INSURANCE_MINIMUMS['general_liability']:,}/occurrence, "
            f"${HCI_INSURANCE_MINIMUMS['aggregate']:,} aggregate; "
            f"WC: ${HCI_INSURANCE_MINIMUMS['workers_comp']:,}; "
            f"Auto: ${HCI_INSURANCE_MINIMUMS['auto_liability']:,}"
        )

        section_guidance = {
            "contract_sum":       f"Contract sum is {contract_sum_text}. Include schedule of values, change order provisions.",
            "payment_terms":      "Net 30 from invoice approval. Retainage 10% through substantial completion. Include lien waiver requirements.",
            "schedule_of_work":   f"Commencement, milestones, and completion date. Include liquidated damages provision if applicable.",
            "insurance_requirements": f"HCI minimums: {insurance_mins}. HCI and owner additional insured. Certificate of insurance required before work begins.",
            "general_conditions": "Incorporate HCI General Conditions by reference. Safety, daily logs, RFI process, submittals.",
            "special_conditions": f"Project-specific requirements for {trade_name}. AHJ requirements, inspection hold points, testing.",
        }.get(section_type, f"Standard {section_type} section for {trade_name} subcontract.")

        prompt = f"""Draft the '{section_type}' section for a subcontract agreement.

SUBCONTRACTOR: {awarded_sub}
TRADE: {trade_name}
CONTRACT SUM: {contract_sum_text}
GUIDANCE: {section_guidance}

Return JSON:
{{
  "section_type": "{section_type}",
  "content": "<full section text — professional construction contract language>",
  "issues_flagged": ["<any item needing PM attention or clarification>"],
  "ai_note": "AI DRAFT — PM TO REVIEW AND CONFIRM"
}}

Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1200)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "section_type": section_type,
                    "ai_note": f"AI draft failed for {section_type} — write manually"}

    @classmethod
    def verify_insurance_requirements(cls, sub_name: str,
                                       provided_limits: dict) -> dict:
        """Check that the sub's stated insurance meets HCI minimums."""
        flags = []
        for coverage, min_val in HCI_INSURANCE_MINIMUMS.items():
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
            "action_required": (
                f"{sub_name} must provide compliant certificates before work begins."
                if flags else None
            ),
            "ai_note": "INSURANCE VERIFICATION — PM TO CONFIRM CERTIFICATES ON FILE",
        }

    @classmethod
    def review_full_draft(cls, sections: list[dict], awarded_sub: str,
                           trade_name: str, award_amount: float) -> dict:
        """AI reviews all sections together for consistency before PM approval."""
        present = [s.get("section_type") for s in sections]
        missing = [s for s in CONTRACT_SECTIONS if s not in present]

        all_issues = []
        for s in sections:
            for issue in s.get("issues_flagged", []):
                all_issues.append({"section": s["section_type"], "issue": issue})

        sections_text = "\n".join(
            f"- {s.get('section_type','?')}: {len(s.get('content',''))} chars "
            f"({'PM confirmed' if s.get('pm_confirmed') else 'pending'})"
            for s in sections
        )
        prompt = f"""Review this subcontract draft for {awarded_sub} ({trade_name}) before PM approval.

CONTRACT SUM: ${award_amount:,.2f}
SECTIONS PRESENT: {len(sections)}/{len(CONTRACT_SECTIONS)}
MISSING SECTIONS: {missing or 'None'}

SECTION STATUS:
{sections_text}

FLAGGED ISSUES ACROSS ALL SECTIONS: {len(all_issues)}
{chr(10).join(f"- [{i['section']}] {i['issue']}" for i in all_issues[:10]) or 'None'}

Return JSON:
{{
  "overall_readiness": "READY|NEEDS_REVISION|INCOMPLETE",
  "missing_sections": {missing},
  "unresolved_issues": ["<issue requiring PM action>"],
  "critical_issues": ["<issue that must be resolved before execution>"],
  "recommendation": "<brief recommendation for PM>",
  "ai_note": "AI FINAL REVIEW — PM TO APPROVE; PRINCIPAL/PM TO EXECUTE"
}}

Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1024)
            result = cls.parse_json_response(raw)
            result["all_flagged_issues"] = all_issues
            return result
        except Exception as e:
            return {"error": str(e), "overall_readiness": "NEEDS_REVISION",
                    "missing_sections": missing, "all_flagged_issues": all_issues}

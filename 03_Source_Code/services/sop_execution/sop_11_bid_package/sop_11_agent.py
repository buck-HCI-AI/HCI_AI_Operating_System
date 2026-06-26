"""SOP 11 — Layer 3: AI Agent Script implementation."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "api"))

from base import BaseIntelligenceService
from .sop_11_templates import INPUT_LABELS


SYSTEM_PROMPT = """You are HCI's Preconstruction AI for Bid Package Assembly (SOP 11).

Your job is to review assembled bid package scope sections, identify gaps and document
control issues, assist the estimator in drafting scope language, and produce structured
output supporting PM and Buck approval before the package is issued to subcontractors.

RULES:
- Return only structured JSON
- Never issue the bid package to any subcontractor
- Never add or remove scope without explicit estimator instruction
- Mark all AI-drafted scope clearly as requiring human review
- If required inputs are missing, return an Inputs Missing report — do not proceed
- Flag HIGH severity gaps — these must be resolved before submission
"""


class SOP11Agent(BaseIntelligenceService):
    SERVICE_NAME = "sop_11_agent"
    STATUS = "active"

    @classmethod
    def review_scope_sections(cls, instance_id: int, scope_sections: list[dict],
                              project_brain_context: str = "") -> dict:
        """
        Layer 3 AI review: analyzes scope sections, identifies gaps and risks.
        Returns structured gap report and risk flags.
        """
        if not scope_sections:
            return {
                "status": "inputs_missing",
                "message": "No scope sections provided — cannot review.",
                "gap_report": [],
                "risk_flags": [],
            }

        sections_text = "\n\n".join(
            f"Trade: {s.get('trade_name')}\n"
            f"Scope: {s.get('scope_text', '')}\n"
            f"Drawings: {', '.join(s.get('drawing_refs', []))}\n"
            f"Specs: {', '.join(s.get('spec_refs', []))}\n"
            f"Exclusions: {', '.join(s.get('exclusions', []))}"
            for s in scope_sections
        )

        prompt = f"""Review these bid package scope sections for SOP 11 Bid Package Assembly.

PROJECT BRAIN CONTEXT:
{project_brain_context or 'No additional context available.'}

SCOPE SECTIONS SUBMITTED:
{sections_text}

Analyze each scope section and return a JSON object with:
{{
  "gap_report": [
    {{
      "trade": "<trade_name>",
      "flag_type": "SCOPE|DOCUMENT|AMBIGUITY|MISSING_EXCLUSION",
      "description": "<what is missing, inconsistent, or ambiguous>",
      "recommended_resolution": "<what to do>",
      "severity": "HIGH|MEDIUM|LOW"
    }}
  ],
  "risk_flags": [
    {{
      "risk_class": "Scope|Cost|Schedule|Contract|Coverage|Document Control",
      "description": "<risk description>",
      "severity": "HIGH|MEDIUM|LOW",
      "location": "<trade or section>"
    }}
  ],
  "document_control_issues": ["<issue 1>", "<issue 2>"],
  "overall_assessment": "<brief assessment of package completeness>",
  "ready_for_pm_review": true|false
}}

Return ONLY the JSON object. No explanation outside the JSON."""

        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=2048)
            result = cls.parse_json_response(raw)
            result["instance_id"] = instance_id
            result["reviewed_by"] = "AI"
            result["review_note"] = "AI REVIEW — REQUIRES ESTIMATOR AND PM CONFIRMATION"
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"AI review failed: {e}",
                "gap_report": [],
                "risk_flags": [],
            }

    @classmethod
    def draft_scope_section(cls, trade_name: str, trade_code: str,
                            project_context: str = "") -> dict:
        """AI drafts a scope section for a trade. Must be reviewed by estimator."""
        prompt = f"""Draft a scope section for trade: {trade_name} (CSI: {trade_code})

Project context: {project_context or 'No additional context.'}

Return JSON:
{{
  "trade_code": "{trade_code}",
  "trade_name": "{trade_name}",
  "scope_text": "<Plain English scope — specific, not vague>",
  "suggested_drawing_refs": ["<drawing ref format>"],
  "suggested_spec_refs": ["<spec section format>"],
  "suggested_exclusions": ["<common exclusion 1>", "<common exclusion 2>"],
  "ai_note": "AI DRAFT — REQUIRES ESTIMATOR REVIEW AND CONFIRMATION"
}}

Return ONLY the JSON object."""

        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1024)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "trade_name": trade_name}

    @classmethod
    def pull_sub_intelligence(cls, trade_name: str,
                              project_number: str | None = None) -> dict:
        """Queries vendor intelligence for available subs for a trade."""
        results = cls.search(
            f"subcontractor {trade_name} bid history performance",
            collection="vendor_memory",
            limit=10,
            project_filter=project_number,
        )
        return {
            "trade": trade_name,
            "vendor_intelligence_results": results,
            "note": "Review performance scores before finalizing sub invite list.",
        }

    @classmethod
    def check_inputs_missing(cls, missing_keys: list[str]) -> dict | None:
        """Returns an Inputs Missing report if any required inputs are missing."""
        if not missing_keys:
            return None
        items = [{"key": k, "label": INPUT_LABELS.get(k, k)} for k in missing_keys]
        return {
            "status": "inputs_missing",
            "message": "SOP 11 AI review cannot proceed — required inputs are missing.",
            "missing_inputs": items,
            "action_required": "PM to confirm each missing input before proceeding.",
        }

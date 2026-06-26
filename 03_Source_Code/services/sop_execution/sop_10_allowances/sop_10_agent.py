"""SOP 10 — Layer 3: Allowances / Alternates / Exclusions AI Agent."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "api"))

from base import BaseIntelligenceService


SYSTEM_PROMPT = """You are HCI's Preconstruction AI for Allowances, Alternates, and Exclusions (SOP 10).

Your job is to suggest appropriate allowances based on project type and historical data,
flag unusual or risky alternates, and ensure all explicit project exclusions are documented
before the bid package (SOP 11) is assembled.

RULES:
- Return only structured JSON
- Suggest allowances based on project type and HCI's historical data — never invent amounts
- Flag any alternate that changes the structural or regulatory basis of the project
- Ensure exclusions are explicit and do not create scope gaps
- Mark all AI suggestions as requiring PM confirmation before inclusion in SOP 11
- If total allowance pool exceeds $50,000, flag for Buck review
"""


class SOP10Agent(BaseIntelligenceService):
    SERVICE_NAME = "sop_10_agent"
    STATUS = "active"

    @classmethod
    def suggest_allowances(cls, project_type: str, scope_narrative: str,
                           estimated_budget: float = 0) -> dict:
        """AI suggests appropriate allowances based on project type and scope."""
        # Query historical cost data for context
        hist_results = cls.search(
            f"{project_type} allowances contingency historical",
            collection="hci_historical_costs",
            limit=5,
        )
        hist_context = "\n".join(
            r.get("payload", {}).get("text", "") for r in hist_results
        ) or "No historical allowance data available."

        budget_str = f"${estimated_budget:,.0f}" if estimated_budget else "not specified"
        prompt = f"""Suggest appropriate allowances for a {project_type} construction project.

SCOPE NARRATIVE: {scope_narrative}
ESTIMATED BUDGET: {budget_str}

HISTORICAL CONTEXT FROM HCI PROJECTS:
{hist_context}

Return JSON with suggested allowances:
{{
  "suggested_allowances": [
    {{
      "description": "<what this allowance covers>",
      "allowance_type": "owner_allowance|construction_allowance|contingency_allowance|design_allowance",
      "suggested_amount": <number>,
      "basis": "<why this amount — historical percentage or typical range>",
      "trade_code": "<CSI division or 'GEN' for general>",
      "risk_level": "LOW|MEDIUM|HIGH",
      "ai_suggested": true
    }}
  ],
  "total_suggested_pool": <sum of all amounts>,
  "requires_buck_review": <true if total > 50000>,
  "overall_note": "<brief note on allowance strategy for this project type>",
  "ai_note": "AI SUGGESTIONS — ALL AMOUNTS REQUIRE PM CONFIRMATION BEFORE USE"
}}

Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1500)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "suggested_allowances": [],
                    "ai_note": "AI suggestion failed — define allowances manually"}

    @classmethod
    def flag_unusual_alternates(cls, alternates: list[dict],
                                project_type: str) -> dict:
        """Flag any alternates that are unusual, risky, or require special review."""
        if not alternates:
            return {"flagged": [], "all_clear": True}

        alts_text = "\n".join(
            f"- {a.get('alternate_code','?')}: {a.get('description','?')} "
            f"({a.get('alternate_type','?')}) | Est. impact: ${a.get('estimated_cost_impact',0):+,.0f}"
            for a in alternates
        )
        prompt = f"""Review these alternates for a {project_type} construction project.

ALTERNATES:
{alts_text}

Flag any that are unusual, involve structural/regulatory changes, or require special review.

Return JSON:
{{
  "flagged_alternates": [
    {{
      "alternate_code": "<code>",
      "flag_type": "STRUCTURAL|REGULATORY|COST_RISK|SCOPE_CREEP|REQUIRES_DESIGN",
      "description": "<why this alternate needs attention>",
      "severity": "HIGH|MEDIUM|LOW",
      "recommended_action": "<what PM should do>"
    }}
  ],
  "all_clear": <true if no flags>,
  "ai_note": "AI REVIEW — PM TO CONFIRM BEFORE INCLUDING IN BID PACKAGE"
}}

Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1024)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "flagged_alternates": [], "all_clear": False}

    @classmethod
    def validate_exclusions(cls, exclusions: list[dict], scope_narrative: str) -> dict:
        """Check that exclusions don't create scope gaps or contradict the scope narrative."""
        if not exclusions:
            return {"gaps": [], "valid": True,
                    "ai_note": "No exclusions to validate"}

        excl_text = "\n".join(
            f"- {e.get('exclusion_code','?')}: {e.get('description','?')} (by {e.get('excluded_party','?')})"
            for e in exclusions
        )
        prompt = f"""Validate these project exclusions against the scope narrative.

SCOPE NARRATIVE: {scope_narrative}

EXCLUSIONS:
{excl_text}

Check for scope gaps — items excluded but not covered by anyone — or contradictions.

Return JSON:
{{
  "scope_gaps": [
    {{
      "description": "<item excluded but not assigned to any party>",
      "severity": "HIGH|MEDIUM|LOW",
      "recommended_resolution": "<who should cover this>"
    }}
  ],
  "contradictions": ["<item in exclusions that contradicts scope narrative>"],
  "valid": <true if no gaps or contradictions>,
  "ai_note": "AI VALIDATION — PM TO CONFIRM BEFORE LOCKING EXCLUSION LIST"
}}

Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1024)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "scope_gaps": [], "valid": False}

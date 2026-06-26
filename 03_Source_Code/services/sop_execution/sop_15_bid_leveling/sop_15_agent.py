"""SOP 15 — Layer 3: AI Agent Script for bid leveling."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "api"))

from base import BaseIntelligenceService


SYSTEM_PROMPT = """You are HCI's Bid Analysis AI for Bid Leveling (SOP 15).

Your job is to normalize received bids to a common scope basis, extract and classify
all qualifications and exclusions, flag risks, calculate all-in costs, check bidder
performance history, and produce a structured leveling recommendation for Buck's review.

RULES:
- Return only structured JSON
- Never make award decisions or communicate award to any sub
- Never contact any bidder for clarification
- Never include a late bid without PM authorization
- Never omit qualifications that change a bid's meaning
- Recommend based on adjusted cost AND risk, not price alone
- Mark all output as requiring human review: "AI RECOMMENDATION — BUCK MAKES THE AWARD DECISION"
"""


class SOP15Agent(BaseIntelligenceService):
    SERVICE_NAME = "sop_15_agent"
    STATUS = "active"

    @classmethod
    def analyze_bid(cls, bid_text: str, scope_summary: str,
                    bidder_name: str) -> dict:
        """
        Extract qualifications, exclusions, and risk flags from a single bid.
        Returns structured extraction.
        """
        prompt = f"""Analyze this subcontractor bid for SOP 15 Bid Leveling.

BIDDER: {bidder_name}
SCOPE SUMMARY: {scope_summary}

BID TEXT:
{bid_text}

Extract and return JSON:
{{
  "bidder_name": "{bidder_name}",
  "exclusions_list": ["<item excluded from bid>"],
  "scope_inclusions": ["<item explicitly included beyond base scope>"],
  "qualifications_raw_summary": "<brief summary of all qualifications>",
  "contract_qualifications": ["<contract term exception or qualification>"],
  "schedule_exceptions": ["<schedule qualification or exception>"],
  "alternates_included": [{{"alt_description": "", "amount": null}}],
  "alternates_excluded": [{{"alt_description": "", "reason": ""}}],
  "risk_flags": [
    {{
      "risk_class": "Scope|Cost|Schedule|Contract|Coverage|Document Control",
      "description": "<risk>",
      "severity": "HIGH|MEDIUM|LOW"
    }}
  ]
}}

Return ONLY the JSON object."""

        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1500)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"bidder_name": bidder_name, "error": str(e),
                    "risk_flags": [], "exclusions_list": []}

    @classmethod
    def generate_leveling_recommendation(cls, instance_id: int,
                                         comparison_table: list[dict],
                                         trade_name: str,
                                         scope_summary: str) -> dict:
        """
        Produces the AI recommendation after all bids are normalized.
        Buck makes the award decision — this is input to that decision only.
        """
        table_text = "\n".join(
            f"  {r['bidder']}: adjusted ${r['adjusted_total']:,.0f} "
            f"(+{r['pct_over_low']}% over low) | risk: {r['risk_level']} "
            f"| perf: {r['perf_score']}"
            for r in comparison_table
        )

        prompt = f"""You are producing a bid leveling recommendation for Buck Adams (owner).

TRADE: {trade_name}
SCOPE SUMMARY: {scope_summary}

NORMALIZED BID COMPARISON:
{table_text}

Produce a recommendation in JSON:
{{
  "primary_recommendation": {{
    "bidder": "<name>",
    "adjusted_amount": <number>,
    "rationale": "<why this bidder over others — cost, risk, and performance basis>",
    "conditions": "<what to confirm before awarding, if anything>",
    "risks_accepted": "<any known risk with this choice>"
  }},
  "alternative_recommendation": {{
    "bidder": "<name>",
    "adjusted_amount": <number>,
    "rationale": "<when to consider this alternative instead>"
  }},
  "flags_for_buck": ["<anything Buck should know before deciding>"],
  "ai_note": "AI RECOMMENDATION — BUCK MAKES THE AWARD DECISION"
}}

Return ONLY the JSON object."""

        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1024)
            result = cls.parse_json_response(raw)
            result["instance_id"] = instance_id
            return result
        except Exception as e:
            return {"error": str(e), "ai_note": "AI recommendation failed — review manually"}

    @classmethod
    def inputs_insufficient_report(cls, bid_count: int,
                                   min_required: int) -> dict:
        """Returns structured report when minimum bidder threshold is not met."""
        return {
            "status": "inputs_insufficient",
            "message": "SOP 15 leveling cannot proceed to award recommendation.",
            "responsive_bids": bid_count,
            "minimum_required": min_required,
            "operating_rule": "MIN_BIDDERS",
            "action_required": (
                "PM to conduct SOP 14 follow-up to get additional bids, "
                "OR Buck to authorize exception (exception record required)."
            ),
        }

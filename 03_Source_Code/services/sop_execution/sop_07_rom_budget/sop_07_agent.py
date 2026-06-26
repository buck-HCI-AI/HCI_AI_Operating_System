"""SOP 07 — Layer 3: ROM Budget AI Agent."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "api"))

from base import BaseIntelligenceService


SYSTEM_PROMPT = """You are HCI's Preconstruction AI for ROM Budget Generation (SOP 07).

Your job is to generate a Rough Order of Magnitude (ROM) budget by trade, using historical
cost data, industry benchmarks, and the confirmed construction narrative.

RULES:
- Return only structured JSON
- All dollar amounts are ESTIMATES based on historical data — not commitments
- Always provide a basis for each estimate (historical $/SF, unit pricing, etc.)
- Flag any line item with LOW confidence — these need PM review before use
- Include contingency per project type
- Mark all AI-generated estimates as requiring PM confirmation
- Never produce a budget that is used to commit to a client without PM + Buck approval
"""


class SOP07Agent(BaseIntelligenceService):
    SERVICE_NAME = "sop_07_agent"
    STATUS = "active"

    @classmethod
    def generate_rom_estimate(cls, project_type: str, gross_sf: float,
                               narrative_sections: list[dict],
                               owner_budget_target: float = 0) -> dict:
        """AI generates a full ROM budget by trade from narrative sections."""
        # Query historical cost data
        hist_results = cls.search(
            f"{project_type} cost per square foot historical budget",
            collection="hci_historical_costs",
            limit=8,
        )
        hist_context = "\n".join(
            r.get("payload", {}).get("text", "") for r in hist_results
        ) or "No historical cost data available — using industry benchmarks."

        trades_text = "\n".join(
            f"- {s.get('trade_name','?')} ({s.get('trade_code','?')}): "
            f"{len(s.get('inclusions',[]))} inclusions, {len(s.get('exclusions',[]))} exclusions"
            for s in narrative_sections
        ) or "No narrative sections provided."

        budget_context = (
            f"OWNER BUDGET TARGET: ${owner_budget_target:,.0f}"
            if owner_budget_target else "No owner budget target provided."
        )
        prompt = f"""Generate a ROM budget estimate for a {project_type} construction project.

GROSS SF: {gross_sf:,.0f} SF
{budget_context}

NARRATIVE SECTIONS (trades in scope):
{trades_text}

HISTORICAL COST DATA:
{hist_context}

Return JSON with line items for each trade:
{{
  "line_items": [
    {{
      "trade_code": "<CSI code>",
      "trade_name": "<trade name>",
      "description": "<brief scope description>",
      "unit": "SF|LS|EA|LF",
      "quantity": <number>,
      "unit_cost": <number>,
      "basis": "<historical_sf|unit_price|ai_estimate|allowance>",
      "confidence": "HIGH|MEDIUM|LOW",
      "ai_generated": true
    }}
  ],
  "suggested_contingency_pct": <number between 0.08 and 0.20>,
  "cost_per_sf_note": "<comment on $/SF vs market>",
  "low_confidence_trades": ["<trade needing PM cost review>"],
  "ai_note": "AI ROM ESTIMATE — ALL AMOUNTS REQUIRE PM REVIEW AND BUCK APPROVAL BEFORE CLIENT USE"
}}

Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=2500)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "line_items": [],
                    "ai_note": "AI estimate failed — build ROM manually"}

    @classmethod
    def flag_high_risk_line_items(cls, line_items: list[dict],
                                   gross_sf: float) -> dict:
        """Flag line items with LOW confidence or unusual unit costs."""
        if not gross_sf or not line_items:
            return {"flagged": [], "all_clear": True}

        total_estimate = sum(
            i.get("quantity", 1) * i.get("unit_cost", 0)
            for i in line_items
        )
        cost_per_sf = total_estimate / gross_sf if gross_sf else 0

        items_text = "\n".join(
            f"- {i.get('trade_name','?')} ({i.get('trade_code','?')}): "
            f"${i.get('quantity',1) * i.get('unit_cost',0):,.0f} "
            f"(confidence: {i.get('confidence','?')}, basis: {i.get('basis','?')})"
            for i in line_items
        )
        prompt = f"""Review these ROM budget line items for risks and outliers.

TOTAL ESTIMATE: ${total_estimate:,.0f} (${cost_per_sf:,.2f}/SF)
PROJECT GROSS SF: {gross_sf:,.0f} SF

LINE ITEMS:
{items_text}

Flag any items that are unusually high/low, have LOW confidence, or need PM attention.

Return JSON:
{{
  "flagged": [
    {{
      "trade_code": "<code>",
      "trade_name": "<name>",
      "flag_reason": "<why this needs PM attention>",
      "severity": "HIGH|MEDIUM|LOW",
      "recommended_action": "<what PM should do>"
    }}
  ],
  "all_clear": <true if no HIGH flags>,
  "total_cost_assessment": "HIGH|WITHIN_RANGE|LOW",
  "ai_note": "AI LINE ITEM RISK REVIEW — PM TO CONFIRM"
}}

Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1024)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "flagged": [], "all_clear": False}

    @classmethod
    def compare_to_owner_target(cls, total_estimate: float,
                                 owner_budget_target: float,
                                 project_type: str) -> dict | None:
        """Return variance analysis if owner has a target budget."""
        if not owner_budget_target:
            return None
        variance = total_estimate - owner_budget_target
        variance_pct = variance / owner_budget_target * 100 if owner_budget_target else 0
        return {
            "owner_budget_target": owner_budget_target,
            "rom_total": total_estimate,
            "variance": variance,
            "variance_pct": round(variance_pct, 1),
            "status": (
                "OVER_BUDGET" if variance > 0
                else "UNDER_BUDGET" if variance < -owner_budget_target * 0.05
                else "WITHIN_TARGET"
            ),
            "action_required": (
                "Budget discussion with owner required before proceeding to bid."
                if abs(variance_pct) > 15 else None
            ),
        }

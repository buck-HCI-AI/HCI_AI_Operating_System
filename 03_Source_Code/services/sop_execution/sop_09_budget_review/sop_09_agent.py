"""SOP 09 — Layer 3: Budget Review AI Agent."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "api"))

from base import BaseIntelligenceService


SYSTEM_PROMPT = """You are HCI's Preconstruction AI for Budget Review (SOP 09).

Your job is to compare the ROM budget against the revised/detailed budget and flag
material variances before the project is approved to proceed to bid.

RULES:
- Return only structured JSON
- Flag any trade line item with variance > 10% above or below ROM
- Flag total budget variance > 10% from ROM
- If total budget > $500,000, Buck approval is required before proceeding
- All reviews are recommendations only — PM and Buck make the approval decision
"""


class SOP09Agent(BaseIntelligenceService):
    SERVICE_NAME = "sop_09_agent"
    STATUS = "active"

    @classmethod
    def analyze_budget_variance(cls, rom_line_items: list[dict],
                                 revised_line_items: list[dict],
                                 project_type: str) -> dict:
        """Compare ROM to revised budget and flag material variances by trade."""
        # Build comparison table
        rom_by_trade = {i.get("trade_code", ""): i for i in rom_line_items}
        rev_by_trade = {i.get("trade_code", ""): i for i in revised_line_items}
        all_trades = set(list(rom_by_trade.keys()) + list(rev_by_trade.keys()))

        comparison = []
        for trade in all_trades:
            rom = rom_by_trade.get(trade, {})
            rev = rev_by_trade.get(trade, {})
            rom_total = rom.get("total", rom.get("quantity", 1) * rom.get("unit_cost", 0))
            rev_total = rev.get("total", rev.get("quantity", 1) * rev.get("unit_cost", 0))
            if not rev_total:
                rev_total = rom_total
            variance = rev_total - rom_total
            variance_pct = (variance / rom_total * 100) if rom_total else 0
            comparison.append({
                "trade_code": trade,
                "trade_name": rom.get("trade_name") or rev.get("trade_name", "Unknown"),
                "rom_amount": rom_total,
                "revised_amount": rev_total,
                "variance": variance,
                "variance_pct": round(variance_pct, 1),
            })

        flagged = [c for c in comparison if abs(c["variance_pct"]) > 10]
        lines_text = "\n".join(
            f"- {c['trade_name']} ({c['trade_code']}): ROM ${c['rom_amount']:,.0f} "
            f"→ Revised ${c['revised_amount']:,.0f} ({c['variance_pct']:+.1f}%)"
            for c in comparison
        )
        prompt = f"""Review this budget comparison for a {project_type} construction project.

BUDGET COMPARISON (ROM vs Revised):
{lines_text}

Flag variances > 10% and trades that need explanation before Buck review.

Return JSON:
{{
  "flagged_variances": [
    {{
      "trade_code": "<code>",
      "trade_name": "<name>",
      "variance_pct": <number>,
      "likely_cause": "<why this line changed>",
      "severity": "HIGH|MEDIUM|LOW",
      "recommended_action": "<what PM should do>"
    }}
  ],
  "overall_verdict": "APPROVED|REVIEW_REQUIRED|ESCALATE_TO_BUCK",
  "budget_narrative": "<2-3 sentence summary of budget status>",
  "ai_note": "AI VARIANCE ANALYSIS — PM AND BUCK TO DECIDE ON APPROVAL"
}}

Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1500)
            result = cls.parse_json_response(raw)
            result["comparison_table"] = comparison
            result["flagged_count"] = len(flagged)
            return result
        except Exception as e:
            return {"error": str(e), "comparison_table": comparison,
                    "flagged_count": len(flagged)}

    @classmethod
    def review_vs_owner_target(cls, revised_total: float,
                                owner_budget_target: float,
                                project_type: str) -> dict | None:
        """Flag if revised budget materially exceeds owner's stated budget."""
        if not owner_budget_target:
            return None
        variance = revised_total - owner_budget_target
        variance_pct = variance / owner_budget_target * 100
        severity = "HIGH" if abs(variance_pct) > 15 else "MEDIUM" if abs(variance_pct) > 5 else "LOW"
        return {
            "owner_budget_target": owner_budget_target,
            "revised_total": revised_total,
            "variance": variance,
            "variance_pct": round(variance_pct, 1),
            "severity": severity,
            "action_required": (
                "Immediate budget discussion with owner required before proceeding to bid."
                if severity == "HIGH"
                else "Review with owner at next meeting."
            ),
        }

    @classmethod
    def generate_buck_review_summary(cls, budget_data: dict,
                                      project_type: str,
                                      project_name: str = "") -> dict:
        """Generate a concise executive summary for Buck's budget approval."""
        total = budget_data.get("revised_total", 0)
        rom = budget_data.get("rom_total", 0)
        variance_pct = budget_data.get("variance_pct", 0)
        flagged = budget_data.get("flagged_count", 0)

        prompt = f"""Write a concise executive budget summary for Buck Adams to approve.

PROJECT: {project_name or project_type}
PROJECT TYPE: {project_type}
ROM TOTAL: ${rom:,.0f}
REVISED BUDGET: ${total:,.0f}
VARIANCE FROM ROM: {variance_pct:+.1f}%
FLAGGED LINE ITEMS: {flagged}

Return JSON:
{{
  "summary_title": "Budget Review — {project_name or project_type}",
  "executive_summary": "<3-4 sentence executive summary for Buck>",
  "key_risks": ["<risk 1>", "<risk 2>"],
  "recommendation": "APPROVE|APPROVE_WITH_CONDITIONS|HOLD|REJECT",
  "conditions": "<any conditions if not clean approval>",
  "ai_note": "AI SUMMARY FOR BUCK REVIEW — BUCK DECISION IS FINAL"
}}

Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=768)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e),
                    "recommendation": "REVIEW_REQUIRED",
                    "ai_note": "AI summary failed — PM to prepare manual summary for Buck"}

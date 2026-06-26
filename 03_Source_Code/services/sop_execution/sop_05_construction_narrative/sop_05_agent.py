"""SOP 05 — Layer 3: Construction Narrative AI Agent."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "api"))

from base import BaseIntelligenceService


SYSTEM_PROMPT = """You are HCI's Preconstruction AI for Construction Narrative writing (SOP 05).

Your job is to draft clear, professional construction narratives per trade — used to
communicate scope to subs, owners, and the project team before bidding begins.

RULES:
- Return only structured JSON
- Narratives describe WHAT is included, what is excluded, and any allowances
- Use plain language suitable for subcontractor review
- Never define a scope that contradicts the plan review findings (SOP 04)
- Mark all AI-drafted narratives as requiring PM review and confirmation
- Do not invent scope not present in the plan review or PM notes
"""


class SOP05Agent(BaseIntelligenceService):
    SERVICE_NAME = "sop_05_agent"
    STATUS = "active"

    @classmethod
    def draft_narrative_section(cls, trade_code: str, trade_name: str,
                                 scope_notes: str, project_type: str,
                                 plan_review_findings: list[str] | None = None,
                                 pm_additions: str = "") -> dict:
        """Draft a narrative section for a single trade."""
        findings_text = (
            "\n".join(f"- {f}" for f in plan_review_findings)
            if plan_review_findings else "No specific findings from plan review."
        )
        prompt = f"""Draft a construction narrative section for a {project_type} project.

TRADE: {trade_name} (CSI: {trade_code})
PM SCOPE NOTES: {scope_notes or "Draft based on typical scope for this trade and project type."}
PLAN REVIEW FINDINGS TO INCORPORATE:
{findings_text}
ADDITIONAL PM ADDITIONS: {pm_additions or "None"}

Draft a narrative section with:
- Clear inclusions (what the sub is responsible for)
- Clear exclusions (what is NOT the sub's responsibility)
- Any allowances that apply to this trade
- Professional construction industry language

Return JSON:
{{
  "trade_code": "{trade_code}",
  "trade_name": "{trade_name}",
  "narrative_text": "<2-4 paragraph scope narrative>",
  "inclusions": ["<specific included item 1>", "<item 2>"],
  "exclusions": ["<specifically excluded item 1>"],
  "allowances_noted": ["<allowance item if applicable>"],
  "ai_note": "AI DRAFT — PM TO REVIEW AND CONFIRM BEFORE USE IN BID PACKAGE"
}}

Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1500)
            result = cls.parse_json_response(raw)
            result["ai_drafted"] = True
            return result
        except Exception as e:
            return {"error": str(e), "trade_code": trade_code,
                    "ai_drafted": True,
                    "ai_note": "AI draft failed — write narrative manually"}

    @classmethod
    def review_narrative_completeness(cls, sections: list[dict],
                                       project_type: str) -> dict:
        """Check that all narratives are internally consistent and complete."""
        section_summary = "\n".join(
            f"- {s.get('trade_name','?')} ({s.get('trade_code','?')}): "
            f"{len(s.get('inclusions',[]))} inclusions, {len(s.get('exclusions',[]))} exclusions"
            for s in sections
        ) or "No sections provided."

        prompt = f"""Review this set of construction narrative sections for a {project_type} project.

NARRATIVE SECTIONS:
{section_summary}

Check for:
1. Scope gaps — items that fall between sections and belong to no trade
2. Overlapping scope — items claimed by multiple trades
3. Missing standard sections for this project type

Return JSON:
{{
  "scope_gaps": ["<item not covered by any section>"],
  "overlaps": ["<item claimed by multiple trades — needs resolution>"],
  "missing_trades": ["<trade typically needed for {project_type} but not in sections>"],
  "completeness_score": "HIGH|MEDIUM|LOW",
  "ready_for_bid_package": <true if no gaps or overlaps>,
  "ai_note": "AI COMPLETENESS REVIEW — PM TO CONFIRM"
}}

Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1024)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "completeness_score": "LOW",
                    "ready_for_bid_package": False}

"""SOP 04 — Layer 3: Plan Review AI Agent."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "api"))

from base import BaseIntelligenceService


SYSTEM_PROMPT = """You are HCI's Preconstruction AI for Plan Review (SOP 04).

Your job is to analyze construction plan sections for scope gaps, document conflicts,
and constructibility issues — before the construction narrative (SOP 05) is written.

RULES:
- Return only structured JSON
- Flag any gap between what the drawings show and what a contractor needs to price
- Flag conflicts between disciplines (architectural vs structural, structural vs MEP, etc.)
- Flag constructibility issues that will cause field problems or change orders
- Do NOT invent scope — only flag what is verifiably missing or conflicting
- All findings require PM review before being added to the SOP 04 record
"""


class SOP04Agent(BaseIntelligenceService):
    SERVICE_NAME = "sop_04_agent"
    STATUS = "active"

    @classmethod
    def analyze_plan_section(cls, trade_code: str, trade_name: str,
                              scope_notes: str, project_type: str,
                              page_refs: list[str] | None = None) -> dict:
        """AI reviews a single plan section for gaps, conflicts, and constructibility issues."""
        pages_str = ", ".join(page_refs) if page_refs else "not specified"
        prompt = f"""Review this construction plan section for gaps, conflicts, and constructibility issues.

PROJECT TYPE: {project_type}
TRADE: {trade_name} (CSI: {trade_code})
PLAN PAGES REFERENCED: {pages_str}
PM SCOPE NOTES: {scope_notes or "No notes provided — review what is typically needed for this trade."}

Identify:
1. GAPS: Information missing from plans needed to price this trade
2. CONFLICTS: Contradictions between drawings or disciplines
3. CONSTRUCTIBILITY: Issues that will cause field problems or change orders

Return JSON:
{{
  "trade_code": "{trade_code}",
  "trade_name": "{trade_name}",
  "gaps_found": ["<gap 1>", "<gap 2>"],
  "conflicts_found": ["<conflict 1>"],
  "constructibility_issues": ["<issue 1>"],
  "severity": "HIGH|MEDIUM|LOW",
  "rfi_candidates": ["<question for architect/engineer>"],
  "ai_note": "AI REVIEW — PM TO CONFIRM BEFORE LOGGING"
}}

Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1024)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "trade_code": trade_code,
                    "ai_note": "AI review failed — log gaps manually"}

    @classmethod
    def flag_constructibility_risks(cls, sections: list[dict],
                                     project_type: str) -> dict:
        """Cross-section analysis: find risks that span multiple trades."""
        if not sections:
            return {"cross_trade_risks": [], "overall_severity": "LOW"}

        summary_lines = []
        for s in sections:
            issues = s.get("constructibility_issues", [])
            conflicts = s.get("conflicts_found", [])
            if issues or conflicts:
                summary_lines.append(
                    f"- {s.get('trade_name','?')} ({s.get('trade_code','?')}): "
                    f"{len(issues)} constructibility, {len(conflicts)} conflicts"
                )
        summary = "\n".join(summary_lines) or "No issues flagged in individual sections."

        prompt = f"""Review this plan review summary for a {project_type} project and identify cross-trade risks.

PER-SECTION SUMMARY:
{summary}

Identify risks that span multiple trades or that, in combination, create HIGH risk.

Return JSON:
{{
  "cross_trade_risks": [
    {{
      "description": "<risk spanning multiple trades>",
      "trades_affected": ["<trade 1>", "<trade 2>"],
      "severity": "HIGH|MEDIUM|LOW",
      "recommended_action": "<what PM should do>"
    }}
  ],
  "overall_severity": "HIGH|MEDIUM|LOW",
  "proceed_to_narrative": <true if no HIGH-severity blockers>,
  "ai_note": "AI CROSS-SECTION ANALYSIS — PM TO REVIEW"
}}

Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1024)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "cross_trade_risks": [],
                    "proceed_to_narrative": False}

    @classmethod
    def generate_rfi_list(cls, sections: list[dict], project_name: str = "") -> dict:
        """Compile all RFI candidates from reviewed sections into a prioritized list."""
        all_rfis = []
        for s in sections:
            for rfi in s.get("rfi_candidates", []):
                all_rfis.append({
                    "trade": s.get("trade_name", "General"),
                    "question": rfi,
                })
            for gap in s.get("gaps_found", []):
                all_rfis.append({
                    "trade": s.get("trade_name", "General"),
                    "question": f"Clarify: {gap}",
                })

        if not all_rfis:
            return {"rfi_list": [], "total_count": 0,
                    "ai_note": "No RFIs identified"}

        rfis_text = "\n".join(f"- [{r['trade']}] {r['question']}" for r in all_rfis)
        prompt = f"""Organize and prioritize these RFI candidates for a construction project{f' ({project_name})' if project_name else ''}.

RAW RFI CANDIDATES:
{rfis_text}

Consolidate duplicates, assign priorities, and format as a clean RFI list.

Return JSON:
{{
  "rfi_list": [
    {{
      "rfi_number": "RFI-001",
      "trade": "<trade>",
      "question": "<clear, concise RFI question>",
      "priority": "CRITICAL|HIGH|MEDIUM|LOW",
      "addressed_to": "Architect|Structural Engineer|MEP Engineer|Owner"
    }}
  ],
  "total_count": <number>,
  "critical_count": <number>,
  "ai_note": "AI RFI LIST — PM TO REVIEW AND SUBMIT"
}}

Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1500)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "rfi_list": all_rfis,
                    "total_count": len(all_rfis)}

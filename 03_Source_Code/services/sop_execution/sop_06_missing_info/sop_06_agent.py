"""SOP 06 — Layer 3: Missing Information / Risk Log AI Agent."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "api"))

from base import BaseIntelligenceService


SYSTEM_PROMPT = """You are HCI's Preconstruction AI for Missing Information and Risk Logging (SOP 06).

Your job is to identify information gaps and project risks from plan review findings and
the construction narrative — before the ROM budget (SOP 07) is built.

RULES:
- Return only structured JSON
- Prioritize gaps that will block pricing or create bid ambiguity
- Flag risks with probability AND impact — both required
- Never recommend holding a project based on risk alone; flag and let PM decide
- Mark all findings as requiring PM confirmation
"""


class SOP06Agent(BaseIntelligenceService):
    SERVICE_NAME = "sop_06_agent"
    STATUS = "active"

    @classmethod
    def identify_gaps_from_review(cls, plan_review_gaps: list[str],
                                   narrative_sections: list[dict],
                                   project_type: str) -> dict:
        """AI compiles missing info items from plan review gaps and narrative findings."""
        gaps_text = "\n".join(f"- {g}" for g in plan_review_gaps) or "No gaps from plan review."
        narratives_with_issues = [
            s for s in narrative_sections
            if s.get("gaps_found") or s.get("conflicts_found") or s.get("allowances_noted")
        ]
        narrative_text = "\n".join(
            f"- {s.get('trade_name','?')}: {', '.join(s.get('gaps_found',[]) + s.get('conflicts_found',[]))}"
            for s in narratives_with_issues
        ) or "No outstanding items from narratives."

        prompt = f"""Identify missing information items that must be resolved before ROM budgeting.

PROJECT TYPE: {project_type}

GAPS FROM PLAN REVIEW (SOP 04):
{gaps_text}

OUTSTANDING ITEMS FROM NARRATIVES (SOP 05):
{narrative_text}

Return JSON with prioritized missing info items:
{{
  "missing_items": [
    {{
      "item_code": "MI-001",
      "description": "<what is missing and why it matters>",
      "source": "<plan review|narrative|SOP 04|SOP 05>",
      "responsible_party": "<who must provide this: Architect|Owner|Engineer|PM>",
      "priority": "CRITICAL|HIGH|MEDIUM|LOW",
      "impact_if_missing": "<what happens if unresolved at bid time>"
    }}
  ],
  "critical_count": <number CRITICAL items>,
  "proceed_to_rom": <true if no CRITICAL items that block pricing>,
  "ai_note": "AI GAP IDENTIFICATION — PM TO CONFIRM BEFORE LOGGING"
}}

Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1500)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "missing_items": [],
                    "proceed_to_rom": False,
                    "ai_note": "AI gap identification failed — log gaps manually"}

    @classmethod
    def flag_project_risks(cls, project_type: str, scope_summary: str,
                            missing_item_count: int, plan_gaps: list[str]) -> dict:
        """AI flags project-level risks based on project type, scope, and known gaps."""
        # Query HCI lessons learned for similar projects
        lessons = cls.search(
            f"{project_type} risk lessons learned change order",
            collection="lessons_learned",
            limit=5,
        )
        lessons_context = "\n".join(
            r.get("payload", {}).get("text", "") for r in lessons
        ) or "No relevant lessons learned available."

        gaps_text = "\n".join(f"- {g}" for g in plan_gaps[:10]) or "None."
        prompt = f"""Flag project risks for a {project_type} construction project.

SCOPE SUMMARY: {scope_summary}
OPEN INFORMATION GAPS: {missing_item_count} items outstanding
SAMPLE GAPS:
{gaps_text}

LESSONS LEARNED FROM SIMILAR PROJECTS:
{lessons_context}

Return JSON:
{{
  "risks": [
    {{
      "risk_code": "R-001",
      "description": "<risk description>",
      "probability": "HIGH|MEDIUM|LOW",
      "impact": "HIGH|MEDIUM|LOW",
      "mitigation": "<recommended mitigation>",
      "owner": "<PM|Buck|Architect|Owner>",
      "ai_flagged": true
    }}
  ],
  "overall_risk_level": "HIGH|MEDIUM|LOW",
  "ai_note": "AI RISK ASSESSMENT — PM TO REVIEW AND CONFIRM"
}}

Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1500)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "risks": [],
                    "overall_risk_level": "MEDIUM"}

    @classmethod
    def prioritize_rfi_list(cls, missing_items: list[dict],
                             bid_due_date: str = "") -> dict:
        """Sort and prioritize outstanding items as RFIs with due dates."""
        if not missing_items:
            return {"rfi_priority_list": [], "critical_path_rfis": []}

        items_text = "\n".join(
            f"- [{i.get('priority','?')}] {i.get('description','?')} (responsible: {i.get('responsible_party','?')})"
            for i in missing_items if not i.get("resolved")
        )
        date_context = f"BID DUE DATE: {bid_due_date}" if bid_due_date else ""

        prompt = f"""Prioritize these outstanding information requests before bid.

{date_context}

OPEN ITEMS:
{items_text}

Identify which items are on the critical path for bidding (must be resolved before subs can price).

Return JSON:
{{
  "rfi_priority_list": [
    {{
      "item": "<description>",
      "priority": "CRITICAL|HIGH|MEDIUM|LOW",
      "recommended_due_date": "<ISO date or 'before bid close'>",
      "send_to": "<Architect|Engineer|Owner>"
    }}
  ],
  "critical_path_rfis": ["<item that MUST be resolved before bid package>"],
  "ai_note": "AI PRIORITIZATION — PM TO CONFIRM DUE DATES"
}}

Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1024)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "rfi_priority_list": [],
                    "critical_path_rfis": []}

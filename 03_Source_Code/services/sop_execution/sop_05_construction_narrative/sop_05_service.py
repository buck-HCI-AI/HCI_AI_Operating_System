"""SOP 05 — Construction Narrative: execution service (Layers 1+2)."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import services.db as db
from shared.base_sop import BaseSOP
from shared.sop_data_model import SOPStatus
from shared.stop_condition import StopConditionChecker
from shared.approval_engine import ApprovalEngine
from .sop_05_templates import REQUIRED_INPUT_KEYS, INPUT_LABELS, NarrativeSection
from .sop_05_agent import SOP05Agent


class SOP05ConstructionNarrativeService(BaseSOP):
    SOP_NUMBER = "05"

    @classmethod
    def start_narrative(cls, project_id: int, sop_04_instance_id: int,
                         owner_name: str, project_type: str,
                         plan_issue_date: str) -> dict:
        """Create SOP 05 instance. Triggered from SOP 04 handoff."""
        instance = cls.create_instance(
            project_id=project_id,
            owner_name=owner_name,
            owner_role="pm",
            parent_instance_id=sop_04_instance_id,
        )
        cls.confirm_input(instance["id"], "sop_04_instance_id", str(sop_04_instance_id))
        cls.confirm_input(instance["id"], "project_type", project_type)
        cls.confirm_input(instance["id"], "plan_issue_date", plan_issue_date)
        cls.transition_status(instance["id"], SOPStatus.IN_PROGRESS, owner_name,
                              "Narrative drafting started")
        return {"instance": instance, "status": SOPStatus.IN_PROGRESS.value,
                "parent_sop_04": sop_04_instance_id,
                "next_step": "Draft narrative sections via draft_section() or run_ai_draft()."}

    @classmethod
    def draft_section(cls, instance_id: int, section_data: dict,
                      actor: str = "pm") -> dict:
        """PM manually adds or edits a narrative section."""
        section = NarrativeSection(
            trade_code=section_data.get("trade_code", ""),
            trade_name=section_data.get("trade_name", ""),
            narrative_text=section_data.get("narrative_text", ""),
            inclusions=section_data.get("inclusions", []),
            exclusions=section_data.get("exclusions", []),
            allowances_noted=section_data.get("allowances_noted", []),
            ai_drafted=section_data.get("ai_drafted", False),
            pm_notes=section_data.get("pm_notes", ""),
        )
        errors = section.validate()
        if errors:
            return {"status": "validation_error", "errors": errors}

        output_id = cls.save_output(
            instance_id, "narrative_section",
            f"Narrative — {section.trade_name}", content=section.to_dict()
        )
        cls._log_event(instance_id, "section_drafted", section.trade_name, actor)
        return {"output_id": output_id, "trade_name": section.trade_name}

    @classmethod
    def run_ai_draft(cls, instance_id: int, trade_code: str,
                     trade_name: str, scope_notes: str = "",
                     pm_additions: str = "") -> dict:
        """Layer 3: AI drafts a narrative section for a single trade."""
        # Get project type and plan review gaps
        inp_rows = db.query("""
            SELECT input_key, confirmed_by FROM sop_inputs
            WHERE sop_instance_id = %s AND input_key IN ('project_type', 'sop_04_instance_id')
        """, (instance_id,))
        inputs = {r["input_key"]: r["confirmed_by"] for r in inp_rows}
        project_type = inputs.get("project_type", "commercial")
        sop04_id = inputs.get("sop_04_instance_id")

        # Pull gaps from SOP 04 for this trade
        plan_review_gaps = []
        if sop04_id:
            rows = db.query("""
                SELECT content FROM sop_outputs
                WHERE sop_instance_id = %s AND output_type = 'plan_section'
                AND content->>'trade_code' = %s
            """, (int(sop04_id), trade_code))
            for row in rows:
                c = json.loads(row["content"]) if isinstance(row["content"], str) else row["content"]
                plan_review_gaps.extend(c.get("gaps_found", []))
                plan_review_gaps.extend(c.get("constructibility_issues", []))

        result = SOP05Agent.draft_narrative_section(
            trade_code=trade_code,
            trade_name=trade_name,
            scope_notes=scope_notes,
            project_type=project_type,
            plan_review_findings=plan_review_gaps,
            pm_additions=pm_additions,
        )

        section = NarrativeSection(
            trade_code=trade_code,
            trade_name=trade_name,
            narrative_text=result.get("narrative_text", ""),
            inclusions=result.get("inclusions", []),
            exclusions=result.get("exclusions", []),
            allowances_noted=result.get("allowances_noted", []),
            ai_drafted=True,
        )
        output_id = cls.save_output(
            instance_id, "narrative_section",
            f"Narrative — {trade_name}", content=section.to_dict()
        )
        result["output_id"] = output_id

        cur = cls.get_instance(instance_id)
        if cur and cur["status"] == SOPStatus.IN_PROGRESS.value:
            cls.transition_status(instance_id, SOPStatus.AI_DRAFTED, "AI",
                                  f"AI narrative drafted: {trade_name}")
        return result

    @classmethod
    def confirm_section(cls, instance_id: int, trade_code: str,
                        pm_name: str, pm_notes: str = "") -> dict:
        """PM confirms a drafted narrative section."""
        rows = db.query("""
            SELECT id, content FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'narrative_section'
            AND content->>'trade_code' = %s ORDER BY id DESC LIMIT 1
        """, (instance_id, trade_code))
        if not rows:
            return {"error": f"No narrative section found for trade {trade_code}"}

        row = rows[0]
        content = json.loads(row["content"]) if isinstance(row["content"], str) else row["content"]
        content["pm_confirmed"] = True
        content["pm_notes"] = pm_notes
        db.execute("UPDATE sop_outputs SET content = %s WHERE id = %s",
                   (json.dumps(content), row["id"]))
        cls._log_event(instance_id, "section_confirmed", trade_code, pm_name)
        return {"trade_code": trade_code, "confirmed": True}

    @classmethod
    def run_completeness_check(cls, instance_id: int) -> dict:
        """AI checks all sections for scope gaps and overlaps."""
        rows = db.query("""
            SELECT content FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'narrative_section'
        """, (instance_id,))
        sections = [
            json.loads(r["content"]) if isinstance(r["content"], str) else r["content"]
            for r in rows
        ]

        inp_rows = db.query("""
            SELECT confirmed_by FROM sop_inputs
            WHERE sop_instance_id = %s AND input_key = 'project_type'
        """, (instance_id,))
        project_type = inp_rows[0]["confirmed_by"] if inp_rows else "commercial"

        result = SOP05Agent.review_narrative_completeness(sections, project_type)
        cls.save_output(instance_id, "completeness_check",
                        "AI Narrative Completeness Check", content=result)
        return result

    @classmethod
    def pm_approve(cls, instance_id: int, pm_name: str) -> dict:
        """PM approves all narrative sections. Transitions to Approved."""
        cls.transition_status(instance_id, SOPStatus.INTERNAL_REVIEW, pm_name,
                              "PM reviewing all narrative sections")
        cls.transition_status(instance_id, SOPStatus.APPROVED, pm_name,
                              "Construction narrative approved by PM")
        return {"status": SOPStatus.APPROVED.value, "approved_by": pm_name}

    @classmethod
    def hand_off_to_sop06(cls, instance_id: int, actor: str,
                           project_id: int, owner_name: str) -> dict:
        """Trigger SOP 06 (Missing Info / Risk Log). Transitions to Handed Off."""
        StopConditionChecker.check_sc07_handoff_destination(instance_id, owner_name)
        cls.transition_status(instance_id, SOPStatus.HANDED_OFF, actor,
                              f"Handed off to SOP 06 — {owner_name}")

        from sop_06_missing_info.sop_06_service import SOP06MissingInfoService
        sop06 = SOP06MissingInfoService.start_risk_log(
            project_id=project_id,
            sop_05_instance_id=instance_id,
            owner_name=owner_name,
        )
        return {"sop_05_status": SOPStatus.HANDED_OFF.value, "sop_06_instance": sop06}

    @classmethod
    def get_full_status(cls, instance_id: int) -> dict:
        instance = cls.get_instance(instance_id)
        if not instance:
            return {"error": "Instance not found"}
        missing = cls.get_missing_inputs(instance_id, REQUIRED_INPUT_KEYS)
        rows = db.query("""
            SELECT content->>'trade_name' AS trade_name,
                   (content->>'pm_confirmed')::boolean AS confirmed
            FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'narrative_section'
        """, (instance_id,))
        sections = [dict(r) for r in rows]
        return {
            "instance": instance,
            "missing_inputs": [INPUT_LABELS.get(k, k) for k in missing],
            "sections": sections,
            "confirmed_count": sum(1 for s in sections if s.get("confirmed")),
            "audit_trail": cls.get_audit_trail(instance_id),
        }

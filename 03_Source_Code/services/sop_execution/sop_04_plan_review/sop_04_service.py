"""SOP 04 — Plan Review: execution service (Layers 1+2)."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import services.db as db
from shared.base_sop import BaseSOP
from shared.sop_data_model import SOPStatus
from shared.stop_condition import StopConditionChecker, WorkflowBlockedError
from shared.approval_engine import ApprovalEngine
from .sop_04_templates import REQUIRED_INPUT_KEYS, INPUT_LABELS, PlanSection
from .sop_04_agent import SOP04Agent


class SOP04PlanReviewService(BaseSOP):
    SOP_NUMBER = "04"

    @classmethod
    def start_review(cls, project_id: int, owner_name: str,
                     plan_set_file: str, plan_issue_date: str,
                     project_type: str) -> dict:
        """Create SOP 04 instance. Trigger: plans received from architect."""
        instance = cls.create_instance(
            project_id=project_id,
            owner_name=owner_name,
            owner_role="pm",
            target_issue_date=plan_issue_date,
        )
        cls.confirm_input(instance["id"], "plan_set_file", plan_set_file)
        cls.confirm_input(instance["id"], "plan_issue_date", plan_issue_date)
        cls.confirm_input(instance["id"], "project_type", project_type)
        cls.transition_status(instance["id"], SOPStatus.IN_PROGRESS, owner_name,
                              "Plan review started")
        return {"instance": instance, "status": SOPStatus.IN_PROGRESS.value,
                "next_step": "Add plan sections via add_plan_section(), then run AI analysis."}

    @classmethod
    def validate_inputs(cls, instance_id: int) -> dict:
        missing = cls.get_missing_inputs(instance_id, REQUIRED_INPUT_KEYS)
        if missing:
            current = cls.get_instance(instance_id) or {}
            if current.get("status") != SOPStatus.INPUTS_MISSING.value:
                cls.transition_status(instance_id, SOPStatus.INPUTS_MISSING,
                                      "system", "Auto: missing required inputs")
            StopConditionChecker.check_sc01_inputs(
                instance_id, [INPUT_LABELS.get(k, k) for k in missing]
            )
        cls.transition_status(instance_id, SOPStatus.READY_TO_START,
                              "system", "All inputs confirmed")
        return {"status": SOPStatus.READY_TO_START.value, "missing_inputs": []}

    @classmethod
    def add_plan_section(cls, instance_id: int, section_data: dict,
                         actor: str = "pm") -> dict:
        """Add a trade-specific plan section for review."""
        section = PlanSection(
            trade_code=section_data.get("trade_code", ""),
            trade_name=section_data.get("trade_name", ""),
            page_refs=section_data.get("page_refs", []),
            scope_notes=section_data.get("scope_notes", ""),
            gaps_found=section_data.get("gaps_found", []),
            conflicts_found=section_data.get("conflicts_found", []),
            constructibility_issues=section_data.get("constructibility_issues", []),
        )
        errors = section.validate()
        if errors:
            return {"status": "validation_error", "errors": errors}

        output_id = cls.save_output(
            instance_id, "plan_section", f"Plan Review — {section.trade_name}",
            content=section.to_dict()
        )
        cls._log_event(instance_id, "section_added", section.trade_name, actor)
        return {"output_id": output_id, "trade_name": section.trade_name}

    @classmethod
    def run_ai_analysis(cls, instance_id: int) -> dict:
        """Layer 3: AI reviews all plan sections and produces cross-trade risk analysis."""
        rows = db.query("""
            SELECT content FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'plan_section'
        """, (instance_id,))
        sections = [
            json.loads(r["content"]) if isinstance(r["content"], str) else r["content"]
            for r in rows
        ]

        instance = cls.get_instance(instance_id) or {}
        project_type = ""
        inp_rows = db.query("""
            SELECT input_key, confirmed_by FROM sop_inputs
            WHERE sop_instance_id = %s AND input_key = 'project_type'
        """, (instance_id,))
        if inp_rows:
            project_type = inp_rows[0].get("confirmed_by", "")

        # Run AI analysis per section
        ai_sections = []
        for s in sections:
            ai_result = SOP04Agent.analyze_plan_section(
                trade_code=s.get("trade_code", ""),
                trade_name=s.get("trade_name", ""),
                scope_notes=s.get("scope_notes", ""),
                project_type=project_type,
                page_refs=s.get("page_refs", []),
            )
            # Merge AI findings into section
            s["gaps_found"] = list(set(s.get("gaps_found", []) + ai_result.get("gaps_found", [])))
            s["conflicts_found"] = list(set(s.get("conflicts_found", []) + ai_result.get("conflicts_found", [])))
            s["constructibility_issues"] = list(set(
                s.get("constructibility_issues", []) + ai_result.get("constructibility_issues", [])
            ))
            s["ai_reviewed"] = True
            ai_sections.append(s)

        # Cross-trade risk analysis
        cross_risks = SOP04Agent.flag_constructibility_risks(ai_sections, project_type)

        # Generate RFI list
        rfi_list = SOP04Agent.generate_rfi_list(ai_sections)

        cls.save_output(instance_id, "ai_plan_analysis", "AI Plan Review Analysis",
                        content={"cross_risks": cross_risks, "rfi_list": rfi_list,
                                 "sections_reviewed": len(ai_sections)})

        cur = cls.get_instance(instance_id)
        if cur and cur["status"] != SOPStatus.AI_DRAFTED.value:
            cls.transition_status(instance_id, SOPStatus.AI_DRAFTED, "AI",
                                  "AI plan review complete")

        if cross_risks.get("overall_severity") == "HIGH":
            try:
                high = [r["description"] for r in cross_risks.get("cross_trade_risks", [])
                        if r.get("severity") == "HIGH"]
                StopConditionChecker.check_sc03_risk_flags(instance_id, [{"description": d} for d in high])
            except WorkflowBlockedError as e:
                return {"cross_risks": cross_risks, "rfi_list": rfi_list,
                        "stop_condition": str(e), "action_required": e.resolution_path}

        return {"cross_risks": cross_risks, "rfi_list": rfi_list,
                "sections_reviewed": len(ai_sections)}

    @classmethod
    def pm_confirm(cls, instance_id: int, pm_name: str) -> dict:
        """PM confirms plan review is complete. Transitions to Approved."""
        cls.transition_status(instance_id, SOPStatus.INTERNAL_REVIEW, pm_name,
                              "PM reviewing plan sections")
        cls.transition_status(instance_id, SOPStatus.APPROVED, pm_name,
                              "Plan review confirmed complete by PM")
        return {"status": SOPStatus.APPROVED.value, "confirmed_by": pm_name}

    @classmethod
    def hand_off_to_sop05(cls, instance_id: int, actor: str,
                           project_id: int, owner_name: str,
                           project_type: str, plan_issue_date: str) -> dict:
        """Trigger SOP 05 (Construction Narrative). Transitions to Handed Off."""
        StopConditionChecker.check_sc07_handoff_destination(instance_id, owner_name)
        cls.transition_status(instance_id, SOPStatus.HANDED_OFF, actor,
                              f"Handed off to SOP 05 — {owner_name}")

        from sop_05_construction_narrative.sop_05_service import SOP05ConstructionNarrativeService
        sop05 = SOP05ConstructionNarrativeService.start_narrative(
            project_id=project_id,
            sop_04_instance_id=instance_id,
            owner_name=owner_name,
            project_type=project_type,
            plan_issue_date=plan_issue_date,
        )
        return {"sop_04_status": SOPStatus.HANDED_OFF.value, "sop_05_instance": sop05}

    @classmethod
    def get_full_status(cls, instance_id: int) -> dict:
        instance = cls.get_instance(instance_id)
        if not instance:
            return {"error": "Instance not found"}
        missing = cls.get_missing_inputs(instance_id, REQUIRED_INPUT_KEYS)
        rows = db.query(
            "SELECT output_type, output_label FROM sop_outputs WHERE sop_instance_id = %s",
            (instance_id,)
        )
        return {
            "instance": instance,
            "missing_inputs": [INPUT_LABELS.get(k, k) for k in missing],
            "outputs": [dict(r) for r in rows],
            "audit_trail": cls.get_audit_trail(instance_id),
        }

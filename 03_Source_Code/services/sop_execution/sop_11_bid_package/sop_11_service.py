"""SOP 11 — Bid Package Assembly: execution service (Layers 1+2)."""
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
from shared.sop_kpi import SOPKPITracker
from .sop_11_templates import (
    REQUIRED_INPUT_KEYS, INPUT_LABELS, ScopeSection, BidPackageOutput
)
from .sop_11_agent import SOP11Agent


class SOP11BidPackageService(BaseSOP):
    SOP_NUMBER = "11"

    # ── Layer 1 + Layer 2 Methods ──────────────────────────────────────────────

    @classmethod
    def start_bid_package(cls, project_id: int, owner_name: str,
                          target_issue_date: str, bid_due_date: str) -> dict:
        """Create a new SOP 11 instance. Trigger: project accepted for bid."""
        instance = cls.create_instance(
            project_id=project_id,
            owner_name=owner_name,
            owner_role="estimator",
            target_issue_date=target_issue_date,
            bid_due_date=bid_due_date,
        )
        return {"instance": instance, "status": SOPStatus.NOT_STARTED.value,
                "next_step": "Confirm all required inputs via confirm_input()."}

    @classmethod
    def validate_inputs(cls, instance_id: int) -> dict:
        """
        SC-01 check: verify all required inputs are confirmed.
        Transitions to Inputs Missing or Ready to Start.
        """
        missing = cls.get_missing_inputs(instance_id, REQUIRED_INPUT_KEYS)
        if missing:
            current = cls.get_instance(instance_id) or {}
            if current.get("status") != SOPStatus.INPUTS_MISSING.value:
                cls.transition_status(instance_id, SOPStatus.INPUTS_MISSING,
                                      "system", "Auto: missing required inputs")
            StopConditionChecker.check_sc01_inputs(
                instance_id,
                [INPUT_LABELS.get(k, k) for k in missing]
            )
        cls.transition_status(instance_id, SOPStatus.READY_TO_START,
                              "system", "All inputs confirmed")
        return {"status": SOPStatus.READY_TO_START.value, "missing_inputs": []}

    @classmethod
    def start_work(cls, instance_id: int, actor: str) -> dict:
        """Transition Ready to Start → In Progress. Call after all inputs confirmed."""
        cls.transition_status(instance_id, SOPStatus.IN_PROGRESS, actor,
                              "Work started — scope assembly in progress")
        return {"status": SOPStatus.IN_PROGRESS.value, "actor": actor}

    @classmethod
    def add_scope_section(cls, instance_id: int, section_data: dict,
                          owner_name: str) -> dict:
        """Add a trade scope section to this bid package instance."""
        section = ScopeSection(**{
            k: section_data[k]
            for k in ("trade_code", "trade_name", "scope_text")
            if k in section_data
        })
        for attr in ("drawing_refs", "spec_refs", "allowances", "alternates",
                     "exclusions", "bid_bond_required"):
            if attr in section_data:
                setattr(section, attr, section_data[attr])

        errors = section.validate()
        if errors:
            return {"status": "validation_error", "errors": errors}

        output_id = cls.save_output(
            instance_id, "scope_section", f"Scope — {section.trade_name}",
            content=section.to_dict()
        )
        cls._log_event(instance_id, "scope_section_added",
                       section.trade_name, owner_name)
        return {"output_id": output_id, "trade_name": section.trade_name,
                "status": "saved"}

    @classmethod
    def run_ai_review(cls, instance_id: int) -> dict:
        """Layer 3: AI gap check on all scope sections. Transitions to AI Drafted."""
        rows = db.query("""
            SELECT content FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'scope_section'
        """, (instance_id,))
        sections = [json.loads(r["content"]) if isinstance(r["content"], str)
                    else r["content"] for r in rows]

        missing = cls.get_missing_inputs(instance_id, REQUIRED_INPUT_KEYS)
        missing_report = SOP11Agent.check_inputs_missing(missing)
        if missing_report:
            return missing_report

        result = SOP11Agent.review_scope_sections(instance_id, sections)

        # Store AI review as an output
        cls.save_output(instance_id, "ai_gap_report", "AI Scope Gap Report",
                        content=result)

        # Check for HIGH severity gaps → SC-03
        high_risks = [f for f in result.get("risk_flags", [])
                      if f.get("severity") == "HIGH"]

        current = cls.get_instance(instance_id) or {}
        if current.get("status") != SOPStatus.AI_DRAFTED.value:
            cls.transition_status(instance_id, SOPStatus.AI_DRAFTED, "AI",
                                  "AI gap review complete")

        if high_risks:
            try:
                StopConditionChecker.check_sc03_risk_flags(instance_id, high_risks)
            except WorkflowBlockedError as e:
                result["stop_condition"] = str(e)
                result["action_required"] = e.resolution_path

        return result

    @classmethod
    def submit_for_review(cls, instance_id: int, reviewer_name: str) -> dict:
        """PM picks up draft for Internal Review."""
        cls.transition_status(instance_id, SOPStatus.INTERNAL_REVIEW,
                              reviewer_name, "Submitted for PM review")
        return {"status": SOPStatus.INTERNAL_REVIEW.value,
                "reviewer": reviewer_name}

    @classmethod
    def revision_required(cls, instance_id: int, reviewer_name: str,
                          comments: str) -> dict:
        """Reviewer sends back for revision. SC-05 invoked."""
        cls.transition_status(instance_id, SOPStatus.REVISION_REQUIRED,
                              reviewer_name, f"Revision: {comments}")
        cls._log_event(instance_id, "revision_comment", comments, reviewer_name)
        return {"status": SOPStatus.REVISION_REQUIRED.value, "comments": comments}

    @classmethod
    def request_buck_approval(cls, instance_id: int, pm_name: str,
                              summary: str = "") -> dict:
        """PM routes to Buck for Gate 11-C approval."""
        cls.transition_status(instance_id, SOPStatus.APPROVAL_REQUIRED,
                              pm_name, "Routed to Buck for Gate 11-C")
        return {"status": SOPStatus.APPROVAL_REQUIRED.value,
                "next_step": "Buck must call record_buck_approval() to approve."}

    @classmethod
    def record_buck_approval(cls, instance_id: int, approver: str = "Buck Adams",
                             conditions: str | None = None) -> dict:
        """Gate 11-C: Buck approves bid package for issue."""
        ApprovalEngine.create_gate_record(
            sop_instance_id=instance_id,
            gate_id="AG-11-C",
            gate_name="Bid Package Issue Authority",
            required_before_status=SOPStatus.ISSUED.value,
            approver_name=approver,
            approver_role="Principal",
            conditions=conditions,
        )
        cls.transition_status(instance_id, SOPStatus.APPROVED, approver,
                              "Gate 11-C: Buck approved bid package for issue")
        return {"status": SOPStatus.APPROVED.value, "gate": "AG-11-C",
                "approver": approver}

    @classmethod
    def issue_bid_package(cls, instance_id: int, actor: str,
                          recipient_list: list[str]) -> dict:
        """
        Mark as Issued. SC-04 and SC-07 enforced.
        recipient_list = list of sub names receiving the package.
        """
        # SC-04: Must have Gate 11-C
        StopConditionChecker.check_sc04_approval_gate(
            instance_id, "AG-11-C", "Bid Package Issue Authority"
        )
        # SC-07: Must have recipients
        StopConditionChecker.check_sc07_handoff_destination(
            instance_id, ", ".join(recipient_list) if recipient_list else None
        )

        cls.save_output(instance_id, "bid_issue_record",
                        "Bid Package Issue Record",
                        content={"recipients": recipient_list, "issued_by": actor})

        db.execute("""
            UPDATE sop_instances SET actual_issue_date = CURRENT_DATE
            WHERE id = %s
        """, (instance_id,))

        cls.transition_status(instance_id, SOPStatus.ISSUED, actor,
                              f"Issued to {len(recipient_list)} subs")

        # Record KPI: days from In Progress to Issued
        hours = SOPKPITracker.compute_cycle_time(
            instance_id, SOPStatus.IN_PROGRESS.value, SOPStatus.ISSUED.value
        )
        if hours:
            row = db.query_one("SELECT project_id FROM sop_instances WHERE id = %s",
                               (instance_id,))
            pid = row["project_id"] if row else None
            SOPKPITracker.record_kpi(instance_id, "SOP11_CYCLE_HOURS", hours,
                                     "hours", pid)

        return {"status": SOPStatus.ISSUED.value, "recipients": recipient_list,
                "note": "Trigger SOP 13 (Bid Distribution) and SOP 14 (Bid Follow-Up)."}

    @classmethod
    def hand_off_to_sop15(cls, instance_id: int, actor: str,
                           project_id: int, owner_name: str) -> dict:
        """Trigger SOP 15 after bid close date. Transitions to Handed Off."""
        # SC-07: confirm handoff
        StopConditionChecker.check_sc07_handoff_destination(instance_id, owner_name)
        cls.transition_status(instance_id, SOPStatus.HANDED_OFF, actor,
                              f"Handed off to SOP 15 — {owner_name}")

        from sop_15_bid_leveling.sop_15_service import SOP15BidLevelingService
        from datetime import date
        sop15 = SOP15BidLevelingService.start_leveling(
            project_id=project_id,
            sop_11_instance_id=instance_id,
            owner_name=owner_name,
        )
        return {"sop_11_status": SOPStatus.HANDED_OFF.value,
                "sop_15_instance": sop15}

    @classmethod
    def get_full_status(cls, instance_id: int) -> dict:
        """Full status view: instance + inputs + outputs + gates + stops."""
        instance = cls.get_instance(instance_id)
        if not instance:
            return {"error": "Instance not found"}
        missing = cls.get_missing_inputs(instance_id, REQUIRED_INPUT_KEYS)
        gates = ApprovalEngine.get_gates(instance_id)
        audit = cls.get_audit_trail(instance_id)

        rows = db.query(
            "SELECT output_type, output_label FROM sop_outputs WHERE sop_instance_id = %s",
            (instance_id,)
        )
        outputs = [dict(r) for r in rows]

        return {
            "instance": instance,
            "missing_inputs": [INPUT_LABELS.get(k, k) for k in missing],
            "approval_gates": gates,
            "outputs": outputs,
            "audit_trail": audit,
        }

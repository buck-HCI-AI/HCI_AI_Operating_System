"""SOP 16 — Buyout: execution service (Layers 1+2)."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import services.db as db
from shared.base_sop import BaseSOP
from shared.sop_data_model import SOPStatus
from shared.stop_condition import StopConditionChecker
from shared.approval_engine import ApprovalEngine
from shared.sop_kpi import SOPKPITracker
from .sop_16_templates import (
    REQUIRED_INPUT_KEYS, INPUT_LABELS, BuyoutRecord
)
from .sop_16_agent import SOP16Agent


class SOP16BuyoutService(BaseSOP):
    SOP_NUMBER = "16"

    @classmethod
    def start_buyout(cls, project_id: int, sop_15_instance_id: int,
                     owner_name: str) -> dict:
        """Create SOP 16 instance. Triggered after SOP 15 award (Gate 15-C)."""
        instance = cls.create_instance(
            project_id=project_id,
            owner_name=owner_name,
            owner_role="pm",
            parent_instance_id=sop_15_instance_id,
        )
        cls.confirm_input(instance["id"], "sop_15_instance_id", str(sop_15_instance_id))
        return {"instance": instance, "status": SOPStatus.NOT_STARTED.value,
                "parent_sop_15": sop_15_instance_id,
                "next_step": "Confirm all required inputs via set_inputs(), then draft award memo."}

    @classmethod
    def set_inputs(cls, instance_id: int, inputs: dict,
                   actor: str = "pm") -> dict:
        """Confirm all required inputs for this buyout instance."""
        for key in REQUIRED_INPUT_KEYS:
            if key in inputs:
                cls.confirm_input(instance_id, key, str(inputs[key]))

        missing = cls.get_missing_inputs(instance_id, REQUIRED_INPUT_KEYS)
        if missing:
            current = cls.get_instance(instance_id) or {}
            if current.get("status") != SOPStatus.INPUTS_MISSING.value:
                cls.transition_status(instance_id, SOPStatus.INPUTS_MISSING,
                                      "system", "Auto: missing required inputs")
            return {"status": SOPStatus.INPUTS_MISSING.value,
                    "missing_inputs": [INPUT_LABELS.get(k, k) for k in missing]}

        cls.transition_status(instance_id, SOPStatus.IN_PROGRESS, actor,
                              "All inputs confirmed — buyout in progress")
        return {"status": SOPStatus.IN_PROGRESS.value, "missing_inputs": []}

    @classmethod
    def draft_award_memo(cls, instance_id: int,
                          actor: str = "pm") -> dict:
        """Layer 3: AI drafts the award memo for PM review."""
        # Load awarded sub details from inputs
        _rows = db.query(
            "SELECT input_key, confirmed_by FROM sop_inputs WHERE sop_instance_id = %s",
            (instance_id,)
        )
        inputs = {r["input_key"]: r["confirmed_by"] for r in _rows}

        awarded_sub = inputs.get("awarded_sub", "")
        trade_name = inputs.get("trade_name", "")
        trade_code = inputs.get("trade_code", "")
        award_amount = float(inputs.get("award_amount", 0))
        scope_basis = inputs.get("scope_basis", "")
        subcontract_type = inputs.get("subcontract_type", "lump_sum")
        conditions = inputs.get("conditions", "")
        rationale = inputs.get("rationale", "")

        if not awarded_sub or not award_amount:
            return {"error": "awarded_sub and award_amount must be confirmed before drafting"}

        memo = SOP16Agent.draft_award_memo(
            awarded_sub=awarded_sub,
            trade_name=trade_name,
            trade_code=trade_code,
            award_amount=award_amount,
            scope_basis=scope_basis,
            subcontract_type=subcontract_type,
            conditions=conditions,
            rationale=rationale,
        )

        output_id = cls.save_output(instance_id, "award_memo_draft",
                                    f"Award Memo Draft — {awarded_sub}",
                                    content=memo)
        cls._log_event(instance_id, "award_memo_drafted", awarded_sub, actor)

        cur = cls.get_instance(instance_id)
        if cur and cur["status"] == SOPStatus.IN_PROGRESS.value:
            cls.transition_status(instance_id, SOPStatus.AI_DRAFTED, "AI",
                                  "AI award memo draft complete")

        memo["output_id"] = output_id
        return memo

    @classmethod
    def confirm_scope(cls, instance_id: int, sub_scope_statement: str,
                      actor: str = "pm") -> dict:
        """AI compares leveled scope to sub's scope statement. PM reviews output."""
        _rows = db.query(
            "SELECT input_key, confirmed_by FROM sop_inputs WHERE sop_instance_id = %s",
            (instance_id,)
        )
        inputs = {r["input_key"]: r["confirmed_by"] for r in _rows}

        scope_basis = inputs.get("scope_basis", "")
        trade_name = inputs.get("trade_name", "")

        comparison = SOP16Agent.check_scope_alignment(
            leveled_scope=scope_basis,
            sub_scope_statement=sub_scope_statement,
            trade_name=trade_name,
        )

        cls.save_output(instance_id, "scope_comparison",
                        "AI Scope Alignment Check", content=comparison)
        cls._log_event(instance_id, "scope_check_run",
                       f"aligned={comparison.get('aligned')}", actor)

        if not comparison.get("aligned") and comparison.get("discrepancies"):
            high = [d for d in comparison["discrepancies"]
                    if d.get("severity") == "HIGH"]
            if high:
                return {
                    "status": "scope_misalignment",
                    "comparison": comparison,
                    "action_required": "Resolve HIGH-severity discrepancies with sub before initiating subcontract.",
                }

        return {"status": "scope_checked", "comparison": comparison}

    @classmethod
    def initiate_subcontract(cls, instance_id: int, subcontract_type: str,
                              conditions: str = "",
                              actor: str = "pm") -> dict:
        """Record that subcontract initiation has been triggered."""
        record = {
            "subcontract_type": subcontract_type,
            "conditions": conditions,
            "initiated_by": actor,
        }
        cls.save_output(instance_id, "subcontract_initiation",
                        "Subcontract Initiation Record", content=record)
        cls._log_event(instance_id, "subcontract_initiated",
                       f"type={subcontract_type}", actor)
        cls.transition_status(instance_id, SOPStatus.INTERNAL_REVIEW, actor,
                              "Subcontract initiated — PM confirming buyout")
        return {"status": SOPStatus.INTERNAL_REVIEW.value,
                "subcontract_type": subcontract_type,
                "next_step": "Call pm_confirm_buyout() when all scope and contract items are confirmed."}

    @classmethod
    def pm_confirm_buyout(cls, instance_id: int, pm_name: str) -> dict:
        """PM confirms buyout complete. Creates Gate 16-C record."""
        _rows = db.query(
            "SELECT input_key, confirmed_by FROM sop_inputs WHERE sop_instance_id = %s",
            (instance_id,)
        )
        inputs = {r["input_key"]: r["confirmed_by"] for r in _rows}

        awarded_sub = inputs.get("awarded_sub", "PM confirmed")
        award_amount = float(inputs.get("award_amount", 0))

        ApprovalEngine.create_gate_record(
            sop_instance_id=instance_id,
            gate_id="AG-16-C",
            gate_name="Buyout Completion Authority",
            required_before_status=SOPStatus.APPROVED.value,
            approver_name=pm_name,
            approver_role="PM",
            conditions=None,
        )

        # Ensure instance passes through INTERNAL_REVIEW if not already there
        cur = cls.get_instance(instance_id)
        cur_status = cur["status"] if cur else ""
        if cur_status not in (SOPStatus.INTERNAL_REVIEW.value,
                               SOPStatus.APPROVAL_REQUIRED.value,
                               SOPStatus.APPROVED.value):
            cls.transition_status(instance_id, SOPStatus.INTERNAL_REVIEW, pm_name,
                                  "Buyout review — PM confirming")

        cls.transition_status(instance_id, SOPStatus.APPROVED, pm_name,
                              f"Gate 16-C: PM confirmed buyout for {awarded_sub}")

        row2 = db.query_one("SELECT project_id FROM sop_instances WHERE id = %s",
                            (instance_id,))
        pid = row2["project_id"] if row2 else None
        if award_amount:
            SOPKPITracker.record_kpi(instance_id, "SOP16_BUYOUT_AMOUNT",
                                     award_amount, "$", pid)

        return {"status": SOPStatus.APPROVED.value, "gate": "AG-16-C",
                "confirmed_by": pm_name, "awarded_sub": awarded_sub,
                "award_amount": award_amount}

    @classmethod
    def hand_off_to_sop19(cls, instance_id: int, actor: str,
                           recipient: str = "contracts_team") -> dict:
        """Hand off to SOP 19 (Subcontract Agreement). Transitions to Handed Off."""
        StopConditionChecker.check_sc04_approval_gate(
            instance_id, "AG-16-C", "Buyout Completion Authority"
        )
        StopConditionChecker.check_sc07_handoff_destination(instance_id, recipient)
        cls.transition_status(instance_id, SOPStatus.HANDED_OFF, actor,
                              f"Handed off to SOP 19 — {recipient}")
        return {"status": SOPStatus.HANDED_OFF.value,
                "next_step": "Initiate SOP 19 (Subcontract Agreement) with contracts team."}

    @classmethod
    def get_full_status(cls, instance_id: int) -> dict:
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
            "outputs": outputs,
            "approval_gates": gates,
            "audit_trail": audit,
        }

"""SOP 07 — ROM Budget: execution service (Layers 1+2)."""
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
from .sop_07_templates import (
    REQUIRED_INPUT_KEYS, INPUT_LABELS, BUCK_ROM_REVIEW_THRESHOLD,
    CONTINGENCY_DEFAULTS, ROMLineItem,
)
from .sop_07_agent import SOP07Agent


class SOP07ROMBudgetService(BaseSOP):
    SOP_NUMBER = "07"

    @classmethod
    def start_rom(cls, project_id: int, owner_name: str, project_type: str,
                  gross_sf: float, sop_05_instance_id: int,
                  sop_06_instance_id: int | None = None,
                  owner_budget_target: float = 0) -> dict:
        """Create SOP 07 instance. Triggered from SOP 06 handoff."""
        instance = cls.create_instance(
            project_id=project_id,
            owner_name=owner_name,
            owner_role="pm",
            parent_instance_id=sop_05_instance_id,
        )
        cls.confirm_input(instance["id"], "project_type", project_type)
        cls.confirm_input(instance["id"], "gross_sf", str(gross_sf))
        cls.confirm_input(instance["id"], "sop_05_instance_id", str(sop_05_instance_id))
        if sop_06_instance_id:
            cls.confirm_input(instance["id"], "sop_06_instance_id", str(sop_06_instance_id))
        if owner_budget_target:
            cls.confirm_input(instance["id"], "owner_budget_target", str(owner_budget_target))

        cls.transition_status(instance["id"], SOPStatus.IN_PROGRESS, owner_name,
                              "ROM budget build started")
        return {"instance": instance, "status": SOPStatus.IN_PROGRESS.value,
                "parent_sop_05": sop_05_instance_id,
                "next_step": "Add line items via add_line_item() or run_ai_estimate() for full AI ROM."}

    @classmethod
    def add_line_item(cls, instance_id: int, item_data: dict,
                      actor: str = "pm") -> dict:
        """Manually add a ROM budget line item."""
        item = ROMLineItem(
            trade_code=item_data.get("trade_code", ""),
            trade_name=item_data.get("trade_name", ""),
            description=item_data.get("description", ""),
            unit=item_data.get("unit", "LS"),
            quantity=float(item_data.get("quantity", 1)),
            unit_cost=float(item_data.get("unit_cost", 0)),
            basis=item_data.get("basis", "pm_estimate"),
            ai_generated=item_data.get("ai_generated", False),
        )
        errors = item.validate()
        if errors:
            return {"status": "validation_error", "errors": errors}

        output_id = cls.save_output(
            instance_id, "rom_line_item", f"ROM — {item.trade_name}",
            content=item.to_dict()
        )
        cls._log_event(instance_id, "line_item_added", item.trade_name, actor)
        subtotal = cls._compute_subtotal(instance_id)
        return {"output_id": output_id, "trade_name": item.trade_name,
                "line_total": item.total(), "current_subtotal": subtotal}

    @classmethod
    def run_ai_estimate(cls, instance_id: int) -> dict:
        """Layer 3: AI generates a full ROM estimate from SOP 05 narratives."""
        inp_rows = db.query("""
            SELECT input_key, confirmed_by FROM sop_inputs WHERE sop_instance_id = %s
        """, (instance_id,))
        inputs = {r["input_key"]: r["confirmed_by"] for r in inp_rows}

        project_type = inputs.get("project_type", "commercial")
        gross_sf = float(inputs.get("gross_sf", 0))
        sop05_id = inputs.get("sop_05_instance_id")
        owner_budget_target = float(inputs.get("owner_budget_target", 0))

        narrative_sections = []
        if sop05_id:
            rows = db.query("""
                SELECT content FROM sop_outputs
                WHERE sop_instance_id = %s AND output_type = 'narrative_section'
            """, (int(sop05_id),))
            narrative_sections = [
                json.loads(r["content"]) if isinstance(r["content"], str) else r["content"]
                for r in rows
            ]

        ai_result = SOP07Agent.generate_rom_estimate(
            project_type, gross_sf, narrative_sections, owner_budget_target
        )

        # Auto-save AI line items
        for item_data in ai_result.get("line_items", []):
            item = ROMLineItem(
                trade_code=item_data.get("trade_code", "GEN"),
                trade_name=item_data.get("trade_name", "General"),
                description=item_data.get("description", ""),
                unit=item_data.get("unit", "LS"),
                quantity=float(item_data.get("quantity", 1)),
                unit_cost=float(item_data.get("unit_cost", 0)),
                basis=item_data.get("basis", "ai_estimate"),
                ai_generated=True,
            )
            cls.save_output(instance_id, "rom_line_item", f"ROM — {item.trade_name}",
                            content=item.to_dict())

        # Apply contingency
        contingency_pct = ai_result.get(
            "suggested_contingency_pct",
            CONTINGENCY_DEFAULTS.get(project_type, 0.10)
        )
        subtotal = cls._compute_subtotal(instance_id)
        contingency_amount = round(subtotal * contingency_pct, 2)
        total_estimated = round(subtotal + contingency_amount, 2)
        cost_per_sf = round(total_estimated / gross_sf, 2) if gross_sf else 0

        # Risk flags
        line_items_raw = db.query("""
            SELECT content FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'rom_line_item'
        """, (instance_id,))
        all_items = [
            json.loads(r["content"]) if isinstance(r["content"], str) else r["content"]
            for r in line_items_raw
        ]
        risk_flags = SOP07Agent.flag_high_risk_line_items(all_items, gross_sf)

        cls.save_output(instance_id, "rom_summary", "ROM Budget Summary",
                        content={
                            "subtotal": subtotal,
                            "contingency_pct": contingency_pct,
                            "contingency_amount": contingency_amount,
                            "total_estimated_cost": total_estimated,
                            "cost_per_sf": cost_per_sf,
                            "risk_flags": risk_flags,
                        })

        cur = cls.get_instance(instance_id)
        if cur and cur["status"] != SOPStatus.AI_DRAFTED.value:
            cls.transition_status(instance_id, SOPStatus.AI_DRAFTED, "AI",
                                  "AI ROM estimate complete")

        requires_buck = total_estimated > BUCK_ROM_REVIEW_THRESHOLD
        return {
            "subtotal": subtotal,
            "contingency_pct": contingency_pct,
            "contingency_amount": contingency_amount,
            "total_estimated_cost": total_estimated,
            "cost_per_sf": cost_per_sf,
            "risk_flags": risk_flags,
            "requires_buck_review": requires_buck,
            "low_confidence_trades": ai_result.get("low_confidence_trades", []),
        }

    @classmethod
    def pm_review(cls, instance_id: int, pm_name: str) -> dict:
        """PM reviews ROM estimate. Routes to Buck if > threshold."""
        subtotal = cls._compute_subtotal(instance_id)
        contingency = round(subtotal * 0.10, 2)
        total = round(subtotal + contingency, 2)
        requires_buck = total > BUCK_ROM_REVIEW_THRESHOLD

        cls.transition_status(instance_id, SOPStatus.INTERNAL_REVIEW, pm_name,
                              "PM reviewing ROM budget")
        if requires_buck:
            cls.transition_status(instance_id, SOPStatus.APPROVAL_REQUIRED, pm_name,
                                  f"ROM ${total:,.0f} > ${BUCK_ROM_REVIEW_THRESHOLD:,.0f} — Buck review required")
            return {"status": SOPStatus.APPROVAL_REQUIRED.value,
                    "total_estimated": total,
                    "requires_buck_review": True,
                    "next_step": "Buck must call buck_approve() before hand-off to SOP 09."}

        cls.transition_status(instance_id, SOPStatus.APPROVED, pm_name,
                              "ROM approved by PM — within threshold")
        return {"status": SOPStatus.APPROVED.value, "total_estimated": total,
                "requires_buck_review": False}

    @classmethod
    def buck_approve(cls, instance_id: int, approver: str = "Buck Adams",
                     conditions: str | None = None) -> dict:
        """Gate 07-C: Buck approves ROM > $500k."""
        subtotal = cls._compute_subtotal(instance_id)
        total = round(subtotal * 1.10, 2)
        ApprovalEngine.create_gate_record(
            sop_instance_id=instance_id,
            gate_id="AG-07-C",
            gate_name="ROM Budget Authorization",
            required_before_status=SOPStatus.APPROVED.value,
            approver_name=approver,
            approver_role="Principal",
            conditions=conditions,
        )
        cls.transition_status(instance_id, SOPStatus.APPROVED, approver,
                              f"Gate 07-C: Buck approved ROM ${total:,.0f}")

        row = db.query_one("SELECT project_id FROM sop_instances WHERE id = %s", (instance_id,))
        pid = row["project_id"] if row else None
        SOPKPITracker.record_kpi(instance_id, "SOP07_ROM_TOTAL", total, "$", pid)

        return {"status": SOPStatus.APPROVED.value, "gate": "AG-07-C",
                "total_estimated": total, "approver": approver}

    @classmethod
    def hand_off_to_sop09(cls, instance_id: int, actor: str,
                           project_id: int, owner_name: str,
                           project_type: str) -> dict:
        """Trigger SOP 09 (Budget Review). Transitions to Handed Off."""
        if cls._compute_subtotal(instance_id) * 1.10 > BUCK_ROM_REVIEW_THRESHOLD:
            StopConditionChecker.check_sc04_approval_gate(
                instance_id, "AG-07-C", "ROM Budget Authorization"
            )
        StopConditionChecker.check_sc07_handoff_destination(instance_id, owner_name)
        cls.transition_status(instance_id, SOPStatus.HANDED_OFF, actor,
                              f"Handed off to SOP 09 — {owner_name}")

        from sop_09_budget_review.sop_09_service import SOP09BudgetReviewService
        sop09 = SOP09BudgetReviewService.start_review(
            project_id=project_id,
            sop_07_instance_id=instance_id,
            owner_name=owner_name,
            project_type=project_type,
        )
        return {"sop_07_status": SOPStatus.HANDED_OFF.value, "sop_09_instance": sop09}

    @classmethod
    def _compute_subtotal(cls, instance_id: int) -> float:
        rows = db.query("""
            SELECT COALESCE(
                SUM((content->>'quantity')::numeric * (content->>'unit_cost')::numeric), 0
            ) AS total
            FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'rom_line_item'
        """, (instance_id,))
        return float(rows[0]["total"]) if rows else 0.0

    @classmethod
    def get_full_status(cls, instance_id: int) -> dict:
        instance = cls.get_instance(instance_id)
        if not instance:
            return {"error": "Instance not found"}
        subtotal = cls._compute_subtotal(instance_id)
        missing = cls.get_missing_inputs(instance_id, REQUIRED_INPUT_KEYS)
        gates = ApprovalEngine.get_gates(instance_id)
        return {
            "instance": instance,
            "missing_inputs": [INPUT_LABELS.get(k, k) for k in missing],
            "current_subtotal": subtotal,
            "estimated_total_with_contingency": round(subtotal * 1.10, 2),
            "requires_buck_review": subtotal * 1.10 > BUCK_ROM_REVIEW_THRESHOLD,
            "approval_gates": gates,
            "audit_trail": cls.get_audit_trail(instance_id),
        }

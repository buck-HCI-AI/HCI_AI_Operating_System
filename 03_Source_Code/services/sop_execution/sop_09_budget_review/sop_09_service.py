"""SOP 09 — Budget Review: execution service (Layers 1+2)."""
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
from shared.sop_kpi import SOPKPITracker
from .sop_09_templates import (
    REQUIRED_INPUT_KEYS, INPUT_LABELS,
    BUCK_BUDGET_REVIEW_THRESHOLD, BUDGET_VARIANCE_ALERT_PCT,
    BudgetLineItem,
)
from .sop_09_agent import SOP09Agent


class SOP09BudgetReviewService(BaseSOP):
    SOP_NUMBER = "09"

    @classmethod
    def start_review(cls, project_id: int, sop_07_instance_id: int,
                     owner_name: str, project_type: str,
                     owner_budget_target: float = 0) -> dict:
        """Create SOP 09 instance. Triggered from SOP 07 handoff."""
        instance = cls.create_instance(
            project_id=project_id,
            owner_name=owner_name,
            owner_role="pm",
            parent_instance_id=sop_07_instance_id,
        )
        cls.confirm_input(instance["id"], "sop_07_instance_id", str(sop_07_instance_id))
        cls.confirm_input(instance["id"], "project_type", project_type)
        if owner_budget_target:
            cls.confirm_input(instance["id"], "owner_budget_target", str(owner_budget_target))

        cls.transition_status(instance["id"], SOPStatus.IN_PROGRESS, owner_name,
                              "Budget review started")
        return {"instance": instance, "status": SOPStatus.IN_PROGRESS.value,
                "parent_sop_07": sop_07_instance_id,
                "next_step": "Add revised line items via revise_line_item() or run_ai_review() to compare against ROM."}

    @classmethod
    def revise_line_item(cls, instance_id: int, item_data: dict,
                         actor: str = "pm") -> dict:
        """Add or update a revised budget line item (vs ROM)."""
        item = BudgetLineItem(
            trade_code=item_data.get("trade_code", ""),
            trade_name=item_data.get("trade_name", ""),
            description=item_data.get("description", ""),
            rom_amount=float(item_data.get("rom_amount", 0)),
            revised_amount=float(item_data.get("revised_amount", 0)),
            basis=item_data.get("basis", ""),
            pm_notes=item_data.get("pm_notes", ""),
        )
        if not item.trade_code or not item.description:
            return {"status": "validation_error",
                    "errors": ["trade_code and description are required"]}

        output_id = cls.save_output(
            instance_id, "budget_line_item",
            f"Budget — {item.trade_name}", content=item.to_dict()
        )
        cls._log_event(instance_id, "line_item_revised", item.trade_name, actor)
        return {"output_id": output_id, "trade_name": item.trade_name,
                "variance_pct": item.variance_pct()}

    @classmethod
    def run_ai_review(cls, instance_id: int) -> dict:
        """Layer 3: AI compares ROM to revised budget and generates variance report."""
        inp_rows = db.query("""
            SELECT input_key, confirmed_by FROM sop_inputs WHERE sop_instance_id = %s
        """, (instance_id,))
        inputs = {r["input_key"]: r["confirmed_by"] for r in inp_rows}

        project_type = inputs.get("project_type", "commercial")
        sop07_id = inputs.get("sop_07_instance_id")
        owner_budget_target = float(inputs.get("owner_budget_target", 0))

        # Pull ROM line items from SOP 07
        rom_items = []
        if sop07_id:
            rows = db.query("""
                SELECT content FROM sop_outputs
                WHERE sop_instance_id = %s AND output_type = 'rom_line_item'
            """, (int(sop07_id),))
            rom_items = [
                json.loads(r["content"]) if isinstance(r["content"], str) else r["content"]
                for r in rows
            ]

        # Pull revised budget line items from this instance
        rev_rows = db.query("""
            SELECT content FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'budget_line_item'
        """, (instance_id,))
        revised_items = [
            json.loads(r["content"]) if isinstance(r["content"], str) else r["content"]
            for r in rev_rows
        ]

        # If no revised items, use ROM as baseline
        if not revised_items:
            revised_items = rom_items

        variance_analysis = SOP09Agent.analyze_budget_variance(
            rom_items, revised_items, project_type
        )

        # Owner budget check
        revised_total = sum(
            i.get("revised_amount", i.get("rom_amount", 0)) for i in revised_items
        )
        owner_check = SOP09Agent.review_vs_owner_target(
            revised_total, owner_budget_target, project_type
        )
        if owner_check:
            variance_analysis["owner_budget_check"] = owner_check

        cls.save_output(instance_id, "budget_variance_report",
                        "AI Budget Variance Report", content=variance_analysis)

        cur = cls.get_instance(instance_id)
        if cur and cur["status"] == SOPStatus.IN_PROGRESS.value:
            cls.transition_status(instance_id, SOPStatus.AI_DRAFTED, "AI",
                                  "AI budget variance review complete")

        return variance_analysis

    @classmethod
    def pm_approve(cls, instance_id: int, pm_name: str) -> dict:
        """PM reviews and routes to Buck if budget > threshold."""
        revised_total = cls._compute_revised_total(instance_id)
        requires_buck = revised_total > BUCK_BUDGET_REVIEW_THRESHOLD

        cls.transition_status(instance_id, SOPStatus.INTERNAL_REVIEW, pm_name,
                              "PM reviewing final budget")
        if requires_buck:
            cls.transition_status(instance_id, SOPStatus.APPROVAL_REQUIRED, pm_name,
                                  f"Budget ${revised_total:,.0f} > ${BUCK_BUDGET_REVIEW_THRESHOLD:,.0f} — Buck approval required")
            return {"status": SOPStatus.APPROVAL_REQUIRED.value,
                    "revised_total": revised_total,
                    "requires_buck_approval": True,
                    "next_step": "Buck must call buck_approve() before hand-off to SOP 10."}

        cls.transition_status(instance_id, SOPStatus.APPROVED, pm_name,
                              "Budget approved by PM — within threshold")
        return {"status": SOPStatus.APPROVED.value,
                "revised_total": revised_total, "requires_buck_approval": False}

    @classmethod
    def buck_approve(cls, instance_id: int, approver: str = "Buck Adams",
                     conditions: str | None = None,
                     project_name: str = "") -> dict:
        """Gate 09-C: Buck approves budget > $500k before proceeding to bid."""
        revised_total = cls._compute_revised_total(instance_id)

        inp_rows = db.query("""
            SELECT confirmed_by FROM sop_inputs
            WHERE sop_instance_id = %s AND input_key = 'project_type'
        """, (instance_id,))
        project_type = inp_rows[0]["confirmed_by"] if inp_rows else "commercial"

        # Generate Buck review summary
        summary = SOP09Agent.generate_buck_review_summary(
            {"revised_total": revised_total,
             "rom_total": cls._compute_rom_total(instance_id),
             "variance_pct": 0, "flagged_count": 0},
            project_type, project_name
        )

        ApprovalEngine.create_gate_record(
            sop_instance_id=instance_id,
            gate_id="AG-09-C",
            gate_name="Budget Approval Authority",
            required_before_status=SOPStatus.APPROVED.value,
            approver_name=approver,
            approver_role="Principal",
            conditions=conditions,
        )

        cls.save_output(instance_id, "buck_review_summary",
                        "Buck Budget Review Summary", content=summary)
        cls.transition_status(instance_id, SOPStatus.APPROVED, approver,
                              f"Gate 09-C: Buck approved budget ${revised_total:,.0f}")

        row = db.query_one("SELECT project_id FROM sop_instances WHERE id = %s", (instance_id,))
        pid = row["project_id"] if row else None
        SOPKPITracker.record_kpi(instance_id, "SOP09_APPROVED_BUDGET",
                                  revised_total, "$", pid)

        return {"status": SOPStatus.APPROVED.value, "gate": "AG-09-C",
                "approved_budget": revised_total, "approver": approver,
                "summary": summary}

    @classmethod
    def hand_off_to_sop10(cls, instance_id: int, actor: str,
                           project_id: int, owner_name: str) -> dict:
        """Trigger SOP 10 (Allowances / Alternates / Exclusions). Transitions to Handed Off."""
        revised_total = cls._compute_revised_total(instance_id)
        if revised_total > BUCK_BUDGET_REVIEW_THRESHOLD:
            StopConditionChecker.check_sc04_approval_gate(
                instance_id, "AG-09-C", "Budget Approval Authority"
            )
        StopConditionChecker.check_sc07_handoff_destination(instance_id, owner_name)
        cls.transition_status(instance_id, SOPStatus.HANDED_OFF, actor,
                              f"Handed off to SOP 10 — {owner_name}")

        from sop_10_allowances.sop_10_service import SOP10AllowancesService
        sop10 = SOP10AllowancesService.start_allowances(
            project_id=project_id,
            owner_name=owner_name,
        )
        # Auto-confirm budget approved input
        SOP10AllowancesService.confirm_input(
            sop10["instance"]["id"], "sop09_budget_approved", "true"
        )
        return {"sop_09_status": SOPStatus.HANDED_OFF.value, "sop_10_instance": sop10}

    @classmethod
    def _compute_revised_total(cls, instance_id: int) -> float:
        rows = db.query("""
            SELECT COALESCE(
                SUM(COALESCE((content->>'revised_amount')::numeric, (content->>'rom_amount')::numeric, 0)),
                0
            ) AS total
            FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'budget_line_item'
        """, (instance_id,))
        if rows and float(rows[0]["total"]) > 0:
            return float(rows[0]["total"])
        return cls._compute_rom_total(instance_id)

    @classmethod
    def _compute_rom_total(cls, instance_id: int) -> float:
        inp_rows = db.query("""
            SELECT confirmed_by FROM sop_inputs
            WHERE sop_instance_id = %s AND input_key = 'sop_07_instance_id'
        """, (instance_id,))
        if not inp_rows:
            return 0.0
        sop07_id = int(inp_rows[0]["confirmed_by"])
        rows = db.query("""
            SELECT COALESCE(
                SUM((content->>'quantity')::numeric * (content->>'unit_cost')::numeric), 0
            ) AS total
            FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'rom_line_item'
        """, (sop07_id,))
        return float(rows[0]["total"]) * 1.10 if rows else 0.0

    @classmethod
    def get_full_status(cls, instance_id: int) -> dict:
        instance = cls.get_instance(instance_id)
        if not instance:
            return {"error": "Instance not found"}
        missing = cls.get_missing_inputs(instance_id, REQUIRED_INPUT_KEYS)
        revised_total = cls._compute_revised_total(instance_id)
        gates = ApprovalEngine.get_gates(instance_id)
        return {
            "instance": instance,
            "missing_inputs": [INPUT_LABELS.get(k, k) for k in missing],
            "revised_total": revised_total,
            "requires_buck_approval": revised_total > BUCK_BUDGET_REVIEW_THRESHOLD,
            "approval_gates": gates,
            "audit_trail": cls.get_audit_trail(instance_id),
        }

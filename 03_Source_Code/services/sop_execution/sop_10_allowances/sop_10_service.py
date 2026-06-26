"""SOP 10 — Allowances / Alternates / Exclusions: execution service (Layers 1+2)."""
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
from .sop_10_templates import (
    REQUIRED_INPUT_KEYS, INPUT_LABELS, BUCK_REVIEW_THRESHOLD,
    AllowanceItem, AlternateItem, ExclusionItem,
)
from .sop_10_agent import SOP10Agent


class SOP10AllowancesService(BaseSOP):
    SOP_NUMBER = "10"

    @classmethod
    def start_allowances(cls, project_id: int, owner_name: str) -> dict:
        """Create SOP 10 instance. Precedes SOP 11 Bid Package Assembly."""
        instance = cls.create_instance(
            project_id=project_id,
            owner_name=owner_name,
            owner_role="pm",
        )
        return {"instance": instance, "status": SOPStatus.NOT_STARTED.value,
                "next_step": "Confirm all required inputs via confirm_input(), "
                             "then add allowances, alternates, and exclusions."}

    @classmethod
    def validate_inputs(cls, instance_id: int) -> dict:
        """SC-01 check: verify all required inputs are confirmed."""
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
        """Transition Ready to Start → In Progress."""
        cls.transition_status(instance_id, SOPStatus.IN_PROGRESS, actor,
                              "Work started — allowances assembly in progress")
        return {"status": SOPStatus.IN_PROGRESS.value, "actor": actor}

    @classmethod
    def add_allowance(cls, instance_id: int, allowance_data: dict,
                      actor: str = "pm") -> dict:
        """Add an allowance item to this instance."""
        item = AllowanceItem(
            allowance_code=allowance_data.get("allowance_code", ""),
            description=allowance_data.get("description", ""),
            allowance_type=allowance_data.get("allowance_type", "construction_allowance"),
            amount=float(allowance_data.get("amount", 0)),
            trade_code=allowance_data.get("trade_code", "GEN"),
            basis=allowance_data.get("basis", ""),
            ai_suggested=allowance_data.get("ai_suggested", False),
            notes=allowance_data.get("notes", ""),
        )
        if not item.allowance_code or not item.description:
            return {"status": "validation_error",
                    "errors": ["allowance_code and description are required"]}

        output_id = cls.save_output(
            instance_id, "allowance_item", f"Allowance — {item.description}",
            content=item.to_dict()
        )
        cls._log_event(instance_id, "allowance_added", item.description, actor)

        total = cls._total_allowance_pool(instance_id)
        return {"output_id": output_id, "allowance_code": item.allowance_code,
                "amount": item.amount, "total_allowance_pool": total,
                "requires_buck_review": total > BUCK_REVIEW_THRESHOLD}

    @classmethod
    def add_alternate(cls, instance_id: int, alternate_data: dict,
                      actor: str = "pm") -> dict:
        """Add an alternate item to this instance."""
        item = AlternateItem(
            alternate_code=alternate_data.get("alternate_code", ""),
            description=alternate_data.get("description", ""),
            alternate_type=alternate_data.get("alternate_type", "additive"),
            estimated_cost_impact=float(alternate_data.get("estimated_cost_impact", 0)),
            trade_code=alternate_data.get("trade_code", "GEN"),
            basis=alternate_data.get("basis", ""),
            included_in_base=alternate_data.get("included_in_base", False),
        )
        if not item.alternate_code or not item.description:
            return {"status": "validation_error",
                    "errors": ["alternate_code and description are required"]}

        output_id = cls.save_output(
            instance_id, "alternate_item", f"Alternate — {item.description}",
            content=item.to_dict()
        )
        cls._log_event(instance_id, "alternate_added", item.description, actor)
        return {"output_id": output_id, "alternate_code": item.alternate_code,
                "cost_impact": item.estimated_cost_impact}

    @classmethod
    def add_exclusion(cls, instance_id: int, exclusion_data: dict,
                      actor: str = "pm") -> dict:
        """Add an exclusion item to this instance."""
        item = ExclusionItem(
            exclusion_code=exclusion_data.get("exclusion_code", ""),
            description=exclusion_data.get("description", ""),
            trade_code=exclusion_data.get("trade_code", "GEN"),
            excluded_party=exclusion_data.get("excluded_party", "subcontractor"),
            basis=exclusion_data.get("basis", ""),
        )
        if not item.exclusion_code or not item.description:
            return {"status": "validation_error",
                    "errors": ["exclusion_code and description are required"]}

        output_id = cls.save_output(
            instance_id, "exclusion_item", f"Exclusion — {item.description}",
            content=item.to_dict()
        )
        cls._log_event(instance_id, "exclusion_added", item.description, actor)
        return {"output_id": output_id, "exclusion_code": item.exclusion_code}

    @classmethod
    def run_ai_review(cls, instance_id: int, project_type: str,
                      scope_narrative: str) -> dict:
        """Layer 3: AI suggests allowances, flags alternates, validates exclusions."""
        # Auto-advance from READY_TO_START
        current = cls.get_instance(instance_id)
        if current and current["status"] == SOPStatus.READY_TO_START.value:
            cls.transition_status(instance_id, SOPStatus.IN_PROGRESS, "system",
                                  "Work started — AI review in progress")

        # Gather existing items
        rows = db.query("""
            SELECT output_type, content FROM sop_outputs
            WHERE sop_instance_id = %s
            AND output_type IN ('allowance_item', 'alternate_item', 'exclusion_item')
        """, (instance_id,))

        allowances, alternates, exclusions = [], [], []
        for row in rows:
            c = json.loads(row["content"]) if isinstance(row["content"], str) else row["content"]
            if row["output_type"] == "allowance_item":
                allowances.append(c)
            elif row["output_type"] == "alternate_item":
                alternates.append(c)
            elif row["output_type"] == "exclusion_item":
                exclusions.append(c)

        # Run AI reviews in sequence
        suggestions = SOP10Agent.suggest_allowances(project_type, scope_narrative)
        alt_flags = SOP10Agent.flag_unusual_alternates(alternates, project_type)
        excl_check = SOP10Agent.validate_exclusions(exclusions, scope_narrative)

        # Save allowance suggestions as a draft output
        cls.save_output(instance_id, "ai_allowance_suggestions",
                        "AI Allowance Suggestions", content=suggestions)
        cls.save_output(instance_id, "ai_alternate_review",
                        "AI Alternate Risk Review", content=alt_flags)
        cls.save_output(instance_id, "ai_exclusion_validation",
                        "AI Exclusion Validation", content=excl_check)

        cur = cls.get_instance(instance_id)
        if cur and cur["status"] != SOPStatus.AI_DRAFTED.value:
            cls.transition_status(instance_id, SOPStatus.AI_DRAFTED, "AI",
                                  "AI review complete")

        total = cls._total_allowance_pool(instance_id)
        requires_buck = total > BUCK_REVIEW_THRESHOLD

        return {
            "allowance_suggestions": suggestions,
            "alternate_flags": alt_flags,
            "exclusion_validation": excl_check,
            "current_allowance_count": len(allowances),
            "current_total_pool": total,
            "requires_buck_review": requires_buck,
        }

    @classmethod
    def pm_approve(cls, instance_id: int, pm_name: str) -> dict:
        """PM confirms all allowances, alternates, and exclusions are complete."""
        total = cls._total_allowance_pool(instance_id)
        requires_buck = total > BUCK_REVIEW_THRESHOLD
        cls.transition_status(instance_id, SOPStatus.INTERNAL_REVIEW, pm_name,
                              "PM reviewing allowances/alternates/exclusions")
        if requires_buck:
            cls.transition_status(instance_id, SOPStatus.APPROVAL_REQUIRED, pm_name,
                                  f"Total allowance pool ${total:,.0f} > ${BUCK_REVIEW_THRESHOLD:,.0f} — Buck review required")
            return {"status": SOPStatus.APPROVAL_REQUIRED.value,
                    "total_allowance_pool": total,
                    "requires_buck_review": True,
                    "next_step": "Buck must call buck_approve() before hand-off to SOP 11."}

        cls.transition_status(instance_id, SOPStatus.APPROVED, pm_name,
                              "PM approved — allowance pool below Buck review threshold")
        return {"status": SOPStatus.APPROVED.value, "total_allowance_pool": total,
                "requires_buck_review": False}

    @classmethod
    def buck_approve(cls, instance_id: int, approver: str = "Buck Adams",
                     conditions: str | None = None) -> dict:
        """Gate 10-C: Buck approves total allowance pool > $50k."""
        total = cls._total_allowance_pool(instance_id)
        ApprovalEngine.create_gate_record(
            sop_instance_id=instance_id,
            gate_id="AG-10-C",
            gate_name="Allowance Pool Authorization",
            required_before_status=SOPStatus.APPROVED.value,
            approver_name=approver,
            approver_role="Principal",
            conditions=conditions,
        )
        cls.transition_status(instance_id, SOPStatus.APPROVED, approver,
                              f"Gate 10-C: Buck approved allowance pool ${total:,.0f}")
        return {"status": SOPStatus.APPROVED.value, "gate": "AG-10-C",
                "total_allowance_pool": total, "approver": approver}

    @classmethod
    def hand_off_to_sop11(cls, instance_id: int, actor: str,
                           project_id: int, owner_name: str,
                           target_issue_date: str, bid_due_date: str) -> dict:
        """Trigger SOP 11 (Bid Package Assembly). Transitions to Handed Off."""
        total = cls._total_allowance_pool(instance_id)
        if total > BUCK_REVIEW_THRESHOLD:
            StopConditionChecker.check_sc04_approval_gate(
                instance_id, "AG-10-C", "Allowance Pool Authorization"
            )
        StopConditionChecker.check_sc07_handoff_destination(instance_id, owner_name)
        cls.transition_status(instance_id, SOPStatus.HANDED_OFF, actor,
                              f"Handed off to SOP 11 — {owner_name}")

        from sop_11_bid_package.sop_11_service import SOP11BidPackageService
        sop11 = SOP11BidPackageService.start_bid_package(
            project_id=project_id,
            owner_name=owner_name,
            target_issue_date=target_issue_date,
            bid_due_date=bid_due_date,
        )
        return {"sop_10_status": SOPStatus.HANDED_OFF.value,
                "sop_11_instance": sop11}

    @classmethod
    def _total_allowance_pool(cls, instance_id: int) -> float:
        rows = db.query("""
            SELECT COALESCE(SUM((content->>'amount')::numeric), 0) AS total
            FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'allowance_item'
        """, (instance_id,))
        return float(rows[0]["total"]) if rows else 0.0

    @classmethod
    def get_full_status(cls, instance_id: int) -> dict:
        instance = cls.get_instance(instance_id)
        if not instance:
            return {"error": "Instance not found"}
        missing = cls.get_missing_inputs(instance_id, REQUIRED_INPUT_KEYS)
        total = cls._total_allowance_pool(instance_id)
        gates = ApprovalEngine.get_gates(instance_id)
        audit = cls.get_audit_trail(instance_id)
        rows = db.query("""
            SELECT output_type, COUNT(*) AS cnt FROM sop_outputs
            WHERE sop_instance_id = %s
            AND output_type IN ('allowance_item', 'alternate_item', 'exclusion_item')
            GROUP BY output_type
        """, (instance_id,))
        counts = {r["output_type"]: r["cnt"] for r in rows}
        return {
            "instance": instance,
            "missing_inputs": [INPUT_LABELS.get(k, k) for k in missing],
            "allowance_count": counts.get("allowance_item", 0),
            "alternate_count": counts.get("alternate_item", 0),
            "exclusion_count": counts.get("exclusion_item", 0),
            "total_allowance_pool": total,
            "requires_buck_review": total > BUCK_REVIEW_THRESHOLD,
            "approval_gates": gates,
            "audit_trail": audit,
        }

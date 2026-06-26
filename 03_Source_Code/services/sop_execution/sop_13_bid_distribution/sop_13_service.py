"""SOP 13 — Bid Distribution: execution service (Layers 1+2)."""
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
from .sop_13_templates import (
    REQUIRED_INPUT_KEYS, INPUT_LABELS, SubDistributionRecord
)
from .sop_13_agent import SOP13Agent


class SOP13BidDistributionService(BaseSOP):
    SOP_NUMBER = "13"

    @classmethod
    def start_distribution(cls, project_id: int, sop_11_instance_id: int,
                           owner_name: str, bid_due_date: str) -> dict:
        """Create SOP 13 instance. Triggered after SOP 11 is Issued."""
        instance = cls.create_instance(
            project_id=project_id,
            owner_name=owner_name,
            owner_role="estimator",
            parent_instance_id=sop_11_instance_id,
            bid_due_date=bid_due_date,
        )
        cls.confirm_input(instance["id"], "sop_11_instance_id", str(sop_11_instance_id))
        cls.confirm_input(instance["id"], "bid_due_date", bid_due_date)
        return {"instance": instance, "status": SOPStatus.NOT_STARTED.value,
                "parent_sop_11": sop_11_instance_id,
                "next_step": "Confirm remaining inputs then log each sub sent via log_sub_sent()."}

    @classmethod
    def log_sub_sent(cls, instance_id: int, sub_name: str, trade_code: str,
                     contact_email: str, method: str, sent_date: str,
                     actor: str = "estimator") -> dict:
        """Record that a bid package was sent to a sub. Auto-advances to In Progress."""
        record = SubDistributionRecord(
            sub_name=sub_name,
            trade_code=trade_code,
            contact_email=contact_email,
            method=method,
            sent_date=sent_date,
        )
        errors = record.validate()
        if errors:
            return {"status": "validation_error", "errors": errors}

        output_id = cls.save_output(
            instance_id, "distribution_record", f"Sent — {sub_name}",
            content=record.to_dict()
        )
        cls._log_event(instance_id, "package_sent", sub_name, actor)

        # Auto-advance from NOT_STARTED to IN_PROGRESS on first send
        current = cls.get_instance(instance_id)
        if current and current["status"] == SOPStatus.NOT_STARTED.value:
            cls.transition_status(instance_id, SOPStatus.IN_PROGRESS, "system",
                                  "Distribution started — first package sent")

        sent_count = cls._count_sent(instance_id)
        return {"output_id": output_id, "sub_name": sub_name,
                "total_sent": sent_count, "method": method}

    @classmethod
    def confirm_receipt(cls, instance_id: int, sub_name: str,
                        confirmed_date: str, actor: str = "estimator") -> dict:
        """Mark that a sub confirmed receipt of the bid package."""
        rows = db.query("""
            SELECT id, content FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'distribution_record'
            AND content->>'sub_name' = %s
        """, (instance_id, sub_name))
        if not rows:
            return {"error": f"No distribution record found for {sub_name}"}

        row = rows[0]
        content = json.loads(row["content"]) if isinstance(row["content"], str) else row["content"]
        content["confirmed_received"] = True
        content["confirmed_date"] = confirmed_date

        db.execute("UPDATE sop_outputs SET content = %s WHERE id = %s",
                   (json.dumps(content), row["id"]))
        cls._log_event(instance_id, "receipt_confirmed", sub_name, actor)

        confirmed_count = cls._count_confirmed(instance_id)
        return {"sub_name": sub_name, "confirmed_date": confirmed_date,
                "total_confirmed": confirmed_count}

    @classmethod
    def run_ai_coverage_check(cls, instance_id: int,
                              required_trades: list[str]) -> dict:
        """AI checks that all required trades have ≥ 3 subs on distribution list."""
        rows = db.query("""
            SELECT content FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'distribution_record'
        """, (instance_id,))
        records = [json.loads(r["content"]) if isinstance(r["content"], str)
                   else r["content"] for r in rows]

        result = SOP13Agent.check_distribution_coverage(records, required_trades)

        cls.save_output(instance_id, "coverage_check", "AI Distribution Coverage Check",
                        content=result)

        current = cls.get_instance(instance_id)
        if current and current["status"] != SOPStatus.AI_DRAFTED.value:
            cls.transition_status(instance_id, SOPStatus.AI_DRAFTED, "AI",
                                  "AI coverage check complete")

        if result.get("gaps"):
            try:
                gap_msgs = [
                    f"{g['trade_code']}: {g['subs_on_list']}/{g['minimum_required']} subs"
                    for g in result["gaps"]
                ]
                StopConditionChecker.check_sc01_inputs(instance_id, gap_msgs)
            except WorkflowBlockedError as e:
                result["stop_condition"] = str(e)
                result["action_required"] = e.resolution_path

        return result

    @classmethod
    def flag_sub_risks(cls, instance_id: int, trade_name: str) -> dict:
        """Run vendor intelligence risk check on current sub list."""
        rows = db.query("""
            SELECT content FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'distribution_record'
        """, (instance_id,))
        sub_list = [json.loads(r["content"]) if isinstance(r["content"], str)
                    else r["content"] for r in rows]
        result = SOP13Agent.flag_sub_risks(sub_list, trade_name)
        cls.save_output(instance_id, "risk_check", "AI Sub Risk Check", content=result)
        return result

    @classmethod
    def pm_confirm_distribution(cls, instance_id: int, pm_name: str) -> dict:
        """PM confirms distribution is complete. Transitions to Approved."""
        cls.transition_status(instance_id, SOPStatus.INTERNAL_REVIEW, pm_name,
                              "PM reviewing distribution completeness")
        cls.transition_status(instance_id, SOPStatus.APPROVED, pm_name,
                              "Distribution confirmed complete by PM")
        return {"status": SOPStatus.APPROVED.value, "confirmed_by": pm_name}

    @classmethod
    def hand_off_to_sop14(cls, instance_id: int, actor: str,
                           project_id: int, owner_name: str,
                           trade_name: str, bid_due_date: str) -> dict:
        """Trigger SOP 14 (Bid Follow-Up). Transitions to Handed Off."""
        StopConditionChecker.check_sc07_handoff_destination(instance_id, owner_name)
        cls.transition_status(instance_id, SOPStatus.HANDED_OFF, actor,
                              f"Handed off to SOP 14 — {owner_name}")

        from sop_14_bid_followup.sop_14_service import SOP14BidFollowUpService
        sop14 = SOP14BidFollowUpService.start_followup(
            project_id=project_id,
            sop_13_instance_id=instance_id,
            owner_name=owner_name,
            trade_name=trade_name,
            bid_due_date=bid_due_date,
        )
        return {"sop_13_status": SOPStatus.HANDED_OFF.value,
                "sop_14_instance": sop14}

    @classmethod
    def _count_sent(cls, instance_id: int) -> int:
        rows = db.query("""
            SELECT COUNT(*) AS cnt FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'distribution_record'
        """, (instance_id,))
        return rows[0]["cnt"] if rows else 0

    @classmethod
    def _count_confirmed(cls, instance_id: int) -> int:
        rows = db.query("""
            SELECT COUNT(*) AS cnt FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'distribution_record'
            AND (content->>'confirmed_received')::boolean = TRUE
        """, (instance_id,))
        return rows[0]["cnt"] if rows else 0

    @classmethod
    def get_full_status(cls, instance_id: int) -> dict:
        instance = cls.get_instance(instance_id)
        if not instance:
            return {"error": "Instance not found"}
        sent_count = cls._count_sent(instance_id)
        confirmed_count = cls._count_confirmed(instance_id)
        gates = ApprovalEngine.get_gates(instance_id)
        audit = cls.get_audit_trail(instance_id)
        return {
            "instance": instance,
            "packages_sent": sent_count,
            "receipts_confirmed": confirmed_count,
            "approval_gates": gates,
            "audit_trail": audit,
        }

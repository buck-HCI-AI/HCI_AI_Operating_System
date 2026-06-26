"""SOP 14 — Bid Follow-Up: execution service (Layers 1+2)."""
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
from .sop_14_templates import (
    REQUIRED_INPUT_KEYS, INPUT_LABELS, SubFollowUpRecord, MIN_RESPONSIVE_SUBS
)
from .sop_14_agent import SOP14Agent


class SOP14BidFollowUpService(BaseSOP):
    SOP_NUMBER = "14"

    @classmethod
    def start_followup(cls, project_id: int, sop_13_instance_id: int,
                       owner_name: str, trade_name: str,
                       bid_due_date: str) -> dict:
        """Create SOP 14 instance. Triggered from SOP 13 handoff."""
        instance = cls.create_instance(
            project_id=project_id,
            owner_name=owner_name,
            owner_role="estimator",
            parent_instance_id=sop_13_instance_id,
            bid_due_date=bid_due_date,
        )
        cls.confirm_input(instance["id"], "sop_13_instance_id", str(sop_13_instance_id))
        cls.confirm_input(instance["id"], "trade_name", trade_name)
        cls.confirm_input(instance["id"], "bid_due_date", bid_due_date)
        cls.transition_status(instance["id"], SOPStatus.IN_PROGRESS, "system",
                              "Follow-up tracking started")
        return {"instance": instance, "status": SOPStatus.IN_PROGRESS.value,
                "parent_sop_13": sop_13_instance_id,
                "next_step": "Log sub list via log_follow_up() and track responses via update_response_status()."}

    @classmethod
    def log_follow_up(cls, instance_id: int, sub_name: str, trade_code: str,
                      contact_email: str, method: str, follow_up_date: str,
                      actor: str = "estimator") -> dict:
        """Record a follow-up contact attempt to a sub."""
        record = SubFollowUpRecord(
            sub_name=sub_name,
            trade_code=trade_code,
            contact_email=contact_email,
            response_status="contacted",
            follow_up_date=follow_up_date,
            follow_up_method=method,
        )
        output_id = cls.save_output(
            instance_id, "follow_up_record", f"Follow-Up — {sub_name}",
            content=record.to_dict()
        )
        cls._log_event(instance_id, "follow_up_logged", sub_name, actor)
        return {"output_id": output_id, "sub_name": sub_name, "method": method,
                "follow_up_date": follow_up_date}

    @classmethod
    def update_response_status(cls, instance_id: int, sub_name: str,
                               response_status: str, response_date: str = "",
                               notes: str = "",
                               actor: str = "estimator") -> dict:
        """Update a sub's bid response status (confirmed, declined, bid_received, etc.)."""
        rows = db.query("""
            SELECT id, content FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'follow_up_record'
            AND content->>'sub_name' = %s
            ORDER BY id DESC LIMIT 1
        """, (instance_id, sub_name))
        if not rows:
            return {"error": f"No follow-up record found for {sub_name}"}

        row = rows[0]
        content = json.loads(row["content"]) if isinstance(row["content"], str) else row["content"]
        content["response_status"] = response_status
        if response_date:
            content["response_date"] = response_date
        if notes:
            content["notes"] = notes

        db.execute("UPDATE sop_outputs SET content = %s WHERE id = %s",
                   (json.dumps(content), row["id"]))
        cls._log_event(instance_id, "response_updated",
                       f"{sub_name}: {response_status}", actor)

        confirmed = cls._count_confirmed(instance_id)
        return {"sub_name": sub_name, "response_status": response_status,
                "total_confirmed": confirmed}

    @classmethod
    def run_ai_summary(cls, instance_id: int, trade_name: str,
                       bid_due_date: str) -> dict:
        """AI summarizes response status and flags minimum bid risk."""
        rows = db.query("""
            SELECT content FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'follow_up_record'
        """, (instance_id,))
        records = [json.loads(r["content"]) if isinstance(r["content"], str)
                   else r["content"] for r in rows]

        summary = SOP14Agent.summarize_response_status(records, trade_name, bid_due_date)

        # Days until close — simplified; bid_due_date expected as ISO date string
        from datetime import date
        try:
            due = date.fromisoformat(bid_due_date)
            days_left = (due - date.today()).days
        except Exception:
            days_left = 7  # default if parse fails

        confirmed_count = summary.get("confirmed_count", 0)
        risk_flag = SOP14Agent.flag_minimum_bid_risk(confirmed_count, days_left, trade_name)
        if risk_flag:
            summary["minimum_bid_risk"] = risk_flag
            if risk_flag["severity"] == "HIGH":
                try:
                    StopConditionChecker.check_sc01_inputs(
                        instance_id,
                        [f"Only {confirmed_count}/{MIN_RESPONSIVE_SUBS} subs confirmed — {days_left} days until close"]
                    )
                except WorkflowBlockedError as e:
                    summary["stop_condition"] = str(e)
                    summary["action_required"] = e.resolution_path

        cls.save_output(instance_id, "follow_up_summary", "AI Follow-Up Summary",
                        content=summary)

        current = cls.get_instance(instance_id)
        if current and current["status"] not in (SOPStatus.AI_DRAFTED.value,
                                                  SOPStatus.INTERNAL_REVIEW.value,
                                                  SOPStatus.APPROVED.value,
                                                  SOPStatus.HANDED_OFF.value):
            cls.transition_status(instance_id, SOPStatus.AI_DRAFTED, "AI",
                                  "AI follow-up summary complete")
        return summary

    @classmethod
    def close_followup(cls, instance_id: int, actor: str) -> dict:
        """PM closes bid follow-up period. Transitions to Approved."""
        confirmed = cls._count_confirmed(instance_id)
        if confirmed < MIN_RESPONSIVE_SUBS:
            # Requires exception if below minimum
            current = cls.get_instance(instance_id)
            return {
                "status": "blocked",
                "message": (
                    f"Only {confirmed}/{MIN_RESPONSIVE_SUBS} subs confirmed. "
                    "Buck must authorize MIN_BIDDERS exception before closing."
                ),
                "confirmed_count": confirmed,
            }
        cls.transition_status(instance_id, SOPStatus.APPROVED, actor,
                              f"Follow-up closed — {confirmed} subs confirmed")
        return {"status": SOPStatus.APPROVED.value, "confirmed_bidders": confirmed,
                "next_step": "Hand off to SOP 15 (Bid Leveling) via hand_off_to_sop15()."}

    @classmethod
    def hand_off_to_sop15(cls, instance_id: int, actor: str,
                           sop_15_instance_id: int | None = None) -> dict:
        """Signal readiness for SOP 15. Transitions to Handed Off."""
        StopConditionChecker.check_sc07_handoff_destination(instance_id, "SOP 15 Bid Leveling")
        cls.transition_status(instance_id, SOPStatus.HANDED_OFF, actor,
                              "Handed off to SOP 15 — bid leveling")
        result: dict = {"sop_14_status": SOPStatus.HANDED_OFF.value}
        if sop_15_instance_id:
            result["sop_15_instance_id"] = sop_15_instance_id
            result["next_step"] = "SOP 15 instance already exists — proceed with bid leveling."
        else:
            result["next_step"] = "Start SOP 15 via SOP15BidLevelingService.start_leveling()."
        return result

    @classmethod
    def _count_confirmed(cls, instance_id: int) -> int:
        rows = db.query("""
            SELECT COUNT(*) AS cnt FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'follow_up_record'
            AND content->>'response_status' IN ('confirmed', 'bid_received')
        """, (instance_id,))
        return rows[0]["cnt"] if rows else 0

    @classmethod
    def get_full_status(cls, instance_id: int) -> dict:
        instance = cls.get_instance(instance_id)
        if not instance:
            return {"error": "Instance not found"}
        confirmed = cls._count_confirmed(instance_id)
        rows = db.query("""
            SELECT COUNT(*) AS cnt FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'follow_up_record'
        """, (instance_id,))
        total_subs = rows[0]["cnt"] if rows else 0
        gates = ApprovalEngine.get_gates(instance_id)
        audit = cls.get_audit_trail(instance_id)
        return {
            "instance": instance,
            "total_subs_tracked": total_subs,
            "confirmed_bidders": confirmed,
            "minimum_required": MIN_RESPONSIVE_SUBS,
            "approval_gates": gates,
            "audit_trail": audit,
        }

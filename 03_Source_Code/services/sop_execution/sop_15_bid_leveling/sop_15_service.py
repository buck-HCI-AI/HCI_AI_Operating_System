"""SOP 15 — Bid Leveling: execution service (Layers 1+2)."""
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
from .sop_15_templates import (
    BidRecord, BidAdjustment, LevelingOutput, MIN_RESPONSIVE_BIDS
)
from .sop_15_agent import SOP15Agent


class SOP15BidLevelingService(BaseSOP):
    SOP_NUMBER = "15"

    # ── Layer 1 + Layer 2 Methods ──────────────────────────────────────────────

    @classmethod
    def start_leveling(cls, project_id: int, sop_11_instance_id: int,
                       owner_name: str) -> dict:
        """Create SOP 15 instance. Triggered at bid close from SOP 11 handoff."""
        instance = cls.create_instance(
            project_id=project_id,
            owner_name=owner_name,
            owner_role="estimator",
            parent_instance_id=sop_11_instance_id,
        )
        return {"instance": instance, "status": SOPStatus.NOT_STARTED.value,
                "parent_sop_11": sop_11_instance_id,
                "next_step": "Log all received bids via log_bid()."}

    @classmethod
    def log_bid(cls, instance_id: int, bidder_name: str, bid_amount: float,
                received_date: str, bid_text: str = "", responsive: bool = True,
                scope_summary: str = "", estimator_name: str = "") -> dict:
        """Log a received bid and run AI extraction on the bid text."""
        record: dict = {
            "bidder_name": bidder_name,
            "bid_amount_base": bid_amount,
            "bid_received_date": received_date,
            "bid_responsive": responsive,
        }

        if bid_text:
            ai_extraction = SOP15Agent.analyze_bid(bid_text, scope_summary, bidder_name)
            record.update({
                "exclusions_list": ai_extraction.get("exclusions_list", []),
                "contract_qualifications": ai_extraction.get("contract_qualifications", []),
                "schedule_exceptions": ai_extraction.get("schedule_exceptions", []),
                "risk_flags": ai_extraction.get("risk_flags", []),
                "qualifications_parsed": ai_extraction,
            })

        output_id = cls.save_output(
            instance_id, "bid_record", f"Bid — {bidder_name}",
            content=record
        )
        cls._log_event(instance_id, "bid_logged", bidder_name, estimator_name)

        # Auto-transition based on bid count
        bid_count = cls._count_responsive_bids(instance_id)
        current = cls.get_instance(instance_id)
        current_status = current["status"] if current else None

        if bid_count >= MIN_RESPONSIVE_BIDS:
            if current_status in (SOPStatus.NOT_STARTED.value, SOPStatus.INPUTS_MISSING.value):
                cls.transition_status(instance_id, SOPStatus.READY_TO_START,
                                      "system", f"Minimum {MIN_RESPONSIVE_BIDS} responsive bids received")
        elif bid_count > 0 and current_status == SOPStatus.NOT_STARTED.value:
            cls.transition_status(instance_id, SOPStatus.INPUTS_MISSING,
                                  "system", f"{bid_count}/{MIN_RESPONSIVE_BIDS} responsive bids — minimum not yet met")

        return {"output_id": output_id, "bidder": bidder_name,
                "responsive_bid_count": bid_count,
                "status": current_status if bid_count < MIN_RESPONSIVE_BIDS else SOPStatus.READY_TO_START.value}

    @classmethod
    def add_bid_adjustment(cls, instance_id: int, bidder_name: str,
                           description: str, amount: float, reason: str,
                           is_estimate: bool = False,
                           estimator_name: str = "") -> dict:
        """Add an adjustment to normalize a specific bid to common scope basis."""
        rows = db.query("""
            SELECT id, content FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'bid_record'
            AND content->>'bidder_name' = %s
        """, (instance_id, bidder_name))
        if not rows:
            return {"error": f"Bid from {bidder_name} not found"}

        row = rows[0]
        content = json.loads(row["content"]) if isinstance(row["content"], str) else row["content"]
        adjustments = content.get("adjustment_items", [])
        adjustments.append({
            "description": description,
            "amount": amount,
            "reason": reason,
            "is_estimate": is_estimate,
        })
        content["adjustment_items"] = adjustments
        content["bid_amount_adjusted"] = content["bid_amount_base"] + sum(
            a["amount"] for a in adjustments
        )

        db.execute("""
            UPDATE sop_outputs SET content = %s WHERE id = %s
        """, (json.dumps(content), row["id"]))

        cls._log_event(instance_id, "adjustment_added",
                       f"{bidder_name}: {description} ${amount:+,.0f}", estimator_name)
        return {"bidder": bidder_name, "adjustment": description, "amount": amount}

    @classmethod
    def run_ai_leveling(cls, instance_id: int, trade_name: str,
                        scope_summary: str = "") -> dict:
        """Layer 3: AI produces normalized comparison and recommendation."""
        # Auto-advance to In Progress if still at Ready to Start
        current = cls.get_instance(instance_id)
        if current and current["status"] == SOPStatus.READY_TO_START.value:
            cls.transition_status(instance_id, SOPStatus.IN_PROGRESS,
                                  "system", "Work started — AI leveling in progress")

        bid_rows = db.query("""
            SELECT content FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'bid_record'
        """, (instance_id,))

        bids = [json.loads(r["content"]) if isinstance(r["content"], str)
                else r["content"] for r in bid_rows]
        responsive = [b for b in bids if b.get("bid_responsive", True)]

        if len(responsive) < MIN_RESPONSIVE_BIDS:
            insufficient = SOP15Agent.inputs_insufficient_report(
                len(responsive), MIN_RESPONSIVE_BIDS
            )
            StopConditionChecker.check_sc01_inputs(
                instance_id,
                [f"Minimum {MIN_RESPONSIVE_BIDS} responsive bids required; only {len(responsive)} received"]
            )
            return insufficient

        low = min(b.get("bid_amount_adjusted", b["bid_amount_base"]) for b in responsive) or 1
        comparison_table = sorted([
            {
                "bidder": b["bidder_name"],
                "base_bid": b["bid_amount_base"],
                "adjusted_total": b.get("bid_amount_adjusted", b["bid_amount_base"]),
                "vs_low": round(b.get("bid_amount_adjusted", b["bid_amount_base"]) - low, 2),
                "pct_over_low": round(
                    (b.get("bid_amount_adjusted", b["bid_amount_base"]) - low) / low * 100, 1),
                "risk_level": "HIGH" if any(f.get("severity") == "HIGH"
                                            for f in b.get("risk_flags", [])) else "LOW",
                "perf_score": b.get("prior_performance_score"),
                "rec_flag": b.get("recommendation_flag", "pending"),
            }
            for b in responsive
        ], key=lambda x: x["adjusted_total"])

        recommendation = SOP15Agent.generate_leveling_recommendation(
            instance_id, comparison_table, trade_name, scope_summary
        )

        cls.save_output(instance_id, "leveling_recommendation",
                        "AI Leveling Recommendation", content={
                            "comparison_table": comparison_table,
                            "recommendation": recommendation,
                        })

        cur = cls.get_instance(instance_id)
        if cur and cur["status"] != SOPStatus.AI_DRAFTED.value:
            cls.transition_status(instance_id, SOPStatus.AI_DRAFTED, "AI",
                                  "AI leveling complete")
        return {
            "comparison_table": comparison_table,
            "recommendation": recommendation,
            "responsive_bid_count": len(responsive),
        }

    @classmethod
    def submit_for_pm_review(cls, instance_id: int, estimator_name: str) -> dict:
        cls.transition_status(instance_id, SOPStatus.INTERNAL_REVIEW,
                              estimator_name, "Submitted for PM review")
        return {"status": SOPStatus.INTERNAL_REVIEW.value}

    @classmethod
    def pm_approve_leveling(cls, instance_id: int, pm_name: str) -> dict:
        """PM confirms all risk flags dispositioned; routes to Buck."""
        # SC-03: check no HIGH risks are open
        risk_rows = db.query("""
            SELECT content FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'bid_record'
        """, (instance_id,))
        high_risks = []
        for row in risk_rows:
            content = json.loads(row["content"]) if isinstance(row["content"], str) else row["content"]
            for flag in content.get("risk_flags", []):
                if flag.get("severity") == "HIGH" and not flag.get("dispositioned"):
                    high_risks.append(flag)

        if high_risks:
            StopConditionChecker.check_sc03_risk_flags(instance_id, high_risks)

        cls.transition_status(instance_id, SOPStatus.APPROVAL_REQUIRED, pm_name,
                              "Leveling complete — routed to Buck for award")
        return {"status": SOPStatus.APPROVAL_REQUIRED.value,
                "next_step": "Buck reviews leveling sheet and calls record_buck_award()."}

    @classmethod
    def record_buck_award(cls, instance_id: int, awarded_sub: str,
                          award_amount: float, scope_basis: str,
                          rationale: str, risks_accepted: str = "",
                          conditions: str = "",
                          approver: str = "Buck Adams") -> dict:
        """Gate 15-C: Buck awards. Creates approval gate + decision record."""
        ApprovalEngine.create_gate_record(
            sop_instance_id=instance_id,
            gate_id="AG-15-C",
            gate_name="Award Decision Authority",
            required_before_status=SOPStatus.APPROVED.value,
            approver_name=approver,
            approver_role="Principal",
            conditions=conditions or None,
        )

        award_record = {
            "awarded_sub": awarded_sub,
            "award_amount": award_amount,
            "scope_basis": scope_basis,
            "rationale": rationale,
            "risks_accepted": risks_accepted,
            "conditions": conditions,
            "decided_by": approver,
        }
        cls.save_output(instance_id, "award_decision", "Buck Award Decision",
                        content=award_record)

        db.execute("""
            UPDATE sop_instances
            SET awarded_sub = %s, award_amount = %s
            WHERE id = %s
        """, (awarded_sub, award_amount, instance_id))

        cls.transition_status(instance_id, SOPStatus.APPROVED, approver,
                              f"Gate 15-C: Awarded to {awarded_sub} at ${award_amount:,.0f}")

        row = db.query_one("SELECT project_id FROM sop_instances WHERE id = %s",
                           (instance_id,))
        pid = row["project_id"] if row else None
        SOPKPITracker.record_kpi(instance_id, "SOP15_AWARD_AMOUNT", award_amount,
                                 "$", pid)

        return {"status": SOPStatus.APPROVED.value, "awarded_to": awarded_sub,
                "amount": award_amount, "gate": "AG-15-C"}

    @classmethod
    def hand_off_to_sop16(cls, instance_id: int, actor: str,
                           recipient_pm: str) -> dict:
        """Trigger SOP 16 (Buyout) handoff."""
        StopConditionChecker.check_sc04_approval_gate(
            instance_id, "AG-15-C", "Award Decision Authority"
        )
        StopConditionChecker.check_sc07_handoff_destination(instance_id, recipient_pm)
        cls.transition_status(instance_id, SOPStatus.HANDED_OFF, actor,
                              f"Handed off to SOP 16 — {recipient_pm}")
        return {"status": SOPStatus.HANDED_OFF.value,
                "next_step": "Initiate SOP 16 (Buyout) and SOP 19 (Subcontract Agreement)."}

    @classmethod
    def _count_responsive_bids(cls, instance_id: int) -> int:
        rows = db.query("""
            SELECT COUNT(*) AS cnt FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'bid_record'
            AND (content->>'bid_responsive')::boolean = TRUE
        """, (instance_id,))
        return rows[0]["cnt"] if rows else 0

    @classmethod
    def get_full_status(cls, instance_id: int) -> dict:
        instance = cls.get_instance(instance_id)
        if not instance:
            return {"error": "Instance not found"}
        bid_count = cls._count_responsive_bids(instance_id)
        gates = ApprovalEngine.get_gates(instance_id)
        audit = cls.get_audit_trail(instance_id)
        return {
            "instance": instance,
            "responsive_bid_count": bid_count,
            "minimum_required": MIN_RESPONSIVE_BIDS,
            "approval_gates": gates,
            "audit_trail": audit,
        }

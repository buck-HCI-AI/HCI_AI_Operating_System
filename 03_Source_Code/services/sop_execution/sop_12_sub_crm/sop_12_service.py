"""SOP 12 — Subcontractor CRM: execution service (Layers 1+2)."""
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
from .sop_12_templates import (
    REQUIRED_INPUT_KEYS, INPUT_LABELS, MIN_QUALIFIED_SUBS, SubCandidateRecord
)
from .sop_12_agent import SOP12Agent


class SOP12SubCRMService(BaseSOP):
    SOP_NUMBER = "12"

    @classmethod
    def start_bid_list(cls, project_id: int, trade_code: str,
                       trade_name: str, sop_11_instance_id: int,
                       owner_name: str) -> dict:
        """Create a SOP 12 instance — builds the qualified sub list for a trade."""
        instance = cls.create_instance(
            project_id=project_id,
            owner_name=owner_name,
            owner_role="estimator",
            parent_instance_id=sop_11_instance_id,
        )
        cls.confirm_input(instance["id"], "trade_code", trade_code)
        cls.confirm_input(instance["id"], "trade_name", trade_name)
        cls.confirm_input(instance["id"], "sop_11_instance_id", str(sop_11_instance_id))
        cls.transition_status(instance["id"], SOPStatus.IN_PROGRESS, owner_name,
                              f"Sub CRM started — building bid list for {trade_name}")
        return {"instance": instance, "status": SOPStatus.IN_PROGRESS.value,
                "trade_name": trade_name, "trade_code": trade_code,
                "next_step": "Add sub candidates via add_sub_candidate() or run_ai_research() to auto-populate from vendor intelligence."}

    @classmethod
    def add_sub_candidate(cls, instance_id: int, sub_data: dict,
                          actor: str = "estimator") -> dict:
        """Manually add a sub candidate to the bid list."""
        record = SubCandidateRecord(
            sub_name=sub_data.get("sub_name", ""),
            trade_code=sub_data.get("trade_code", ""),
            contact_name=sub_data.get("contact_name", ""),
            contact_email=sub_data.get("contact_email", ""),
            contact_phone=sub_data.get("contact_phone", ""),
            license_number=sub_data.get("license_number", ""),
            bonded=sub_data.get("bonded", False),
            insured=sub_data.get("insured", False),
            prequalified=sub_data.get("prequalified", False),
            performance_rating=sub_data.get("performance_rating", "QUALIFIED"),
            last_hci_project=sub_data.get("last_hci_project", ""),
            notes=sub_data.get("notes", ""),
        )
        errors = record.validate()
        if errors:
            return {"status": "validation_error", "errors": errors}

        output_id = cls.save_output(
            instance_id, "sub_candidate", f"Sub — {record.sub_name}",
            content=record.to_dict()
        )
        cls._log_event(instance_id, "sub_added", record.sub_name, actor)
        qualified_count = cls._count_qualified(instance_id)
        return {"output_id": output_id, "sub_name": record.sub_name,
                "qualified_count": qualified_count,
                "meets_minimum": qualified_count >= MIN_QUALIFIED_SUBS}

    @classmethod
    def run_ai_research(cls, instance_id: int, project_type: str = "") -> dict:
        """Layer 3: AI searches vendor intelligence and recommends subs for the trade."""
        inp_rows = db.query("""
            SELECT input_key, confirmed_by FROM sop_inputs WHERE sop_instance_id = %s
        """, (instance_id,))
        inputs = {r["input_key"]: r["confirmed_by"] for r in inp_rows}
        trade_code = inputs.get("trade_code", "")
        trade_name = inputs.get("trade_name", "")

        result = SOP12Agent.research_sub_candidates(trade_code, trade_name, project_type)

        # Auto-add AI-recommended candidates that aren't already on the list
        for candidate in result.get("raw_candidates", []):
            existing = db.query("""
                SELECT id FROM sop_outputs
                WHERE sop_instance_id = %s AND output_type = 'sub_candidate'
                AND content->>'sub_name' = %s
            """, (instance_id, candidate["sub_name"]))
            if not existing:
                record = SubCandidateRecord(
                    sub_name=candidate["sub_name"],
                    trade_code=trade_code,
                    contact_email=candidate.get("contact_email", ""),
                    performance_rating=candidate.get("performance_rating", "QUALIFIED"),
                    last_hci_project=candidate.get("last_hci_project", ""),
                    ai_risk_flag=candidate.get("ai_risk_flag", ""),
                    notes=candidate.get("notes", ""),
                )
                cls.save_output(instance_id, "sub_candidate",
                                f"Sub — {record.sub_name}", content=record.to_dict())

        cls.save_output(instance_id, "ai_research", "AI Sub Research",
                        content=result)

        cur = cls.get_instance(instance_id)
        if cur and cur["status"] == SOPStatus.IN_PROGRESS.value:
            cls.transition_status(instance_id, SOPStatus.AI_DRAFTED, "AI",
                                  "AI sub research complete")

        result["qualified_count"] = cls._count_qualified(instance_id)
        return result

    @classmethod
    def assess_sub(cls, instance_id: int, sub_name: str) -> dict:
        """AI qualification assessment for a specific sub."""
        rows = db.query("""
            SELECT content FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'sub_candidate'
            AND content->>'sub_name' = %s LIMIT 1
        """, (instance_id, sub_name))
        if not rows:
            return {"error": f"Sub {sub_name} not found in candidate list"}

        content = json.loads(rows[0]["content"]) if isinstance(rows[0]["content"], str) else rows[0]["content"]
        result = SOP12Agent.assess_sub_qualification(
            sub_name=sub_name,
            trade_code=content.get("trade_code", ""),
            bonded=content.get("bonded", False),
            insured=content.get("insured", False),
            license_number=content.get("license_number", ""),
        )

        # Update the record with AI assessment
        content["ai_risk_flag"] = result.get("risk_flag", "")
        content["performance_rating"] = result.get("recommended_rating", content.get("performance_rating", "QUALIFIED"))
        db.execute("UPDATE sop_outputs SET content = %s WHERE sop_instance_id = %s AND output_type = 'sub_candidate' AND content->>'sub_name' = %s",
                   (json.dumps(content), instance_id, sub_name))
        return result

    @classmethod
    def pm_approve_sub(cls, instance_id: int, sub_name: str,
                       pm_name: str) -> dict:
        """PM approves a sub candidate for inclusion on the bid list."""
        rows = db.query("""
            SELECT id, content FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'sub_candidate'
            AND content->>'sub_name' = %s LIMIT 1
        """, (instance_id, sub_name))
        if not rows:
            return {"error": f"Sub {sub_name} not found"}

        row = rows[0]
        content = json.loads(row["content"]) if isinstance(row["content"], str) else row["content"]
        content["pm_approved"] = True
        db.execute("UPDATE sop_outputs SET content = %s WHERE id = %s",
                   (json.dumps(content), row["id"]))
        cls._log_event(instance_id, "sub_approved", sub_name, pm_name)

        qualified_count = cls._count_qualified(instance_id)
        return {"sub_name": sub_name, "approved": True,
                "qualified_count": qualified_count,
                "meets_minimum": qualified_count >= MIN_QUALIFIED_SUBS}

    @classmethod
    def pm_approve_list(cls, instance_id: int, pm_name: str) -> dict:
        """PM finalizes and approves the complete bid list. Enforces MIN_BIDDERS."""
        qualified_count = cls._count_qualified(instance_id)
        if qualified_count < MIN_QUALIFIED_SUBS:
            try:
                StopConditionChecker.check_sc01_inputs(
                    instance_id,
                    [f"Only {qualified_count}/{MIN_QUALIFIED_SUBS} PM-approved subs — MIN_BIDDERS rule requires {MIN_QUALIFIED_SUBS}"]
                )
            except WorkflowBlockedError as e:
                return {"status": "blocked", "message": str(e),
                        "qualified_count": qualified_count}

        # AI quality check
        rows = db.query("""
            SELECT content FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'sub_candidate'
            AND (content->>'pm_approved')::boolean = TRUE
        """, (instance_id,))
        approved_subs = [
            json.loads(r["content"]) if isinstance(r["content"], str) else r["content"]
            for r in rows
        ]
        quality = SOP12Agent.assess_bid_list_quality(approved_subs, "")
        cls.save_output(instance_id, "bid_list_quality", "AI Bid List Quality Check",
                        content=quality)

        cls.transition_status(instance_id, SOPStatus.INTERNAL_REVIEW, pm_name,
                              "PM reviewing final bid list")
        cls.transition_status(instance_id, SOPStatus.APPROVED, pm_name,
                              f"Bid list approved — {qualified_count} subs confirmed")
        return {"status": SOPStatus.APPROVED.value, "qualified_count": qualified_count,
                "quality_check": quality}

    @classmethod
    def hand_off_to_sop13(cls, instance_id: int, actor: str,
                           project_id: int, owner_name: str,
                           bid_due_date: str, sop_11_instance_id: int) -> dict:
        """Build approved sub list and trigger SOP 13 Distribution."""
        StopConditionChecker.check_sc07_handoff_destination(instance_id, owner_name)
        cls.transition_status(instance_id, SOPStatus.HANDED_OFF, actor,
                              f"Handed off to SOP 13 — {owner_name}")

        from sop_13_bid_distribution.sop_13_service import SOP13BidDistributionService
        sop13 = SOP13BidDistributionService.start_distribution(
            project_id=project_id,
            sop_11_instance_id=sop_11_instance_id,
            owner_name=owner_name,
            bid_due_date=bid_due_date,
        )
        return {"sop_12_status": SOPStatus.HANDED_OFF.value, "sop_13_instance": sop13}

    @classmethod
    def _count_qualified(cls, instance_id: int) -> int:
        rows = db.query("""
            SELECT COUNT(*) AS cnt FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'sub_candidate'
            AND (content->>'pm_approved')::boolean = TRUE
            AND content->>'performance_rating' != 'DO_NOT_USE'
        """, (instance_id,))
        return rows[0]["cnt"] if rows else 0

    @classmethod
    def get_full_status(cls, instance_id: int) -> dict:
        instance = cls.get_instance(instance_id)
        if not instance:
            return {"error": "Instance not found"}
        qualified_count = cls._count_qualified(instance_id)
        rows = db.query("""
            SELECT COUNT(*) AS cnt FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'sub_candidate'
        """, (instance_id,))
        total_candidates = rows[0]["cnt"] if rows else 0
        return {
            "instance": instance,
            "total_candidates": total_candidates,
            "qualified_count": qualified_count,
            "minimum_required": MIN_QUALIFIED_SUBS,
            "meets_minimum": qualified_count >= MIN_QUALIFIED_SUBS,
            "audit_trail": cls.get_audit_trail(instance_id),
        }

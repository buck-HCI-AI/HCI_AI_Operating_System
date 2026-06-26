"""SOP 06 — Missing Information / Risk Log: execution service (Layers 1+2)."""
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
from .sop_06_templates import REQUIRED_INPUT_KEYS, INPUT_LABELS, MissingInfoItem, RiskItem
from .sop_06_agent import SOP06Agent


class SOP06MissingInfoService(BaseSOP):
    SOP_NUMBER = "06"

    @classmethod
    def start_risk_log(cls, project_id: int, sop_05_instance_id: int,
                       owner_name: str) -> dict:
        """Create SOP 06 instance. Triggered from SOP 05 handoff."""
        instance = cls.create_instance(
            project_id=project_id,
            owner_name=owner_name,
            owner_role="pm",
            parent_instance_id=sop_05_instance_id,
        )
        cls.confirm_input(instance["id"], "sop_05_instance_id", str(sop_05_instance_id))
        cls.transition_status(instance["id"], SOPStatus.IN_PROGRESS, owner_name,
                              "Missing info / risk log started")
        return {"instance": instance, "status": SOPStatus.IN_PROGRESS.value,
                "parent_sop_05": sop_05_instance_id,
                "next_step": "Add missing info via add_missing_info() and risks via add_risk(). "
                             "Run run_ai_gap_check() to auto-populate from SOP 04/05 findings."}

    @classmethod
    def add_missing_info(cls, instance_id: int, item_data: dict,
                         actor: str = "pm") -> dict:
        """Log a missing information item."""
        item = MissingInfoItem(
            item_code=item_data.get("item_code", ""),
            description=item_data.get("description", ""),
            source=item_data.get("source", ""),
            responsible_party=item_data.get("responsible_party", ""),
            due_date=item_data.get("due_date", ""),
            priority=item_data.get("priority", "MEDIUM"),
        )
        errors = item.validate()
        if errors:
            return {"status": "validation_error", "errors": errors}

        output_id = cls.save_output(
            instance_id, "missing_info_item", f"Missing Info — {item.item_code}",
            content=item.to_dict()
        )
        cls._log_event(instance_id, "missing_info_added", item.item_code, actor)
        critical_count = cls._count_critical_open(instance_id)
        return {"output_id": output_id, "item_code": item.item_code,
                "priority": item.priority, "open_critical_count": critical_count}

    @classmethod
    def add_risk(cls, instance_id: int, risk_data: dict,
                 actor: str = "pm") -> dict:
        """Log a project risk."""
        risk = RiskItem(
            risk_code=risk_data.get("risk_code", ""),
            description=risk_data.get("description", ""),
            probability=risk_data.get("probability", "MEDIUM"),
            impact=risk_data.get("impact", "MEDIUM"),
            mitigation=risk_data.get("mitigation", ""),
            owner=risk_data.get("owner", "PM"),
            ai_flagged=risk_data.get("ai_flagged", False),
        )
        if not risk.risk_code or not risk.description:
            return {"status": "validation_error",
                    "errors": ["risk_code and description are required"]}

        output_id = cls.save_output(
            instance_id, "risk_item", f"Risk — {risk.risk_code}",
            content=risk.to_dict()
        )
        cls._log_event(instance_id, "risk_added", risk.risk_code, actor)
        return {"output_id": output_id, "risk_code": risk.risk_code,
                "risk_score": risk.calculate_score()}

    @classmethod
    def resolve_item(cls, instance_id: int, item_code: str,
                     resolution_note: str, actor: str = "pm") -> dict:
        """Mark a missing info item as resolved."""
        rows = db.query("""
            SELECT id, content FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'missing_info_item'
            AND content->>'item_code' = %s
        """, (instance_id, item_code))
        if not rows:
            return {"error": f"Item {item_code} not found"}

        row = rows[0]
        content = json.loads(row["content"]) if isinstance(row["content"], str) else row["content"]
        content["resolved"] = True
        content["resolution_note"] = resolution_note
        db.execute("UPDATE sop_outputs SET content = %s WHERE id = %s",
                   (json.dumps(content), row["id"]))
        cls._log_event(instance_id, "item_resolved", item_code, actor)
        return {"item_code": item_code, "resolved": True,
                "open_critical_count": cls._count_critical_open(instance_id)}

    @classmethod
    def run_ai_gap_check(cls, instance_id: int) -> dict:
        """AI pulls gaps from SOP 04/05 and identifies missing info and risks."""
        # Get project context
        inp_rows = db.query("""
            SELECT input_key, confirmed_by FROM sop_inputs
            WHERE sop_instance_id = %s
        """, (instance_id,))
        inputs = {r["input_key"]: r["confirmed_by"] for r in inp_rows}
        sop05_id = inputs.get("sop_05_instance_id")

        plan_review_gaps = []
        narrative_sections = []
        scope_summary = ""

        if sop05_id:
            # Get SOP 05's parent (SOP 04) instance
            sop05_inst = db.query_one(
                "SELECT parent_instance_id FROM sop_instances WHERE id = %s",
                (int(sop05_id),)
            )
            sop04_id = sop05_inst["parent_instance_id"] if sop05_inst else None

            if sop04_id:
                rows = db.query("""
                    SELECT content FROM sop_outputs
                    WHERE sop_instance_id = %s AND output_type = 'plan_section'
                """, (sop04_id,))
                for row in rows:
                    c = json.loads(row["content"]) if isinstance(row["content"], str) else row["content"]
                    plan_review_gaps.extend(c.get("gaps_found", []))

            # Get narrative sections
            rows = db.query("""
                SELECT content FROM sop_outputs
                WHERE sop_instance_id = %s AND output_type = 'narrative_section'
            """, (int(sop05_id),))
            narrative_sections = [
                json.loads(r["content"]) if isinstance(r["content"], str) else r["content"]
                for r in rows
            ]
            scope_summary = ", ".join(s.get("trade_name", "") for s in narrative_sections[:5])

        # Get project type
        inp_rows2 = db.query("""
            SELECT confirmed_by FROM sop_inputs
            WHERE sop_instance_id = %s AND input_key = 'project_type'
            LIMIT 1
        """, (instance_id,))
        project_type = inp_rows2[0]["confirmed_by"] if inp_rows2 else "commercial"

        gap_result = SOP06Agent.identify_gaps_from_review(
            plan_review_gaps, narrative_sections, project_type
        )
        risk_result = SOP06Agent.flag_project_risks(
            project_type, scope_summary,
            len(gap_result.get("missing_items", [])), plan_review_gaps
        )

        # Auto-create missing info items from AI findings
        for item in gap_result.get("missing_items", []):
            existing = db.query("""
                SELECT id FROM sop_outputs
                WHERE sop_instance_id = %s AND output_type = 'missing_info_item'
                AND content->>'item_code' = %s
            """, (instance_id, item.get("item_code", "")))
            if not existing:
                cls.add_missing_info(instance_id, {
                    "item_code": item.get("item_code", "MI-AI"),
                    "description": item.get("description", ""),
                    "source": item.get("source", "AI"),
                    "responsible_party": item.get("responsible_party", "PM"),
                    "priority": item.get("priority", "MEDIUM"),
                }, actor="AI")

        # Auto-create risks from AI findings
        for risk in risk_result.get("risks", []):
            existing = db.query("""
                SELECT id FROM sop_outputs
                WHERE sop_instance_id = %s AND output_type = 'risk_item'
                AND content->>'risk_code' = %s
            """, (instance_id, risk.get("risk_code", "")))
            if not existing:
                cls.add_risk(instance_id, {
                    "risk_code": risk.get("risk_code", "R-AI"),
                    "description": risk.get("description", ""),
                    "probability": risk.get("probability", "MEDIUM"),
                    "impact": risk.get("impact", "MEDIUM"),
                    "mitigation": risk.get("mitigation", ""),
                    "owner": risk.get("owner", "PM"),
                    "ai_flagged": True,
                }, actor="AI")

        cls.save_output(instance_id, "ai_gap_analysis", "AI Gap Analysis",
                        content={"gaps": gap_result, "risks": risk_result})

        cur = cls.get_instance(instance_id)
        if cur and cur["status"] == SOPStatus.IN_PROGRESS.value:
            cls.transition_status(instance_id, SOPStatus.AI_DRAFTED, "AI",
                                  "AI gap and risk analysis complete")

        return {"gap_analysis": gap_result, "risk_analysis": risk_result,
                "open_critical_count": cls._count_critical_open(instance_id)}

    @classmethod
    def close_log(cls, instance_id: int, actor: str) -> dict:
        """Close the missing info log. SC-01 enforced if CRITICAL items remain."""
        critical = cls._count_critical_open(instance_id)
        if critical > 0:
            try:
                StopConditionChecker.check_sc01_inputs(
                    instance_id,
                    [f"{critical} CRITICAL missing info item(s) not yet resolved"]
                )
            except WorkflowBlockedError as e:
                return {"status": "blocked", "message": str(e),
                        "open_critical": critical}

        cls.transition_status(instance_id, SOPStatus.APPROVED, actor,
                              "Missing info log closed — all critical items resolved")
        return {"status": SOPStatus.APPROVED.value,
                "next_step": "Hand off to SOP 07 (ROM Budget) via hand_off_to_sop07()."}

    @classmethod
    def hand_off_to_sop07(cls, instance_id: int, actor: str,
                           project_id: int, owner_name: str,
                           project_type: str, gross_sf: float,
                           sop_05_instance_id: int) -> dict:
        """Trigger SOP 07 (ROM Budget). Transitions to Handed Off."""
        StopConditionChecker.check_sc07_handoff_destination(instance_id, owner_name)
        cls.transition_status(instance_id, SOPStatus.HANDED_OFF, actor,
                              f"Handed off to SOP 07 — {owner_name}")

        from sop_07_rom_budget.sop_07_service import SOP07ROMBudgetService
        sop07 = SOP07ROMBudgetService.start_rom(
            project_id=project_id,
            owner_name=owner_name,
            project_type=project_type,
            gross_sf=gross_sf,
            sop_05_instance_id=sop_05_instance_id,
            sop_06_instance_id=instance_id,
        )
        return {"sop_06_status": SOPStatus.HANDED_OFF.value, "sop_07_instance": sop07}

    @classmethod
    def _count_critical_open(cls, instance_id: int) -> int:
        rows = db.query("""
            SELECT COUNT(*) AS cnt FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'missing_info_item'
            AND content->>'priority' = 'CRITICAL'
            AND (content->>'resolved')::boolean IS NOT TRUE
        """, (instance_id,))
        return rows[0]["cnt"] if rows else 0

    @classmethod
    def get_full_status(cls, instance_id: int) -> dict:
        instance = cls.get_instance(instance_id)
        if not instance:
            return {"error": "Instance not found"}
        rows = db.query("""
            SELECT output_type, COUNT(*) AS cnt FROM sop_outputs
            WHERE sop_instance_id = %s
            AND output_type IN ('missing_info_item', 'risk_item')
            GROUP BY output_type
        """, (instance_id,))
        counts = {r["output_type"]: r["cnt"] for r in rows}
        return {
            "instance": instance,
            "missing_info_count": counts.get("missing_info_item", 0),
            "risk_count": counts.get("risk_item", 0),
            "open_critical_count": cls._count_critical_open(instance_id),
            "audit_trail": cls.get_audit_trail(instance_id),
        }

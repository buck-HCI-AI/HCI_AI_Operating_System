"""SOP 17 — Project Schedule: execution service (Layers 1+2)."""
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
from .sop_17_templates import REQUIRED_INPUT_KEYS, INPUT_LABELS, ScheduleMilestone
from .sop_17_agent import SOP17Agent


class SOP17ProjectScheduleService(BaseSOP):
    SOP_NUMBER = "17"

    @classmethod
    def start_schedule(cls, project_id: int, project_name: str, project_type: str,
                        construction_start: str, substantial_completion: str,
                        owner_name: str, sop_23_instance_id: int = 0) -> dict:
        instance = cls.create_instance(project_id=project_id, owner_name=owner_name, owner_role="pm",
                                        parent_instance_id=sop_23_instance_id or None)
        iid = instance["id"]
        cls.confirm_input(iid, "project_name", project_name)
        cls.confirm_input(iid, "project_type", project_type)
        cls.confirm_input(iid, "construction_start", construction_start)
        cls.confirm_input(iid, "substantial_completion", substantial_completion)
        if sop_23_instance_id:
            cls.confirm_input(iid, "sop_23_instance_id", str(sop_23_instance_id))
        cls.transition_status(iid, SOPStatus.IN_PROGRESS, owner_name, "Schedule started")
        return {"instance": instance, "status": SOPStatus.IN_PROGRESS.value,
                "next_step": "Run AI schedule generation via run_ai_schedule() or add milestones manually."}

    @classmethod
    def run_ai_schedule(cls, instance_id: int) -> dict:
        rows = db.query("SELECT input_key, confirmed_by FROM sop_inputs WHERE sop_instance_id = %s", (instance_id,))
        inputs = {r["input_key"]: r["confirmed_by"] for r in rows}
        result = SOP17Agent.generate_schedule_outline(
            inputs.get("project_type", "commercial"),
            inputs.get("construction_start", ""),
            inputs.get("substantial_completion", ""),
            inputs.get("project_name", ""),
        )
        for m in result.get("milestones", []):
            milestone = ScheduleMilestone(
                milestone_code=m.get("milestone_code", "M-000"),
                phase=m.get("phase", "framing"),
                description=m.get("description", ""),
                planned_start=m.get("planned_start", ""),
                planned_finish=m.get("planned_finish", ""),
                duration_days=m.get("duration_days", 0),
                float_days=m.get("float_days", 0),
                critical_path=m.get("critical_path", False),
                predecessor_codes=m.get("predecessor_codes", []),
                trade_codes=m.get("trade_codes", []),
                ai_generated=True,
            )
            cls.save_output(instance_id, "milestone", f"Milestone — {milestone.description}", content=milestone.to_dict())
        cls.save_output(instance_id, "schedule_risk", "AI Schedule Risk", content=result)
        cur = cls.get_instance(instance_id)
        if cur and cur["status"] == SOPStatus.IN_PROGRESS.value:
            cls.transition_status(instance_id, SOPStatus.AI_DRAFTED, "AI", "AI schedule generated")
        result["milestone_count"] = len(result.get("milestones", []))
        return result

    @classmethod
    def add_milestone(cls, instance_id: int, milestone_data: dict, actor: str = "pm") -> dict:
        m = ScheduleMilestone(**{k: v for k, v in milestone_data.items() if k in ScheduleMilestone.__dataclass_fields__})
        errors = m.validate()
        if errors:
            return {"status": "validation_error", "errors": errors}
        oid = cls.save_output(instance_id, "milestone", f"Milestone — {m.description}", content=m.to_dict())
        cls._log_event(instance_id, "milestone_added", m.milestone_code, actor)
        return {"output_id": oid, "milestone_code": m.milestone_code}

    @classmethod
    def pm_confirm_milestone(cls, instance_id: int, milestone_code: str, pm_name: str) -> dict:
        rows = db.query("SELECT id, content FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'milestone' AND content->>'milestone_code' = %s LIMIT 1",
                        (instance_id, milestone_code))
        if not rows:
            return {"error": f"Milestone {milestone_code} not found"}
        row = rows[0]
        content = json.loads(row["content"]) if isinstance(row["content"], str) else row["content"]
        content["pm_confirmed"] = True
        db.execute("UPDATE sop_outputs SET content = %s WHERE id = %s", (json.dumps(content), row["id"]))
        return {"milestone_code": milestone_code, "confirmed": True}

    @classmethod
    def pm_approve(cls, instance_id: int, pm_name: str) -> dict:
        rows = db.query("SELECT COUNT(*) AS cnt FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'milestone' AND (content->>'pm_confirmed')::boolean = TRUE", (instance_id,))
        confirmed = rows[0]["cnt"] if rows else 0

        # Pass through INTERNAL_REVIEW if not already there
        _cur = cls.get_instance(instance_id)
        _cs = _cur["status"] if _cur else ""
        if _cs not in ("Internal Review", "Approval Required", "Approved", "Handed Off", "Issued"):
            cls.transition_status(instance_id, SOPStatus.INTERNAL_REVIEW, pm_name,
                                  "PM review in progress")
        cls.transition_status(instance_id, SOPStatus.APPROVED, pm_name, f"Schedule approved — {confirmed} milestones confirmed")
        return {"status": SOPStatus.APPROVED.value, "confirmed_milestones": confirmed}

    @classmethod
    def hand_off_to_sop18(cls, instance_id: int, actor: str, project_id: int, owner_name: str) -> dict:
        StopConditionChecker.check_sc07_handoff_destination(instance_id, owner_name)
        cls.transition_status(instance_id, SOPStatus.HANDED_OFF, actor, "Handed off to SOP 18")
        from sop_18_long_lead.sop_18_service import SOP18LongLeadService
        sop18 = SOP18LongLeadService.start_procurement_log(project_id, instance_id, owner_name)
        return {"sop_17_status": SOPStatus.HANDED_OFF.value, "sop_18_instance": sop18}

    @classmethod
    def get_full_status(cls, instance_id: int) -> dict:
        instance = cls.get_instance(instance_id)
        if not instance:
            return {"error": "Instance not found"}
        rows = db.query("SELECT COUNT(*) AS cnt FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'milestone'", (instance_id,))
        total = rows[0]["cnt"] if rows else 0
        rows2 = db.query("SELECT COUNT(*) AS cnt FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'milestone' AND (content->>'pm_confirmed')::boolean = TRUE", (instance_id,))
        confirmed = rows2[0]["cnt"] if rows2 else 0
        return {"instance": instance, "total_milestones": total, "confirmed_milestones": confirmed, "audit_trail": cls.get_audit_trail(instance_id)}

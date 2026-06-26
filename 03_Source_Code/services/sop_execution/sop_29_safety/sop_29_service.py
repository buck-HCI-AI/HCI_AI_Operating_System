"""SOP 29 — Safety: execution service (Layers 1+2)."""
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
from .sop_29_templates import REQUIRED_INPUT_KEYS, INPUT_LABELS, SafetyHazard
from .sop_29_agent import SOP29Agent


class SOP29SafetyService(BaseSOP):
    SOP_NUMBER = "29"

    @classmethod
    def start_safety_plan(cls, project_id: int, project_type: str, superintendent_name: str,
                           sop_23_instance_id: int, owner_name: str,
                           scope_summary: str = "") -> dict:
        instance = cls.create_instance(project_id=project_id, owner_name=owner_name, owner_role="superintendent",
                                        parent_instance_id=sop_23_instance_id)
        iid = instance["id"]
        cls.confirm_input(iid, "project_type", project_type)
        cls.confirm_input(iid, "superintendent_name", superintendent_name)
        cls.confirm_input(iid, "sop_23_instance_id", str(sop_23_instance_id))
        cls.transition_status(iid, SOPStatus.IN_PROGRESS, owner_name, "Safety plan started")
        return {"instance": instance, "status": SOPStatus.IN_PROGRESS.value,
                "next_step": "Generate safety plan via run_ai_safety_plan() or add hazards manually."}

    @classmethod
    def run_ai_safety_plan(cls, instance_id: int, scope_summary: str = "",
                            site_conditions: str = "") -> dict:
        rows = db.query("SELECT input_key, confirmed_by FROM sop_inputs WHERE sop_instance_id = %s", (instance_id,))
        inputs = {r["input_key"]: r["confirmed_by"] for r in rows}
        row_inst = db.query_one("SELECT project_id FROM sop_instances WHERE id = %s", (instance_id,))
        pid = row_inst["project_id"] if row_inst else None
        proj_row = db.query_one("SELECT name FROM projects WHERE id = %s", (pid,)) if pid else None
        result = SOP29Agent.generate_safety_plan(
            inputs.get("project_type", "commercial"),
            proj_row["name"] if proj_row else f"Project {pid}",
            scope_summary, site_conditions,
        )
        for hazard in result.get("hazards", []):
            h = SafetyHazard(
                hazard_code=hazard.get("hazard_code", "SAF-000"),
                category=hazard.get("category", "struck_by"),
                description=hazard.get("description", ""),
                location=hazard.get("location", "General site"),
                risk_level=hazard.get("risk_level", "MEDIUM"),
                controls=hazard.get("controls", []),
                ai_identified=True,
            )
            errors = h.validate()
            if not errors:
                cls.save_output(instance_id, "safety_hazard", f"Hazard — {h.hazard_code}", content=h.to_dict())

        critical_open = SOP29Agent.flag_uncontrolled_critical(result.get("hazards", []))
        if critical_open.get("work_stop_required"):
            try:
                StopConditionChecker.check_sc03_risk_flag(instance_id, critical_open.get("immediate_actions", []))
            except WorkflowBlockedError:
                pass

        cur = cls.get_instance(instance_id)
        if cur and cur["status"] == SOPStatus.IN_PROGRESS.value:
            cls.transition_status(instance_id, SOPStatus.AI_DRAFTED, "AI", "AI safety plan generated")
        return result

    @classmethod
    def control_hazard(cls, instance_id: int, hazard_code: str, controls: list[str],
                        actor: str = "superintendent") -> dict:
        rows = db.query("SELECT id, content FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'safety_hazard' AND content->>'hazard_code' = %s LIMIT 1",
                        (instance_id, hazard_code))
        if not rows:
            return {"error": f"Hazard {hazard_code} not found"}
        row = rows[0]
        content = json.loads(row["content"]) if isinstance(row["content"], str) else row["content"]
        content["controls"] = controls
        content["status"] = "CONTROLLED"
        content["superintendent_confirmed"] = True
        db.execute("UPDATE sop_outputs SET content = %s WHERE id = %s", (json.dumps(content), row["id"]))
        cls._log_event(instance_id, "hazard_controlled", hazard_code, actor)
        return {"hazard_code": hazard_code, "status": "CONTROLLED"}

    @classmethod
    def pm_approve(cls, instance_id: int, pm_name: str) -> dict:
        rows = db.query("SELECT content FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'safety_hazard' AND content->>'risk_level' = 'CRITICAL' AND content->>'status' = 'IDENTIFIED'", (instance_id,))
        uncontrolled_critical = len(rows)
        if uncontrolled_critical > 0:
            return {"status": "blocked", "message": f"{uncontrolled_critical} CRITICAL hazards uncontrolled — work cannot proceed"}

        # Pass through INTERNAL_REVIEW if not already there
        _cur = cls.get_instance(instance_id)
        _cs = _cur["status"] if _cur else ""
        if _cs not in ("Internal Review", "Approval Required", "Approved", "Handed Off", "Issued"):
            cls.transition_status(instance_id, SOPStatus.INTERNAL_REVIEW, pm_name,
                                  "PM review in progress")
        cls.transition_status(instance_id, SOPStatus.APPROVED, pm_name, "Safety plan approved")
        return {"status": SOPStatus.APPROVED.value, "safe_to_proceed": True}

    @classmethod
    def get_full_status(cls, instance_id: int) -> dict:
        instance = cls.get_instance(instance_id)
        if not instance:
            return {"error": "Instance not found"}
        rows = db.query("SELECT COUNT(*) AS cnt FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'safety_hazard'", (instance_id,))
        total = rows[0]["cnt"] if rows else 0
        rows2 = db.query("SELECT COUNT(*) AS cnt FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'safety_hazard' AND content->>'risk_level' = 'CRITICAL' AND content->>'status' = 'IDENTIFIED'", (instance_id,))
        critical_open = rows2[0]["cnt"] if rows2 else 0
        return {"instance": instance, "total_hazards": total, "critical_uncontrolled": critical_open, "safe_to_proceed": critical_open == 0, "audit_trail": cls.get_audit_trail(instance_id)}

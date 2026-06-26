"""SOP 23 — Project Startup: execution service (Layers 1+2)."""
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
from .sop_23_templates import REQUIRED_INPUT_KEYS, INPUT_LABELS, StartupItem
from .sop_23_agent import SOP23Agent


class SOP23ProjectStartupService(BaseSOP):
    SOP_NUMBER = "23"

    @classmethod
    def start_startup(cls, project_id: int, sop_22_instance_id: int, owner_name: str,
                       superintendent_name: str, project_name: str, project_type: str,
                       construction_start: str) -> dict:
        instance = cls.create_instance(project_id=project_id, owner_name=owner_name, owner_role="pm",
                                        parent_instance_id=sop_22_instance_id)
        iid = instance["id"]
        cls.confirm_input(iid, "sop_22_instance_id", str(sop_22_instance_id))
        cls.confirm_input(iid, "superintendent_name", superintendent_name)
        cls.confirm_input(iid, "project_name", project_name)
        cls.confirm_input(iid, "project_type", project_type)
        cls.confirm_input(iid, "construction_start", construction_start)
        cls.transition_status(iid, SOPStatus.IN_PROGRESS, owner_name, "Project startup checklist started")
        return {"instance": instance, "status": SOPStatus.IN_PROGRESS.value,
                "next_step": "Generate startup checklist via run_ai_checklist() then complete items."}

    @classmethod
    def run_ai_checklist(cls, instance_id: int) -> dict:
        rows = db.query("SELECT input_key, confirmed_by FROM sop_inputs WHERE sop_instance_id = %s", (instance_id,))
        inputs = {r["input_key"]: r["confirmed_by"] for r in rows}
        result = SOP23Agent.generate_startup_checklist(
            inputs.get("project_type", "commercial"),
            inputs.get("project_name", ""),
            inputs.get("superintendent_name", ""),
            inputs.get("construction_start", ""),
        )
        for item in result.get("checklist_items", []):
            si = StartupItem(
                item_code=item.get("item_code", "STR-000"),
                category=item.get("category", "documents"),
                description=item.get("description", ""),
                responsible_party=item.get("responsible_party", "PM"),
                due_by=item.get("due_by", "Before construction start"),
                ai_generated=True,
            )
            errors = si.validate()
            if not errors:
                cls.save_output(instance_id, "startup_item", f"Startup — {si.description}", content=si.to_dict())
        cur = cls.get_instance(instance_id)
        if cur and cur["status"] == SOPStatus.IN_PROGRESS.value:
            cls.transition_status(instance_id, SOPStatus.AI_DRAFTED, "AI", "AI startup checklist generated")
        return result

    @classmethod
    def complete_item(cls, instance_id: int, item_code: str, actor: str = "pm") -> dict:
        rows = db.query("SELECT id, content FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'startup_item' AND content->>'item_code' = %s LIMIT 1",
                        (instance_id, item_code))
        if not rows:
            return {"error": f"Item {item_code} not found"}
        row = rows[0]
        content = json.loads(row["content"]) if isinstance(row["content"], str) else row["content"]
        content["status"] = "COMPLETE"
        content["pm_confirmed"] = True
        db.execute("UPDATE sop_outputs SET content = %s WHERE id = %s", (json.dumps(content), row["id"]))
        cls._log_event(instance_id, "startup_item_completed", item_code, actor)
        return {"item_code": item_code, "status": "COMPLETE"}

    @classmethod
    def pm_approve(cls, instance_id: int, pm_name: str) -> dict:
        rows = db.query("""SELECT content FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'startup_item'
                          AND content->>'category' IN ('safety','personnel','documents')
                          AND content->>'status' = 'PENDING'""", (instance_id,))
        blocking = len(rows)
        if blocking > 0:
            return {"status": "blocked", "message": f"{blocking} mandatory startup items still pending"}

        # Pass through INTERNAL_REVIEW if not already there
        _cur = cls.get_instance(instance_id)
        _cs = _cur["status"] if _cur else ""
        if _cs not in ("Internal Review", "Approval Required", "Approved", "Handed Off", "Issued"):
            cls.transition_status(instance_id, SOPStatus.INTERNAL_REVIEW, pm_name,
                                  "PM review in progress")
        cls.transition_status(instance_id, SOPStatus.APPROVED, pm_name, "Project startup approved — ready to build")
        return {"status": SOPStatus.APPROVED.value, "ready_to_build": True}

    @classmethod
    def hand_off_to_sop24(cls, instance_id: int, actor: str, project_id: int, owner_name: str) -> dict:
        StopConditionChecker.check_sc07_handoff_destination(instance_id, owner_name)
        cls.transition_status(instance_id, SOPStatus.HANDED_OFF, actor, "Handed off to SOP 24")
        from sop_24_super_dashboard.sop_24_service import SOP24SuperDashboardService
        sop24 = SOP24SuperDashboardService.start_dashboard(project_id, instance_id, owner_name)
        return {"sop_23_status": SOPStatus.HANDED_OFF.value, "sop_24_instance": sop24}

    @classmethod
    def get_full_status(cls, instance_id: int) -> dict:
        instance = cls.get_instance(instance_id)
        if not instance:
            return {"error": "Instance not found"}
        rows = db.query("SELECT COUNT(*) AS cnt FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'startup_item'", (instance_id,))
        total = rows[0]["cnt"] if rows else 0
        rows2 = db.query("SELECT COUNT(*) AS cnt FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'startup_item' AND content->>'status' = 'COMPLETE'", (instance_id,))
        done = rows2[0]["cnt"] if rows2 else 0
        return {"instance": instance, "total_items": total, "completed_items": done, "audit_trail": cls.get_audit_trail(instance_id)}

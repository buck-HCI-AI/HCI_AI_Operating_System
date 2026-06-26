"""SOP 20 — Contract Setup: execution service (Layers 1+2)."""
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
from .sop_20_templates import REQUIRED_INPUT_KEYS, INPUT_LABELS, ContractSetupItem
from .sop_20_agent import SOP20Agent


class SOP20ContractSetupService(BaseSOP):
    SOP_NUMBER = "20"

    @classmethod
    def start_contract_setup(cls, project_id: int, project_name: str, contract_type: str,
                              owner_name_client: str, gc_contract_value: float,
                              pm_name: str, sop_19_instance_id: int = 0) -> dict:
        instance = cls.create_instance(project_id=project_id, owner_name=pm_name, owner_role="pm",
                                        parent_instance_id=sop_19_instance_id or None)
        iid = instance["id"]
        cls.confirm_input(iid, "project_name", project_name)
        cls.confirm_input(iid, "contract_type", contract_type)
        cls.confirm_input(iid, "owner_name", owner_name_client)
        cls.confirm_input(iid, "gc_contract_value", str(gc_contract_value))
        if sop_19_instance_id:
            cls.confirm_input(iid, "sop_19_instance_id", str(sop_19_instance_id))
        cls.transition_status(iid, SOPStatus.IN_PROGRESS, pm_name, "Contract setup started")
        return {"instance": instance, "status": SOPStatus.IN_PROGRESS.value,
                "next_step": "Generate checklist via run_ai_checklist() or add items manually."}

    @classmethod
    def run_ai_checklist(cls, instance_id: int, scope_summary: str = "") -> dict:
        rows = db.query("SELECT input_key, confirmed_by FROM sop_inputs WHERE sop_instance_id = %s", (instance_id,))
        inputs = {r["input_key"]: r["confirmed_by"] for r in rows}
        result = SOP20Agent.generate_setup_checklist(
            inputs.get("contract_type", "lump_sum"),
            "",
            float(inputs.get("gc_contract_value", 0)),
            inputs.get("owner_name", ""),
        )
        for item in result.get("checklist_items", []):
            ci = ContractSetupItem(
                item_code=item.get("item_code", "CS-000"),
                category=item.get("category", "prime_contract"),
                description=item.get("description", ""),
                responsible_party=item.get("responsible_party", "PM"),
                due_date=item.get("due_date_offset", "Before NTP"),
                ai_flagged=item.get("priority") == "HIGH",
            )
            cls.save_output(instance_id, "setup_item", f"Setup — {ci.description}", content=ci.to_dict())
        cur = cls.get_instance(instance_id)
        if cur and cur["status"] == SOPStatus.IN_PROGRESS.value:
            cls.transition_status(instance_id, SOPStatus.AI_DRAFTED, "AI", "AI contract checklist generated")
        return result

    @classmethod
    def complete_item(cls, instance_id: int, item_code: str, actor: str = "pm") -> dict:
        rows = db.query("SELECT id, content FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'setup_item' AND content->>'item_code' = %s LIMIT 1",
                        (instance_id, item_code))
        if not rows:
            return {"error": f"Item {item_code} not found"}
        row = rows[0]
        content = json.loads(row["content"]) if isinstance(row["content"], str) else row["content"]
        content["status"] = "COMPLETE"
        content["pm_confirmed"] = True
        db.execute("UPDATE sop_outputs SET content = %s WHERE id = %s", (json.dumps(content), row["id"]))
        cls._log_event(instance_id, "item_completed", item_code, actor)
        return {"item_code": item_code, "status": "COMPLETE"}

    @classmethod
    def pm_approve(cls, instance_id: int, pm_name: str) -> dict:
        rows = db.query("SELECT content FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'setup_item' AND content->>'status' NOT IN ('COMPLETE', 'WAIVED')", (instance_id,))
        pending = len(rows)
        if pending > 0:
            return {"status": "blocked", "message": f"{pending} setup items still pending", "pending": pending}

        # Pass through INTERNAL_REVIEW if not already there
        _cur = cls.get_instance(instance_id)
        _cs = _cur["status"] if _cur else ""
        if _cs not in ("Internal Review", "Approval Required", "Approved", "Handed Off", "Issued"):
            cls.transition_status(instance_id, SOPStatus.INTERNAL_REVIEW, pm_name,
                                  "PM review in progress")
        cls.transition_status(instance_id, SOPStatus.APPROVED, pm_name, "Contract setup complete")
        return {"status": SOPStatus.APPROVED.value}

    @classmethod
    def hand_off_to_sop21(cls, instance_id: int, actor: str, project_id: int, owner_name: str, jurisdiction: str) -> dict:
        StopConditionChecker.check_sc07_handoff_destination(instance_id, owner_name)
        cls.transition_status(instance_id, SOPStatus.HANDED_OFF, actor, "Handed off to SOP 21")
        from sop_21_compliance.sop_21_service import SOP21ComplianceService
        sop21 = SOP21ComplianceService.start_compliance_log(project_id, instance_id, owner_name, jurisdiction)
        return {"sop_20_status": SOPStatus.HANDED_OFF.value, "sop_21_instance": sop21}

    @classmethod
    def get_full_status(cls, instance_id: int) -> dict:
        instance = cls.get_instance(instance_id)
        if not instance:
            return {"error": "Instance not found"}
        rows = db.query("SELECT COUNT(*) AS cnt FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'setup_item'", (instance_id,))
        total = rows[0]["cnt"] if rows else 0
        rows2 = db.query("SELECT COUNT(*) AS cnt FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'setup_item' AND content->>'status' IN ('COMPLETE', 'WAIVED')", (instance_id,))
        done = rows2[0]["cnt"] if rows2 else 0
        return {"instance": instance, "total_items": total, "completed_items": done, "audit_trail": cls.get_audit_trail(instance_id)}

"""SOP 21 — Compliance: execution service (Layers 1+2)."""
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
from .sop_21_templates import REQUIRED_INPUT_KEYS, INPUT_LABELS, ComplianceItem
from .sop_21_agent import SOP21Agent


class SOP21ComplianceService(BaseSOP):
    SOP_NUMBER = "21"

    @classmethod
    def start_compliance_log(cls, project_id: int, sop_20_instance_id: int,
                              owner_name: str, jurisdiction: str, project_type: str = "") -> dict:
        instance = cls.create_instance(project_id=project_id, owner_name=owner_name, owner_role="pm",
                                        parent_instance_id=sop_20_instance_id)
        iid = instance["id"]
        cls.confirm_input(iid, "sop_20_instance_id", str(sop_20_instance_id))
        cls.confirm_input(iid, "jurisdiction", jurisdiction)
        if project_type:
            cls.confirm_input(iid, "project_type", project_type)
        cls.transition_status(iid, SOPStatus.IN_PROGRESS, owner_name, f"Compliance log started — {jurisdiction}")
        return {"instance": instance, "status": SOPStatus.IN_PROGRESS.value,
                "next_step": "Run AI requirement identification via run_ai_identification()."}

    @classmethod
    def run_ai_identification(cls, instance_id: int, scope_summary: str = "",
                               contract_value: float = 0) -> dict:
        rows = db.query("SELECT input_key, confirmed_by FROM sop_inputs WHERE sop_instance_id = %s", (instance_id,))
        inputs = {r["input_key"]: r["confirmed_by"] for r in rows}
        result = SOP21Agent.identify_compliance_requirements(
            inputs.get("project_type", "commercial"),
            inputs.get("jurisdiction", ""),
            scope_summary,
            contract_value,
        )
        for req in result.get("requirements", []):
            ci = ComplianceItem(
                item_code=req.get("item_code", "CMP-000"),
                category=req.get("category", "building_permit"),
                description=req.get("description", ""),
                issuing_authority=req.get("issuing_authority", ""),
                required_by_date=req.get("required_by_date", "Before NTP"),
                responsible_party=req.get("responsible_party", "PM"),
                ai_identified=True,
            )
            errors = ci.validate()
            if not errors:
                cls.save_output(instance_id, "compliance_item", f"Compliance — {ci.description}", content=ci.to_dict())
        cur = cls.get_instance(instance_id)
        if cur and cur["status"] == SOPStatus.IN_PROGRESS.value:
            cls.transition_status(instance_id, SOPStatus.AI_DRAFTED, "AI", "AI compliance requirements identified")
        return result

    @classmethod
    def update_permit_status(cls, instance_id: int, item_code: str, status: str,
                              permit_number: str = "", actor: str = "pm") -> dict:
        rows = db.query("SELECT id, content FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'compliance_item' AND content->>'item_code' = %s LIMIT 1",
                        (instance_id, item_code))
        if not rows:
            return {"error": f"Item {item_code} not found"}
        row = rows[0]
        content = json.loads(row["content"]) if isinstance(row["content"], str) else row["content"]
        content["status"] = status
        if permit_number:
            content["permit_number"] = permit_number
        db.execute("UPDATE sop_outputs SET content = %s WHERE id = %s", (json.dumps(content), row["id"]))
        cls._log_event(instance_id, "permit_status_updated", f"{item_code}→{status}", actor)
        return {"item_code": item_code, "status": status}

    @classmethod
    def pm_approve(cls, instance_id: int, pm_name: str) -> dict:
        rows = db.query("""SELECT content FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'compliance_item'
                          AND content->>'category' IN ('building_permit','contractor_license')
                          AND content->>'status' NOT IN ('APPROVED','POSTED','NOT_REQUIRED')""", (instance_id,))
        blocking = len(rows)
        if blocking > 0:
            return {"status": "blocked", "message": f"{blocking} critical permits not yet approved"}

        # Pass through INTERNAL_REVIEW if not already there
        _cur = cls.get_instance(instance_id)
        _cs = _cur["status"] if _cur else ""
        if _cs not in ("Internal Review", "Approval Required", "Approved", "Handed Off", "Issued"):
            cls.transition_status(instance_id, SOPStatus.INTERNAL_REVIEW, pm_name,
                                  "PM review in progress")
        cls.transition_status(instance_id, SOPStatus.APPROVED, pm_name, "Compliance log approved — clear to build")
        return {"status": SOPStatus.APPROVED.value, "clear_to_build": True}

    @classmethod
    def hand_off_to_sop22(cls, instance_id: int, actor: str, project_id: int, owner_name: str) -> dict:
        StopConditionChecker.check_sc07_handoff_destination(instance_id, owner_name)
        cls.transition_status(instance_id, SOPStatus.HANDED_OFF, actor, "Handed off to SOP 22")
        from sop_22_coi_w9_lien.sop_22_service import SOP22COIService
        sop22 = SOP22COIService.start_doc_collection(project_id, instance_id, owner_name)
        return {"sop_21_status": SOPStatus.HANDED_OFF.value, "sop_22_instance": sop22}

    @classmethod
    def get_full_status(cls, instance_id: int) -> dict:
        instance = cls.get_instance(instance_id)
        if not instance:
            return {"error": "Instance not found"}
        rows = db.query("SELECT COUNT(*) AS cnt FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'compliance_item'", (instance_id,))
        total = rows[0]["cnt"] if rows else 0
        rows2 = db.query("SELECT COUNT(*) AS cnt FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'compliance_item' AND content->>'status' IN ('APPROVED','POSTED','CLOSED','NOT_REQUIRED')", (instance_id,))
        resolved = rows2[0]["cnt"] if rows2 else 0
        return {"instance": instance, "total_items": total, "resolved_items": resolved, "audit_trail": cls.get_audit_trail(instance_id)}

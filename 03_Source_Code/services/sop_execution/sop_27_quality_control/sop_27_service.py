"""SOP 27 — Quality Control: execution service (Layers 1+2)."""
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
from .sop_27_templates import REQUIRED_INPUT_KEYS, INPUT_LABELS, QCInspectionItem
from .sop_27_agent import SOP27Agent


class SOP27QualityControlService(BaseSOP):
    SOP_NUMBER = "27"

    @classmethod
    def start_qc(cls, project_id: int, project_type: str, sop_23_instance_id: int, owner_name: str) -> dict:
        instance = cls.create_instance(project_id=project_id, owner_name=owner_name, owner_role="superintendent",
                                        parent_instance_id=sop_23_instance_id)
        iid = instance["id"]
        cls.confirm_input(iid, "sop_23_instance_id", str(sop_23_instance_id))
        cls.confirm_input(iid, "project_type", project_type)
        cls.transition_status(iid, SOPStatus.IN_PROGRESS, owner_name, "QC log active")
        return {"instance": instance, "status": SOPStatus.IN_PROGRESS.value}

    @classmethod
    def generate_checklist(cls, instance_id: int, trade_code: str, category: str,
                            spec_section: str = "") -> dict:
        rows = db.query("SELECT input_key, confirmed_by FROM sop_inputs WHERE sop_instance_id = %s", (instance_id,))
        inputs = {r["input_key"]: r["confirmed_by"] for r in rows}
        result = SOP27Agent.generate_qc_checklist(
            inputs.get("project_type", "commercial"), trade_code, category, spec_section
        )
        for item in result.get("inspection_items", []):
            qi = QCInspectionItem(
                item_code=item.get("item_code", "QC-000"),
                category=category,
                description=item.get("description", ""),
                specification_ref=item.get("specification_ref", ""),
                trade_code=trade_code,
                inspector="",
                inspection_date="",
                ai_generated=True,
            )
            errors = qi.validate()
            if not errors:
                cls.save_output(instance_id, "qc_item", f"QC — {qi.description}", content=qi.to_dict())
        return result

    @classmethod
    def record_result(cls, instance_id: int, item_code: str, result: str,
                       inspector: str, inspection_date: str,
                       deficiency_notes: str = "", severity: str = "MINOR") -> dict:
        rows = db.query("SELECT id, content FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'qc_item' AND content->>'item_code' = %s LIMIT 1",
                        (instance_id, item_code))
        if not rows:
            return {"error": f"QC item {item_code} not found"}
        row = rows[0]
        content = json.loads(row["content"]) if isinstance(row["content"], str) else row["content"]
        content["result"] = result
        content["inspector"] = inspector
        content["inspection_date"] = inspection_date
        content["deficiency_notes"] = deficiency_notes
        content["severity"] = severity
        content["re_inspection_required"] = result == "FAIL"
        db.execute("UPDATE sop_outputs SET content = %s WHERE id = %s", (json.dumps(content), row["id"]))
        cls._log_event(instance_id, "qc_result_recorded", f"{item_code}→{result}", inspector)

        if result == "FAIL" and severity == "CRITICAL":
            try:
                StopConditionChecker.check_sc03_risk_flag(instance_id, [f"CRITICAL QC FAILURE: {item_code} — {deficiency_notes}"])
            except WorkflowBlockedError:
                pass

        return {"item_code": item_code, "result": result, "re_inspection_required": result == "FAIL"}

    @classmethod
    def get_full_status(cls, instance_id: int) -> dict:
        instance = cls.get_instance(instance_id)
        if not instance:
            return {"error": "Instance not found"}
        rows = db.query("SELECT COUNT(*) AS cnt FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'qc_item'", (instance_id,))
        total = rows[0]["cnt"] if rows else 0
        rows2 = db.query("SELECT COUNT(*) AS cnt FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'qc_item' AND content->>'result' = 'FAIL'", (instance_id,))
        failures = rows2[0]["cnt"] if rows2 else 0
        rows3 = db.query("SELECT COUNT(*) AS cnt FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'qc_item' AND content->>'result' = 'FAIL' AND content->>'severity' = 'CRITICAL'", (instance_id,))
        critical = rows3[0]["cnt"] if rows3 else 0
        return {"instance": instance, "total_items": total, "failures": failures, "critical_failures": critical, "audit_trail": cls.get_audit_trail(instance_id)}

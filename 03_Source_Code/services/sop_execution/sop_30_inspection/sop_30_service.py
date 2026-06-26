"""SOP 30 — Inspection: execution service (Layers 1+2)."""
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
from .sop_30_templates import REQUIRED_INPUT_KEYS, INPUT_LABELS, InspectionRecord
from .sop_30_agent import SOP30Agent


class SOP30InspectionService(BaseSOP):
    SOP_NUMBER = "30"

    @classmethod
    def start_inspection_log(cls, project_id: int, jurisdiction: str,
                              sop_21_instance_id: int, owner_name: str) -> dict:
        instance = cls.create_instance(project_id=project_id, owner_name=owner_name, owner_role="superintendent",
                                        parent_instance_id=sop_21_instance_id)
        iid = instance["id"]
        cls.confirm_input(iid, "jurisdiction", jurisdiction)
        cls.confirm_input(iid, "sop_21_instance_id", str(sop_21_instance_id))
        cls.transition_status(iid, SOPStatus.IN_PROGRESS, owner_name, f"Inspection log started — {jurisdiction}")
        return {"instance": instance, "status": SOPStatus.IN_PROGRESS.value}

    @classmethod
    def schedule_inspection(cls, instance_id: int, inspection_type: str, permit_number: str,
                             scheduled_date: str, description: str = "",
                             actor: str = "pm") -> dict:
        rows = db.query("SELECT input_key, confirmed_by FROM sop_inputs WHERE sop_instance_id = %s", (instance_id,))
        inputs = {r["input_key"]: r["confirmed_by"] for r in rows}
        prep = SOP30Agent.prepare_inspection_checklist(
            inspection_type, "", inputs.get("jurisdiction", ""), permit_number
        )
        inspection_code = f"INS-{inspection_type[:4].upper()}-{scheduled_date.replace('-', '')}"
        ir = InspectionRecord(
            inspection_code=inspection_code,
            inspection_type=inspection_type,
            description=description or inspection_type.replace("_", " ").title(),
            permit_number=permit_number,
            scheduled_date=scheduled_date,
            result="SCHEDULED",
            ai_prep_notes=prep.get("pass_criteria_summary", ""),
        )
        errors = ir.validate()
        if errors:
            return {"status": "validation_error", "errors": errors}
        oid = cls.save_output(instance_id, "inspection", f"Inspection — {ir.inspection_type}", content=ir.to_dict())
        cls.save_output(instance_id, "inspection_prep", f"Prep — {inspection_type}", content=prep)
        cls._log_event(instance_id, "inspection_scheduled", inspection_code, actor)
        return {"output_id": oid, "inspection_code": inspection_code, "prep_checklist": prep}

    @classmethod
    def record_result(cls, instance_id: int, inspection_code: str, result: str,
                       inspector_name: str, inspection_date: str,
                       correction_items: list[str] | None = None,
                       actor: str = "superintendent") -> dict:
        rows = db.query("SELECT id, content FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'inspection' AND content->>'inspection_code' = %s LIMIT 1",
                        (instance_id, inspection_code))
        if not rows:
            return {"error": f"Inspection {inspection_code} not found"}
        row = rows[0]
        content = json.loads(row["content"]) if isinstance(row["content"], str) else row["content"]
        content["result"] = result
        content["inspector_name"] = inspector_name
        content["inspection_date"] = inspection_date
        content["correction_items"] = correction_items or []
        content["card_signed"] = result == "PASS"
        db.execute("UPDATE sop_outputs SET content = %s WHERE id = %s", (json.dumps(content), row["id"]))
        cls._log_event(instance_id, "inspection_result_recorded", f"{inspection_code}→{result}", actor)

        if result in ("FAIL", "CORRECTION_NOTICE") and correction_items:
            analysis = SOP30Agent.analyze_correction_notice(content.get("inspection_type", ""), correction_items)
            cls.save_output(instance_id, "correction_analysis", f"Corrections — {inspection_code}", content=analysis)
            try:
                StopConditionChecker.check_sc03_risk_flag(instance_id, [f"INSPECTION FAILED: {inspection_code} — {len(correction_items)} corrections required"])
            except WorkflowBlockedError:
                pass

        return {"inspection_code": inspection_code, "result": result, "card_signed": content["card_signed"]}

    @classmethod
    def get_full_status(cls, instance_id: int) -> dict:
        instance = cls.get_instance(instance_id)
        if not instance:
            return {"error": "Instance not found"}
        rows = db.query("SELECT COUNT(*) AS cnt FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'inspection'", (instance_id,))
        total = rows[0]["cnt"] if rows else 0
        rows2 = db.query("SELECT COUNT(*) AS cnt FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'inspection' AND content->>'result' = 'PASS'", (instance_id,))
        passed = rows2[0]["cnt"] if rows2 else 0
        rows3 = db.query("SELECT COUNT(*) AS cnt FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'inspection' AND content->>'result' IN ('FAIL','CORRECTION_NOTICE')", (instance_id,))
        failed = rows3[0]["cnt"] if rows3 else 0
        return {"instance": instance, "total_inspections": total, "passed": passed, "failed": failed, "audit_trail": cls.get_audit_trail(instance_id)}

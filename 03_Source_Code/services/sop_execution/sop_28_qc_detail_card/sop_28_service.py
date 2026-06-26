"""SOP 28 — QC Detail Card: execution service (Layers 1+2)."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import services.db as db
from shared.base_sop import BaseSOP
from shared.sop_data_model import SOPStatus
from .sop_28_templates import REQUIRED_INPUT_KEYS, INPUT_LABELS, QCDetailWorkItem
from .sop_28_agent import SOP28Agent


class SOP28QCDetailCardService(BaseSOP):
    SOP_NUMBER = "28"

    @classmethod
    def start_detail_card(cls, project_id: int, trade_code: str, trade_name: str,
                           sop_27_instance_id: int, owner_name: str,
                           spec_sections: list[str] | None = None) -> dict:
        instance = cls.create_instance(project_id=project_id, owner_name=owner_name, owner_role="pm",
                                        parent_instance_id=sop_27_instance_id)
        iid = instance["id"]
        cls.confirm_input(iid, "trade_code", trade_code)
        cls.confirm_input(iid, "trade_name", trade_name)
        cls.confirm_input(iid, "sop_27_instance_id", str(sop_27_instance_id))
        cls.transition_status(iid, SOPStatus.IN_PROGRESS, owner_name, f"QC detail card started — {trade_name}")
        return {"instance": instance, "status": SOPStatus.IN_PROGRESS.value,
                "next_step": "Run AI draft via run_ai_draft() to auto-generate work items."}

    @classmethod
    def run_ai_draft(cls, instance_id: int, project_type: str = "commercial",
                     spec_sections: list[str] | None = None) -> dict:
        rows = db.query("SELECT input_key, confirmed_by FROM sop_inputs WHERE sop_instance_id = %s", (instance_id,))
        inputs = {r["input_key"]: r["confirmed_by"] for r in rows}
        result = SOP28Agent.draft_detail_card(
            inputs.get("trade_code", ""), inputs.get("trade_name", ""),
            project_type, spec_sections or [],
        )
        for item in result.get("work_items", []):
            wi = QCDetailWorkItem(
                work_item_code=item.get("work_item_code", "WI-000"),
                description=item.get("description", ""),
                specification_ref=item.get("specification_ref", ""),
                acceptance_criteria=item.get("acceptance_criteria", ""),
                hold_point=item.get("hold_point", False),
                inspection_method=item.get("inspection_method", "Visual"),
                frequency=item.get("frequency", ""),
                responsible_party=item.get("responsible_party", "Superintendent"),
                ai_drafted=True,
            )
            errors = wi.validate()
            if not errors:
                cls.save_output(instance_id, "qc_work_item", f"WI — {wi.description}", content=wi.to_dict())
        cur = cls.get_instance(instance_id)
        if cur and cur["status"] == SOPStatus.IN_PROGRESS.value:
            cls.transition_status(instance_id, SOPStatus.AI_DRAFTED, "AI", "QC detail card AI-drafted")
        return result

    @classmethod
    def confirm_work_item(cls, instance_id: int, work_item_code: str, pm_name: str) -> dict:
        rows = db.query("SELECT id, content FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'qc_work_item' AND content->>'work_item_code' = %s LIMIT 1",
                        (instance_id, work_item_code))
        if not rows:
            return {"error": f"Work item {work_item_code} not found"}
        row = rows[0]
        content = json.loads(row["content"]) if isinstance(row["content"], str) else row["content"]
        content["pm_confirmed"] = True
        db.execute("UPDATE sop_outputs SET content = %s WHERE id = %s", (json.dumps(content), row["id"]))
        return {"work_item_code": work_item_code, "confirmed": True}

    @classmethod
    def pm_approve(cls, instance_id: int, pm_name: str) -> dict:
        rows = db.query("SELECT COUNT(*) AS cnt FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'qc_work_item' AND (content->>'pm_confirmed')::boolean = TRUE", (instance_id,))
        confirmed = rows[0]["cnt"] if rows else 0

        # Pass through INTERNAL_REVIEW if not already there
        _cur = cls.get_instance(instance_id)
        _cs = _cur["status"] if _cur else ""
        if _cs not in ("Internal Review", "Approval Required", "Approved", "Handed Off", "Issued"):
            cls.transition_status(instance_id, SOPStatus.INTERNAL_REVIEW, pm_name,
                                  "PM review in progress")
        cls.transition_status(instance_id, SOPStatus.APPROVED, pm_name, f"QC detail card approved — {confirmed} work items")
        return {"status": SOPStatus.APPROVED.value, "confirmed_work_items": confirmed}

    @classmethod
    def get_full_status(cls, instance_id: int) -> dict:
        instance = cls.get_instance(instance_id)
        if not instance:
            return {"error": "Instance not found"}
        rows = db.query("SELECT COUNT(*) AS cnt FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'qc_work_item'", (instance_id,))
        total = rows[0]["cnt"] if rows else 0
        rows2 = db.query("SELECT COUNT(*) AS cnt FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'qc_work_item' AND content->>'hold_point' = 'true' AND content->>'hold_point_status' = 'OPEN'", (instance_id,))
        open_holds = rows2[0]["cnt"] if rows2 else 0
        return {"instance": instance, "total_work_items": total, "open_hold_points": open_holds, "audit_trail": cls.get_audit_trail(instance_id)}

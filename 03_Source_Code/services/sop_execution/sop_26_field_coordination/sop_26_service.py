"""SOP 26 — Field Coordination: execution service (Layers 1+2)."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
from datetime import date
import services.db as db
from shared.base_sop import BaseSOP
from shared.sop_data_model import SOPStatus
from .sop_26_templates import REQUIRED_INPUT_KEYS, INPUT_LABELS, FieldCoordItem, COORD_TYPES
from .sop_26_agent import SOP26Agent


class SOP26FieldCoordService(BaseSOP):
    SOP_NUMBER = "26"

    @classmethod
    def start_coordination(cls, project_id: int, sop_23_instance_id: int, owner_name: str) -> dict:
        instance = cls.create_instance(project_id=project_id, owner_name=owner_name, owner_role="pm",
                                        parent_instance_id=sop_23_instance_id)
        iid = instance["id"]
        cls.confirm_input(iid, "sop_23_instance_id", str(sop_23_instance_id))
        cls.transition_status(iid, SOPStatus.IN_PROGRESS, owner_name, "Field coordination log active")
        return {"instance": instance, "status": SOPStatus.IN_PROGRESS.value}

    @classmethod
    def add_item(cls, instance_id: int, item_data: dict, actor: str = "pm") -> dict:
        item_data.setdefault("date_opened", date.today().isoformat())
        fi = FieldCoordItem(**{k: v for k, v in item_data.items() if k in FieldCoordItem.__dataclass_fields__})
        errors = fi.validate()
        if errors:
            return {"status": "validation_error", "errors": errors}
        oid = cls.save_output(instance_id, "coord_item", f"{fi.coord_type} — {fi.item_code}", content=fi.to_dict())
        cls._log_event(instance_id, "coord_item_added", fi.item_code, actor)
        return {"output_id": oid, "item_code": fi.item_code}

    @classmethod
    def draft_response(cls, instance_id: int, item_code: str) -> dict:
        rows = db.query("SELECT content FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'coord_item' AND content->>'item_code' = %s LIMIT 1",
                        (instance_id, item_code))
        if not rows:
            return {"error": f"Item {item_code} not found"}
        content = json.loads(rows[0]["content"]) if isinstance(rows[0]["content"], str) else rows[0]["content"]
        row_inst = db.query_one("SELECT project_id FROM sop_instances WHERE id = %s", (instance_id,))
        pid = row_inst["project_id"] if row_inst else None
        proj_row = db.query_one("SELECT scope FROM projects WHERE id = %s", (pid,)) if pid else None
        result = SOP26Agent.draft_rfi_response(
            item_code, content.get("description", ""),
            content.get("drawing_refs", []), content.get("spec_refs", []),
            "commercial",
        )
        content["response"] = result.get("draft_response", "")
        content["ai_drafted_response"] = True
        db.execute("UPDATE sop_outputs SET content = %s WHERE sop_instance_id = %s AND output_type = 'coord_item' AND content->>'item_code' = %s",
                   (json.dumps(content), instance_id, item_code))
        return result

    @classmethod
    def close_item(cls, instance_id: int, item_code: str, resolution: str, actor: str = "pm") -> dict:
        rows = db.query("SELECT id, content FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'coord_item' AND content->>'item_code' = %s LIMIT 1",
                        (instance_id, item_code))
        if not rows:
            return {"error": f"Item {item_code} not found"}
        row = rows[0]
        content = json.loads(row["content"]) if isinstance(row["content"], str) else row["content"]
        content["status"] = "CLOSED"
        content["date_closed"] = date.today().isoformat()
        content["response"] = resolution or content.get("response", "")
        content["pm_confirmed"] = True
        db.execute("UPDATE sop_outputs SET content = %s WHERE id = %s", (json.dumps(content), row["id"]))
        cls._log_event(instance_id, "coord_item_closed", item_code, actor)
        return {"item_code": item_code, "status": "CLOSED"}

    @classmethod
    def get_full_status(cls, instance_id: int) -> dict:
        instance = cls.get_instance(instance_id)
        if not instance:
            return {"error": "Instance not found"}
        rows = db.query("SELECT COUNT(*) AS cnt FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'coord_item'", (instance_id,))
        total = rows[0]["cnt"] if rows else 0
        rows2 = db.query("SELECT COUNT(*) AS cnt FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'coord_item' AND content->>'status' = 'OPEN'", (instance_id,))
        open_count = rows2[0]["cnt"] if rows2 else 0
        return {"instance": instance, "total_items": total, "open_items": open_count, "audit_trail": cls.get_audit_trail(instance_id)}

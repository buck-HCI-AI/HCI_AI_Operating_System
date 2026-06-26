"""SOP 18 — Long-Lead Procurement: execution service (Layers 1+2)."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import services.db as db
from shared.base_sop import BaseSOP
from shared.sop_data_model import SOPStatus
from .sop_18_templates import REQUIRED_INPUT_KEYS, INPUT_LABELS, LongLeadItem
from .sop_18_agent import SOP18Agent


class SOP18LongLeadService(BaseSOP):
    SOP_NUMBER = "18"

    @classmethod
    def start_procurement_log(cls, project_id: int, sop_17_instance_id: int,
                               owner_name: str, project_type: str = "",
                               construction_start: str = "") -> dict:
        instance = cls.create_instance(project_id=project_id, owner_name=owner_name, owner_role="pm",
                                        parent_instance_id=sop_17_instance_id)
        iid = instance["id"]
        cls.confirm_input(iid, "sop_17_instance_id", str(sop_17_instance_id))
        if project_type:
            cls.confirm_input(iid, "project_type", project_type)
        if construction_start:
            cls.confirm_input(iid, "construction_start", construction_start)
        cls.transition_status(iid, SOPStatus.IN_PROGRESS, owner_name, "Long-lead procurement log started")
        return {"instance": instance, "status": SOPStatus.IN_PROGRESS.value,
                "next_step": "Run AI identification via run_ai_identification() or add items manually."}

    @classmethod
    def run_ai_identification(cls, instance_id: int, narrative_summary: str = "") -> dict:
        rows = db.query("SELECT input_key, confirmed_by FROM sop_inputs WHERE sop_instance_id = %s", (instance_id,))
        inputs = {r["input_key"]: r["confirmed_by"] for r in rows}
        result = SOP18Agent.identify_long_lead_items(
            inputs.get("project_type", "commercial"),
            narrative_summary,
            inputs.get("construction_start", ""),
        )
        for item in result.get("items", []):
            ll = LongLeadItem(
                item_code=f"LL-{len(result.get('items', []))+1:03d}",
                description=item.get("description", ""),
                trade_code=item.get("trade_code", "GEN"),
                lead_time_weeks=item.get("lead_time_weeks", 4),
                order_by_date=item.get("order_by_date", ""),
                required_on_site=item.get("required_on_site", ""),
                risk_level=item.get("risk_level", "MEDIUM"),
                ai_identified=True,
                notes=item.get("notes", ""),
            )
            cls.save_output(instance_id, "long_lead_item", f"LL — {ll.description}", content=ll.to_dict())
        cur = cls.get_instance(instance_id)
        if cur and cur["status"] == SOPStatus.IN_PROGRESS.value:
            cls.transition_status(instance_id, SOPStatus.AI_DRAFTED, "AI", "AI long-lead identification complete")
        return result

    @classmethod
    def add_long_lead_item(cls, instance_id: int, item_data: dict, actor: str = "pm") -> dict:
        ll = LongLeadItem(**{k: v for k, v in item_data.items() if k in LongLeadItem.__dataclass_fields__})
        errors = ll.validate()
        if errors:
            return {"status": "validation_error", "errors": errors}
        oid = cls.save_output(instance_id, "long_lead_item", f"LL — {ll.description}", content=ll.to_dict())
        cls._log_event(instance_id, "ll_item_added", ll.item_code, actor)
        return {"output_id": oid, "item_code": ll.item_code}

    @classmethod
    def update_item_status(cls, instance_id: int, item_code: str, status: str, actor: str = "pm") -> dict:
        rows = db.query("SELECT id, content FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'long_lead_item' AND content->>'item_code' = %s LIMIT 1",
                        (instance_id, item_code))
        if not rows:
            return {"error": f"Item {item_code} not found"}
        row = rows[0]
        content = json.loads(row["content"]) if isinstance(row["content"], str) else row["content"]
        content["status"] = status
        db.execute("UPDATE sop_outputs SET content = %s WHERE id = %s", (json.dumps(content), row["id"]))
        cls._log_event(instance_id, "ll_status_updated", f"{item_code}→{status}", actor)
        return {"item_code": item_code, "status": status}

    @classmethod
    def pm_approve(cls, instance_id: int, pm_name: str) -> dict:
        rows = db.query("SELECT COUNT(*) AS cnt FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'long_lead_item'", (instance_id,))
        total = rows[0]["cnt"] if rows else 0

        # Pass through INTERNAL_REVIEW if not already there
        _cur = cls.get_instance(instance_id)
        _cs = _cur["status"] if _cur else ""
        if _cs not in ("Internal Review", "Approval Required", "Approved", "Handed Off", "Issued"):
            cls.transition_status(instance_id, SOPStatus.INTERNAL_REVIEW, pm_name,
                                  "PM review in progress")
        cls.transition_status(instance_id, SOPStatus.APPROVED, pm_name, f"Long-lead log approved — {total} items")
        return {"status": SOPStatus.APPROVED.value, "total_items": total}

    @classmethod
    def get_full_status(cls, instance_id: int) -> dict:
        instance = cls.get_instance(instance_id)
        if not instance:
            return {"error": "Instance not found"}
        rows = db.query("SELECT content FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'long_lead_item'", (instance_id,))
        items = [json.loads(r["content"]) if isinstance(r["content"], str) else r["content"] for r in rows]
        critical = [i for i in items if i.get("risk_level") in ("HIGH", "CRITICAL")]
        return {"instance": instance, "total_items": len(items), "critical_items": len(critical),
                "items": items, "audit_trail": cls.get_audit_trail(instance_id)}

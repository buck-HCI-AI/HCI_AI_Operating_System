"""SOP 24 — Superintendent Daily Dashboard: execution service (Layers 1+2)."""
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
from .sop_24_templates import REQUIRED_INPUT_KEYS, INPUT_LABELS, DashboardMetric
from .sop_24_agent import SOP24Agent


class SOP24SuperDashboardService(BaseSOP):
    SOP_NUMBER = "24"

    @classmethod
    def start_dashboard(cls, project_id: int, sop_23_instance_id: int, owner_name: str) -> dict:
        instance = cls.create_instance(project_id=project_id, owner_name=owner_name, owner_role="superintendent",
                                        parent_instance_id=sop_23_instance_id)
        iid = instance["id"]
        cls.confirm_input(iid, "sop_23_instance_id", str(sop_23_instance_id))
        cls.confirm_input(iid, "superintendent_name", owner_name)
        cls.transition_status(iid, SOPStatus.IN_PROGRESS, owner_name, "Superintendent dashboard active")
        return {"instance": instance, "status": SOPStatus.IN_PROGRESS.value,
                "next_step": "Update metrics via update_metric() and run generate_daily_brief()."}

    @classmethod
    def update_metric(cls, instance_id: int, metric_data: dict, actor: str = "superintendent") -> dict:
        m = DashboardMetric(**{k: v for k, v in metric_data.items() if k in DashboardMetric.__dataclass_fields__})
        errors = m.validate()
        if errors:
            return {"status": "validation_error", "errors": errors}
        if not m.date:
            m.date = date.today().isoformat()
        oid = cls.save_output(instance_id, "dashboard_metric", f"Metric — {m.label}", content=m.to_dict())
        cls._log_event(instance_id, "metric_updated", f"{m.label}={m.value}", actor)
        return {"output_id": oid, "metric_code": m.metric_code, "alert_level": m.alert_level}

    @classmethod
    def generate_daily_brief(cls, instance_id: int, snap_date: str = "") -> dict:
        snap_date = snap_date or date.today().isoformat()
        rows = db.query("SELECT input_key, confirmed_by FROM sop_inputs WHERE sop_instance_id = %s", (instance_id,))
        inputs = {r["input_key"]: r["confirmed_by"] for r in rows}
        row_inst = db.query_one("SELECT project_id FROM sop_instances WHERE id = %s", (instance_id,))
        pid = row_inst["project_id"] if row_inst else None
        proj_row = db.query_one("SELECT name FROM projects WHERE id = %s", (pid,)) if pid else None
        project_name = proj_row["name"] if proj_row else f"Project {pid}"

        metric_rows = db.query("SELECT content FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'dashboard_metric' AND content->>'date' = %s",
                               (instance_id, snap_date))
        metrics = [json.loads(r["content"]) if isinstance(r["content"], str) else r["content"] for r in metric_rows]

        result = SOP24Agent.generate_daily_brief(project_name, snap_date, metrics)
        cls.save_output(instance_id, "daily_brief", f"Brief — {snap_date}", content=result)
        return result

    @classmethod
    def get_full_status(cls, instance_id: int) -> dict:
        instance = cls.get_instance(instance_id)
        if not instance:
            return {"error": "Instance not found"}
        today = date.today().isoformat()
        metric_rows = db.query("SELECT content FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'dashboard_metric' AND content->>'date' = %s",
                               (instance_id, today))
        metrics = [json.loads(r["content"]) if isinstance(r["content"], str) else r["content"] for r in metric_rows]
        red = [m for m in metrics if m.get("alert_level") == "RED"]
        return {"instance": instance, "today": today, "metric_count": len(metrics), "red_alerts": len(red), "metrics": metrics}

"""SOP 25 — Daily Log: execution service (Layers 1+2)."""
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
from .sop_25_templates import REQUIRED_INPUT_KEYS, INPUT_LABELS, DailyLogEntry
from .sop_25_agent import SOP25Agent


class SOP25DailyLogService(BaseSOP):
    SOP_NUMBER = "25"

    @classmethod
    def start_log(cls, project_id: int, sop_23_instance_id: int, owner_name: str) -> dict:
        instance = cls.create_instance(project_id=project_id, owner_name=owner_name, owner_role="superintendent",
                                        parent_instance_id=sop_23_instance_id)
        iid = instance["id"]
        cls.confirm_input(iid, "sop_23_instance_id", str(sop_23_instance_id))
        cls.confirm_input(iid, "superintendent_name", owner_name)
        cls.transition_status(iid, SOPStatus.IN_PROGRESS, owner_name, "Daily log active")
        return {"instance": instance, "status": SOPStatus.IN_PROGRESS.value}

    @classmethod
    def create_entry(cls, instance_id: int, entry_data: dict,
                     actor: str = "superintendent") -> dict:
        entry = DailyLogEntry(**{k: v for k, v in entry_data.items() if k in DailyLogEntry.__dataclass_fields__})
        errors = entry.validate()
        if errors:
            return {"status": "validation_error", "errors": errors}

        analysis = SOP25Agent.analyze_log_entry(
            entry.log_date, entry.weather, entry.work_performed,
            entry.delays, entry.incidents, entry.total_workers,
        )
        entry.ai_risk_flags = analysis.get("risk_flags", [])

        oid = cls.save_output(instance_id, "daily_log_entry", f"Log — {entry.log_date}", content=entry.to_dict())
        cls._log_event(instance_id, "log_entry_created", entry.log_date, actor)

        if analysis.get("pm_notification_required"):
            cls.save_output(instance_id, "pm_notification", f"PM Alert — {entry.log_date}", content=analysis)

        return {"output_id": oid, "log_date": entry.log_date,
                "risk_flags": entry.ai_risk_flags,
                "pm_notification": analysis.get("pm_notification_required", False)}

    @classmethod
    def close_day(cls, instance_id: int, log_date: str, actor: str = "superintendent") -> dict:
        rows = db.query("SELECT id, content FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'daily_log_entry' AND content->>'log_date' = %s LIMIT 1",
                        (instance_id, log_date))
        if not rows:
            return {"error": f"No log entry found for {log_date}"}
        row = rows[0]
        content = json.loads(row["content"]) if isinstance(row["content"], str) else row["content"]
        content["status"] = "CLOSED"
        db.execute("UPDATE sop_outputs SET content = %s WHERE id = %s", (json.dumps(content), row["id"]))
        cls._log_event(instance_id, "day_closed", log_date, actor)
        return {"log_date": log_date, "status": "CLOSED"}

    @classmethod
    def get_weekly_summary(cls, instance_id: int, week_start: str) -> dict:
        rows = db.query("SELECT content FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'daily_log_entry' AND content->>'log_date' >= %s ORDER BY content->>'log_date' LIMIT 7",
                        (instance_id, week_start))
        entries = [json.loads(r["content"]) if isinstance(r["content"], str) else r["content"] for r in rows]
        if not entries:
            return {"error": "No log entries found for that week"}
        row_inst = db.query_one("SELECT project_id FROM sop_instances WHERE id = %s", (instance_id,))
        pid = row_inst["project_id"] if row_inst else None
        proj_row = db.query_one("SELECT name FROM projects WHERE id = %s", (pid,)) if pid else None
        project_name = proj_row["name"] if proj_row else f"Project {pid}"
        return SOP25Agent.generate_weekly_summary(entries, project_name)

    @classmethod
    def get_full_status(cls, instance_id: int) -> dict:
        instance = cls.get_instance(instance_id)
        if not instance:
            return {"error": "Instance not found"}
        rows = db.query("SELECT COUNT(*) AS cnt FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'daily_log_entry'", (instance_id,))
        total_logs = rows[0]["cnt"] if rows else 0
        return {"instance": instance, "total_log_days": total_logs, "audit_trail": cls.get_audit_trail(instance_id)}

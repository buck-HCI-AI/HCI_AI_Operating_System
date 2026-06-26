"""KPI tracking for SOP execution instances."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import services.db as db


class SOPKPITracker:
    """Records and queries cycle time and quality KPIs for SOP instances."""

    @staticmethod
    def record_kpi(sop_instance_id: int, kpi_code: str, value: float,
                   unit: str, project_id: int | None = None) -> None:
        db.execute("""
            INSERT INTO sop_kpi_records
                (sop_instance_id, project_id, kpi_code, value, unit, recorded_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (sop_instance_id, project_id, kpi_code, value, unit))

    @staticmethod
    def compute_cycle_time(sop_instance_id: int, from_status: str,
                           to_status: str) -> float | None:
        """Return hours between two status events. None if either event is missing."""
        row = db.query_one("""
            SELECT
                MIN(CASE WHEN event_value = %s THEN occurred_at END) AS start_time,
                MAX(CASE WHEN event_value = %s THEN occurred_at END) AS end_time
            FROM sop_workflow_events
            WHERE sop_instance_id = %s AND event_type = 'status_change'
        """, (from_status, to_status, sop_instance_id))
        if not row or not row["start_time"] or not row["end_time"]:
            return None
        delta = row["end_time"] - row["start_time"]
        return round(delta.total_seconds() / 3600, 2)

    @staticmethod
    def get_kpis(sop_instance_id: int) -> list[dict]:
        rows = db.query("""
            SELECT kpi_code, value, unit, recorded_at
            FROM sop_kpi_records
            WHERE sop_instance_id = %s
            ORDER BY recorded_at
        """, (sop_instance_id,))
        return [dict(r) for r in rows]

    @staticmethod
    def avg_cycle_time(sop_number: str, kpi_code: str,
                       project_id: int | None = None) -> dict:
        """Company-wide average cycle time for a given SOP KPI."""
        params: list = [sop_number, kpi_code]
        where = ""
        if project_id:
            where = "AND si.project_id = %s"
            params.append(project_id)
        row = db.query_one(f"""
            SELECT
                COUNT(*)        AS sample_count,
                AVG(k.value)    AS avg_value,
                MIN(k.value)    AS min_value,
                MAX(k.value)    AS max_value
            FROM sop_kpi_records k
            JOIN sop_instances si ON si.id = k.sop_instance_id
            WHERE si.sop_number = %s AND k.kpi_code = %s {where}
        """, params)
        return dict(row) if row else {}

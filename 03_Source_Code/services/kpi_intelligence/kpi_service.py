"""KPI Intelligence Service — project and company KPI snapshots with threshold alerts."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))

from datetime import date
import services.db as db
from base import BaseIntelligenceService


class KPIIntelligenceService(BaseIntelligenceService):
    SERVICE_NAME = "kpi_intelligence"
    STATUS = "active"

    # Default thresholds — overridden by operating_rules if configured
    COMPANY_KPI_DEFAULTS = {
        "BID_WIN_RATE":        {"yellow": 25, "red": 15, "op": "<", "unit": "%"},
        "BID_MARGIN_AVG":      {"yellow": 7,  "red": 5,  "op": "<", "unit": "%"},
        "REVENUE_AT_RISK":     {"yellow": 10, "red": 20, "op": ">", "unit": "%"},
        "CO_REVENUE_PCT":      {"yellow": 6,  "red": 10, "op": ">", "unit": "%"},
        "CLOSEOUT_AVG_DAYS":   {"yellow": 30, "red": 60, "op": ">", "unit": "days"},
        "SUB_NONCOMPLIANCE":   {"yellow": 0,  "red": 2,  "op": ">", "unit": "count"},
        "MARGIN_VARIANCE":     {"yellow": 2,  "red": 4,  "op": ">", "unit": "%pts"},
        "ON_TIME_COMPLETION":  {"yellow": 85, "red": 70, "op": "<", "unit": "%"},
    }

    PROJECT_KPI_DEFAULTS = {
        "BUDGET_VAR_MAX":    {"yellow": 5,  "red": 10, "op": ">", "unit": "%"},
        "BUDGET_VAR_TOTAL":  {"yellow": 3,  "red": 7,  "op": ">", "unit": "%"},
        "SCHED_VAR_DAYS":    {"yellow": 3,  "red": 7,  "op": ">", "unit": "days"},
        "OPEN_RFI_AGE":      {"yellow": 10, "red": 14, "op": ">", "unit": "days"},
        "LOG_COMPLETION":    {"yellow": 95, "red": 85, "op": "<", "unit": "%"},
        "CO_PENDING_DAYS":   {"yellow": 7,  "red": 14, "op": ">", "unit": "days"},
        "PUNCH_OPEN_AGE":    {"yellow": 20, "red": 30, "op": ">", "unit": "days"},
        "SUB_COMPLIANCE":    {"yellow": 99, "red": 95, "op": "<", "unit": "%"},
    }

    @classmethod
    def _traffic_light(cls, value: float, config: dict) -> str:
        op = config["op"]
        yellow, red = config["yellow"], config["red"]
        if op == ">":
            if value > red:
                return "red"
            if value > yellow:
                return "yellow"
        elif op == "<":
            if value < red:
                return "red"
            if value < yellow:
                return "yellow"
        return "green"

    @classmethod
    def snapshot_project_kpi(cls, project_id: int, kpi_code: str,
                              value: float) -> dict:
        """Record a point-in-time project KPI value and compute status."""
        config = cls.PROJECT_KPI_DEFAULTS.get(kpi_code, {})
        status = cls._traffic_light(value, config) if config else "none"
        today = date.today().isoformat()
        cls.pg_execute("""
            INSERT INTO kpi_snapshots
                (kpi_code, scope, project_id, value, unit, period_start, period_end,
                 status, threshold_low, threshold_high, source_service)
            VALUES (%s, 'project', %s, %s, %s, %s, %s, %s, %s, %s, 'kpi_intelligence')
        """, (kpi_code, project_id, value, config.get("unit"),
              today, today, status,
              config.get("yellow"), config.get("red")))
        return {"kpi_code": kpi_code, "value": value, "status": status,
                "project_id": project_id}

    @classmethod
    def get_project_kpis(cls, project_id: int) -> dict:
        """Current KPI snapshot for one project — latest value per KPI code."""
        rows = cls.pg_query("""
            SELECT DISTINCT ON (kpi_code)
                kpi_code, value, unit, status, calculated_at
            FROM kpi_snapshots
            WHERE scope = 'project' AND project_id = %s
            ORDER BY kpi_code, calculated_at DESC
        """, (project_id,))
        kpis = [dict(r) for r in rows]
        traffic = "green"
        for k in kpis:
            if k["status"] == "red":
                traffic = "red"
                break
            elif k["status"] == "yellow":
                traffic = "yellow"
        return {"project_id": project_id, "overall_status": traffic, "kpis": kpis}

    @classmethod
    def get_alerts(cls, project_id: int | None = None) -> list[dict]:
        """All active KPI threshold breaches (yellow or red)."""
        params: list = ["yellow", "red"]
        where = "WHERE status IN (%s, %s)"
        if project_id:
            where += " AND project_id = %s"
            params.append(project_id)
        rows = cls.pg_query(f"""
            SELECT DISTINCT ON (kpi_code, project_id)
                kpi_code, scope, project_id, value, unit, status, calculated_at
            FROM kpi_snapshots {where}
            ORDER BY kpi_code, project_id, calculated_at DESC
        """, params)
        return [dict(r) for r in rows]

    @classmethod
    def get_trend(cls, kpi_code: str, project_id: int | None = None,
                  period_days: int = 90) -> list[dict]:
        params: list = [kpi_code, period_days]
        where = "WHERE kpi_code = %s AND calculated_at > NOW() - INTERVAL '%s days'"
        if project_id:
            where += " AND project_id = %s"
            params.append(project_id)
        rows = cls.pg_query(f"""
            SELECT value, unit, status, calculated_at
            FROM kpi_snapshots {where}
            ORDER BY calculated_at
        """, params)
        return [dict(r) for r in rows]

    @classmethod
    def executive_summary(cls) -> dict:
        """Top-level: all alerts + per-project traffic lights."""
        alerts = cls.get_alerts()
        rows = cls.pg_query(
            "SELECT DISTINCT id, name FROM projects WHERE id IN "
            "(SELECT DISTINCT project_id FROM kpi_snapshots WHERE project_id IS NOT NULL)"
        )
        projects_summary = []
        for p in rows:
            snap = cls.get_project_kpis(p["id"])
            projects_summary.append({
                "project_id": p["id"],
                "project_name": p["name"],
                "status": snap["overall_status"],
                "kpi_count": len(snap["kpis"]),
            })
        return {
            "alerts": alerts,
            "projects": projects_summary,
            "total_alerts": len(alerts),
            "red_alerts": sum(1 for a in alerts if a["status"] == "red"),
        }

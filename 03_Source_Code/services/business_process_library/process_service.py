"""Business Process Library Service — process registry and maturity tracking."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))

import json
import services.db as db
from base import BaseIntelligenceService


class BusinessProcessLibraryService(BaseIntelligenceService):
    SERVICE_NAME = "business_process_library"
    STATUS = "active"

    @classmethod
    def list_processes(cls, phase: str | None = None,
                       active_only: bool = True) -> list[dict]:
        conditions, params = [], []
        if active_only:
            conditions.append("active = TRUE")
        if phase:
            conditions.append("phase = %s")
            params.append(phase)
        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        rows = cls.pg_query(f"""
            SELECT process_code, process_name, phase, description,
                   related_sop_ids, related_workflows, kpi_codes,
                   owner_role, maturity_level, active
            FROM business_processes {where}
            ORDER BY phase, process_code
        """, params or None)
        return [dict(r) for r in rows]

    @classmethod
    def get_process(cls, process_code: str) -> dict | None:
        row = cls.pg_one(
            "SELECT * FROM business_processes WHERE process_code = %s",
            (process_code,)
        )
        return dict(row) if row else None

    @classmethod
    def maturity_summary(cls) -> dict:
        rows = cls.pg_query("""
            SELECT maturity_level, COUNT(*) AS count,
                   ARRAY_AGG(process_name) AS processes
            FROM business_processes
            WHERE active = TRUE
            GROUP BY maturity_level
            ORDER BY maturity_level
        """)
        levels = {
            0: "Ad Hoc", 1: "Defined", 2: "Executed",
            3: "Measured", 4: "Optimized"
        }
        summary = []
        for r in rows:
            summary.append({
                "level": r["maturity_level"],
                "level_name": levels.get(r["maturity_level"], "Unknown"),
                "count": r["count"],
                "processes": r["processes"],
            })
        return {"maturity_summary": summary}

    @classmethod
    def register_process(cls, process_code: str, process_name: str, phase: str,
                         description: str, trigger_event: str,
                         related_sop_ids: list | None = None,
                         related_workflows: list | None = None,
                         kpi_codes: list | None = None,
                         owner_role: str | None = None,
                         maturity_level: int = 0) -> dict:
        row = cls.pg_execute_returning("""
            INSERT INTO business_processes
                (process_code, process_name, phase, description, trigger_event,
                 related_sop_ids, related_workflows, kpi_codes, owner_role,
                 maturity_level)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (process_code) DO UPDATE SET
                process_name = EXCLUDED.process_name,
                description = EXCLUDED.description,
                maturity_level = EXCLUDED.maturity_level,
                updated_at = NOW()
            RETURNING id, process_code
        """, (process_code, process_name, phase, description, trigger_event,
              related_sop_ids, related_workflows, kpi_codes, owner_role,
              maturity_level))
        return dict(row)

    @classmethod
    def update_maturity(cls, process_code: str, maturity_level: int) -> dict:
        if not 0 <= maturity_level <= 4:
            return {"error": "maturity_level must be 0-4"}
        cls.pg_execute("""
            UPDATE business_processes SET maturity_level = %s, updated_at = NOW()
            WHERE process_code = %s
        """, (maturity_level, process_code))
        return {"process_code": process_code, "maturity_level": maturity_level}

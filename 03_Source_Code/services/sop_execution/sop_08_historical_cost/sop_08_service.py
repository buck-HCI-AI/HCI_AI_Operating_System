"""SOP 08 — Historical Cost Database: execution service (Layers 1+2)."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import services.db as db
from shared.base_sop import BaseSOP
from shared.sop_data_model import SOPStatus
from .sop_08_templates import REQUIRED_INPUT_KEYS, INPUT_LABELS, CostRecord, CostQueryResult
from .sop_08_agent import SOP08Agent


class SOP08HistoricalCostService(BaseSOP):
    SOP_NUMBER = "08"

    @classmethod
    def start_lookup(cls, project_id: int, trade_code: str,
                     work_description: str, project_type: str,
                     owner_name: str = "estimator") -> dict:
        """Create SOP 08 instance for a cost lookup. Can be standalone or from SOP 07."""
        instance = cls.create_instance(
            project_id=project_id,
            owner_name=owner_name,
            owner_role="estimator",
        )
        cls.confirm_input(instance["id"], "trade_code", trade_code)
        cls.confirm_input(instance["id"], "work_description", work_description)
        cls.confirm_input(instance["id"], "project_type", project_type)
        cls.transition_status(instance["id"], SOPStatus.IN_PROGRESS, owner_name,
                              "Historical cost lookup started")
        return {"instance": instance, "status": SOPStatus.IN_PROGRESS.value,
                "next_step": "Run lookup_cost() for unit costs or benchmark_sf() for $/SF."}

    @classmethod
    def lookup_cost(cls, instance_id: int, unit: str = "SF",
                    actor: str = "estimator") -> dict:
        """Query historical DB for unit cost data on the logged work item."""
        inp_rows = db.query("""
            SELECT input_key, confirmed_by FROM sop_inputs WHERE sop_instance_id = %s
        """, (instance_id,))
        inputs = {r["input_key"]: r["confirmed_by"] for r in inp_rows}

        trade_code = inputs.get("trade_code", "")
        work_description = inputs.get("work_description", "")
        project_type = inputs.get("project_type", "commercial")

        result = SOP08Agent.lookup_historical_cost(
            trade_code, work_description, project_type, unit
        )

        output_id = cls.save_output(
            instance_id, "cost_lookup", f"Cost Lookup — {trade_code}",
            content=result
        )
        cls._log_event(instance_id, "cost_lookup_run", trade_code, actor)

        cur = cls.get_instance(instance_id)
        if cur and cur["status"] == SOPStatus.IN_PROGRESS.value:
            cls.transition_status(instance_id, SOPStatus.AI_DRAFTED, "AI",
                                  "AI cost lookup complete")

        result["output_id"] = output_id
        return result

    @classmethod
    def benchmark_sf(cls, instance_id: int, gross_sf: float,
                     actor: str = "estimator") -> dict:
        """Get $/SF benchmark for the project type."""
        inp_rows = db.query("""
            SELECT confirmed_by FROM sop_inputs
            WHERE sop_instance_id = %s AND input_key = 'project_type'
        """, (instance_id,))
        project_type = inp_rows[0]["confirmed_by"] if inp_rows else "commercial"

        result = SOP08Agent.benchmark_cost_per_sf(project_type, gross_sf)
        cls.save_output(instance_id, "sf_benchmark",
                        f"$/SF Benchmark — {project_type}", content=result)
        cls._log_event(instance_id, "sf_benchmark_run", f"{gross_sf:,.0f} SF", actor)
        return result

    @classmethod
    def add_cost_record(cls, project_id: int, trade_code: str,
                        description: str, unit: str, unit_cost: float,
                        project_type: str, year: int,
                        source_project_id: int | None = None,
                        notes: str = "",
                        actor: str = "pm") -> dict:
        """Add a new historical cost record to the database."""
        record = CostRecord(
            trade_code=trade_code,
            description=description,
            unit=unit,
            unit_cost=unit_cost,
            project_type=project_type,
            year=year,
            source_project_id=source_project_id,
            notes=notes,
        )
        # Store in historical_costs table if it exists, else log as output
        try:
            db.execute("""
                INSERT INTO historical_costs
                    (project_id, trade_code, description, unit, unit_cost,
                     project_type, year, source, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (project_id, trade_code, description, unit, unit_cost,
                  project_type, year, "hci_historical", notes))
            return {"status": "saved", "trade_code": trade_code,
                    "unit_cost": unit_cost, "note": "Embed via ingestion pipeline for Qdrant search"}
        except Exception as e:
            return {"status": "error", "error": str(e),
                    "record": record.to_dict()}

    @classmethod
    def pm_confirm(cls, instance_id: int, pm_name: str,
                   recommended_unit_cost: float | None = None) -> dict:
        """PM confirms lookup result and optionally overrides the recommended unit cost."""
        if recommended_unit_cost is not None:
            cls.save_output(instance_id, "cost_confirmation",
                            "PM Confirmed Unit Cost",
                            content={"recommended_unit_cost": recommended_unit_cost,
                                     "confirmed_by": pm_name})
        cls.transition_status(instance_id, SOPStatus.APPROVED, pm_name,
                              "Cost lookup confirmed by PM")
        return {"status": SOPStatus.APPROVED.value,
                "confirmed_unit_cost": recommended_unit_cost}

    @classmethod
    def get_full_status(cls, instance_id: int) -> dict:
        instance = cls.get_instance(instance_id)
        if not instance:
            return {"error": "Instance not found"}
        rows = db.query(
            "SELECT output_type, output_label FROM sop_outputs WHERE sop_instance_id = %s",
            (instance_id,)
        )
        return {
            "instance": instance,
            "outputs": [dict(r) for r in rows],
            "audit_trail": cls.get_audit_trail(instance_id),
        }

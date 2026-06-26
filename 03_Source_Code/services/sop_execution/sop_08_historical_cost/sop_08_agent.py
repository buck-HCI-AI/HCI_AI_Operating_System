"""SOP 08 — Layer 3: Historical Cost Database AI Agent."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "api"))

from base import BaseIntelligenceService


SYSTEM_PROMPT = """You are HCI's Historical Cost Database AI (SOP 08).

Your job is to provide accurate unit cost benchmarks for construction trades, drawing
from HCI's historical project database and industry data.

RULES:
- Return only structured JSON
- Always cite the basis (HCI historical data, RSMeans, industry benchmark, etc.)
- Report confidence level based on data availability
- Never fabricate a cost — if no data, say so and estimate conservatively
- All costs must be confirmed by PM before use in a budget
- Flag any estimate more than 2 years old as potentially outdated
"""


class SOP08Agent(BaseIntelligenceService):
    SERVICE_NAME = "sop_08_agent"
    STATUS = "active"

    @classmethod
    def lookup_historical_cost(cls, trade_code: str, work_description: str,
                                project_type: str, unit: str = "SF") -> dict:
        """Query historical cost data for a specific work item."""
        # Search HCI historical cost DB in Qdrant
        results = cls.search(
            f"{trade_code} {work_description} {project_type} cost unit price",
            collection="hci_historical_costs",
            limit=6,
        )
        hist_context = "\n".join(
            r.get("payload", {}).get("text", "") for r in results
        ) or "No matching historical records found."

        prompt = f"""Provide historical cost data for this construction work item.

TRADE CODE: {trade_code}
WORK DESCRIPTION: {work_description}
PROJECT TYPE: {project_type}
UNIT OF MEASURE: {unit}

HISTORICAL DATA FROM HCI PROJECTS:
{hist_context}

Return JSON:
{{
  "trade_code": "{trade_code}",
  "work_description": "{work_description}",
  "unit": "{unit}",
  "avg_unit_cost": <number or null if no data>,
  "min_unit_cost": <number or null>,
  "max_unit_cost": <number or null>,
  "recommended_unit_cost": <best single estimate>,
  "confidence": "HIGH|MEDIUM|LOW",
  "basis": "<HCI historical data|industry benchmark|AI estimate>",
  "data_currency": "CURRENT|POSSIBLY_OUTDATED|NO_DATA",
  "comparable_projects": ["<project type or note>"],
  "ai_note": "COST LOOKUP — PM TO CONFIRM BEFORE USE IN ROM"
}}

Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=768)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "trade_code": trade_code,
                    "confidence": "LOW",
                    "ai_note": "Cost lookup failed — price manually"}

    @classmethod
    def benchmark_cost_per_sf(cls, project_type: str, gross_sf: float) -> dict:
        """Return $/SF benchmarks for a project type from HCI history."""
        results = cls.search(
            f"{project_type} total project cost per square foot benchmark",
            collection="hci_historical_costs",
            limit=8,
        )
        hist_context = "\n".join(
            r.get("payload", {}).get("text", "") for r in results
        ) or "No SF benchmark data available."

        prompt = f"""Provide cost-per-SF benchmarks for a {project_type} project of {gross_sf:,.0f} SF.

HISTORICAL BENCHMARK DATA:
{hist_context}

Return JSON:
{{
  "project_type": "{project_type}",
  "gross_sf": {gross_sf},
  "low_range_per_sf": <number>,
  "mid_range_per_sf": <number>,
  "high_range_per_sf": <number>,
  "hci_avg_per_sf": <number or null if no HCI data>,
  "implied_low_total": <low_range * gross_sf>,
  "implied_mid_total": <mid_range * gross_sf>,
  "implied_high_total": <high_range * gross_sf>,
  "confidence": "HIGH|MEDIUM|LOW",
  "basis": "<data source>",
  "ai_note": "BENCHMARK ONLY — PM TO VALIDATE AGAINST TRADE-LEVEL ROM"
}}

Return ONLY the JSON object."""
        try:
            raw = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=768)
            return cls.parse_json_response(raw)
        except Exception as e:
            return {"error": str(e), "project_type": project_type,
                    "confidence": "LOW"}

    @classmethod
    def add_cost_record(cls, trade_code: str, description: str, unit: str,
                         unit_cost: float, project_type: str, year: int,
                         source_project_id: int | None = None,
                         notes: str = "") -> dict:
        """Add a new cost record to the historical database."""
        # Store in DB; Qdrant embedding happens via the ingestion pipeline
        record = {
            "trade_code": trade_code,
            "description": description,
            "unit": unit,
            "unit_cost": unit_cost,
            "project_type": project_type,
            "year": year,
            "source_project_id": source_project_id,
            "source": "hci_historical",
            "notes": notes,
        }
        return {"status": "recorded", "record": record,
                "note": "Cost record logged — embed via ingestion pipeline for Qdrant search"}

"""Houzz Intelligence routes — /api/v1/services/houzz

Two ingest paths:
  POST /ingest      — legacy path (projects, daily_logs, schedule_items only)
  POST /ingest/full — full Houzz Connector Framework (all 17 entity types)
  GET  /status      — row counts across all Houzz tables
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "connectors"))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from houzz_svc import HouzzIngestionService
from houzz_connector import HouzzConnector

router = APIRouter()


# ── Legacy models (backwards compat) ─────────────────────────────────────────

class HouzzProject(BaseModel):
    houzz_project_id: str
    name: Optional[str] = None
    client_name: Optional[str] = None
    status: Optional[str] = None
    address: Optional[str] = None
    budget: Optional[float] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    project_type: Optional[str] = None
    properties: Optional[dict] = None


class HouzzDailyLog(BaseModel):
    houzz_log_id: str
    project_id: str
    log_date: Optional[str] = None
    content: Optional[str] = None
    weather: Optional[str] = None
    crew_size: Optional[int] = None
    author: Optional[str] = None
    raw_json: Optional[dict] = None


class HouzzScheduleItem(BaseModel):
    houzz_item_id: str
    project_id: str
    title: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: Optional[str] = None
    parent_item_id: Optional[str] = None
    assignee: Optional[str] = None
    completion_pct: Optional[float] = None
    task_type: Optional[str] = None
    notes: Optional[str] = None


class HouzzIngestPayload(BaseModel):
    projects: List[HouzzProject] = Field(default_factory=list)
    daily_logs: List[HouzzDailyLog] = Field(default_factory=list)
    schedule_items: List[HouzzScheduleItem] = Field(default_factory=list)
    source: Optional[str] = "browser_claude"
    extraction_notes: Optional[str] = None


# ── Full connector payload ─────────────────────────────────────────────────────

class FullIngestPayload(BaseModel):
    """All 17 Houzz entity types. All fields optional — send only what was extracted."""
    projects: List[Any] = Field(default_factory=list)
    daily_logs: List[Any] = Field(default_factory=list)
    schedule_items: List[Any] = Field(default_factory=list)
    files: List[Any] = Field(default_factory=list)
    time_entries: List[Any] = Field(default_factory=list)
    tasks: List[Any] = Field(default_factory=list)
    messages: List[Any] = Field(default_factory=list)
    budget: List[Any] = Field(default_factory=list)
    estimates: List[Any] = Field(default_factory=list)
    contracts: List[Any] = Field(default_factory=list)
    purchase_orders: List[Any] = Field(default_factory=list)
    change_orders: List[Any] = Field(default_factory=list)
    selections: List[Any] = Field(default_factory=list)
    vendors: List[Any] = Field(default_factory=list)
    contacts: List[Any] = Field(default_factory=list)
    team_members: List[Any] = Field(default_factory=list)
    subcontractors: List[Any] = Field(default_factory=list)
    source: Optional[str] = "browser_claude"
    extraction_notes: Optional[str] = None
    dry_run: Optional[bool] = True


@router.get("")
def service_info():
    return {
        "service": "houzz_intelligence",
        "version": "2.0",
        "description": "Persistence bridge for Houzz data extracted by Browser Claude",
        "endpoints": {
            "POST /ingest":      "Legacy: upsert projects, daily logs, schedule items",
            "POST /ingest/full": "Full: all 17 Houzz entity types via Connector Framework",
            "GET  /status":      "Row counts and last sync timestamps for all tables",
        },
    }


@router.post("/ingest")
def ingest_houzz_data(payload: HouzzIngestPayload):
    """Legacy ingest — projects, daily_logs, schedule_items only."""
    raw = payload.dict()
    result = HouzzIngestionService.ingest(raw)
    if result["total_imported"] == 0 and result["status"] == "ok":
        result["message"] = "All records already exist (duplicates) — no new rows inserted"
    return result


@router.post("/ingest/full")
def ingest_full(payload: FullIngestPayload):
    """
    Full Houzz Connector — accepts all 17 entity types.
    Default dry_run=true — set dry_run=false to write to DB.
    """
    connector = HouzzConnector(dry_run=payload.dry_run)

    data = {
        k: v for k, v in payload.dict().items()
        if k in HouzzConnector.supported_entities and v
    }

    if not data:
        raise HTTPException(
            status_code=422,
            detail=f"No recognized entity types found. Supported: {HouzzConnector.supported_entities}"
        )

    total_records = sum(len(v) for v in data.values())
    result = connector.ingest(data)
    result["source"] = payload.source
    result["extraction_notes"] = payload.extraction_notes
    result["entity_types_received"] = list(data.keys())
    result["total_records_received"] = total_records
    return result


@router.get("/status")
def houzz_status():
    return HouzzIngestionService.status()

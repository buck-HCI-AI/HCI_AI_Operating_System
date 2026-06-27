"""Houzz Intelligence routes — /api/v1/services/houzz"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from houzz_svc import HouzzIngestionService

router = APIRouter()


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


@router.get("")
def service_info():
    return {
        "service": "houzz_intelligence",
        "description": "Persistence bridge for Houzz data extracted by Browser Claude",
        "endpoints": {
            "POST /ingest": "Upsert projects, daily logs, and schedule items",
            "GET /status": "Row counts and last sync timestamps",
        },
    }


@router.post("/ingest")
def ingest_houzz_data(payload: HouzzIngestPayload):
    """
    Accepts structured Houzz data from Browser Claude and writes to houzz_* tables.
    All writes are idempotent via ON CONFLICT DO UPDATE.
    """
    raw = payload.dict()
    # Convert pydantic models to plain dicts for service layer
    raw["projects"] = [p for p in raw.get("projects", [])]
    raw["daily_logs"] = [l for l in raw.get("daily_logs", [])]
    raw["schedule_items"] = [s for s in raw.get("schedule_items", [])]

    result = HouzzIngestionService.ingest(raw)

    if result["total_imported"] == 0 and result["status"] == "ok":
        result["message"] = "All records already exist (duplicates) — no new rows inserted"

    return result


@router.get("/status")
def houzz_status():
    return HouzzIngestionService.status()

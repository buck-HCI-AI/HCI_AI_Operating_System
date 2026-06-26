import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from background_learning_service import BackgroundLearningService

router = APIRouter()


class DiscoverRequest(BaseModel):
    source_system: str
    source_id: str
    source_name: str
    source_url: Optional[str] = ""
    project_id: Optional[int] = None
    metadata: Optional[dict] = None


class AdvanceRequest(BaseModel):
    new_status: str
    updates: Optional[dict] = None


@router.get("")
def service_info():
    return {
        "service": "background-learning",
        "mode": "read_only",
        "statuses": BackgroundLearningService.__module__,
        "endpoints": {
            "GET  /summary":              "Record counts by status",
            "POST /discover":             "Register one source item",
            "POST /discover/all":         "Trigger full discovery (Drive + HubSpot + Houzz)",
            "POST /discover/hubspot":     "Discover from HubSpot deals",
            "POST /discover/drive":       "Discover from Drive sync log",
            "POST /discover/houzz":       "Discover from Houzz projects",
            "GET  /records":              "Query records (filter by status/source/project)",
            "POST /records/{id}/advance": "Advance record to next pipeline status",
            "POST /records/{id}/classify":"Auto-classify and extract intelligence candidates",
        }
    }


@router.get("/summary")
def get_summary():
    return BackgroundLearningService.summary()


@router.post("/discover")
def discover_one(req: DiscoverRequest):
    return BackgroundLearningService.discover(
        source_system=req.source_system,
        source_id=req.source_id,
        source_name=req.source_name,
        source_url=req.source_url or "",
        project_id=req.project_id,
        metadata=req.metadata,
    )


@router.post("/discover/all")
def discover_all():
    """Trigger read-only discovery across Drive, HubSpot, and Houzz."""
    return BackgroundLearningService.run_full_discovery()


@router.post("/discover/hubspot")
def discover_hubspot():
    return BackgroundLearningService.discover_from_hubspot()


@router.post("/discover/drive")
def discover_drive():
    return BackgroundLearningService.discover_from_drive()


@router.post("/discover/houzz")
def discover_houzz():
    return BackgroundLearningService.discover_from_houzz()


@router.get("/records")
def get_records(
    status: Optional[str] = None,
    source_system: Optional[str] = None,
    project_id: Optional[int] = None,
    review_status: Optional[str] = None,
    limit: int = Query(50, le=200),
):
    return {"records": BackgroundLearningService.get_records(
        status=status, source_system=source_system,
        project_id=project_id, review_status=review_status, limit=limit
    )}


@router.post("/records/{record_id}/advance")
def advance_record(record_id: int, req: AdvanceRequest):
    result = BackgroundLearningService.advance(record_id, req.new_status, req.updates)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


@router.post("/records/{record_id}/classify")
def classify_record(record_id: int):
    """Auto-classify document type, infer project, generate intelligence candidates."""
    result = BackgroundLearningService.extract_and_classify(record_id)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result

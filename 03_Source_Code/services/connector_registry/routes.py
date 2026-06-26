import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from connector_registry_service import ConnectorRegistryService

router = APIRouter()


class RegisterRequest(BaseModel):
    project_id: int
    project_code: str
    source_system: str
    source_reference: str
    notes: Optional[str] = ""


@router.get("")
def service_info():
    return {"service": "connector-registry", "description": "External source connections per project"}


@router.get("/summary")
def get_summary():
    return ConnectorRegistryService.summary()


@router.post("/register")
def register(req: RegisterRequest):
    result = ConnectorRegistryService.register(
        req.project_id, req.project_code, req.source_system,
        req.source_reference, req.notes or ""
    )
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


@router.post("/init-pilots")
def init_pilots():
    """Register all source connections for the 3 pilot projects (64EW, 101F, 1355R)."""
    return ConnectorRegistryService.initialize_pilot_projects()


@router.get("/connectors")
def get_connectors(project_id: Optional[int] = None, source_system: Optional[str] = None):
    return {"connectors": ConnectorRegistryService.get_connectors(project_id, source_system)}


@router.post("/connectors/{connector_id}/status")
def update_status(connector_id: int, status: str, record_count: Optional[int] = None):
    result = ConnectorRegistryService.update_status(connector_id, status, record_count)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result

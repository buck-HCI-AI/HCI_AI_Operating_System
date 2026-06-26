"""Business Process Library — FastAPI routes."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from process_service import BusinessProcessLibraryService

router = APIRouter()


class ProcessRegisterRequest(BaseModel):
    process_code: str
    process_name: str
    phase: str
    description: str
    trigger_event: str
    related_sop_ids: Optional[List[str]] = None
    related_workflows: Optional[List[str]] = None
    kpi_codes: Optional[List[str]] = None
    owner_role: Optional[str] = None
    maturity_level: int = 0


@router.get("")
def info():
    return BusinessProcessLibraryService.info()


@router.get("/processes")
def list_processes(phase: Optional[str] = None, active_only: bool = True):
    return {"processes": BusinessProcessLibraryService.list_processes(phase, active_only)}


@router.get("/processes/maturity")
def maturity_summary():
    return BusinessProcessLibraryService.maturity_summary()


@router.get("/processes/{process_code}")
def get_process(process_code: str):
    proc = BusinessProcessLibraryService.get_process(process_code)
    if not proc:
        raise HTTPException(404, f"Process {process_code} not found")
    return proc


@router.post("/processes")
def register_process(req: ProcessRegisterRequest):
    return BusinessProcessLibraryService.register_process(
        req.process_code, req.process_name, req.phase, req.description,
        req.trigger_event, req.related_sop_ids, req.related_workflows,
        req.kpi_codes, req.owner_role, req.maturity_level
    )


@router.patch("/processes/{process_code}/maturity")
def update_maturity(process_code: str, maturity_level: int):
    return BusinessProcessLibraryService.update_maturity(process_code, maturity_level)

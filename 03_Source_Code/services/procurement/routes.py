"""Procurement Intelligence routes — /api/v1/services/procurement"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter, Query
from typing import Optional
from procurement_svc import ProcurementService

router = APIRouter()

@router.get("")
def service_info():
    return ProcurementService.info()

@router.get("/long-lead")
def long_lead(project: Optional[str] = Query(default=None)):
    return ProcurementService.long_lead_items(project)

@router.get("/status")
def procurement_status(project: Optional[str] = Query(default=None)):
    return ProcurementService.procurement_status(project)

@router.get("/search")
def search(q: str):
    return ProcurementService.search(q)

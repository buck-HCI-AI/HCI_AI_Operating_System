"""KPI Intelligence Service — FastAPI routes."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastapi import APIRouter
from typing import Optional
from kpi_service import KPIIntelligenceService

router = APIRouter()


@router.get("")
def info():
    return KPIIntelligenceService.info()


@router.get("/company")
def company_summary():
    return KPIIntelligenceService.executive_summary()


@router.get("/alerts")
def alerts(project_id: Optional[int] = None):
    return {"alerts": KPIIntelligenceService.get_alerts(project_id)}


@router.get("/project/{project_id}")
def project_kpis(project_id: int):
    return KPIIntelligenceService.get_project_kpis(project_id)


@router.get("/trend")
def trend(kpi_code: str, project_id: Optional[int] = None, period_days: int = 90):
    return {"kpi_code": kpi_code,
            "data": KPIIntelligenceService.get_trend(kpi_code, project_id, period_days)}

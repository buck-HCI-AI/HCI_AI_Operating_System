"""Schedule Intelligence routes — /api/v1/services/schedule-intelligence"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter
from schedule_intelligence_svc import ScheduleIntelligenceService

router = APIRouter()

@router.get("")
def service_info():
    return ScheduleIntelligenceService.info()

@router.get("/variance/{project_number}")
def recent_variance(project_number: str, limit: int = 10):
    return ScheduleIntelligenceService.recent_variance(project_number, limit)

@router.post("/analyze/{log_id}")
def analyze_log(log_id: int):
    """Run schedule variance analysis on a submitted daily log."""
    return ScheduleIntelligenceService.analyze_log(log_id)

@router.get("/search")
def search(q: str):
    return ScheduleIntelligenceService.search(q)

@router.get("/{project_number}")
def project_schedule(project_number: str):
    return ScheduleIntelligenceService.project_schedule(project_number)

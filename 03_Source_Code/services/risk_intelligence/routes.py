"""Risk Intelligence routes — /api/v1/services/risk-intelligence"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter
from risk_intelligence_svc import RiskIntelligenceService

router = APIRouter()

@router.get("")
def service_info():
    return RiskIntelligenceService.info()

@router.get("/{project_number}")
def project_risks(project_number: str):
    return RiskIntelligenceService.project_risks(project_number)

@router.get("/search")
def search(q: str):
    return RiskIntelligenceService.search(q)

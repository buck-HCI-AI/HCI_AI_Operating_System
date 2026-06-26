"""Bid Intelligence API routes — /api/v1/services/bid-intelligence"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter, Query
from typing import Optional
from bid_intelligence_svc import BidIntelligenceService

router = APIRouter()

@router.get("")
def service_info():
    return BidIntelligenceService.info()

@router.get("/summary")
def bid_summary(project_number: Optional[str] = Query(default=None)):
    return BidIntelligenceService.summary(project_number)

@router.get("/leveling")
def bid_leveling(
    package: Optional[str]  = Query(default=None),
    project: Optional[str]  = Query(default=None),
):
    return BidIntelligenceService.leveling_analysis(package, project)

@router.get("/search")
def bid_search(q: str, project: Optional[str] = Query(default=None)):
    return BidIntelligenceService.search(q, project)

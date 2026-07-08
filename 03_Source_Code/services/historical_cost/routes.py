"""Historical Cost Intelligence routes — /api/v1/services/historical-cost"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter, Query
from typing import Optional
from historical_cost_svc import HistoricalCostService

router = APIRouter()

@router.get("")
def service_info():
    return HistoricalCostService.info()

@router.get("/benchmarks")
def benchmarks(csi_division: Optional[str] = None, scope_type: Optional[str] = None):
    return HistoricalCostService.cost_benchmarks(csi_division, scope_type)

@router.get("/benchmark-summary")
def benchmark_summary(csi_division: Optional[str] = None, scope_type: Optional[str] = None):
    return HistoricalCostService.cost_benchmark_summary(csi_division, scope_type)

@router.get("/bid-vs-actual/{project_number}")
def bid_vs_actual(project_number: str):
    return HistoricalCostService.bid_vs_actual(project_number)

@router.get("/search")
def search(q: str):
    return HistoricalCostService.search(q)

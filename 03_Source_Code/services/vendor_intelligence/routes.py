"""Vendor Intelligence routes — /api/v1/services/vendor-intelligence"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter, Query
from typing import Optional
from vendor_intelligence_svc import VendorIntelligenceService

router = APIRouter()

@router.get("")
def service_info():
    return VendorIntelligenceService.info()

@router.get("/vendors")
def list_vendors(csi_division: Optional[str] = None, status: Optional[str] = None):
    return VendorIntelligenceService.list_vendors(csi_division, status)

@router.get("/vendors/{vendor_id}")
def vendor_performance(vendor_id: int):
    return VendorIntelligenceService.vendor_performance(vendor_id)

@router.get("/search")
def search_vendors(q: str):
    return VendorIntelligenceService.search_vendors(q)

@router.get("/reliable")
def most_reliable(csi_division: Optional[str] = None, trade: Optional[str] = None, limit: int = 15):
    return VendorIntelligenceService.most_reliable(csi_division, trade, limit)

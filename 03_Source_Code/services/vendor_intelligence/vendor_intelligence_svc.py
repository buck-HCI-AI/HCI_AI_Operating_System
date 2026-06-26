"""Vendor Intelligence Service — performance, coverage, risk, and search."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from base import BaseIntelligenceService


class VendorIntelligenceService(BaseIntelligenceService):
    SERVICE_NAME = "vendor_intelligence"
    STATUS = "active"

    @staticmethod
    def list_vendors(csi_division: str = None, status: str = None) -> dict:
        conditions, params = [], []
        if csi_division:
            conditions.append("%s = ANY(csi_divisions)")
            params.append(csi_division)
        if status:
            conditions.append("preferred_status = %s")
            params.append(status)
        where = "WHERE " + " AND ".join(conditions) if conditions else ""
        rows = VendorIntelligenceService.pg_query(
            f"SELECT * FROM vendors {where} ORDER BY company_name", params or None
        )
        return {"vendors": rows, "total": len(rows)}

    @staticmethod
    def vendor_performance(vendor_id: int) -> dict:
        vendor = VendorIntelligenceService.pg_one("SELECT * FROM vendors WHERE id = %s", (vendor_id,))
        if not vendor:
            return {"error": f"Vendor {vendor_id} not found"}
        bids = VendorIntelligenceService.pg_query("""
            SELECT be.bid_amount, be.status, be.date_received,
                   bp.package_name, bp.csi_division, p.name as project_name
            FROM bid_entries be
            JOIN bid_packages bp ON bp.id = be.bid_package_id
            JOIN projects p ON p.id = be.project_id
            WHERE be.vendor_id = %s
            ORDER BY be.date_received DESC
        """, (vendor_id,))
        return {"vendor": vendor, "bid_history": bids, "total_bids": len(bids)}

    @staticmethod
    def search_vendors(query: str) -> dict:
        results = BaseIntelligenceService.search(query, collection="vendor_memory", limit=10)
        return {"query": query, "results": results}

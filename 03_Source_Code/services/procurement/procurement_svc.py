"""Procurement Intelligence Service — long leads, purchase orders, material tracking."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from base import BaseIntelligenceService


class ProcurementService(BaseIntelligenceService):
    SERVICE_NAME = "procurement"
    STATUS = "active"

    @staticmethod
    def long_lead_items(project_number: str = None) -> dict:
        """Items with long lead times requiring early procurement."""
        where, params = "", None
        if project_number:
            pid = ProcurementService.resolve_project_id(project_number)
            if pid:
                where  = "WHERE lli.project_id = %s"
                params = (pid,)
        rows = ProcurementService.pg_query(f"""
            SELECT lli.*, p.name as project_name
            FROM long_lead_items lli
            JOIN projects p ON p.id = lli.project_id
            {where}
            ORDER BY lli.required_on_site_date
        """, params)
        return {"long_lead_items": [dict(r) for r in rows], "total": len(rows)}

    @staticmethod
    def procurement_status(project_number: str = None) -> dict:
        """Overview of procurement items by status."""
        where, params = "", None
        if project_number:
            pid = ProcurementService.resolve_project_id(project_number)
            if pid:
                where  = "WHERE pi.project_id = %s"
                params = (pid,)
        rows = ProcurementService.pg_query(f"""
            SELECT pi.*, p.name as project_name
            FROM procurement_items pi
            JOIN projects p ON p.id = pi.project_id
            {where}
            ORDER BY pi.required_date
        """, params)
        return {"procurement_items": [dict(r) for r in rows], "total": len(rows)}

    @staticmethod
    def search(query: str) -> dict:
        results = BaseIntelligenceService.search(query, collection="hci_procurement", limit=8)
        return {"query": query, "results": results}

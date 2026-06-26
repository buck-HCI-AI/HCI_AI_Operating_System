"""Bid Intelligence Service — analysis across all bids, packages, and leveling."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from base import BaseIntelligenceService


class BidIntelligenceService(BaseIntelligenceService):
    SERVICE_NAME = "bid_intelligence"
    STATUS = "active"

    @staticmethod
    def summary(project_number: str = None) -> dict:
        where, params = "", None
        if project_number:
            pid = BidIntelligenceService.resolve_project_id(project_number)
            if pid:
                where  = "WHERE be.project_id = %s"
                params = (pid,)
            else:
                return {"packages": [], "total_packages": 0, "error": f"Project {project_number} not found"}
        rows = BidIntelligenceService.pg_query(f"""
            SELECT bp.package_name, bp.csi_division,
                   COUNT(be.id)       AS bid_count,
                   MIN(be.bid_amount) AS low_bid,
                   MAX(be.bid_amount) AS high_bid,
                   AVG(be.bid_amount) AS avg_bid
            FROM bid_packages bp
            JOIN bid_entries be ON be.bid_package_id = bp.id
            {where}
            GROUP BY bp.id, bp.package_name, bp.csi_division
            ORDER BY bp.csi_division NULLS LAST, bp.package_name
        """, params)
        return {"packages": [dict(r) for r in rows], "total_packages": len(rows)}

    @staticmethod
    def leveling_analysis(package_name: str = None, project_number: str = None) -> dict:
        """Return bid spread analysis per package."""
        conditions, params = [], []
        if package_name:
            conditions.append("bp.package_name ILIKE %s")
            params.append(f"%{package_name}%")
        if project_number:
            pid = BidIntelligenceService.resolve_project_id(project_number)
            if pid:
                conditions.append("be.project_id = %s")
                params.append(pid)
        where = "WHERE " + " AND ".join(conditions) if conditions else ""

        rows = BidIntelligenceService.pg_query(f"""
            SELECT bp.package_name, bp.csi_division,
                   v.company_name, be.bid_amount, be.status,
                   be.date_received, be.notes,
                   be.bid_amount - MIN(be.bid_amount) OVER (PARTITION BY bp.id) AS vs_low,
                   ROUND(
                     (be.bid_amount - MIN(be.bid_amount) OVER (PARTITION BY bp.id))
                     / NULLIF(MIN(be.bid_amount) OVER (PARTITION BY bp.id), 0) * 100, 1
                   ) AS pct_over_low
            FROM bid_entries be
            JOIN bid_packages bp ON bp.id = be.bid_package_id
            LEFT JOIN vendors v ON v.id = be.vendor_id
            {where}
            ORDER BY bp.package_name, be.bid_amount
        """, params or None)
        return {"analysis": [dict(r) for r in rows]}

    @staticmethod
    def search(question: str, project_number: str = None) -> dict:
        results = BaseIntelligenceService.search(
            question, collection="bid_memory", limit=8, project_filter=project_number)
        return {"question": question, "results": results}

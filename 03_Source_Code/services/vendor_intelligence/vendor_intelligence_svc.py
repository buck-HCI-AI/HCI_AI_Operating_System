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

    @staticmethod
    def most_reliable(csi_division: str = None, trade: str = None, limit: int = 15) -> dict:
        """Real answer to 'who is the most reliable sub for this type of job'.
        vendor_performance_scores only covers 31 of 1,256 vendors and is mostly
        placeholder ('not yet contacted') as of 2026-07-08 — not a usable signal
        alone. This ranks on what's actually populated at scale: win_rate_pct and
        bid_count from vendors, plus real on-budget performance pulled from
        historical_cost_records via the bid_packages award link, where it exists."""
        conditions, params = ["v.bid_count > 0"], []
        if csi_division:
            conditions.append("%s = ANY(v.csi_divisions)")
            params.append(csi_division)
        if trade:
            conditions.append("LOWER(v.trade) LIKE LOWER(%s)")
            params.append(f"%{trade}%")
        where = "WHERE " + " AND ".join(conditions)
        rows = VendorIntelligenceService.pg_query(f"""
            SELECT v.id, v.company_name, v.trade, v.csi_divisions, v.tier,
                   v.bid_count, v.win_rate_pct, v.avg_bid_amount, v.last_bid_date,
                   vps.score as performance_score, vps.grade as performance_grade,
                   awarded.awarded_count,
                   round(hist.avg_variance_pct::numeric, 2) as avg_cost_variance_pct,
                   hist.jobs_with_variance
            FROM vendors v
            LEFT JOIN vendor_performance_scores vps ON vps.vendor_id = v.id
            LEFT JOIN (
                SELECT awarded_vendor_id, count(*) as awarded_count
                FROM bid_packages WHERE awarded_vendor_id IS NOT NULL
                GROUP BY awarded_vendor_id
            ) awarded ON awarded.awarded_vendor_id = v.id
            LEFT JOIN (
                SELECT bp.awarded_vendor_id,
                       avg(hcr.variance_pct) as avg_variance_pct,
                       count(*) as jobs_with_variance
                FROM historical_cost_records hcr
                JOIN bid_packages bp ON bp.id = hcr.bid_package_id
                WHERE bp.awarded_vendor_id IS NOT NULL AND hcr.variance_pct IS NOT NULL
                GROUP BY bp.awarded_vendor_id
            ) hist ON hist.awarded_vendor_id = v.id
            {where}
            ORDER BY
                (COALESCE(v.win_rate_pct, 0) * 0.5
                 + LEAST(COALESCE(awarded.awarded_count, 0), 10) * 5
                 - COALESCE(ABS(hist.avg_variance_pct), 0) * 2) DESC,
                v.bid_count DESC
            LIMIT %s
        """, params + [limit])
        return {
            "filter": {"csi_division": csi_division, "trade": trade},
            "ranked_vendors": [dict(r) for r in rows],
            "ranking_basis": "win_rate_pct + awarded-job count - |cost variance %| where known; vendor_performance_scores shown for reference but not weighted (only 31/1256 vendors scored, mostly placeholder)",
        }

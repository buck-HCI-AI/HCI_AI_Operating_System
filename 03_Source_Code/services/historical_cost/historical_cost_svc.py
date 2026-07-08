"""Historical Cost Intelligence — cost benchmarking across all completed projects."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from base import BaseIntelligenceService


class HistoricalCostService(BaseIntelligenceService):
    SERVICE_NAME = "historical_cost"
    STATUS = "active"

    @staticmethod
    def cost_benchmarks(csi_division: str = None, scope_type: str = None) -> dict:
        conditions, params = [], []
        if csi_division:
            conditions.append("csi_division = %s")
            params.append(csi_division)
        if scope_type:
            conditions.append("(LOWER(scope_description) LIKE LOWER(%s) OR LOWER(notes) LIKE LOWER(%s))")
            params += [f"%{scope_type}%", f"%{scope_type}%"]
        where = "WHERE " + " AND ".join(conditions) if conditions else ""
        rows = HistoricalCostService.pg_query(f"""
            SELECT hcr.*, p.name as project_name
            FROM historical_cost_records hcr
            LEFT JOIN projects p ON p.id = hcr.project_id
            {where}
            ORDER BY hcr.csi_division, hcr.completed_date DESC
        """, params or None)
        return {"records": [dict(r) for r in rows], "total": len(rows)}

    @staticmethod
    def cost_benchmark_summary(csi_division: str = None, scope_type: str = None) -> dict:
        """Real answer to 'what does a similar build cost' — aggregated stats per
        CSI division, not a raw record dump. No square-footage column exists
        anywhere in the schema (projects, houzz_projects) as of 2026-07-08, so this
        benchmarks by division + scope keyword match, the best real proxy available
        — not fabricated $/sqft."""
        conditions, params = ["hcr.awarded_amount IS NOT NULL"], []
        if csi_division:
            conditions.append("hcr.csi_division = %s")
            params.append(csi_division)
        if scope_type:
            conditions.append("(LOWER(hcr.scope_description) LIKE LOWER(%s) OR LOWER(hcr.notes) LIKE LOWER(%s))")
            params += [f"%{scope_type}%", f"%{scope_type}%"]
        where = "WHERE " + " AND ".join(conditions)
        groups = HistoricalCostService.pg_query(f"""
            SELECT hcr.csi_division,
                   count(*) as sample_size,
                   round(avg(hcr.awarded_amount)::numeric, 0) as avg_awarded,
                   round((percentile_cont(0.5) WITHIN GROUP (ORDER BY hcr.awarded_amount))::numeric, 0) as median_awarded,
                   round(min(hcr.awarded_amount)::numeric, 0) as min_awarded,
                   round(max(hcr.awarded_amount)::numeric, 0) as max_awarded,
                   round(avg(hcr.variance_pct) FILTER (WHERE hcr.variance_pct IS NOT NULL)::numeric, 2) as avg_variance_pct,
                   count(*) FILTER (WHERE hcr.variance_pct IS NOT NULL) as variance_sample_size
            FROM historical_cost_records hcr
            {where}
            GROUP BY hcr.csi_division
            ORDER BY sample_size DESC
        """, params or None)
        examples = HistoricalCostService.pg_query(f"""
            SELECT hcr.csi_division, hcr.awarded_amount, hcr.scope_description, hcr.notes,
                   p.name as project_name, hcr.completed_date, hcr.source
            FROM historical_cost_records hcr
            LEFT JOIN projects p ON p.id = hcr.project_id
            {where}
            ORDER BY hcr.completed_date DESC NULLS LAST
            LIMIT 10
        """, params or None)
        return {
            "filter": {"csi_division": csi_division, "scope_keyword": scope_type},
            "by_division": [dict(r) for r in groups],
            "example_records": [dict(r) for r in examples],
            "known_limitation": "No square-footage field exists in the schema yet — benchmark is by CSI division + scope keyword, not $/sqft.",
        }

    @staticmethod
    def bid_vs_actual(project_number: str) -> dict:
        """Compare winning bids to actual costs for a project."""
        pid = HistoricalCostService.resolve_project_id(project_number)
        if not pid:
            return {"error": f"Project {project_number} not found"}
        awarded = HistoricalCostService.pg_query("""
            SELECT bp.package_name, bp.csi_division,
                   be.bid_amount as awarded_amount, v.company_name as vendor,
                   hcr.final_cost, hcr.variance_pct
            FROM bid_entries be
            JOIN bid_packages bp ON bp.id = be.bid_package_id
            LEFT JOIN vendors v ON v.id = be.vendor_id
            LEFT JOIN historical_cost_records hcr
                   ON hcr.bid_package_id = bp.id AND hcr.project_id = %s
            WHERE be.project_id = %s AND be.status = 'awarded'
            ORDER BY bp.csi_division
        """, (pid, pid))
        return {"project_number": project_number, "awarded_bids": [dict(r) for r in awarded]}

    @staticmethod
    def search(query: str) -> dict:
        results = BaseIntelligenceService.search(query, collection="hci_historical_costs", limit=8)
        if not results:
            terms = [f"%{t}%" for t in query.split() if t]
            if terms:
                conditions = " OR ".join(
                    ["LOWER(csi_division) LIKE LOWER(%s)",
                     "LOWER(notes) LIKE LOWER(%s)"] * len(terms)
                )
                params = []
                for t in terms:
                    params += [f"%{t}%", f"%{t}%"]
                rows = HistoricalCostService.pg_query(f"""
                    SELECT id, csi_division, awarded_amount, final_cost,
                           variance_pct, notes, completed_date
                    FROM historical_cost_records
                    WHERE {conditions}
                    ORDER BY csi_division
                    LIMIT 20
                """, params)
                results = [dict(r) for r in rows]
        return {"query": query, "results": results}

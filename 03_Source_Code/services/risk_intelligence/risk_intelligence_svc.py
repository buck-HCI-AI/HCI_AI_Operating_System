"""Risk Intelligence Service — project risks, flags, and mitigation tracking."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from base import BaseIntelligenceService


class RiskIntelligenceService(BaseIntelligenceService):
    SERVICE_NAME = "risk_intelligence"
    STATUS = "active"

    @staticmethod
    def project_risks(project_number: str) -> dict:
        pid = RiskIntelligenceService.resolve_project_id(project_number)
        project = {"id": pid} if pid else None
        if not project:
            return {"error": f"Project {project_number} not found"}
        risks_table = RiskIntelligenceService.pg_one(
            "SELECT 1 FROM pg_tables WHERE tablename='risks'")
        if not risks_table:
            # Derive risks from available data signals
            return RiskIntelligenceService._derive_risks(project_number, project["id"])
        rows = RiskIntelligenceService.pg_query(
            "SELECT * FROM risks WHERE project_id = %s ORDER BY severity DESC", (project["id"],))
        return {"project_number": project_number, "risks": rows}

    @staticmethod
    def _derive_risks(project_number: str, project_id: int) -> dict:
        """Infer risks from bid data, missing subs, and schedule gaps."""
        risks = []
        # Packages with < 2 bids = coverage risk
        sparse = RiskIntelligenceService.pg_query("""
            SELECT bp.package_name, bp.csi_division, COUNT(be.id) as bid_count
            FROM bid_packages bp
            LEFT JOIN bid_entries be ON be.bid_package_id = bp.id
            WHERE bp.project_id = %s
            GROUP BY bp.id, bp.package_name, bp.csi_division
            HAVING COUNT(be.id) < 2
        """, (project_id,))
        for p in sparse:
            risks.append({
                "type": "coverage",
                "severity": "medium",
                "description": f"{p['package_name']} has only {p['bid_count']} bid(s) — limited competition",
                "source": "bid_analysis"
            })
        return {"project_number": project_number, "derived_risks": risks,
                "note": "Full risk tracking available after applying new UUID schema"}

    @staticmethod
    def search(query: str) -> dict:
        results = BaseIntelligenceService.search(query, collection="drive_memory", limit=8)
        return {"query": query, "results": results}

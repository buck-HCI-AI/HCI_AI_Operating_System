"""
Project Brain API routes.
Mounted at /api/v1/services/project-brain
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter, HTTPException
from models import ProjectQuery
from service import ProjectBrainService
from intelligence import ProjectIntelligenceEngine

router = APIRouter()


@router.get("")
def service_info():
    return ProjectBrainService.info()


@router.get("/{project_number}")
def project_snapshot(project_number: str):
    """
    Full intelligence snapshot for a project.
    Returns: project metadata, all bid packages, recent meetings/logs, vector counts.
    Cached 30 minutes. Pass ?refresh=true to force rebuild.
    """
    svc = ProjectBrainService(project_number)
    result = svc.snapshot()
    if "error" in result:
        raise HTTPException(404, detail=result)
    return result


@router.post("/{project_number}/refresh")
def refresh_snapshot(project_number: str):
    """Force-rebuild the project intelligence snapshot (clears Redis cache)."""
    svc = ProjectBrainService(project_number)
    result = svc.snapshot(force_refresh=True)
    if "error" in result:
        raise HTTPException(404, detail=result)
    return {"status": "refreshed", "snapshot": result}


@router.post("/{project_number}/query")
def query_project(project_number: str, req: ProjectQuery):
    """
    Ask any question about the project. Returns a Claude-synthesized answer
    grounded in all project documents, bids, meetings, and structured data.

    Example questions:
    - "What is the current framing budget?"
    - "Who are the top 3 bidders for electrical?"
    - "What were the main issues in last week's site meeting?"
    - "What are the long lead items for this project?"
    """
    svc = ProjectBrainService(project_number)
    if not svc._get_project_row():
        raise HTTPException(404, f"Project '{project_number}' not found")
    return svc.query(
        question=req.question,
        context_hint=req.context_hint,
        max_sources=req.max_sources,
    )


@router.get("/{project_number}/bids")
def project_bids(project_number: str):
    """All bid packages and entries for the project."""
    svc = ProjectBrainService(project_number)
    project = svc._get_project_row()
    if not project:
        raise HTTPException(404, f"Project '{project_number}' not found")

    rows = svc.pg_query("""
        SELECT bp.package_name, bp.csi_division, bp.scope_description,
               be.id as bid_id, v.company_name as vendor,
               be.bid_amount, be.status, be.date_received, be.notes
        FROM bid_packages bp
        LEFT JOIN bid_entries be ON be.bid_package_id = bp.id
        LEFT JOIN vendors v ON v.id = be.vendor_id
        WHERE bp.project_id = %s
        ORDER BY bp.csi_division, bp.package_name, be.bid_amount
    """, (project["id"],))
    return {"project_number": project_number, "bids": rows}


@router.get("/{project_number}/activity")
def project_activity(project_number: str):
    """Recent activity: meetings, daily logs, HubSpot notes."""
    svc = ProjectBrainService(project_number)
    project = svc._get_project_row()
    if not project:
        raise HTTPException(404, f"Project '{project_number}' not found")

    pid = project["id"]
    meetings   = svc.pg_query(
        "SELECT * FROM meetings WHERE project_id=%s ORDER BY meeting_date DESC LIMIT 10", (pid,))
    daily_logs = svc.pg_query(
        "SELECT * FROM daily_logs WHERE project_id=%s ORDER BY log_date DESC LIMIT 10", (pid,))

    return {
        "project_number": project_number,
        "meetings":       meetings,
        "daily_logs":     daily_logs,
    }


@router.get("/{project_number}/vendors")
def project_vendors(project_number: str):
    """All vendors who have submitted bids on this project."""
    svc = ProjectBrainService(project_number)
    project = svc._get_project_row()
    if not project:
        raise HTTPException(404, f"Project '{project_number}' not found")

    rows = svc.pg_query("""
        SELECT DISTINCT v.company_name, v.contact_name, v.email, v.phone,
                        v.csi_divisions, v.preferred_status,
                        COUNT(be.id) as bids_submitted
        FROM vendors v
        JOIN bid_entries be ON be.vendor_id = v.id
        WHERE be.project_id = %s
        GROUP BY v.id, v.company_name, v.contact_name, v.email, v.phone,
                 v.csi_divisions, v.preferred_status
        ORDER BY bids_submitted DESC
    """, (project["id"],))
    return {"project_number": project_number, "vendors": rows}


# ── Phase 2: Intelligence Endpoints ───────────────────────────────────────────

@router.get("/{project_id}/intelligence")
def project_intelligence(project_id: int, ai_summary: bool = True):
    """
    Full Phase 2 intelligence snapshot — health, risks, decisions, open questions,
    missing information, AI summary, and recommended next actions.
    """
    engine = ProjectIntelligenceEngine(project_id)
    result = engine.intelligence(include_ai_summary=ai_summary)
    if "error" in result:
        raise HTTPException(404, detail=result["error"])
    return result


@router.get("/{project_id}/health")
def project_health(project_id: int):
    """Lightweight health check — RED/YELLOW/GREEN with factors. No AI call."""
    engine = ProjectIntelligenceEngine(project_id)
    return engine.health()


@router.get("/{project_id}/risks")
def project_risks(project_id: int):
    """Auto-detected risks from all available data sources."""
    engine = ProjectIntelligenceEngine(project_id)
    risks = engine.detect_risks()
    return {
        "project_id": project_id,
        "risk_count": len(risks),
        "critical": len([r for r in risks if r["severity"] == "critical"]),
        "high": len([r for r in risks if r["severity"] == "high"]),
        "medium": len([r for r in risks if r["severity"] == "medium"]),
        "low": len([r for r in risks if r["severity"] == "low"]),
        "risks": risks,
    }


@router.get("/{project_id}/summary")
def project_summary(project_id: int):
    """AI-generated narrative summary of project current state + recommended actions."""
    engine = ProjectIntelligenceEngine(project_id)
    return engine.summary()


@router.get("/{project_id}/health-history")
def project_health_history(project_id: int, days: int = 30):
    """Health score history for trending (last N days)."""
    from service import ProjectBrainService
    svc = ProjectBrainService(str(project_id))
    rows = svc.pg_query("""
        SELECT snapshot_date, health, risk_count, open_decisions, open_bids,
               data_completeness_pct, health_factors
        FROM project_brain_snapshots
        WHERE project_id = %s AND snapshot_date >= CURRENT_DATE - %s::interval
        ORDER BY snapshot_date DESC
    """, (project_id, f"{days} days"))
    return {"project_id": project_id, "days": days, "history": [dict(r) for r in rows]}

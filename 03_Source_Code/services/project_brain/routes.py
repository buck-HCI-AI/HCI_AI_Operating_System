"""
Project Brain API routes.
Mounted at /api/v1/services/project-brain
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter, HTTPException
from models import ProjectQuery, EventCreate, DocumentLinkCreate
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
    import json as _json
    svc = ProjectBrainService(project_number)
    project = svc._get_project_row()
    if not project:
        raise HTTPException(404, f"Project '{project_number}' not found")
    result = svc.query(
        question=req.question,
        context_hint=req.context_hint,
        max_sources=req.max_sources,
    )
    # Log to conversation memory (non-blocking — skip if table missing)
    if not result.get("cached"):
        try:
            sources_json = _json.dumps(result.get("sources", []))
            answer_text = result.get("answer", "")
            svc.pg_one("""
                INSERT INTO project_ai_conversations
                    (project_id, question, answer_summary, full_answer, context_used, model_used)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (project["id"], req.question, answer_text[:500], answer_text,
                  sources_json, result.get("model_used", "claude-haiku-4-5-20251001")))
        except Exception:
            pass
    return result


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


# ── Phase 3: Extended Memory Endpoints ────────────────────────────────────────

@router.get("/{project_id}/timeline")
def project_timeline(project_id: int, days: int = 90, event_type: str = None):
    """Chronological event timeline for the project (milestones, risks, decisions, changes)."""
    svc = ProjectBrainService(str(project_id))
    params = [project_id, f"{days} days"]
    type_filter = ""
    if event_type:
        type_filter = " AND event_type = %s"
        params.append(event_type)
    rows = svc.pg_query(f"""
        SELECT id, event_type, event_date, title, description,
               source_table, source_id, created_by, metadata, created_at
        FROM project_events
        WHERE project_id = %s
          AND event_date >= CURRENT_DATE - %s::interval
          {type_filter}
        ORDER BY event_date DESC, created_at DESC
    """, tuple(params))
    return {
        "project_id": project_id,
        "days": days,
        "event_count": len(rows),
        "events": [dict(r) for r in rows],
    }


@router.post("/{project_id}/events")
def log_event(project_id: int, req: EventCreate):
    """Log a project event to the timeline."""
    svc = ProjectBrainService(str(project_id))
    import json as _json
    from datetime import date as _date
    event_date = req.event_date or str(_date.today())
    metadata = _json.dumps(req.metadata or {})
    row = svc.pg_one("""
        INSERT INTO project_events
            (project_id, event_type, event_date, title, description,
             source_table, source_id, created_by, metadata)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        RETURNING id, event_type, event_date, title, created_at
    """, (project_id, req.event_type, event_date, req.title, req.description,
          req.source_table, req.source_id, req.created_by, metadata))
    return {"logged": True, "event": dict(row) if row else {}}


@router.get("/{project_id}/conversations")
def project_conversations(project_id: int, limit: int = 20):
    """Recent AI interaction history for this project."""
    svc = ProjectBrainService(str(project_id))
    rows = svc.pg_query("""
        SELECT id, session_id, question, answer_summary, context_used,
               tokens_used, model_used, queried_at
        FROM project_ai_conversations
        WHERE project_id = %s
        ORDER BY queried_at DESC
        LIMIT %s
    """, (project_id, limit))
    return {
        "project_id": project_id,
        "conversation_count": len(rows),
        "conversations": [dict(r) for r in rows],
    }


@router.get("/{project_id}/document-links")
def project_document_links(project_id: int, entity_type: str = None):
    """Document relationships — which documents drove which decisions/risks/changes."""
    svc = ProjectBrainService(str(project_id))
    params = [project_id]
    entity_filter = ""
    if entity_type:
        entity_filter = " AND linked_entity_type = %s"
        params.append(entity_type)
    rows = svc.pg_query(f"""
        SELECT id, document_type, document_id, document_name, document_date,
               linked_entity_type, linked_entity_id, linked_entity_name,
               relationship, notes, linked_at, created_by
        FROM project_document_links
        WHERE project_id = %s {entity_filter}
        ORDER BY linked_at DESC
    """, tuple(params))
    return {
        "project_id": project_id,
        "link_count": len(rows),
        "document_links": [dict(r) for r in rows],
    }


@router.post("/{project_id}/document-links")
def create_document_link(project_id: int, req: DocumentLinkCreate):
    """Link a document to a decision, risk, change order, or other entity."""
    svc = ProjectBrainService(str(project_id))
    row = svc.pg_one("""
        INSERT INTO project_document_links
            (project_id, document_type, document_id, document_name, document_date,
             linked_entity_type, linked_entity_id, linked_entity_name,
             relationship, notes, created_by)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        RETURNING id, document_name, linked_entity_type, relationship, linked_at
    """, (project_id, req.document_type, req.document_id, req.document_name,
          req.document_date, req.linked_entity_type, req.linked_entity_id,
          req.linked_entity_name, req.relationship, req.notes, req.created_by))
    return {"linked": True, "link": dict(row) if row else {}}


@router.get("/{project_id}/daily-summary")
def project_daily_summary(project_id: int, force_refresh: bool = False):
    """
    Daily AI-generated project summary. Returns today's cached summary if available.
    Pass ?force_refresh=true to regenerate. Stored in project_daily_summaries table.
    """
    import json as _json
    from datetime import date as _date

    svc = ProjectBrainService(str(project_id))

    # Return cached summary if available and not forcing refresh
    if not force_refresh:
        cached = svc.pg_one("""
            SELECT * FROM project_daily_summaries
            WHERE project_id = %s AND summary_date = CURRENT_DATE
        """, (project_id,))
        if cached:
            return dict(cached)

    # Generate fresh summary
    engine = ProjectIntelligenceEngine(project_id)
    project = engine._project_row()
    if not project:
        raise HTTPException(404, f"Project {project_id} not found")

    result = engine.summary()
    health = result.get("health", "GREEN")
    ai_summary = result.get("ai_summary", "")
    risks = engine.detect_risks()
    key_risks = [{"code": r["risk_code"], "title": r["title"], "severity": r["severity"]}
                 for r in risks[:3]]
    key_actions = result.get("recommended_next_actions", [])[:3]

    decisions = engine._open_decisions()
    today_events = svc.pg_one(
        "SELECT COUNT(*) as n FROM project_events WHERE project_id=%s AND event_date=CURRENT_DATE",
        (project_id,))
    event_count = int(today_events.get("n") or 0) if today_events else 0

    svc.pg_one("""
        INSERT INTO project_daily_summaries
            (project_id, summary_date, health, ai_summary, key_risks,
             key_actions, event_count, decisions_open, generated_by)
        VALUES (%s, CURRENT_DATE, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (project_id, summary_date) DO UPDATE SET
            health       = EXCLUDED.health,
            ai_summary   = EXCLUDED.ai_summary,
            key_risks    = EXCLUDED.key_risks,
            key_actions  = EXCLUDED.key_actions,
            event_count  = EXCLUDED.event_count,
            decisions_open = EXCLUDED.decisions_open,
            generated_by = EXCLUDED.generated_by,
            generated_at = NOW()
        RETURNING id
    """, (project_id, health, ai_summary, _json.dumps(key_risks),
          _json.dumps(key_actions), event_count, len(decisions),
          "on_demand" if force_refresh else "system"))

    return {
        "project_id": project_id,
        "project_name": project.get("name"),
        "summary_date": str(_date.today()),
        "health": health,
        "ai_summary": ai_summary,
        "key_risks": key_risks,
        "key_actions": key_actions,
        "event_count": event_count,
        "decisions_open": len(decisions),
        "generated_at": engine.__class__.__module__,
        "cached": False,
    }

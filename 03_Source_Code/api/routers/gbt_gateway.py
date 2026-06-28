"""
GBT Orchestrator Gateway — n8n Bridge for ChatGPT
Exposes all HCI AI OS services via authenticated HTTPS endpoints (ngrok tunnel on :8000).

ChatGPT → https://speculate-armband-retinal.ngrok-free.dev/gateway/{path}
Architecture:  ChatGPT → ngrok → FastAPI Gateway → internal HCI services → normalized JSON

Prefix: /gateway
Auth:   X-API-Key header  OR  ?api_key= query param
"""
import os, uuid, time, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import psycopg2, psycopg2.extras, requests
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))
from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime, timezone

router = APIRouter(prefix="/gateway", tags=["gbt-gateway"])

_INTERNAL_BASE = "http://localhost:8000/api/v1"
_INTERNAL_KEY  = os.environ.get("HCI_API_KEY", "hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6")
_INTERNAL_H    = {"X-API-Key": _INTERNAL_KEY}

DB = dict(
    host=os.environ.get("POSTGRES_HOST", "localhost"),
    port=int(os.environ.get("POSTGRES_PORT", 5432)),
    dbname=os.environ.get("POSTGRES_DB", "hci_os"),
    user=os.environ.get("POSTGRES_USER", "hci_admin"),
    password=os.environ.get("POSTGRES_PASSWORD", ""),
)

SERVICE_REGISTRY = [
    {"name": "project-brain",       "path": "/gateway/project/{code}/brain",      "description": "Full project intelligence snapshot"},
    {"name": "project-schedule",    "path": "/gateway/project/{code}/schedule",   "description": "Schedule status and variances"},
    {"name": "project-bids",        "path": "/gateway/project/{code}/bids",       "description": "Bid packages and procurement status"},
    {"name": "pm-weekly",           "path": "/gateway/project/{code}/pm",         "description": "PM weekly console"},
    {"name": "project-state",       "path": "/gateway/project-state",             "description": "Full live system state (all projects, health, AI team)"},
    {"name": "executive-report",    "path": "/gateway/executive/report",          "description": "Executive morning brief across all projects"},
    {"name": "knowledge-graph",     "path": "/gateway/knowledge/vendor",         "description": "Vendor cross-project lookup"},
    {"name": "drive-search",        "path": "/gateway/drive/search",             "description": "Search Google Drive files"},
    {"name": "agent-handoff",       "path": "/gateway/agent/handoff",            "description": "POST a platform intelligence document"},
    {"name": "health",              "path": "/gateway/health",                   "description": "Gateway health check"},
    {"name": "services",            "path": "/gateway/services",                 "description": "This service registry"},
]


def _pg():
    return psycopg2.connect(**DB, cursor_factory=psycopg2.extras.RealDictCursor)


def _response(path: str, payload: Any, source: str = "hci-api",
              start: float = None, warnings: list = None, errors: list = None) -> dict:
    elapsed = round((time.time() - start) * 1000) if start else 0
    return {
        "status": "ok" if not errors else "error",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "execution_time_ms": elapsed,
        "source_system": source,
        "payload": payload,
        "warnings": warnings or [],
        "errors": errors or [],
    }


def _log(path: str, source: str, upstream: str, status: str, ms: int,
         request_id: str, response_summary: str = ""):
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO gateway_request_log
                        (request_id, path, source_system, upstream_endpoint, status, execution_ms, response_summary)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (request_id, path, source, upstream, status, ms, response_summary[:200]))
            conn.commit()
    except Exception:
        pass


def _proxy(endpoint: str, params: dict = None) -> dict:
    r = requests.get(f"{_INTERNAL_BASE}{endpoint}", headers=_INTERNAL_H,
                     params=params, timeout=30)
    if not r.ok:
        raise HTTPException(r.status_code, f"Upstream error: {r.text[:200]}")
    return r.json()


# ── Service Registry + Health ─────────────────────────────────────────────────

@router.get("/health")
def gateway_health():
    t0 = time.time()
    try:
        _proxy("/health")
        upstream_ok = True
    except Exception:
        upstream_ok = False
    return _response("/health", {
        "gateway": "GBT Orchestrator Bridge v1.0",
        "hci_api_reachable": upstream_ok,
        "service_count": len(SERVICE_REGISTRY),
        "ngrok_url": "https://speculate-armband-retinal.ngrok-free.dev",
        "auth": "X-API-Key header required for write endpoints; reads open",
    }, start=t0)


@router.get("/services")
def list_services():
    t0 = time.time()
    return _response("/services", {
        "services": SERVICE_REGISTRY,
        "usage": "GET /gateway/{path} — all endpoints return standard JSON envelope",
        "auth": "Pass X-API-Key header for authenticated calls",
        "base_url": "https://speculate-armband-retinal.ngrok-free.dev",
    }, start=t0)


# ── Project State ─────────────────────────────────────────────────────────────

@router.get("/project-state")
def project_state():
    """Full live system state — same as /project-state root endpoint."""
    t0 = time.time()
    rid = str(uuid.uuid4())[:8]
    try:
        r = requests.get("http://localhost:8000/project-state", timeout=15)
        data = r.json() if r.ok else {"error": r.text[:200]}
        _log("/project-state", "ChatGPT", "/project-state", "ok",
             round((time.time()-t0)*1000), rid, "project state fetched")
        return _response("/project-state", data, start=t0)
    except Exception as e:
        return _response("/project-state", {}, errors=[str(e)], start=t0)


# ── Project Endpoints ─────────────────────────────────────────────────────────

@router.get("/project/{code}/brain")
def project_brain(code: str):
    """Project Brain snapshot — bids, risks, schedule, activity, intelligence."""
    t0 = time.time()
    rid = str(uuid.uuid4())[:8]
    try:
        snap = _proxy(f"/services/project-brain/{code}")
        intel = {}
        try:
            intel = _proxy(f"/services/project-brain/{code.replace(code, _get_pid(code))}/intelligence")
        except Exception:
            pass
        payload = {"snapshot": snap, "intelligence": intel}
        _log(f"/project/{code}/brain", "ChatGPT", f"/services/project-brain/{code}",
             "ok", round((time.time()-t0)*1000), rid)
        return _response(f"/project/{code}/brain", payload, start=t0)
    except HTTPException as e:
        return _response(f"/project/{code}/brain", {}, errors=[str(e.detail)], start=t0)


@router.get("/project/{code}/schedule")
def project_schedule(code: str):
    """Schedule status, variances, and superintendent view."""
    t0 = time.time()
    try:
        data = _proxy(f"/mvp/projects/{code}/schedule-status")
        return _response(f"/project/{code}/schedule", data, start=t0)
    except HTTPException as e:
        return _response(f"/project/{code}/schedule", {}, errors=[str(e.detail)], start=t0)


@router.get("/project/{code}/bids")
def project_bids(code: str):
    """Bid packages and procurement status."""
    t0 = time.time()
    try:
        data = _proxy(f"/services/project-brain/{code}/bids")
        return _response(f"/project/{code}/bids", data, start=t0)
    except HTTPException as e:
        return _response(f"/project/{code}/bids", {}, errors=[str(e.detail)], start=t0)


@router.get("/project/{code}/pm")
def project_pm(code: str):
    """PM weekly console — health, risks, procurement, client comms, ranked actions."""
    t0 = time.time()
    try:
        data = _proxy(f"/mvp/projects/{code}/pm-review")
        return _response(f"/project/{code}/pm", data, start=t0)
    except HTTPException as e:
        return _response(f"/project/{code}/pm", {}, errors=[str(e.detail)], start=t0)


# ── Executive ─────────────────────────────────────────────────────────────────

@router.get("/executive/report")
def executive_report():
    """Executive morning brief — all projects health, ROI, decisions, risks."""
    t0 = time.time()
    try:
        data = _proxy("/executive/morning-brief")
        return _response("/executive/report", data, start=t0)
    except HTTPException as e:
        return _response("/executive/report", {}, errors=[str(e.detail)], start=t0)


@router.get("/executive/mission-control")
def mission_control():
    """Mission control — cross-project command center."""
    t0 = time.time()
    try:
        data = _proxy("/executive/mission-control")
        return _response("/executive/mission-control", data, start=t0)
    except HTTPException as e:
        return _response("/executive/mission-control", {}, errors=[str(e.detail)], start=t0)


# ── Knowledge Graph ───────────────────────────────────────────────────────────

@router.get("/knowledge/vendor")
def knowledge_vendor(name: str = Query(..., description="Vendor or subcontractor name")):
    """Look up all projects a vendor was involved in."""
    t0 = time.time()
    try:
        data = _proxy("/services/knowledge-graph/vendor", {"name": name})
        return _response("/knowledge/vendor", data, start=t0)
    except HTTPException as e:
        return _response("/knowledge/vendor", {}, errors=[str(e.detail)], start=t0)


@router.get("/knowledge/issues")
def knowledge_issues(q: str = Query(..., description="Search term, e.g. 'waterproofing'")):
    """Semantic search for similar issues across all projects."""
    t0 = time.time()
    try:
        data = _proxy("/services/knowledge-graph/issues", {"q": q})
        return _response("/knowledge/issues", data, start=t0)
    except HTTPException as e:
        return _response("/knowledge/issues", {}, errors=[str(e.detail)], start=t0)


# ── Drive Search ──────────────────────────────────────────────────────────────

@router.get("/drive/search")
def drive_search(q: str = Query(..., description="Search term for Drive files")):
    """Search Google Drive files (buck@hendricksoninc.com)."""
    t0 = time.time()
    try:
        data = _proxy("/services/drive-intelligence/search", {"q": q})
        return _response("/drive/search", data, start=t0)
    except HTTPException as e:
        return _response("/drive/search", {}, errors=[str(e.detail)], start=t0)


# ── Agent Handoff ─────────────────────────────────────────────────────────────

class HandoffPayload(BaseModel):
    source_agent: str = "ChatGPT"
    destination_agent: str = "Claude Code"
    document_type: str = "implementation_request"
    priority: str = "medium"
    status: str = "pending"
    related_system: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    body: Optional[str] = None


@router.post("/agent/handoff")
async def agent_handoff(req: HandoffPayload):
    """
    POST a platform intelligence document or implementation request.
    Writes directly to Agent Handoff Bus Inbox — processed by handoff_processor.py.
    """
    t0 = time.time()
    rid = str(uuid.uuid4())[:8]
    ts  = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    inbox = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "..", "..",
        "Architecture", "Agent_Handoff", "Inbox"
    ))
    os.makedirs(inbox, exist_ok=True)

    slug = (req.title or req.document_type or "handoff").replace(" ", "_")[:40]
    fname = f"GBT_HANDOFF_{ts}_{slug}_{rid}.md"
    fpath = os.path.join(inbox, fname)

    content = f"""---
source_agent: {req.source_agent}
destination_agent: {req.destination_agent}
document_type: {req.document_type}
priority: {req.priority}
status: {req.status}
related_system: {req.related_system or ''}
title: {req.title or slug}
created_at: {ts}
summary: {req.summary or f'Handoff from {req.source_agent} via GBT Gateway'}
---

{req.body or ''}
"""

    with open(fpath, "w") as f:
        f.write(content)

    # Trigger processor async (best-effort)
    import subprocess, threading
    def _run():
        subprocess.run(
            ["python3", os.path.join(inbox, "..", "handoff_processor.py"), "--file", fpath],
            capture_output=True, timeout=30
        )
    threading.Thread(target=_run, daemon=True).start()

    _log("/agent/handoff", req.source_agent, "Agent_Handoff/Inbox",
         "queued", round((time.time()-t0)*1000), rid, f"queued {fname}")

    return _response("/agent/handoff", {
        "queued": True, "filename": fname, "request_id": rid,
        "message": "Handoff written to Inbox — processor will route within 60s",
    }, start=t0)


# ── Request Log ───────────────────────────────────────────────────────────────

@router.get("/admin/log")
def gateway_log(limit: int = Query(50, le=200)):
    """Recent gateway request log."""
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT request_id, path, source_system, upstream_endpoint,
                           status, execution_ms, response_summary, created_at
                    FROM gateway_request_log ORDER BY created_at DESC LIMIT %s
                """, (limit,))
                rows = [dict(r) for r in cur.fetchall()]
        return _response("/admin/log", {"count": len(rows), "entries": rows})
    except Exception as e:
        return _response("/admin/log", {}, errors=[str(e)])


def _get_pid(code: str) -> int:
    PILOT = {"64EW": 1, "101F": 2, "1355R": 3}
    return PILOT.get(code.upper(), 1)

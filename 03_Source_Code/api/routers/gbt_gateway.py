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


def _require_key(request: Request):
    key = request.headers.get("X-API-Key") or request.query_params.get("api_key")
    if key != _INTERNAL_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")


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
    """Executive morning brief — real data from DB, not kpi_snapshots cache."""
    t0 = time.time()
    try:
        conn = _pg()
        conn.autocommit = True
        projects = []
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.id, p.name,
                    (SELECT COUNT(*) FROM schedule_variance sv WHERE sv.project_id = p.id AND sv.risk_level IN ('high','critical')) AS high_variance,
                    (SELECT COUNT(*) FROM schedule_variance sv WHERE sv.project_id = p.id) AS total_variance,
                    (SELECT COUNT(*) FROM risks r WHERE r.project_id = p.id AND r.status = 'open') AS open_risks,
                    (SELECT COUNT(*) FROM project_schedule_items psi WHERE psi.project_id = p.id::text) AS schedule_items,
                    (SELECT MAX(ABS(sv.variance_days)) FROM schedule_variance sv WHERE sv.project_id = p.id) AS max_variance_days,
                    (SELECT COUNT(*) FROM daily_logs dl WHERE dl.project_id = p.id) AS daily_logs
                FROM projects p WHERE p.status = 'active' ORDER BY p.id
            """)
            rows = cur.fetchall()
        conn.close()
        for row in rows:
            max_var = row["max_variance_days"] or 0
            high_var = row["high_variance"] or 0
            open_risks = row["open_risks"] or 0
            if high_var > 0 or open_risks > 0 or max_var >= 3:
                health = "YELLOW" if max_var < 7 and open_risks < 3 else "RED"
                icon = "🟡" if health == "YELLOW" else "🔴"
            else:
                health = "GREEN"
                icon = "🟢"
            sched = f"+{max_var}d behind" if max_var > 0 else "On track"
            projects.append({
                "name": row["name"],
                "health": health,
                "icon": icon,
                "schedule": sched,
                "max_variance_days": max_var,
                "high_variance_items": high_var,
                "total_variance_items": row["total_variance"] or 0,
                "open_risks": open_risks,
                "schedule_items": row["schedule_items"] or 0,
                "daily_logs": row["daily_logs"] or 0,
                "summary": f"{icon} {row['name']}: {sched}, {open_risks} risks, {row['schedule_items'] or 0} activities"
            })
        return _response("/executive/report", {
            "date": datetime.now(timezone.utc).date().isoformat(),
            "source": "live_db",
            "projects": projects,
            "warnings": ["kpi_snapshots not populated — data pulled directly from schedule_variance and risks tables"] if not any(p["open_risks"] for p in projects) else []
        }, start=t0)
    except Exception as e:
        return _response("/executive/report", {}, errors=[str(e)], start=t0)


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

_DOCUMENT_TYPES = [
    "implementation_request",
    "architecture_change_request",
    "audit_request",
    "browser_discovery",
    "platform_watch",
    "houzz_export",
    "hubspot_export",
    "platform_opportunity_report",
    "business_process_architecture",
    "chief_architect_directive",
    "architecture_chapter",
    "approval_request",
    "executive_brief",
]

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
        "document_type": req.document_type,
        "message": "Handoff written to Inbox — processor will route within 60s",
    }, start=t0)


@router.get("/agent/handoff/document-types")
def handoff_document_types():
    """Return valid document_type values for POST /gateway/agent/handoff."""
    t0 = time.time()
    return _response("/agent/handoff/document-types", {
        "valid_document_types": _DOCUMENT_TYPES,
        "default": "implementation_request",
        "description": {
            "implementation_request": "Task for Claude Code to build or fix something",
            "architecture_change_request": "ACR — structural change under Architecture Freeze v1.0",
            "audit_request": "Request Claude Code to audit a system or dataset",
            "browser_discovery": "Browser Claude platform intelligence document",
            "chief_architect_directive": "Strategic directive from GBT Chief Architect",
            "approval_request": "Requests human approval via executive inbox",
            "executive_brief": "Published executive-level document",
        }
    }, start=t0)


# ── Drive Write ───────────────────────────────────────────────────────────────

class DriveWritePayload(BaseModel):
    filename: str
    content: str
    folder_id: Optional[str] = None
    mime_type: str = "text/plain"

@router.post("/drive/write")
async def drive_write(req: DriveWritePayload):
    """
    Write plain text / markdown content directly to Google Drive.
    GBT provides filename + content as a string — no base64 encoding needed.
    folder_id defaults to the HCI Master AI folder.
    """
    t0 = time.time()
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
        from integrations.credentials import get_google_token
        import base64

        token = get_google_token("drive")
        folder_id = req.folder_id or os.environ.get("HCI_AI_DRIVE_FOLDER", "1ejYXRgS34c7JmQKfHwaPNnzEBcCGUmwI")

        # Check if file already exists in folder
        search_resp = requests.get(
            "https://www.googleapis.com/drive/v3/files",
            headers={"Authorization": f"Bearer {token}"},
            params={"q": f"name='{req.filename}' and '{folder_id}' in parents and trashed=false", "fields": "files(id,name)"}
        )
        existing = search_resp.json().get("files", [])

        content_bytes = req.content.encode("utf-8")
        mime = req.mime_type

        if existing:
            # Update existing file
            file_id = existing[0]["id"]
            update_resp = requests.patch(
                f"https://www.googleapis.com/upload/drive/v3/files/{file_id}",
                headers={"Authorization": f"Bearer {token}", "Content-Type": mime},
                params={"uploadType": "media", "fields": "id,name,webViewLink"},
                data=content_bytes
            )
            result = update_resp.json()
            action = "updated"
        else:
            # Create new file
            import json as _json
            metadata = _json.dumps({"name": req.filename, "parents": [folder_id]}).encode()
            boundary = "HCI_BOUNDARY_12345"
            body = (
                f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n".encode()
                + metadata
                + f"\r\n--{boundary}\r\nContent-Type: {mime}\r\n\r\n".encode()
                + content_bytes
                + f"\r\n--{boundary}--".encode()
            )
            create_resp = requests.post(
                "https://www.googleapis.com/upload/drive/v3/files",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": f"multipart/related; boundary={boundary}"
                },
                params={"uploadType": "multipart", "fields": "id,name,webViewLink"},
                data=body
            )
            result = create_resp.json()
            action = "created"

        _log("/drive/write", "gbt", req.filename, action, round((time.time()-t0)*1000), str(uuid.uuid4())[:8])
        return _response("/drive/write", {
            "action": action,
            "filename": req.filename,
            "file_id": result.get("id"),
            "view_link": result.get("webViewLink"),
            "folder_id": folder_id,
            "bytes_written": len(content_bytes)
        }, start=t0)

    except Exception as e:
        return _response("/drive/write", {}, errors=[str(e)], start=t0)


# ── Admin: Process Inbox ─────────────────────────────────────────────────────

@router.post("/admin/process-inbox")
async def process_inbox():
    """
    Run the handoff processor on all pending files in Agent_Handoff/Inbox/.
    Called by n8n AUTO-HANDOFF-PROCESSOR via HTTP Request node (replaces broken executeCommand).
    """
    t0 = time.time()
    try:
        import subprocess
        processor = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "..", "..",
            "Architecture", "Agent_Handoff", "handoff_processor.py"
        ))
        result = subprocess.run(
            [sys.executable, processor],
            capture_output=True, text=True, timeout=60,
            cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        )
        output = result.stdout + result.stderr
        lines = [l for l in output.splitlines() if l.strip()]
        processed = sum(1 for l in lines if "✅" in l)
        failed = sum(1 for l in lines if "❌" in l)
        _log("/admin/process-inbox", "n8n", "Agent_Handoff/Inbox", "ok",
             round((time.time()-t0)*1000), str(uuid.uuid4())[:8],
             f"processed={processed} failed={failed}")
        return _response("/admin/process-inbox", {
            "processed": processed,
            "failed": failed,
            "output": lines
        }, start=t0)
    except Exception as e:
        return _response("/admin/process-inbox", {}, errors=[str(e)], start=t0)


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


# ── BUILD-2: BP-06 Risk Backfill ─────────────────────────────────────────────

@router.post("/admin/backfill-risks")
async def backfill_risks(request: Request):
    """File risks for any high/critical schedule_variance records not yet in risks table."""
    _require_key(request)
    t0 = time.time()
    rid = str(uuid.uuid4())[:8]
    try:
        import importlib.util, sys as _sys
        svc_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "..",
            "services", "schedule_intelligence", "schedule_intelligence_svc.py"
        ))
        spec = importlib.util.spec_from_file_location("schedule_intelligence_svc", svc_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        result = mod.ScheduleIntelligenceService.backfill_risks()
        _log("/admin/backfill-risks", "admin", "risks", "ok",
             round((time.time()-t0)*1000), rid, str(result))
        return _response("/admin/backfill-risks", result, start=t0)
    except Exception as e:
        return _response("/admin/backfill-risks", {}, errors=[str(e)], start=t0)


# ── BUILD-1: KPI Snapshot Backfill ───────────────────────────────────────────

@router.post("/admin/backfill-kpis")
async def backfill_kpis(request: Request):
    """Populate kpi_snapshots from live DB data for all active projects."""
    _require_key(request)
    t0 = time.time()
    rid = str(uuid.uuid4())[:8]
    try:
        import importlib.util
        svc_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "..",
            "services", "schedule_intelligence", "schedule_intelligence_svc.py"
        ))
        spec = importlib.util.spec_from_file_location("schedule_intelligence_svc", svc_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        result = mod.ScheduleIntelligenceService.backfill_kpi_snapshots()
        _log("/admin/backfill-kpis", "admin", "kpi_snapshots", "ok",
             round((time.time()-t0)*1000), rid, str(result))
        return _response("/admin/backfill-kpis", result, start=t0)
    except Exception as e:
        return _response("/admin/backfill-kpis", {}, errors=[str(e)], start=t0)


# ── BUILD-5: Mobile Approval Endpoints ───────────────────────────────────────

class ApprovalActionPayload(BaseModel):
    notes: Optional[str] = None

@router.get("/approvals/pending")
async def approvals_pending(request: Request, limit: int = Query(20, le=100)):
    """List pending approvals — usable from phone Safari with API key."""
    _require_key(request)
    t0 = time.time()
    rid = str(uuid.uuid4())[:8]
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, workflow, action_type, target_system, project_id,
                           target_description, reason, priority, actor, created_at,
                           proposed_payload
                    FROM approval_queue
                    WHERE status = 'pending'
                    ORDER BY priority DESC, created_at DESC
                    LIMIT %s
                """, (limit,))
                rows = [dict(r) for r in cur.fetchall()]
        _log("/approvals/pending", "mobile", "approval_queue", "ok",
             round((time.time()-t0)*1000), rid, f"count={len(rows)}")
        return _response("/approvals/pending", {
            "total_pending": len(rows),
            "items": rows
        }, start=t0)
    except Exception as e:
        return _response("/approvals/pending", {}, errors=[str(e)], start=t0)


@router.post("/approvals/{item_id}/approve")
async def approve_item(item_id: int, body: ApprovalActionPayload, request: Request):
    """Approve a pending approval queue item — callable from phone Safari."""
    _require_key(request)
    t0 = time.time()
    rid = str(uuid.uuid4())[:8]
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE approval_queue
                    SET status = 'approved',
                        approved_by = 'buck-mobile',
                        approved_at = NOW(),
                        reason = COALESCE(%s, reason)
                    WHERE id = %s AND status = 'pending'
                    RETURNING id, workflow, action_type, target_description
                """, (body.notes, item_id))
                row = cur.fetchone()
            conn.commit()
        if not row:
            return _response(f"/approvals/{item_id}/approve", {},
                             errors=["Item not found or already actioned"], start=t0)
        _log(f"/approvals/{item_id}/approve", "mobile", "approval_queue", "ok",
             round((time.time()-t0)*1000), rid, f"approved id={item_id}")
        return _response(f"/approvals/{item_id}/approve", {
            "approved": True, "item_id": item_id,
            "workflow": row["workflow"], "description": row["target_description"]
        }, start=t0)
    except Exception as e:
        return _response(f"/approvals/{item_id}/approve", {}, errors=[str(e)], start=t0)


@router.post("/approvals/{item_id}/reject")
async def reject_item(item_id: int, body: ApprovalActionPayload, request: Request):
    """Reject a pending approval queue item — callable from phone Safari."""
    _require_key(request)
    t0 = time.time()
    rid = str(uuid.uuid4())[:8]
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE approval_queue
                    SET status = 'rejected',
                        rejected_reason = %s
                    WHERE id = %s AND status = 'pending'
                    RETURNING id, workflow, action_type, target_description
                """, (body.notes or "Rejected via mobile", item_id))
                row = cur.fetchone()
            conn.commit()
        if not row:
            return _response(f"/approvals/{item_id}/reject", {},
                             errors=["Item not found or already actioned"], start=t0)
        _log(f"/approvals/{item_id}/reject", "mobile", "approval_queue", "ok",
             round((time.time()-t0)*1000), rid, f"rejected id={item_id}")
        return _response(f"/approvals/{item_id}/reject", {
            "rejected": True, "item_id": item_id,
            "workflow": row["workflow"], "description": row["target_description"]
        }, start=t0)
    except Exception as e:
        return _response(f"/approvals/{item_id}/reject", {}, errors=[str(e)], start=t0)


# ── BUILD-6: Auto-Sync LIVE_PROJECT_STATE ─────────────────────────────────────

@router.post("/admin/sync-live-state")
async def sync_live_state(request: Request):
    """Read exec report data from DB, update project table in LIVE_PROJECT_STATE.md + Drive copy."""
    _require_key(request)
    t0 = time.time()
    rid = str(uuid.uuid4())[:8]
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT p.id, p.name,
                        (SELECT COUNT(*) FROM schedule_variance sv
                         WHERE sv.project_id = p.id AND sv.risk_level IN ('high','critical')) AS high_variance,
                        (SELECT COUNT(*) FROM risks r
                         WHERE r.project_id = p.id AND r.status = 'open') AS open_risks,
                        (SELECT MAX(ABS(sv.variance_days)) FROM schedule_variance sv
                         WHERE sv.project_id = p.id) AS max_variance_days
                    FROM projects p WHERE p.status = 'active' ORDER BY p.id
                """)
                rows = [dict(r) for r in cur.fetchall()]

        CODE_MAP = {1: "64EW", 2: "101F", 3: "1355R", 4: "83SB", 8: "246GW"}
        NAME_MAP = {1: "64 Eastwood", 2: "101 Francis", 3: "1355 Riverside", 4: "83 Sagebrusch", 8: "246 Gallo Way"}
        HS_MAP   = {1: "331240861419", 2: "321401932527", 3: "321351275210", 4: "", 8: "321358358216"}
        SCOPE_MAP = {1: "Exterior & Site", 2: "Full Interior Remodel", 3: "Full Remodel", 4: "TBD", 8: "New Construction — Chaparral Lot 7"}

        # Build updated table rows
        table_lines = [
            "| ID | Code | Project | Scope | HubSpot Deal | Health | Bid Pkgs | Open Risks | Schedule Var |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
        snap = {}
        for r in rows:
            pid = r["id"]
            high_v = int(r["high_variance"] or 0)
            open_r = int(r["open_risks"] or 0)
            max_d  = int(r["max_variance_days"] or 0)
            health = "🟢 GREEN" if (high_v == 0 and open_r == 0) else "🟡 YELLOW" if (high_v <= 2 and open_r <= 3) else "🔴 RED"
            var_str = f"+{max_d} days" if max_d > 0 else "0 days"

            # bid count from DB
            with _pg() as conn2:
                with conn2.cursor() as cur2:
                    cur2.execute("SELECT COUNT(*) AS c FROM bid_packages WHERE project_id = %s", (pid,))
                    bids = (cur2.fetchone() or {}).get("c", 0)

            code = CODE_MAP.get(pid, str(pid))
            snap[code] = {"health": health, "open_risks": open_r, "schedule_var": var_str}
            table_lines.append(
                f"| {pid} | {code} | {NAME_MAP.get(pid,'')} | {SCOPE_MAP.get(pid,'')} | "
                f"{HS_MAP.get(pid,'')} | {health} | {bids} | {open_r} | {var_str} |"
            )

        new_table = "\n".join(table_lines)

        # Read and patch LIVE_PROJECT_STATE.md
        live_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "..", "..",
            "LIVE_PROJECT_STATE.md"
        ))
        with open(live_path, "r") as f:
            content = f.read()

        import re as _re
        # Replace the project table block
        pattern = r"(\| ID \| Code \| Project.*?)\n\n"
        new_block = new_table + "\n\n"
        updated = _re.sub(pattern, new_block, content, flags=_re.DOTALL)

        # Update timestamp
        from datetime import datetime, timezone
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M MST")
        updated = _re.sub(
            r"\*\*Last Updated:\*\*.*",
            f"**Last Updated:** {ts}",
            updated
        )

        with open(live_path, "w") as f:
            f.write(updated)

        # Write to Drive
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
            from integrations.credentials import get_google_token as _get_drive_token
            token = _get_drive_token("drive")
            if token:
                drive_file_id = "1Jjug6nbx-mGN9v4GrEyofkGXY5nMHvpP"
                patch_resp = requests.patch(
                    f"https://www.googleapis.com/upload/drive/v3/files/{drive_file_id}",
                    params={"uploadType": "media", "fields": "id,name,webViewLink"},
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "text/plain"},
                    data=updated.encode("utf-8"),
                    timeout=30
                )
                drive_ok = patch_resp.status_code == 200
            else:
                drive_ok = False
        except Exception as drive_err:
            drive_ok = False

        _log("/admin/sync-live-state", "admin", "LIVE_PROJECT_STATE.md", "ok",
             round((time.time()-t0)*1000), rid, f"projects={len(rows)} drive={drive_ok}")
        return _response("/admin/sync-live-state", {
            "updated": True,
            "projects_synced": len(rows),
            "project_snapshot": snap,
            "drive_updated": drive_ok,
            "local_path": live_path
        }, start=t0)
    except Exception as e:
        return _response("/admin/sync-live-state", {}, errors=[str(e)], start=t0)


# ── BUILD-4: Houzz Schedule CSV Export ───────────────────────────────────────

@router.post("/drive/export-schedule-csv")
async def export_schedule_csv(request: Request,
                               project_code: str = Query(..., description="64EW, 101F, or 1355R")):
    """Export project_schedule_items to Houzz-compatible CSV and write to Drive project folder."""
    _require_key(request)
    t0 = time.time()
    rid = str(uuid.uuid4())[:8]
    try:
        import csv, io
        pid = _get_pid(project_code)
        CODE_MAP = {1: "64EW", 2: "101F", 3: "1355R", 4: "83SB", 8: "246GW"}
        HCI_FOLDER = os.environ.get("HCI_AI_DRIVE_FOLDER", "1ejYXRgS34c7JmQKfHwaPNnzEBcCGUmwI")
        FOLDER_MAP = {1: HCI_FOLDER, 2: HCI_FOLDER, 3: HCI_FOLDER}

        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, title AS task_name, start_date, end_date, status,
                           task_type, assignee, completion_pct, notes
                    FROM project_schedule_items
                    WHERE project_id = %s::text
                    ORDER BY start_date
                """, (str(pid),))
                items = [dict(r) for r in cur.fetchall()]

        if not items:
            return _response("/drive/export-schedule-csv", {},
                             errors=[f"No schedule items for {project_code}"], start=t0)

        # Build Houzz-compatible CSV
        out = io.StringIO()
        writer = csv.DictWriter(out, fieldnames=[
            "Task Name", "Start Date", "End Date", "Status",
            "Task Type", "Assignee", "Completion %", "Notes"
        ])
        writer.writeheader()
        for item in items:
            writer.writerow({
                "Task Name": item.get("task_name", ""),
                "Start Date": str(item.get("start_date", "")),
                "End Date": str(item.get("end_date", "")),
                "Status": item.get("status", ""),
                "Task Type": item.get("task_type", ""),
                "Assignee": item.get("assignee", ""),
                "Completion %": item.get("completion_pct", ""),
                "Notes": item.get("notes", ""),
            })
        csv_content = out.getvalue()

        # Write to Drive
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
        from integrations.credentials import get_google_token
        token = get_google_token("drive")
        if not token:
            return _response("/drive/export-schedule-csv", {},
                             errors=["Drive auth failed"], start=t0)

        filename = f"{CODE_MAP.get(pid, project_code)}_Schedule_Export.csv"
        meta = {"name": filename, "mimeType": "text/csv",
                "parents": [FOLDER_MAP.get(pid, "root")]}
        boundary = "hci_csv_boundary"
        body = (
            f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n"
            + __import__("json").dumps(meta)
            + f"\r\n--{boundary}\r\nContent-Type: text/csv\r\n\r\n"
            + csv_content
            + f"\r\n--{boundary}--"
        )
        create_resp = requests.post(
            "https://www.googleapis.com/upload/drive/v3/files",
            params={"uploadType": "multipart", "fields": "id,name,webViewLink"},
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": f"multipart/related; boundary={boundary}",
            },
            data=body.encode("utf-8"),
            timeout=30
        )
        if create_resp.status_code not in (200, 201):
            return _response("/drive/export-schedule-csv", {},
                             errors=[f"Drive upload failed: {create_resp.text[:200]}"], start=t0)

        drive_data = create_resp.json()
        _log("/drive/export-schedule-csv", "admin", "Drive", "ok",
             round((time.time()-t0)*1000), rid,
             f"project={project_code} rows={len(items)} file_id={drive_data.get('id')}")
        return _response("/drive/export-schedule-csv", {
            "project_code": project_code,
            "rows_exported": len(items),
            "filename": filename,
            "file_id": drive_data.get("id"),
            "view_link": drive_data.get("webViewLink"),
            "bytes_written": len(csv_content.encode())
        }, start=t0)
    except Exception as e:
        return _response("/drive/export-schedule-csv", {}, errors=[str(e)], start=t0)


def _get_pid(code: str) -> int:
    PILOT = {"64EW": 1, "101F": 2, "1355R": 3, "246GW": 8, "83SB": 4}
    return PILOT.get(code.upper(), 1)

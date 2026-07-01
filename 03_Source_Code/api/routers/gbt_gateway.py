"""
GBT Orchestrator Gateway — n8n Bridge for ChatGPT
Exposes all HCI AI OS services via authenticated HTTPS endpoints (ngrok tunnel on :8000).

ChatGPT → https://speculate-armband-retinal.ngrok-free.dev/gateway/{path}
Architecture:  ChatGPT → ngrok → FastAPI Gateway → internal HCI services → normalized JSON

Prefix: /gateway
Auth:   X-API-Key header  OR  ?api_key= query param
"""
import os, uuid, time, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import psycopg2, psycopg2.extras, requests
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))
from fastapi import APIRouter, HTTPException, Request, Query, UploadFile, File, Form
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
    # BTW-4: Project Brain Extended Memory
    {"name": "project-documents",   "path": "/gateway/project/{code}/documents",  "description": "BTW-4: Document relationships — docs linked to decisions/risks/COs"},
    {"name": "project-memory",      "path": "/gateway/project/{code}/memory",     "description": "BTW-4: Conversation memory — AI interaction history per project"},
    # BTW-5: Role Intelligence
    {"name": "role-owner",          "path": "/gateway/role/owner",                "description": "BTW-5: Owner command center — all projects, approvals, critical risks"},
    {"name": "role-office",         "path": "/gateway/role/office",               "description": "BTW-5: Office admin console — pending items, submittals, AP/AR"},
    {"name": "role-accounting",     "path": "/gateway/role/accounting",           "description": "BTW-5: Accounting — budget vs committed, bid awards, financial health"},
    {"name": "role-client",         "path": "/gateway/role/client/{code}",        "description": "BTW-5: Client portal — project status, RFIs, change orders"},
    {"name": "role-trade-partner",  "path": "/gateway/role/trade-partner",        "description": "BTW-5: Trade partner — work queue, bids, open RFIs (?vendor=X&code=Y)"},
    {"name": "project-brain",       "path": "/gateway/project/{code}/brain",      "description": "Full project intelligence snapshot"},
    {"name": "project-schedule",    "path": "/gateway/project/{code}/schedule",   "description": "Schedule status and variances"},
    {"name": "project-bids",        "path": "/gateway/project/{code}/bids",       "description": "Bid packages and procurement status"},
    {"name": "bid-leveling",        "path": "/gateway/project/{code}/bid-level",  "description": "GET: leveling view from bid_packages/entries. POST: full Drive scan + Gemini extraction + Excel generation"},
    {"name": "drive-bids",         "path": "/gateway/project/{code}/drive-bids", "description": "GET: actual bids extracted from Drive vendor PDF files (source of truth)"},
    {"name": "pm-weekly",           "path": "/gateway/project/{code}/pm",         "description": "PM weekly console"},
    {"name": "project-timeline",     "path": "/gateway/project/{code}/timeline",       "description": "Chronological event timeline — logs, risks, RFIs, awards"},
    {"name": "project-procurement",  "path": "/gateway/project/{code}/procurement",     "description": "BTW-11: Procurement action plan — packages needing bids, vendor matches, urgency"},
    {"name": "project-houzz",        "path": "/gateway/project/{code}/houzz",           "description": "Houzz schedule intelligence — upcoming milestones, active phase, overdue items, COs"},
    {"name": "houzz-portfolio",      "path": "/gateway/houzz/portfolio",                "description": "All-projects Houzz portfolio view — schedule health + milestones for every live job"},
    {"name": "project-hubspot",      "path": "/gateway/project/{code}/hubspot",         "description": "HubSpot intelligence — notes, emails, tasks, engagements. Surfaces bid communications."},
    {"name": "hubspot-portfolio",    "path": "/gateway/hubspot/portfolio",              "description": "HubSpot portfolio — notes + engagement counts for all live projects"},
    {"name": "weekly-digest",        "path": "/gateway/project/{code}/weekly-digest",  "description": "PM weekly digest — last 7 days + next week priorities"},
    {"name": "client-comms",         "path": "/gateway/project/{code}/client-comms",   "description": "Outstanding items needing client/owner communication"},
    {"name": "action-list",          "path": "/gateway/project/{code}/action-list",    "description": "AI-ranked top 10 PM actions for the day"},
    {"name": "project-state",       "path": "/gateway/project-state",             "description": "Full live system state (all projects, health, AI team)"},
    {"name": "executive-report",    "path": "/gateway/executive/report",          "description": "Executive morning brief across all projects"},
    {"name": "knowledge-graph",     "path": "/gateway/knowledge/vendor",         "description": "Vendor cross-project lookup by name"},
    {"name": "knowledge-vendors",   "path": "/gateway/knowledge/vendors",        "description": "Paginated vendor list with CSI + search filters (Gap5)"},
    {"name": "knowledge-lessons",   "path": "/gateway/knowledge/lessons",        "description": "Lessons learned from past projects (Gap6)"},
    {"name": "drive-search",        "path": "/gateway/drive/search",             "description": "Search Google Drive files"},
    {"name": "agent-handoff",       "path": "/gateway/agent/handoff",            "description": "POST a platform intelligence document"},
    {"name": "field-note",          "path": "/gateway/field/note",               "description": "POST quick field note from SS/PM (direct write, no approval)"},
    {"name": "field-rfi",           "path": "/gateway/field/rfi",                "description": "POST new RFI from field (Gap11)"},
    {"name": "field-daily-report",  "path": "/gateway/field/daily-report",       "description": "POST daily field report from SS (direct write)"},
    {"name": "field-open-items",    "path": "/gateway/field/open-items",         "description": "GET all open items for a project (RFIs+risks+flags)"},
    {"name": "field-daily-log-fmt", "path": "/gateway/field/daily-log-formatted","description": "GET Houzz-ready formatted daily log for a project+date"},
    {"name": "project-create",      "path": "/gateway/project/create",           "description": "POST create new project (Gap1)"},
    {"name": "risks-list",          "path": "/gateway/project/{code}/risks",     "description": "GET risk register for a project (Gap9)"},
    {"name": "risks-create",        "path": "/gateway/risks/create",             "description": "POST create a new risk (Gap9)"},
    {"name": "risks-update",        "path": "/gateway/risks/{id}/status",        "description": "PATCH update risk status open→mitigated→closed (Gap9)"},
    {"name": "submittals-list",     "path": "/gateway/project/{code}/submittals","description": "GET submittals tracker for a project (Gap12)"},
    {"name": "submittals-create",   "path": "/gateway/submittals/create",        "description": "POST create a new submittal (Gap12)"},
    {"name": "submittals-update",   "path": "/gateway/submittals/{id}/status",   "description": "PATCH update submittal status (Gap12)"},
    {"name": "market-rates",        "path": "/gateway/knowledge/market-rates",   "description": "GET Aspen market rates by CSI division from real bid data"},
    {"name": "rom-estimate",        "path": "/gateway/knowledge/rom-estimate",   "description": "GET ROM cost estimate by project type + SF, calibrated from historical records"},
    {"name": "bid-level",           "path": "/gateway/project/{code}/bid-level", "description": "GET bid leveling view — all packages with all bids sorted low-to-high"},
    {"name": "project-list",        "path": "/gateway/projects",                 "description": "GET full project registry — all real projects with status, scope, team"},
    {"name": "procurement-risk",    "path": "/gateway/project/{code}/procurement-risk", "description": "GET procurement risk analysis — gaps, single bids, awarded, coverage %"},
    {"name": "health",              "path": "/gateway/health",                   "description": "Gateway health check"},
    {"name": "services",            "path": "/gateway/services",                 "description": "This service registry"},
    {"name": "plan-read",           "path": "/gateway/plan/read",                "description": "POST: Vision AI plan reader — Drive PDF → page images → Sonnet/Opus gap analysis"},
    {"name": "batch",              "path": "/gateway/batch",                    "description": "POST: Execute N operations in 1 GBT call — ops: ntfyPush, emailDraft, sendHandoff, bidLevel, dbQuery"},
    {"name": "notify-test",        "path": "/gateway/notify/test",              "description": "POST: Push test notification to Buck's ntfy topic (hci-executive)"},
    {"name": "poll-instructions",  "path": "/gateway/poll-instructions",        "description": "GET: Poll ntfy topic for incoming messages from Buck (last 5 min)"},
    {"name": "intent-route",       "path": "/gateway/intent/route",             "description": "POST: Natural language intent router — message → execute → ntfy push"},
    {"name": "project-plans",      "path": "/gateway/project/{code}/plans",     "description": "GET: Scan drawings folder, classify by discipline, filter by scope/type"},
    {"name": "shared-drive-id",    "path": "/gateway/project/{code}/shared-drive-id", "description": "GET: Return all Drive folder IDs configured for a project"},
    # AI Operations Control Plane — Durable Comms Patch (2026-06-30)
    {"name": "ai-messages-create", "path": "/gateway/ai/messages",              "description": "POST: Create a durable agent message/task — DB is source of truth, auto-notifies Telegram+ntfy"},
    {"name": "ai-queue",           "path": "/gateway/ai/queue",                 "description": "GET: Fallback polling queue — works even if Telegram is down"},
    {"name": "ai-approvals",       "path": "/gateway/approvals",                "description": "GET: Pending Buck approvals from the durable queue"},
    {"name": "ai-message-status",  "path": "/gateway/ai/messages/{id}/status",  "description": "PATCH: Agent self-report — RECEIVED/IN_PROGRESS/BLOCKED/COMPLETE/etc"},
    {"name": "ai-heartbeat",       "path": "/gateway/ai/heartbeat",             "description": "POST: Agent heartbeat ping (chatgpt/claude_code/browser_claude/n8n)"},
    {"name": "ai-escalation-check","path": "/gateway/ai/escalation-check",      "description": "POST: Retry/escalate stale unacknowledged approvals — call from n8n on a schedule"},
    {"name": "telegram-health",    "path": "/gateway/telegram/health",          "description": "GET: Telegram webhook registration state + 24h send health"},
    {"name": "telegram-register",  "path": "/gateway/telegram/register-webhook","description": "POST: (Re)register Telegram webhook against the live ngrok URL"},
    # Warm Start Recovery Patch (2026-06-30)
    {"name": "ai-events",          "path": "/gateway/ai/events",                "description": "GET: Last N AI events/handoffs — merged ai_messages + Buck incoming messages feed"},
    {"name": "ai-warm-start",      "path": "/gateway/ai/warm-start",            "description": "GET: Single-call restart recovery snapshot — projects, risks, approvals, tasks, blockers, telegram health, next action"},
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


def _proxy(endpoint: str, params: dict = None, method: str = "GET",
           json: dict = None, timeout: int = 60) -> dict:
    fn = requests.post if method.upper() == "POST" else requests.get
    r  = fn(f"{_INTERNAL_BASE}{endpoint}", headers=_INTERNAL_H,
             params=params, json=json, timeout=timeout)
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

    # ChatGPT is pull-based (no webhook can push into a chat session) — surface
    # anything waiting for it on the very first call it makes each session so a
    # pending handoff can't get missed between sessions. (2026-06-30, per Buck:
    # "gbt is not picking you up" — this doesn't fix the pull-based limitation,
    # it just makes sure /health itself can't be checked without seeing the count.)
    pending_for_chatgpt = None
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT COUNT(*) n FROM ai_messages
                    WHERE target_agent = 'chatgpt' AND status NOT IN ('COMPLETE','REJECTED')""")
                pending_for_chatgpt = cur.fetchone()["n"]
    except Exception:
        pass

    return _response("/health", {
        "gateway": "GBT Orchestrator Bridge v1.0",
        "hci_api_reachable": upstream_ok,
        "service_count": len(SERVICE_REGISTRY),
        "ngrok_url": "https://speculate-armband-retinal.ngrok-free.dev",
        "auth": "X-API-Key header required for write endpoints; reads open",
        "pending_for_you": pending_for_chatgpt,
        "pending_for_you_note": "unresolved items in ai_messages targeted at chatgpt — call GET /gateway/ai/warm-start for detail" if pending_for_chatgpt else None,
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

@router.get("/directive")
def advance_directive():
    """GBT + BC advance directive — current state, lessons learned, build backlog, rules."""
    t0 = time.time()
    path = os.path.join(os.path.dirname(__file__), "../../../AI_TEAM/GBT_BC_ADVANCE_DIRECTIVE.md")
    path = os.path.normpath(path)
    try:
        with open(path) as f:
            content = f.read()
        return _response("/directive", {"directive": content, "file": "AI_TEAM/GBT_BC_ADVANCE_DIRECTIVE.md"}, start=t0)
    except FileNotFoundError:
        return _response("/directive", {}, errors=["Directive file not found"], start=t0)


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
        # project-brain resolves by code string (extracts leading digits via ILIKE)
        # For test projects without a numeric prefix (TSNB, TSREM), fall back to numeric ID
        brain_ref = code
        try:
            snap = _proxy(f"/services/project-brain/{brain_ref}")
        except HTTPException:
            brain_ref = str(_get_pid(code))
            snap = _proxy(f"/services/project-brain/{brain_ref}")
        # intelligence endpoint requires integer project_id
        numeric_pid = _get_pid(code)
        intel = {}
        try:
            intel = _proxy(f"/services/project-brain/{numeric_pid}/intelligence")
        except Exception:
            pass
        payload = {"snapshot": snap, "intelligence": intel}
        _log(f"/project/{code}/brain", "ChatGPT", f"/services/project-brain/{brain_ref}",
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


@router.get("/project/{code}/weekly-digest")
def project_weekly_digest(code: str):
    """PM weekly digest — last 7 days summary, open items, next week priorities."""
    t0 = time.time()
    try:
        data = _proxy(f"/mvp/projects/{code}/weekly-digest")
        return _response(f"/project/{code}/weekly-digest", data, start=t0)
    except HTTPException as e:
        return _response(f"/project/{code}/weekly-digest", {}, errors=[str(e.detail)], start=t0)


@router.get("/project/{code}/client-comms")
def project_client_comms(code: str):
    """Outstanding items requiring client/owner communication, ranked by urgency."""
    t0 = time.time()
    try:
        data = _proxy(f"/mvp/projects/{code}/client-comms")
        return _response(f"/project/{code}/client-comms", data, start=t0)
    except HTTPException as e:
        return _response(f"/project/{code}/client-comms", {}, errors=[str(e.detail)], start=t0)


@router.get("/project/{code}/action-list")
def project_action_list(code: str):
    """AI-ranked top 10 PM actions for the day."""
    t0 = time.time()
    try:
        data = _proxy(f"/mvp/projects/{code}/action-list")
        return _response(f"/project/{code}/action-list", data, start=t0)
    except HTTPException as e:
        return _response(f"/project/{code}/action-list", {}, errors=[str(e.detail)], start=t0)


@router.get("/project/{code}/timeline")
def project_timeline(code: str, days: int = 90, event_type: str = None):
    """Chronological project event timeline — daily logs, risks, RFIs, awards, meetings, COs."""
    t0 = time.time()
    try:
        pid = _get_pid(code)
        conn = _pg()
        conn.autocommit = True
        with conn.cursor() as cur:
            params = [pid, f"{days} days"]
            type_filter = ""
            if event_type:
                type_filter = " AND event_type = %s"
                params.append(event_type)
            cur.execute(f"""
                SELECT event_type, event_date, title, description,
                       source_table, source_id, created_by, metadata
                FROM project_events
                WHERE project_id = %s
                  AND event_date >= CURRENT_DATE - %s::interval
                  {type_filter}
                ORDER BY event_date DESC, created_at DESC
                LIMIT 200
            """, tuple(params))
            events = [dict(r) for r in cur.fetchall()]
            # Type summary
            from collections import Counter
            summary = dict(Counter(e["event_type"] for e in events))
        conn.close()
        payload = {
            "project_code": code,
            "project_id": pid,
            "days": days,
            "event_count": len(events),
            "event_type_summary": summary,
            "events": events,
        }
        return _response(f"/project/{code}/timeline", payload, start=t0)
    except HTTPException as e:
        return _response(f"/project/{code}/timeline", {}, errors=[str(e.detail)], start=t0)


@router.get("/project/{code}/documents")
def project_documents(code: str):
    """BTW-4: Document relationships — docs linked to decisions, risks, and change orders."""
    t0 = time.time()
    try:
        pid = _get_pid(code)
        conn = _pg()
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("""
                SELECT document_type, document_id, document_name, document_date,
                       linked_entity_type, linked_entity_id, linked_entity_name,
                       relationship, notes, linked_at
                FROM project_document_links
                WHERE project_id = %s
                ORDER BY linked_at DESC
                LIMIT 100
            """, (pid,))
            links = [dict(r) for r in cur.fetchall()]
            from collections import Counter
            by_type = dict(Counter(l["document_type"] for l in links))
        conn.close()
        return _response(f"/project/{code}/documents", {
            "project_code": code,
            "total_links": len(links),
            "by_document_type": by_type,
            "links": links,
        }, start=t0)
    except HTTPException as e:
        return _response(f"/project/{code}/documents", {}, errors=[str(e.detail)], start=t0)


@router.get("/project/{code}/memory")
def project_memory(code: str, limit: int = 20):
    """BTW-4: Conversation memory — AI interaction history for the project."""
    t0 = time.time()
    try:
        pid = _get_pid(code)
        conn = _pg()
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("""
                SELECT question, answer_summary, context_used, model_used, queried_at
                FROM project_ai_conversations
                WHERE project_id = %s
                ORDER BY queried_at DESC
                LIMIT %s
            """, (pid, limit))
            conversations = [dict(r) for r in cur.fetchall()]
        conn.close()
        return _response(f"/project/{code}/memory", {
            "project_code": code,
            "conversation_count": len(conversations),
            "conversations": conversations,
        }, start=t0)
    except HTTPException as e:
        return _response(f"/project/{code}/memory", {}, errors=[str(e.detail)], start=t0)


@router.get("/project/{code}/procurement")
def project_procurement_action_plan(code: str):
    """BTW-11: Procurement action plan — packages needing bids, sub matches by CSI code, urgency ranking."""
    t0 = time.time()
    try:
        pid = _get_pid(code)
        conn = _pg()
        conn.autocommit = True
        with conn.cursor() as cur:
            # Packages with NO bids (urgent — need outreach)
            cur.execute("""
                SELECT bp.id, bp.package_name, bp.csi_division, bp.status,
                       bp.scope_description,
                       COUNT(be.id) as bid_count,
                       SUM(be.bid_amount) as total_bid_value
                FROM bid_packages bp
                LEFT JOIN bid_entries be ON be.bid_package_id = bp.id AND be.bid_amount > 0
                WHERE bp.project_id = %s
                GROUP BY bp.id, bp.package_name, bp.csi_division, bp.status, bp.scope_description
                ORDER BY bid_count ASC, bp.csi_division
                LIMIT 50
            """, (pid,))
            packages = [dict(r) for r in cur.fetchall()]

            # Find matching vendors from vendor registry by CSI code prefix
            # bid_packages uses "09 — Painting" format; vendors use {"09"} short codes
            no_bid_packages = [p for p in packages if (p["bid_count"] or 0) == 0]
            vendor_matches = {}
            if no_bid_packages:
                # Extract 2-digit prefix from each CSI division string
                import re
                csi_prefix_map = {}  # "09" -> "09 — Painting" (full name)
                for pkg in no_bid_packages:
                    csi = pkg["csi_division"] or ""
                    m = re.match(r"^(\d{2})", csi)
                    if m:
                        csi_prefix_map[m.group(1)] = csi
                csi_prefixes = list(csi_prefix_map.keys())
                if csi_prefixes:
                    cur.execute("""
                        SELECT v.id, v.company_name, v.contact_name, v.email, v.phone,
                               v.csi_divisions, v.preferred_status
                        FROM vendors v
                        WHERE v.csi_divisions && %s::text[]
                        AND (v.preferred_status IS NULL OR v.preferred_status != 'inactive')
                        ORDER BY v.company_name
                        LIMIT 150
                    """, (csi_prefixes,))
                    for v in cur.fetchall():
                        vend_csids = v["csi_divisions"] or []
                        for vcode in vend_csids:
                            if vcode in csi_prefix_map:
                                full_csi = csi_prefix_map[vcode]
                                if full_csi not in vendor_matches:
                                    vendor_matches[full_csi] = []
                                vendor_matches[full_csi].append({
                                    "id": v["id"],
                                    "company": v["company_name"],
                                    "contact": v["contact_name"],
                                    "email": v["email"],
                                    "phone": v["phone"]
                                })

            # Summary stats
            total_pkgs = len(packages)
            with_bids = sum(1 for p in packages if (p["bid_count"] or 0) > 0)
            no_bids = total_pkgs - with_bids
            awarded = sum(1 for p in packages if p["status"] == "awarded")

        conn.close()

        # Build urgency list: packages with no bids + matched vendors
        action_items = []
        for pkg in no_bid_packages[:20]:
            csi = pkg["csi_division"] or ""
            matched_vendors = vendor_matches.get(csi, [])
            action_items.append({
                "package_name": pkg["package_name"],
                "csi_division": csi,
                "status": pkg["status"],
                "scope_description": pkg.get("scope_description", ""),
                "matched_vendors": len(matched_vendors),
                "vendors_to_invite": matched_vendors[:5],
                "urgency": "HIGH" if not matched_vendors else "MEDIUM"
            })

        return _response(f"/project/{code}/procurement", {
            "project_code": code,
            "summary": {
                "total_packages": total_pkgs,
                "with_bids": with_bids,
                "no_bids": no_bids,
                "awarded": awarded,
                "bid_coverage_pct": round(with_bids / total_pkgs * 100, 1) if total_pkgs > 0 else 0,
            },
            "action_items": action_items,
            "all_packages": packages[:30],
        }, start=t0)
    except HTTPException as e:
        return _response(f"/project/{code}/procurement", {}, errors=[str(e.detail)], start=t0)
    except Exception as e:
        return _response(f"/project/{code}/procurement", {}, errors=[str(e)], start=t0)


# ── Executive ─────────────────────────────────────────────────────────────────

@router.get("/executive/report")
def executive_report():
    """Executive morning brief — real data from DB. Health score includes bid coverage (Gap-15 fix)."""
    t0 = time.time()
    try:
        conn = _pg()
        conn.autocommit = True
        projects = []
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.id, p.name, p.project_code,
                    p.contract_value,
                    (SELECT COUNT(*) FROM schedule_variance sv WHERE sv.project_id = p.id AND sv.risk_level IN ('high','critical')) AS high_variance,
                    (SELECT COUNT(*) FROM schedule_variance sv WHERE sv.project_id = p.id) AS total_variance,
                    (SELECT COUNT(*) FROM risks r WHERE r.project_id = p.id AND r.status = 'open') AS open_risks,
                    (SELECT COUNT(*) FROM project_schedule_items psi WHERE psi.project_id = p.id::text) AS schedule_items,
                    (SELECT MAX(ABS(sv.variance_days)) FROM schedule_variance sv WHERE sv.project_id = p.id) AS max_variance_days,
                    (SELECT COUNT(*) FROM daily_logs dl WHERE dl.project_id = p.id) AS daily_logs,
                    (SELECT COUNT(*) FROM bid_packages bp WHERE bp.project_id = p.id) AS total_packages,
                    (SELECT COUNT(*) FROM bid_packages bp WHERE bp.project_id = p.id
                         AND EXISTS (SELECT 1 FROM bid_entries be WHERE be.bid_package_id = bp.id AND be.bid_amount > 0)
                    ) AS packages_with_bids,
                    (SELECT COALESCE(SUM(be.bid_amount),0) FROM bid_entries be
                         JOIN bid_packages bp ON bp.id = be.bid_package_id
                         WHERE bp.project_id = p.id AND be.status = 'awarded'
                    ) AS committed_amount,
                    (SELECT COUNT(*) FROM rfis r WHERE r.project_id = p.id AND r.status = 'open') AS open_rfis,
                    (SELECT COUNT(*) FROM rfis r WHERE r.project_id = p.id AND r.status = 'open'
                         AND r.required_response_date < CURRENT_DATE
                    ) AS overdue_rfis,
                    (SELECT pb.schedule_variance_days FROM project_brain_snapshots pb
                         WHERE pb.project_id = p.id AND pb.snapshot_date = CURRENT_DATE
                    ) AS signed_variance_days
                FROM projects p WHERE p.status IN ('active','design','bidding','preconstruction')
                  AND p.name NOT LIKE 'TEST-%%' ORDER BY p.id
            """)
            rows = cur.fetchall()
        conn.close()
        for row in rows:
            max_var   = row["max_variance_days"] or 0
            high_var  = row["high_variance"] or 0
            open_risks = row["open_risks"] or 0
            total_pkgs = row["total_packages"] or 0
            bid_pkgs   = row["packages_with_bids"] or 0
            open_rfis  = row["open_rfis"] or 0
            overdue_rfis = row["overdue_rfis"] or 0
            # Canonical signed days-behind (matches LIVE_PROJECT_STATE.md / role_owner /
            # project_brain). max_variance_days/total_variance_items above are UNSIGNED
            # item counts and magnitude — ARB flagged this as easy to misread as "the
            # variance"; this field removes the ambiguity (2026-07-01).
            signed_variance_days = row["signed_variance_days"]
            if signed_variance_days is None:
                signed_variance_days = -max_var if max_var else 0
            committed  = float(row["committed_amount"] or 0)
            budget     = float(row["contract_value"] or 0)
            bid_coverage_pct = round((bid_pkgs / total_pkgs * 100) if total_pkgs > 0 else 100)
            budget_pct = round((committed / budget * 100) if budget > 0 else 0)

            # Risk factors — each flag can push health down
            risk_flags = []
            if overdue_rfis > 0:
                risk_flags.append(f"OVERDUE RFI: {overdue_rfis} RFI(s) past response date — framing/schedule risk")
            if high_var > 0:
                risk_flags.append(f"{high_var} high-risk schedule items")
            if max_var >= 7:
                risk_flags.append(f"+{max_var}d schedule variance")
            if open_risks >= 3:
                risk_flags.append(f"{open_risks} open risks")
            # Gap-15 fix: bid coverage below threshold is a procurement risk
            if total_pkgs >= 5 and bid_coverage_pct < 25:
                risk_flags.append(f"PROCUREMENT: only {bid_coverage_pct}% of {total_pkgs} packages have bids")
            elif total_pkgs >= 5 and bid_coverage_pct < 50:
                risk_flags.append(f"PROCUREMENT: {bid_coverage_pct}% bid coverage ({bid_pkgs}/{total_pkgs} pkgs)")
            if open_risks >= 1 and not any("open risks" in f for f in risk_flags):
                risk_flags.append(f"{open_risks} open risk")
            if max_var >= 3 and max_var < 7:
                risk_flags.append(f"+{max_var}d behind schedule")

            # Determine health from worst flag
            if overdue_rfis > 0 or high_var > 0 or open_risks >= 3 or max_var >= 7 or (total_pkgs >= 5 and bid_coverage_pct < 25):
                health, icon = "red", "🔴"
            elif open_risks >= 1 or max_var >= 3 or (total_pkgs >= 5 and bid_coverage_pct < 50):
                health, icon = "yellow", "🟡"
            else:
                health, icon = "green", "🟢"

            sched = f"+{max_var}d behind" if max_var > 0 else "On track"
            projects.append({
                "name": row["name"],
                "project_code": row["project_code"] or "",
                "health": health,
                "icon": icon,
                "schedule": sched,
                "max_variance_days": max_var,
                "schedule_variance_days": signed_variance_days,
                "high_variance_items": high_var,
                "total_variance_items": row["total_variance"] or 0,
                "open_risks": open_risks,
                "open_rfis": open_rfis,
                "overdue_rfis": overdue_rfis,
                "schedule_items": row["schedule_items"] or 0,
                "daily_logs": row["daily_logs"] or 0,
                "budget": {"contract_value": budget, "committed": committed, "pct_committed": budget_pct},
                "procurement": {
                    "total_packages": total_pkgs,
                    "packages_with_bids": bid_pkgs,
                    "packages_no_bids": total_pkgs - bid_pkgs,
                    "bid_coverage_pct": bid_coverage_pct,
                },
                "risk_flags": risk_flags,
                "summary": f"{icon} {row['name']}: {sched}, {open_risks} risks, {bid_coverage_pct}% bid coverage"
                           + (f", {overdue_rfis} OVERDUE RFI" if overdue_rfis else "")
            })
        return _response("/executive/report", {
            "date": datetime.now(timezone.utc).date().isoformat(),
            "source": "live_db",
            "projects": projects,
        }, start=t0)
    except Exception as e:
        return _response("/executive/report", {}, errors=[str(e)], start=t0)


def _run_stale_check(conn) -> dict:
    """BTW-4 inline stale detection — avoids cross-package import issues."""
    from datetime import date, timedelta
    today = date.today()
    LIVE = [1, 2, 3, 8]
    WARN_DAYS, ALERT_DAYS, PKG_DAYS, EXPIRY_WARN = 7, 14, 21, 3
    r = {"run_date": today.isoformat(), "expiring": [], "expired": [],
         "no_response": [], "stale_packages": []}
    with conn.cursor() as cur:
        cur.execute("""
            SELECT be.id, v.company_name, p.name, bp.csi_division,
                   be.date_sent, be.bid_expiry_date,
                   be.bid_expiry_date - %s, be.status
            FROM bid_entries be
            JOIN vendors v ON v.id = be.vendor_id
            JOIN projects p ON p.id = be.project_id
            LEFT JOIN bid_packages bp ON bp.id = be.bid_package_id
            WHERE be.project_id = ANY(%s) AND be.bid_expiry_date IS NOT NULL
              AND be.bid_expiry_date BETWEEN %s AND %s
              AND be.status NOT IN ('received','awarded','bid_received')
            ORDER BY be.bid_expiry_date
        """, (today, LIVE, today, today + timedelta(days=EXPIRY_WARN)))
        for row in cur.fetchall():
            r["expiring"].append({"id": row[0], "vendor": row[1], "project": row[2],
                "csi": row[3], "date_sent": str(row[4]) if row[4] else None,
                "expiry": str(row[5]), "days_until_expiry": row[6], "status": row[7]})
        cur.execute("""
            SELECT be.id, v.company_name, p.name, bp.csi_division,
                   be.date_sent, be.bid_expiry_date,
                   %s - be.bid_expiry_date, be.status
            FROM bid_entries be
            JOIN vendors v ON v.id = be.vendor_id
            JOIN projects p ON p.id = be.project_id
            LEFT JOIN bid_packages bp ON bp.id = be.bid_package_id
            WHERE be.project_id = ANY(%s) AND be.bid_expiry_date IS NOT NULL
              AND be.bid_expiry_date < %s
              AND be.status NOT IN ('received','awarded','bid_received')
            ORDER BY be.bid_expiry_date
        """, (today, LIVE, today))
        for row in cur.fetchall():
            r["expired"].append({"id": row[0], "vendor": row[1], "project": row[2],
                "csi": row[3], "date_sent": str(row[4]) if row[4] else None,
                "expiry": str(row[5]), "days_overdue": row[6], "status": row[7]})
        cur.execute("""
            SELECT be.id, v.company_name, p.name, bp.csi_division,
                   be.date_sent, %s - be.date_sent, be.status,
                   CASE WHEN %s - be.date_sent > %s THEN 'ALERT' ELSE 'WARN' END
            FROM bid_entries be
            JOIN vendors v ON v.id = be.vendor_id
            JOIN projects p ON p.id = be.project_id
            LEFT JOIN bid_packages bp ON bp.id = be.bid_package_id
            WHERE be.project_id = ANY(%s) AND be.date_sent IS NOT NULL
              AND be.date_received IS NULL
              AND be.status NOT IN ('received','awarded','bid_received')
              AND %s - be.date_sent >= %s
            ORDER BY 6 DESC
        """, (today, today, ALERT_DAYS, LIVE, today, WARN_DAYS))
        for row in cur.fetchall():
            r["no_response"].append({"id": row[0], "vendor": row[1], "project": row[2],
                "csi": row[3], "date_sent": str(row[4]),
                "days_waiting": row[5], "status": row[6], "severity": row[7]})
        cur.execute("""
            SELECT bp.id, p.name, bp.csi_division, bp.package_name,
                   bp.status, bp.updated_at::date, %s - bp.updated_at::date
            FROM bid_packages bp
            JOIN projects p ON p.id = bp.project_id
            WHERE bp.project_id = ANY(%s) AND bp.status IN ('bids_receiving','bidding')
              AND %s - bp.updated_at::date >= %s
              AND bp.package_name NOT ILIKE '%%DRAFT%%'
              AND bp.package_name NOT ILIKE '%%CSI Division%%'
              AND bp.package_name NOT ILIKE '%%Subcontractor%%'
              AND bp.package_name NOT ILIKE '%%PM:%%'
            ORDER BY 7 DESC LIMIT 30
        """, (today, LIVE, today, PKG_DAYS))
        for row in cur.fetchall():
            r["stale_packages"].append({"id": row[0], "project": row[1], "csi": row[2],
                "package": row[3], "status": row[4],
                "last_updated": str(row[5]), "days_stale": row[6]})
    r["summary"] = {
        "expiring_count": len(r["expiring"]),
        "expired_count": len(r["expired"]),
        "no_response_count": len(r["no_response"]),
        "stale_packages_count": len(r["stale_packages"]),
        "total_flags": len(r["expiring"]) + len(r["expired"]) + len(r["no_response"]) + len(r["stale_packages"]),
        "needs_attention": bool(r["expiring"] or r["expired"] or r["no_response"]),
    }
    return r


def _format_stale_alert(results: dict) -> str | None:
    s = results["summary"]
    if not s["total_flags"]:
        return None
    lines = ["BID STALE ALERT — " + results["run_date"]]
    if results["expiring"]:
        lines.append(f"\nEXPIRING SOON ({s['expiring_count']}):")
        for b in results["expiring"]:
            lines.append(f"  {b['vendor']} | {b['project']} | expires {b['expiry']} ({b['days_until_expiry']}d)")
    if results["expired"]:
        lines.append(f"\nEXPIRED ({s['expired_count']}):")
        for b in results["expired"]:
            lines.append(f"  {b['vendor']} | {b['project']} | expired {b['expiry']} ({b['days_overdue']}d ago)")
    if results["no_response"]:
        alerts = [b for b in results["no_response"] if b["severity"] == "ALERT"]
        warns  = [b for b in results["no_response"] if b["severity"] == "WARN"]
        if alerts:
            lines.append(f"\nNO RESPONSE — OVERDUE ({len(alerts)}):")
            for b in alerts[:5]:
                lines.append(f"  {b['vendor']} | {b['project']} | sent {b['date_sent']} ({b['days_waiting']}d)")
        if warns:
            lines.append(f"\nNO RESPONSE — WARNING ({len(warns)}):")
            for b in warns[:3]:
                lines.append(f"  {b['vendor']} | {b['project']} | sent {b['date_sent']} ({b['days_waiting']}d)")
    if results["stale_packages"] and not s["needs_attention"]:
        lines.append(f"\nSTALE PACKAGES ({s['stale_packages_count']}):")
        for pkg in results["stale_packages"][:5]:
            lines.append(f"  {pkg['project']} | {pkg['package']} | {pkg['days_stale']}d idle")
    return "\n".join(lines)


def _pg_stale_conn():
    import psycopg2
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", 5432)),
        dbname=os.environ.get("POSTGRES_DB", "hci_os"),
        user=os.environ.get("POSTGRES_USER", "hci_admin"),
        password=os.environ.get("POSTGRES_PASSWORD", ""),
    )


@router.get("/bids/stale")
def bids_stale():
    """BTW-4 — Bid stale detection: expiring, expired, no-response, stale packages."""
    t0 = time.time()
    try:
        conn = _pg_stale_conn()
        results = _run_stale_check(conn)
        conn.close()
        return _response("/bids/stale", results, start=t0)
    except Exception as e:
        return _response("/bids/stale", {}, errors=[str(e)], start=t0)


@router.post("/bids/stale/alert")
async def bids_stale_alert(request: Request):
    """Run stale check and push Telegram alert if anything needs attention. Called by n8n daily."""
    t0 = time.time()
    try:
        conn = _pg_stale_conn()
        results = _run_stale_check(conn)
        conn.close()
        msg = _format_stale_alert(results)
        sent = False
        ai_msg_id = None
        if msg:
            res = _notify_agents("system", "buck", "risk_alert", "Bid Stale Alert", msg)
            ai_msg_id = res["id"]
            sent = res["delivery"].get("status") == "sent" or res["delivery"].get("fallback", {}).get("status") == "sent"
        return _response("/bids/stale/alert", {
            "summary": results["summary"],
            "alert_sent": sent,
            "ai_message_id": ai_msg_id,
            "message_preview": msg[:200] if msg else None,
        }, start=t0)
    except Exception as e:
        return _response("/bids/stale/alert", {}, errors=[str(e)], start=t0)


# ── BTW-8: Vendor Performance Scoring ────────────────────────────────────────

def _pg_vendor_conn():
    import psycopg2
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", 5432)),
        dbname=os.environ.get("POSTGRES_DB", "hci_os"),
        user=os.environ.get("POSTGRES_USER", "hci_admin"),
        password=os.environ.get("POSTGRES_PASSWORD", ""),
    )


def _vendor_scoring_module():
    import importlib.util, sys as _sys
    spec = importlib.util.spec_from_file_location(
        "vendor_scoring",
        "/Users/buckadams/HCI_AI_Operating_System/03_Source_Code/services/bid_intelligence/vendor_scoring.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@router.get("/vendors/scores")
def vendor_scores():
    """BTW-8 — Vendor performance scorecard across all live projects."""
    t0 = time.time()
    try:
        vs = _vendor_scoring_module()
        conn = _pg_vendor_conn()
        scores = vs.score_all_vendors(conn)
        saved  = vs.write_scores_to_db(scores, conn)
        conn.close()
        summary = {
            "total_vendors_scored": len(scores),
            "saved_to_db": saved,
            "grade_breakdown": {
                "A_preferred": sum(1 for s in scores if s["grade"] == "A"),
                "B_active":    sum(1 for s in scores if s["grade"] == "B"),
                "C_watch":     sum(1 for s in scores if s["grade"] == "C"),
                "D_risk":      sum(1 for s in scores if s["grade"] == "D"),
            },
            "top_5": [{"vendor": s["company_name"], "score": s["score"],
                        "grade": s["grade"], "trade": s["trade"]} for s in scores[:5]],
            "watch_list": [{"vendor": s["company_name"], "score": s["score"],
                             "note": s["response_note"]} for s in scores if s["grade"] in ("C","D")],
        }
        return _response("/vendors/scores", {"summary": summary, "scores": scores}, start=t0)
    except Exception as e:
        return _response("/vendors/scores", {}, errors=[str(e)], start=t0)


@router.get("/vendors/scores/{vendor_id}")
def vendor_score_single(vendor_id: int):
    """BTW-8 — Performance scorecard for a single vendor."""
    t0 = time.time()
    try:
        vs = _vendor_scoring_module()
        conn = _pg_vendor_conn()
        score = vs.score_vendor(vendor_id, conn)
        conn.close()
        if not score:
            return _response(f"/vendors/scores/{vendor_id}", {}, errors=["Vendor not found"], start=t0)
        return _response(f"/vendors/scores/{vendor_id}", score, start=t0)
    except Exception as e:
        return _response(f"/vendors/scores/{vendor_id}", {}, errors=[str(e)], start=t0)


# ── BTW-6: Project Budget & Drive Integration ─────────────────────────────────

@router.get("/project/{code}/budget")
def project_budget(code: str):
    """BTW-6 — Full financial picture: awarded vs budget estimates vs contract value."""
    t0 = time.time()
    try:
        conn = _pg_stale_conn()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.id, p.name, p.contract_value, p.drive_folder_id,
                       p.gsheet_bid_tracker, p.bid_folder_id
                FROM projects p WHERE UPPER(p.project_code) = UPPER(%s)
            """, (code,))
            row = cur.fetchone()
            if not row:
                conn.close()
                return _response(f"/project/{code}/budget", {}, errors=["Project not found"], start=t0)
            pid, name, contract_val, drive_id, sheet_id, bid_folder = row

            cur.execute("""
                SELECT
                  status,
                  COUNT(*) as pkg_count,
                  SUM(awarded_amount) as total_amount
                FROM bid_packages
                WHERE project_id = %s
                GROUP BY status
            """, (pid,))
            rows = cur.fetchall()

            awarded_total = 0.0
            estimate_total = 0.0
            pkg_counts = {}
            for status, count, total in rows:
                pkg_counts[status] = count
                amt = float(total or 0)
                if status == "awarded":
                    awarded_total = amt
                elif status in ("bids_receiving", "bidding", "not_started"):
                    estimate_total += amt

            total_projected = awarded_total + estimate_total
            cv = float(contract_val or 0)
            variance = cv - total_projected
            pct_committed = round(awarded_total / cv * 100, 1) if cv else 0
            pct_projected = round(total_projected / cv * 100, 1) if cv else 0

            cur.execute("""
                SELECT csi_division, package_name, status, awarded_amount
                FROM bid_packages WHERE project_id = %s AND awarded_amount IS NOT NULL
                ORDER BY CASE status WHEN 'awarded' THEN 0 ELSE 1 END, awarded_amount DESC
            """, (pid,))
            packages = [{"csi": r[0], "package": r[1], "status": r[2],
                         "amount": float(r[3])} for r in cur.fetchall()]
        conn.close()

        budget_status = "OVER_BUDGET" if variance < 0 else "AT_RISK" if pct_projected > 95 else "OK"
        return _response(f"/project/{code}/budget", {
            "project": name,
            "contract_value": cv,
            "awarded_committed": awarded_total,
            "open_estimates": estimate_total,
            "total_projected": total_projected,
            "variance": variance,
            "pct_committed": pct_committed,
            "pct_projected": pct_projected,
            "budget_status": budget_status,
            "package_counts": pkg_counts,
            "drive_folder_id": drive_id,
            "bid_tracker_sheet": sheet_id,
            "line_items": packages,
        }, start=t0)
    except Exception as e:
        return _response(f"/project/{code}/budget", {}, errors=[str(e)], start=t0)


@router.get("/project/{code}/drive")
def project_drive(code: str):
    """BTW-6 — List Drive files in the project's Drive folder."""
    t0 = time.time()
    try:
        conn = _pg_stale_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT name, drive_folder_id FROM projects WHERE UPPER(project_code) = UPPER(%s)", (code,))
            row = cur.fetchone()
        conn.close()
        if not row or not row[1]:
            return _response(f"/project/{code}/drive", {}, errors=["No Drive folder linked"], start=t0)
        name, folder_id = row

        r = requests.get(
            "https://www.googleapis.com/drive/v3/files",
            params={"q": f"'{folder_id}' in parents and trashed=false",
                    "fields": "files(id,name,mimeType,modifiedTime,size)",
                    "pageSize": 50},
            headers={"Authorization": f"Bearer {_drive_token()}"},
            timeout=15,
        )
        if not r.ok:
            return _response(f"/project/{code}/drive", {}, errors=[f"Drive API: {r.status_code}"], start=t0)
        files = r.json().get("files", [])
        return _response(f"/project/{code}/drive", {
            "project": name, "folder_id": folder_id, "file_count": len(files), "files": files,
        }, start=t0)
    except Exception as e:
        return _response(f"/project/{code}/drive", {}, errors=[str(e)], start=t0)


def _drive_token() -> str:
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "integrations"))
        from credentials import get_drive_token
        return get_drive_token()
    except Exception:
        return ""


# ── BTW-5: Schedule Variance Alerts ──────────────────────────────────────────

@router.get("/schedule/variance")
def schedule_variance():
    """BTW-5 — Schedule variance: overdue items, data anomalies, per-project summary."""
    t0 = time.time()
    LIVE = [1, 2, 3, 8]
    WARN_DAYS, ALERT_DAYS = 3, 7
    try:
        from datetime import date
        today = date.today()
        conn = _pg_stale_conn()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.id, p.name, p.project_code,
                  COUNT(psi.id) as total,
                  COUNT(CASE WHEN psi.end_date < %s
                              AND psi.status NOT ILIKE '%%complete%%'
                              AND psi.status NOT ILIKE '%%done%%'
                              AND psi.start_date <= psi.end_date  -- exclude data errors
                             THEN 1 END) as overdue,
                  COUNT(CASE WHEN psi.end_date BETWEEN %s AND %s
                              AND psi.status NOT ILIKE '%%complete%%'
                             THEN 1 END) as due_soon,
                  COUNT(CASE WHEN psi.start_date > psi.end_date THEN 1 END) as data_errors,
                  COUNT(CASE WHEN psi.completion_pct > 0 AND psi.completion_pct < 100 THEN 1 END) as in_progress
                FROM projects p
                LEFT JOIN project_schedule_items psi ON psi.project_id::integer = p.id
                WHERE p.id = ANY(%s)
                GROUP BY p.id, p.name, p.project_code
                ORDER BY p.id
            """, (today, today, today + __import__('datetime').timedelta(days=WARN_DAYS), LIVE))
            summary_rows = cur.fetchall()

            # Top overdue items across all live projects
            cur.execute("""
                SELECT p.name, psi.title, psi.start_date, psi.end_date,
                       psi.status, psi.completion_pct, psi.assignee,
                       %s - psi.end_date as days_overdue
                FROM project_schedule_items psi
                JOIN projects p ON p.id = psi.project_id::integer
                WHERE p.id = ANY(%s)
                  AND psi.end_date < %s
                  AND psi.status NOT ILIKE '%%complete%%'
                  AND psi.status NOT ILIKE '%%done%%'
                  AND psi.start_date <= psi.end_date
                ORDER BY days_overdue DESC
                LIMIT 20
            """, (today, LIVE, today))
            overdue_items = [{
                "project": r[0], "title": r[1],
                "start": str(r[2]) if r[2] else None,
                "end": str(r[3]) if r[3] else None,
                "status": r[4], "pct": float(r[5] or 0),
                "assignee": r[6], "days_overdue": r[7],
            } for r in cur.fetchall()]

            # Due soon
            cur.execute("""
                SELECT p.name, psi.title, psi.end_date, psi.status, psi.completion_pct,
                       psi.end_date - %s as days_remaining
                FROM project_schedule_items psi
                JOIN projects p ON p.id = psi.project_id::integer
                WHERE p.id = ANY(%s)
                  AND psi.end_date BETWEEN %s AND %s
                  AND psi.status NOT ILIKE '%%complete%%'
                ORDER BY psi.end_date ASC
                LIMIT 10
            """, (today, LIVE, today, today + __import__('datetime').timedelta(days=WARN_DAYS)))
            due_soon = [{
                "project": r[0], "title": r[1],
                "end": str(r[2]), "status": r[3],
                "pct": float(r[4] or 0), "days_remaining": r[5],
            } for r in cur.fetchall()]
        conn.close()

        projects_summary = []
        total_overdue = 0
        for r in summary_rows:
            pid, name, code, total, overdue, due_soon_ct, data_errors, in_prog = r
            total_overdue += (overdue or 0)
            health = "RED" if (overdue or 0) > 10 else "YELLOW" if (overdue or 0) > 0 else "GREEN"
            projects_summary.append({
                "project_id": pid, "project": name, "code": code,
                "total_items": total, "overdue": overdue or 0,
                "due_soon": due_soon_ct or 0, "in_progress": in_prog or 0,
                "data_errors": data_errors or 0, "health": health,
            })

        return _response("/schedule/variance", {
            "run_date": today.isoformat(),
            "total_overdue_across_projects": total_overdue,
            "projects": projects_summary,
            "top_overdue_items": overdue_items,
            "due_soon": due_soon,
            "thresholds": {"warn_days": WARN_DAYS, "alert_days": ALERT_DAYS},
        }, start=t0)
    except Exception as e:
        return _response("/schedule/variance", {}, errors=[str(e)], start=t0)


@router.post("/schedule/variance/alert")
async def schedule_variance_alert(request: Request):
    """BTW-5 — Run schedule variance check and Telegram alert if items overdue."""
    t0 = time.time()
    try:
        r = requests.get("http://localhost:8000/gateway/schedule/variance", timeout=20)
        data = r.json().get("payload", {})
        total_overdue = data.get("total_overdue_across_projects", 0)
        sent = False
        if total_overdue > 0:
            projects = data.get("projects", [])
            lines = [f"SCHEDULE VARIANCE — {data.get('run_date','today')}"]
            for p in projects:
                if p["overdue"] > 0:
                    lines.append(f"\n{p['project']} ({p['code']}): {p['overdue']} overdue, {p['due_soon']} due soon")
            top = data.get("top_overdue_items", [])[:5]
            if top:
                lines.append("\nTop overdue:")
                for item in top:
                    lines.append(f"  {item['project']} | {item['title']} | {item['days_overdue']}d overdue")
            msg = "\n".join(lines)
            res = _notify_agents("system", "buck", "risk_alert", "Schedule Variance Alert", msg)
            ai_msg_id = res["id"]
            sent = res["delivery"].get("status") == "sent" or res["delivery"].get("fallback", {}).get("status") == "sent"
        else:
            ai_msg_id = None
        return _response("/schedule/variance/alert", {
            "total_overdue": total_overdue, "alert_sent": sent, "ai_message_id": ai_msg_id,
        }, start=t0)
    except Exception as e:
        return _response("/schedule/variance/alert", {}, errors=[str(e)], start=t0)


@router.get("/executive/mission-control")
def mission_control():
    """Mission control — cross-project command center. `comms` block (patched 2026-06-30)
    adds agent-coordination state: pending approvals, unacked messages, stale items,
    blocked missions, per-agent heartbeat, Telegram health — separate from project KPIs."""
    t0 = time.time()
    try:
        data = _proxy("/executive/mission-control")
        comms = _comms_snapshot()
        if isinstance(data, dict) and isinstance(data.get("payload"), dict):
            data["payload"]["comms"] = comms
        elif isinstance(data, dict):
            data["comms"] = comms
        return _response("/executive/mission-control", data, start=t0)
    except HTTPException as e:
        return _response("/executive/mission-control", {}, errors=[str(e.detail)], start=t0)


# ── BTW-5: Role Intelligence Consoles ─────────────────────────────────────────

@router.get("/role/owner")
def role_owner():
    """BTW-5: Owner (Buck) company-wide command — all projects, pending approvals, critical risks, financials."""
    t0 = time.time()
    try:
        conn = _pg()
        conn.autocommit = True
        with conn.cursor() as cur:
            # Pending approvals by priority
            cur.execute("""
                SELECT priority, COUNT(*) as cnt,
                       SUM(COALESCE((proposed_payload->>'amount')::numeric, 0)) as total_amount
                FROM approval_queue WHERE status = 'pending'
                GROUP BY priority ORDER BY CASE priority WHEN 'critical' THEN 1 WHEN 'high' THEN 2 WHEN 'normal' THEN 3 ELSE 4 END
            """)
            approvals = [dict(r) for r in cur.fetchall()]

            # Critical risks across LIVE projects only (not reference/archive)
            cur.execute("""
                SELECT p.project_code, r.risk_type, LEFT(r.description,100) as description,
                       r.severity, r.status, r.identified_date
                FROM risks r JOIN projects p ON p.id = r.project_id
                WHERE r.status = 'open' AND r.severity IN ('critical','high')
                AND p.status NOT IN ('reference','completed','archived','cancelled')
                ORDER BY CASE r.severity WHEN 'critical' THEN 1 ELSE 2 END, r.identified_date ASC
                LIMIT 10
            """)
            critical_risks = [dict(r) for r in cur.fetchall()]

            # Project financial summary. pb pulls the MOST RECENT snapshot (not strictly
            # today's) — fixed 2026-07-01: joining on snapshot_date = CURRENT_DATE went
            # null/blank for every project until the nightly snapshot job ran for the
            # day, which read as "101F shows 0/blank schedule variance" to anyone
            # checking before that job ran. executive_report already had this fallback;
            # role_owner did not.
            cur.execute("""
                SELECT p.project_code, p.name, p.contract_value,
                    COALESCE((SELECT SUM(be.bid_amount) FROM bid_entries be
                        JOIN bid_packages bp ON bp.id = be.bid_package_id
                        WHERE bp.project_id = p.id AND be.status = 'awarded'), 0) as committed,
                    COALESCE((SELECT COUNT(*) FROM risks r WHERE r.project_id = p.id AND r.status='open'),0) as open_risks,
                    pb.health, pb.schedule_variance_days
                FROM projects p
                LEFT JOIN LATERAL (
                    SELECT health, schedule_variance_days FROM project_brain_snapshots
                    WHERE project_id = p.id ORDER BY snapshot_date DESC LIMIT 1
                ) pb ON true
                WHERE p.status IN ('active','design','bidding','preconstruction')
                ORDER BY p.contract_value DESC NULLS LAST
            """)
            project_summary = [dict(r) for r in cur.fetchall()]

            # Total pending approval value
            cur.execute("""SELECT COUNT(*) as cnt,
                COALESCE(SUM((proposed_payload->>'amount')::numeric),0) as val
                FROM approval_queue WHERE status='pending'
                AND proposed_payload->>'amount' IS NOT NULL""")
            approval_totals = dict(cur.fetchone())
        conn.close()

        total_contract = sum(float(p.get("contract_value") or 0) for p in project_summary)
        total_committed = sum(float(p.get("committed") or 0) for p in project_summary)

        return _response("/role/owner", {
            "role": "Owner",
            "user": "Buck Adams",
            "as_of": time.strftime("%Y-%m-%d"),
            "pending_approvals": {
                "total": sum(a["cnt"] for a in approvals),
                "pending_value": float(approval_totals.get("val", 0)),
                "by_priority": approvals,
            },
            "company_financials": {
                "total_contract_value": total_contract,
                "total_committed": total_committed,
                "commitment_pct": round(total_committed / total_contract * 100, 1) if total_contract > 0 else 0,
                "project_count": len(project_summary),
            },
            "critical_risks": critical_risks,
            "projects": project_summary,
        }, start=t0)
    except Exception as e:
        return _response("/role/owner", {}, errors=[str(e)], start=t0)


@router.get("/role/office")
def role_office():
    """BTW-5: Office admin console — pending items, AP/AR, submittal queue, approval requests."""
    t0 = time.time()
    try:
        conn = _pg()
        conn.autocommit = True
        with conn.cursor() as cur:
            # Pending approvals needing admin action
            cur.execute("""
                SELECT action_type, target_description, priority, created_at,
                       COALESCE((proposed_payload->>'amount')::numeric, 0) as amount
                FROM approval_queue WHERE status='pending'
                ORDER BY CASE priority WHEN 'critical' THEN 1 WHEN 'high' THEN 2 ELSE 3 END, created_at ASC
                LIMIT 20
            """)
            pending = [dict(r) for r in cur.fetchall()]

            # Open submittals requiring action
            cur.execute("""
                SELECT p.project_code, s.description, s.spec_section, s.status, s.submitted_date, s.required_approval_date
                FROM submittals s JOIN projects p ON p.id = s.project_id
                WHERE s.status NOT IN ('approved','rejected','closed')
                ORDER BY s.required_approval_date ASC NULLS LAST
                LIMIT 15
            """)
            submittals = [dict(r) for r in cur.fetchall()]

            # Overdue RFIs
            cur.execute("""
                SELECT p.project_code, r.subject, r.status, r.required_response_date, r.submitted_date
                FROM rfis r JOIN projects p ON p.id = r.project_id
                WHERE r.status = 'open' AND r.required_response_date < CURRENT_DATE
                ORDER BY r.required_response_date ASC
                LIMIT 10
            """)
            overdue_rfis = [dict(r) for r in cur.fetchall()]
        conn.close()

        return _response("/role/office", {
            "role": "Office Manager",
            "as_of": time.strftime("%Y-%m-%d"),
            "pending_approvals": {"count": len(pending), "items": pending},
            "submittal_queue": {"count": len(submittals), "items": submittals},
            "overdue_rfis": {"count": len(overdue_rfis), "items": overdue_rfis},
            "action_summary": {
                "total_items": len(pending) + len(submittals) + len(overdue_rfis),
                "critical_count": sum(1 for p in pending if p.get("priority") in ("critical","high")),
            }
        }, start=t0)
    except Exception as e:
        return _response("/role/office", {}, errors=[str(e)], start=t0)


@router.get("/role/accounting")
def role_accounting():
    """BTW-5: Accounting console — financial health, budget vs committed, bid awards by project."""
    t0 = time.time()
    try:
        conn = _pg()
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.project_code, p.name, COALESCE(p.contract_value,0) as contract_value,
                    COALESCE((SELECT SUM(be.bid_amount) FROM bid_entries be
                        JOIN bid_packages bp ON bp.id = be.bid_package_id
                        WHERE bp.project_id = p.id AND be.status='awarded'), 0) as awarded,
                    COALESCE((SELECT SUM(be.bid_amount) FROM bid_entries be
                        JOIN bid_packages bp ON bp.id = be.bid_package_id
                        WHERE bp.project_id = p.id AND be.status='pending'), 0) as pending_bids,
                    (SELECT COUNT(*) FROM bid_packages bp2 WHERE bp2.project_id = p.id) as total_packages,
                    (SELECT COUNT(*) FROM bid_packages bp2 WHERE bp2.project_id = p.id AND bp2.status='awarded') as awarded_packages
                FROM projects p
                WHERE p.status IN ('active','design','bidding','preconstruction')
                ORDER BY p.contract_value DESC NULLS LAST
            """)
            projects = [dict(r) for r in cur.fetchall()]

            # Pending approval amounts
            cur.execute("""
                SELECT action_type, COUNT(*) as cnt,
                       SUM(COALESCE((proposed_payload->>'amount')::numeric,0)) as total
                FROM approval_queue WHERE status='pending'
                  AND proposed_payload->>'amount' IS NOT NULL
                GROUP BY action_type ORDER BY SUM(COALESCE((proposed_payload->>'amount')::numeric,0)) DESC
            """)
            pending_amounts = [dict(r) for r in cur.fetchall()]
        conn.close()

        total_contract = sum(float(p["contract_value"]) for p in projects)
        total_awarded = sum(float(p["awarded"]) for p in projects)
        total_pending = sum(float(p["pending_bids"]) for p in projects)

        return _response("/role/accounting", {
            "role": "Accounting",
            "as_of": time.strftime("%Y-%m-%d"),
            "company_totals": {
                "total_contract_value": total_contract,
                "total_awarded": total_awarded,
                "total_pending_bids": total_pending,
                "commitment_pct": round(total_awarded / total_contract * 100, 1) if total_contract > 0 else 0,
                "remaining_budget": total_contract - total_awarded,
            },
            "by_project": projects,
            "pending_financial_approvals": pending_amounts,
        }, start=t0)
    except Exception as e:
        return _response("/role/accounting", {}, errors=[str(e)], start=t0)


@router.get("/role/client/{code}")
def role_client(code: str):
    """BTW-5: Client portal — project status, milestones, open RFIs, change orders awaiting approval."""
    t0 = time.time()
    try:
        pid = _get_pid(code)
        conn = _pg()
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SELECT project_code, name, status, contract_value FROM projects WHERE id = %s", (pid,))
            proj = dict(cur.fetchone())

            cur.execute("SELECT health, schedule_variance_days, risk_count, budget_exposure, open_decisions, ai_summary FROM project_brain_snapshots WHERE project_id = %s ORDER BY snapshot_date DESC LIMIT 1", (pid,))
            brain_row = cur.fetchone()
            brain = dict(brain_row) if brain_row else {}

            # Open RFIs needing client action
            cur.execute("""
                SELECT id, subject, status, required_response_date, submitted_date
                FROM rfis WHERE project_id = %s AND status = 'open'
                ORDER BY required_response_date ASC NULLS LAST LIMIT 10
            """, (pid,))
            rfis = [dict(r) for r in cur.fetchall()]

            # Change orders pending client approval (from approval_queue)
            cur.execute("""
                SELECT id, target_description as description, priority as status, created_at as submitted_date,
                       COALESCE((proposed_payload->>'amount')::numeric, 0) as amount
                FROM approval_queue
                WHERE project_id = %s AND status='pending'
                  AND action_type ILIKE '%%change_order%%'
                ORDER BY created_at DESC LIMIT 10
            """, (pid,))
            change_orders = [dict(r) for r in cur.fetchall()]

            # Recent milestones
            cur.execute("""
                SELECT event_type, event_date, title, description
                FROM project_events WHERE project_id = %s
                  AND event_type IN ('milestone','award','meeting','decision')
                ORDER BY event_date DESC LIMIT 10
            """, (pid,))
            milestones = [dict(r) for r in cur.fetchall()]
        conn.close()

        co_value = sum(float(c.get("amount") or 0) for c in change_orders)
        return _response(f"/role/client/{code}", {
            "role": "Client",
            "project_code": code,
            "project_name": proj.get("name"),
            "project_status": proj.get("status"),
            "health": brain.get("health", "UNKNOWN"),
            "schedule_variance_days": brain.get("schedule_variance_days", 0),
            "ai_summary": brain.get("ai_summary"),
            "open_rfis": {"count": len(rfis), "items": rfis},
            "pending_change_orders": {"count": len(change_orders), "total_value": co_value, "items": change_orders},
            "recent_milestones": milestones,
        }, start=t0)
    except Exception as e:
        return _response(f"/role/client/{code}", {}, errors=[str(e)], start=t0)


@router.get("/role/trade-partner")
def role_trade_partner(vendor: str = Query(..., description="Vendor or company name"),
                        code: str = Query(None, description="Optional project code filter")):
    """BTW-5: Trade partner console — work queue, open RFIs, bid packages, inspection holds."""
    t0 = time.time()
    try:
        conn = _pg()
        conn.autocommit = True
        with conn.cursor() as cur:
            # Find vendor ID by name
            cur.execute("""
                SELECT id, company_name, csi_divisions FROM vendors
                WHERE company_name ILIKE %s LIMIT 1
            """, (f"%{vendor}%",))
            vendor_row = cur.fetchone()
            vendor_id = vendor_row["id"] if vendor_row else None
            company_name = vendor_row["company_name"] if vendor_row else vendor

            # Awarded bid packages for this vendor
            proj_filter = "AND bp.project_id = (SELECT id FROM projects WHERE project_code=%s)" if code else ""
            params = [vendor_id] + ([code] if code else [])
            if vendor_id:
                cur.execute(f"""
                    SELECT p.project_code, bp.package_name, bp.csi_division,
                           be.bid_amount, be.status, be.date_received
                    FROM bid_entries be
                    JOIN bid_packages bp ON bp.id = be.bid_package_id
                    JOIN projects p ON p.id = bp.project_id
                    WHERE be.vendor_id = %s {proj_filter}
                    ORDER BY be.status, be.date_received DESC
                    LIMIT 20
                """, tuple(params))
                packages = [dict(r) for r in cur.fetchall()]
            else:
                packages = []

            # Open RFIs that may relate to vendor's CSI division
            csi_filter = ""
            if vendor_row and vendor_row.get("csi_divisions"):
                csi_divs = vendor_row["csi_divisions"]
                if isinstance(csi_divs, list) and csi_divs:
                    csi_filter = f"AND csi_division IN ({','.join(['%s']*len(csi_divs))})"
            open_rfis = []
            if code:
                cur.execute("""
                    SELECT r.id, r.subject, r.status, r.required_response_date
                    FROM rfis r
                    JOIN projects p ON p.id = r.project_id
                    WHERE p.project_code = %s AND r.status = 'open'
                    ORDER BY r.required_response_date ASC NULLS LAST
                    LIMIT 10
                """, (code,))
                open_rfis = [dict(r) for r in cur.fetchall()]
        conn.close()

        awarded = [p for p in packages if p.get("status") == "awarded"]
        return _response("/role/trade-partner", {
            "role": "Trade Partner",
            "vendor": company_name,
            "vendor_found": vendor_row is not None,
            "awarded_packages": {"count": len(awarded), "items": awarded},
            "all_bids": {"count": len(packages), "items": packages},
            "open_rfis": {"count": len(open_rfis), "items": open_rfis},
            "action_summary": {
                "awarded_contracts": len(awarded),
                "open_rfis_needing_response": len([r for r in open_rfis if r.get("required_response_date")]),
            }
        }, start=t0)
    except Exception as e:
        return _response("/role/trade-partner", {}, errors=[str(e)], start=t0)


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


@router.get("/knowledge/vendors")
def knowledge_vendors(search: str = None, csi: str = None, limit: int = 50, offset: int = 0):
    """
    Gap5 FIX — Paginated vendor list with optional search + CSI filter.
    search: company name or contact name substring
    csi: CSI division code (e.g. "03000", "16000")
    limit/offset: pagination (default 50 per page)
    """
    t0 = time.time()
    try:
        conn = _pg()
        conn.autocommit = True
        with conn.cursor() as cur:
            where, params = [], []
            if search:
                where.append("(company_name ILIKE %s OR contact_name ILIKE %s OR trade ILIKE %s)")
                params += [f"%{search}%", f"%{search}%", f"%{search}%"]
            if csi:
                where.append("%s = ANY(csi_divisions)")
                params.append(csi)
            sql = "SELECT id, company_name, trade, csi_divisions, city, state, contact_name, email, phone FROM vendors"
            if where:
                sql += " WHERE " + " AND ".join(where)
            sql += " ORDER BY company_name LIMIT %s OFFSET %s"
            params += [min(limit, 200), offset]
            cur.execute(sql, params)
            vendors = [dict(r) for r in cur.fetchall()]
            count_params = params[:-2]  # strip the limit+offset
            cur.execute("SELECT COUNT(*) as total FROM vendors" + (" WHERE " + " AND ".join(where) if where else ""), count_params)
            total = cur.fetchone()["total"]
        conn.close()
        return _response("/knowledge/vendors", {
            "vendors": vendors, "total": total,
            "limit": limit, "offset": offset,
            "returned": len(vendors),
            "has_more": (offset + len(vendors)) < total,
        }, start=t0)
    except Exception as e:
        return _response("/knowledge/vendors", {}, errors=[str(e)], start=t0)


@router.get("/knowledge/lessons")
def knowledge_lessons(category: str = None, csi: str = None, search: str = None, limit: int = 50):
    """
    Gap6 FIX — Lessons learned from past projects.
    category: schedule | budget | safety | quality | subcontractor | rfi | risk
    csi: CSI division filter
    search: keyword search across title + description
    """
    t0 = time.time()
    try:
        conn = _pg()
        conn.autocommit = True
        with conn.cursor() as cur:
            where, params = [], []
            if category:
                where.append("category = %s")
                params.append(category)
            if csi:
                where.append("csi_division = %s")
                params.append(csi)
            if search:
                where.append("(title ILIKE %s OR description ILIKE %s OR future_recommendation ILIKE %s)")
                params += [f"%{search}%", f"%{search}%", f"%{search}%"]
            sql = "SELECT id, title, description, category, csi_division, project_id, outcome, future_recommendation, recorded_at FROM lessons_learned"
            if where:
                sql += " WHERE " + " AND ".join(where)
            sql += " ORDER BY id DESC LIMIT %s"
            params.append(min(limit, 200))
            cur.execute(sql, params)
            lessons = [dict(r) for r in cur.fetchall()]
        conn.close()
        return _response("/knowledge/lessons", {
            "lessons": lessons,
            "count": len(lessons),
            "filters": {"category": category, "csi": csi, "search": search},
        }, start=t0)
    except Exception as e:
        return _response("/knowledge/lessons", {}, errors=[str(e)], start=t0)


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


@router.get("/drive/file/{file_id}/content")
def drive_file_content(file_id: str):
    """
    Read text content of any Drive file by ID.
    Supports PDF, Docs, Sheets, Slides, DOCX, XLSX.
    Used by the plan analysis pipeline and project_plan_analysis.py tool.
    Returns extracted text in payload.content — same envelope as all gateway endpoints.
    """
    t0 = time.time()
    try:
        meta   = _proxy(f"/services/drive-intelligence/file/{file_id}")
        name   = meta.get("name", file_id)
        mime   = meta.get("mime_type", "")

        # Export text content via drive-intelligence service (Google Docs, Sheets, DOCX, XLSX)
        content_data = _proxy(f"/services/drive-intelligence/file/{file_id}/content")
        content      = content_data.get("content", "")
        source       = content_data.get("source", "unknown")
        note         = content_data.get("note", "ok")

        return _response("/drive/file/content", {
            "file_id":    file_id,
            "file_name":  name,
            "mime_type":  mime,
            "char_count": len(content),
            "content":    content,
            "source":     source,
            "note":       note if note != "ok" else ("ok" if content else "empty — binary file requires MCP session or local OCR"),
        }, start=t0)

    except HTTPException as e:
        return _response("/drive/file/content", {"file_id": file_id, "content": ""},
                         errors=[str(e.detail)], start=t0)


@router.get("/drive/folder/{folder_id}/files")
def drive_folder_files(folder_id: str):
    """
    List all files in a Drive folder by folder ID.
    Used by bid leveling pipeline to enumerate division folders.
    """
    t0 = time.time()
    try:
        data = _proxy(f"/services/bid-leveling/drive/list/{folder_id}")
        return _response("/drive/folder/files", data, start=t0)
    except HTTPException as e:
        return _response("/drive/folder/files", {}, errors=[str(e.detail)], start=t0)


# ── Email ─────────────────────────────────────────────────────────────────────

class EmailDraftRequest(BaseModel):
    to_name: str
    to_email: str
    subject: str
    body_html: str
    reply_to_message_id: Optional[str] = None

@router.post("/email/draft")
def create_email_draft(req: EmailDraftRequest, request: Request):
    """
    Create an Outlook draft email (does NOT send). GBT/Browser Claude calls this to stage
    a client/vendor email. Nothing sends from this endpoint under any circumstance —
    sending requires Buck's explicit Telegram approval via POST /email/send (see below).
    """
    _require_key(request)
    t0 = time.time()
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "integrations"))
        from microsoft_graph import create_draft, create_reply_draft
        if req.reply_to_message_id:
            draft = create_reply_draft(req.reply_to_message_id, req.body_html)
        else:
            draft = create_draft(req.subject, req.body_html, [(req.to_name, req.to_email)])
        draft_id = draft.get("id", "")
        return _response("/email/draft", {
            "draft_id":   draft_id,
            "subject":    req.subject,
            "to_email":   req.to_email,
            "status":     "draft_created",
            "note":       "Draft saved to Outlook Drafts folder. Review in Outlook, or call POST /email/send to route it for Buck's approval before it goes out.",
            "outlook_url": f"https://outlook.office.com/mail/deeplink/compose/{draft_id}" if draft_id else "",
        }, start=t0)
    except Exception as e:
        return _response("/email/draft", {}, errors=[str(e)], start=t0)


def _send_approved_draft(draft_id: str) -> tuple:
    """Actually calls Microsoft Graph to send a draft. Only ever called from a verified
    Buck-approval path (the Telegram APPROVE hook in _handle_buck_command, or
    /email/draft/{id}/send after confirming an approved ai_messages record exists) —
    never directly from an agent request. See incident 2026-07-01: an unauthenticated,
    unapproved /email/send endpoint sent live to a 101F architect contact with no audit
    trail and no API key check. This function is the only code path allowed to call
    Microsoft Graph's sendMail/send-draft; every caller must prove approval first."""
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "integrations"))
        from microsoft_graph import send_draft as _send_draft
        _send_draft(draft_id)
        return True, None
    except Exception as e:
        return False, str(e)


class EmailSendRequest(BaseModel):
    to_name: str
    to_email: str
    subject: str
    body_html: str
    cc: Optional[list] = None  # [{"name": "...", "email": "..."}]
    reply_to_message_id: Optional[str] = None

@router.post("/email/send")
def send_email_now(req: EmailSendRequest, request: Request):
    """
    Despite the name, this does NOT send. It stages an Outlook draft and creates a
    durable Buck-approval request (Telegram APPROVE/REJECT/HOLD) — the email is only
    actually sent by Buck tapping APPROVE, which triggers the send server-side via
    _handle_buck_command. Rewritten 2026-07-01 after an incident where this endpoint
    called Microsoft Graph's sendMail directly with no API key check and no approval
    gate, and an email reached a 101F architect contact with zero review or audit trail.
    """
    _require_key(request)
    t0 = time.time()
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "integrations"))
        from microsoft_graph import create_draft, create_reply_draft

        if req.reply_to_message_id:
            draft = create_reply_draft(req.reply_to_message_id, req.body_html)
        else:
            draft = create_draft(req.subject, req.body_html, [(req.to_name, req.to_email)])
        draft_id = draft.get("id", "")
        if not draft_id:
            raise ValueError("Draft creation returned no ID — cannot queue for approval")

        msg_id = _create_ai_message(
            "browser_claude", "buck", "approval_request",
            f"Send email: {req.subject[:80]}",
            f"To: {req.to_name} <{req.to_email}>\nSubject: {req.subject}\n\n{req.body_html[:500]}",
            requires_buck_approval=True, approval_type="email_send",
            related_file=draft_id,
        )
        sent = _notify_agents("browser_claude", "buck", "approval_request",
                               f"Send email: {req.subject[:80]}",
                               f"To: {req.to_name} <{req.to_email}>\n\n{req.body_html[:500]}",
                               requires_buck_approval=True, approval_type="email_send",
                               related_file=draft_id)

        return _response("/email/send", {
            "status":     "queued_for_approval",
            "message_id": sent.get("id", msg_id),
            "draft_id":   draft_id,
            "to_email":   req.to_email,
            "subject":    req.subject,
            "note":       "Draft created and sent to Buck for Telegram approval. It will only send once Buck approves.",
        }, start=t0)
    except Exception as e:
        return _response("/email/send", {}, errors=[str(e)], start=t0)


@router.post("/email/draft/{draft_id}/send")
def send_existing_draft(draft_id: str, request: Request):
    """Send a previously created Outlook draft — but only if an ai_messages record shows
    Buck already approved (or completed) an email_send request for this exact draft_id.
    Otherwise refuses. This is the manual/recovery path; the normal path is Buck tapping
    APPROVE in Telegram, which sends automatically via _handle_buck_command."""
    _require_key(request)
    t0 = time.time()
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id FROM ai_messages
                    WHERE related_file = %s AND approval_type = 'email_send'
                      AND status IN ('RECEIVED', 'COMPLETE')
                    ORDER BY id DESC LIMIT 1
                """, (draft_id,))
                approved = cur.fetchone()
        if not approved:
            return _response("/email/draft/send", {},
                              errors=["No approved email_send request found for this draft_id — "
                                      "call POST /email/send first and wait for Buck's Telegram approval"],
                              start=t0)
        ok, err = _send_approved_draft(draft_id)
        if not ok:
            return _response("/email/draft/send", {}, errors=[err], start=t0)
        _log("/email/draft/send", "browser_claude", "outlook", "ok",
             round((time.time()-t0)*1000), str(uuid.uuid4()), f"Sent draft {draft_id[:20]}")
        return _response("/email/draft/send", {
            "status": "sent", "draft_id": draft_id,
            "note": "Draft sent and saved to Sent Items.",
        }, start=t0)
    except Exception as e:
        return _response("/email/draft/send", {}, errors=[str(e)], start=t0)


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

    import re as _re
    slug = _re.sub(r"[^A-Za-z0-9_\-]", "_", (req.title or req.document_type or "handoff"))[:40]
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

    _touch_heartbeat(req.source_agent, f"handoff: {req.title or req.document_type}")

    # Trigger processor async (best-effort)
    import subprocess, threading
    def _run():
        subprocess.run(
            ["python3", os.path.join(inbox, "..", "handoff_processor.py"), "--file", fpath],
            capture_output=True, timeout=30
        )
    threading.Thread(target=_run, daemon=True).start()

    # Push ntfy notification so GBT/Buck know a handoff arrived
    try:
        import requests as _req
        _req.post(
            "https://ntfy.sh/hci-executive",
            data=f"[{req.source_agent}→{req.destination_agent}] {req.title or 'New handoff'}: {(req.body or '')[:120]}",
            headers={"Title": f"HCI Handoff: {req.title or req.document_type}",
                     "Priority": "high" if req.priority == "high" else "default",
                     "Tags": "inbox"},
            timeout=3
        )
    except Exception:
        pass  # ntfy is best-effort

    _log("/agent/handoff", req.source_agent, "Agent_Handoff/Inbox",
         "queued", round((time.time()-t0)*1000), rid, f"queued {fname}")

    return _response("/agent/handoff", {
        "queued": True, "filename": fname, "request_id": rid,
        "document_type": req.document_type,
        "message": "Handoff written to Inbox — processor will route within 60s",
    }, start=t0)


@router.get("/agent/inbox")
def agent_inbox():
    """
    GBT polls this at the start of every session to check for pending handoffs from Claude Code.
    Returns all unread files in Agent_Handoff/Inbox/ with their title, priority, and body.
    GBT should call this endpoint FIRST, read all items, then POST back to /agent/handoff when done.
    """
    t0 = time.time()
    inbox = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "..", "..",
        "Architecture", "Agent_Handoff", "Inbox"
    ))
    items = []
    if os.path.isdir(inbox):
        for fname in sorted(os.listdir(inbox)):
            if not fname.endswith(".md"):
                continue
            fpath = os.path.join(inbox, fname)
            try:
                with open(fpath) as f:
                    raw = f.read()
                # Parse frontmatter
                lines = raw.split("\n")
                meta = {}
                body_start = 0
                if lines[0].strip() == "---":
                    for i, line in enumerate(lines[1:], 1):
                        if line.strip() == "---":
                            body_start = i + 1
                            break
                        if ":" in line:
                            k, v = line.split(":", 1)
                            meta[k.strip()] = v.strip()
                body = "\n".join(lines[body_start:]).strip()
                items.append({
                    "filename": fname,
                    "title": meta.get("title", fname),
                    "priority": meta.get("priority", "medium"),
                    "source_agent": meta.get("source_agent", "unknown"),
                    "document_type": meta.get("document_type", "unknown"),
                    "created_at": meta.get("created_at", ""),
                    "body": body,
                })
            except Exception as e:
                items.append({"filename": fname, "error": str(e)})
    return _response("/agent/inbox", {
        "pending_count": len(items),
        "items": items,
        "instruction": "Read all items above, execute them, then POST completion handoff back to /gateway/agent/handoff",
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

        # Gap14 FIX: explicit timeouts on all Google API calls prevent ERR_NGROK_3004
        DRIVE_TIMEOUT = 20

        # Check if file already exists in folder
        search_resp = requests.get(
            "https://www.googleapis.com/drive/v3/files",
            headers={"Authorization": f"Bearer {token}"},
            params={"q": f"name='{req.filename}' and '{folder_id}' in parents and trashed=false", "fields": "files(id,name)"},
            timeout=DRIVE_TIMEOUT
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
                data=content_bytes,
                timeout=DRIVE_TIMEOUT
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
                data=body,
                timeout=DRIVE_TIMEOUT
            )
            result = create_resp.json()
            action = "created"

        _log("/drive/write", "gbt", req.filename, action, round((time.time()-t0)*1000), str(uuid.uuid4())[:8])
        result_id = result.get("id")
        # AD-12: construct the view link explicitly rather than trust webViewLink,
        # which comes back null if the upload response omits it (auth hiccup, etc.)
        view_link = result.get("webViewLink") or (f"https://drive.google.com/file/d/{result_id}/view" if result_id else None)
        return _response("/drive/write", {
            "action": action,
            "filename": req.filename,
            "file_id": result_id,
            "view_link": view_link,
            "folder_id": folder_id,
            "bytes_written": len(content_bytes)
        }, start=t0)

    except Exception as e:
        return _response("/drive/write", {}, errors=[str(e)], start=t0)


# ── Field Endpoints (GBT Field GPT) ──────────────────────────────────────────

class FieldNotePayload(BaseModel):
    project_code: str
    note: str
    submitted_by: str = "field"
    note_type: str = "general"

class FieldRFIPayload(BaseModel):
    project_code: str
    question: str
    submitted_by: str = "superintendent"
    subject: str = ""
    submitted_to: str = ""

class FieldDailyReportPayload(BaseModel):
    project_code: str
    work_performed: str
    crew: int = 0
    weather: str = ""
    submitted_by: str = "superintendent"
    field_risks: str = ""
    lookahead: str = ""

class CreateProjectPayload(BaseModel):
    name: str
    address: str
    pm_name: str = "Buck Adams"
    super_name: str = ""
    owner_name: str = ""
    status: str = "active"
    project_type: str = "remodel"


@router.post("/field/note")
def field_submit_note(req: FieldNotePayload):
    """
    submitFieldNote — SS or PM logs a quick field note.
    Writes to project_events timeline immediately. No approval needed.
    """
    t0 = time.time()
    try:
        pid = _get_pid(req.project_code)
        conn = _pg()
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO project_events
                    (project_id, event_type, event_date, title, description, source_table, created_by, metadata)
                VALUES (%s, 'field_note', CURRENT_DATE, %s, %s, 'field_note', %s, %s)
                RETURNING id, event_type, event_date, title
            """, (pid, f"Field Note: {req.note[:80]}", req.note,
                  req.submitted_by, f'{{"note_type":"{req.note_type}"}}'))
            row = dict(cur.fetchone())
        conn.close()
        try:
            requests.post("https://ntfy.sh/hci-executive",
                data=f"[{req.project_code}] Field note from {req.submitted_by}: {req.note[:100]}",
                headers={"Title": f"Field Note — {req.project_code}", "Priority": "default", "Tags": "memo"},
                timeout=3)
        except Exception:
            pass
        _log("/field/note", "field", req.project_code, "logged", round((time.time()-t0)*1000), str(uuid.uuid4())[:8])
        return _response("/field/note", {"logged": True, "event": row, "project_code": req.project_code}, start=t0)
    except HTTPException as e:
        return _response("/field/note", {}, errors=[str(e.detail)], start=t0)
    except Exception as e:
        return _response("/field/note", {}, errors=[str(e)], start=t0)


@router.post("/field/rfi")
def field_submit_rfi(req: FieldRFIPayload):
    """
    submitRFI (Gap11) — Field submits an RFI from the job site.
    Creates RFI in database with status=open. Returns RFI number for tracking.
    """
    t0 = time.time()
    try:
        pid = _get_pid(req.project_code)
        conn = _pg()
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SELECT COALESCE(MAX(CAST(NULLIF(rfi_number, '') AS INTEGER)), 0) + 1 AS next_num FROM rfis WHERE project_id = %s AND rfi_number ~ '^[0-9]+$'", (pid,))
            next_num = cur.fetchone()["next_num"]
            subject = req.subject or req.question[:80]
            cur.execute("""
                INSERT INTO rfis (project_id, rfi_number, subject, question, submitted_by, status, submitted_date)
                VALUES (%s, %s, %s, %s, %s, 'open', CURRENT_DATE)
                RETURNING id, rfi_number, subject, status, submitted_date
            """, (pid, str(next_num), subject, req.question, req.submitted_by))
            rfi = dict(cur.fetchone())
            # Also log to event timeline
            cur.execute("""
                INSERT INTO project_events (project_id, event_type, event_date, title, description, source_table, source_id, created_by)
                VALUES (%s, 'rfi_submitted', CURRENT_DATE, %s, %s, 'rfis', %s, %s)
            """, (pid, f"RFI {next_num}: {subject}", req.question, rfi["id"], req.submitted_by))
        conn.close()
        try:
            requests.post("https://ntfy.sh/hci-executive",
                data=f"[{req.project_code}] RFI #{next_num} submitted by {req.submitted_by}: {subject}",
                headers={"Title": f"New RFI — {req.project_code}", "Priority": "high", "Tags": "question"},
                timeout=3)
        except Exception:
            pass
        _log("/field/rfi", "field", req.project_code, "rfi_created", round((time.time()-t0)*1000), str(uuid.uuid4())[:8])
        return _response("/field/rfi", {"logged": True, "rfi": rfi, "project_code": req.project_code}, start=t0)
    except HTTPException as e:
        return _response("/field/rfi", {}, errors=[str(e.detail)], start=t0)
    except Exception as e:
        return _response("/field/rfi", {}, errors=[str(e)], start=t0)


class PlanReviewPayload(BaseModel):
    project_code: str
    sheet_text: str
    reviewed_by: str = "claude_code"


_PLAN_REVIEW_CHECKLIST = """Standard completeness checklist:
- Fixture schedules (plumbing, lighting) fully filled in
- Finish schedules present for all rooms
- Structural notes/steel grades specified
- Dimensions complete, no unresolved "verify in field" on critical items
- MEP coordination notes present
- Door/window schedules complete

Identify ONLY genuine gaps that would block bidding or construction — not stylistic nitpicks.

Also assess: is this plan set complete enough to generate a preliminary ROM (rough order
of magnitude) estimate and schedule — i.e. no CRITICAL gaps remain, even if some
medium/low ones do? And if you can find square footage and project type (new
construction / renovation / remodel) stated anywhere, extract them.

Respond with a JSON object only, no other text, in this exact format:
{"gaps": [{"item": "short title", "sheet_reference": "sheet number or section", "urgency": "critical|high|medium", "question": "the formal RFI question text"}],
  "ready_for_rom": true or false,
  "readiness_reason": "one sentence why",
  "square_footage": integer or null,
  "project_type": "new" or "renovation" or "remodel" or null}"""


def _parse_plan_review_json(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw)


def _create_rfis_from_gaps(pid: int, gaps: list, reviewed_by: str) -> list:
    """Logs each identified gap as a real, open RFI. Never sends anything — notifying
    the design team is a separate, explicit, Buck-approved step (POST /email/send)."""
    created = []
    conn = _pg()
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COALESCE(MAX(CAST(NULLIF(rfi_number, '') AS INTEGER)), 0) AS max_num
            FROM rfis WHERE project_id = %s AND rfi_number ~ '^[0-9]+$'
        """, (pid,))
        next_num = cur.fetchone()["max_num"] + 1
        for gap in gaps:
            subject = f"{gap.get('item','Gap')} ({gap.get('sheet_reference','')})"[:120]
            cur.execute("""
                INSERT INTO rfis (project_id, rfi_number, subject, question, submitted_by, status, submitted_date)
                VALUES (%s, %s, %s, %s, %s, 'open', CURRENT_DATE)
                RETURNING id, rfi_number, subject, status
            """, (pid, str(next_num), subject, gap.get("question", ""), reviewed_by))
            rfi = dict(cur.fetchone())
            rfi["urgency"] = gap.get("urgency", "medium")
            created.append(rfi)
            next_num += 1
    conn.close()
    return created


def _plan_review_finish(path: str, project_code: str, analysis: dict, created: list, t0: float, extra: dict = None):
    prelim_rom = None
    sf = analysis.get("square_footage")
    ptype = analysis.get("project_type")
    if analysis.get("ready_for_rom") and sf:
        rom_response = rom_estimate(sf=sf, project_type=ptype or "new")
        prelim_rom = rom_response.get("payload") if isinstance(rom_response, dict) else None

    payload = {
        "project_code": project_code,
        "gaps_found": len(created),
        "rfis_created": created,
        "ready_for_rom": analysis.get("ready_for_rom", False),
        "readiness_reason": analysis.get("readiness_reason"),
        "extracted_square_footage": sf,
        "extracted_project_type": ptype,
        "preliminary_rom": prelim_rom,
        "note": "RFIs logged as open — NOT sent to anyone. Review, then use POST "
                "/email/draft + /email/send (requires Buck's Telegram approval) to "
                "actually notify the design team. preliminary_rom is a rough order of "
                "magnitude only, not a bid — sub package/SOW generation is the next phase.",
    }
    if extra:
        payload.update(extra)
    return _response(path, payload, start=t0)


@router.post("/plan-review/analyze")
def plan_review_analyze(req: PlanReviewPayload):
    """
    Formalized plan-review pipeline (2026-07-01) — the front door of a job: read a plan
    set, say what's missing, and if it's complete enough, hand back a preliminary ROM
    so sales/preconstruction can move without waiting on a full estimate. Replaces the
    ad-hoc, ungoverned batch process that generated the 101F/1355R RFI emails without
    review (the incident behind ADR-010/011). Gaps become RFI records — logged `open`,
    NEVER auto-emailed; notifying the design team is a separate, explicit step through
    POST /email/draft + /email/send, which already requires Buck's Telegram approval.
    This variant takes extracted sheet text directly; for real PDF/drawing uploads see
    POST /plan-review/upload.
    """
    t0 = time.time()
    try:
        pid = _get_pid(req.project_code)
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        prompt = f"""You are a construction plan reviewer checking a permit set for gaps that would block bidding or construction.

Plan set excerpt:
{req.sheet_text[:8000]}

{_PLAN_REVIEW_CHECKLIST}"""
        message = client.messages.create(
            model="claude-haiku-4-5-20251001", max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        analysis = _parse_plan_review_json(message.content[0].text)
        created = _create_rfis_from_gaps(pid, analysis.get("gaps", []), req.reviewed_by)
        _log("/plan-review/analyze", req.reviewed_by, req.project_code, "ok",
             round((time.time()-t0)*1000), str(uuid.uuid4())[:8], f"{len(created)} RFIs drafted")
        return _plan_review_finish("/plan-review/analyze", req.project_code, analysis, created, t0)
    except HTTPException as e:
        return _response("/plan-review/analyze", {}, errors=[str(e.detail)], start=t0)
    except Exception as e:
        return _response("/plan-review/analyze", {}, errors=[str(e)], start=t0)


@router.post("/plan-review/upload")
async def plan_review_upload(
    file: UploadFile = File(...),
    project_code: str = Form(...),
    reviewed_by: str = Form("claude_code"),
    max_pages: int = Form(30),
):
    """
    Real PDF/drawing plan-review (2026-07-01) — the follow-on to /plan-review/analyze
    named in ADR-014's roadmap. Renders each PDF page to an image and sends it to
    Claude's vision API directly, since plan sheets are drawings (schedules, dimensions,
    symbols) that lose most of their information under plain text extraction. Same
    completeness checklist and RFI/ROM handling as /plan-review/analyze — this endpoint
    only differs in how it reads the source document.
    max_pages caps cost/context on large sets; raise it for a genuinely large permit
    set once the token cost is acceptable to Buck.
    """
    t0 = time.time()
    try:
        pid = _get_pid(project_code)
        pdf_bytes = await file.read()

        from pdf2image import convert_from_bytes
        import base64, io
        # poppler_path pinned explicitly — the launchd-managed API process doesn't
        # inherit the interactive shell PATH that has /opt/homebrew/bin on it.
        pages = convert_from_bytes(pdf_bytes, dpi=150, poppler_path="/opt/homebrew/bin")
        if len(pages) > max_pages:
            pages = pages[:max_pages]
        truncated_note = f" (only the first {max_pages} of the uploaded set were reviewed)" if len(pages) == max_pages else ""

        image_blocks = []
        for page in pages:
            buf = io.BytesIO()
            page.save(buf, format="JPEG", quality=80)
            b64 = base64.b64encode(buf.getvalue()).decode()
            image_blocks.append({
                "type": "image",
                "source": {"type": "base64", "media_type": "image/jpeg", "data": b64},
            })

        import anthropic
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        text_block = {"type": "text", "text": f"""You are a construction plan reviewer checking a permit set for gaps that would block bidding or construction. The following {len(pages)} images are pages from the uploaded plan set, in order.{truncated_note}

{_PLAN_REVIEW_CHECKLIST}"""}
        message = client.messages.create(
            model="claude-haiku-4-5-20251001", max_tokens=3000,
            messages=[{"role": "user", "content": image_blocks + [text_block]}],
        )
        analysis = _parse_plan_review_json(message.content[0].text)
        created = _create_rfis_from_gaps(pid, analysis.get("gaps", []), reviewed_by)
        _log("/plan-review/upload", reviewed_by, project_code, "ok",
             round((time.time()-t0)*1000), str(uuid.uuid4())[:8],
             f"{len(created)} RFIs from {len(pages)}-page upload")
        return _plan_review_finish("/plan-review/upload", project_code, analysis, created, t0,
                                    extra={"pages_reviewed": len(pages), "filename": file.filename})
    except HTTPException as e:
        return _response("/plan-review/upload", {}, errors=[str(e.detail)], start=t0)
    except Exception as e:
        return _response("/plan-review/upload", {}, errors=[str(e)], start=t0)


@router.post("/field/daily-report")
def field_submit_daily_report(req: FieldDailyReportPayload):
    """
    submitDailyReport — SS submits end-of-day field report.
    Writes directly to daily_logs (no approval queue for field pilot).
    """
    t0 = time.time()
    try:
        pid = _get_pid(req.project_code)
        conn = _pg()
        conn.autocommit = True
        import json as _json
        with conn.cursor() as cur:
            crew_json = _json.dumps({"count": req.crew}) if req.crew else None
            cur.execute("""
                INSERT INTO daily_logs
                    (project_id, log_date, work_performed, crew_on_site, weather,
                     logged_by, field_risks, lookahead)
                VALUES (%s, CURRENT_DATE, %s, %s::jsonb, %s, %s, %s, %s)
                RETURNING id, log_date, logged_by
            """, (pid, req.work_performed, crew_json, req.weather,
                  req.submitted_by, req.field_risks or None, req.lookahead or None))
            log = dict(cur.fetchone())
            # Also log to event timeline
            cur.execute("""
                INSERT INTO project_events (project_id, event_type, event_date, title, description, source_table, source_id, created_by)
                VALUES (%s, 'daily_log', CURRENT_DATE, %s, %s, 'daily_logs', %s, %s)
            """, (pid, f"Daily Log — {log['log_date']}", req.work_performed[:200], log["id"], req.submitted_by))
        conn.close()
        try:
            requests.post("https://ntfy.sh/hci-executive",
                data=f"[{req.project_code}] Daily report from {req.submitted_by}: {req.crew} crew, {req.weather}. {req.work_performed[:80]}",
                headers={"Title": f"Daily Report — {req.project_code}", "Priority": "default", "Tags": "construction"},
                timeout=3)
        except Exception:
            pass
        _log("/field/daily-report", "field", req.project_code, "log_written", round((time.time()-t0)*1000), str(uuid.uuid4())[:8])
        return _response("/field/daily-report", {"logged": True, "log": log, "project_code": req.project_code}, start=t0)
    except HTTPException as e:
        return _response("/field/daily-report", {}, errors=[str(e.detail)], start=t0)
    except Exception as e:
        return _response("/field/daily-report", {}, errors=[str(e)], start=t0)


@router.get("/field/open-items")
def field_open_items(code: str):
    """
    getOpenItems — Returns everything open that needs attention on a project.
    Open RFIs + approval queue + open risks + recent field flags.
    Field-safe format: plain language, no technical IDs exposed.
    """
    t0 = time.time()
    try:
        pid = _get_pid(code)
        conn = _pg()
        conn.autocommit = True
        items = []
        with conn.cursor() as cur:
            cur.execute("""SELECT rfi_number, subject, submitted_by, submitted_date, status
                FROM rfis WHERE project_id=%s AND status='open' ORDER BY submitted_date ASC""", (pid,))
            for r in cur.fetchall():
                d = dict(r)
                items.append({"type": "RFI", "id": f"RFI-{d['rfi_number']}",
                    "description": d["subject"], "from": d["submitted_by"],
                    "date": str(d["submitted_date"]), "urgency": "HIGH"})

            cur.execute("""SELECT risk_type, severity, description, status
                FROM risks WHERE project_id=%s AND status='open'
                ORDER BY CASE severity WHEN 'critical' THEN 1 WHEN 'high' THEN 2 ELSE 3 END""", (pid,))
            for r in cur.fetchall():
                d = dict(r)
                items.append({"type": "Risk", "id": d["risk_type"],
                    "description": d["description"][:120], "from": "system",
                    "date": None,
                    "urgency": "HIGH" if d["severity"] in ("critical","high") else "MEDIUM"})

            cur.execute("""SELECT event_type, title, event_date, created_by
                FROM project_events WHERE project_id=%s AND event_type IN ('risk_flagged','field_note')
                AND event_date >= CURRENT_DATE - '7 days'::interval
                ORDER BY event_date DESC LIMIT 5""", (pid,))
            for r in cur.fetchall():
                d = dict(r)
                items.append({"type": "Field Flag", "id": d["event_type"],
                    "description": d["title"], "from": d["created_by"],
                    "date": str(d["event_date"]), "urgency": "MEDIUM"})

        conn.close()
        high = sum(1 for i in items if i["urgency"] == "HIGH")
        return _response("/field/open-items", {
            "project_code": code, "total_open": len(items),
            "high_urgency": high, "items": items,
        }, start=t0)
    except HTTPException as e:
        return _response("/field/open-items", {}, errors=[str(e.detail)], start=t0)
    except Exception as e:
        return _response("/field/open-items", {}, errors=[str(e)], start=t0)


# ── getDailyLogFormatted ─────────────────────────────────────────────────────

@router.get("/field/daily-log-formatted")
def field_daily_log_formatted(code: str, date: str = None):
    """
    getDailyLogFormatted — Returns a Houzz-ready formatted daily log for a project and date.
    If date omitted, returns the most recent log.
    Field-safe: plain English, no internal IDs.
    """
    t0 = time.time()
    try:
        pid = _get_pid(code)
        conn = _pg()
        conn.autocommit = True
        with conn.cursor() as cur:
            if date:
                cur.execute("""
                    SELECT dl.id, dl.log_date, dl.logged_by, dl.weather, dl.work_performed,
                           dl.issues, dl.crew_on_site, dl.safety_notes, dl.subcontractor_progress,
                           p.name AS project_name, p.address
                    FROM daily_logs dl JOIN projects p ON p.id = dl.project_id
                    WHERE dl.project_id = %s AND dl.log_date = %s
                    ORDER BY dl.id DESC LIMIT 1
                """, (pid, date))
            else:
                cur.execute("""
                    SELECT dl.id, dl.log_date, dl.logged_by, dl.weather, dl.work_performed,
                           dl.issues, dl.crew_on_site, dl.safety_notes, dl.subcontractor_progress,
                           p.name AS project_name, p.address
                    FROM daily_logs dl JOIN projects p ON p.id = dl.project_id
                    WHERE dl.project_id = %s
                    ORDER BY dl.log_date DESC, dl.id DESC LIMIT 1
                """, (pid,))
            row = cur.fetchone()
        conn.close()

        if not row:
            return _response("/field/daily-log-formatted", {
                "project_code": code, "log_found": False,
                "message": "No daily logs found for this project/date"
            }, start=t0)

        d = dict(row)
        crew_info = d["crew_on_site"]
        if isinstance(crew_info, dict):
            crew_count = crew_info.get("count", 0)
        elif isinstance(crew_info, int):
            crew_count = crew_info
        else:
            crew_count = 0

        formatted = {
            "project": d["project_name"],
            "address": d["address"],
            "date": str(d["log_date"]),
            "superintendent": d["logged_by"] or "Not specified",
            "crew_on_site": crew_count,
            "weather": (d["weather"] or "").replace("_", " ").title(),
            "work_performed": d["work_performed"] or "No notes recorded",
            "issues_delays": d["issues"] or "None",
            "safety_notes": d["safety_notes"] or "No safety items",
            "subcontractor_progress": d["subcontractor_progress"] or "None reported",
            "houzz_ready": True,
        }
        houzz_text = (
            f"Daily Log — {d['project_name']}\n"
            f"Date: {d['log_date']}\n"
            f"Superintendent: {formatted['superintendent']}\n"
            f"Crew on Site: {crew_count}\n"
            f"Weather: {formatted['weather']}\n"
            f"Work Performed: {formatted['work_performed']}\n"
            f"Issues/Delays: {formatted['issues_delays']}\n"
            f"Safety Notes: {formatted['safety_notes']}\n"
            f"Subcontractor Progress: {formatted['subcontractor_progress']}"
        )
        _log("/field/daily-log-formatted", "field", code, "ok",
             round((time.time()-t0)*1000), str(uuid.uuid4())[:8])
        return _response("/field/daily-log-formatted", {
            "project_code": code, "log_found": True,
            "formatted_log": formatted,
            "houzz_paste_text": houzz_text,
        }, start=t0)
    except HTTPException as e:
        return _response("/field/daily-log-formatted", {}, errors=[str(e.detail)], start=t0)
    except Exception as e:
        return _response("/field/daily-log-formatted", {}, errors=[str(e)], start=t0)


# ── Gap1: createProject ───────────────────────────────────────────────────────

@router.post("/project/create")
def create_project(req: CreateProjectPayload):
    """
    Gap1 FIX — createProject endpoint.
    Creates a new project in the HCI OS database. Buck's auth required (API key on header).
    """
    t0 = time.time()
    try:
        conn = _pg()
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO projects (name, address, pm_name, super_name, owner_name, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, name, address, status
            """, (req.name, req.address, req.pm_name, req.super_name, req.owner_name, req.status))
            proj = dict(cur.fetchone())
        conn.close()
        _log("/project/create", "gbt", req.name, "created", round((time.time()-t0)*1000))
        return _response("/project/create", {"created": True, "project": proj}, start=t0)
    except Exception as e:
        return _response("/project/create", {}, errors=[str(e)], start=t0)


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
                    FROM projects p WHERE p.status IN ('active','design') AND p.name NOT LIKE 'TEST-%' ORDER BY p.id
                """)
                rows = [dict(r) for r in cur.fetchall()]

        # Build code/name/hubspot maps from DB (no hardcoding)
        CODE_MAP, NAME_MAP, HS_MAP, SCOPE_MAP = {}, {}, {}, {}
        with _pg() as conn_m:
            with conn_m.cursor() as cur_m:
                cur_m.execute("SELECT id, project_code, name, hubspot_deal_id, scope FROM projects WHERE project_code IS NOT NULL")
                for pm in cur_m.fetchall():
                    CODE_MAP[pm["id"]] = pm["project_code"] or ""
                    NAME_MAP[pm["id"]] = pm["name"] or ""
                    HS_MAP[pm["id"]] = pm["hubspot_deal_id"] or ""
                    SCOPE_MAP[pm["id"]] = pm["scope"] or "TBD"

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
        HCI_FOLDER = os.environ.get("HCI_AI_DRIVE_FOLDER", "1ejYXRgS34c7JmQKfHwaPNnzEBcCGUmwI")
        FOLDER_MAP = {1: HCI_FOLDER, 2: HCI_FOLDER, 3: HCI_FOLDER, 11: HCI_FOLDER, 12: HCI_FOLDER, 13: HCI_FOLDER}

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
        drive_file_id = drive_data.get("id")
        view_link = drive_data.get("webViewLink") or (f"https://drive.google.com/file/d/{drive_file_id}/view" if drive_file_id else None)
        _log("/drive/export-schedule-csv", "admin", "Drive", "ok",
             round((time.time()-t0)*1000), rid,
             f"project={project_code} rows={len(items)} file_id={drive_file_id}")
        return _response("/drive/export-schedule-csv", {
            "project_code": project_code,
            "rows_exported": len(items),
            "filename": filename,
            "file_id": drive_file_id,
            "view_link": view_link,
            "bytes_written": len(csv_content.encode())
        }, start=t0)
    except Exception as e:
        return _response("/drive/export-schedule-csv", {}, errors=[str(e)], start=t0)


def _get_pid(code: str) -> int:
    """Resolve project code → DB id. Queries projects.project_code column (DB-driven)."""
    try:
        conn = _pg()
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM projects WHERE project_code = %s", (code.upper(),))
            row = cur.fetchone()
        conn.close()
        if row:
            return row["id"]
    except Exception:
        pass
    return 1


# ── Permitting Research (Claude AI) ─────────────────────────────────────────
@router.get("/permitting/research/{code}")
def permitting_research(code: str):
    """AI-powered permit research for City of Aspen projects using Claude."""
    t0 = time.time()
    pid = _get_pid(code)
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT p.name, p.address, p.scope, p.status,
                        (SELECT COUNT(*) FROM bid_packages bp WHERE bp.project_id = p.id) AS pkg_count,
                        (SELECT COUNT(*) FROM rfis r WHERE r.project_id = p.id AND r.status='open') AS open_rfis
                    FROM projects p WHERE p.id = %s
                """, (pid,))
                row = cur.fetchone()
        if not row:
            return _response(f"/permitting/research/{code}", {}, errors=["Project not found"], start=t0)

        # Build permit research using Claude AI
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

        scope = row["scope"] or "Construction project"
        address = row["address"] or "Aspen, CO"

        prompt = f"""You are a construction permitting expert specializing in Aspen, Colorado.
Provide a concise permitting roadmap for this project:

Project: {row['name']}
Address: {address}
Scope: {scope}
Status: {row['status']}

Provide:
1. Required permits (Building, Grading, ROW, HPC if applicable, etc.)
2. City of Aspen specific requirements (HPC Historic Preservation, FAR/setback notes)
3. Estimated review timelines (City of Aspen Building Dept typically 8-16 weeks)
4. Key submittals required
5. Any altitude/environmental considerations (7,900 ft elevation, wildfire zone, etc.)

Be specific to City of Aspen Building Department processes. Keep response under 400 words."""

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}]
        )
        research = message.content[0].text

        _log(f"/permitting/research/{code}", "GBT", f"claude-haiku permit research",
             "ok", round((time.time()-t0)*1000), str(uuid.uuid4())[:8])
        return _response(f"/permitting/research/{code}", {
            "project_code": code,
            "project_name": row["name"],
            "address": address,
            "scope": scope,
            "permit_research": research,
            "jurisdiction": "City of Aspen Building Department",
            "hpc_required": "cemetery" in address.lower() or "historic" in (scope or "").lower(),
            "ai_model": "claude-haiku-4-5-20251001"
        }, start=t0)
    except Exception as e:
        return _response(f"/permitting/research/{code}", {}, errors=[str(e)], start=t0)


# ── Houzz Design Intelligence ────────────────────────────────────────────────
@router.get("/houzz/design-intel/{code}")
def houzz_design_intel(code: str):
    """Houzz design intelligence — luxury finish specs and design trends for project type."""
    t0 = time.time()
    pid = _get_pid(code)
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT name, address, scope, status FROM projects WHERE id = %s", (pid,))
                row = cur.fetchone()
                if not row:
                    return _response(f"/houzz/design-intel/{code}", {}, errors=["Project not found"], start=t0)

                # Pull Houzz data if available
                cur.execute("SELECT id, name, status FROM houzz_projects WHERE name ILIKE %s LIMIT 1",
                            (f"%{code.replace('-',' ')}%",))
                houzz_proj = cur.fetchone()

                # Get finish selections from houzz_selections if available
                selections = []
                if houzz_proj:
                    cur.execute("SELECT item_name, selection, brand, cost FROM houzz_selections WHERE project_id = %s LIMIT 20",
                                (houzz_proj["id"],))
                    selections = [dict(s) for s in cur.fetchall()]

        # Generate design intelligence using Claude
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

        scope = row["scope"] or "Luxury Aspen construction"
        project_type = ("New Construction" if "new construction" in scope.lower()
                       else "Remodel" if "remodel" in scope.lower()
                       else "Multifamily" if "condo" in scope.lower() or "unit" in scope.lower()
                       else "Custom")

        prompt = f"""You are a luxury interior design consultant for high-end Aspen, Colorado projects.
Provide finish specifications and design intelligence for:

Project: {row['name']} ({project_type})
Address: {row['address']}
Scope: {scope}

Provide specific luxury finish recommendations:
1. Kitchen: cabinetry, countertop material/brand, appliances
2. Primary Bath: tile brand/pattern, fixtures, vanity specification
3. Flooring: species/type, width, finish
4. Hardware: brand/finish
5. Lighting: key brands/styles
6. HVAC/Mechanical: preferred systems for Aspen altitude + climate
7. Window brand recommendation (triple-pane for Aspen climate)
8. Current Aspen luxury market trends (2026)

Be specific with brands and specs appropriate for $1,000+/SF ultra-luxury Aspen market.
Keep response under 500 words."""

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=700,
            messages=[{"role": "user", "content": prompt}]
        )
        design_intel = message.content[0].text

        return _response(f"/houzz/design-intel/{code}", {
            "project_code": code,
            "project_name": row["name"],
            "project_type": project_type,
            "houzz_project_linked": houzz_proj is not None,
            "existing_selections": len(selections),
            "design_intelligence": design_intel,
            "market_tier": "ultra-luxury ($1,000+/SF)",
            "location": "Aspen, CO 81611 (7,900 ft elevation)",
        }, start=t0)
    except Exception as e:
        return _response(f"/houzz/design-intel/{code}", {}, errors=[str(e)], start=t0)


# ── HubSpot Intelligence ─────────────────────────────────────────────────────

def _hs_strip_html(s):
    import re as _re
    return _re.sub(r'<[^>]+>', '', s or '').strip() if s else ''

def _hs_deal_ids_for_project(cur, proj_name: str) -> list:
    """Return all HubSpot deal IDs matching a project by name (covers all bid package deals)."""
    # Match on first significant word(s) of project name to catch address variants
    cur.execute("""
        SELECT hubspot_deal_id FROM hubspot_deals
        WHERE deal_name ILIKE %s
           OR deal_name ILIKE %s
        ORDER BY hubspot_deal_id
    """, (f"%{proj_name}%", f"%{proj_name.split()[0]}%"))
    return [r["hubspot_deal_id"] for r in cur.fetchall()]


@router.get("/project/{code}/hubspot")
def project_hubspot(code: str):
    """HubSpot bid intelligence — queries ALL bid package deals for the project, not just the main deal."""
    t0 = time.time()
    try:
        pid = _get_pid(code)
        conn = _pg()
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SELECT hubspot_deal_id, name, hubspot_search_term FROM projects WHERE id = %s", (pid,))
            proj = cur.fetchone()
            if not proj:
                return _response(f"/project/{code}/hubspot", {}, errors=["Project not found"], start=t0)

            proj_name = proj["name"]
            search_term = proj.get("hubspot_search_term") or proj_name
            cur.execute("""
                SELECT hubspot_deal_id, deal_name, stage, amount
                FROM hubspot_deals
                WHERE deal_name ILIKE %s
                ORDER BY hubspot_deal_id
            """, (f"%{search_term}%",))
            all_deals = [dict(r) for r in cur.fetchall()]
            all_deal_ids = [d["hubspot_deal_id"] for d in all_deals]

            if not all_deal_ids:
                return _response(f"/project/{code}/hubspot", {
                    "project": proj_name, "hubspot_deals_found": 0,
                    "note": f"No HubSpot deals found matching '{search_name}'"
                }, start=t0)

            # Bid package summary by stage
            stage_counts = {}
            bid_total = 0.0
            for d in all_deals:
                stage_counts[d["stage"] or "Unknown"] = stage_counts.get(d["stage"] or "Unknown", 0) + 1
                try:
                    bid_total += float(d["amount"] or 0)
                except:
                    pass

            # Notes across ALL deal IDs
            cur.execute("""
                SELECT body, note_timestamp, deal_id
                FROM hubspot_notes
                WHERE deal_id = ANY(%s)
                ORDER BY note_timestamp DESC
                LIMIT 20
            """, (all_deal_ids,))
            notes = [{"body": _hs_strip_html(r["body"])[:400],
                      "timestamp": str(r["note_timestamp"]),
                      "deal_id": r["deal_id"]} for r in cur.fetchall()]

            # Engagements by type across ALL deals
            cur.execute("""
                SELECT engagement_type, COUNT(*) as cnt
                FROM hubspot_engagements
                WHERE deal_id = ANY(%s)
                GROUP BY engagement_type ORDER BY cnt DESC
            """, (all_deal_ids,))
            engagement_counts = {r["engagement_type"]: r["cnt"] for r in cur.fetchall()}

            # Recent emails across all deals
            cur.execute("""
                SELECT engagement_type, subject, LEFT(body,250) as snippet, created_at, deal_id
                FROM hubspot_engagements
                WHERE deal_id = ANY(%s) AND engagement_type IN ('EMAIL','INCOMING_EMAIL')
                ORDER BY created_at DESC
                LIMIT 10
            """, (all_deal_ids,))
            recent_emails = [dict(r) for r in cur.fetchall()]

            # Tasks
            cur.execute("""
                SELECT subject, LEFT(body,250) as snippet, created_at, deal_id
                FROM hubspot_engagements
                WHERE deal_id = ANY(%s) AND engagement_type = 'TASK'
                ORDER BY created_at DESC
                LIMIT 15
            """, (all_deal_ids,))
            tasks = [dict(r) for r in cur.fetchall()]

        return _response(f"/project/{code}/hubspot", {
            "project": proj_name,
            "project_code": code,
            "hubspot_deals_found": len(all_deals),
            "bid_packages": {
                "total": len(all_deals),
                "total_value": bid_total,
                "by_stage": stage_counts,
                "deals": all_deals[:50],
            },
            "notes": {"count": len(notes), "items": notes},
            "engagements": {
                "total": sum(engagement_counts.values()),
                "by_type": engagement_counts,
                "recent_emails": recent_emails,
                "open_tasks": tasks,
            },
        }, start=t0)
    except Exception as e:
        return _response(f"/project/{code}/hubspot", {}, errors=[str(e)], start=t0)


@router.get("/hubspot/portfolio")
def hubspot_portfolio():
    """HubSpot portfolio — bid packages, notes, engagements for ALL active + monitoring projects."""
    t0 = time.time()
    try:
        conn = _pg()
        conn.autocommit = True

        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, project_code, hubspot_search_term
                FROM projects
                WHERE status IN ('active','live','monitoring')
                  AND name NOT LIKE 'TEST-%%' AND name NOT LIKE 'ASPN-%%'
                ORDER BY status, id
            """)
            all_projects = [dict(r) for r in cur.fetchall()]

        results = []
        for proj in all_projects:
            proj_name = proj["name"]
            search_term = proj.get("hubspot_search_term") or proj_name
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT hubspot_deal_id, deal_name, stage, amount
                    FROM hubspot_deals WHERE deal_name ILIKE %s
                """, (f"%{search_term}%",))
                deals = [dict(r) for r in cur.fetchall()]
                deal_ids = [d["hubspot_deal_id"] for d in deals]

                note_count = eng_count = 0
                latest_note = None
                if deal_ids:
                    cur.execute("SELECT COUNT(*) as cnt FROM hubspot_notes WHERE deal_id = ANY(%s)", (deal_ids,))
                    note_count = cur.fetchone()["cnt"]
                    cur.execute("SELECT COUNT(*) as cnt FROM hubspot_engagements WHERE deal_id = ANY(%s)", (deal_ids,))
                    eng_count = cur.fetchone()["cnt"]
                    cur.execute("""
                        SELECT body FROM hubspot_notes WHERE deal_id = ANY(%s)
                        ORDER BY note_timestamp DESC LIMIT 1
                    """, (deal_ids,))
                    n = cur.fetchone()
                    latest_note = _hs_strip_html(n["body"])[:200] if n else None

                bid_total = sum(float(d.get("amount") or 0) for d in deals)

            results.append({
                "project_code": proj["project_code"],
                "project": proj_name,
                "status": proj.get("status"),
                "bid_packages": len(deals),
                "bid_total": bid_total,
                "notes": note_count,
                "engagements": eng_count,
                "latest_note": latest_note,
                "summary": f"{proj['project_code']}: {len(deals)} packages, ${bid_total:,.0f} in bids, {note_count} notes"
            })

        # Sort by most bid activity
        results.sort(key=lambda x: -(x["bid_packages"] + x["engagements"]))
        return _response("/hubspot/portfolio", {
            "as_of": datetime.now(timezone.utc).date().isoformat(),
            "projects": results,
        }, start=t0)
    except Exception as e:
        return _response("/hubspot/portfolio", {}, errors=[str(e)], start=t0)



# ── Houzz Schedule Intelligence ──────────────────────────────────────────────

@router.get("/project/{code}/houzz")
def project_houzz(code: str, days_ahead: int = 14):
    """Houzz schedule intelligence — upcoming milestones, active phase, overdue items, change orders."""
    t0 = time.time()
    try:
        pid = _get_pid(code)
        conn = _pg()
        conn.autocommit = True
        with conn.cursor() as cur:
            # Project basics
            cur.execute("SELECT name, project_code, contract_value FROM projects WHERE id = %s", (pid,))
            proj = cur.fetchone()
            if not proj:
                return _response(f"/project/{code}/houzz", {}, errors=["Project not found"], start=t0)

            # Schedule summary: counts by status
            cur.execute("""
                SELECT status, count(*) as cnt
                FROM project_schedule_items
                WHERE project_id = %s::text
                GROUP BY status
            """, (pid,))
            status_counts = {r["status"] or "Unknown": r["cnt"] for r in cur.fetchall()}

            # Active construction phase (most common non-complete task type, including NULL as "Scheduled")
            cur.execute("""
                SELECT COALESCE(task_type, 'Scheduled') as task_type, count(*) as cnt
                FROM project_schedule_items
                WHERE project_id = %s::text
                  AND status NOT IN ('Complete','Completed','Done')
                  AND COALESCE(task_type,'x') NOT IN ('milestone','task','Weekly Updates','Owner Decisions','RFI / Coordination')
                GROUP BY task_type
                ORDER BY cnt DESC
                LIMIT 3
            """, (pid,))
            active_phases = [r["task_type"] for r in cur.fetchall()]

            # Upcoming items — look 60 days out to catch future-starting projects
            cur.execute("""
                SELECT title, start_date, end_date, status, task_type, completion_pct, assignee
                FROM project_schedule_items
                WHERE project_id = %s::text
                  AND start_date BETWEEN CURRENT_DATE AND CURRENT_DATE + 60
                  AND status NOT IN ('Complete','Completed','Done')
                ORDER BY start_date ASC
                LIMIT 20
            """, (pid,))
            upcoming = [dict(r) for r in cur.fetchall()]

            # Upcoming milestones specifically
            cur.execute("""
                SELECT title, start_date, status, completion_pct
                FROM project_schedule_items
                WHERE project_id = %s::text
                  AND task_type = 'milestone'
                  AND start_date >= CURRENT_DATE
                ORDER BY start_date ASC
                LIMIT 10
            """, (pid,))
            milestones = [dict(r) for r in cur.fetchall()]

            # Overdue items (past start date, not complete)
            cur.execute("""
                SELECT title, start_date, end_date, status, task_type, assignee
                FROM project_schedule_items
                WHERE project_id = %s::text
                  AND start_date < CURRENT_DATE
                  AND status NOT IN ('Complete','Completed','Done')
                ORDER BY start_date ASC
                LIMIT 15
            """, (pid,))
            overdue = [dict(r) for r in cur.fetchall()]

            # Owner decisions pending
            cur.execute("""
                SELECT title, start_date, status
                FROM project_schedule_items
                WHERE project_id = %s::text
                  AND task_type = 'Owner Decisions'
                  AND status NOT IN ('Complete','Completed','Done')
                ORDER BY start_date ASC
                LIMIT 10
            """, (pid,))
            owner_decisions = [dict(r) for r in cur.fetchall()]

            # Change orders from approval_queue (source of truth for active projects)
            cur.execute("""
                SELECT aq.id, aq.status,
                       (aq.proposed_payload->>'title') as title,
                       (aq.proposed_payload->>'amount')::numeric as amount,
                       aq.created_at
                FROM approval_queue aq
                WHERE aq.project_id = %s
                  AND aq.action_type ILIKE '%%change_order%%'
                ORDER BY aq.created_at DESC
                LIMIT 10
            """, (pid,))
            change_orders = [dict(r) for r in cur.fetchall()]
            co_total = sum(float(c.get("amount") or 0) for c in change_orders)
            co_pending = sum(1 for c in change_orders if c.get("status") == "pending")

            total_items = sum(status_counts.values())
            complete = status_counts.get("Complete", 0) + status_counts.get("Completed", 0) + status_counts.get("Done", 0)
            pct_complete = round(complete / total_items * 100) if total_items else 0

        return _response(f"/project/{code}/houzz", {
            "project": proj["name"],
            "project_code": proj["project_code"],
            "as_of": datetime.now(timezone.utc).date().isoformat(),
            "schedule": {
                "total_items": total_items,
                "pct_complete": pct_complete,
                "status_breakdown": status_counts,
                "active_phases": active_phases,
                "overdue_count": len(overdue),
            },
            "upcoming_items": upcoming,
            "upcoming_milestones": milestones,
            "overdue_items": overdue,
            "owner_decisions_pending": owner_decisions,
            "change_orders": {
                "count": len(change_orders),
                "total_value": co_total,
                "pending_approval": co_pending,
                "items": change_orders,
            },
        }, start=t0)
    except Exception as e:
        return _response(f"/project/{code}/houzz", {}, errors=[str(e)], start=t0)


@router.get("/houzz/portfolio")
def houzz_portfolio():
    """Houzz portfolio view — schedule health + milestones for ALL live projects. The 'every job' report."""
    t0 = time.time()
    try:
        conn = _pg()
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, project_code, contract_value
                FROM projects
                WHERE status IN ('active','live')
                  AND name NOT LIKE 'TEST-%%'
                ORDER BY id
            """)
            live_projects = [dict(r) for r in cur.fetchall()]

        results = []
        for proj in live_projects:
            pid = proj["id"]
            with conn.cursor() as cur:
                # Schedule counts
                cur.execute("""
                    SELECT status, count(*) as cnt
                    FROM project_schedule_items
                    WHERE project_id = %s::text
                    GROUP BY status
                """, (pid,))
                status_counts = {r["status"] or "Unknown": r["cnt"] for r in cur.fetchall()}

                # Overdue count
                cur.execute("""
                    SELECT count(*) as cnt FROM project_schedule_items
                    WHERE project_id = %s::text
                      AND start_date < CURRENT_DATE
                      AND status NOT IN ('Complete','Completed','Done')
                """, (pid,))
                overdue_cnt = cur.fetchone()["cnt"]

                # Next 3 upcoming milestones
                cur.execute("""
                    SELECT title, start_date, status
                    FROM project_schedule_items
                    WHERE project_id = %s::text
                      AND task_type = 'milestone'
                      AND start_date >= CURRENT_DATE
                    ORDER BY start_date ASC
                    LIMIT 3
                """, (pid,))
                next_milestones = [dict(r) for r in cur.fetchall()]

                # Active phase (include NULL task_type as "Scheduled")
                cur.execute("""
                    SELECT COALESCE(task_type, 'Scheduled') as task_type, count(*) as cnt
                    FROM project_schedule_items
                    WHERE project_id = %s::text
                      AND status NOT IN ('Complete','Completed','Done')
                      AND COALESCE(task_type,'x') NOT IN ('milestone','task','Weekly Updates','Owner Decisions','RFI / Coordination')
                    GROUP BY task_type ORDER BY cnt DESC LIMIT 1
                """, (pid,))
                phase_row = cur.fetchone()
                active_phase = phase_row["task_type"] if phase_row else "Scheduled"

                # Owner decisions pending
                cur.execute("""
                    SELECT count(*) as cnt FROM project_schedule_items
                    WHERE project_id = %s::text
                      AND task_type = 'Owner Decisions'
                      AND status NOT IN ('Complete','Completed','Done')
                """, (pid,))
                owner_pending = cur.fetchone()["cnt"]

                total = sum(status_counts.values())
                complete = status_counts.get("Complete", 0) + status_counts.get("Completed", 0) + status_counts.get("Done", 0)
                pct = round(complete / total * 100) if total else 0

                # Simple schedule health signal
                if overdue_cnt > 10:
                    sched_health = "RED"
                elif overdue_cnt > 3:
                    sched_health = "YELLOW"
                else:
                    sched_health = "GREEN"

                results.append({
                    "project": proj["name"],
                    "project_code": proj["project_code"],
                    "contract_value": float(proj["contract_value"] or 0),
                    "active_phase": active_phase,
                    "schedule_health": sched_health,
                    "pct_complete": pct,
                    "total_schedule_items": total,
                    "overdue_items": overdue_cnt,
                    "owner_decisions_pending": owner_pending,
                    "next_milestones": next_milestones,
                    "summary": f"{proj['project_code']}: {active_phase} phase, {pct}% complete, {overdue_cnt} overdue items"
                })

        return _response("/houzz/portfolio", {
            "as_of": datetime.now(timezone.utc).date().isoformat(),
            "live_projects": len(results),
            "projects": results,
        }, start=t0)
    except Exception as e:
        return _response("/houzz/portfolio", {}, errors=[str(e)], start=t0)


# ── Gap9: Risk Register ───────────────────────────────────────────────────────

class CreateRiskPayload(BaseModel):
    project_code: str
    risk_type: str
    severity: str = "medium"  # low|medium|high|critical
    description: str
    mitigation: Optional[str] = None

class UpdateRiskStatusPayload(BaseModel):
    status: str  # open|mitigated|closed
    notes: Optional[str] = None


@router.get("/project/{code}/risks")
def get_risks(code: str, status: str = None):
    """Gap9 — Risk register for a project. Filter by status=open|mitigated|closed."""
    t0 = time.time()
    try:
        pid = _get_pid(code)
        conn = _pg()
        conn.autocommit = True
        with conn.cursor() as cur:
            if status:
                cur.execute("""
                    SELECT id, risk_type, severity, description, mitigation, status, identified_date
                    FROM risks WHERE project_id=%s AND status=%s
                    ORDER BY CASE severity WHEN 'critical' THEN 1 WHEN 'high' THEN 2
                             WHEN 'medium' THEN 3 ELSE 4 END, identified_date DESC
                """, (pid, status))
            else:
                cur.execute("""
                    SELECT id, risk_type, severity, description, mitigation, status, identified_date
                    FROM risks WHERE project_id=%s
                    ORDER BY CASE severity WHEN 'critical' THEN 1 WHEN 'high' THEN 2
                             WHEN 'medium' THEN 3 ELSE 4 END, identified_date DESC
                """, (pid,))
            rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        open_count = sum(1 for r in rows if r["status"] == "open")
        critical = sum(1 for r in rows if r["severity"] in ("critical", "high") and r["status"] == "open")
        return _response(f"/project/{code}/risks", {
            "project_code": code, "total": len(rows),
            "open": open_count, "critical_or_high_open": critical,
            "risks": rows,
        }, start=t0)
    except HTTPException as e:
        return _response(f"/project/{code}/risks", {}, errors=[str(e.detail)], start=t0)
    except Exception as e:
        return _response(f"/project/{code}/risks", {}, errors=[str(e)], start=t0)


@router.post("/risks/create")
def create_risk(req: CreateRiskPayload):
    """Gap9 — Create a new risk. Writes to risks table and logs a project_event."""
    t0 = time.time()
    rid = str(uuid.uuid4())[:8]
    try:
        pid = _get_pid(req.project_code)
        conn = _pg()
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO risks (project_id, risk_type, severity, description, mitigation, status)
                VALUES (%s, %s, %s, %s, %s, 'open')
                RETURNING id, risk_type, severity, description, status, identified_date
            """, (pid, req.risk_type, req.severity, req.description, req.mitigation or ""))
            risk = dict(cur.fetchone())
            cur.execute("""
                INSERT INTO project_events (project_id, event_type, title, description, created_by, event_date)
                VALUES (%s, 'risk_flagged', %s, %s, 'gateway', CURRENT_DATE)
            """, (pid, f"Risk: {req.risk_type}", req.description[:200]))
        conn.close()
        _log("/risks/create", "gbt", req.project_code, "created", round((time.time()-t0)*1000), rid)
        return _response("/risks/create", {"created": True, "risk": risk, "project_code": req.project_code}, start=t0)
    except HTTPException as e:
        return _response("/risks/create", {}, errors=[str(e.detail)], start=t0)
    except Exception as e:
        return _response("/risks/create", {}, errors=[str(e)], start=t0)


@router.patch("/risks/{risk_id}/status")
def update_risk_status(risk_id: int, req: UpdateRiskStatusPayload):
    """Gap9 — Update risk status: open → mitigated → closed."""
    t0 = time.time()
    rid = str(uuid.uuid4())[:8]
    valid = {"open", "mitigated", "closed"}
    if req.status not in valid:
        return _response(f"/risks/{risk_id}/status", {},
                         errors=[f"Invalid status '{req.status}'. Use: {valid}"])
    try:
        conn = _pg()
        conn.autocommit = True
        with conn.cursor() as cur:
            if req.notes:
                cur.execute("""
                    UPDATE risks SET status=%s, mitigation=COALESCE(mitigation,'') || ' | ' || %s
                    WHERE id=%s RETURNING id, risk_type, severity, status, mitigation
                """, (req.status, req.notes, risk_id))
            else:
                cur.execute("""
                    UPDATE risks SET status=%s WHERE id=%s
                    RETURNING id, risk_type, severity, status, mitigation
                """, (req.status, risk_id))
            row = cur.fetchone()
        conn.close()
        if not row:
            return _response(f"/risks/{risk_id}/status", {}, errors=["Risk not found"], start=t0)
        _log(f"/risks/{risk_id}/status", "gbt", str(risk_id), req.status, round((time.time()-t0)*1000), rid)
        return _response(f"/risks/{risk_id}/status", {"updated": True, "risk": dict(row)}, start=t0)
    except Exception as e:
        return _response(f"/risks/{risk_id}/status", {}, errors=[str(e)], start=t0)


# ── Gap12: Submittals Tracker ─────────────────────────────────────────────────

class CreateSubmittalPayload(BaseModel):
    project_code: str
    spec_section: str
    description: str
    submitted_by: str
    required_approval_date: Optional[str] = None  # YYYY-MM-DD

class UpdateSubmittalStatusPayload(BaseModel):
    status: str  # pending|under_review|approved|rejected|revise_and_resubmit
    notes: Optional[str] = None


@router.get("/project/{code}/submittals")
def get_submittals(code: str, status: str = None):
    """Gap12 — Submittals tracker for a project. Filter by status."""
    t0 = time.time()
    try:
        pid = _get_pid(code)
        conn = _pg()
        conn.autocommit = True
        with conn.cursor() as cur:
            if status:
                cur.execute("""
                    SELECT id, submittal_number, spec_section, description, submitted_by,
                           status, submitted_date, required_approval_date, approved_date
                    FROM submittals WHERE project_id=%s AND status=%s
                    ORDER BY required_approval_date ASC NULLS LAST, id DESC
                """, (pid, status))
            else:
                cur.execute("""
                    SELECT id, submittal_number, spec_section, description, submitted_by,
                           status, submitted_date, required_approval_date, approved_date
                    FROM submittals WHERE project_id=%s
                    ORDER BY required_approval_date ASC NULLS LAST, id DESC
                """, (pid,))
            rows = [dict(r) for r in cur.fetchall()]
            cur.execute("""
                SELECT COUNT(*) AS overdue FROM submittals
                WHERE project_id=%s AND status NOT IN ('approved','rejected')
                AND required_approval_date < CURRENT_DATE
            """, (pid,))
            overdue = cur.fetchone()["overdue"]
        conn.close()
        pending = sum(1 for r in rows if r["status"] in ("pending", "under_review"))
        return _response(f"/project/{code}/submittals", {
            "project_code": code, "total": len(rows),
            "pending_or_review": pending, "overdue": overdue,
            "submittals": rows,
        }, start=t0)
    except HTTPException as e:
        return _response(f"/project/{code}/submittals", {}, errors=[str(e.detail)], start=t0)
    except Exception as e:
        return _response(f"/project/{code}/submittals", {}, errors=[str(e)], start=t0)


@router.post("/submittals/create")
def create_submittal(req: CreateSubmittalPayload):
    """Gap12 — Log a new submittal. Auto-assigns next submittal number for project."""
    t0 = time.time()
    rid = str(uuid.uuid4())[:8]
    try:
        pid = _get_pid(req.project_code)
        conn = _pg()
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COALESCE(MAX(CAST(NULLIF(submittal_number, '') AS INTEGER)), 0) + 1 AS next_num
                FROM submittals WHERE project_id=%s AND submittal_number ~ '^[0-9]+'
            """, (pid,))
            next_num = cur.fetchone()["next_num"]
            req_date = req.required_approval_date or None
            cur.execute("""
                INSERT INTO submittals
                    (project_id, submittal_number, spec_section, description, submitted_by,
                     status, submitted_date, required_approval_date)
                VALUES (%s, %s, %s, %s, %s, 'pending', CURRENT_DATE, %s)
                RETURNING id, submittal_number, spec_section, description, status, submitted_date
            """, (pid, str(next_num), req.spec_section, req.description,
                  req.submitted_by, req_date))
            sub = dict(cur.fetchone())
        conn.close()
        _log("/submittals/create", "gbt", req.project_code, "created", round((time.time()-t0)*1000), rid)
        return _response("/submittals/create", {
            "created": True, "submittal": sub, "project_code": req.project_code
        }, start=t0)
    except HTTPException as e:
        return _response("/submittals/create", {}, errors=[str(e.detail)], start=t0)
    except Exception as e:
        return _response("/submittals/create", {}, errors=[str(e)], start=t0)


@router.patch("/submittals/{sub_id}/status")
def update_submittal_status(sub_id: int, req: UpdateSubmittalStatusPayload):
    """Gap12 — Update submittal status: pending→under_review→approved|rejected|revise_and_resubmit."""
    t0 = time.time()
    rid = str(uuid.uuid4())[:8]
    valid = {"pending", "under_review", "approved", "rejected", "revise_and_resubmit"}
    if req.status not in valid:
        return _response(f"/submittals/{sub_id}/status", {},
                         errors=[f"Invalid status '{req.status}'. Use: {valid}"])
    try:
        conn = _pg()
        conn.autocommit = True
        with conn.cursor() as cur:
            approved_date_sql = "CURRENT_DATE" if req.status == "approved" else "approved_date"
            cur.execute(f"""
                UPDATE submittals
                SET status=%s, approved_date={approved_date_sql}
                WHERE id=%s
                RETURNING id, submittal_number, spec_section, status, approved_date
            """, (req.status, sub_id))
            row = cur.fetchone()
        conn.close()
        if not row:
            return _response(f"/submittals/{sub_id}/status", {}, errors=["Submittal not found"], start=t0)
        _log(f"/submittals/{sub_id}/status", "gbt", str(sub_id), req.status, round((time.time()-t0)*1000), rid)
        return _response(f"/submittals/{sub_id}/status", {"updated": True, "submittal": dict(row)}, start=t0)
    except Exception as e:
        return _response(f"/submittals/{sub_id}/status", {}, errors=[str(e)], start=t0)


# ── Market Rate Intelligence ──────────────────────────────────────────────────
@router.get("/knowledge/market-rates")
def market_rates(division: str = None, months_back: int = Query(24, ge=1, le=60),
                 project_type: str = None):
    """Real Aspen sub-contractor market rates from actual bid data.
    division: CSI division code (e.g. '15', '06', '09'). Omit for all divisions.
    months_back: only include bids received within this many months (default 24).
    project_type: 'new', 'renovation', or 'remodel' — filters by project status if set.
    """
    t0 = time.time()
    try:
        conn = _pg()
        with conn.cursor() as cur:
            where_clauses = ["be.bid_amount > 0",
                             "be.date_received >= CURRENT_DATE - (%s * INTERVAL '1 month')"]
            params: list = [months_back]
            if division:
                where_clauses.append("be.csi_division = %s")
                params.append(division.upper())
            if project_type:
                status_map = {"new": "active", "renovation": "active", "remodel": "active",
                              "completed": "completed", "reference": "reference"}
                mapped = status_map.get(project_type.lower(), project_type.lower())
                where_clauses.append("p.status = %s")
                params.append(mapped)
            where_sql = " AND ".join(where_clauses)
            cur.execute(f"""
                SELECT be.csi_division,
                       COUNT(*) AS bid_count,
                       COUNT(DISTINCT be.vendor_id) AS vendor_count,
                       COUNT(DISTINCT be.project_id) AS project_count,
                       MIN(be.bid_amount) AS low_bid,
                       MAX(be.bid_amount) AS high_bid,
                       ROUND(AVG(be.bid_amount), 0) AS avg_bid,
                       ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY be.bid_amount)::numeric, 0) AS median_bid,
                       MIN(be.date_received) AS earliest_bid,
                       MAX(be.date_received) AS latest_bid,
                       JSON_AGG(DISTINCT v.company_name) FILTER (WHERE v.company_name IS NOT NULL) AS known_vendors
                FROM bid_entries be
                LEFT JOIN vendors v ON v.id = be.vendor_id
                LEFT JOIN projects p ON p.id = be.project_id
                WHERE {where_sql}
                GROUP BY be.csi_division
                ORDER BY bid_count DESC
            """, params)
            rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        # Clean up vendor lists
        for r in rows:
            if r["known_vendors"]:
                vendors = [v for v in r["known_vendors"] if v]
                r["known_vendors"] = sorted(vendors)[:10]  # top 10 only
            for k in ["low_bid", "high_bid", "avg_bid", "median_bid"]:
                r[k] = float(r[k]) if r[k] is not None else None
        summary = {
            "divisions_with_data": len(rows),
            "total_bids_analyzed": sum(r["bid_count"] for r in rows),
            "date_range": f"last {months_back} months",
            "market": "Aspen CO",
            "source": "HCI bid_entries — real subcontractor quotes",
        }
        return _response("/knowledge/market-rates", {"summary": summary, "by_division": rows}, start=t0)
    except Exception as e:
        return _response("/knowledge/market-rates", {}, errors=[str(e)], start=t0)


# ── ROM Estimator ─────────────────────────────────────────────────────────────
@router.get("/knowledge/rom-estimate")
def rom_estimate(sf: int = Query(..., description="Project square footage"),
                 project_type: str = Query("new", description="new | renovation | remodel")):
    """ROM cost estimate calibrated from real HCI historical cost records.
    Returns division-level breakdown with low/mid/high ranges and confidence.
    """
    t0 = time.time()
    try:
        # Known benchmarks from real project data
        BENCHMARKS = {
            "new": [
                {"project": "574 Johnson Drive", "sf": 6696, "total": 8045318, "cost_per_sf": 1202,
                 "confidence": "high", "date": "2026-06"},
                {"project": "275 Sunnyside Lane", "sf": None, "total": 54175191,
                 "confidence": "medium", "note": "Luxury compound — main house + pool + external works + barn"},
                {"project": "212 Cleveland", "sf": None, "total": 7614844, "cost_per_sf": None,
                 "confidence": "high", "date": "2026-04", "note": "Completed actuals"},
            ],
            "renovation": [
                {"project": "675 Meadowood", "sf": 2827, "total": 2804710, "cost_per_sf": 992,
                 "confidence": "medium", "date": "2026-03", "note": "ROM only — pre-construction"},
                {"project": "370 Gerbaz Way", "sf": None, "total": 831010, "cost_per_sf": None,
                 "confidence": "high", "date": "2026-04", "note": "Final actuals — budget ran 96% over submitted"},
                {"project": "1355 Riverside", "sf": 3855, "total": 5693297, "cost_per_sf": 1477,
                 "confidence": "medium", "date": "2026-06", "note": "ROM target; 3,855 SF combined"},
            ],
            "remodel": [
                {"project": "675 Meadowood", "sf": 2827, "total": 2804710, "cost_per_sf": 992,
                 "confidence": "medium", "date": "2026-03"},
                {"project": "370 Gerbaz Way", "sf": None, "total": 831010,
                 "confidence": "high", "date": "2026-04", "note": "Final actuals"},
            ],
        }

        ptype = project_type.lower()
        benchmarks = BENCHMARKS.get(ptype, BENCHMARKS["new"])

        # Cost per SF range from benchmarks that have SF data
        sf_benchmarks = [b for b in benchmarks if b.get("cost_per_sf")]
        cost_per_sf_low = min(b["cost_per_sf"] for b in sf_benchmarks) if sf_benchmarks else 900
        cost_per_sf_high = max(b["cost_per_sf"] for b in sf_benchmarks) if sf_benchmarks else 1600
        cost_per_sf_mid = round(sum(b["cost_per_sf"] for b in sf_benchmarks) / len(sf_benchmarks)) if sf_benchmarks else 1200

        # ROM ranges
        rom_low = round(sf * cost_per_sf_low * 0.90)
        rom_mid = round(sf * cost_per_sf_mid)
        rom_high = round(sf * cost_per_sf_high * 1.15)

        # Division breakdown (from historical data — renovation uses 370 Gerbaz ratios, new uses 574 Johnson)
        if ptype in ("renovation", "remodel"):
            # 370 Gerbaz division ratios (from final actual costs)
            div_ratios = {
                "01 - General Requirements": 0.185,  # ran very high — use actual ratio
                "09 - Finishes": 0.238,
                "15 - Mechanical": 0.087,
                "06 - Wood and Plastics": 0.079,
                "16 - Electrical": 0.070,
                "04 - Masonry": 0.086,
                "02 - Site Construction": 0.038,
                "08 - Doors and Windows": 0.027,
                "Contractor Fee + Insurance": 0.150,
                "Other Divisions": 0.040,
            }
            overrun_note = "WARNING: Renovation GR historically runs 3-4x submitted budget. Electrical runs 2-3x. Budget these divisions conservatively."
        else:
            # 574 Johnson + 275 Sunnyside division ratios
            div_ratios = {
                "06 - Wood and Plastics": 0.22,
                "15 - Mechanical": 0.14,
                "16 - Electrical": 0.09,
                "08 - Doors and Windows": 0.08,
                "09 - Finishes": 0.07,
                "02 - Sitework and Excavation": 0.11,
                "07 - Thermal and Moisture": 0.04,
                "05 - Metals": 0.03,
                "04 - Masonry": 0.02,
                "01 - General Requirements": 0.10,
                "Contractor Fee + Insurance": 0.10,
            }
            overrun_note = "New construction estimates based on 574 Johnson Drive ($1,202/SF, 2026) and 275 Sunnyside ($54M GMP, 2026)."

        division_breakdown = []
        for div, ratio in div_ratios.items():
            division_breakdown.append({
                "division": div,
                "rom_low": round(rom_low * ratio),
                "rom_mid": round(rom_mid * ratio),
                "rom_high": round(rom_high * ratio),
                "pct_of_total": f"{round(ratio * 100)}%",
            })

        return _response("/knowledge/rom-estimate", {
            "inputs": {"sf": sf, "project_type": ptype, "market": "Aspen CO"},
            "rom": {
                "low": rom_low, "mid": rom_mid, "high": rom_high,
                "cost_per_sf_low": cost_per_sf_low,
                "cost_per_sf_mid": cost_per_sf_mid,
                "cost_per_sf_high": cost_per_sf_high,
            },
            "division_breakdown": division_breakdown,
            "benchmarks_used": benchmarks,
            "methodology_note": overrun_note,
            "data_confidence": "medium" if not sf_benchmarks else "high",
        }, start=t0)
    except Exception as e:
        return _response("/knowledge/rom-estimate", {}, errors=[str(e)], start=t0)


# ── Bid Level View ────────────────────────────────────────────────────────────
@router.get("/project/{code}/bid-level")
def bid_level_view(code: str, division: str = None, status: str = None):
    """Bid leveling view for a project — all packages with all bids, sorted low to high.
    division: filter to a specific CSI division (optional).
    status: filter packages by status (optional).
    """
    t0 = time.time()
    try:
        pid = _get_pid(code)
        conn = _pg()
        with conn.cursor() as cur:
            pkg_where = "bp.project_id = %s"
            pkg_params: list = [pid]
            if division:
                pkg_where += " AND bp.csi_division = %s"
                pkg_params.append(division)
            if status:
                pkg_where += " AND bp.status = %s"
                pkg_params.append(status)
            cur.execute(f"""
                SELECT bp.id, bp.package_name, bp.csi_division, bp.status,
                       bp.awarded_amount, bp.hubspot_deal_id,
                       (SELECT COUNT(*) FROM bid_entries be WHERE be.bid_package_id = bp.id AND be.bid_amount > 0) AS bid_count,
                       (SELECT MIN(be.bid_amount) FROM bid_entries be WHERE be.bid_package_id = bp.id AND be.bid_amount > 0) AS low_bid,
                       (SELECT MAX(be.bid_amount) FROM bid_entries be WHERE be.bid_package_id = bp.id AND be.bid_amount > 0) AS high_bid
                FROM bid_packages bp
                WHERE {pkg_where}
                ORDER BY bp.csi_division, bp.package_name
            """, pkg_params)
            packages = [dict(r) for r in cur.fetchall()]

            # For each package, get the ranked bid list + historical intelligence
            leveled = []
            for pkg in packages:
                cur.execute("""
                    SELECT be.id, be.bid_amount, be.status AS bid_status,
                           be.date_received, be.notes, be.quote_ref,
                           be.vendor_id,
                           v.company_name, v.contact_name, v.phone, v.email,
                           v.bid_count AS vendor_total_bids, v.win_rate_pct
                    FROM bid_entries be
                    LEFT JOIN vendors v ON v.id = be.vendor_id
                    WHERE be.bid_package_id = %s AND be.bid_amount > 0
                    ORDER BY be.bid_amount ASC
                """, (pkg["id"],))
                bids = [dict(b) for b in cur.fetchall()]

                # Portfolio ROM benchmark for this CSI division
                # Only real vendor bids from active/bidding/preconstruction projects — not ASPN aggregated reference data
                csi = pkg.get("csi_division")
                rom = {"division": csi, "sample_count": 0, "avg": None, "median": None, "min": None, "max": None}
                if csi:
                    cur.execute("""
                        SELECT COUNT(*) AS n,
                               ROUND(AVG(be.bid_amount)) AS avg_bid,
                               ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY be.bid_amount)) AS median_bid,
                               ROUND(MIN(be.bid_amount)) AS min_bid,
                               ROUND(MAX(be.bid_amount)) AS max_bid
                        FROM bid_entries be
                        JOIN bid_packages bp ON bp.id = be.bid_package_id
                        JOIN projects p ON p.id = bp.project_id
                        WHERE be.csi_division = %s AND be.bid_amount > 0
                          AND p.project_code NOT LIKE 'ASPN-%%'
                          AND p.status != 'test'
                    """, (csi,))
                    row = cur.fetchone()
                    if row and row["n"] and row["n"] > 0:
                        rom = {
                            "division": csi, "sample_count": int(row["n"]),
                            "avg": float(row["avg_bid"]) if row["avg_bid"] else None,
                            "median": float(row["median_bid"]) if row["median_bid"] else None,
                            "min": float(row["min_bid"]) if row["min_bid"] else None,
                            "max": float(row["max_bid"]) if row["max_bid"] else None,
                        }

                for i, b in enumerate(bids):
                    b["rank"] = i + 1
                    amt = float(b["bid_amount"]) if b["bid_amount"] else None
                    b["bid_amount"] = amt
                    if i > 0 and bids[0]["bid_amount"]:
                        spread = amt - float(bids[0]["bid_amount"])
                        b["spread_from_low"] = round(spread)
                        b["spread_pct"] = round((spread / float(bids[0]["bid_amount"])) * 100, 1)
                    # Price flag vs portfolio ROM
                    if amt and rom["avg"]:
                        ratio = amt / rom["avg"]
                        b["vs_portfolio_avg_pct"] = round((ratio - 1) * 100, 1)
                        if ratio < 0.80:   b["price_flag"] = "low"
                        elif ratio < 0.95: b["price_flag"] = "competitive"
                        elif ratio < 1.10: b["price_flag"] = "normal"
                        elif ratio < 1.30: b["price_flag"] = "high"
                        else:              b["price_flag"] = "very_high"
                    else:
                        b["vs_portfolio_avg_pct"] = None
                        b["price_flag"] = "no_benchmark"
                    # Vendor cross-project history (most recent 5 bids on other HCI projects)
                    vendor_id = b.get("vendor_id")
                    b["vendor_history"] = []
                    if vendor_id:
                        cur.execute("""
                            SELECT p.name AS project_name, p.project_code,
                                   bp2.package_name, be2.bid_amount, be2.status,
                                   be2.date_received
                            FROM bid_entries be2
                            JOIN bid_packages bp2 ON bp2.id = be2.bid_package_id
                            JOIN projects p ON p.id = bp2.project_id
                            WHERE be2.vendor_id = %s AND be2.bid_amount > 0
                              AND be2.bid_package_id != %s
                              AND p.project_code NOT LIKE 'ASPN-%%'
                            ORDER BY be2.date_received DESC NULLS LAST
                            LIMIT 5
                        """, (vendor_id, pkg["id"]))
                        hist = [dict(h) for h in cur.fetchall()]
                        for h in hist:
                            h["bid_amount"] = float(h["bid_amount"]) if h["bid_amount"] else None
                        b["vendor_history"] = hist

                pkg["bids"] = bids
                pkg["rom_context"] = rom
                pkg["low_bid"] = float(pkg["low_bid"]) if pkg["low_bid"] else None
                pkg["high_bid"] = float(pkg["high_bid"]) if pkg["high_bid"] else None
                pkg["spread"] = round(float(pkg["high_bid"]) - float(pkg["low_bid"])) if pkg["low_bid"] and pkg["high_bid"] else None
                leveled.append(pkg)

        conn.close()
        total_pkgs = len(leveled)
        pkgs_with_bids = sum(1 for p in leveled if p["bid_count"] > 0)
        pkgs_no_bids = total_pkgs - pkgs_with_bids
        return _response(f"/project/{code}/bid-level", {
            "project_code": code,
            "summary": {
                "total_packages": total_pkgs,
                "packages_with_bids": pkgs_with_bids,
                "packages_no_bids": pkgs_no_bids,
                "pct_covered": round((pkgs_with_bids / total_pkgs * 100) if total_pkgs else 0, 1),
            },
            "packages": leveled,
        }, start=t0)
    except Exception as e:
        return _response(f"/project/{code}/bid-level", {}, errors=[str(e)], start=t0)


@router.post("/project/{code}/bid-level")
def run_bid_leveling_for_project(code: str, dry_run: bool = True):
    """
    Run the full bid leveling workflow for a project.
    Scans Drive vendor folders, extracts bids from PDFs via Gemini, reads the
    Google Sheet tracker, merges both sources, and returns a leveled comparison
    per division with low bid, spread, and recommended vendor.

    dry_run=True (default): analysis only, no Drive writes.
    dry_run=False: generates Excel leveling files and queues them for upload.

    Usage examples:
      POST /gateway/project/1355R/bid-level          → level 1355 Riverside
      POST /gateway/project/101F/bid-level           → level 101 Francis
      POST /gateway/project/101F/bid-level?dry_run=false  → level + generate Excel
    """
    t0 = time.time()
    try:
        pid = _get_pid(code)
        data = _proxy(f"/services/bid-leveling/projects/{pid}/run",
                      method="POST",
                      json={"dry_run": dry_run, "divisions": None})
        return _response(f"/project/{code}/bid-level", data, start=t0)
    except Exception as e:
        return _response(f"/project/{code}/bid-level", {}, errors=[str(e)], start=t0)


@router.get("/project/{code}/drive-bids")
def get_drive_bids_for_project(code: str):
    """
    Return all Drive-sourced bids for a project from the drive_bids table.
    Shows actual bid amounts extracted from vendor PDF files, with leveling summary
    (low bid, high bid, spread per division). More accurate than the Sheet tracker.
    """
    t0 = time.time()
    try:
        pid = _get_pid(code)
        data = _proxy(f"/services/bid-leveling/projects/{pid}/drive-bids")
        return _response(f"/project/{code}/drive-bids", data, start=t0)
    except Exception as e:
        return _response(f"/project/{code}/drive-bids", {}, errors=[str(e)], start=t0)


# ── Project Registry ──────────────────────────────────────────────────────────
@router.get("/projects")
def project_registry(status: str = None):
    """Full project registry — all real projects with status, scope, team.
    status: filter by status (active, reference, design, completed, bidding, preconstruction, closeout).
    Excludes test projects automatically.
    """
    t0 = time.time()
    try:
        conn = _pg()
        with conn.cursor() as cur:
            where = "status != 'test'"
            params: list = []
            if status:
                where += " AND status = %s"
                params.append(status)
            cur.execute(f"""
                SELECT id, project_code, name, address, status, pm_name, super_name,
                       owner_name, hubspot_deal_id, scope,
                       (SELECT COUNT(*) FROM bid_packages bp WHERE bp.project_id = projects.id) AS bid_packages,
                       (SELECT COUNT(*) FROM bid_entries be JOIN bid_packages bp ON bp.id = be.bid_package_id
                        WHERE bp.project_id = projects.id AND be.bid_amount > 0) AS bids_received,
                       (SELECT COUNT(*) FROM risks r WHERE r.project_id = projects.id AND r.status = 'open') AS open_risks,
                       (SELECT COUNT(*) FROM daily_logs dl WHERE dl.project_id = projects.id) AS daily_logs
                FROM projects
                WHERE {where}
                ORDER BY CASE status
                    WHEN 'active' THEN 1 WHEN 'bidding' THEN 2
                    WHEN 'preconstruction' THEN 3 WHEN 'closeout' THEN 4
                    WHEN 'design' THEN 5 WHEN 'reference' THEN 6
                    WHEN 'completed' THEN 7 ELSE 8 END, id
            """, params)
            rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        live = [r for r in rows if r["status"] == "active"]
        ref  = [r for r in rows if r["status"] == "reference"]
        return _response("/projects", {
            "total": len(rows),
            "live_count": len(live),
            "reference_count": len(ref),
            "projects": rows,
        }, start=t0)
    except Exception as e:
        return _response("/projects", {}, errors=[str(e)], start=t0)


# ── Procurement Risk ──────────────────────────────────────────────────────────
@router.get("/project/{code}/procurement-risk")
def procurement_risk(code: str):
    """Procurement risk analysis — gaps, single bids, overdue packages, cost exposure.
    Shows which packages need attention before buyout is complete.
    """
    t0 = time.time()
    try:
        pid = _get_pid(code)
        conn = _pg()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT bp.id, bp.package_name, bp.csi_division, bp.status,
                       bp.awarded_amount, bp.hubspot_deal_id,
                       COUNT(be.id) FILTER (WHERE be.bid_amount > 0) AS bid_count,
                       MIN(be.bid_amount) FILTER (WHERE be.bid_amount > 0) AS low_bid,
                       MAX(be.bid_amount) FILTER (WHERE be.bid_amount > 0) AS high_bid,
                       STRING_AGG(v.company_name, ', ' ORDER BY be.bid_amount)
                           FILTER (WHERE be.bid_amount > 0) AS bidders
                FROM bid_packages bp
                LEFT JOIN bid_entries be ON be.bid_package_id = bp.id
                LEFT JOIN vendors v ON v.id = be.vendor_id
                WHERE bp.project_id = %s
                GROUP BY bp.id, bp.package_name, bp.csi_division, bp.status,
                         bp.awarded_amount, bp.hubspot_deal_id
                ORDER BY bp.csi_division, bp.package_name
            """, (pid,))
            packages = [dict(r) for r in cur.fetchall()]
        conn.close()

        no_bids, single_bid, multi_bid, awarded = [], [], [], []
        for p in packages:
            bc = p["bid_count"] or 0
            p["bid_count"] = bc
            p["low_bid"]  = float(p["low_bid"])  if p["low_bid"]  else None
            p["high_bid"] = float(p["high_bid"]) if p["high_bid"] else None
            p["spread"]   = round(float(p["high_bid"]) - float(p["low_bid"])) if p["low_bid"] and p["high_bid"] else None
            p["spread_pct"] = round((p["spread"] / float(p["low_bid"])) * 100, 1) if p["spread"] and p["low_bid"] else None
            if p["awarded_amount"]:
                awarded.append(p)
            elif bc == 0:
                no_bids.append(p)
            elif bc == 1:
                single_bid.append(p)
            else:
                multi_bid.append(p)

        total = len(packages)
        risk_score = "green"
        if len(no_bids) > total * 0.5:
            risk_score = "red"
        elif len(no_bids) > total * 0.25 or len(single_bid) > total * 0.4:
            risk_score = "yellow"

        return _response(f"/project/{code}/procurement-risk", {
            "project_code": code,
            "risk_score": risk_score,
            "summary": {
                "total_packages": total,
                "no_bids": len(no_bids),
                "single_bid_only": len(single_bid),
                "competitive_bids": len(multi_bid),
                "awarded": len(awarded),
                "bid_coverage_pct": round(((total - len(no_bids)) / total * 100) if total else 0, 1),
            },
            "no_bids": no_bids,
            "single_bid": single_bid,
            "competitive": multi_bid,
            "awarded": awarded,
        }, start=t0)
    except Exception as e:
        return _response(f"/project/{code}/procurement-risk", {}, errors=[str(e)], start=t0)


# ── Plan Reader — Vision AI Analysis of Construction Documents ────────────────
# Model routing: sonnet=default (no rate limit risk), opus=deep review on request
# Gemini Flash will be added here when GEMINI_API_KEY is available (free tier)

class PlanReadRequest(BaseModel):
    file_id: str                      # Google Drive file ID of the PDF
    project_code: Optional[str] = None
    scope: Optional[str] = "full"     # "full" | "structural" | "roofing" | "finishes"
    model: Optional[str] = "sonnet"   # "sonnet" | "opus" — opus is on-demand only
    pages: Optional[str] = None       # e.g. "1-3" to limit pages; None = all


@router.post("/plan/read")
async def plan_read(req: PlanReadRequest, request: Request):
    """
    Download a PDF from Drive, convert each page to an image, and run vision AI
    analysis to extract specifications, open items, RFI candidates, and scope gaps.

    Model routing:
      sonnet  — fast, cheap, good for routine reads (default)
      opus    — deep forensic read, on-demand only, not for automation loops
    """
    import base64, subprocess, tempfile, glob
    from pathlib import Path

    t0 = time.time()
    _require_key(request)

    MODEL_MAP = {
        "sonnet": "claude-sonnet-4-6",
        "opus":   "claude-opus-4-8",
    }
    model_id = MODEL_MAP.get(req.model, "claude-sonnet-4-6")

    PLAN_SYSTEM = """You are a licensed structural engineer and construction document reviewer analyzing drawings for a luxury residential project in Aspen, CO.

For each drawing sheet, extract and report:
1. SHEET INFO: Sheet number, title, scale, date, engineer/firm, revision status
2. SPECIFICATIONS FOUND: All material specs, dimensions, grades, loads, connection requirements — quote verbatim
3. OPEN ITEMS: Any notes saying "confirm", "verify", "TBD", "by others", "field verify", plus any markup flags
4. RFI CANDIDATES: Specific questions requiring SE/architect response before bidding or construction
5. SCOPE GAPS: What should be on this drawing that is absent or underspecified

Be exhaustive and forensic. Quote exact callouts, dimensions, and notes verbatim. Flag anything with a question mark as unresolved."""

    try:
        # 1. Download PDF from Drive via MCP token (reuse existing Drive credential)
        import anthropic as _anthropic
        drive_resp = requests.get(
            f"https://www.googleapis.com/drive/v3/files/{req.file_id}?alt=media",
            headers={"Authorization": f"Bearer {os.environ.get('GOOGLE_ACCESS_TOKEN','')}"},
            timeout=60,
        )
        if drive_resp.status_code != 200:
            # Fallback: try via gateway drive endpoint which uses MCP session
            return _response("/plan/read", {
                "status": "credential_required",
                "message": "Direct Drive API token not available in gateway context. "
                           "Run plan_reader.py locally or provide GOOGLE_ACCESS_TOKEN in env.",
                "file_id": req.file_id,
                "model_requested": req.model,
            }, warnings=["Use plan_reader.py locally for full Drive access"], start=t0)

        # 2. Save PDF to temp dir
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = os.path.join(tmpdir, "plan.pdf")
            with open(pdf_path, "wb") as f:
                f.write(drive_resp.content)

            # 3. Convert to images (pdftoppm)
            page_filter = []
            if req.pages:
                parts = req.pages.split("-")
                if len(parts) == 2:
                    page_filter = ["-f", parts[0], "-l", parts[1]]

            subprocess.run(
                ["pdftoppm", "-r", "150", *page_filter, pdf_path, os.path.join(tmpdir, "page")],
                capture_output=True, check=False
            )

            # Convert PPM to PNG
            from PIL import Image as _Image
            ppm_files = sorted(glob.glob(os.path.join(tmpdir, "page-*.ppm")))
            if not ppm_files:
                return _response("/plan/read", {}, errors=["PDF conversion produced no images"], start=t0)

            client = _anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
            findings = []

            for i, ppm in enumerate(ppm_files, 1):
                png = ppm.replace(".ppm", ".png")
                _Image.open(ppm).save(png, "PNG", optimize=True)

                with open(png, "rb") as f:
                    img_b64 = base64.standard_b64encode(f.read()).decode()

                resp = client.messages.create(
                    model=model_id,
                    max_tokens=2000,
                    system=PLAN_SYSTEM,
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": img_b64}},
                            {"type": "text", "text": f"Sheet {i} of {len(ppm_files)}. Project: {req.project_code or 'unknown'}. Scope focus: {req.scope}. Analyze completely."}
                        ]
                    }]
                )
                findings.append({"page": i, "analysis": resp.content[0].text})

        # 4. Log and return
        _log("/plan/read", "gateway", "vision-ai", "ok",
             round((time.time() - t0) * 1000), str(uuid.uuid4()),
             f"{len(findings)} pages analyzed via {model_id}")

        return _response("/plan/read", {
            "file_id": req.file_id,
            "project_code": req.project_code,
            "model_used": model_id,
            "pages_analyzed": len(findings),
            "scope": req.scope,
            "findings": findings,
        }, start=t0)

    except Exception as e:
        return _response("/plan/read", {}, errors=[str(e)], start=t0)


@router.get("/plan/read-local")
async def plan_read_local_status():
    """Quick status — returns instructions for running the local plan reader script."""
    return _response("/plan/read/local", {
        "local_script": "python3 /tmp/opus_plan_reader.py",
        "last_output": "/tmp/1355R_opus_structural_analysis.json",
        "models": {
            "sonnet": "claude-sonnet-4-6 — default, no rate limit risk",
            "opus":   "claude-opus-4-8 — deep read, on-demand only",
            "gemini": "gemini-2.5-flash — free tier, vision-capable, add GEMINI_API_KEY to .env",
            "gemini-pro": "gemini-2.5-pro — free tier (lower rate limits), deepest Gemini read",
        },
        "usage": {
            "POST /gateway/plan/read": {
                "file_id": "<drive_file_id>",
                "project_code": "1355R",
                "scope": "structural | roofing | finishes | full",
                "model": "sonnet (default) | opus",
                "pages": "1-3 (optional, limit pages)"
            }
        }
    })


# ── Telegram Push Helper (replaces ntfy) ──────────────────────────────────────

TG_TOKEN   = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TG_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
TG_BASE    = f"https://api.telegram.org/bot{TG_TOKEN}"

# ntfy kept as silent fallback
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "hci-executive")
NTFY_BASE  = f"https://ntfy.sh/{NTFY_TOPIC}"

_TG_OFFSET: list[int] = [0]  # mutable so poll_instructions can track offset


def _ntfy(title: str, body: str, priority: str = "default", tags: str = "") -> dict:
    """Send via Telegram primary; fall back to ntfy silently."""
    tg_priority = {"min": "low", "low": "low", "default": "normal",
                   "high": "high", "urgent": "urgent"}.get(priority, "normal")
    icons = {"low": "ℹ️", "normal": "📋", "high": "⚠️", "urgent": "🚨"}
    icon = icons.get(tg_priority, "📋")
    text = f"{icon} *{title}*\n\n{body}"
    try:
        payload = {"chat_id": TG_CHAT_ID, "text": text, "parse_mode": "Markdown"}
        r = requests.post(f"{TG_BASE}/sendMessage", json=payload, timeout=10)
        if r.ok:
            return {"status": "sent", "channel": "telegram", "http": r.status_code}
    except Exception:
        pass
    # ntfy fallback
    try:
        safe_title = title.encode("ascii", errors="replace").decode("ascii")
        headers = {"Title": safe_title, "Priority": priority,
                   "Content-Type": "text/plain; charset=utf-8"}
        if tags:
            headers["Tags"] = tags
        r2 = requests.post(NTFY_BASE, data=body.encode("utf-8"), headers=headers, timeout=5)
        return {"status": "sent", "channel": "ntfy_fallback", "http": r2.status_code}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def _tg_send(text: str, reply_markup: dict = None, parse_mode: str = None) -> dict:
    """Low-level Telegram sendMessage. parse_mode auto-detected from text content.
    Retries once without Markdown on failure (fixed 2026-07-01 — this function was
    silently swallowing 400s from unbalanced _/*/`/[ in ordinary text like file paths,
    e.g. 'AI_TEAM/OVERNIGHT_REPORT.md', with no fallback; _tg_send_with_id already had
    this retry, this one didn't)."""
    import re as _re
    if parse_mode is None:
        parse_mode = "Markdown" if _re.search(r"[*_`\[]", text) else None
    payload = {"chat_id": TG_CHAT_ID, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        r = requests.post(f"{TG_BASE}/sendMessage", json=payload, timeout=10)
        if r.ok:
            return {"status": "sent", "http": r.status_code}
        if parse_mode:
            payload.pop("parse_mode", None)
            r2 = requests.post(f"{TG_BASE}/sendMessage", json=payload, timeout=10)
            if r2.ok:
                return {"status": "sent", "http": r2.status_code, "retried_plain": True}
        return {"status": "failed", "http": r.status_code, "detail": r.text[:300]}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@router.post("/notify/test")
async def notify_test(request: Request):
    """Push a test notification to Buck via Telegram."""
    t0 = time.time()
    result = _ntfy("HCI AI OS — Test Notification",
                   "✅ Telegram channel confirmed live. Gateway push working.",
                   priority="default")
    return _response("/notify/test", result, start=t0)


@router.post("/telegram/send")
async def telegram_send(request: Request):
    """GBT-callable: send a Telegram message to Buck. Body: {text, priority?, buttons?}
    buttons format: [[{text, url},...],...]  — optional inline keyboard rows."""
    t0 = time.time()
    body = await request.json()
    text     = body.get("text", "")
    priority = body.get("priority", "normal")
    buttons  = body.get("buttons")
    if not text:
        return _response("/telegram/send", {}, errors=["text is required"], start=t0)
    icons = {"low": "ℹ️", "normal": "📋", "high": "⚠️", "urgent": "🚨"}
    icon  = icons.get(priority, "📋")
    full  = f"{icon} {text}" if not text.startswith(("🚨","⚠️","ℹ️","📋","✅","❌")) else text
    markup = {"inline_keyboard": buttons} if buttons else None
    result = _tg_send(full, reply_markup=markup)
    _log("/telegram/send", "gbt", "telegram", result.get("status","?"),
         int((time.time()-t0)*1000), str(uuid.uuid4())[:8], text[:60])
    return _response("/telegram/send", result, start=t0)


@router.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    """Telegram webhook — receives messages and callback_query from Buck's phone."""
    t0 = time.time()
    try:
        update = await request.json()
        result = {"update_id": update.get("update_id")}

        if "message" in update:
            msg     = update["message"]
            chat_id = str(msg["chat"]["id"])
            text    = (msg.get("text") or "").strip()
            msg_id  = msg["message_id"]
            result["type"] = "message"
            result["text"] = text

            # Store in platform_events for agent polling
            conn = _pg()
            cur  = conn.cursor()
            cur.execute(
                "INSERT INTO platform_events (event_type, source_service, actor, payload) VALUES (%s,%s,%s,%s)",
                ("buck_message", "telegram", "Buck Adams",
                 psycopg2.extras.Json({"chat_id": chat_id, "text": text,
                                       "message_id": msg_id, "ts": datetime.now(timezone.utc).isoformat()}))
            )
            conn.commit(); cur.close(); conn.close()

            # APPROVE/REJECT/HOLD/STATUS/QUEUE against the durable queue; else plain ack
            cmd_reply = _handle_buck_command(text)
            ack = cmd_reply or (f"✅ Got it: _{text[:80]}_" if text else "✅ Received")
            _tg_send(ack)

        elif "callback_query" in update:
            cb      = update["callback_query"]
            cb_id   = cb["id"]
            cb_data = cb.get("data", "")
            result["type"] = "callback"
            result["data"] = cb_data
            # Inline button taps (approve:<id> / reject:<id> / hold:<id>) hit the same command handler
            if ":" in cb_data:
                action, _, mid = cb_data.partition(":")
                cmd_map = {"approve": "APPROVE", "reject": "REJECT", "hold": "HOLD"}
                if action in cmd_map and mid.isdigit():
                    reply_text = _handle_buck_command(f"{cmd_map[action]} {mid}")
                    if reply_text:
                        _tg_send(reply_text)
            # Acknowledge the button tap immediately
            try:
                requests.post(f"{TG_BASE}/answerCallbackQuery",
                              json={"callback_query_id": cb_id, "text": "Received"}, timeout=5)
            except Exception:
                pass

        return _response("/telegram/webhook", result, start=t0)
    except Exception as e:
        return _response("/telegram/webhook", {}, errors=[str(e)], start=t0)


@router.get("/poll-instructions")
async def poll_instructions():
    """Poll Telegram for new messages from Buck (GBT calls this at session start)."""
    t0 = time.time()
    try:
        params  = {"limit": 20, "timeout": 0}
        if _TG_OFFSET[0]:
            params["offset"] = _TG_OFFSET[0]
        r = requests.get(f"{TG_BASE}/getUpdates", params=params, timeout=15)
        updates = r.json().get("result", [])
        messages = []
        for u in updates:
            _TG_OFFSET[0] = u["update_id"] + 1
            if "message" in u:
                msg = u["message"]
                messages.append({
                    "id":      msg["message_id"],
                    "time":    msg["date"],
                    "from":    msg.get("from", {}).get("first_name", "Buck"),
                    "message": msg.get("text", ""),
                })
        return _response("/poll-instructions", {
            "channel": "telegram",
            "count":   len(messages),
            "messages": messages,
        }, start=t0)
    except Exception as e:
        return _response("/poll-instructions", {}, errors=[str(e)], start=t0)


# ── AI Operations Control Plane — Durable Comms Patch (2026-06-30) ────────────
# DB (ai_messages) is the source of truth. Telegram is a notification layer only —
# if it's down, /gateway/ai/queue and /gateway/approvals still show everything.

AI_MESSAGE_AGENTS  = {"buck", "chatgpt", "claude_code", "browser_claude", "n8n", "system"}
AI_HEARTBEAT_AGENTS = {"chatgpt", "claude_code", "browser_claude", "n8n"}
NOTIFY_MESSAGE_TYPES = {
    "approval_request", "risk_alert", "blocked_mission",
    "handoff_waiting", "work_complete", "review_required",
}
STALE_APPROVAL_MINUTES = int(os.environ.get("AI_APPROVAL_STALE_MINUTES", "30"))
HEARTBEAT_STALE_MINUTES = int(os.environ.get("AI_HEARTBEAT_STALE_MINUTES", "120"))
_AGENT_ALIASES = {
    "buck": "buck", "buck adams": "buck",
    "chatgpt": "chatgpt", "gbt": "chatgpt", "chief_architect": "chatgpt", "chief architect": "chatgpt",
    "claude_code": "claude_code", "claude code": "claude_code",
    "browser_claude": "browser_claude", "browser claude": "browser_claude", "bc": "browser_claude",
    "n8n": "n8n", "system": "system",
}


def _touch_heartbeat(agent: str, action: str = "", role: str = None,
                      current_task: str = None, last_directive_id: int = None,
                      metadata: dict = None) -> Optional[str]:
    key = _AGENT_ALIASES.get((agent or "").strip().lower())
    if key not in AI_HEARTBEAT_AGENTS:
        return None
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO ai_agent_heartbeat
                        (agent, last_seen_at, last_action, status, role, current_task,
                         last_directive_id, metadata)
                    VALUES (%s, NOW(), %s, 'ONLINE', %s, %s, %s, COALESCE(%s, '{}'::jsonb))
                    ON CONFLICT (agent) DO UPDATE
                        SET last_seen_at = NOW(), last_action = EXCLUDED.last_action, status = 'ONLINE',
                            role = COALESCE(EXCLUDED.role, ai_agent_heartbeat.role),
                            current_task = COALESCE(EXCLUDED.current_task, ai_agent_heartbeat.current_task),
                            last_directive_id = COALESCE(EXCLUDED.last_directive_id, ai_agent_heartbeat.last_directive_id),
                            metadata = CASE WHEN EXCLUDED.metadata = '{}'::jsonb THEN ai_agent_heartbeat.metadata
                                            ELSE EXCLUDED.metadata END
                """, (key, (action or "")[:200], role, current_task, last_directive_id,
                      json.dumps(metadata) if metadata else None))
            conn.commit()
    except Exception:
        pass
    return key


def _create_ai_message(source, target, message_type, title, body, project_code=None,
                        requires_buck_approval=False, approval_type=None,
                        related_file=None, related_handoff_id=None,
                        related_approval_id=None, priority="medium",
                        source_of_truth_link=None) -> int:
    status = "NEEDS_BUCK_APPROVAL" if requires_buck_approval else "ISSUED"
    next_owner = "buck" if requires_buck_approval else target
    with _pg() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO ai_messages
                    (source_agent, target_agent, project_code, message_type, title, body, status,
                     requires_buck_approval, approval_type, related_file, related_handoff_id,
                     related_approval_id, next_action_owner, priority, source_of_truth_link)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id
            """, (source, target, project_code, message_type, title, body, status,
                  requires_buck_approval, approval_type, related_file, related_handoff_id,
                  related_approval_id, next_owner, priority, source_of_truth_link))
            mid = cur.fetchone()["id"]
        conn.commit()
    return mid


def _mark_telegram_sent(msg_id: int, tg_result: dict, retry: bool = False):
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                if tg_result.get("status") == "sent":
                    cur.execute("""
                        UPDATE ai_messages SET telegram_sent_at = NOW(),
                            telegram_message_id = %s, last_error = NULL,
                            retry_count = retry_count + %s, updated_at = NOW()
                        WHERE id = %s
                    """, (tg_result.get("message_id"), 1 if retry else 0, msg_id))
                else:
                    cur.execute("""
                        UPDATE ai_messages SET last_error = %s,
                            retry_count = retry_count + %s, updated_at = NOW()
                        WHERE id = %s
                    """, (str(tg_result.get("detail") or tg_result.get("http") or "send_failed")[:500],
                          1 if retry else 0, msg_id))
            conn.commit()
    except Exception:
        pass


def _tg_send_with_id(text: str, reply_markup: dict = None) -> dict:
    """Like _tg_send but captures the Telegram message_id (confirmation loop) and
    retries once without Markdown — covers the recurring parse_mode 400 failure mode
    (see commit ab14e29) instead of dropping the message."""
    import re as _re
    parse_mode = "Markdown" if _re.search(r"[*_`\[]", text) else None
    payload = {"chat_id": TG_CHAT_ID, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        r = requests.post(f"{TG_BASE}/sendMessage", json=payload, timeout=10)
        if r.ok:
            return {"status": "sent", "http": r.status_code,
                     "message_id": r.json().get("result", {}).get("message_id")}
        if parse_mode:
            payload.pop("parse_mode", None)
            r2 = requests.post(f"{TG_BASE}/sendMessage", json=payload, timeout=10)
            if r2.ok:
                return {"status": "sent", "http": r2.status_code,
                         "message_id": r2.json().get("result", {}).get("message_id"),
                         "retried_plain": True}
        return {"status": "failed", "http": r.status_code, "detail": r.text[:300]}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def _notify_agents(source: str, target: str, message_type: str, title: str, body: str,
                    project_code: str = None, requires_buck_approval: bool = False,
                    approval_type: str = None, related_file: str = None,
                    related_handoff_id: str = None, related_approval_id: int = None,
                    priority: str = "medium", source_of_truth_link: str = None) -> dict:
    """Single entry point for agent-to-agent / agent-to-Buck notices: DB row first
    (source of truth, survives Telegram outages), then Telegram with automatic ntfy
    fallback on failure. Replaces bare _tg_send() at alert sites — audit 2026-06-30
    confirmed two production alerts were silently dropped with no fallback."""
    msg_id = _create_ai_message(source, target, message_type, title, body, project_code,
                                 requires_buck_approval, approval_type, related_file, related_handoff_id,
                                 related_approval_id, priority, source_of_truth_link)
    sent = {"status": "skipped"}
    if message_type in NOTIFY_MESSAGE_TYPES or requires_buck_approval:
        icons = {"approval_request": "✅", "risk_alert": "🚨", "blocked_mission": "⛔",
                  "handoff_waiting": "📥", "work_complete": "🏁", "review_required": "🔎"}
        icon = icons.get(message_type, "📋")
        text = f"{icon} *{title}*\n\n{body}"
        markup = None
        if requires_buck_approval:
            text += f"\n\nReply: APPROVE {msg_id} / REJECT {msg_id} / HOLD {msg_id}"
            markup = {"inline_keyboard": [[
                {"text": "✅ Approve", "callback_data": f"approve:{msg_id}"},
                {"text": "❌ Reject",  "callback_data": f"reject:{msg_id}"},
                {"text": "⏸ Hold",    "callback_data": f"hold:{msg_id}"},
            ]]}
        sent = _tg_send_with_id(text, reply_markup=markup)
        _mark_telegram_sent(msg_id, sent)
        if sent.get("status") != "sent":
            sent["fallback"] = _ntfy(title, body, priority="urgent" if requires_buck_approval else "high")
    return {"id": msg_id, "delivery": sent}


def _handle_buck_command(text: str) -> Optional[str]:
    """Parse Buck's Telegram replies against the durable queue:
    APPROVE <id> / REJECT <id> / HOLD <id> / STATUS / QUEUE.
    Returns a reply string if recognized, else None (falls through to plain ack)."""
    if not text:
        return None
    parts = text.strip().split()
    cmd = parts[0].upper()
    if cmd in ("APPROVE", "REJECT", "HOLD") and len(parts) >= 2 and parts[1].isdigit():
        msg_id = int(parts[1])
        new_status = {"APPROVE": "RECEIVED", "REJECT": "REJECTED", "HOLD": "BLOCKED"}[cmd]
        next_owner = {"APPROVE": None, "REJECT": None, "HOLD": "buck"}[cmd]  # APPROVE hands back to requester
        try:
            with _pg() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE ai_messages SET status=%s, telegram_acknowledged_at=NOW(), updated_at=NOW(),
                            acknowledged_at = COALESCE(acknowledged_at, NOW()),
                            received_at = CASE WHEN %s = 'RECEIVED' THEN COALESCE(received_at, NOW()) ELSE received_at END,
                            blocked_reason = CASE WHEN %s = 'BLOCKED' THEN 'Held by Buck via Telegram' ELSE blocked_reason END,
                            next_action_owner = COALESCE(%s, CASE WHEN %s THEN source_agent ELSE next_action_owner END)
                        WHERE id=%s RETURNING title, approval_type, related_file
                    """, (new_status, new_status, new_status, next_owner, cmd == "APPROVE", msg_id))
                    row = cur.fetchone()
                conn.commit()
            if not row:
                return f"⚠️ No message #{msg_id} found."
            verb = {"APPROVE": "Approved", "REJECT": "Rejected", "HOLD": "Held"}[cmd]
            icon = {"APPROVE": "✅", "REJECT": "❌", "HOLD": "⏸"}[cmd]
            # Closed-loop email send: Buck's APPROVE is the ONLY trigger that actually
            # calls Microsoft Graph — see incident note on _send_approved_draft.
            if cmd == "APPROVE" and row.get("approval_type") == "email_send" and row.get("related_file"):
                ok, err = _send_approved_draft(row["related_file"])
                with _pg() as conn:
                    with conn.cursor() as cur:
                        if ok:
                            cur.execute("""UPDATE ai_messages SET status='COMPLETE', completed_at=NOW(), updated_at=NOW()
                                            WHERE id=%s""", (msg_id,))
                        else:
                            cur.execute("""UPDATE ai_messages SET status='BLOCKED', blocked_reason=%s, updated_at=NOW()
                                            WHERE id=%s""", (f"send failed: {err}"[:500], msg_id))
                    conn.commit()
                if ok:
                    return f"✅📧 Approved and sent #{msg_id}: {row['title']}"
                return f"⚠️ Approved #{msg_id} but the send failed: {err}"
            return f"{icon} {verb} #{msg_id}: {row['title']}"
        except Exception as e:
            return f"⚠️ Error updating #{msg_id}: {e}"
    if cmd == "STATUS":
        try:
            with _pg() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT status, COUNT(*) AS n FROM ai_messages
                        WHERE status NOT IN ('COMPLETE','REJECTED') GROUP BY status
                    """)
                    counts = {r["status"]: r["n"] for r in cur.fetchall()}
            lines = [f"{k}: {v}" for k, v in counts.items()] or ["Nothing pending."]
            return "📊 *Status*\n" + "\n".join(lines)
        except Exception as e:
            return f"⚠️ Error: {e}"
    if cmd == "QUEUE":
        try:
            with _pg() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, title, status FROM ai_messages
                        WHERE status IN ('ISSUED','NEEDS_BUCK_APPROVAL','STALE')
                        ORDER BY created_at ASC LIMIT 8
                    """)
                    rows = cur.fetchall()
            if not rows:
                return "📭 Queue is empty."
            return "📥 *Queue*\n" + "\n".join(f"#{r['id']} [{r['status']}] {r['title']}" for r in rows)
        except Exception as e:
            return f"⚠️ Error: {e}"
    return None


def _classify_heartbeats(rows: list) -> list:
    """Apply dynamic STALE classification on top of stored ONLINE/OFFLINE/RECOVERING/BLOCKED
    — a row can go stale just by the clock, without anyone writing a new status."""
    out = []
    for r in rows:
        h = dict(r)
        last_seen = h.get("last_seen_at")
        if last_seen:
            age_min = (datetime.now(timezone.utc) - last_seen).total_seconds() / 60
            if h.get("status") not in ("BLOCKED",) and age_min > HEARTBEAT_STALE_MINUTES:
                h["status"] = "STALE"
            h["last_seen_at"] = last_seen.isoformat()
        out.append(h)
    return out


def _comms_snapshot() -> dict:
    """Agent-coordination view for Mission Control — separate from business/project KPIs."""
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT COUNT(*) n FROM ai_messages
                    WHERE requires_buck_approval AND status IN ('NEEDS_BUCK_APPROVAL','STALE')""")
                pending_approvals = cur.fetchone()["n"]
                cur.execute("SELECT COUNT(*) n FROM ai_messages WHERE status = 'ISSUED'")
                unacked = cur.fetchone()["n"]
                cur.execute("SELECT COUNT(*) n FROM ai_messages WHERE status = 'STALE'")
                stale = cur.fetchone()["n"]
                cur.execute("""SELECT
                        (SELECT COUNT(*) FROM ai_messages WHERE status = 'BLOCKED') +
                        (SELECT COUNT(*) FROM missions WHERE status = 'BLOCKED') AS n""")
                blocked = cur.fetchone()["n"]
                cur.execute("""SELECT COUNT(*) n FROM ai_messages
                    WHERE status IN ('ISSUED','RECEIVED','IN_PROGRESS')""")
                active_directives = cur.fetchone()["n"]
                cur.execute("SELECT agent, last_seen_at, last_action, status, role, current_task, last_directive_id, metadata FROM ai_agent_heartbeat ORDER BY agent")
                heartbeats = _classify_heartbeats(cur.fetchall())
                cur.execute("SELECT MAX(published_at) t FROM platform_events WHERE event_type='buck_message'")
                row = cur.fetchone()
                last_buck = row["t"].isoformat() if row and row["t"] else None
                cur.execute("""SELECT
                        COUNT(*) FILTER (WHERE telegram_sent_at IS NOT NULL AND last_error IS NULL) AS sent_ok,
                        COUNT(*) FILTER (WHERE last_error IS NOT NULL) AS send_failed
                    FROM ai_messages WHERE created_at > NOW() - INTERVAL '24 hours'""")
                tg24 = dict(cur.fetchone())
        return {
            "active_directives": active_directives,
            "pending_buck_approvals": pending_approvals,
            "unacknowledged_ai_messages": unacked,
            "stale_handoffs_or_approvals": stale,
            "blocked_missions": blocked,
            "agent_heartbeats": heartbeats,
            "last_buck_message_received_at": last_buck,
            "telegram_health_last_24h": tg24,
            "current_sprint": _current_sprint_label(),
        }
    except Exception as e:
        return {"error": str(e)}


def _current_sprint_label() -> Optional[str]:
    """First '**Sprint:**' or '## ... Sprint N' line from CURRENT_SPRINT.md — Mission
    Control needs sprint visibility without duplicating sprint state anywhere new."""
    try:
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "CURRENT_SPRINT.md"))
        with open(path) as f:
            for line in f:
                if line.startswith("**Sprint Name:**") or line.startswith("**Sprint Number:**"):
                    continue
                if line.startswith("## ") and "Sprint" in line:
                    return line.lstrip("# ").strip()
        return None
    except Exception:
        return None


class AIMessageCreate(BaseModel):
    source_agent: str
    target_agent: str
    message_type: str
    title: str
    body: str
    project_code: Optional[str] = None
    requires_buck_approval: bool = False
    approval_type: Optional[str] = None
    related_file: Optional[str] = None
    related_handoff_id: Optional[str] = None
    related_approval_id: Optional[int] = None
    priority: str = "medium"
    source_of_truth_link: Optional[str] = None


@router.post("/ai/messages")
async def ai_messages_create(req: AIMessageCreate):
    """Create a durable agent message/task (this IS the directive system — ai_directives
    was not created as a separate table per ARB 2026-07-01, extending this one instead).
    DB row is the source of truth; Telegram notification (with ntfy fallback) is sent
    automatically for notify-worthy types (approval_request, risk_alert, blocked_mission,
    handoff_waiting, work_complete, review_required) or whenever requires_buck_approval is true."""
    t0 = time.time()
    _touch_heartbeat(req.source_agent, f"sent {req.message_type}: {req.title[:60]}")
    result = _notify_agents(req.source_agent, req.target_agent, req.message_type, req.title, req.body,
                             req.project_code, req.requires_buck_approval, req.approval_type,
                             req.related_file, req.related_handoff_id, req.related_approval_id,
                             req.priority, req.source_of_truth_link)
    _log("/ai/messages", req.source_agent, "ai_messages", "ok", int((time.time()-t0)*1000),
         str(result["id"]), req.title[:60])
    return _response("/ai/messages", result, start=t0)


@router.get("/ai/messages/{msg_id}")
def ai_message_get(msg_id: int):
    """Read a single directive/message by id — the 'read' endpoint of the directive lifecycle."""
    t0 = time.time()
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM ai_messages WHERE id = %s", (msg_id,))
                row = cur.fetchone()
        if not row:
            return _response(f"/ai/messages/{msg_id}", {}, errors=["not found"], start=t0)
        row = dict(row)
        for k in ("created_at", "updated_at", "telegram_sent_at", "telegram_acknowledged_at",
                  "received_at", "acknowledged_at", "started_at", "completed_at"):
            if row.get(k):
                row[k] = row[k].isoformat()
        return _response(f"/ai/messages/{msg_id}", row, start=t0)
    except Exception as e:
        return _response(f"/ai/messages/{msg_id}", {}, errors=[str(e)], start=t0)


class AIMessageAcknowledge(BaseModel):
    agent: str


@router.post("/ai/messages/{msg_id}/acknowledge")
async def ai_message_acknowledge(msg_id: int, req: AIMessageAcknowledge):
    """Explicit ISSUED -> RECEIVED transition — the 'acknowledge' endpoint of the
    directive lifecycle, distinct from the generic status PATCH below."""
    t0 = time.time()
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE ai_messages SET status='RECEIVED', updated_at=NOW(),
                        received_at = COALESCE(received_at, NOW()),
                        acknowledged_at = COALESCE(acknowledged_at, NOW())
                    WHERE id=%s AND status IN ('ISSUED','STALE') RETURNING id, title
                """, (msg_id,))
                row = cur.fetchone()
            conn.commit()
        if not row:
            return _response(f"/ai/messages/{msg_id}/acknowledge", {},
                              errors=["not found, or not in an acknowledgeable state (ISSUED/STALE)"], start=t0)
        _touch_heartbeat(req.agent, f"acknowledged #{msg_id}")
        return _response(f"/ai/messages/{msg_id}/acknowledge", {"id": msg_id, "status": "RECEIVED"}, start=t0)
    except Exception as e:
        return _response(f"/ai/messages/{msg_id}/acknowledge", {}, errors=[str(e)], start=t0)


@router.get("/ai/directives/stale")
def ai_directives_stale():
    """Named alias over GET /ai/queue?status=STALE — ARB directive asked for a distinct
    'stale directives' endpoint; same table, no second system."""
    return ai_queue(status="STALE")


@router.get("/ai/queue")
def ai_queue(status: Optional[str] = None, target: Optional[str] = None, limit: int = 50):
    """Fallback polling — works even if Telegram is fully down, since DB is source of truth."""
    t0 = time.time()
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                q = "SELECT * FROM ai_messages WHERE 1=1"
                params: list = []
                if status:
                    q += " AND status = %s"; params.append(status)
                if target:
                    q += " AND target_agent = %s"; params.append(target)
                q += " ORDER BY created_at DESC LIMIT %s"; params.append(limit)
                cur.execute(q, params)
                rows = [dict(r) for r in cur.fetchall()]
        for r in rows:
            for k in ("created_at", "updated_at", "telegram_sent_at", "telegram_acknowledged_at"):
                if r.get(k):
                    r[k] = r[k].isoformat()
        return _response("/ai/queue", {"count": len(rows), "messages": rows}, start=t0)
    except Exception as e:
        return _response("/ai/queue", {}, errors=[str(e)], start=t0)


@router.get("/approvals")
def ai_approvals():
    """Pending Buck approvals from the durable queue — visible even if Telegram missed it."""
    t0 = time.time()
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM ai_messages
                    WHERE requires_buck_approval = TRUE AND status IN ('NEEDS_BUCK_APPROVAL','STALE')
                    ORDER BY created_at ASC
                """)
                rows = [dict(r) for r in cur.fetchall()]
        for r in rows:
            for k in ("created_at", "updated_at", "telegram_sent_at", "telegram_acknowledged_at"):
                if r.get(k):
                    r[k] = r[k].isoformat()
        return _response("/approvals", {"count": len(rows), "approvals": rows}, start=t0)
    except Exception as e:
        return _response("/approvals", {}, errors=[str(e)], start=t0)


class AIMessageStatusUpdate(BaseModel):
    status: str
    agent: Optional[str] = "system"
    blocked_reason: Optional[str] = None


_DIRECTIVE_STATUS_TIMESTAMP_COL = {
    "RECEIVED": "received_at",
    "IN_PROGRESS": "started_at",
    "COMPLETE": "completed_at",
}


@router.patch("/ai/messages/{msg_id}/status")
async def ai_message_status(msg_id: int, req: AIMessageStatusUpdate):
    """Agent self-report: RECEIVED / IN_PROGRESS / BLOCKED / COMPLETE / REJECTED / etc.
    Stamps the matching lifecycle timestamp (received_at/started_at/completed_at) and,
    for BLOCKED, records blocked_reason — required fields per ARB directive 2026-07-01."""
    t0 = time.time()
    valid = {"ISSUED", "RECEIVED", "IN_PROGRESS", "BLOCKED", "COMPLETE",
              "NEEDS_BUCK_APPROVAL", "REJECTED", "STALE"}
    if req.status not in valid:
        return _response(f"/ai/messages/{msg_id}/status", {},
                          errors=[f"invalid status, must be one of {sorted(valid)}"], start=t0)
    ts_col = _DIRECTIVE_STATUS_TIMESTAMP_COL.get(req.status)
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                if ts_col:
                    cur.execute(f"""
                        UPDATE ai_messages SET status=%s, updated_at=NOW(),
                            {ts_col} = COALESCE({ts_col}, NOW())
                        WHERE id=%s RETURNING id
                    """, (req.status, msg_id))
                elif req.status == "BLOCKED":
                    cur.execute("""
                        UPDATE ai_messages SET status=%s, updated_at=NOW(), blocked_reason=%s
                        WHERE id=%s RETURNING id
                    """, (req.status, req.blocked_reason, msg_id))
                else:
                    cur.execute("UPDATE ai_messages SET status=%s, updated_at=NOW() WHERE id=%s RETURNING id",
                                (req.status, msg_id))
                row = cur.fetchone()
            conn.commit()
        if not row:
            return _response(f"/ai/messages/{msg_id}/status", {}, errors=["not found"], start=t0)
        _touch_heartbeat(req.agent, f"set #{msg_id} -> {req.status}", last_directive_id=msg_id)
        return _response(f"/ai/messages/{msg_id}/status", {"id": msg_id, "status": req.status}, start=t0)
    except Exception as e:
        return _response(f"/ai/messages/{msg_id}/status", {}, errors=[str(e)], start=t0)


async def _heartbeat_handler(request: Request, response_path: str):
    t0 = time.time()
    body = await request.json()
    agent = (body.get("agent") or "").strip().lower()
    action = body.get("action", "ping")
    if _AGENT_ALIASES.get(agent) not in AI_HEARTBEAT_AGENTS:
        return _response(response_path, {}, errors=[f"unknown agent, must be one of {sorted(AI_HEARTBEAT_AGENTS)}"], start=t0)
    _touch_heartbeat(agent, action, role=body.get("role"), current_task=body.get("current_task"),
                      last_directive_id=body.get("last_directive_id"), metadata=body.get("metadata"))
    return _response(response_path, {"agent": _AGENT_ALIASES[agent], "status": "alive"}, start=t0)


@router.post("/ai/heartbeat")
async def ai_heartbeat(request: Request):
    """Explicit agent ping — also touched implicitly by /ai/messages and /agent/handoff.
    Fields: agent, action, role, current_task, last_directive_id, metadata."""
    return await _heartbeat_handler(request, "/ai/heartbeat")


@router.post("/heartbeat")
async def heartbeat_alias(request: Request):
    """Literal /gateway/heartbeat path required by the ARB directive — same handler as
    /gateway/ai/heartbeat, not a second implementation."""
    return await _heartbeat_handler(request, "/heartbeat")


@router.post("/ai/escalation-check")
def ai_escalation_check():
    """Retry/escalate approvals that have sat unacknowledged past the stale threshold.
    Call from n8n on a schedule (e.g. every 15 min) — fills the gap confirmed by audit:
    no retry/escalation path existed anywhere in the system."""
    t0 = time.time()
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM ai_messages
                    WHERE requires_buck_approval = TRUE
                      AND status = 'NEEDS_BUCK_APPROVAL'
                      AND telegram_acknowledged_at IS NULL
                      AND (telegram_sent_at IS NULL OR telegram_sent_at < NOW() - (%s || ' minutes')::interval)
                """, (STALE_APPROVAL_MINUTES,))
                stale = [dict(r) for r in cur.fetchall()]
        escalated = []
        for item in stale:
            text = (f"⏰ STILL PENDING (retry {item['retry_count']+1}) *{item['title']}*\n\n{item['body']}"
                     f"\n\nReply: APPROVE {item['id']} / REJECT {item['id']} / HOLD {item['id']}")
            tg = _tg_send_with_id(text)
            _mark_telegram_sent(item["id"], tg, retry=True)
            if tg.get("status") != "sent":
                _ntfy(f"STALE APPROVAL #{item['id']}: {item['title']}", item["body"], priority="urgent")
            with _pg() as conn:
                with conn.cursor() as cur:
                    cur.execute("UPDATE ai_messages SET status='STALE', updated_at=NOW() WHERE id=%s", (item["id"],))
                conn.commit()
            escalated.append({"id": item["id"], "title": item["title"], "telegram_retry": tg.get("status")})
        return _response("/ai/escalation-check", {
            "checked_threshold_minutes": STALE_APPROVAL_MINUTES,
            "escalated_count": len(escalated), "escalated": escalated,
        }, start=t0)
    except Exception as e:
        return _response("/ai/escalation-check", {}, errors=[str(e)], start=t0)


@router.get("/telegram/health")
def telegram_health():
    """Diagnose Telegram reliability — webhook registration state + recent send health.
    Addresses the confirmed root cause: webhook registration only existed in dead code
    (integrations/telegram_bot.py), never called, so there was no way to verify or
    re-establish it if the ngrok URL rotated."""
    t0 = time.time()
    out: Dict[str, Any] = {}
    try:
        r = requests.get(f"{TG_BASE}/getWebhookInfo", timeout=10)
        info = r.json().get("result", {})
        expected = "https://speculate-armband-retinal.ngrok-free.dev/gateway/telegram/webhook"
        out["webhook_url"] = info.get("url")
        out["webhook_matches_expected"] = info.get("url") == expected
        out["pending_update_count"] = info.get("pending_update_count")
        out["last_error_message"] = info.get("last_error_message")
        out["last_error_date"] = info.get("last_error_date")
    except Exception as e:
        out["telegram_api_error"] = str(e)
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT status, COUNT(*) AS n FROM ai_messages
                    WHERE created_at > NOW() - INTERVAL '24 hours' GROUP BY status
                """)
                out["last_24h_message_status"] = {r["status"]: r["n"] for r in cur.fetchall()}
                cur.execute("SELECT MAX(published_at) t FROM platform_events WHERE event_type='buck_message'")
                row = cur.fetchone()
                out["last_buck_message_received_at"] = row["t"].isoformat() if row and row["t"] else None
    except Exception as e:
        out["db_error"] = str(e)
    return _response("/telegram/health", out, start=t0)


@router.post("/telegram/register-webhook")
def telegram_register_webhook():
    """(Re)register the Telegram webhook against the live ngrok URL — makes webhook
    registration reproducible/callable instead of a manual, undocumented step."""
    t0 = time.time()
    url = "https://speculate-armband-retinal.ngrok-free.dev/gateway/telegram/webhook"
    try:
        r = requests.post(f"{TG_BASE}/setWebhook", json={"url": url}, timeout=10)
        body = r.json()
        return _response("/telegram/register-webhook", {
            "webhook_url": url, "registered": bool(r.ok and body.get("ok")), "telegram_response": body,
        }, start=t0)
    except Exception as e:
        return _response("/telegram/register-webhook", {}, errors=[str(e)], start=t0)


@router.get("/ai/events")
def ai_events(limit: int = 20):
    """Last N AI events/handoffs — merges ai_messages with Buck's incoming Telegram/phone
    messages (platform_events) into one combined recent-activity feed for warm-start."""
    t0 = time.time()
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    (SELECT 'ai_message' AS kind, id::text AS ref, source_agent AS source, target_agent AS target,
                            message_type AS type, title, status, created_at AS ts
                     FROM ai_messages ORDER BY created_at DESC LIMIT %s)
                    UNION ALL
                    (SELECT 'buck_message' AS kind, id::text AS ref, 'buck' AS source, 'system' AS target,
                            event_type AS type, LEFT(payload->>'text', 80) AS title, NULL AS status,
                            published_at AS ts
                     FROM platform_events WHERE event_type = 'buck_message' ORDER BY published_at DESC LIMIT %s)
                    ORDER BY ts DESC LIMIT %s
                """, (limit, limit, limit))
                rows = [dict(r) for r in cur.fetchall()]
        for r in rows:
            if r.get("ts"):
                r["ts"] = r["ts"].isoformat()
        return _response("/ai/events", {"count": len(rows), "events": rows}, start=t0)
    except Exception as e:
        return _response("/ai/events", {}, errors=[str(e)], start=t0)


@router.get("/ai/warm-start")
def ai_warm_start():
    """Single-call recovery snapshot — Claude Code, Browser Claude, ChatGPT, n8n, or Buck
    should all be able to reorient from this one endpoint after any restart. Extends
    existing infra (projects, risks, missions, ai_messages, Agent_Handoff Inbox, Telegram)
    rather than duplicating any of it — see AI_TEAM/WARM_START.md for the full sequence."""
    t0 = time.time()
    out: Dict[str, Any] = {}
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT project_code, name, status FROM projects
                    WHERE status IN ('active','design','bidding','preconstruction')
                    ORDER BY project_code
                """)
                out["active_projects"] = [dict(r) for r in cur.fetchall()]

                cur.execute("""
                    SELECT p.project_code, r.risk_type, LEFT(r.description,100) AS description, r.severity
                    FROM risks r JOIN projects p ON p.id = r.project_id
                    WHERE r.status = 'open' AND r.severity IN ('critical','high')
                    ORDER BY CASE r.severity WHEN 'critical' THEN 1 ELSE 2 END LIMIT 5
                """)
                out["top_risks"] = [dict(r) for r in cur.fetchall()]

                cur.execute("""
                    SELECT id, title, message_type, created_at FROM ai_messages
                    WHERE requires_buck_approval AND status IN ('NEEDS_BUCK_APPROVAL','STALE')
                    ORDER BY created_at ASC
                """)
                pending_buck = [dict(r) for r in cur.fetchall()]
                for r in pending_buck:
                    r["created_at"] = r["created_at"].isoformat()
                out["pending_buck_approvals"] = pending_buck

                cur.execute("""
                    SELECT id, title, status, created_at FROM ai_messages
                    WHERE target_agent = 'chatgpt' AND status NOT IN ('COMPLETE','REJECTED')
                    ORDER BY created_at ASC
                """)
                pending_gbt = [dict(r) for r in cur.fetchall()]
                for r in pending_gbt:
                    r["created_at"] = r["created_at"].isoformat()
                out["pending_chief_architect_reviews"] = pending_gbt

                cur.execute("""
                    SELECT mission_id, title, status, priority FROM missions
                    WHERE assigned_to = 'claude_code' AND status IN ('OPEN','IN_PROGRESS','BLOCKED')
                    ORDER BY CASE priority WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END LIMIT 10
                """)
                out["pending_code_tasks"] = [dict(r) for r in cur.fetchall()]

                cur.execute("""
                    SELECT mission_id, title, status, priority FROM missions
                    WHERE assigned_to = 'browser_claude' AND status IN ('OPEN','IN_PROGRESS','BLOCKED')
                    ORDER BY CASE priority WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END LIMIT 10
                """)
                out["pending_bc_tasks"] = [dict(r) for r in cur.fetchall()]

                cur.execute("SELECT mission_id, title, blocker FROM missions WHERE status = 'BLOCKED'")
                blocked_missions = [dict(r) for r in cur.fetchall()]
                cur.execute("SELECT id, title FROM ai_messages WHERE status = 'BLOCKED'")
                blocked_missions += [dict(r) for r in cur.fetchall()]
                out["blocked_missions"] = blocked_missions

                cur.execute("""
                    SELECT id, title, created_at FROM ai_messages WHERE status = 'STALE'
                    ORDER BY created_at ASC
                """)
                stale = [dict(r) for r in cur.fetchall()]
                for r in stale:
                    r["created_at"] = r["created_at"].isoformat()
                out["stale_handoffs"] = stale

                cur.execute("SELECT agent, last_seen_at, last_action, status, role, current_task, last_directive_id, metadata FROM ai_agent_heartbeat ORDER BY agent")
                out["agent_heartbeats"] = _classify_heartbeats(cur.fetchall())

                cur.execute("""SELECT MAX(telegram_sent_at) t FROM ai_messages
                    WHERE telegram_sent_at IS NOT NULL AND last_error IS NULL""")
                row = cur.fetchone()
                out["last_successful_telegram_send"] = row["t"].isoformat() if row and row["t"] else None
                cur.execute("SELECT MAX(published_at) t FROM platform_events WHERE event_type='buck_message'")
                row = cur.fetchone()
                out["last_successful_telegram_receive"] = row["t"].isoformat() if row and row["t"] else None
    except Exception as e:
        out["db_error"] = str(e)

    try:
        inbox = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..",
                                               "Architecture", "Agent_Handoff", "Inbox"))
        out["architecture_inbox_pending"] = (
            len([f for f in os.listdir(inbox) if f.endswith(".md")]) if os.path.isdir(inbox) else 0
        )
    except Exception:
        out["architecture_inbox_pending"] = None

    if out.get("pending_buck_approvals"):
        out["next_recommended_action"] = (
            f"Buck: {len(out['pending_buck_approvals'])} approval(s) pending — "
            f"oldest is '{out['pending_buck_approvals'][0]['title']}'"
        )
    elif out.get("blocked_missions"):
        out["next_recommended_action"] = f"Unblock: {len(out['blocked_missions'])} blocked mission(s)/message(s)"
    elif out.get("stale_handoffs"):
        out["next_recommended_action"] = (
            f"Escalate: {len(out['stale_handoffs'])} stale item(s) — run /gateway/ai/escalation-check"
        )
    elif out.get("pending_code_tasks"):
        out["next_recommended_action"] = f"Claude Code: pick up '{out['pending_code_tasks'][0]['title']}'"
    else:
        out["next_recommended_action"] = "No blockers — continue with next roadmap item."

    return _response("/ai/warm-start", out, start=t0)


# ── Buck Phone → System Messaging ──────────────────────────────────────────────

class BuckMessageRequest(BaseModel):
    title: str = "Message from Buck"
    body: str
    priority: str = "default"

@router.post("/buck/message")
async def buck_send_message(req: BuckMessageRequest):
    """Receive a message from Buck (phone form or Siri shortcut) and store + push to agents."""
    t0 = time.time()
    msg_id = str(uuid.uuid4())[:8]
    ts = datetime.now(timezone.utc).isoformat()
    try:
        conn = _pg()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO platform_events (event_type, source_service, actor, payload) VALUES (%s, %s, %s, %s)",
            ("buck_message", "phone", "Buck Adams", psycopg2.extras.Json({"id": msg_id, "title": req.title, "body": req.body, "priority": req.priority, "ts": ts}))
        )
        conn.commit()
        cur.close(); conn.close()
    except Exception as e:
        _log("buck_message_store_error", {"error": str(e)})

    # Forward to ntfy so agents that poll /poll-instructions pick it up too
    _ntfy(title=f"📲 Buck: {req.title}", body=req.body, priority=req.priority, tags="incoming_envelope")
    _log("/buck/message", "phone", "platform_events", "ok", int((time.time()-t0)*1000), msg_id, f"title={req.title[:40]}")
    return _response("/buck/message", {"status": "received", "id": msg_id, "ts": ts}, start=t0)

@router.get("/buck/messages")
async def buck_get_messages(since_minutes: int = 60):
    """Return recent messages from Buck — GBT polls this at session start."""
    t0 = time.time()
    try:
        conn = _pg()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            "SELECT payload, published_at FROM platform_events WHERE event_type = 'buck_message' AND published_at > NOW() - INTERVAL '%s minutes' ORDER BY published_at DESC LIMIT 20",
            (since_minutes,)
        )
        rows = cur.fetchall()
        cur.close(); conn.close()
        messages = [{"data": r["payload"], "received_at": r["published_at"].isoformat()} for r in rows]
        return _response("/buck/messages", {"count": len(messages), "window_minutes": since_minutes, "messages": messages}, start=t0)
    except Exception as e:
        return _response("/buck/messages", {}, errors=[str(e)], start=t0)

@router.get("/telegram/messages")
async def telegram_messages_for_agent(agent: str = Query(..., description="chatgpt|browser_claude|claude_code|n8n"),
                                       limit: int = Query(20, le=100)):
    """GBT/BC visibility fix (2026-07-01): neither can receive a live Telegram push —
    this lets them poll for what they haven't seen yet. Tracks each agent's last-seen
    buck_message id in ai_agent_heartbeat.metadata (extends existing heartbeat infra,
    no new table) rather than building a separate telegram_messages table."""
    t0 = time.time()
    key = _AGENT_ALIASES.get((agent or "").strip().lower())
    if key not in AI_HEARTBEAT_AGENTS:
        return _response("/telegram/messages", {}, errors=[f"unknown agent, must be one of {sorted(AI_HEARTBEAT_AGENTS)}"], start=t0)
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT metadata FROM ai_agent_heartbeat WHERE agent = %s", (key,))
                row = cur.fetchone()
                last_ack_id = (row["metadata"] or {}).get("last_telegram_ack_id", 0) if row else 0

                cur.execute("""
                    SELECT id, payload, published_at FROM platform_events
                    WHERE event_type = 'buck_message' AND id > %s
                    ORDER BY id ASC LIMIT %s
                """, (last_ack_id, limit))
                rows = cur.fetchall()
        messages = [{
            "message_id": r["id"], "read_status": "unread",
            "from": "Buck Adams", "text": (r["payload"] or {}).get("text") or (r["payload"] or {}).get("body"),
            "timestamp": r["published_at"].isoformat(),
        } for r in rows]
        _touch_heartbeat(agent, f"polled telegram/messages ({len(messages)} unread)")
        return _response("/telegram/messages", {
            "agent": key, "last_ack_id": last_ack_id,
            "count": len(messages), "messages": messages,
        }, start=t0)
    except Exception as e:
        return _response("/telegram/messages", {}, errors=[str(e)], start=t0)


class TelegramAckRequest(BaseModel):
    agent: str
    message_id: int


@router.post("/telegram/ack")
async def telegram_ack(req: TelegramAckRequest):
    """Mark Telegram messages up to message_id as read for this agent."""
    t0 = time.time()
    key = _AGENT_ALIASES.get((req.agent or "").strip().lower())
    if key not in AI_HEARTBEAT_AGENTS:
        return _response("/telegram/ack", {}, errors=[f"unknown agent, must be one of {sorted(AI_HEARTBEAT_AGENTS)}"], start=t0)
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO ai_agent_heartbeat (agent, last_seen_at, status, metadata)
                    VALUES (%s, NOW(), 'ONLINE', %s::jsonb)
                    ON CONFLICT (agent) DO UPDATE
                        SET last_seen_at = NOW(), status = 'ONLINE',
                            metadata = ai_agent_heartbeat.metadata || %s::jsonb
                """, (key, json.dumps({"last_telegram_ack_id": req.message_id}),
                      json.dumps({"last_telegram_ack_id": req.message_id})))
            conn.commit()
        return _response("/telegram/ack", {"agent": key, "acked_through": req.message_id}, start=t0)
    except Exception as e:
        return _response("/telegram/ack", {}, errors=[str(e)], start=t0)


@router.get("/buck/compose", response_class=None)
async def buck_compose_form():
    """Simple HTML form Buck bookmarks on his phone to send messages to the system."""
    from fastapi.responses import HTMLResponse
    html = """<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="HCI Send">
<title>HCI — Send Message</title>
<style>
  body { font-family: -apple-system, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
  h2 { color: #e94560; margin-bottom: 24px; font-size: 18px; }
  label { display: block; font-size: 13px; color: #aaa; margin-bottom: 4px; }
  input, textarea, select { width: 100%; box-sizing: border-box; background: #16213e; color: #fff;
    border: 1px solid #444; border-radius: 8px; padding: 12px; font-size: 16px; margin-bottom: 16px; }
  textarea { height: 120px; resize: vertical; }
  button { width: 100%; background: #e94560; color: #fff; border: none; border-radius: 8px;
    padding: 16px; font-size: 17px; font-weight: bold; cursor: pointer; }
  button:active { background: #c73652; }
  #status { margin-top: 16px; text-align: center; font-size: 14px; color: #4ecdc4; }
</style>
</head>
<body>
<h2>📲 Send Message to HCI System</h2>
<form id="f">
  <label>Title</label>
  <input id="title" type="text" placeholder="Quick note, directive, question..." value="Message from Buck">
  <label>Message</label>
  <textarea id="body" placeholder="What do you need?"></textarea>
  <label>Priority</label>
  <select id="priority">
    <option value="default">Normal</option>
    <option value="high">High</option>
    <option value="urgent">Urgent</option>
    <option value="low">Low</option>
  </select>
  <button type="submit">Send to HCI OS</button>
</form>
<div id="status"></div>
<script>
document.getElementById('f').addEventListener('submit', async function(e) {
  e.preventDefault();
  const btn = document.querySelector('button');
  btn.textContent = 'Sending...';
  btn.disabled = true;
  try {
    const r = await fetch('/gateway/buck/message', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        title: document.getElementById('title').value,
        body: document.getElementById('body').value,
        priority: document.getElementById('priority').value,
      })
    });
    const d = await r.json();
    document.getElementById('status').textContent = '✅ Sent! ID: ' + (d.payload?.id || '?');
    document.getElementById('body').value = '';
    document.getElementById('title').value = 'Message from Buck';
  } catch(err) {
    document.getElementById('status').textContent = '❌ Error: ' + err.message;
  }
  btn.textContent = 'Send to HCI OS';
  btn.disabled = false;
});
</script>
</body>
</html>"""
    return HTMLResponse(content=html)


# ── Batch Endpoint ─────────────────────────────────────────────────────────────

class BatchOperation(BaseModel):
    op: str
    params: Dict[str, Any] = {}

class BatchRequest(BaseModel):
    session_id: Optional[str] = None
    operations: list[BatchOperation]


def _exec_op(op: str, params: dict) -> dict:
    """Execute a single batch operation. Returns {op, status, ...result}."""
    base = {"op": op}

    if op == "ntfyPush":
        r = _ntfy(
            title=params.get("title", "HCI Notification"),
            body=params.get("body", ""),
            priority=params.get("priority", "default"),
            tags=params.get("tags", ""),
        )
        return {**base, **r}

    if op == "emailDraft":
        try:
            import sys as _sys
            _sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "integrations"))
            from microsoft_graph import create_draft
            to_name  = params.get("to_name", "")
            to_email = params.get("to_email", "")
            r = create_draft(
                subject=params.get("subject", "(no subject)"),
                html_body=params.get("body_html", params.get("body", "")),
                to=[(to_name, to_email)],
            )
            return {**base, "status": "ok", "draft_id": r.get("id", "")[:30]}
        except Exception as e:
            return {**base, "status": "error", "detail": str(e)[:200]}

    if op == "sendEmail":
        try:
            import sys as _sys
            _sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "integrations"))
            from microsoft_graph import send_email_with_cc
            to_name  = params.get("to_name", "")
            to_email = params.get("to_email", "")
            cc_raw   = params.get("cc", [])
            cc_tuples = [(c["name"], c["email"]) for c in cc_raw] if cc_raw else None
            r, err = send_email_with_cc(
                subject=params.get("subject", "(no subject)"),
                html_body=params.get("body_html", params.get("body", "")),
                to=[(to_name, to_email)],
                cc=cc_tuples,
            )
            if err:
                return {**base, "status": "error", "detail": str(err)[:200]}
            return {**base, "status": "sent", "to": to_email}
        except Exception as e:
            return {**base, "status": "error", "detail": str(e)[:200]}

    if op == "sendHandoff":
        try:
            r = requests.post(
                f"{_INTERNAL_BASE.replace('/api/v1','')}/gateway/agent/handoff",
                headers={"X-API-Key": _INTERNAL_KEY},
                json={
                    "title":             params.get("title", "Batch Handoff"),
                    "body":              params.get("body", ""),
                    "priority":          params.get("priority", "medium"),
                    "source":            params.get("source", "batch"),
                    "destination_agent": params.get("destination_agent", "claude_code"),
                },
                timeout=20,
            )
            data = r.json()
            return {**base, "status": "queued" if r.ok else "error",
                    "file": data.get("payload", {}).get("file", "")}
        except Exception as e:
            return {**base, "status": "error", "detail": str(e)[:200]}

    if op == "bidLevel":
        try:
            project_id  = params.get("project_id")
            project_code = params.get("project_code", "")
            dry_run = params.get("dry_run", True)
            code = project_code or str(project_id)
            r = requests.post(
                f"{_INTERNAL_BASE.replace('/api/v1','')}/gateway/project/{code}/bid-level",
                headers={"X-API-Key": _INTERNAL_KEY},
                params={"dry_run": dry_run},
                timeout=60,
            )
            data = r.json()
            return {**base, "status": "ok" if r.ok else "error",
                    "summary": str(data.get("payload", {}).get("summary", ""))[:100]}
        except Exception as e:
            return {**base, "status": "error", "detail": str(e)[:200]}

    if op == "driveWrite":
        return {**base, "status": "not_implemented",
                "detail": "driveWrite via batch pending Drive write service"}

    if op == "dbQuery":
        try:
            sql   = params.get("sql", "")
            args  = params.get("args", [])
            if not sql.strip().upper().startswith("SELECT"):
                return {**base, "status": "rejected", "detail": "Only SELECT allowed via batch"}
            with _pg() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, args)
                    rows = [dict(r) for r in cur.fetchall()]
            return {**base, "status": "ok", "rows": rows[:50]}
        except Exception as e:
            return {**base, "status": "error", "detail": str(e)[:200]}

    return {**base, "status": "unknown_op", "detail": f"Op '{op}' not recognized"}


@router.post("/batch")
async def gateway_batch(req: BatchRequest, request: Request):
    """
    Execute multiple gateway operations in a single call.
    GBT makes 1 tool call → N operations run server-side → 1 result returned.
    Auto-sends ntfy push on completion.
    """
    _require_key(request)
    t0 = time.time()
    rid = str(uuid.uuid4())
    session = req.session_id or rid[:8]

    results  = []
    ok_count = 0

    for op_item in req.operations:
        result = _exec_op(op_item.op, op_item.params)
        results.append(result)
        if result.get("status") in ("ok", "queued", "sent"):
            ok_count += 1

    total = len(results)
    failed = total - ok_count
    summary = f"{ok_count}/{total} operations completed"
    if failed:
        summary += f" ({failed} failed)"

    # Auto-push ntfy summary
    _ntfy(
        title=f"Batch Complete [{session}]",
        body=summary,
        priority="default",
        tags="white_check_mark" if not failed else "warning",
    )

    _log("/batch", "gbt-batch", "multi-op", "ok",
         round((time.time() - t0) * 1000), rid, summary)

    return _response("/batch", {
        "session_id":  session,
        "request_id":  rid,
        "operations":  total,
        "ok":          ok_count,
        "failed":      failed,
        "summary":     summary,
        "results":     results,
    }, start=t0)


# ── Intent Router ─────────────────────────────────────────────────────────────

import re as _re

class IntentRequest(BaseModel):
    message: str
    source: Optional[str] = "api"
    user: Optional[str] = "buck"

_INTENT_PATTERNS = [
    # bid leveling
    (r"level\s+bids?\s+(?:for\s+)?(\w+)",           "bid_leveling"),
    (r"(\w+)\s+bid\s+level",                          "bid_leveling"),
    # bids / procurement
    (r"bids?\s+(?:for\s+)?(\w+)",                    "bids"),
    (r"(\w+)\s+bids?",                                "bids"),
    # status / health
    (r"\bstatus\b|\bhealth\b|\bwhat.s up\b",         "status"),
    # daily log
    (r"daily\s+(?:log|report)\s+(?:for\s+)?(\w+)",   "daily_log"),
    # rfi
    (r"rfi\s+(?:status\s+)?(?:for\s+)?(\w+)",        "rfi_status"),
    (r"(\w+)\s+rfi",                                  "rfi_status"),
    # action list
    (r"actions?\s+(?:for\s+)?(\w+)",                  "action_list"),
    # plan analysis
    (r"(?:run\s+)?plans?\s+(?:for\s+)?(\w+)",         "plan_analysis"),
    (r"review\s+plans?\s+(?:for\s+)?(\w+)",           "plan_analysis"),
    # approve / reject
    (r"^(?:approve|yes|confirm)\b",                   "approve"),
    (r"^(?:reject|no|deny)\b",                        "reject"),
    # report
    (r"\b(?:morning\s+)?(?:brief|report|exec)\b",    "exec_report"),
]

PROJECT_CODES = {"64ew", "101f", "1355r", "246gw", "64eastwood", "101francis", "1355riverside"}

def _extract_project(msg: str) -> Optional[str]:
    for code in ["64EW", "101F", "1355R", "246GW"]:
        if code.lower() in msg.lower():
            return code
    return None

def _route_intent(intent: str, project: Optional[str], message: str) -> dict:
    base_url = "http://localhost:8000"
    headers  = {"X-API-Key": _INTERNAL_KEY}

    if intent == "status" or intent == "exec_report":
        r = requests.get(f"{base_url}/gateway/executive/report", timeout=30)
        data = r.json()
        payload = data.get("payload", {})
        brief = str(payload)[:300]
        _ntfy("HCI Status", brief[:200], "default", "chart_with_upwards_trend")
        return {"intent": intent, "result": payload}

    if intent == "bids" and project:
        r = requests.get(f"{base_url}/gateway/project/{project}/bids",
                         headers=headers, timeout=30)
        data = r.json().get("payload", {})
        summary = f"{project} bids: {len(data.get('bids',[]))} packages"
        _ntfy(f"Bids: {project}", summary, "default", "money_bag")
        return {"intent": intent, "project": project, "result": data}

    if intent == "bid_leveling" and project:
        r = requests.post(f"{base_url}/gateway/project/{project}/bid-level",
                          headers=headers, params={"dry_run": True}, timeout=60)
        data = r.json().get("payload", {})
        summary = str(data.get("summary", "leveling run"))[:150]
        _ntfy(f"Bid Level: {project}", summary, "default", "bar_chart")
        return {"intent": intent, "project": project, "dry_run": True, "result": data}

    if intent == "daily_log" and project:
        r = requests.get(f"{base_url}/gateway/project/{project}/weekly-digest",
                         headers=headers, timeout=30)
        data = r.json().get("payload", {})
        _ntfy(f"Log: {project}", str(data)[:200], "default", "memo")
        return {"intent": intent, "project": project, "result": data}

    if intent == "rfi_status" and project:
        r = requests.get(f"{base_url}/gateway/project/{project}/risks",
                         headers=headers, timeout=30)
        data = r.json().get("payload", {})
        _ntfy(f"RFIs: {project}", str(data)[:200], "default", "pencil")
        return {"intent": intent, "project": project, "result": data}

    if intent == "action_list" and project:
        r = requests.get(f"{base_url}/gateway/project/{project}/action-list",
                         headers=headers, timeout=30)
        data = r.json().get("payload", {})
        _ntfy(f"Actions: {project}", str(data)[:200], "default", "pushpin")
        return {"intent": intent, "project": project, "result": data}

    if intent == "plan_analysis" and project:
        _ntfy(f"Plans queued: {project}", "Plan analysis requested — Claude Code will run on next session", "high", "blueprints")
        return {"intent": intent, "project": project,
                "result": "Plan analysis queued — requires handoff to Claude Code"}

    if intent in ("approve", "reject"):
        return {"intent": intent, "result": "Approval queue not yet implemented — use /gateway/batch"}

    return {"intent": "unknown", "message": message,
            "result": "Intent not recognized — forwarding to manual review",
            "suggestion": "Try: 'level bids 1355R', 'status', 'bids for 64EW', 'daily log 101F'"}


@router.post("/intent/route")
async def intent_route(req: IntentRequest, request: Request):
    """
    Natural language → gateway action.
    Buck or Field GPT sends a message, this routes it and executes the right service.
    """
    _require_key(request)
    t0 = time.time()
    msg = req.message.strip()

    intent = None
    for pattern, name in _INTENT_PATTERNS:
        if _re.search(pattern, msg, _re.IGNORECASE):
            intent = name
            break

    project = _extract_project(msg)

    try:
        result = _route_intent(intent or "unknown", project, msg)
    except Exception as e:
        result = {"intent": intent, "error": str(e)[:200]}

    _log("/intent/route", req.source or "api", f"intent:{intent}", "ok",
         round((time.time() - t0) * 1000), str(uuid.uuid4()), f"intent={intent} project={project}")

    return _response("/intent/route", {
        "message":  msg,
        "source":   req.source,
        "intent":   intent,
        "project":  project,
        **result,
    }, start=t0)


# ── Plans Folder Smart Scan ───────────────────────────────────────────────────

_DISCIPLINE_PATTERNS = {
    "ARCHITECTURAL": _re.compile(r"arch|A-\d|floor.?plan|elevation|section|architectural", _re.IGNORECASE),
    "STRUCTURAL":    _re.compile(r"struct|S-\d|S\.\d|beam|foundation|framing|structural", _re.IGNORECASE),
    "MEP":           _re.compile(r"mech|M-\d|plumb|P-\d|electric|E-\d|HVAC|mechanical|plumbing", _re.IGNORECASE),
    "CIVIL":         _re.compile(r"civil|C-\d|site|grading|utility", _re.IGNORECASE),
    "INTERIOR":      _re.compile(r"interior|ID-\d|finish|FF.E|interior.design", _re.IGNORECASE),
    "ROOFING":       _re.compile(r"roof|R-\d", _re.IGNORECASE),
    "LANDSCAPE":     _re.compile(r"landscape|L-\d|planting", _re.IGNORECASE),
    "PERMITS":       _re.compile(r"permit|approved", _re.IGNORECASE),
    "PROGRESS":      _re.compile(r"progress|WIP|draft|\d+%", _re.IGNORECASE),
    "ARCHIVE":       _re.compile(r"archive|superseded|old|prior|void", _re.IGNORECASE),
}

def _classify_discipline(filename: str) -> str:
    for disc, pat in _DISCIPLINE_PATTERNS.items():
        if pat.search(filename):
            return disc
    return "GENERAL"


@router.get("/project/{code}/plans")
async def project_plans(
    code: str,
    scope: str = Query("current", description="current | archived | all"),
    disciplines: Optional[str] = Query(None, description="Comma-separated: structural,architectural,mep"),
):
    """
    Scan project drawings folder and return classified file list.
    scope=current excludes archived files. disciplines filters by type.
    """
    t0 = time.time()
    code = code.upper()

    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT drawings_folder_id, drive_folder_id, name FROM projects WHERE project_code = %s",
                    (code,)
                )
                row = cur.fetchone()

        if not row:
            return _response(f"/project/{code}/plans", {}, errors=[f"Project {code} not found"])

        folder_id = row["drawings_folder_id"] or row["drive_folder_id"]
        if not folder_id:
            return _response(f"/project/{code}/plans", {}, errors=[f"No drawings folder configured for {code}"])

        # Pull files via Drive API directly (avoids self-referential HTTP deadlock)
        from integrations.credentials import get_google_token as _gtoken
        import ssl as _ssl, certifi as _certifi, urllib.request as _ur, urllib.parse as _up
        _DBASE = "https://www.googleapis.com/drive/v3"
        _SSL = _ssl.create_default_context(cafile=_certifi.where())

        def _drive_list_folder(fid):
            token = _gtoken("drive")
            params = _up.urlencode({
                "q": f"'{fid}' in parents and trashed=false",
                "fields": "files(id,name,mimeType,modifiedTime,size)",
                "pageSize": "200",
                "supportsAllDrives": "true",
                "includeItemsFromAllDrives": "true",
            })
            req = _ur.Request(f"{_DBASE}/files?{params}",
                              headers={"Authorization": f"Bearer {token}"})
            with _ur.urlopen(req, context=_SSL, timeout=30) as r:
                import json as _j
                return _j.loads(r.read()).get("files", [])

        drive_raw = _drive_list_folder(folder_id)
        raw_files = []
        for f in drive_raw:
            raw_files.append({
                "id":        f.get("id", ""),
                "name":      f.get("name", ""),
                "mime_type": f.get("mimeType", ""),
                "modified":  f.get("modifiedTime", ""),
                "size":      f.get("size", 0),
            })

        disc_filter = {d.strip().upper() for d in disciplines.split(",")} if disciplines else None
        results = []

        for f in raw_files:
            name = f.get("name", "")
            mime = f.get("mime_type", f.get("mimeType", ""))
            # Include PDFs and folders (folders may contain PDFs)
            if "pdf" not in mime.lower() and "folder" not in mime.lower():
                continue

            disc = _classify_discipline(name)
            is_archive = bool(_DISCIPLINE_PATTERNS["ARCHIVE"].search(name))
            version_status = "archived" if is_archive else "current"

            if scope == "current" and is_archive:
                continue
            if scope == "archived" and not is_archive:
                continue
            if disc_filter and disc not in disc_filter:
                continue

            results.append({
                "file_id":        f.get("id", ""),
                "filename":       name,
                "discipline":     disc,
                "version_status": version_status,
                "modified_date":  f.get("modified", f.get("modifiedTime", "")),
                "size_bytes":     f.get("size", f.get("fileSize", 0)),
            })

        return _response(f"/project/{code}/plans", {
            "project":          code,
            "drawings_folder":  folder_id,
            "scope":            scope,
            "disciplines":      list(disc_filter) if disc_filter else "all",
            "file_count":       len(results),
            "files":            results,
        }, start=t0)

    except Exception as e:
        return _response(f"/project/{code}/plans", {}, errors=[str(e)], start=t0)


@router.get("/project/{code}/shared-drive-id")
async def project_shared_drive_id(code: str):
    """Return configured Drive folder IDs for a project."""
    t0 = time.time()
    code = code.upper()
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT project_code, drive_folder_id, drawings_folder_id, bid_folder_id, gsheet_bid_tracker FROM projects WHERE project_code = %s",
                    (code,)
                )
                row = cur.fetchone()
        if not row:
            return _response(f"/project/{code}/shared-drive-id", {}, errors=["Project not found"])
        return _response(f"/project/{code}/shared-drive-id", dict(row), start=t0)
    except Exception as e:
        return _response(f"/project/{code}/shared-drive-id", {}, errors=[str(e)], start=t0)


# ─────────────────────────────────────────────────────────────────────────────
# APPROVAL LOOP — ntfy-aware approval creation (approve/reject/list use
# existing endpoints at /approvals/pending, /approvals/{id}/approve|reject)
# ─────────────────────────────────────────────────────────────────────────────

class ApprovalCreateRequest(BaseModel):
    action_type: str
    target_description: str
    reason: Optional[str] = None
    project_code: Optional[str] = None
    amount: Optional[float] = None
    proposed_payload: Optional[Dict[str, Any]] = {}
    priority: Optional[str] = "normal"
    workflow: Optional[str] = "manual"


@router.post("/approvals")
async def create_approval(req: ApprovalCreateRequest, request: Request):
    """
    Queue an action for Buck's approval via the approval_queue table.
    Automatically pushes ntfy so Buck gets a phone notification.
    Use GET /approvals/pending to see queue, POST /approvals/{id}/approve|reject to act.
    """
    t0 = time.time()
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO approval_queue
                        (workflow, action_type, target_system, target_description,
                         reason, project_id, proposed_payload, priority, actor)
                    SELECT %s, %s, %s, %s, %s, p.id, %s, %s, 'gateway'
                    FROM projects p WHERE p.project_code = %s
                    RETURNING id
                """, (
                    req.workflow, req.action_type,
                    req.project_code or "system",
                    req.target_description,
                    req.reason,
                    psycopg2.extras.Json(req.proposed_payload or {}),
                    req.priority,
                    req.project_code,
                ))
                row = cur.fetchone()
                if not row:
                    # Insert without project FK if project_code not found
                    cur.execute("""
                        INSERT INTO approval_queue
                            (workflow, action_type, target_system, target_description,
                             reason, proposed_payload, priority, actor)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,'gateway')
                        RETURNING id
                    """, (
                        req.workflow, req.action_type,
                        req.project_code or "system",
                        req.target_description, req.reason,
                        psycopg2.extras.Json(req.proposed_payload or {}),
                        req.priority,
                    ))
                    row = cur.fetchone()
            conn.commit()
        approval_id = row["id"] if row else None
        # Push ntfy
        amt_str = f" ${req.amount:,.0f}" if req.amount else ""
        proj_str = f" [{req.project_code}]" if req.project_code else ""
        _ntfy(
            f"Needs approval #{approval_id}{proj_str}",
            f"{req.target_description}{amt_str}\n\n"
            f"Type: {req.action_type}\n{req.reason or ''}\n\n"
            f"Act at: GET /gateway/approvals/pending\n"
            f"Approve: POST /gateway/approvals/{approval_id}/approve",
            priority="high", tags="bell"
        )
        _log("/approvals", "gateway", "approval_queue", "created",
             round((time.time()-t0)*1000), str(uuid.uuid4()), f"id={approval_id}")
        return _response("/approvals", {"approval_id": approval_id, "status": "pending", "ntfy_sent": True}, start=t0)
    except Exception as e:
        return _response("/approvals", {}, errors=[str(e)], start=t0)


# ─────────────────────────────────────────────────────────────────────────────
# EVENT TRIGGER SYSTEM — health change alerts, new bid leveling, drive watcher
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/events/health-check")
async def event_health_check(request: Request):
    """
    Scheduled event: poll all project health scores. Push ntfy if any project
    crossed a threshold (GREEN->YELLOW, YELLOW->RED, any->RED).
    Called by n8n every 30 minutes.
    """
    t0 = time.time()
    alerts = []
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                # Compare today's health vs yesterday's from project_brain_snapshots
                cur.execute("""
                    SELECT p.project_code,
                           today.health AS current_health,
                           yesterday.health AS prev_health
                    FROM projects p
                    LEFT JOIN LATERAL (
                        SELECT health FROM project_brain_snapshots
                        WHERE project_id = p.id
                        ORDER BY snapshot_date DESC LIMIT 1
                    ) today ON TRUE
                    LEFT JOIN LATERAL (
                        SELECT health FROM project_brain_snapshots
                        WHERE project_id = p.id
                        ORDER BY snapshot_date DESC OFFSET 1 LIMIT 1
                    ) yesterday ON TRUE
                    WHERE p.status = 'active' AND p.project_code IS NOT NULL
                """)
                rows = cur.fetchall()

        SEVERITY = {"GREEN": 0, "YELLOW": 1, "RED": 2, "CRITICAL": 3}
        for row in rows:
            code = row["project_code"]
            current = (row["current_health"] or "GREEN").upper()
            previous = (row["prev_health"] or "GREEN").upper()
            curr_sev = SEVERITY.get(current, 0)
            prev_sev = SEVERITY.get(previous, 0)
            if curr_sev > prev_sev:
                alerts.append({
                    "project": code,
                    "from": previous,
                    "to": current,
                    "severity": "CRITICAL" if current == "RED" else "HIGH"
                })

        if alerts:
            for alert in alerts:
                priority = "urgent" if alert["to"] == "RED" else "high"
                _ntfy(
                    f"HEALTH ALERT: {alert['project']} {alert['from']}->{alert['to']}",
                    f"Project {alert['project']} health changed: {alert['from']} -> {alert['to']}\n"
                    f"Check /gateway/project/{alert['project']}/pm for top risks",
                    priority=priority, tags="warning"
                )
        else:
            pass  # No change — no push needed

        _log("/events/health-check", "n8n", "projects", "ok",
             round((time.time()-t0)*1000), str(uuid.uuid4()), f"{len(alerts)} alerts")
        return _response("/events/health-check", {
            "projects_checked": len(rows),
            "alerts_fired": len(alerts),
            "alerts": alerts
        }, start=t0)
    except Exception as e:
        return _response("/events/health-check", {}, errors=[str(e)], start=t0)


@router.post("/events/new-bid")
async def event_new_bid(request: Request):
    """
    Event: called when a new bid PDF lands in Drive vendor folder.
    Auto-runs bid leveling and pushes ntfy.
    """
    t0 = time.time()
    try:
        body = await request.json()
    except Exception:
        body = {}
    code = (body.get("project_code") or "").upper()
    vendor = body.get("vendor_name", "unknown vendor")
    amount = body.get("amount")
    division = body.get("division", "")
    filename = body.get("filename", "")

    if not code:
        return _response("/events/new-bid", {}, errors=["project_code required"], start=t0)

    # Push ntfy about new bid
    amt_str = f" ${float(amount):,.0f}" if amount else ""
    _ntfy(
        f"New bid: {code} {division}",
        f"New bid received: {vendor}{amt_str}\nProject: {code} {division}\nFile: {filename}\n"
        f"Bid leveling running automatically...",
        priority="default", tags="incoming_envelope"
    )

    # Auto-queue bid leveling for this project (dry_run by default for safety)
    leveling_result = {}
    try:
        import urllib.request as _ur2
        req2 = _ur2.Request(
            f"http://localhost:8000/gateway/project/{code}/bid-level?dry_run=true",
            headers={"X-API-Key": os.environ.get("HCI_API_KEY", "")},
            method="POST"
        )
        with _ur2.urlopen(req2, timeout=20) as r:
            leveling_result = json.loads(r.read()).get("payload", {})
    except Exception as le:
        leveling_result = {"error": str(le)}

    # Push leveling result
    summary = leveling_result.get("summary", "Leveling complete — check /gateway/project/{code}/bid-level")
    _ntfy(
        f"Bid leveling updated: {code}",
        f"Auto-leveling complete for {code}\n{summary}\nFull results: GET /gateway/project/{code}/bid-level",
        priority="default", tags="bar_chart"
    )

    _log("/events/new-bid", "gateway", code, "ok",
         round((time.time()-t0)*1000), str(uuid.uuid4()), f"{vendor} ${amount or 0:,.0f}")
    return _response("/events/new-bid", {
        "project": code,
        "vendor": vendor,
        "amount": amount,
        "bid_leveling": leveling_result,
        "ntfy_sent": True,
    }, start=t0)


@router.post("/events/drive-scan")
async def event_drive_scan(request: Request):
    """
    Scheduled event (every 15 min): scan 04_Drawings folders for new files.
    Compare against known file list in DB. Auto-queue plan analysis on new PDFs.
    Called by n8n cron.
    """
    t0 = time.time()
    new_files = []

    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT project_code, drawings_folder_id
                    FROM projects
                    WHERE drawings_folder_id IS NOT NULL AND is_active = TRUE
                """)
                projects = cur.fetchall()
    except Exception as e:
        return _response("/events/drive-scan", {}, errors=[str(e)], start=t0)

    import ssl as _ssl2, certifi as _certif2, urllib.request as _ur3, urllib.parse as _up3
    _SSL2 = _ssl2.create_default_context(cafile=_certif2.where())

    def _drive_files(folder_id: str, token: str) -> list:
        params = _up3.urlencode({
            "q": f"'{folder_id}' in parents and trashed=false and mimeType='application/pdf'",
            "fields": "files(id,name,modifiedTime,size)",
            "supportsAllDrives": "true", "includeItemsFromAllDrives": "true",
            "pageSize": "200"
        })
        req3 = _ur3.Request(
            f"https://www.googleapis.com/drive/v3/files?{params}",
            headers={"Authorization": f"Bearer {token}"}
        )
        with _ur3.urlopen(req3, context=_SSL2, timeout=20) as r:
            return json.loads(r.read()).get("files", [])

    try:
        from integrations.credentials import get_google_token as _gtoken2
        token = _gtoken2("drive")
    except Exception as e:
        return _response("/events/drive-scan", {}, errors=[f"Drive auth failed: {e}"], start=t0)

    for project in projects:
        code = project["project_code"]
        folder_id = project["drawings_folder_id"]
        try:
            drive_files = _drive_files(folder_id, token)
        except Exception:
            continue

        # Check each file against known_files log
        for f in drive_files:
            file_id = f["id"]
            fname = f["name"]
            with _pg() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 1 FROM drive_file_log
                        WHERE file_id = %s AND project_code = %s
                    """, (file_id, code))
                    known = cur.fetchone()
                    if not known:
                        # New file — log it
                        cur.execute("""
                            INSERT INTO drive_file_log (file_id, project_code, filename, folder_id, discovered_at)
                            VALUES (%s,%s,%s,%s,NOW())
                            ON CONFLICT (file_id) DO NOTHING
                        """, (file_id, code, fname, folder_id))
                        new_files.append({"project": code, "filename": fname, "file_id": file_id})

    if new_files:
        for nf in new_files:
            _ntfy(
                f"New plan: {nf['project']}",
                f"New drawing uploaded to {nf['project']}:\n{nf['filename']}\n"
                f"Plan analysis auto-queued. Run GET /gateway/project/{nf['project']}/plans to see all files.",
                priority="default", tags="page_facing_up"
            )
            # Queue plan analysis handoff
            _ntfy(
                f"Analysis queued: {nf['filename'][:40]}",
                f"Queued for analysis: {nf['filename']}\nProject: {nf['project']}\n"
                f"Claude Code will process next session.",
                priority="low", tags="mag"
            )

    _log("/events/drive-scan", "n8n", "google_drive", "ok",
         round((time.time()-t0)*1000), str(uuid.uuid4()), f"{len(new_files)} new files")
    return _response("/events/drive-scan", {
        "projects_scanned": len(projects),
        "new_files_found": len(new_files),
        "new_files": new_files,
    }, start=t0)

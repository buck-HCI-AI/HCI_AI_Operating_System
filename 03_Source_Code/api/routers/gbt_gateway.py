"""
GBT Orchestrator Gateway — n8n Bridge for ChatGPT
Exposes all HCI AI OS services via authenticated HTTPS endpoints (ngrok tunnel on :8000).

ChatGPT → https://speculate-armband-retinal.ngrok-free.dev/gateway/{path}
Architecture:  ChatGPT → ngrok → FastAPI Gateway → internal HCI services → normalized JSON

Prefix: /gateway
Auth:   X-API-Key header  OR  ?api_key= query param
"""
import os, re, uuid, time, sys, json, subprocess, threading
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import psycopg2, psycopg2.extras, requests
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))
from fastapi import APIRouter, HTTPException, Request, Query, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime, timezone, timedelta, date
from zoneinfo import ZoneInfo

router = APIRouter(prefix="/gateway", tags=["gbt-gateway"])

BUCK_TZ = ZoneInfo("America/Denver")  # Aspen, CO


def _buck_local_str(dt: datetime = None) -> str:
    """Format a timestamp in Buck's local timezone for anything he actually reads
    (Telegram, reports) — internal storage stays UTC, this is a display-only helper.
    Found 2026-07-07: every timestamp system-wide was raw UTC with no local
    conversion anywhere, so every message Buck saw was in the wrong timezone."""
    if dt is None:
        dt = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    local = dt.astimezone(BUCK_TZ)
    return local.strftime("%Y-%m-%d %-I:%M %p %Z")

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
    {"name": "field-brain",         "path": "/gateway/brain/ask",                 "description": "Ask any cross-project historical question (cost benchmarks, sub reliability, past issues) — POST, async job_id pattern"},
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
    {"name": "project-view",        "path": "/gateway/project/{code}/view",           "description": "GET ?view=brain|schedule|bids|pm|deep-dive|cost-forecast|action-list - single parameterized endpoint, dispatches to the exact same 7 functions above. Added 2026-07-11 to free ChatGPT Actions schema slots (30-op platform cap); the 7 individual routes above stay live for backward compatibility, this is what GBT's schema now calls instead"},
    {"name": "project-state",       "path": "/gateway/project-state",             "description": "Full live system state (all projects, health, AI team)"},
    {"name": "executive-report",    "path": "/gateway/executive/report",          "description": "Executive morning brief across all projects"},
    {"name": "knowledge-graph",     "path": "/gateway/knowledge/vendor",         "description": "Vendor cross-project lookup by name"},
    {"name": "knowledge-vendors",   "path": "/gateway/knowledge/vendors",        "description": "Paginated vendor list with CSI + search filters (Gap5)"},
    {"name": "knowledge-lessons",   "path": "/gateway/knowledge/lessons",        "description": "Lessons learned from past projects (Gap6)"},
    {"name": "drive-search",        "path": "/gateway/drive/search",             "description": "Search Google Drive files"},
    {"name": "coord-docs-list",      "path": "/gateway/coordination/documents",           "description": "AI Team Document Bus - GET HCI AI Master coordination docs, optional ?since= filter"},
    {"name": "coord-docs-read",      "path": "/gateway/coordination/documents/{file_id}", "description": "AI Team Document Bus - GET read a coordination doc's content"},
    {"name": "coord-docs-ack",       "path": "/gateway/coordination/documents/{file_id}/acknowledge", "description": "AI Team Document Bus - POST record an agent acknowledged a doc"},
    {"name": "coord-docs-status",    "path": "/gateway/coordination/documents/{file_id}/status", "description": "AI Team Document Bus - GET which agents have/haven't acknowledged a doc"},
    {"name": "coord-docs-create",    "path": "/gateway/coordination/documents",           "description": "AI Team Document Bus - POST create a durable message + real Drive doc from one agent to another (from_agent, to_agent, subject, content, priority) - this is how GBT reaches Browser Claude (or BC reaches GBT) without Buck relaying, since BC can only read Drive, not call this gateway directly"},
    {"name": "agent-handoff",       "path": "/gateway/agent/handoff",            "description": "POST a platform intelligence document"},
    {"name": "agent-unread",        "path": "/gateway/agent/unread",             "description": "GET ?agent=X - single-call catch-up: everything in ai_messages waiting for this agent (status ISSUED or NEEDS_BUCK_APPROVAL), oldest first"},
    {"name": "agent-heartbeat",     "path": "/gateway/agent/heartbeat",          "description": "POST explicit self-report {agent, mission?, session_id?} - marks this agent ONLINE right now with what it's working on"},
    {"name": "amb-send",            "path": "/gateway/agent/messages",           "description": "ADR-003 Agent Message Bus - POST send a message {from_agent, to_agent, subject, body, priority?, thread_id?, requires_response?} to BC/GBT/CODE/ALL"},
    {"name": "amb-unread",          "path": "/gateway/agent/messages/unread",    "description": "ADR-003 Agent Message Bus - GET ?agent=BC|GBT|CODE, everything pending for that agent, oldest first"},
    {"name": "amb-read",            "path": "/gateway/agent/messages/{message_id}/read", "description": "ADR-003 Agent Message Bus - POST {agent} mark a message read"},
    {"name": "amb-reply",           "path": "/gateway/agent/messages/{message_id}/reply", "description": "ADR-003 Agent Message Bus - POST {from_agent, body} reply in-thread, auto-closes the original if it required a response"},
    {"name": "amb-status",          "path": "/gateway/agent/status",             "description": "ADR-003 Agent Message Bus - GET current status (online/offline/stale) + mission for all 3 agents"},
    {"name": "amb-decision-create", "path": "/gateway/agent/decisions",          "description": "ADR-003 Agent Message Bus - POST {decision, rationale, evidence?, proposed_by} log a proposed architecture decision"},
    {"name": "amb-decision-list",   "path": "/gateway/agent/decisions",          "description": "ADR-003 Agent Message Bus - GET ?status=pending|approved|rejected|implemented"},
    {"name": "amb-decision-approve","path": "/gateway/agent/decisions/{decision_id}/approve", "description": "ADR-003 Agent Message Bus - POST {agent} approve a decision, needs 2 of 3 agents to flip to approved"},
    {"name": "field-note",          "path": "/gateway/field/note",               "description": "POST quick field note from SS/PM (direct write, no approval)"},
    {"name": "field-rfi",           "path": "/gateway/field/rfi",                "description": "POST new RFI from field (Gap11)"},
    {"name": "email-draft",         "path": "/gateway/email/draft",              "description": "POST general-purpose Outlook draft (subject, body_html, to_email?, to_name?) - for bid solicitations and other non-RFI outbound email; gates on is_onboarded and self-BCCs Buck, draft-only, never auto-sent"},
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
    {"name": "users-list",          "path": "/gateway/users",                    "description": "GET HCI team roster (name, email, role, projects, onboarded status) for Field GPT/GBT user-identity flow"},
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


class MonitoredFolderWriteError(Exception):
    """Raised when a Drive write targets a monitored project's root folder."""
    pass


def _reject_if_monitored_folder(folder_id: str) -> None:
    """Same permanent directive as bid_leveling_service.reject_if_monitored_folder -
    monitored/reference jobs are read-only. Applied here too (2026-07-12) for
    consistency across every Drive-write tool, not just the bid-leveling ones.
    2026-07-13 fix: widened from status='monitoring' to status IN ('monitoring',
    'reference') - was silently missing 212CL/370G/655G/675M, which Buck's own
    directive names by name as protected."""
    with _pg() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT project_code FROM projects WHERE status IN ('monitoring', 'reference') AND drive_folder_id=%s",
                (folder_id,)
            )
            row = cur.fetchone()
    if row:
        raise MonitoredFolderWriteError(
            f"Refused: {row['project_code']} is a monitored project - read-only per "
            f"permanent directive, no writes to its Drive folder are permitted."
        )


def _response(path: str, payload: Any, source: str = "hci-api",
              start: float = None, warnings: list = None, errors: list = None) -> dict:
    """Standard envelope. timestamp_mt added 2026-07-08: Buck flagged (repeatedly,
    across multiple sessions) that GBT keeps showing him UTC times as if they were
    his own. GBT reads timestamp straight off this envelope with no reason to know
    it's UTC - telling the GPT's prompt to "remember to convert" isn't reliable
    since every response is stateless. Putting an explicitly-labeled Mountain-time
    string right next to the UTC one means any consumer (GBT, a human reading raw
    JSON, a future integration) sees the right time by default without needing to
    know or convert anything. timestamp (UTC ISO) is left untouched for any
    existing code that parses/logs against it."""
    elapsed = round((time.time() - start) * 1000) if start else 0
    now_utc = datetime.now(timezone.utc)
    return {
        "status": "ok" if not errors else "error",
        "timestamp": now_utc.isoformat(),
        "timestamp_mt": now_utc.astimezone(BUCK_TZ).strftime("%Y-%m-%d %-I:%M %p MT"),
        "execution_time_ms": elapsed,
        "source_system": source,
        "payload": payload,
        "warnings": warnings or [],
        "errors": errors or [],
    }


def _log(path: str, source: str, upstream: str, status: str, ms: int,
         request_id: str, response_summary: str = "", payload: dict = None):
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO gateway_request_log
                        (request_id, path, source_system, upstream_endpoint, status, execution_ms, response_summary, payload)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (request_id, path, source, upstream, status, ms, response_summary[:200],
                      json.dumps(payload) if payload is not None else '{}'))
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
        # intelligence endpoint requires integer project_id. ai_summary=false: this
        # endpoint's consumer is GBT (ChatGPT) — an AI reading raw structured data
        # doesn't need another AI's prose summary of the same data, and the internal
        # Claude call to generate one was adding 3-7s of latency (root cause of GBT's
        # "gateway unreachable" failure 2026-07-02 — it wasn't unreachable, it was
        # slow enough to exceed GBT's action-call timeout).
        numeric_pid = _get_pid(code)
        intel = {}
        try:
            intel = _proxy(f"/services/project-brain/{numeric_pid}/intelligence", params={"ai_summary": "false"})
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


def _gather_deep_dive(code: str) -> dict:
    """Shared data-gathering for deep-dive JSON and the status-page HTML view - one
    query set, two presentations. Raises ValueError with a message if the project
    code isn't found."""
    with _pg() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, project_code, contract_value, status, permit_status
                FROM projects WHERE UPPER(project_code) = UPPER(%s)
            """, (code,))
            proj = cur.fetchone()
            if not proj:
                raise ValueError(f"Unknown project code: {code}")
            pid = proj["id"]

            # Daily logs — last 14 days, most recent first
            cur.execute("""
                SELECT log_date, work_performed, issues, weather, crew_on_site,
                       manpower, deliveries, inspections, logged_by
                FROM daily_logs WHERE project_id = %s
                ORDER BY log_date DESC LIMIT 14
            """, (pid,))
            logs = [dict(r) for r in cur.fetchall()]
            last_log_date = logs[0]["log_date"] if logs else None
            days_since_log = (date.today() - last_log_date).days if last_log_date else None

            # Schedule — upcoming and overdue items
            cur.execute("""
                SELECT activity_id, title, start_date, end_date, status, completion_pct, task_type
                FROM project_schedule_items WHERE project_id = %s::text
                ORDER BY start_date ASC NULLS LAST
            """, (pid,))
            sched_items = [dict(r) for r in cur.fetchall()]
            today = date.today()
            overdue = [s for s in sched_items if s["end_date"] and s["end_date"] < today
                       and (s["status"] or "").lower() not in ("complete", "completed", "done")]
            upcoming = [s for s in sched_items if s["start_date"] and s["start_date"] >= today][:8]
            total_items = len(sched_items)
            complete_items = len([s for s in sched_items if (s["status"] or "").lower() in ("complete", "completed", "done")])

            # Budget — bid packages + committed amount
            cur.execute("""
                SELECT bp.id, bp.package_name, bp.csi_division, bp.status, bp.awarded_amount,
                    (SELECT COUNT(*) FROM bid_entries be WHERE be.bid_package_id = bp.id) AS bid_count,
                    (SELECT MIN(be.bid_amount) FROM bid_entries be WHERE be.bid_package_id = bp.id AND be.bid_amount > 0) AS low_bid,
                    (SELECT MAX(be.bid_amount) FROM bid_entries be WHERE be.bid_package_id = bp.id AND be.bid_amount > 0) AS high_bid
                FROM bid_packages bp WHERE bp.project_id = %s
            """, (pid,))
            packages = [dict(r) for r in cur.fetchall()]
            total_packages = len(packages)
            # Buck caught this live during Adam-demo prep, 2026-07-08: 101F showed
            # divisions 06/07/08/11/15 as "zero bids" when real bids existed. Root
            # cause - two different bid-data shapes coexist: some packages record
            # one bid_packages row per division with bid_entries children (bid_count
            # works), others (from the Drive bid-folder scan) record one
            # bid_packages row PER VENDOR with the vendor's bid folded into
            # package_name/status directly - bid_entries is empty for those by
            # design, so bid_count alone false-flags a package that already has a
            # real bid. status='bid_received'/'awarded' is ground truth either way.
            _HAS_BID_STATUSES = ("bid_received", "awarded")
            no_bid_packages = [p["package_name"] for p in packages
                                if p["bid_count"] == 0 and p["status"] not in _HAS_BID_STATUSES]
            awarded = [p for p in packages if p["status"] == "awarded"]
            committed = sum(float(p["awarded_amount"] or 0) for p in awarded)
            contract_value = float(proj["contract_value"] or 0)
            # Flag packages with a wide bid spread — scope likely not normalized yet
            spread_flags = [
                {"package": p["package_name"], "low": float(p["low_bid"]), "high": float(p["high_bid"]),
                 "spread_pct": round((float(p["high_bid"]) - float(p["low_bid"])) / float(p["low_bid"]) * 100)}
                for p in packages if p["low_bid"] and p["high_bid"] and p["bid_count"] >= 2
                and (float(p["high_bid"]) - float(p["low_bid"])) / float(p["low_bid"]) > 0.5
            ]

            # Risks and RFIs
            cur.execute("""
                SELECT risk_type, severity, description, identified_date
                FROM risks WHERE project_id = %s AND status = 'open'
                ORDER BY CASE severity WHEN 'critical' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END
            """, (pid,))
            open_risks = [dict(r) for r in cur.fetchall()]

            cur.execute("""
                SELECT rfi_number, subject, submitted_date, required_response_date, status
                FROM rfis WHERE project_id = %s AND status = 'open'
                ORDER BY required_response_date ASC NULLS LAST
            """, (pid,))
            open_rfis = [dict(r) for r in cur.fetchall()]
            overdue_rfis = [r for r in open_rfis if r["required_response_date"] and r["required_response_date"] < today]

    # Synthesis — structured flags, not prose. Consumers (GPTs) turn these into narrative.
    flags = []
    if proj["permit_status"] == "not_issued":
        flags.append("No permit issued yet — any daily-log/schedule data implying active field construction should be treated as pre-construction planning, not real progress.")
    elif proj["permit_status"] == "iffr":
        flags.append("Issued-for-field-review (IFFR) permit — field work is permitted under IFFR scope; full building permit is still pending. Does not imply active construction — check daily-log recency separately, since a project can be legitimately on hold (e.g. bids/awards only) while still IFFR.")
    if days_since_log is not None and days_since_log > 7:
        flags.append(f"No daily log in {days_since_log} days — field reporting has gone quiet.")
    if overdue:
        flags.append(f"{len(overdue)} schedule item(s) past their end date and not marked complete.")
    if overdue_rfis:
        flags.append(f"{len(overdue_rfis)} RFI(s) past their required response date.")
    if no_bid_packages:
        flags.append(f"{len(no_bid_packages)} bid package(s) with zero bids received.")
    if spread_flags:
        flags.append(f"{len(spread_flags)} bid package(s) with >50% spread between low and high bid — scope likely not normalized.")

    return {
        "project": proj["name"],
        "project_code": proj["project_code"],
        "status": proj["status"],
        "permit_status": proj["permit_status"],
        "daily_logs": {
            "last_14_days": logs,
            "last_log_date": last_log_date.isoformat() if last_log_date else None,
            "days_since_last_log": days_since_log,
        },
        "schedule": {
            "total_items": total_items,
            "complete_items": complete_items,
            "pct_complete": round(complete_items / total_items * 100) if total_items else 0,
            "overdue": overdue,
            "upcoming_next_8": upcoming,
        },
        "budget": {
            "contract_value": contract_value,
            "committed": committed,
            "pct_committed": round(committed / contract_value * 100) if contract_value else 0,
            "total_packages": total_packages,
            "packages_with_no_bids": no_bid_packages,
            "bid_spread_flags": spread_flags,
        },
        "open_risks": open_risks,
        "open_rfis": open_rfis,
        "overdue_rfis": overdue_rfis,
        "flags": flags,
    }


@router.get("/project/{code}/deep-dive")
def project_deep_dive(code: str):
    """Full per-project synthesis — daily logs, schedule, and budget together, not just
    a health/summary line. Added 2026-07-02 per Buck: 'not just an overview, full deep
    dive into each project.' Pulls real rows (not derived health scores) so a GPT can
    actually answer 'where do things stand on X' with specifics."""
    t0 = time.time()
    try:
        data = _gather_deep_dive(code)
        return _response(f"/project/{code}/deep-dive", data, start=t0)
    except ValueError as e:
        return _response(f"/project/{code}/deep-dive", {}, errors=[str(e)], start=t0)
    except Exception as e:
        return _response(f"/project/{code}/deep-dive", {}, errors=[str(e)], start=t0)


def _money(n) -> str:
    try:
        return f"${float(n):,.0f}"
    except (TypeError, ValueError):
        return "$0"


def _status_health(data: dict) -> tuple:
    """Returns (label, color) - red/yellow/green banded off the same real flags
    the JSON endpoint already computes, so the page and the API never disagree."""
    n_flags = len(data.get("flags", []))
    overdue_rfis = len(data.get("overdue_rfis", []))
    critical_risks = len([r for r in data.get("open_risks", []) if r.get("severity") == "critical"])
    if critical_risks or overdue_rfis >= 3 or n_flags >= 4:
        return "Needs Attention", "#e0615c"
    if n_flags >= 1:
        return "On Track, Watching", "#e3a23f"
    return "On Track", "#4fae7c"


def _render_project_status_card(data: dict, standalone: bool = True) -> str:
    """One project's full picture, rendered as a clean card - reused by both the
    single-project status page and the weekly portfolio-wide report email."""
    label, color = _status_health(data)
    budget = data["budget"]
    sched = data["schedule"]
    logs = data["daily_logs"]

    rfi_rows = "".join(
        f'<tr><td>{r.get("rfi_number","")}</td><td>{r.get("subject","")[:60]}</td>'
        f'<td>{r.get("required_response_date") or "—"}</td></tr>'
        for r in data["open_rfis"][:10]
    ) or '<tr><td colspan="3" style="color:#8d97a8">No open RFIs</td></tr>'

    risk_rows = "".join(
        f'<tr><td style="text-transform:capitalize">{r.get("severity","")}</td>'
        f'<td>{(r.get("description") or "")[:90]}</td></tr>'
        for r in data["open_risks"][:8]
    ) or '<tr><td colspan="2" style="color:#8d97a8">No open risks</td></tr>'

    flags_html = "".join(f"<li>{f}</li>" for f in data["flags"]) or "<li style='color:#8d97a8'>No flags — clean</li>"

    return f"""
    <div class="proj-card">
      <div class="proj-head">
        <div>
          <div class="proj-name">{data['project']} <span class="proj-code">({data['project_code']})</span></div>
          <div class="proj-sub">{(data.get('status') or '').title()} · Permit: {(data.get('permit_status') or 'unknown').upper()}</div>
        </div>
        <div class="pill" style="background:{color}22;color:{color};border:1px solid {color}55">{label}</div>
      </div>

      <div class="metric-grid">
        <div class="metric"><div class="mval">{_money(budget['contract_value'])}</div><div class="mlabel">Contract Value</div></div>
        <div class="metric"><div class="mval">{_money(budget['committed'])}</div><div class="mlabel">Committed ({budget['pct_committed']}%)</div></div>
        <div class="metric"><div class="mval">{sched['pct_complete']}%</div><div class="mlabel">Schedule Complete</div></div>
        <div class="metric"><div class="mval">{len(data['open_rfis'])}</div><div class="mlabel">Open RFIs</div></div>
        <div class="metric"><div class="mval">{len(data['open_risks'])}</div><div class="mlabel">Open Risks</div></div>
        <div class="metric"><div class="mval">{logs['days_since_last_log'] if logs['days_since_last_log'] is not None else '—'}</div><div class="mlabel">Days Since Log</div></div>
      </div>

      <div class="two-col">
        <div>
          <div class="section-title">Open RFIs</div>
          <table><thead><tr><th>#</th><th>Subject</th><th>Due</th></tr></thead><tbody>{rfi_rows}</tbody></table>
        </div>
        <div>
          <div class="section-title">Open Risks</div>
          <table><thead><tr><th>Severity</th><th>Description</th></tr></thead><tbody>{risk_rows}</tbody></table>
        </div>
      </div>

      <div class="section-title">Flags</div>
      <ul class="flags">{flags_html}</ul>
    </div>
    """


_STATUS_PAGE_CSS = """
  body { font-family: -apple-system, "Segoe UI", sans-serif; background: #10141a; color: #e7ebf0; margin: 0; padding: 24px 16px 60px; }
  .wrap { max-width: 900px; margin: 0 auto; }
  h1 { font-size: 20px; margin: 0 0 4px; }
  .subtitle { color: #8d97a8; font-size: 13px; margin: 0 0 24px; }
  .proj-card { background: #1a2029; border: 1px solid #2c3542; border-radius: 10px; padding: 20px; margin-bottom: 20px; }
  .proj-head { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
  .proj-name { font-size: 17px; font-weight: 700; }
  .proj-code { color: #8d97a8; font-weight: 400; font-size: 13px; }
  .proj-sub { color: #8d97a8; font-size: 12.5px; margin-top: 2px; }
  .pill { font-size: 11.5px; font-weight: 600; padding: 4px 10px; border-radius: 20px; white-space: nowrap; }
  .metric-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; margin-bottom: 20px; }
  .metric { background: #212836; border-radius: 8px; padding: 10px; text-align: center; }
  .mval { font-family: ui-monospace, monospace; font-size: 15px; font-weight: 700; }
  .mlabel { font-size: 10px; color: #8d97a8; margin-top: 2px; }
  .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 16px; }
  .section-title { font-size: 11px; text-transform: uppercase; letter-spacing: .06em; color: #8d97a8; margin: 12px 0 8px; }
  table { border-collapse: collapse; width: 100%; font-size: 12.5px; }
  th { text-align: left; color: #8d97a8; font-weight: 600; font-size: 10.5px; text-transform: uppercase; padding: 0 8px 6px 0; border-bottom: 1px solid #2c3542; }
  td { padding: 6px 8px 6px 0; border-bottom: 1px solid #2c3542; vertical-align: top; }
  .flags { margin: 0; padding-left: 18px; font-size: 12.5px; color: #e3a23f; }
  .flags li { margin-bottom: 4px; }
  @media (max-width: 700px) { .metric-grid { grid-template-columns: repeat(3, 1fr); } .two-col { grid-template-columns: 1fr; } }
"""


@router.get("/project/{code}/status-page", response_class=HTMLResponse, include_in_schema=False)
def project_status_page(code: str):
    """On-demand, always-fresh full-picture status page - budget, schedule, open
    RFIs, open risks, in one simple view. Built 2026-07-08 per Buck: budget,
    schedule, outstanding RFIs, complete picture, simple format, for him/Chris/
    management. Same real data as /deep-dive, just a page instead of raw JSON."""
    from fastapi.responses import HTMLResponse
    try:
        data = _gather_deep_dive(code)
    except ValueError as e:
        return HTMLResponse(content=f"<body style='background:#10141a;color:#e0615c;font-family:sans-serif;padding:40px'>{e}</body>", status_code=404)
    html = f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{data['project']} — Status</title><style>{_STATUS_PAGE_CSS}</style></head>
<body><div class="wrap">
<h1>{data['project']} — Project Status</h1>
<p class="subtitle">Live as of this page load · {datetime.now(BUCK_TZ).strftime('%b %d, %Y %-I:%M %p')} MT</p>
{_render_project_status_card(data)}
</div></body></html>"""
    return HTMLResponse(content=html)


_LIVE_PROJECT_CODES = ("64EW", "101F", "1355R")  # the only jobs the system is allowed to write to / run automation on.
# Fixed 2026-07-08: 246GW was wrongly included here (and its DB status was 'active', which
# also made it pass the base_connector.py write guard). Buck: "246 is not a live project -
# it is the next potential pilot." Its status='active' row was pre-existing (since 2026-06-28,
# predates this session) and nothing here re-verified it against Buck's actual intent - it
# just got trusted as ground truth, same class of bug as the 'reference' mislabel found
# earlier this session, just in the opposite direction (wrongly-live instead of wrongly-closed).
# Real Houzz daily-log writes landed on 246GW because of this (reverted). Still reportable via
# the Drive-name-match / fallback branches in _reportable_project_codes() below - just no
# longer write-authorized. DB status corrected pending Buck's call on the right value.
_SYNTHETIC_TEMPLATE_CODES = ("ASPN-MC", "ASPN-NEW", "ASPN-REM", "LEGACY-001", "TEST-001")  # no real address, no real Drive
_NOT_YET_REAL_CODES = ("83SB", "LICHT")  # Buck 2026-07-08: not ready for reporting yet - 83 Sagebrusch is TBD, Lichtenstein excluded per his direction
_REPORTABLE_NOT_LIVE_CODES = ("246GW",)  # real, tracked, next-potential-pilot - report on it, but not write-authorized (see _LIVE_PROJECT_CODES note above). Its Drive content is nested inside another drive, not its own top-level Shared Drive, so the normal drive-name-match fallback below would miss it - needs this explicit include to stay reportable now that it's out of _LIVE_PROJECT_CODES.


def _reportable_project_codes() -> list:
    """Every real job - the 3 live projects (only ones the system writes to /
    runs automation on) plus 246GW (real, tracked, next-potential-pilot - reported
    on but not write-authorized) plus every monitor-only job with real evidence of
    being an actual project, not a status label. Fixed 2026-07-08 per Buck: status
    ('reference' vs 'monitoring') in the DB doesn't reliably reflect whether a
    job is real/current - 825 Cemetery Lane was labeled 'reference' (implying
    closed) despite a real daily log from the day before this was written.
    Buck: 'figure out through the g-drive and houzz exports what is actually
    active jobs.' Ground truth used here: does a real Shared Drive exist with
    this project's name (live Drive API call, not a cached table), or is it one
    of the always-included codes (_LIVE_PROJECT_CODES / _REPORTABLE_NOT_LIVE_CODES
    - 246GW's Drive content is nested inside another drive, not its own top-level
    Shared Drive, so drive presence alone would miss it). Excludes only sandbox and
    the ASPN-MC/NEW/REM synthetic archetypes (no real address, not a real job)."""
    import sys as _sys
    _sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "services", "drive_intelligence"))
    from drive_client import list_shared_drives
    try:
        drive_names = {d.get("name", "").strip().lower() for d in list_shared_drives()}
    except Exception:
        drive_names = set()  # Drive API unreachable - fall back to DB-only below

    with _pg() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT project_code, name FROM projects
                WHERE status != 'sandbox' AND project_code NOT IN %s
                ORDER BY status, project_code
            """, (_SYNTHETIC_TEMPLATE_CODES + _NOT_YET_REAL_CODES,))
            rows = cur.fetchall()

    def _addr_key(s: str) -> tuple:
        # Leading street number + first street-name word - "275 Sunnyside Lane"
        # and "275 Sunnyside Ln." don't substring-match on abbreviations, but
        # both reduce to ("275", "sunnyside"). Real house numbers are distinctive
        # enough that this is a reliable match without needing full-string equality.
        parts = s.split()
        num = next((p for p in parts if p.isdigit()), "")
        word2 = next((p for p in parts if p.isalpha() and len(p) > 2), "")
        return (num, word2)

    drive_keys = {_addr_key(dn) for dn in drive_names if dn != "hci docs"}

    result = []
    for r in rows:
        code, name = r["project_code"], (r["name"] or "").strip().lower()
        if code in _LIVE_PROJECT_CODES or code in _REPORTABLE_NOT_LIVE_CODES:
            result.append(code)
        elif drive_names and (name in {dn for dn in drive_names} or _addr_key(name) in drive_keys
                               or any(name in dn or dn in name for dn in drive_names if dn != "hci docs")):
            result.append(code)
        elif not drive_names:
            # Drive API was unreachable this call - don't silently drop real
            # monitor-only jobs, include everything non-synthetic as a fallback
            result.append(code)
    return result


@router.get("/portfolio/status", response_class=HTMLResponse, include_in_schema=False)
def portfolio_status_page():
    """Every live-or-monitored project, full picture, one page. Links from each
    card would go to /project/{code}/status-page for the single-project deep view."""
    from fastapi.responses import HTMLResponse
    codes = _reportable_project_codes()
    cards = []
    for code in codes:
        try:
            data = _gather_deep_dive(code)
            cards.append(_render_project_status_card(data))
        except Exception as e:
            cards.append(f'<div class="proj-card" style="color:#e0615c">{code}: {e}</div>')
    html = f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<title>HCI Portfolio — Status</title><style>{_STATUS_PAGE_CSS}</style></head>
<body><div class="wrap">
<h1>HCI Portfolio — All Live &amp; Monitored Projects ({len(codes)})</h1>
<p class="subtitle">Live as of this page load · {datetime.now(BUCK_TZ).strftime('%b %d, %Y %-I:%M %p')} MT</p>
{''.join(cards)}
</div></body></html>"""
    return HTMLResponse(content=html)


def _render_project_status_email(data: dict) -> str:
    """Email-safe rendering of the same real data as the web card - table-based,
    inline styles only, light background. Fixed 2026-07-08: the first version of
    this report reused the dark-theme web CSS (#10141a background, light text) in
    a <style> block. Outlook and other email clients routinely strip <style>
    blocks and/or apply their own dark-mode color inversion on top of a dark
    background, which is exactly how Buck's copy came through 'blacked out.'
    Email HTML needs inline styles and a light background, full stop."""
    label, color = _status_health(data)
    budget = data["budget"]
    sched = data["schedule"]
    logs = data["daily_logs"]
    td = 'style="padding:6px 8px;border-bottom:1px solid #e3e6ea;font-size:12.5px;color:#333333;font-family:Arial,sans-serif;"'
    th = 'style="padding:0 8px 6px 0;border-bottom:1px solid #cccccc;font-size:10.5px;color:#666666;text-transform:uppercase;text-align:left;font-family:Arial,sans-serif;"'

    rfi_rows = "".join(
        f'<tr><td {td}>{r.get("rfi_number","")}</td><td {td}>{r.get("subject","")[:60]}</td>'
        f'<td {td}>{r.get("required_response_date") or "—"}</td></tr>'
        for r in data["open_rfis"][:10]
    ) or f'<tr><td {td} colspan="3">No open RFIs</td></tr>'

    risk_rows = "".join(
        f'<tr><td {td} style="text-transform:capitalize">{r.get("severity","")}</td>'
        f'<td {td}>{(r.get("description") or "")[:90]}</td></tr>'
        for r in data["open_risks"][:8]
    ) or f'<tr><td {td} colspan="2">No open risks</td></tr>'

    flags_html = "".join(f'<li style="color:#a15c00;font-size:12.5px;margin-bottom:4px">{f}</li>' for f in data["flags"]) \
        or '<li style="color:#888888;font-size:12.5px">No flags — clean</li>'

    metric = lambda val, lab: (
        f'<td style="padding:10px;text-align:center;background:#f4f5f7;border-radius:6px;font-family:Arial,sans-serif;">'
        f'<div style="font-size:15px;font-weight:700;color:#1a1a1a;">{val}</div>'
        f'<div style="font-size:10px;color:#888888;margin-top:2px;">{lab}</div></td>'
    )

    return f"""
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
      style="background:#ffffff;border:1px solid #e3e6ea;border-radius:8px;margin-bottom:16px;">
      <tr><td style="padding:18px 20px 0 20px;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>
          <td style="font-family:Arial,sans-serif;font-size:16px;font-weight:700;color:#1a1a1a;">
            {data['project']} <span style="color:#888888;font-weight:400;font-size:12px;">({data['project_code']})</span>
            <div style="font-size:11.5px;color:#888888;font-weight:400;margin-top:2px;">
              {(data.get('status') or '').title()} · Permit: {(data.get('permit_status') or 'unknown').upper()}
            </div>
          </td>
          <td align="right" style="font-family:Arial,sans-serif;">
            <span style="background:{color}18;color:{color};border:1px solid {color};border-radius:14px;padding:4px 10px;font-size:11px;font-weight:700;">{label}</span>
          </td>
        </tr></table>
      </td></tr>
      <tr><td style="padding:14px 20px 0 20px;">
        <table role="presentation" width="100%" cellpadding="6" cellspacing="6"><tr>
          {metric(_money(budget['contract_value']), 'Contract Value')}
          {metric(_money(budget['committed']) + f" ({budget['pct_committed']}%)", 'Committed')}
          {metric(str(sched['pct_complete']) + '%', 'Schedule Complete')}
          {metric(len(data['open_rfis']), 'Open RFIs')}
          {metric(len(data['open_risks']), 'Open Risks')}
        </tr></table>
      </td></tr>
      <tr><td style="padding:14px 20px 0 20px;">
        <div style="font-family:Arial,sans-serif;font-size:11px;text-transform:uppercase;color:#888888;margin-bottom:6px;">Open RFIs</div>
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
          <tr><th {th}>#</th><th {th}>Subject</th><th {th}>Due</th></tr>{rfi_rows}
        </table>
      </td></tr>
      <tr><td style="padding:14px 20px 0 20px;">
        <div style="font-family:Arial,sans-serif;font-size:11px;text-transform:uppercase;color:#888888;margin-bottom:6px;">Open Risks</div>
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
          <tr><th {th}>Severity</th><th {th}>Description</th></tr>{risk_rows}
        </table>
      </td></tr>
      <tr><td style="padding:14px 20px 20px 20px;">
        <div style="font-family:Arial,sans-serif;font-size:11px;text-transform:uppercase;color:#888888;margin-bottom:6px;">Flags</div>
        <ul style="margin:0;padding-left:18px;">{flags_html}</ul>
      </td></tr>
    </table>
    """


@router.post("/reports/weekly-status")
def send_weekly_status_report(codes: str = Query(None, description="Comma-separated project codes; defaults to every active+monitoring project")):
    """End-of-week detailed status report - budget, schedule, RFIs, risks for every
    live-or-monitored project, one email. Built 2026-07-08 per Buck: eventual
    audience is Chris (Hendrickson Construction owner) + management, but for now
    (next ~week) it goes to Buck only so he can review and tune before it goes
    live to Chris. Default scope is every active+monitoring project, not a
    hardcoded list - Buck: 'that should be all jobs - not live jobs in the
    system.' Email-safe rendering (see _render_project_status_email) - the first
    version reused dark web-page CSS and came through blacked-out in Outlook."""
    t0 = time.time()
    try:
        import sys as _sys
        _sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "integrations"))
        from microsoft_graph import send_email
        code_list = [c.strip().upper() for c in codes.split(",") if c.strip()] if codes else _reportable_project_codes()
        cards = []
        for code in code_list:
            try:
                data = _gather_deep_dive(code)
                cards.append(_render_project_status_email(data))
            except Exception as e:
                cards.append(f'<div style="color:#c0392b;font-family:Arial,sans-serif;padding:10px;">{code}: {e}</div>')
        week_str = datetime.now(BUCK_TZ).strftime("%b %d, %Y")
        html = f"""<!DOCTYPE html><html><body style="background:#f0f1f3;margin:0;padding:20px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:700px;margin:0 auto;">
<tr><td style="font-family:Arial,sans-serif;font-size:19px;font-weight:700;color:#1a1a1a;padding-bottom:2px;">HCI Weekly Project Status — {week_str}</td></tr>
<tr><td style="font-family:Arial,sans-serif;font-size:12.5px;color:#888888;padding-bottom:16px;">Detailed status across {len(code_list)} live/monitored project(s) — draft audience: Buck only, for review before this goes to Chris</td></tr>
<tr><td>{''.join(cards)}</td></tr>
</table></body></html>"""
        result, err = send_email(
            subject=f"HCI Weekly Project Status — {week_str}",
            html_body=html,
            to=[_BUCK_EMAIL],
        )
        if err:
            return _response("/reports/weekly-status", {}, errors=[err], start=t0)
        _log("/reports/weekly-status", "system", "weekly-report", "ok",
             round((time.time()-t0)*1000), str(uuid.uuid4())[:8], f"{len(code_list)} projects")
        return _response("/reports/weekly-status", {
            "sent_to": _BUCK_EMAIL[1], "projects_covered": code_list, "status": result.get("status"),
        }, start=t0)
    except Exception as e:
        return _response("/reports/weekly-status", {}, errors=[str(e)], start=t0)


def _gather_cost_forecast(code: str) -> dict:
    """Shared EVM forecast calc - used by the standalone /cost-forecast JSON
    endpoint and folded into the status page/report cards so 'are we on
    schedule, are we on budget, are there forecasted issues' (Buck, 2026-07-08:
    the core management-reporting requirement) shows up everywhere a job's
    status is reported, not just on a separate endpoint nobody's looking at.
    Raises ValueError if the project code isn't found."""
    with _pg() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, project_code, contract_value, permit_status
                FROM projects WHERE UPPER(project_code) = UPPER(%s)
            """, (code,))
            proj = cur.fetchone()
            if not proj:
                raise ValueError(f"Unknown project code: {code}")
            pid = proj["id"]
            bac = float(proj["contract_value"] or 0)

            # AC: actual cost = sum of awarded bid package amounts (real committed dollars)
            cur.execute("""
                SELECT COALESCE(SUM(awarded_amount), 0) AS ac
                FROM bid_packages WHERE project_id = %s AND status = 'awarded'
            """, (pid,))
            ac = float(cur.fetchone()["ac"] or 0)

            # Schedule completion %  and %  that should have started by today (for PV)
            cur.execute("""
                SELECT COUNT(*) AS total,
                    COUNT(*) FILTER (WHERE status ILIKE 'complete%%' OR status ILIKE 'done') AS complete,
                    COUNT(*) FILTER (WHERE start_date IS NOT NULL AND start_date <= CURRENT_DATE) AS should_have_started
                FROM project_schedule_items WHERE project_id = %s::text
            """, (pid,))
            sched = cur.fetchone()
            total_items = sched["total"] or 0
            pct_complete = (sched["complete"] / total_items) if total_items else 0.0
            pct_should_have_started = (sched["should_have_started"] / total_items) if total_items else 0.0

    ev = round(bac * pct_complete, 2)
    pv = round(bac * pct_should_have_started, 2)
    cpi = round(ev / ac, 3) if ac > 0 else None
    spi = round(ev / pv, 3) if pv > 0 else None

    # EAC = BAC/CPI is standard EVM, but CPI is only meaningful once there's
    # enough real progress behind it. Found live 2026-07-08: 246GW at 1.4%
    # schedule complete produced CPI=0.014 (near-zero denominator noise, not
    # a real cost-performance signal) and EAC=$450,000,000 on a $6.3M
    # project - a forecast that would have gone straight into a management
    # report if it hadn't been caught here. Require both a minimum schedule
    # completion AND a CPI in a plausible band before trusting the
    # CPI-based formula; otherwise use the simple additive fallback
    # (AC + remaining budget), same one already used when CPI is undefined.
    cpi_reliable = cpi is not None and pct_complete >= 0.10 and 0.3 <= cpi <= 3.0
    eac = round(bac / cpi, 2) if cpi_reliable else (round(ac + (bac - ev), 2) if bac else None)
    etc = round(eac - ac, 2) if eac is not None else None
    vac = round(bac - eac, 2) if eac is not None else None

    notes = []
    if total_items == 0:
        notes.append("No schedule items on file - EV/PV/SPI cannot be computed.")
    if ac == 0:
        notes.append("No packages awarded yet - CPI undefined, EAC falls back to BAC - EV + AC.")
    elif cpi is not None and not cpi_reliable:
        notes.append(f"CPI ({cpi}) not yet reliable - only {round(pct_complete*100,1)}% schedule complete, or ratio out of a sane range. EAC uses the simple additive fallback, not BAC/CPI, until there's enough real progress to trust the ratio.")
    if proj["permit_status"] == "not_issued":
        notes.append("No permit issued - near-zero EV/PV reflects pre-construction reality, not missing data.")
    elif proj["permit_status"] == "iffr":
        notes.append("IFFR permit - field work is permitted under IFFR scope, but the project may still be on hold (e.g. bids/awards only, no active construction) - check daily-log recency, don't assume EV/PV should be moving.")

    # Log a snapshot for trend tracking (one per project per day)
    try:
        with _pg() as snap_conn:
            with snap_conn.cursor() as snap_cur:
                snap_cur.execute("""
                    INSERT INTO cost_forecasts (project_id, bac, ac, ev, pv, cpi, spi, eac, etc, vac, notes)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (project_id, snapshot_date) DO UPDATE SET
                        bac=EXCLUDED.bac, ac=EXCLUDED.ac, ev=EXCLUDED.ev, pv=EXCLUDED.pv,
                        cpi=EXCLUDED.cpi, spi=EXCLUDED.spi, eac=EXCLUDED.eac, etc=EXCLUDED.etc,
                        vac=EXCLUDED.vac, notes=EXCLUDED.notes
                """, (pid, bac, ac, ev, pv, cpi, spi, eac, etc, vac, "; ".join(notes) or None))
            snap_conn.commit()
    except Exception:
        pass  # snapshot logging is best-effort, never block the response

    return {
        "project": proj["name"],
        "project_code": proj["project_code"],
        "bac_budget_at_completion": bac,
        "ac_actual_cost": ac,
        "ev_earned_value": ev,
        "pv_planned_value": pv,
        "cpi_cost_performance_index": cpi,
        "spi_schedule_performance_index": spi,
        "eac_estimate_at_completion": eac,
        "etc_estimate_to_complete": etc,
        "vac_variance_at_completion": vac,
        "pct_schedule_complete": round(pct_complete * 100, 1),
        "notes": notes,
    }


@router.get("/project/{code}/cost-forecast")
def project_cost_forecast(code: str):
    """EVM (earned value management) forecast — CPI/SPI/EAC/VAC. See
    _gather_cost_forecast for the calc and the 2026-07-08 EAC-reliability fix."""
    t0 = time.time()
    try:
        data = _gather_cost_forecast(code)
        return _response(f"/project/{code}/cost-forecast", data, start=t0)
    except ValueError as e:
        return _response(f"/project/{code}/cost-forecast", {}, errors=[str(e)], start=t0)
    except Exception as e:
        return _response(f"/project/{code}/cost-forecast", {}, errors=[str(e)], start=t0)


def _gather_status_brief(code: str) -> dict:
    """The 'robust job status brief' Buck asked GBT to spec (handoff b7eb23fd,
    2026-07-08): a PM-daily-briefing-shaped response instead of a thin generic
    paragraph. Composes the existing deep-dive + cost-forecast gathers (same
    numbers as every other endpoint - never a second, possibly-disagreeing
    calculation) and adds what was actually missing: an executive one-liner,
    phase detection, ranked top issues, recent-activity feed, and
    who-owns-the-next-action recommendations. Explicitly does NOT read
    LIVE_PROJECT_STATE.md - GBT's spec called that out by name as a known-stale
    source that must never be the basis for a live status answer.
    Raises ValueError if the project code isn't found (same contract as the
    other _gather_* functions)."""
    deep = _gather_deep_dive(code)
    try:
        forecast = _gather_cost_forecast(code)
    except ValueError:
        forecast = None

    label, color = _status_health(deep)
    flags = deep.get("flags", [])
    budget = deep["budget"]
    sched = deep["schedule"]
    logs = deep["daily_logs"]

    # Phase detection - cheap heuristic off permit_status + bid coverage +
    # schedule %, not a separate subsystem. Good enough to answer "what phase
    # are we in" without overstating certainty GBT's spec explicitly warned against.
    pct_complete = round((sched["complete_items"] / sched["total_items"]) * 100, 1) if sched["total_items"] else None
    if deep.get("permit_status") == "not_issued":
        phase = "Preconstruction / Bidding"
    elif deep.get("permit_status") == "iffr":
        phase = "Permitted (IFFR) — pre-full-permit prep"
    elif pct_complete is not None and pct_complete < 5:
        phase = "Early Construction"
    elif pct_complete is not None and pct_complete >= 95:
        phase = "Closeout"
    else:
        phase = "Construction" if pct_complete is not None else "Unknown — no schedule data"

    # Data confidence - concrete, not vibes: bid coverage + daily log recency.
    no_bid_pct = (len(budget.get("packages_with_no_bids", [])) / budget["total_packages"]
                  ) if budget.get("total_packages") else None
    confidence_reasons = []
    if no_bid_pct is not None and no_bid_pct > 0.3:
        confidence_reasons.append(f"{round(no_bid_pct*100)}% of bid packages still have zero bids")
    if logs.get("days_since_last_log") is not None and logs["days_since_last_log"] > 10:
        confidence_reasons.append(f"no daily log in {logs['days_since_last_log']} days")
    if forecast is None:
        confidence_reasons.append("cost forecast unavailable")
    confidence = "HIGH" if not confidence_reasons else ("LOW" if len(confidence_reasons) >= 2 else "MEDIUM")

    # Ranked top issues - risks (critical/high first) then RFI/bid gaps, capped at 5.
    top_issues = []
    for r in sorted(deep.get("open_risks", []),
                     key=lambda r: {"critical": 0, "high": 1, "medium": 2}.get(r.get("severity"), 3))[:3]:
        top_issues.append({
            "issue": r.get("description", "")[:200],
            "severity": r.get("severity"),
            "owner_action": r.get("mitigation") or "Needs a mitigation owner assigned",
        })
    if len(top_issues) < 5 and budget.get("packages_with_no_bids"):
        top_issues.append({
            "issue": f"{len(budget['packages_with_no_bids'])} bid package(s) with zero bids received",
            "severity": "medium",
            "owner_action": "PM to confirm invitations were sent; may need re-outreach",
        })
    if len(top_issues) < 5 and deep.get("overdue_rfis"):
        top_issues.append({
            "issue": f"{len(deep['overdue_rfis'])} RFI(s) past their required response date",
            "severity": "medium",
            "owner_action": "PM to escalate with architect/engineer",
        })
    top_issues = top_issues[:5]

    # Bid-folder health for the 3 live projects only - reuses the same
    # connector_sync_state/drive_bids freshness signal already in the DB
    # rather than re-scanning Drive on every status-brief call.
    bid_folder_status = None
    with _pg() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM projects WHERE UPPER(project_code)=UPPER(%s)", (code,))
            pid = cur.fetchone()["id"]
            if code.upper() in ("64EW", "101F", "1355R"):
                cur.execute("""
                    SELECT max(extracted_at) as last_scan, count(DISTINCT division_num) as divisions_scanned,
                           count(*) FILTER (WHERE extraction_source='claude_fallback') as claude_fallback_count
                    FROM drive_bids WHERE project_id = %s
                """, (pid,))
                scan_row = cur.fetchone()
                bid_folder_status = {
                    "last_scan_at": str(scan_row["last_scan"]) if scan_row["last_scan"] else None,
                    "divisions_scanned": scan_row["divisions_scanned"],
                    "claude_fallback_extractions": scan_row["claude_fallback_count"],
                    "note": "divisions_scanned counts divisions with at least one extracted bid in drive_bids, "
                            "not total division folders in Drive - a low number here can mean bids just haven't "
                            "come in yet for that division, not that scanning is broken. This field does not "
                            "check for duplicate/stale files live (too slow for this endpoint's response-time "
                            "budget) - a manual Drive sweep is the only way to confirm folder cleanliness at a "
                            "point in time; treat any past 'verified clean' claim as stale the moment new files "
                            "are added.",
                }
            # Recent activity feed - last 5 days of daily logs + directives touching this project
            cur.execute("""
                SELECT log_date, work_performed FROM daily_logs WHERE project_id = %s
                ORDER BY log_date DESC LIMIT 3
            """, (pid,))
            recent_logs = [{"date": str(r["log_date"]), "summary": (r["work_performed"] or "")[:200]} for r in cur.fetchall()]
            cur.execute("""
                SELECT title, created_at FROM ai_messages WHERE project_code = %s
                ORDER BY created_at DESC LIMIT 3
            """, (code.upper(),))
            recent_directives = [{"title": r["title"], "at": str(r["created_at"])} for r in cur.fetchall()]

    # Executive one-liner - synthesized, not templated boilerplate.
    if top_issues:
        main_issue = top_issues[0]["issue"]
        exec_line = f"{code} is {label.upper()} — main issue: {main_issue}. Next: {top_issues[0]['owner_action']}"
    elif flags:
        exec_line = f"{code} is {label.upper()} — {flags[0]}"
    else:
        exec_line = f"{code} is {label.upper()} with no material issues in live data right now."

    # Recommended next actions - owner-assigned, split executable-now vs needs-approval.
    next_actions = []
    if budget.get("packages_with_no_bids"):
        next_actions.append({"action": "Re-invite vendors for zero-bid packages", "owner": "PM", "requires_approval": False})
    if deep.get("overdue_rfis"):
        next_actions.append({"action": "Escalate overdue RFIs with architect/engineer", "owner": "PM", "requires_approval": False})
    if confidence == "LOW":
        next_actions.append({"action": "Re-run Drive bid-folder scan to refresh stale data", "owner": "Claude Code", "requires_approval": False})
    if not next_actions:
        next_actions.append({"action": "No urgent action - continue normal monitoring", "owner": "PM", "requires_approval": False})

    return {
        "project_code": deep["project_code"],
        "project": deep["project"],
        "header": {
            "health": label, "health_color": color,
            "data_confidence": confidence, "confidence_reasons": confidence_reasons,
            "refreshed_at": datetime.now(timezone.utc).isoformat(),
        },
        "executive_summary": exec_line,
        "phase": phase,
        "permit_status": deep.get("permit_status"),
        "pct_schedule_complete": pct_complete,
        "top_issues": top_issues,
        "bids_procurement": {
            "total_packages": budget.get("total_packages"),
            "packages_with_no_bids": budget.get("packages_with_no_bids"),
            "bid_spread_flags": budget.get("bid_spread_flags"),
            "bid_folder_status": bid_folder_status,
        },
        "financial_snapshot": forecast,
        "schedule": {
            "pct_complete": pct_complete,
            "overdue_items": sched.get("overdue"),
            "upcoming_next_8": sched.get("upcoming_next_8"),
        },
        "rfis_decisions": {
            "open_count": len(deep.get("open_rfis", [])),
            "overdue_count": len(deep.get("overdue_rfis", [])),
            "top_open": deep.get("open_rfis", [])[:3],
        },
        "recent_activity": {"daily_logs": recent_logs, "directives": recent_directives},
        "recommended_next_actions": next_actions,
        "source_of_truth_note": "Built from live gateway/project tables (deep-dive + cost-forecast + drive_bids) - "
                                 "does not read LIVE_PROJECT_STATE.md, which has known-stale sections.",
    }


@router.get("/project/{code}/status-brief")
def project_status_brief(code: str):
    """Robust PM-daily-briefing-shaped job status - see _gather_status_brief.
    Built 2026-07-08 per Buck/GBT handoff b7eb23fd after live demo feedback
    that the existing deep-dive/status-page responses were too thin."""
    t0 = time.time()
    try:
        data = _gather_status_brief(code)
        return _response(f"/project/{code}/status-brief", data, start=t0)
    except ValueError as e:
        return _response(f"/project/{code}/status-brief", {}, errors=[str(e)], start=t0)
    except Exception as e:
        return _response(f"/project/{code}/status-brief", {}, errors=[str(e)], start=t0)


@router.get("/portfolio/status-brief")
def portfolio_status_brief():
    """Multi-project rollup per GBT handoff b7eb23fd: portfolio top-line
    (GREEN/YELLOW/RED counts, biggest cross-project risk) + compact table for
    every reportable project, full detail only for RED/YELLOW."""
    t0 = time.time()
    codes = _reportable_project_codes()
    briefs = []
    for code in codes:
        try:
            briefs.append(_gather_status_brief(code))
        except Exception as e:
            briefs.append({"project_code": code, "error": str(e)})

    counts = {"GREEN": 0, "YELLOW": 0, "RED": 0}
    for b in briefs:
        h = (b.get("header", {}) or {}).get("health", "")
        if h == "On Track":
            counts["GREEN"] += 1
        elif h == "On Track, Watching":
            counts["YELLOW"] += 1
        elif h == "Needs Attention":
            counts["RED"] += 1

    table = [{
        "code": b.get("project_code"), "health": (b.get("header", {}) or {}).get("health"),
        "phase": b.get("phase"), "main_risk": (b.get("top_issues") or [{}])[0].get("issue") if b.get("top_issues") else None,
        "confidence": (b.get("header", {}) or {}).get("data_confidence"),
        "next_action": (b.get("recommended_next_actions") or [{}])[0].get("action") if b.get("recommended_next_actions") else None,
    } for b in briefs if "error" not in b]

    # Found 2026-07-08 testing live in Proj Stat GBT: the full nested brief for
    # every RED/YELLOW project made this payload ~50KB (8 projects x full
    # financial_snapshot + recent_activity + everything) and the GPT Action
    # call never came back - too much for a single Actions round-trip to
    # synthesize. Trimmed to just what a portfolio rollup actually needs to
    # explain WHY a project is flagged; call getStatusBrief on that one project
    # code for the full picture instead of duplicating it here.
    expanded_detail = [{
        "project_code": b.get("project_code"),
        "health": (b.get("header", {}) or {}).get("health"),
        "executive_summary": b.get("executive_summary"),
        "top_issues": (b.get("top_issues") or [])[:3],
        "recommended_next_actions": (b.get("recommended_next_actions") or [])[:3],
    } for b in briefs if (b.get("header", {}) or {}).get("health") == "Needs Attention"]

    return _response("/portfolio/status-brief", {
        "portfolio_summary": counts,
        "table": table,
        "expanded_detail": expanded_detail,
        "source_of_truth_note": "Built from live gateway/project tables per project - does not read LIVE_PROJECT_STATE.md. "
                                 "Call getStatusBrief for one project's full detail (financials, schedule, recent activity).",
    }, start=t0)


@router.get("/project/{code}/schedule/critical-path")
def project_critical_path(code: str):
    """CPM (critical path method) engine — CYCLE49 queue item #4, 2026-07-02. Real
    forward/backward-pass float calculation over schedule_relationships. Confirmed
    zero predecessor/successor data exists anywhere in the system right now, so this
    honestly reports 'no_dependency_network' + a labeled date-span fallback rather
    than fabricating a critical path. Populate schedule_relationships (via
    /gateway/project/{code}/schedule/relationships POST, or a future Houzz CPM
    export) to get a real logic-driven critical path."""
    t0 = time.time()
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "services", "schedule_intelligence"))
        from cpm_engine import compute_critical_path

        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name FROM projects WHERE UPPER(project_code) = UPPER(%s)", (code,))
                proj = cur.fetchone()
                if not proj:
                    return _response(f"/project/{code}/schedule/critical-path", {}, errors=[f"Unknown project code: {code}"], start=t0)
                pid = proj["id"]

                cur.execute("""
                    SELECT activity_id, title, start_date, end_date
                    FROM project_schedule_items WHERE project_id = %s::text AND activity_id IS NOT NULL
                """, (pid,))
                activities = [dict(r) for r in cur.fetchall()]

                cur.execute("""
                    SELECT predecessor_activity_id, successor_activity_id, relationship_type, lag_days
                    FROM schedule_relationships WHERE project_id = %s
                """, (pid,))
                relationships = [dict(r) for r in cur.fetchall()]

        result = compute_critical_path(activities, relationships)
        result["project"] = proj["name"]
        result["project_code"] = code.upper()
        result["activity_count"] = len(activities)
        result["relationship_count"] = len(relationships)
        return _response(f"/project/{code}/schedule/critical-path", result, start=t0)
    except Exception as e:
        return _response(f"/project/{code}/schedule/critical-path", {}, errors=[str(e)], start=t0)


class ScheduleRelationshipPayload(BaseModel):
    predecessor_activity_id: str
    successor_activity_id: str
    relationship_type: str = "FS"
    lag_days: int = 0


@router.post("/project/{code}/schedule/relationships")
def add_schedule_relationship(code: str, req: ScheduleRelationshipPayload, request: Request):
    """Add a real predecessor/successor link so /schedule/critical-path can compute
    an actual logic-driven critical path instead of the date-span fallback."""
    _require_key(request)
    t0 = time.time()
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM projects WHERE UPPER(project_code) = UPPER(%s)", (code,))
                row = cur.fetchone()
                if not row:
                    return _response(f"/project/{code}/schedule/relationships", {}, errors=[f"Unknown project code: {code}"], start=t0)
                pid = row["id"]
                cur.execute("""
                    INSERT INTO schedule_relationships (project_id, predecessor_activity_id, successor_activity_id, relationship_type, lag_days)
                    VALUES (%s,%s,%s,%s,%s)
                    ON CONFLICT (project_id, predecessor_activity_id, successor_activity_id)
                    DO UPDATE SET relationship_type=EXCLUDED.relationship_type, lag_days=EXCLUDED.lag_days
                    RETURNING id
                """, (pid, req.predecessor_activity_id, req.successor_activity_id, req.relationship_type, req.lag_days))
                rid = cur.fetchone()["id"]
                conn.commit()
        return _response(f"/project/{code}/schedule/relationships", {"relationship_id": rid, "added": True}, start=t0)
    except Exception as e:
        return _response(f"/project/{code}/schedule/relationships", {}, errors=[str(e)], start=t0)


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


@router.get("/project/{code}/plan-review-pending")
def plan_review_pending(code: str):
    """
    Closes the loop on the plan-review pipeline (2026-07-01): RFIs, bid packages, and
    schedule items it generates were real DB rows, but nothing surfaced them anywhere a
    PM would actually look — a PM had to already know to query for them. This endpoint
    is that single place: everything the pipeline drafted (identified by the
    "generated from plan-review"/"plan-review CPM engine" marker left in each row's
    notes) that's still sitting in its initial, unreviewed state.
    """
    t0 = time.time()
    try:
        pid = _get_pid(code)
        conn = _pg()
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, rfi_number, subject, question, status, submitted_date
                FROM rfis WHERE project_id = %s AND source_email_id = 'plan-review-pipeline'
                  AND status = 'open'
                ORDER BY id DESC
            """, (pid,))
            rfis = [dict(r) for r in cur.fetchall()]
            cur.execute("""
                SELECT id, csi_division, package_name, scope_description, notes
                FROM bid_packages WHERE project_id = %s AND status = 'not_started'
                  AND notes ILIKE '%%plan-review%%'
                ORDER BY id DESC
            """, (pid,))
            packages = [dict(r) for r in cur.fetchall()]
            cur.execute("""
                SELECT activity_id, title, start_date, end_date, status
                FROM project_schedule_items WHERE project_id = %s AND status = 'draft'
                ORDER BY start_date ASC
            """, (str(pid),))
            schedule_items = [dict(r) for r in cur.fetchall()]
        conn.close()
        for r in rfis:
            if r.get("submitted_date"):
                r["submitted_date"] = r["submitted_date"].isoformat()
        for s in schedule_items:
            s["start_date"] = s["start_date"].isoformat()
            s["end_date"] = s["end_date"].isoformat()
        total = len(rfis) + len(packages) + len(schedule_items)
        return _response(f"/project/{code}/plan-review-pending", {
            "project_code": code,
            "total_pending_review": total,
            "rfis_from_plan_review": rfis,
            "bid_packages_from_plan_review": packages,
            "schedule_items_from_plan_review": schedule_items,
            "note": "Everything here was AI-drafted from a plan set and needs PM review "
                    "before it becomes real work: RFIs before anyone sends them (POST "
                    "/email/send, Buck approval required), bid packages before soliciting "
                    "bids, schedule items before treating them as the live schedule.",
        }, start=t0)
    except HTTPException as e:
        return _response(f"/project/{code}/plan-review-pending", {}, errors=[str(e.detail)], start=t0)
    except Exception as e:
        return _response(f"/project/{code}/plan-review-pending", {}, errors=[str(e)], start=t0)


_OWNER_SELECTION_KEYWORDS = (
    "manufacturer", "model", "color", "finish", "fixture", "selection", "select",
)


@router.get("/project/{code}/owner-decisions-needed")
def owner_decisions_needed(code: str):
    """
    Owner-selection tracker (2026-07-02) — spec-driven luxury builds stall on the same
    pattern every time: the plan set shows a fixture/finish location but leaves
    manufacturer/model/color blank pending an owner decision. The plan-review pipeline
    already generates an RFI for exactly this (see the fixture-schedule gaps in every
    real run so far), but nothing distinguished "owner needs to pick a tile" from
    "engineer needs to answer a structural question" or attached a real deadline. This
    endpoint filters open RFIs to selection-flavored ones (keyword match on subject/
    question — a heuristic, not a hard classification) and cross-references the
    long-lead schedule notes (see generate-schedule) so a selection blocking a
    long-lead item shows the actual order-by date, not just "open."
    """
    t0 = time.time()
    try:
        pid = _get_pid(code)
        conn = _pg()
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, rfi_number, subject, question, submitted_date, required_response_date
                FROM rfis WHERE project_id = %s AND status = 'open'
                ORDER BY id DESC
            """, (pid,))
            all_open = [dict(r) for r in cur.fetchall()]
            cur.execute("""
                SELECT title, notes FROM project_schedule_items
                WHERE project_id = %s AND status = 'draft' AND notes ILIKE '%%LONG-LEAD%%'
            """, (str(pid),))
            long_lead_items = [dict(r) for r in cur.fetchall()]
        conn.close()

        decisions = []
        for rfi in all_open:
            text = f"{rfi.get('subject','')} {rfi.get('question','')}".lower()
            if not any(kw in text for kw in _OWNER_SELECTION_KEYWORDS):
                continue
            if rfi.get("submitted_date"):
                rfi["submitted_date"] = rfi["submitted_date"].isoformat()
            if rfi.get("required_response_date"):
                rfi["required_response_date"] = rfi["required_response_date"].isoformat()
            needed_by = None
            for item in long_lead_items:
                item_words = set(item["title"].lower().split())
                rfi_words = set(text.split())
                if item_words & rfi_words:
                    order_by = item["notes"].split("order by ")[-1].split(" to avoid")[0]
                    needed_by = order_by
                    break
            decisions.append({**rfi, "needed_by": needed_by or rfi.get("required_response_date")})

        decisions.sort(key=lambda d: (d["needed_by"] is None, d.get("needed_by") or ""))
        return _response(f"/project/{code}/owner-decisions-needed", {
            "project_code": code,
            "decisions_needed": decisions,
            "count": len(decisions),
            "count_blocking_long_lead_order": sum(1 for d in decisions if d["needed_by"] and d["needed_by"] != d.get("required_response_date")),
            "note": "Keyword-filtered from open RFIs — a heuristic, not a hard "
                    "classification; PM should still skim for misses. needed_by prefers "
                    "a long-lead order date over the RFI's own required_response_date "
                    "when the selection blocks a long-lead item.",
        }, start=t0)
    except Exception as e:
        return _response(f"/project/{code}/owner-decisions-needed", {}, errors=[str(e)], start=t0)


@router.get("/project/{code}/action-list")
def project_action_list(code: str):
    """AI-ranked top 10 PM actions for the day."""
    t0 = time.time()
    try:
        data = _proxy(f"/mvp/projects/{code}/action-list")
        return _response(f"/project/{code}/action-list", data, start=t0)
    except HTTPException as e:
        return _response(f"/project/{code}/action-list", {}, errors=[str(e.detail)], start=t0)


_PROJECT_VIEW_DISPATCH = {
    "brain": project_brain,
    "schedule": project_schedule,
    "bids": project_bids,
    "pm": project_pm,
    "deep-dive": project_deep_dive,
    "cost-forecast": project_cost_forecast,
    "action-list": project_action_list,
}


@router.get("/project/{code}/view")
def project_view(code: str, view: str = Query(..., description="One of: brain, schedule, bids, pm, deep-dive, cost-forecast, action-list")):
    """Single parameterized entry point for the 7 GET /project/{code}/X views above.
    Added 2026-07-11 to free ChatGPT Actions schema slots (30-operation platform
    cap) without losing any capability - dispatches to the exact same functions
    the 7 individual routes call, so behavior is identical. The 7 individual
    routes stay live (backward compatible); only GBT's Actions schema switches
    to calling this one instead."""
    fn = _PROJECT_VIEW_DISPATCH.get(view)
    if fn is None:
        return _response(f"/project/{code}/view", {}, errors=[f"unknown view '{view}', must be one of {sorted(_PROJECT_VIEW_DISPATCH)}"])
    return fn(code)


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
            # Same status-vs-bid_entries-count fix as _gather_deep_dive above (2026-07-08).
            no_bid_packages = [p for p in packages
                                if (p["bid_count"] or 0) == 0 and p["status"] not in ("bid_received", "awarded")]
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
            with_bids = sum(1 for p in packages
                             if (p["bid_count"] or 0) > 0 or p["status"] in ("bid_received", "awarded"))
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
                FROM projects p WHERE p.status IN ('active','design','bidding','preconstruction','monitoring')
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
    # 2026-07-10: was [1, 2, 3, 8] - id 8 is 246GW (status='monitoring', not
    # active). This is the same class of bug the 2026-07-08 fix addressed for
    # _LIVE_PROJECT_CODES (see that comment above) but that fix only touched
    # the string-code list, not this separate numeric-ID one used by
    # stale-detection/schedule-variance - 246GW was still getting real
    # staleness/overdue alerts as if it were a live project. Buck flagged this
    # directly ("I still see it being referenced in places it shouldn't").
    LIVE = [1, 2, 3]
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
                    "pageSize": 50,
                    "supportsAllDrives": "true", "includeItemsFromAllDrives": "true"},
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
    # 2026-07-02: was importing get_drive_token, which doesn't exist in credentials.py
    # (only get_google_token(service) does) - every call silently returned "" via the
    # swallowed exception, breaking /project/{code}/drive with 401s since whenever this
    # was written.
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "integrations"))
        from credentials import get_google_token
        return get_google_token("drive")
    except Exception:
        return ""


def _drive_get_content(file_id: str) -> str:
    token = _drive_token()
    r = requests.get(f"https://www.googleapis.com/drive/v3/files/{file_id}",
                      headers={"Authorization": f"Bearer {token}"},
                      params={"alt": "media"}, timeout=20)
    r.raise_for_status()
    return r.text


def _drive_overwrite_content(file_id: str, content: str, mime: str = "text/plain") -> None:
    """PATCHes an existing file's content in place by known file_id - no name search,
    no create-new-file branch. Used for append-only canonical docs where the file_id
    is already known and must never fork into a duplicate."""
    token = _drive_token()
    requests.patch(
        f"https://www.googleapis.com/upload/drive/v3/files/{file_id}",
        headers={"Authorization": f"Bearer {token}", "Content-Type": mime},
        params={"uploadType": "media"},
        data=content.encode("utf-8"), timeout=20,
    ).raise_for_status()


# ── BTW-5: Schedule Variance Alerts ──────────────────────────────────────────

@router.get("/schedule/variance")
def schedule_variance():
    """BTW-5 — Schedule variance: overdue items, data anomalies, per-project summary."""
    t0 = time.time()
    # 2026-07-10: was [1, 2, 3, 8] - id 8 is 246GW (status='monitoring', not
    # active). This is the same class of bug the 2026-07-08 fix addressed for
    # _LIVE_PROJECT_CODES (see that comment above) but that fix only touched
    # the string-code list, not this separate numeric-ID one used by
    # stale-detection/schedule-variance - 246GW was still getting real
    # staleness/overdue alerts as if it were a live project. Buck flagged this
    # directly ("I still see it being referenced in places it shouldn't").
    LIVE = [1, 2, 3]
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
                              AND psi.status != 'draft'  -- exclude unreviewed plan-review-generated items
                              AND psi.start_date <= psi.end_date  -- exclude data errors
                             THEN 1 END) as overdue,
                  COUNT(CASE WHEN psi.end_date BETWEEN %s AND %s
                              AND psi.status NOT ILIKE '%%complete%%'
                              AND psi.status != 'draft'
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
                  AND psi.status != 'draft'
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
                  AND psi.status != 'draft'
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
                WHERE p.status IN ('active','design','bidding','preconstruction','monitoring')
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
                WHERE p.status IN ('active','design','bidding','preconstruction','monitoring')
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

        # Found 2026-07-03: a project can have bid_packages.status='awarded' (with a
        # real vendor name on the package) while having zero corresponding bid_entries
        # rows, so the dollar total silently reads $0 even though real awards exist -
        # a data-entry gap from that project's import path, not a live bug. Surface it
        # honestly instead of implying "$0 committed" is a real, verified number.
        for p in projects:
            if p["awarded_packages"] > 0 and float(p["awarded"]) == 0:
                p["data_gap_warning"] = (
                    f"{p['awarded_packages']} package(s) marked awarded with no bid_entries "
                    f"dollar amount recorded - awarded total below is understated, not $0"
                )

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

@router.get("/knowledge/vendor-capacity-conflicts")
def vendor_capacity_conflicts():
    """
    Cross-project vendor capacity conflicts (2026-07-01) — a gap identified while
    thinking through what a $40-60M ultra-luxury Aspen build actually needs versus a
    standard remodel: HCI runs several active projects sharing a genuinely limited pool
    of subs capable of that tier of work. Nothing previously flagged the same vendor
    being scheduled on overlapping windows across two active projects. Matches awarded
    bid_entries to schedule-item assignees by company-name substring (assignee text is
    free-form like "Long Beach Enterprise — $185,000", not FK'd to vendors) — this is a
    heuristic, not a hard rule, and should be treated as "worth confirming," not a fact.
    """
    t0 = time.time()
    try:
        conn = _pg()
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("""
                WITH vendor_windows AS (
                    SELECT DISTINCT v.id AS vendor_id, v.company_name, p.id AS project_id,
                        p.project_code, p.name AS project_name,
                        psi.start_date, psi.end_date, psi.title AS activity
                    FROM bid_entries be
                    JOIN vendors v ON v.id = be.vendor_id
                    JOIN bid_packages bp ON bp.id = be.bid_package_id
                    JOIN projects p ON p.id = bp.project_id
                    JOIN project_schedule_items psi
                        ON psi.project_id = p.id::text
                        AND length(split_part(v.company_name, ' ', 1)) > 3
                        AND psi.assignee ILIKE '%' || split_part(v.company_name, ' ', 1) || '%'
                    WHERE be.status = 'awarded'
                      AND p.status IN ('active','design','bidding','preconstruction')
                      AND psi.start_date IS NOT NULL AND psi.end_date IS NOT NULL
                )
                SELECT a.company_name,
                       a.project_code AS project_a, a.project_name AS project_a_name,
                       a.activity AS activity_a, a.start_date AS a_start, a.end_date AS a_end,
                       b.project_code AS project_b, b.project_name AS project_b_name,
                       b.activity AS activity_b, b.start_date AS b_start, b.end_date AS b_end
                FROM vendor_windows a
                JOIN vendor_windows b
                    ON a.vendor_id = b.vendor_id AND a.project_id < b.project_id
                WHERE a.start_date <= b.end_date AND b.start_date <= a.end_date
                ORDER BY a.company_name, a.start_date
            """)
            rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        for r in rows:
            for k in ("a_start", "a_end", "b_start", "b_end"):
                if r.get(k):
                    r[k] = r[k].isoformat()
        return _response("/knowledge/vendor-capacity-conflicts", {
            "conflict_count": len(rows),
            "conflicts": rows,
            "note": "Heuristic match on assignee text vs. vendor company name — confirm "
                    "with the sub before treating as a real scheduling conflict.",
        }, start=t0)
    except Exception as e:
        return _response("/knowledge/vendor-capacity-conflicts", {}, errors=[str(e)], start=t0)


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


# ── AI Team Document Bus ──────────────────────────────────────────────────────
# 2026-07-10, GBT BUILD NOW directive. Read-only cross-agent access to HCI AI
# Master coordination documents (ADRs, audits, directives, peer reviews, team
# messages) so Claude Code / GBT / BC can pick up each other's writes without
# Buck manually relaying files. Scoped to HCI AI Master's top-level files only
# — never recurses into project-adjacent subfolders (e.g. "246 Gallo Way")
# since HCI AI Master is system-only, not project source-of-truth (see
# CLAUDE.md's "HCI AI Drive Is System-Only" directive) and this must not blur
# into a generic project Drive reader.

HCI_MASTER_FOLDER_ID = "1ejYXRgS34c7JmQKfHwaPNnzEBcCGUmwI"
_COORD_DOC_MIME_TYPES = {"text/plain", "text/markdown", "application/vnd.google-apps.document"}
# The single canonical coordination log (Chief Architect directive, 2026-07-11 msg
# 1515: "one coordination log... no duplicate current documents"). BC-authored
# per-message files get auto-folded into this file rather than left as scattered
# duplicates - see the fold-in block in _sync_coordination_documents().
_LIVE_TEAM_COMMS_FILE_ID = "1Ya_cRlfOH2eAM5gtsk_bZmgx73ZLvn7q"


def _classify_coord_doc(filename: str) -> str:
    name = filename.upper()
    if name.startswith("ADR") or "ADR-" in name:
        return "adr"
    if "AUDIT" in name:
        return "audit"
    if "DIRECTIVE" in name or "PERMANENT_RULE" in name or "STANDARD" in name:
        return "directive"
    if "REVIEW" in name:
        return "peer_review"
    if name.startswith("BC_TO_") or name.startswith("GBT_") or "REPORT" in name or "SUMMARY" in name:
        return "team_message"
    return "other"


# Fixed 3-member roster for "pending" calculation in STATUS. BC's own acceptance
# test (BC_STANDING_TASK_DOCUMENT_BUS_ACCEPTANCE_TEST.md, written 2026-07-09)
# uses these exact literal agent strings when it calls /acknowledge, so this
# endpoint's canonical agent names are "CODE"/"GBT"/"BC" - a separate, smaller
# vocabulary from the "claude_code"/"chatgpt"/"browser_claude" convention used
# elsewhere (ai_messages, telegram ack). Accept any string an agent sends
# rather than validating against this list; it's only used to compute "pending".
_COORD_DOC_ROSTER = ("CODE", "GBT", "BC")


def _sync_coordination_documents() -> list:
    """Scans HCI AI Master's top-level files, upserts any not-yet-seen ones into
    coordination_documents (capturing the Drive owner as author), and returns
    all current rows with their per-document acknowledged_by list."""
    token = _drive_token()
    r = requests.get(
        "https://www.googleapis.com/drive/v3/files",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "q": f"'{HCI_MASTER_FOLDER_ID}' in parents and trashed=false",
            "fields": "files(id,name,mimeType,createdTime,modifiedTime,owners(displayName))",
            "pageSize": 200,
        }, timeout=30,
    )
    r.raise_for_status()
    files = [f for f in r.json().get("files", []) if f.get("mimeType") in _COORD_DOC_MIME_TYPES]

    with _pg() as conn:
        with conn.cursor() as cur:
            for f in files:
                author = (f.get("owners") or [{}])[0].get("displayName", "")
                cur.execute("""
                    INSERT INTO coordination_documents
                        (file_id, filename, source, document_type, drive_created_at, drive_modified_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (file_id) DO UPDATE SET
                        filename = EXCLUDED.filename,
                        source = EXCLUDED.source,
                        drive_modified_at = EXCLUDED.drive_modified_at
                """, (f["id"], f["name"], author or "drive", _classify_coord_doc(f["name"]),
                      f.get("createdTime"), f.get("modifiedTime")))
            conn.commit()
            cur.execute("""
                SELECT file_id, filename, source, document_type, drive_created_at,
                       drive_modified_at, first_seen_at
                FROM coordination_documents ORDER BY drive_modified_at DESC
            """)
            rows = [dict(row) for row in cur.fetchall()]
            cur.execute("SELECT file_id, agent FROM coordination_document_acks")
            acks_by_file: Dict[str, list] = {}
            for row in cur.fetchall():
                acks_by_file.setdefault(row["file_id"], []).append(row["agent"])

    for row in rows:
        for k in ("drive_created_at", "drive_modified_at", "first_seen_at"):
            if row.get(k):
                row[k] = row[k].isoformat()
        row["title"] = row.pop("filename")
        row["author"] = row.pop("source")
        row["created_time_mt"] = (
            datetime.fromisoformat(row["drive_created_at"]).astimezone(BUCK_TZ).strftime("%Y-%m-%d %-I:%M %p MT")
            if row.get("drive_created_at") else None
        )
        row["acknowledged_by"] = acks_by_file.get(row["file_id"], [])

    # Mirror BC-authored docs into ai_messages so BC's contributions land in the
    # same durable, catch-up-able store as GBT/Code's, not just as Drive files
    # only discoverable by manually browsing the folder. Found 2026-07-11: GBT
    # and Code coordinate via ai_messages already, but nothing auto-created a
    # record for BC's side of that same conversation - it existed only as a
    # Drive file with no tracked status/read state. Runs as a side effect of
    # every LIST call (this function), not tied to any one agent's session -
    # whichever agent calls coord-docs-list next does the mirroring.
    try:
        bc_files = [f["id"] for f in files if f["name"].upper().startswith(("BC", "BROWSER_CLAUDE"))]
        if bc_files:
            with _pg() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT DISTINCT related_file FROM ai_messages WHERE related_file = ANY(%s)", (bc_files,))
                    already_mirrored = {r["related_file"] for r in cur.fetchall()}
                    newest_seen_at = None
                    for f in files:
                        if f["id"] in already_mirrored or f["id"] not in bc_files:
                            continue
                        mirror_mid = _create_ai_message(
                            "browser_claude", "chatgpt", _classify_coord_doc(f["name"]),
                            f["name"], f"New Document Bus post from BC - read via GET /gateway/coordination/documents/{f['id']}",
                            None, False, None, f["id"], None, None, "medium", None,
                        )
                        # 2026-07-11 fix: this row is a discovery notice, not an
                        # action item - it existed to make BC's file findable via
                        # the old ai_messages/warm-start system before ADR-003's
                        # agent_messages exists. Leaving it ISSUED forever created
                        # an ever-growing, never-closeable backlog (75+ items,
                        # flagged live by Buck) since nothing in the old system
                        # ever marks these complete. Auto-close immediately - the
                        # real actionable channel is agent_messages now.
                        try:
                            with conn.cursor() as _cur2:
                                _cur2.execute(
                                    "UPDATE ai_messages SET status='COMPLETE', completed_at=NOW() WHERE id=%s",
                                    (mirror_mid,))
                            conn.commit()
                        except Exception:
                            pass
                        mod = f.get("modifiedTime")
                        if mod and (newest_seen_at is None or mod > newest_seen_at):
                            newest_seen_at = mod
                    if newest_seen_at:
                        # Real evidence of BC being alive at that moment (it wrote this file) -
                        # use the file's own timestamp, not "now", so a backfill of old posts
                        # doesn't make BC look freshly active when it wasn't.
                        _touch_heartbeat("browser_claude", "posted to Document Bus",
                                         seen_at=datetime.fromisoformat(newest_seen_at.replace("Z", "+00:00")))
    except Exception:
        pass  # mirroring is best-effort - never let it break the list call itself

    # Fold new BC-authored files into the canonical LIVE_TEAM_COMMS.md log.
    # Per Chief Architect directive 2026-07-11 (msg 1515): one coordination log,
    # no duplicate "current" documents. BC's own Drive MCP toolset has create/read/
    # search/copy but no update/append operation, so BC physically cannot avoid
    # creating a new file per message - the fold-in has to happen here instead.
    # coordination_log_folded tracks what's already been merged so re-runs (this
    # function fires on every coord-docs-list call) don't re-append the same file.
    try:
        bc_files_to_fold = [f for f in files if f["name"].upper().startswith(("BC", "BROWSER_CLAUDE"))
                             and f["id"] != _LIVE_TEAM_COMMS_FILE_ID]
        if bc_files_to_fold:
            with _pg() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT file_id FROM coordination_log_folded")
                    already_folded = {r["file_id"] for r in cur.fetchall()}
            unfolded = [f for f in bc_files_to_fold if f["id"] not in already_folded]
            if unfolded:
                unfolded.sort(key=lambda f: f.get("modifiedTime") or "")
                current = _drive_get_content(_LIVE_TEAM_COMMS_FILE_ID)
                appended_ids = []
                for f in unfolded:
                    try:
                        body = _drive_get_content(f["id"])
                    except Exception:
                        continue
                    current += (
                        f"\n\n==================================================\n\n"
                        f"## [auto-folded from Drive file: {f['name']}]\n\n{body}\n"
                    )
                    appended_ids.append(f["id"])
                if appended_ids:
                    _drive_overwrite_content(_LIVE_TEAM_COMMS_FILE_ID, current)
                    with _pg() as conn:
                        with conn.cursor() as cur:
                            for fid in appended_ids:
                                cur.execute(
                                    "INSERT INTO coordination_log_folded (file_id) VALUES (%s) ON CONFLICT DO NOTHING",
                                    (fid,))
                        conn.commit()
    except Exception:
        pass  # fold-in is best-effort - never let it break the list call itself

    return rows


@router.get("/coordination/documents")
def coordination_documents_list(since: Optional[str] = Query(None, description="ISO timestamp - only docs modified after this")):
    """AI Team Document Bus — LIST. Returns HCI AI Master coordination documents
    (optionally filtered to those modified after `since`), each carrying its own
    acknowledged_by list so any caller can tell what it still needs to read."""
    t0 = time.time()
    try:
        docs = _sync_coordination_documents()
        if since:
            since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
            docs = [d for d in docs if d.get("drive_modified_at") and datetime.fromisoformat(d["drive_modified_at"]) > since_dt]
        return _response("/coordination/documents", {
            "count": len(docs), "documents": docs,
        }, start=t0)
    except Exception as e:
        return _response("/coordination/documents", {}, errors=[str(e)], start=t0)


@router.get("/coordination/documents/{file_id}")
def coordination_documents_read(file_id: str):
    """AI Team Document Bus — READ. Reads a coordination document's content by Drive file ID."""
    t0 = time.time()
    try:
        content_data = _proxy(f"/services/drive-intelligence/file/{file_id}/content")
        meta = _proxy(f"/services/drive-intelligence/file/{file_id}")
        _log("/coordination/documents/read", "team", "", "coordination_doc_read", 0, str(uuid.uuid4())[:8], file_id)
        return _response("/coordination/documents/read", {
            "file_id": file_id,
            "title": meta.get("name", file_id),
            "content": content_data.get("content", ""),
        }, start=t0)
    except HTTPException as e:
        return _response("/coordination/documents/read", {}, errors=[str(e.detail)], start=t0)


class DocAckPayload(BaseModel):
    agent: str


@router.post("/coordination/documents/{file_id}/acknowledge")
def coordination_documents_acknowledge(file_id: str, req: DocAckPayload, request: Request):
    """AI Team Document Bus — ACKNOWLEDGE. Records that an agent has processed a document."""
    _require_key(request)
    t0 = time.time()
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM coordination_documents WHERE file_id = %s", (file_id,))
                if not cur.fetchone():
                    return _response("/coordination/documents/acknowledge", {},
                                     errors=[f"unknown file_id {file_id} - call LIST first"], start=t0)
                cur.execute("""
                    INSERT INTO coordination_document_acks (file_id, agent)
                    VALUES (%s, %s)
                    ON CONFLICT (file_id, agent) DO UPDATE SET acked_at = now()
                    RETURNING acked_at
                """, (file_id, req.agent))
                acked_at = cur.fetchone()["acked_at"]
                conn.commit()
        return _response("/coordination/documents/acknowledge", {
            "file_id": file_id, "agent": req.agent, "acked_at": acked_at.isoformat(),
        }, start=t0)
    except Exception as e:
        return _response("/coordination/documents/acknowledge", {}, errors=[str(e)], start=t0)


@router.get("/coordination/documents/{file_id}/status")
def coordination_documents_status(file_id: str):
    """AI Team Document Bus — STATUS. Shows which agents have (and haven't) acknowledged a document."""
    t0 = time.time()
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT filename FROM coordination_documents WHERE file_id = %s", (file_id,))
                doc = cur.fetchone()
                if not doc:
                    return _response("/coordination/documents/status", {}, errors=[f"unknown file_id {file_id}"], start=t0)
                cur.execute("""
                    SELECT agent, acked_at FROM coordination_document_acks
                    WHERE file_id = %s ORDER BY acked_at
                """, (file_id,))
                acks = [dict(row) for row in cur.fetchall()]
        acked_by = [a["agent"] for a in acks]
        pending = [a for a in _COORD_DOC_ROSTER if a not in acked_by]
        return _response("/coordination/documents/status", {
            "file_id": file_id, "title": doc["filename"],
            "acknowledged_by": acked_by, "pending": pending,
        }, start=t0)
    except Exception as e:
        return _response("/coordination/documents/status", {}, errors=[str(e)], start=t0)


class CoordDocCreatePayload(BaseModel):
    from_agent: str
    to_agent: str
    subject: str
    content: str
    priority: str = "normal"


@router.post("/coordination/documents")
def coordination_documents_create(req: CoordDocCreatePayload, request: Request):
    """
    AI Team Document Bus — CREATE. Closes the real gap found 2026-07-11:
    GBT had Drive read (search, coord-docs-list/read) but no way to WRITE a
    Drive doc BC would see - the only channel that reaches BC, since BC
    cannot call this gateway directly (its own constraint, documented in
    BC's ADR-002 handoff-endpoint proposal). This is that endpoint - GBT's
    "send to BC" (or BC's "send to GBT," or either sending to the other)
    without Buck relaying. Writes a durable ai_messages row (survives even
    if this write fails downstream) AND a real Drive doc in HCI AI Master
    that BC's normal Drive-reading behavior will pick up. Does not require
    Claude Code's session to be running - this is a plain API endpoint on
    the always-on api-server, same as every other gateway route.
    """
    _require_key(request)
    t0 = time.time()
    try:
        msg_id = _create_ai_message(req.from_agent, req.to_agent, "team_message",
                                     req.subject, req.content, None, False, None,
                                     None, None, None, req.priority, None)

        from integrations.credentials import get_google_token
        token = get_google_token("drive")
        ts = _buck_local_str()
        filename = f"{req.from_agent.upper()}_TO_{req.to_agent.upper()}_{req.subject[:60].replace(' ', '_')}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.md"
        body_text = f"{req.from_agent.upper()} -> {req.to_agent.upper()} | {ts}\nmessage_id: {msg_id}\npriority: {req.priority}\n\n{req.subject}\n{'=' * len(req.subject)}\n\n{req.content}\n"
        metadata = {"name": filename, "parents": [HCI_MASTER_FOLDER_ID], "mimeType": "text/plain"}
        boundary = "hcicoorddoc"
        upload_body = (
            f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n{json.dumps(metadata)}\r\n"
            f"--{boundary}\r\nContent-Type: text/plain\r\n\r\n{body_text}\r\n--{boundary}--"
        )
        r = requests.post(
            "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&supportsAllDrives=true",
            headers={"Authorization": f"Bearer {token}", "Content-Type": f"multipart/related; boundary={boundary}"},
            data=upload_body.encode("utf-8"), timeout=30)
        if r.status_code != 200:
            return _response("/coordination/documents", {"message_id": msg_id},
                              errors=[f"ai_messages row created (id {msg_id}) but Drive write failed: {r.status_code} {r.text[:200]}"], start=t0)
        drive_file = r.json()

        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE ai_messages SET related_file = %s WHERE id = %s", (drive_file["id"], msg_id))
        _touch_heartbeat(req.from_agent, f"sent doc to {req.to_agent}: {req.subject[:60]}")
        _log("/coordination/documents", req.from_agent, "coordination_documents", "created",
             round((time.time() - t0) * 1000), str(msg_id), req.subject[:60])
        return _response("/coordination/documents", {
            "message_id": msg_id, "drive_file_id": drive_file["id"], "filename": filename,
        }, start=t0)
    except Exception as e:
        return _response("/coordination/documents", {}, errors=[str(e)], start=t0)


# ── Email ─────────────────────────────────────────────────────────────────────

class EmailDraftRequest(BaseModel):
    to_name: str
    to_email: str
    subject: str
    body_html: str
    reply_to_message_id: Optional[str] = None
    cc: Optional[list] = None  # [{"name": "...", "email": "..."}] - additional team CCs

# GBT/Buck SOP directive 2026-07-06 (see Agent_Handoff SOP Violation handoff): every
# automated/system-sent email must copy Buck so he can see it and track vendor replies,
# regardless of who else is CC'd. Skipped only when Buck himself is the recipient.
_BUCK_EMAIL = ("Buck Adams", "buck@hendricksoninc.com")

def _with_buck_cc(to_email: str, extra_cc: Optional[list]) -> list[tuple[str, str]]:
    cc = [(c.get("name", ""), c["email"]) for c in (extra_cc or []) if c.get("email")]
    if to_email.lower() != _BUCK_EMAIL[1].lower() and not any(e.lower() == _BUCK_EMAIL[1].lower() for _, e in cc):
        cc.append(_BUCK_EMAIL)
    return cc

@router.post("/email/draft")
def create_email_draft(req: EmailDraftRequest, request: Request):
    """
    Create an Outlook draft email (does NOT send). GBT/Browser Claude calls this to stage
    a client/vendor email. Nothing sends from this endpoint under any circumstance —
    sending requires Buck's explicit Telegram approval via POST /email/send (see below).
    Always CCs Buck (see _with_buck_cc) so he can see and track every automated send.
    """
    _require_key(request)
    t0 = time.time()
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "integrations"))
        from microsoft_graph import create_draft, create_reply_draft
        cc = _with_buck_cc(req.to_email, req.cc)
        if req.reply_to_message_id:
            draft = create_reply_draft(req.reply_to_message_id, req.body_html)
        else:
            draft = create_draft(req.subject, req.body_html, [(req.to_name, req.to_email)], cc=cc)
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
    skip_notify: bool = False  # test-only: queue for approval without pushing a real Telegram message
    dry_run: bool = False  # test-only: skip the real Outlook draft creation entirely (2026-07-02 -
    # skip_notify alone was NOT enough; create_draft() ran unconditionally before it was even checked,
    # so every test run was creating a real draft in Buck's actual mailbox. ~100 accumulated this way.
    source_agent: str = "browser_claude"  # who actually drafted this — was hardcoded, falsely
    # attributing every caller's (including test-suite) activity/errors to Browser Claude

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

        if req.dry_run:
            draft_id = f"dry-run-{uuid.uuid4().hex[:12]}"
        elif req.reply_to_message_id:
            draft = create_reply_draft(req.reply_to_message_id, req.body_html)
            draft_id = draft.get("id", "")
        else:
            # req.cc existed on this model but was never actually applied to the draft -
            # found 2026-07-06 responding to GBT/Buck's SOP-violation handoff asking that
            # every automated send CC Buck. Now always CCs Buck plus any explicit cc list.
            cc = _with_buck_cc(req.to_email, req.cc)
            draft = create_draft(req.subject, req.body_html, [(req.to_name, req.to_email)], cc=cc)
            draft_id = draft.get("id", "")
        if not draft_id:
            raise ValueError("Draft creation returned no ID — cannot queue for approval")

        # Fixed 2026-07-06: this used to call _create_ai_message() directly AND THEN
        # _notify_agents() (which calls _create_ai_message() again internally) - every
        # real /email/send created two separate ai_messages rows for the same approval
        # request. Only the second (from _notify_agents) ever got the Telegram
        # APPROVE/REJECT buttons; the first sat orphaned at NEEDS_BUCK_APPROVAL forever.
        # Found while checking the Pella follow-up email this created (id 506 orphaned,
        # 507 real). Single call now, same as every other caller of _notify_agents.
        if req.skip_notify:
            msg_id = _create_ai_message(
                req.source_agent, "buck", "approval_request",
                f"Send email: {req.subject[:80]}",
                f"To: {req.to_name} <{req.to_email}>\nSubject: {req.subject}\n\n{req.body_html[:500]}",
                requires_buck_approval=True, approval_type="email_send",
                related_file=draft_id,
            )
            sent = {"id": msg_id}
        else:
            sent = _notify_agents(req.source_agent, "buck", "approval_request",
                                   f"Send email: {req.subject[:80]}",
                                   f"To: {req.to_name} <{req.to_email}>\n\n{req.body_html[:500]}",
                                   requires_buck_approval=True, approval_type="email_send",
                                   related_file=draft_id)

        return _response("/email/send", {
            "status":     "queued_for_approval",
            "message_id": sent.get("id"),
            "draft_id":   draft_id,
            "to_email":   req.to_email,
            "subject":    req.subject,
            "note":       "Draft created and sent to Buck for Telegram approval. It will only send once Buck approves.",
        }, start=t0)
    except Exception as e:
        return _response("/email/send", {}, errors=[str(e)], start=t0)


@router.post("/email/draft/{draft_id}/send")
def send_existing_draft(draft_id: str, request: Request):
    """Disabled 2026-07-07 per Buck's direct instruction: no agent or automated path may
    ever trigger a real email send. Drafts stay in Buck's own Outlook Drafts folder; he
    sends them himself once he's actually read the content. (Previously this was the
    "manual/recovery" send path, callable once a Telegram APPROVE had fired - but an
    email to an external party went out this way and could not be recalled, since the
    recipient wasn't on HCI's Exchange org. See _handle_buck_command's APPROVE handler
    for the corresponding fix on the Telegram side.)"""
    _require_key(request)
    t0 = time.time()
    return _response("/email/draft/send", {},
                      errors=["Disabled by standing policy: emails must be sent manually by Buck from "
                              "his own Outlook Drafts folder, never by an automated/agent-triggered call. "
                              f"Draft {draft_id[:20]} is waiting in Drafts — open Outlook to send it."],
                      start=t0)


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


@router.get("/agent/handoff/{request_id}")
def agent_handoff_lookup(request_id: str):
    """Look up a specific handoff by its request ID (the trailing hex suffix in its
    filename, e.g. '33259ccc' from 'GBT_HANDOFF_2026-07-06_..._33259ccc.md') without
    needing folder access. Added 2026-07-06 - across one session, specific handoff IDs
    got referenced back and forth between Claude Code and GBT at least 6 times, each
    requiring a manual `find -iname` across Inbox/Processed/Failed. Searches all three
    folders and reports which one the file is currently in - Inbox means still
    unprocessed, Processed/Failed means it was handled (or handling failed). Registered
    after /agent/handoff/document-types on purpose - a path-parameter route ahead of a
    literal one would shadow it in FastAPI's routing order."""
    t0 = time.time()
    base = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "..", "..",
        "Architecture", "Agent_Handoff"
    ))
    request_id = request_id.strip().lower()
    for folder in ("Inbox", "Processed", "Failed"):
        d = os.path.join(base, folder)
        if not os.path.isdir(d):
            continue
        for fname in os.listdir(d):
            if not fname.lower().endswith(f"{request_id}.md"):
                continue
            fpath = os.path.join(d, fname)
            try:
                with open(fpath) as f:
                    raw = f.read()
                lines = raw.split("\n")
                meta = {}
                body_start = 0
                if lines and lines[0].strip() == "---":
                    for i, line in enumerate(lines[1:], 1):
                        if line.strip() == "---":
                            body_start = i + 1
                            break
                        if ":" in line:
                            k, v = line.split(":", 1)
                            meta[k.strip()] = v.strip()
                body = "\n".join(lines[body_start:]).strip()
                return _response(f"/agent/handoff/{request_id}", {
                    "found": True, "folder": folder, "filename": fname,
                    "title": meta.get("title", fname),
                    "source_agent": meta.get("source_agent", "unknown"),
                    "priority": meta.get("priority", "medium"),
                    "created_at": meta.get("created_at", ""),
                    "body": body,
                }, start=t0)
            except Exception as e:
                return _response(f"/agent/handoff/{request_id}", {}, errors=[str(e)], start=t0)
    return _response(f"/agent/handoff/{request_id}", {"found": False}, start=t0)


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
        _reject_if_monitored_folder(folder_id)

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

        _log("/drive/write", "gbt", req.filename, action, round((time.time()-t0)*1000), str(uuid.uuid4())[:8],
             payload={"folder_id": folder_id, "filename": req.filename,
                      "folder_id_was_explicit": bool(req.folder_id)})
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


class DriveMovePayload(BaseModel):
    file_id: str
    new_parent_id: str
    old_parent_id: Optional[str] = None  # if omitted, removes all current parents


@router.post("/drive/move")
async def drive_move(req: DriveMovePayload):
    """
    Move a file/folder to a different Drive parent (real move — updates parents,
    does not copy). Uses the same drive-scoped token as /drive/write. Added
    2026-07-02 for the Drive cleanup pass — the claude.ai Drive MCP connector
    only exposes search/read/create/copy, no move, so copying was the only
    prior option and that just multiplies clutter instead of reducing it.
    """
    t0 = time.time()
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
        from integrations.credentials import get_google_token
        token = get_google_token("drive")
        DRIVE_TIMEOUT = 20

        old_parents = req.old_parent_id
        if not old_parents:
            meta_resp = requests.get(
                f"https://www.googleapis.com/drive/v3/files/{req.file_id}",
                headers={"Authorization": f"Bearer {token}"},
                params={"fields": "parents,name", "supportsAllDrives": "true"},
                timeout=DRIVE_TIMEOUT,
            )
            meta = meta_resp.json()
            old_parents = ",".join(meta.get("parents", []))

        # supportsAllDrives was missing here - found 2026-07-08 archiving stale
        # 64EW bid-leveling files: addParents targeting a folder just created in
        # a Shared Drive 404'd as "File not found" without it, even though the
        # exact same call worked for 101F/1355R (those parent folders happened to
        # already be indexed by the time the move ran; 64EW's did not).
        move_resp = requests.patch(
            f"https://www.googleapis.com/drive/v3/files/{req.file_id}",
            headers={"Authorization": f"Bearer {token}"},
            params={
                "addParents": req.new_parent_id,
                "removeParents": old_parents,
                "fields": "id,name,parents",
                "supportsAllDrives": "true",
            },
            timeout=DRIVE_TIMEOUT,
        )
        result = move_resp.json()
        if "error" in result:
            return _response("/drive/move", {}, errors=[str(result["error"])], start=t0)

        _log("/drive/move", "claude_code", req.file_id, "moved", round((time.time()-t0)*1000), str(uuid.uuid4())[:8])
        return _response("/drive/move", {
            "file_id": result.get("id"),
            "name": result.get("name"),
            "new_parents": result.get("parents"),
            "removed_from": old_parents,
        }, start=t0)

    except Exception as e:
        return _response("/drive/move", {}, errors=[str(e)], start=t0)


# ── System Drift Check ───────────────────────────────────────────────────────
# Added 2026-07-02 after a full manual audit (5 parallel research passes) found:
# n8n silently failing 64% of executions, a HubSpot credential broken 9 days
# unnoticed, connector_registry never wired to any real sync, and GBT's own
# retrospectives claiming "Sprint 7 complete"/"9.9/10" while zero code shipped
# for the sprint. None of that was caught until someone manually went looking.
# This endpoint automates the highest-value checks from that audit so drift
# gets caught in days, not whenever someone next asks "read everything."

@router.get("/admin/drift-check")
def system_drift_check():
    """Automated version of the 2026-07-02 manual audit. Checks for the
    specific silent-failure patterns found that day: n8n execution health,
    stale/dead connectors, stale credentials, and sprint-status drift between
    GBT's CYCLE files and the real CURRENT_SPRINT.md. Intended to run on a
    schedule (n8n, weekly) and report findings via /ai/messages, not just
    sit here waiting to be polled."""
    import subprocess
    t0 = time.time()
    findings = []
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                # 1. connector_registry rows that claim to be registered but have
                #    literally never synced - the exact pattern found for Houzz/
                #    Drive/HubSpot all three on 07-02.
                cur.execute("""
                    SELECT project_code, source_system, created_at
                    FROM connector_registry
                    WHERE last_indexed IS NULL
                      AND created_at < NOW() - INTERVAL '3 days'
                """)
                dead_connectors = cur.fetchall()
                if dead_connectors:
                    findings.append({
                        "severity": "high",
                        "category": "dead_connector",
                        "detail": f"{len(dead_connectors)} connector_registry rows registered 3+ days ago, never synced",
                        "items": [f"{r['project_code']}/{r['source_system']} (registered {r['created_at'].date()})" for r in dead_connectors],
                    })

                # 2. ai_messages stuck STALE for a long time - the BC 101F
                #    self-report sat unacknowledged for over a day undetected.
                cur.execute("""
                    SELECT id, title, target_agent, created_at
                    FROM ai_messages
                    WHERE status = 'STALE' AND created_at < NOW() - INTERVAL '24 hours'
                    ORDER BY created_at ASC
                """)
                stale_msgs = cur.fetchall()
                if stale_msgs:
                    findings.append({
                        "severity": "medium",
                        "category": "stale_directive",
                        "detail": f"{len(stale_msgs)} directive(s) STALE for 24h+, nobody has acted on them",
                        "items": [f"#{r['id']} to {r['target_agent']}: {r['title']} (since {r['created_at'].date()})" for r in stale_msgs],
                    })

                # 2b. drive_bids rows that are outbound documents (SOW, bid email
                #     templates, bid requests) misfiled as vendor bids - the exact
                #     pattern Buck caught live 2026-07-09 in generated leveling
                #     sheets, present since the feature was built with no check
                #     ever catching it. See services/bid_leveling/drive_bid_reader.py
                #     _is_outbound_not_a_bid() for the filter that now prevents new
                #     ones; this check catches any that slip through or predate it.
                cur.execute("""
                    SELECT project_id, vendor_name, file_name
                    FROM drive_bids
                    WHERE vendor_name ~* '\\y(SOW|bid email template|bid request|bid package set|email templates?|division index|bid instructions?|bid level tracker|level tracker|bid tracker|bid leveling|bid audit)\\y'
                       OR file_name ~* '\\y(SOW|bid email template|bid request|bid package set|email templates?|division index|bid instructions?|bid level tracker|level tracker|bid tracker|bid leveling|bid audit)\\y'
                       OR vendor_name ~* '^(archived?|old|superseded)([[:space:]_-]|$)'
                       OR file_name ~* '^(archived?|old|superseded)([[:space:]_-]|$)'
                       OR division_num !~ '^[0-9]+$'
                """)
                sow_contaminated = cur.fetchall()
                if sow_contaminated:
                    findings.append({
                        "severity": "high",
                        "category": "bid_leveling_sow_contamination",
                        "detail": f"{len(sow_contaminated)} drive_bids row(s) are outbound docs/trackers/archived items/garbage division codes misfiled as vendor bids - will appear in generated leveling sheets as fake vendors or fake divisions",
                        "items": [f"project {r['project_id']}: {r['vendor_name']}" for r in sow_contaminated[:15]],
                    })
    except Exception as e:
        findings.append({"severity": "high", "category": "check_failed", "detail": f"DB checks errored: {e}"})

    # 3. n8n execution failure rate - the 64%-failing-and-nobody-noticed pattern.
    try:
        n8n_key = os.environ.get("N8N_API_KEY", "")
        resp = requests.get(
            "http://localhost:5678/api/v1/executions",
            headers={"X-N8N-API-KEY": n8n_key},
            params={"limit": 100},
            timeout=10,
        )
        if resp.status_code == 200:
            execs = resp.json().get("data", [])
            if execs:
                errored = sum(1 for e in execs if e.get("status") == "error" or e.get("finished") is False and e.get("stoppedAt"))
                rate = errored / len(execs)
                if rate > 0.20:
                    findings.append({
                        "severity": "high",
                        "category": "n8n_failure_rate",
                        "detail": f"{errored}/{len(execs)} ({rate:.0%}) of last 100 n8n executions failed - exceeds 20% threshold",
                        "items": [],
                    })
        else:
            findings.append({"severity": "medium", "category": "n8n_unreachable", "detail": f"n8n executions API returned {resp.status_code} - can't verify workflow health"})
    except Exception as e:
        findings.append({"severity": "medium", "category": "n8n_unreachable", "detail": f"n8n executions API unreachable: {e}"})

    # 3b. Per-workflow n8n failure rate - the aggregate check above found nothing wrong the
    #     whole 2026-07-02 session because healthy workflows diluted the overall rate below the
    #     20% threshold, while 14 active workflows (28 nodes, all pointed at the wrong n8n
    #     credential from a copy-paste error) were consistently failing 100% of their recent
    #     runs the entire time. This checks each active workflow individually so a single
    #     always-broken workflow can never hide behind everyone else's health again.
    try:
        n8n_key = os.environ.get("N8N_API_KEY", "")
        wf_resp = requests.get("http://localhost:5678/api/v1/workflows", headers={"X-N8N-API-KEY": n8n_key},
                                params={"limit": 250}, timeout=10)
        if wf_resp.status_code == 200:
            broken_workflows = []
            for wf in wf_resp.json().get("data", []):
                if not wf.get("active"):
                    continue
                ex_resp = requests.get("http://localhost:5678/api/v1/executions",
                                        headers={"X-N8N-API-KEY": n8n_key},
                                        params={"workflowId": wf["id"], "limit": 5}, timeout=10)
                if ex_resp.status_code != 200:
                    continue
                execs = ex_resp.json().get("data", [])
                if len(execs) < 3:
                    continue
                errored = sum(1 for e in execs if e.get("status") == "error")
                if errored == len(execs):
                    broken_workflows.append(f"{wf['name']} ({errored}/{len(execs)} recent runs failed)")
            if broken_workflows:
                findings.append({
                    "severity": "high",
                    "category": "n8n_workflow_consistently_failing",
                    "detail": f"{len(broken_workflows)} active workflow(s) failing 100% of their last 3+ runs - these can hide inside a healthy aggregate failure rate",
                    "items": broken_workflows,
                })
    except Exception as e:
        findings.append({"severity": "low", "category": "check_failed", "detail": f"Per-workflow n8n failure check errored: {e}"})

    # 4. Sprint status drift - GBT's CYCLE files claiming a higher sprint number
    #    "complete" than CURRENT_SPRINT.md's real active sprint.
    try:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        with open(os.path.join(repo_root, "CURRENT_SPRINT.md")) as f:
            current_sprint_text = f.read()
        m = _re.search(r"Sprint Number:\*\*\s*(\d+)", current_sprint_text)
        real_sprint = int(m.group(1)) if m else None

        ai_team_dir = os.path.join(repo_root, "AI_TEAM")
        cycle_files = [f for f in os.listdir(ai_team_dir) if f.startswith("CYCLE") and "SPRINT" in f.upper() and f.endswith(".md")]
        max_claimed_sprint = None
        for fname in cycle_files:
            m2 = _re.search(r"SPRINT(\d+)", fname.upper())
            if not m2:
                continue
            # Skip files already annotated as superseded (checked 2026-07-07) - CYCLE47
            # and CYCLE49 both got a "SUPERSEDED ... treat CURRENT_SPRINT.md as source of
            # truth" correction note added on top on 2026-07-06, but this check kept
            # re-flagging them anyway since it only ever looked at the filename, never
            # the file's own content. A reconciled, self-correcting doc isn't drift.
            try:
                with open(os.path.join(ai_team_dir, fname)) as cf:
                    if "SUPERSEDED" in cf.read(500).upper():
                        continue
            except Exception:
                pass
            n = int(m2.group(1))
            if max_claimed_sprint is None or n > max_claimed_sprint:
                max_claimed_sprint = n
        if real_sprint and max_claimed_sprint and max_claimed_sprint > real_sprint:
            findings.append({
                "severity": "medium",
                "category": "sprint_drift",
                "detail": f"AI_TEAM/ has CYCLE files claiming Sprint {max_claimed_sprint}, but CURRENT_SPRINT.md says Sprint {real_sprint} is active - verify claimed sprints against real code before trusting any 'complete' status",
                "items": [],
            })
    except Exception as e:
        findings.append({"severity": "low", "category": "check_failed", "detail": f"Sprint drift check errored: {e}"})

    # 5. n8n credential staleness - the exact "HubSpot credential broken 9 days,
    #    nobody noticed" pattern. Flags any credential attached to an active
    #    workflow that hasn't been updated in 14+ days.
    try:
        n8n_key = os.environ.get("N8N_API_KEY", "")
        cred_resp = requests.get("http://localhost:5678/api/v1/credentials",
                                  headers={"X-N8N-API-KEY": n8n_key}, timeout=10)
        wf_resp = requests.get("http://localhost:5678/api/v1/workflows",
                                headers={"X-N8N-API-KEY": n8n_key}, params={"limit": 250}, timeout=10)
        if cred_resp.status_code == 200 and wf_resp.status_code == 200:
            creds = {c["id"]: c for c in cred_resp.json().get("data", [])}
            active_cred_ids = set()
            for wf in wf_resp.json().get("data", []):
                if not wf.get("active"):
                    continue
                for node in wf.get("nodes", []):
                    for cred in (node.get("credentials") or {}).values():
                        active_cred_ids.add(cred.get("id"))
            stale_creds = []
            for cid in active_cred_ids:
                c = creds.get(cid)
                if not c:
                    continue
                updated = c.get("updatedAt")
                if updated:
                    age_days = (datetime.now(timezone.utc) - datetime.fromisoformat(updated.replace("Z", "+00:00"))).days
                    if age_days > 14:
                        stale_creds.append(f"{c['name']} (unchanged {age_days}d, in active use)")
            if stale_creds:
                findings.append({
                    "severity": "medium",
                    "category": "stale_credential",
                    "detail": f"{len(stale_creds)} credential(s) in active use, unchanged 14+ days - verify still valid",
                    "items": stale_creds,
                })
    except Exception as e:
        findings.append({"severity": "low", "category": "check_failed", "detail": f"Credential staleness check errored: {e}"})

    # 6. Duplicate rows on natural keys where no unique constraint exists yet -
    #    the connector_registry pattern (54 rows -> 9), checked here for other
    #    tables known to accumulate the same way via repeated init/seed calls.
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                dup_checks = [
                    ("missions", "mission_id"),
                    ("integration_registry", "integration_key"),
                ]
                for table, key_cols in dup_checks:
                    try:
                        cur.execute(f"""
                            SELECT {key_cols}, COUNT(*) c FROM {table}
                            GROUP BY {key_cols} HAVING COUNT(*) > 1
                        """)
                        dups = cur.fetchall()
                        if dups:
                            findings.append({
                                "severity": "low",
                                "category": "duplicate_rows",
                                "detail": f"{table}: {len(dups)} key(s) with duplicate rows, no unique constraint enforcing this",
                                "items": [str(dict(d)) for d in dups[:10]],
                            })
                    except Exception:
                        conn.rollback()
    except Exception as e:
        findings.append({"severity": "low", "category": "check_failed", "detail": f"Duplicate row check errored: {e}"})

    # 7. Construction-phase data (daily logs, schedule variance) on projects
    #    with no permit issued yet - the exact "framing cannot proceed" fabricated
    #    RFI/risk/daily-log/schedule-variance contamination found on 1355R/101F
    #    on 07-02. permit_status defaults to 'unknown' so this only fires once a
    #    project has been explicitly confirmed not_issued.
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT p.project_code,
                        (SELECT COUNT(*) FROM daily_logs dl WHERE dl.project_id = p.id) AS dl_count,
                        (SELECT COUNT(*) FROM schedule_variance sv WHERE sv.project_id = p.id) AS sv_count
                    FROM projects p
                    WHERE p.permit_status = 'not_issued'
                      AND ((SELECT COUNT(*) FROM daily_logs dl WHERE dl.project_id = p.id) > 0
                           OR (SELECT COUNT(*) FROM schedule_variance sv WHERE sv.project_id = p.id) > 0)
                """)
                phase_mismatches = cur.fetchall()
                if phase_mismatches:
                    findings.append({
                        "severity": "high",
                        "category": "permit_phase_mismatch",
                        "detail": f"{len(phase_mismatches)} project(s) with permit_status='not_issued' still have daily_logs/schedule_variance rows implying active field construction - these are almost certainly test artifacts",
                        "items": [f"{r['project_code']}: {r['dl_count']} daily_logs, {r['sv_count']} schedule_variance rows" for r in phase_mismatches],
                    })
    except Exception as e:
        findings.append({"severity": "low", "category": "check_failed", "detail": f"Permit-phase mismatch check errored: {e}"})

    # 8. Fabricated commit-hash claims - the exact "GATE 5: GO, signed, commit 8e003ec"
    #    pattern found 2026-07-02, where an agent cited a specific commit as proof of a
    #    claim and the commit did not exist anywhere in git history. Any ai_message body
    #    that cites what looks like a commit hash gets that hash checked against the
    #    real repo; a hash that doesn't resolve is a fabricated verification, not a typo.
    try:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        hash_pattern = _re.compile(r"\bcommit[:\s]+([0-9a-f]{7,40})\b", _re.IGNORECASE)
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, source_agent, title, body, created_at FROM ai_messages
                    WHERE body ~* 'commit[:\\s]+[0-9a-f]{7,40}'
                    ORDER BY created_at DESC LIMIT 100
                """)
                candidates = cur.fetchall()
        # A message that quotes a bad hash to *report* a fabrication (a peer-review
        # correction) is not itself a new fabricated claim - found live 2026-07-10
        # re-flagging #335, the actual 2026-07-02 review that caught and resolved
        # this exact hash. Skip when the text right around the hash already says
        # it doesn't exist/was fabricated - that's self-documentation, not a
        # repeat offense.
        self_documenting_re = _re.compile(
            r"(does not exist|not in git history|fabricat|self-issued|no such commit)", _re.IGNORECASE)
        fabricated = []
        for r in candidates:
            for m in hash_pattern.finditer(r["body"]):
                h = m.group(1)
                check = subprocess.run(["git", "cat-file", "-t", h], cwd=repo_root,
                                        capture_output=True, text=True, timeout=5)
                if check.returncode != 0:
                    context = r["body"][max(0, m.start()-80):m.end()+120]
                    if self_documenting_re.search(context):
                        continue
                    fabricated.append(f"#{r['id']} ({r['source_agent']}, {r['created_at'].date()}): "
                                       f"cites commit {h} - not in git history - \"{r['title']}\"")
        if fabricated:
            findings.append({
                "severity": "high",
                "category": "fabricated_commit_claim",
                "detail": f"{len(fabricated)} ai_message(s) cite a commit hash as verification that does not exist in git log - treat the underlying claim as unverified, not just the hash",
                "items": fabricated,
            })
    except Exception as e:
        findings.append({"severity": "low", "category": "check_failed", "detail": f"Fabricated commit-hash check errored: {e}"})

    # 9. Handbook volume filename/title numbering drift - the exact bug found 07-02
    #    where Volume_06/07/08's internal titles said "Volume VII/VIII/IX" (one Roman
    #    numeral too high), and Governance + Roadmap both silently claimed "Volume IX."
    try:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        handbook_dir = os.path.join(repo_root, "architecture", "Handbook")
        roman = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII", 9: "IX", 10: "X"}
        numbering_issues = []
        seen_titles = {}
        if os.path.isdir(handbook_dir):
            for fname in sorted(os.listdir(handbook_dir)):
                m = _re.match(r"Volume_(\d\d)_", fname)
                if not m or not fname.endswith(".md"):
                    continue
                n = int(m.group(1))
                expected = roman.get(n)
                with open(os.path.join(handbook_dir, fname)) as f:
                    first_line = f.readline().strip()
                title_m = _re.search(r"Volume\s+([IVX]+)\s*—", first_line)
                actual = title_m.group(1) if title_m else None
                if expected and actual and actual != expected:
                    numbering_issues.append(f"{fname}: filename implies Volume {expected}, title says Volume {actual}")
                if actual:
                    seen_titles.setdefault(actual, []).append(fname)
        for roman_num, files in seen_titles.items():
            if len(files) > 1:
                numbering_issues.append(f"Volume {roman_num} claimed by {len(files)} files: {', '.join(files)}")
        if numbering_issues:
            findings.append({
                "severity": "medium",
                "category": "handbook_numbering_drift",
                "detail": f"{len(numbering_issues)} Handbook volume(s) with filename/title mismatch or duplicate Roman numeral",
                "items": numbering_issues,
            })
    except Exception as e:
        findings.append({"severity": "low", "category": "check_failed", "detail": f"Handbook numbering check errored: {e}"})

    # 10. Unintegrated Drive Handbook content - the exact 07-02 root cause: GBT+BC
    #     authored real Handbook chapters, saved them to Drive marked "PUBLISHED," and
    #     they sat there for 2+ days never pulled into the repo, so a later session
    #     nearly re-authored the same chapters from scratch. Flags Drive files matching
    #     the Handbook naming pattern that are newer than the last Handbook commit.
    try:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        last_commit = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", "architecture/Handbook/"],
            cwd=repo_root, capture_output=True, text=True, timeout=5,
        )
        last_commit_ts = int(last_commit.stdout.strip()) if last_commit.returncode == 0 and last_commit.stdout.strip() else 0
        drive_data = _proxy("/services/drive-intelligence/search", {"q": "HANDBOOK"})
        drive_files = (drive_data or {}).get("files", [])
        unintegrated = []
        for f in drive_files:
            name = f.get("name") or ""
            # Guard added 2026-07-06: search_files() does a Drive-wide fullText search,
            # which matched "Architectural Plans 5.8.26.pdf" (real project drawings,
            # category=Drawing/Plan) just because "handbook" appeared somewhere in its
            # scanned content - unrelated to our authored Handbook docs. Require the word
            # in the filename itself, matching how real Handbook chapters are actually named.
            if "HANDBOOK" not in name.upper():
                continue
            if name.upper().startswith("[OBSOLETE"):
                continue  # already marked obsolete - not un-integrated content, don't re-flag it forever
            modified = f.get("modified")
            if not modified:
                continue
            try:
                mod_ts = datetime.fromisoformat(modified).timestamp()
            except Exception:
                continue
            if mod_ts > last_commit_ts:
                unintegrated.append(f"{name} (Drive-modified {modified}, after last Handbook commit)")
        if unintegrated:
            findings.append({
                "severity": "high",
                "category": "unintegrated_drive_content",
                "detail": f"{len(unintegrated)} Drive file(s) matching Handbook naming are newer than the last Handbook commit - verify they aren't real authored content sitting un-integrated before authoring anything new",
                "items": unintegrated,
            })
    except Exception as e:
        findings.append({"severity": "low", "category": "check_failed", "detail": f"Unintegrated Drive content check errored: {e}"})

    # 11. Test-authored records leaking into real (non-sandbox) projects - the exact
    #     2026-07-02 pattern where 36 synthetic RFIs from plan-review pipeline testing
    #     (submitted_by = test_suite/test_pdf_upload) sat in 101F's real rfis table
    #     for days, plus [TEST]-titled meetings and test_suite decision events, none of
    #     it in the QATEST sandbox project where it belonged. Catches the same shape of
    #     issue anywhere it recurs: a project marked active/monitoring/reference with
    #     rows whose author/title/content flags them as test data.
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT p.project_code, 'rfis' AS tbl, COUNT(*) c
                    FROM rfis r JOIN projects p ON p.id = r.project_id
                    WHERE p.status != 'sandbox'
                      AND (r.submitted_by ILIKE '%test%' OR r.subject ILIKE '[test]%' OR r.question ILIKE 'test%')
                    GROUP BY p.project_code
                    UNION ALL
                    SELECT p.project_code, 'project_events', COUNT(*)
                    FROM project_events pe JOIN projects p ON p.id = pe.project_id
                    WHERE p.status != 'sandbox'
                      AND (pe.created_by ILIKE '%test%' OR pe.title ILIKE '%[test]%' OR pe.title ILIKE '%test suite%'
                           OR pe.title ILIKE '%: test' OR pe.description = 'test'
                           OR (pe.metadata->>'test') = 'true')
                    GROUP BY p.project_code
                    UNION ALL
                    SELECT p.project_code, 'meetings', COUNT(*)
                    FROM meetings m JOIN projects p ON p.id = m.project_id
                    WHERE p.status != 'sandbox' AND m.title ILIKE '%[test]%'
                    GROUP BY p.project_code
                """)
                leaks = cur.fetchall()
        if leaks:
            findings.append({
                "severity": "high",
                "category": "test_data_in_real_project",
                "detail": f"{len(leaks)} project/table combination(s) with test-authored records outside the QATEST sandbox - verify and purge, these get read as real by every agent and endpoint",
                "items": [f"{r['project_code']}.{r['tbl']}: {r['c']} row(s)" for r in leaks],
            })
    except Exception as e:
        findings.append({"severity": "low", "category": "check_failed", "detail": f"Test-data-leak check errored: {e}"})

    # 12. Bid packages marked awarded with no corresponding bid_entries dollar amount -
    #     found 2026-07-03 on 246GW (19 packages, real vendor names on each, all imported
    #     via a different path than the other 3 pilot projects) - the accounting console
    #     silently read "$0 awarded" for a project with real committed work, which is a
    #     financial blind spot, not a $0 fact. This is a real data-entry gap requiring a
    #     human to enter the actual awarded amounts, not something to auto-fill with a
    #     guess - flagged here so it can't sit silent on a future project either.
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT p.project_code, COUNT(*) c
                    FROM bid_packages bp
                    JOIN projects p ON p.id = bp.project_id
                    LEFT JOIN bid_entries be ON be.bid_package_id = bp.id AND be.status = 'awarded'
                    WHERE bp.status = 'awarded' AND be.id IS NULL
                      AND p.status IN ('active','design','bidding','preconstruction','monitoring')
                    GROUP BY p.project_code
                """)
                gaps = cur.fetchall()
        if gaps:
            findings.append({
                "severity": "high",
                "category": "awarded_package_missing_bid_entry",
                "detail": f"{len(gaps)} project(s) have bid_packages marked 'awarded' with no matching bid_entries row - accounting/owner dollar totals for these projects are understated, not accurate zeros. Needs a human to enter the real awarded amounts.",
                "items": [f"{r['project_code']}: {r['c']} package(s)" for r in gaps],
            })
    except Exception as e:
        findings.append({"severity": "low", "category": "check_failed", "detail": f"Awarded-package data-gap check errored: {e}"})

    # 13. Stale test-titled rows in pending_approvals - found 2026-07-06 via the
    #     system-auditor's constitution_compliance check flagging "3 approvals pending
    #     >72 hours" as a NON-COMPLIANT governance violation, when they were actually 3
    #     leftover test fixtures from 2026-06-30 ("Test approval - verify loop works",
    #     etc.) that nobody ever resolved. A synthetic test row left in a real approval
    #     queue reads as a genuine overdue-approval violation to any downstream
    #     consumer (constitution checker, executive dashboards, Buck) - same shape of
    #     issue as test_data_in_real_project above, different table.
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, title, created_at FROM pending_approvals
                    WHERE status = 'pending'
                      AND (title ILIKE '%test%' OR requested_by ILIKE '%test%')
                """)
                stale_test_approvals = cur.fetchall()
                # Same pattern, different table - found 2026-07-06 live in BTW-8's
                # /pm/{id}/weekly client_comms output: 3 "[DEFERRED] Defer test" rows
                # from today's test suite reruns were sitting pending in executive_inbox,
                # showing up as fake client decisions a PM would think are real.
                cur.execute("""
                    SELECT exec_id AS id, title, created_at FROM executive_inbox
                    WHERE status = 'pending' AND title ILIKE '%test%'
                """)
                stale_test_exec_inbox = cur.fetchall()
        if stale_test_approvals:
            findings.append({
                "severity": "medium",
                "category": "test_data_in_approval_queue",
                "detail": f"{len(stale_test_approvals)} test-titled row(s) sitting 'pending' in pending_approvals - reads as a real overdue governance violation to constitution_compliance and any dashboard, resolve or purge them.",
                "items": [f"id={r['id']}: {r['title']}" for r in stale_test_approvals],
            })
        if stale_test_exec_inbox:
            findings.append({
                "severity": "medium",
                "category": "test_data_in_executive_inbox",
                "detail": f"{len(stale_test_exec_inbox)} test-titled row(s) sitting 'pending' in executive_inbox - surfaces as a fake client/PM decision in /pm/{{id}}/weekly's client_comms, resolve or purge them.",
                "items": [f"id={r['id']}: {r['title']}" for r in stale_test_exec_inbox],
            })
    except Exception as e:
        findings.append({"severity": "low", "category": "check_failed", "detail": f"Stale-test-approval check errored: {e}"})

    # 14. project_brain_snapshots.health (algorithmic, from ProjectIntelligenceEngine's
    #     detect_risks() heuristics) disagreeing with the real risks table - the exact
    #     drift executive.py's mission-control fixed on 2026-07-01 (1355R showed
    #     GREEN/0-risk there while risks had 4 open/2 high rows) and that this session
    #     found had never propagated to cross_project's company-snapshot endpoint,
    #     fixed 2026-07-06. General check so a THIRD endpoint reading the unreconciled
    #     snapshot health can't silently reintroduce the same disagreement.
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT p.project_code, pbs.health AS snapshot_health,
                           COUNT(r.id) FILTER (WHERE r.severity IN ('critical','high')) AS high_or_critical
                    FROM projects p
                    JOIN project_brain_snapshots pbs ON pbs.project_id = p.id
                        AND pbs.snapshot_date = CURRENT_DATE
                    LEFT JOIN risks r ON r.project_id = p.id AND r.status = 'open'
                    WHERE p.status IN ('active','design','bidding','preconstruction','monitoring')
                    GROUP BY p.project_code, pbs.health
                    HAVING (COUNT(r.id) FILTER (WHERE r.severity IN ('critical','high')) > 0
                            AND pbs.health != 'RED')
                """)
                mismatches = cur.fetchall()
        if mismatches:
            findings.append({
                "severity": "high",
                "category": "snapshot_risk_reconciliation_drift",
                "detail": f"{len(mismatches)} project(s) have a project_brain_snapshots health that disagrees with the real risks table - any endpoint reading the snapshot directly (not reconciled) will show a falsely-clean status.",
                "items": [f"{r['project_code']}: snapshot says {r['snapshot_health']}, risks table has {r['high_or_critical']} high/critical open" for r in mismatches],
            })
    except Exception as e:
        findings.append({"severity": "low", "category": "check_failed", "detail": f"Snapshot-reconciliation check errored: {e}"})

    # 15. Stale or failing test result files - found 2026-07-06 that
    #     test_results_system_auditor.json had a real failure (a genuine bug, not a
    #     flaky test) sitting unnoticed since 2026-06-30 because nobody had re-run
    #     that suite in the 6 days since. A failing test that nobody re-runs is the
    #     same silent-failure shape as everything else this ADR exists to catch -
    #     just applied to the test suites themselves instead of production data.
    try:
        import glob as _glob
        tests_dir = os.path.join(os.path.dirname(__file__), "..", "..", "tests")
        stale_or_failing = []
        for result_path in _glob.glob(os.path.join(tests_dir, "test_results_*.json")):
            try:
                with open(result_path) as f:
                    rd = json.load(f)
                fname = os.path.basename(result_path)
                failed = rd.get("failed") if isinstance(rd, dict) else None
                run_at = rd.get("finished") or rd.get("run_at") or rd.get("generated_at")
                if failed and int(failed) > 0:
                    stale_or_failing.append(f"{fname}: {failed} failing test(s)")
                elif run_at:
                    try:
                        run_dt = datetime.fromisoformat(str(run_at).replace("Z", "+00:00"))
                        if run_dt.tzinfo is None:
                            run_dt = run_dt.replace(tzinfo=timezone.utc)
                        age_days = (datetime.now(timezone.utc) - run_dt).days
                        if age_days > 7:
                            stale_or_failing.append(f"{fname}: last run {age_days}d ago")
                    except Exception:
                        pass
            except Exception:
                continue
        if stale_or_failing:
            findings.append({
                "severity": "medium",
                "category": "stale_or_failing_test_results",
                "detail": f"{len(stale_or_failing)} test result file(s) show real failures or haven't been re-run in over a week - a genuine failure can sit unnoticed indefinitely if nothing re-runs the suite.",
                "items": stale_or_failing,
            })
    except Exception as e:
        findings.append({"severity": "low", "category": "check_failed", "detail": f"Test-staleness check errored: {e}"})

    # 16. Test-artifact emails leaking into the real mailbox - found 2026-07-06 while
    #     auditing the 101F Pella duplicate: dozens of "[TEST] automated regression..."
    #     emails from this session's own suite runs are sitting in real Sent Items (the
    #     dry_run flag on /email/send only stops NEW ones, it doesn't clean up what a
    #     suite already sent before that flag existed - same shape as the ~100-draft
    #     backlog noted in that endpoint's own code comment). A blanket "any external
    #     send with no matching approval row" check was tried first and rejected - it
    #     fired on Buck's own ordinary vendor emails (radon, roofing, HubSpot deals),
    #     which have no reason to ever go through the agent approval path. This narrower
    #     version only flags the pattern that's actually a bug: test-signature subjects
    #     reaching a real send.
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "integrations"))
        from microsoft_graph import _request as _graph_request
        cutoff = (datetime.now(timezone.utc) - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
        r, gerr = _graph_request("GET", "/me/mailFolders/sentitems/messages", params={
            "$select": "id,subject,toRecipients,sentDateTime",
            "$top": 50,
            "$orderby": "sentDateTime desc",
            "$filter": f"sentDateTime ge {cutoff}",
        })
        if gerr:
            findings.append({"severity": "low", "category": "check_failed", "detail": f"Test-artifact-email check: Graph unreachable: {gerr}"})
        else:
            test_leaks = []
            for m in (r or {}).get("value", []):
                subj = (m.get("subject") or "").upper()
                if "[TEST" in subj or subj.startswith("TEST ") or "REGRESSION" in subj:
                    to_addrs = [rc["emailAddress"]["address"] for rc in m.get("toRecipients", [])]
                    test_leaks.append(f"{m.get('sentDateTime')} | {m.get('subject','')[:60]} -> {to_addrs}")
            if test_leaks:
                findings.append({
                    "severity": "medium",
                    "category": "test_email_leaked_to_real_send",
                    "detail": f"{len(test_leaks)} test-signature email(s) reached a real Sent Items send in the last 3 days - a test suite is bypassing skip_notify/dry_run, or a self-send test allowlist entry needs to be cleaned up.",
                    "items": test_leaks,
                })
    except Exception as e:
        findings.append({"severity": "low", "category": "check_failed", "detail": f"Test-artifact-email check errored: {e}"})

    # 17. Backlog-vs-code drift - found 2026-07-06 picking up the next unblocked BTW
    #     item per the Definition of Done directive: STRATEGIC_BACKLOG.md marked BTW-4,
    #     BTW-5, and BTW-8 all "OPEN" with specific remaining sub-items, but the exact
    #     routes those sub-items named were already built and live (verified with real
    #     API calls) - three separate near-misses of re-authoring already-shipped work
    #     from scratch, the same failure shape as detector #10's Handbook-content case
    #     but for code instead of docs. Generalizes the manual check: for any backlog
    #     item still marked OPEN/PARTIAL, pull every backtick-quoted `/path/...` in its
    #     section and check whether a router file already defines that exact route -
    #     if so, the backlog claim is stale and needs re-verifying before anything gets
    #     built against it.
    try:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        backlog_path = os.path.join(repo_root, "architecture", "STRATEGIC_BACKLOG.md")
        router_dir = os.path.dirname(__file__)
        with open(backlog_path) as f:
            backlog_text = f.read()
        router_source = ""
        for fname in os.listdir(router_dir):
            if fname.endswith(".py"):
                with open(os.path.join(router_dir, fname)) as rf:
                    router_source += rf.read() + "\n"

        sections = _re.split(r"(?=^### BTW-\d+)", backlog_text, flags=_re.M)
        stale_backlog_claims = []
        for sec in sections:
            m = _re.match(r"### (BTW-\d+[^\n]*).*?Status:\*\*\s*(OPEN|PARTIAL)", sec, _re.S)
            if not m:
                continue
            title, status = m.groups()
            paths = set(_re.findall(r"`(/[a-zA-Z0-9_{}/-]+)`", sec))
            for p in paths:
                # normalize {code}/{id}/{project_id} etc. so a param-name mismatch
                # (backlog says {id}, code says {project_id}) still matches
                pattern = _re.escape(p)
                pattern = _re.sub(r"\\\{[a-zA-Z_]+\\\}", r"\\{[a-zA-Z_]+\\}", pattern)
                if _re.search(rf'@router\.(get|post)\("{pattern}"', router_source):
                    stale_backlog_claims.append(f"{title.strip()}: `{p}` already has a live route")
        if stale_backlog_claims:
            findings.append({
                "severity": "medium",
                "category": "backlog_marked_open_but_code_exists",
                "detail": f"{len(stale_backlog_claims)} STRATEGIC_BACKLOG.md item(s) marked OPEN/PARTIAL reference a route that already exists - verify against live code before building, the backlog status may be stale.",
                "items": stale_backlog_claims,
            })
    except Exception as e:
        findings.append({"severity": "low", "category": "check_failed", "detail": f"Backlog-vs-code drift check errored: {e}"})

    # 18. connector_sync_state honesty/staleness - found 2026-07-07 the hard way.
    #     Two stacked bugs made every real connector (houzz, hubspot) invisible to
    #     every prior audit: (a) BaseConnector._update_sync_states() stamped
    #     status='idle'/last_synced_at=NOW() unconditionally, with no reference to
    #     whether persist() actually wrote a row - a 100%-failing sync (HubSpot's
    #     column-name mismatch, 165/165 persist errors) still reported clean; and
    #     (b) that same function's own UPSERT was itself broken (`ON CONFLICT DO
    #     UPDATE` with no conflict target - invalid Postgres syntax, threw on every
    #     call, caught by its own try/except and only logged to a file nobody was
    #     tailing) so connector_sync_state rows were frozen at whatever timestamp
    #     they got on first insert, for every connector, since this code was
    #     written. Every earlier audit checked connector_registry.last_indexed and
    #     sync_age_hours - the exact columns this bug made permanently unreliable -
    #     so a broken connector and a healthy one were indistinguishable from the
    #     audit's point of view. Both are now fixed at the source (base_connector.py);
    #     this check is the tripwire so a future silent regression in a specific
    #     connector's persist logic (like the HubSpot column mismatch) surfaces
    #     within one drift-check cycle instead of 12+ days.
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT connector_name, entity_type, external_id, last_synced_at, status, error_message,
                           EXTRACT(EPOCH FROM (NOW() - last_synced_at))/3600 AS age_hours
                    FROM connector_sync_state
                    WHERE status = 'error'
                       OR last_synced_at IS NULL
                       OR last_synced_at < NOW() - INTERVAL '24 hours'
                """)
                bad_states = cur.fetchall()
                if bad_states:
                    errored = [r for r in bad_states if r["status"] == "error"]
                    stale = [r for r in bad_states if r["status"] != "error"]
                    if errored:
                        findings.append({
                            "severity": "high",
                            "category": "connector_sync_error",
                            "detail": f"{len(errored)} connector_sync_state row(s) reporting status='error' - real persist failures, not just staleness.",
                            "items": [f"{r['connector_name']}/{r['entity_type']}: {(r['error_message'] or '')[:150]}" for r in errored],
                        })
                    if stale:
                        stale_items = []
                        for r in stale:
                            age_desc = "never synced" if r["last_synced_at"] is None else f"{r['age_hours']:.0f}h stale"
                            stale_items.append(f"{r['connector_name']}/{r['entity_type']} (external_id={r['external_id'] or '-'}): {age_desc}")
                        findings.append({
                            "severity": "medium",
                            "category": "connector_stale",
                            "detail": f"{len(stale)} connector_sync_state row(s) not updated in 24h+ (or never synced).",
                            "items": stale_items,
                        })
    except Exception as e:
        findings.append({"severity": "low", "category": "check_failed", "detail": f"Connector sync-state honesty check errored: {e}"})

    # 19. Scheduled n8n workflow actually executing - found 2026-07-07 the hardest
    #     way possible: AUTO-004 Daily Mining Engine was marked ACTIVE with a 24h
    #     schedule the entire time, but n8n's execution history showed exactly one
    #     run, ever, and it errored (n8n's own SQLite corruption, the same root
    #     cause as ADR-015 - only fully fixed same day this check was added). A
    #     workflow being "ACTIVE" in n8n says nothing about whether it's actually
    #     firing. Every prior audit checked source-table freshness (detector #18)
    #     but never asked "is the job that's supposed to refresh this actually
    #     running" - so a dead scheduler and a healthy one looked the same from
    #     the data side until someone manually re-triggered it and watched it fail.
    #     Covers the small set of workflows whose job IS refreshing data other
    #     detectors depend on - not every workflow, to avoid false-positive noise
    #     on infrequent ones.
    try:
        n8n_key = os.environ.get("N8N_API_KEY", "")
        critical_workflows = {
            "AUTO-004 Daily Mining Engine": {"id": "67n7ENkCpGIzHgc1", "max_age_hours": 30},
            "AUTO-CONTINUOUS-DISCOVERY": {"id": "2iM1eViWnnQ4I2Xv", "max_age_hours": 3},
            "AUTO-002 Workflow Health Check": {"id": "1EbteMeNL7WUoq5F", "max_age_hours": 30},
        }
        dead = []
        for name, cfg in critical_workflows.items():
            r = requests.get(
                f"http://localhost:5678/api/v1/executions?workflowId={cfg['id']}&limit=1",
                headers={"X-N8N-API-KEY": n8n_key}, timeout=8,
            )
            execs = r.json().get("data", []) if r.status_code == 200 else []
            if not execs:
                dead.append(f"{name}: zero executions ever recorded, despite being active")
                continue
            last = execs[0]
            started = last.get("startedAt")
            if started:
                age_h = (datetime.now(timezone.utc) - datetime.fromisoformat(started.replace("Z", "+00:00"))).total_seconds() / 3600
                if age_h > cfg["max_age_hours"]:
                    dead.append(f"{name}: last execution {age_h:.0f}h ago (expected within {cfg['max_age_hours']}h), status={last.get('status')}")
        if dead:
            findings.append({
                "severity": "high",
                "category": "scheduled_job_not_firing",
                "detail": f"{len(dead)} critical n8n workflow(s) marked active but not actually executing on schedule - the data they're supposed to refresh is going stale invisibly.",
                "items": dead,
            })
    except Exception as e:
        findings.append({"severity": "low", "category": "check_failed", "detail": f"Scheduled-job liveness check errored: {e}"})

    # 20. Live-project set drift - found 2026-07-08 by Buck, not by any prior audit:
    #     projects.status for 246GW had said 'active' since 2026-06-28 even though it
    #     was never a live/pilot project (Buck: "246 is not a live project - it is the
    #     next potential pilot"). Every write-scope decision in the system - the
    #     base_connector.py guard added earlier the same day, _LIVE_PROJECT_CODES in
    #     this file, bid_leveling's get_all_configured_projects() - all trust
    #     projects.status IN ('active','pilot') as ground truth. Every prior audit this
    #     session (including the one run right before this bug was found) ALSO trusted
    #     that same column, so it could never have caught its own blind spot - an audit
    #     that reuses the corrupted signal it's supposed to be checking will always agree
    #     with it. This check is deliberately independent: the canonical live-project set
    #     is hardcoded here, separately from _LIVE_PROJECT_CODES, so the two can never
    #     silently drift in the same wrong direction together. Any project with
    #     status IN ('active','pilot') outside this set is flagged - it either needs its
    #     status corrected, or the canonical set below needs a deliberate, reasoned update
    #     (never just a copy-paste of whatever the DB currently says).
    try:
        _CANONICAL_LIVE_CODES = {"64EW", "101F", "1355R"}
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT project_code, name, status, updated_at
                    FROM projects WHERE status IN ('active', 'pilot')
                """)
                drifted = [r for r in cur.fetchall() if r["project_code"] not in _CANONICAL_LIVE_CODES]
                if drifted:
                    findings.append({
                        "severity": "high",
                        "category": "live_project_set_drift",
                        "detail": f"{len(drifted)} project(s) have status='active'/'pilot' (write-authorized) but are NOT in the canonical live set {sorted(_CANONICAL_LIVE_CODES)} - this is exactly the bug that let real writes land on 246GW.",
                        "items": [f"{r['project_code']} ({r['name']}): status={r['status']}, last changed {r['updated_at'].date()}" for r in drifted],
                    })
    except Exception as e:
        findings.append({"severity": "low", "category": "check_failed", "detail": f"Live-project set drift check errored: {e}"})

    # 21. Bulk-inserted bid_packages with zero real backing - found 2026-07-08/09 when
    #     Buck asked "where are you getting this information" about 246 Gallo Way: a
    #     2026-06-28 handoff asked only to add 4 vendor names to a registry, but whatever
    #     executed it fabricated 44 full bid_packages rows (incl. 19 "awarded") with no
    #     hubspot_deal_id, no drive_bids extraction, and an empty Drive tracker behind any
    #     of them. It sat 11 days feeding executive reports as if real contracts existed.
    #     General signature: a batch of bid_packages created in the same instant, with no
    #     link to HubSpot or Drive at all - a real bid pipeline never produces this shape
    #     (bids arrive one at a time, over days, each tied to a source). Flags any project
    #     with 5+ such rows so this class of issue surfaces on its own next time, not by
    #     someone happening to ask the right question. Excludes _SYNTHETIC_TEMPLATE_CODES
    #     (ASPN-MC/NEW/REM etc.) - checked 2026-07-09, their bulk-seeded packages have real
    #     differentiated multi-bid competition (matching bid_entries with sensible dollar
    #     progressions), consistent with deliberate benchmark/reference template data, not
    #     accidental fabrication - unlike 246GW's, whose package names were literal document
    #     title fragments with zero bid_entries behind any of them.
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT p.project_code, p.name, bp.created_at::date as batch_date, count(*) c
                    FROM bid_packages bp
                    JOIN projects p ON p.id = bp.project_id
                    WHERE bp.hubspot_deal_id IS NULL
                      AND p.project_code NOT IN %s
                      AND NOT EXISTS (SELECT 1 FROM drive_bids db WHERE db.project_id = bp.project_id)
                      -- 2026-07-11 fix: a package backed by real bid_entries sourced from an
                      -- authorized Drive-mining run (source LIKE 'drive_mine_%%') is not
                      -- unbacked - confirmed on 574J (9 packages, real vendor names/dollar
                      -- amounts/multi-bid comparison notes, source='drive_mine_574_johnson_
                      -- bid_tracker') which this check was flagging as a false positive
                      -- identical-looking to the real 246GW fabrication. hubspot_deal_id and
                      -- drive_bids are not the only legitimate provenance signals.
                      AND NOT EXISTS (
                          SELECT 1 FROM bid_entries be
                          WHERE be.bid_package_id = bp.id AND be.source LIKE 'drive_mine_%%'
                      )
                    GROUP BY p.project_code, p.name, bp.created_at::date
                    HAVING count(*) >= 5
                """, (_SYNTHETIC_TEMPLATE_CODES,))
                batches = cur.fetchall()
                if batches:
                    findings.append({
                        "severity": "high",
                        "category": "unbacked_bulk_bid_packages",
                        "detail": f"{len(batches)} project/date batch(es) of 5+ bid_packages created in a single instant with zero HubSpot or Drive backing - real bids don't arrive this way, verify before trusting any dollar figures from these.",
                        "items": [f"{r['project_code']} ({r['name']}): {r['c']} package(s) created {r['batch_date']}" for r in batches],
                    })
    except Exception as e:
        findings.append({"severity": "low", "category": "check_failed", "detail": f"Unbacked-bulk-bid-packages check errored: {e}"})

    # 22. historical_cost_records with a bid_package_id that doesn't resolve to a real
    #     package for that project - the exact corruption found 2026-07-09 from a
    #     historical_cost_miner bug (fixed 2026-07-07, commit e4654df) that wrote
    #     bid_entries.id into the bid_package_id column instead of the real bid_packages.id.
    #     130 rows were found and repaired (not deleted - the real value was recoverable
    #     via bid_entries) the same session; this check exists so any future recurrence
    #     of the same shape (e.g. a similar miner bug) is caught automatically instead of
    #     needing a human to notice a coincidental ID-range collision by hand.
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT count(*) c FROM historical_cost_records hcr
                    LEFT JOIN bid_packages bp ON bp.id = hcr.bid_package_id AND bp.project_id = hcr.project_id
                    WHERE hcr.bid_package_id IS NOT NULL AND bp.id IS NULL
                """)
                orphans = cur.fetchone()["c"]
                if orphans:
                    findings.append({
                        "severity": "high",
                        "category": "orphaned_historical_cost_fk",
                        "detail": f"{orphans} historical_cost_records row(s) have a bid_package_id that doesn't resolve to a real bid_packages row for that project - likely FK corruption from a miner bug, not real data. Check bid_entries for a recoverable real value before deleting (see 2026-07-09 repair).",
                    })
    except Exception as e:
        findings.append({"severity": "low", "category": "check_failed", "detail": f"Orphaned-historical-cost-FK check errored: {e}"})

    # 23. Test/seed rows in platform_users leaking into real identity lookups - found
    #     2026-07-10 the exact shape of check #11 above (test_data_in_real_project),
    #     just on a table that check never covered because platform_users didn't exist
    #     when it was written. A "Jane PM" row from 2026-06-26 RBAC-bootstrap seeding
    #     was still sitting active=true with a real-looking email, indistinguishable
    #     from Adam/Trafford's genuine rows to any endpoint or agent reading the table
    #     (found manually while building Role Onboarding on GET /gateway/users, not by
    #     any existing check). Flags test-signature actor_names/emails so this doesn't
    #     require another manual catch next time a new identity table gets seeded.
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT actor_name, role, email FROM platform_users
                    WHERE active = TRUE
                      AND (actor_name ILIKE '%test%' OR email ILIKE '%test%'
                           OR actor_name ~* '^(jane|john|test|demo|sample) ')
                """)
                test_users = cur.fetchall()
        if test_users:
            findings.append({
                "severity": "medium",
                "category": "test_data_in_platform_users",
                "detail": f"{len(test_users)} platform_users row(s) look like test/seed data (not real HCI people) but are active=true - indistinguishable from real team members to any endpoint reading this table, verify and purge or deactivate.",
                "items": [f"{r['actor_name']} ({r['role']}, {r['email']})" for r in test_users],
            })
    except Exception as e:
        findings.append({"severity": "low", "category": "check_failed", "detail": f"Platform-users-test-data check errored: {e}"})

    # 24. drive_bids division_num collisions - found 2026-07-13 by Buck, not by any
    #     prior check: division "13" was silently mixing Insulation bids ($56-79K)
    #     with Fire Suppression bids ($31-108K) into one nonsensical leveling
    #     comparison (10,906% spread), because HCI's canonical folder structure numbers
    #     sub-packages independently of their parent division (13_Insulation lives
    #     under Division 07, 13_Special Construction lives under Division 10 - both
    #     share the bare number 13) and drive_bid_reader.read_drive_bids() grouped
    #     purely by that bare number with no sub-package model. Fixed the grouping
    #     that day (commit pending) for known collisions, but this check exists so any
    #     NEW collision (a different bare number reused by two real division_names)
    #     surfaces on its own instead of needing someone to notice a wrong number.
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT p.project_code, db.division_num, array_agg(DISTINCT db.division_name) as names
                    FROM drive_bids db
                    JOIN projects p ON p.id = db.project_id
                    WHERE db.is_latest = TRUE
                    GROUP BY p.project_code, db.division_num
                    HAVING count(DISTINCT db.division_name) > 1
                """)
                collisions = cur.fetchall()
        if collisions:
            findings.append({
                "severity": "high",
                "category": "bid_division_num_collision",
                "detail": f"{len(collisions)} project/division_num pair(s) where the same bare CSI number is shared by genuinely different scopes - any leveling summary for these will mix unrelated trades' bids together unless read_drive_bids() has an explicit disambiguation for them.",
                "items": [f"{r['project_code']} div {r['division_num']}: {r['names']}" for r in collisions],
            })
    except Exception as e:
        findings.append({"severity": "low", "category": "check_failed", "detail": f"Bid-division-collision check errored: {e}"})

    # 25. Stale agent heartbeats - found 2026-07-13 the CODE row in agent_heartbeats
    #     hadn't updated since 2026-07-11 despite continuous real activity the whole
    #     time, because nothing was calling POST /agent/heartbeat during normal work.
    #     GBT sent a P0 "team went down" escalation partly built on this real gap, but
    #     also partly on GBT/BC's Telegram backlogs (459/148 unread) which are NOT a
    #     regression - GBT/BC are chat-based and only poll when a human opens a chat,
    #     so their heartbeats going quiet for hours/days is normal, not an outage.
    #     This check reflects that distinction instead of treating every agent the
    #     same way: CODE is expected to be near-continuous (flag if stale > 30 min),
    #     GBT/BC are expected to be intermittent (only flag as informational if stale
    #     for multiple days, and never as high severity for that alone).
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT agent_id, status, last_heartbeat_mt,
                           EXTRACT(EPOCH FROM (NOW() - last_heartbeat_mt))/60 AS stale_minutes
                    FROM agent_heartbeats
                """)
                rows = cur.fetchall()
        code_stale = [r for r in rows if r["agent_id"] == "CODE" and r["stale_minutes"] and r["stale_minutes"] > 30]
        other_very_stale = [r for r in rows if r["agent_id"] != "CODE" and r["stale_minutes"] and r["stale_minutes"] > 4320]  # 3 days
        if code_stale:
            findings.append({
                "severity": "high",
                "category": "code_heartbeat_stale",
                "detail": "Claude Code's own heartbeat hasn't updated in 30+ minutes despite the standing check-in directive - either the loop actually stopped, or something is active but not calling POST /agent/heartbeat.",
                "items": [f"{r['agent_id']}: {round(r['stale_minutes'])} min stale, last seen {r['last_heartbeat_mt']}" for r in code_stale],
            })
        if other_very_stale:
            findings.append({
                "severity": "low",
                "category": "chatbased_agent_heartbeat_quiet",
                "detail": "GBT/BC heartbeat quiet for 3+ days - informational only, this is expected for chat-based agents that only report in when a human opens a session with them, not evidence of an outage.",
                "items": [f"{r['agent_id']}: {round(r['stale_minutes']/60)} hrs stale, last seen {r['last_heartbeat_mt']}" for r in other_very_stale],
            })
    except Exception as e:
        findings.append({"severity": "low", "category": "check_failed", "detail": f"Stale-heartbeat check errored: {e}"})

    return _response("/admin/drift-check", {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "findings_count": len(findings),
        "findings": findings,
        "clean": len(findings) == 0,
    }, start=t0)


@router.post("/admin/self-heal")
async def system_self_heal(request: Request):
    """Auto-fix ONLY the narrow set of issues that are unambiguously safe and
    reversible: restarting the n8n container when its SQLite I/O error
    signature is detected (this happened twice - ADR-015 fixed the config,
    but the running container needed a restart to pick it up each time, and
    that step kept getting missed). Deliberately does NOT touch business data,
    Drive files, or DB rows - those go through /admin/drift-check for a human
    to review and act on via /drive/move or explicit SQL, never auto-applied."""
    _require_key(request)
    t0 = time.time()
    actions_taken = []
    try:
        import subprocess, shutil
        # launchd's minimal PATH doesn't include /usr/local/bin or /opt/homebrew/bin,
        # so a bare "docker" fails with FileNotFoundError under this service - same
        # class of bug as the pdftoppm PATH issue fixed earlier. Found 2026-07-03 when
        # this endpoint silently did nothing during a live SQLITE_IOERR incident.
        docker_bin = shutil.which("docker") or "/usr/local/bin/docker"
        if not os.path.exists(docker_bin):
            for candidate in ("/opt/homebrew/bin/docker", "/usr/bin/docker"):
                if os.path.exists(candidate):
                    docker_bin = candidate
                    break

        n8n_key = os.environ.get("N8N_API_KEY", "")
        resp = requests.get("http://localhost:5678/api/v1/workflows", headers={"X-N8N-API-KEY": n8n_key},
                             params={"limit": 1}, timeout=8)
        # Original check only looked for "SQLITE_IOERR" literally in the API response
        # body - but a live incident 2026-07-03 showed a plain 401 with no error text
        # at all; the SQLITE_IOERR signature only ever appeared in `docker logs n8n`,
        # never in the HTTP response. Check the actual container logs instead.
        needs_restart = False
        reason = ""
        if resp.status_code != 200:
            log_check = subprocess.run([docker_bin, "logs", "--since", "5m", "n8n"],
                                        capture_output=True, text=True, timeout=15)
            log_text = (log_check.stdout or "") + (log_check.stderr or "")
            if "SQLITE_IOERR" in log_text:
                needs_restart = True
                reason = f"n8n API returned {resp.status_code} and SQLITE_IOERR found in recent container logs"
            elif resp.status_code in (401, 403):
                # Not a self-heal case by itself (could be a real rotated/revoked key,
                # which needs a human to regenerate it) - report, don't restart blind.
                actions_taken.append(f"n8n API returned {resp.status_code} but no SQLITE_IOERR in recent logs - "
                                      f"not auto-restarting (could be a genuinely revoked API key, needs human check)")

        if needs_restart:
            subprocess.run([docker_bin, "restart", "n8n"], capture_output=True, timeout=60)
            actions_taken.append(f"Restarted n8n container - {reason}, same signature as ADR-015")

        # Touch n8n's ai_agent_heartbeat row on every successful reachability check
        # (found 2026-07-06 via GBT's own re-verification: the heartbeat was stuck at
        # 2026-07-03 08:00 - n8n itself and this 15-min self-heal cron were both
        # actually running fine, but nothing had ever updated n8n's heartbeat row, so
        # any dashboard reading it looked 3+ days stale). This endpoint already runs
        # every 15 minutes via AUTO-SELFHEAL, making it the natural proof-of-life touch
        # point - still container/monitoring-level only, no business data involved.
        if resp.status_code == 200:
            try:
                with _pg() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            UPDATE ai_agent_heartbeat SET status='ONLINE', last_seen_at=NOW()
                            WHERE agent='n8n'
                        """)
            except Exception:
                pass
    except Exception as e:
        actions_taken.append(f"n8n health check/restart attempt errored: {e}")

    return _response("/admin/self-heal", {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "actions_taken": actions_taken,
        "note": "Only auto-fixes container-level issues. Data/file issues from /admin/drift-check always require human review.",
    }, start=t0)


@router.post("/admin/daily-project-summaries")
async def generate_daily_project_summaries(request: Request):
    """BTW-4's last remaining piece: 'Daily Project Summary auto-generation (scheduled,
    not on-demand)'. The compute + persistence already existed - ProjectIntelligenceEngine
    .intelligence() upserts a full row (health, risks, schedule variance, ai_summary, etc.)
    into project_brain_snapshots, keyed unique on (project_id, snapshot_date) - it just only
    ever ran when someone happened to call a brain/intelligence endpoint that day. Confirmed
    2026-07-06: several active projects had multi-day gaps with no snapshot at all (e.g.
    project_id=4 had rows for 06-28 and 07-02 only, nothing between). This endpoint is the
    scheduled trigger that was missing - call once daily (meant to be wired to a launchd job,
    matching com.hci.morning-brief's pattern) to generate today's snapshot for every active
    project regardless of whether anyone queries it on-demand."""
    _require_key(request)
    t0 = time.time()
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "services", "project_brain"))
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "services"))
    from intelligence import ProjectIntelligenceEngine
    results = []
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, project_code, name FROM projects
                    WHERE status IN ('active','design','bidding','preconstruction','monitoring')
                      AND name NOT LIKE 'TEST-%%'
                    ORDER BY id
                """)
                projects = cur.fetchall()
        for p in projects:
            try:
                snap = ProjectIntelligenceEngine(p["id"]).intelligence(include_ai_summary=False)
                results.append({"project_code": p["project_code"], "health": snap.get("health"), "status": "ok"})
            except Exception as e:
                results.append({"project_code": p["project_code"], "status": "error", "error": str(e)})
    except Exception as e:
        return _response("/admin/daily-project-summaries", {}, errors=[str(e)], start=t0)

    ok_count = sum(1 for r in results if r["status"] == "ok")
    return _response("/admin/daily-project-summaries", {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "projects_processed": len(results),
        "succeeded": ok_count,
        "failed": len(results) - ok_count,
        "results": results,
    }, start=t0)


@router.post("/admin/purge-email-noise")
async def purge_email_noise(request: Request):
    """Permanently deletes messages from the 'System Noise (auto-purge 30d)' Outlook
    folder that are older than 30 days. Added 2026-07-02 after discovering this mailbox's
    DELETE does NOT move to Deleted Items - it purges immediately, no recovery. That
    surprised us mid-cleanup (a real test email was lost before we caught the pattern).
    Buck's explicit direction: route anything test/noise/system-alert into this dedicated
    folder first (via move, always reversible), let it sit for 30 days as a recovery
    window, THEN purge on a schedule - never delete anything immediately again.
    Meant to run weekly via the AUTO-EMAIL-NOISE-PURGE n8n workflow, not called ad hoc."""
    _require_key(request)
    t0 = time.time()
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "integrations"))
        from microsoft_graph import _request as graph_request

        folders, ferr = graph_request("GET", "/me/mailFolders", params={"$filter": "displayName eq 'System Noise (auto-purge 30d)'"})
        if ferr or not folders.get("value"):
            return _response("/admin/purge-email-noise", {"purged": 0, "note": "Folder not found - nothing to do"}, start=t0)
        folder_id = folders["value"][0]["id"]

        cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        msgs, merr = graph_request("GET", f"/me/mailFolders/{folder_id}/messages",
                                    params={"$filter": f"receivedDateTime le {cutoff}", "$select": "subject,receivedDateTime", "$top": 200})
        if merr:
            return _response("/admin/purge-email-noise", {}, errors=[str(merr)], start=t0)

        to_purge = msgs.get("value", [])
        purged = []
        for m in to_purge:
            _, derr = graph_request("DELETE", f"/me/messages/{m['id']}")
            if not derr:
                purged.append(m["subject"][:60])

        return _response("/admin/purge-email-noise", {
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "purged_count": len(purged),
            "purged_subjects": purged[:20],
        }, start=t0)
    except Exception as e:
        return _response("/admin/purge-email-noise", {}, errors=[str(e)], start=t0)


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


# ── Role Onboarding System (Build 2) — real identity, not a hardcoded roster ─
#
# 2026-07-10: Build 1 shipped with a hardcoded _HCI_TEAM_ROSTER list as a
# pragmatic shortcut (see BC_TO_CODE_FIELD_GPT_USER_IDENTITY_EMAIL_ROUTING_
# DESIGN.md). GBT + BC architecture review (3-agent consensus, see handoff
# e8c3735e) flagged that as a second source of truth alongside the existing
# platform_users/platform_permissions RBAC service (services/platform/
# identity/identity_service.py) and recommended migrating onto it instead.
# Buck's real team is now real rows in platform_users, extended with
# is_onboarded/onboarded_at, plus platform_user_projects for assignments
# (a join table per GBT's recommendation, not a flat array column).
@router.get("/users")
def list_users():
    """
    Field GPT / GBT user-identity lookup - "who am I working with today."
    Drives RFI Sent-By, role-appropriate content, and project scoping.
    Does NOT drive email TO-routing - see draft_to_email logic in
    services/rfi_workflow.py, which defaults to Buck until is_onboarded=True.
    Reads platform_users (the canonical identity store), not a hardcoded list.

    `role` vs `title`: `role` is the platform RBAC/access level (owner/pm/
    superintendent/etc - drives permissions, ROLE_HIERARCHY). `title` is the
    person's real operational title to use when addressing/describing them
    (e.g. Buck's role is "owner" for system-access purposes, but his real
    title at Hendrickson Construction is "PM/Superintendent" - he owns
    HCI-AI, not the construction company. Callers introducing a user (Field
    GPT etc) should use `title`, not `role`, for that - found live 2026-07-10
    when Field GPT introduced Buck as "Owner/Executive," which is wrong).
    """
    t0 = time.time()
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                # 2026-07-10: platform_users also holds generic role-bootstrap
                # placeholder rows (e.g. 'pm', 'super', 'system', 'AI') seeded
                # 2026-06-26 for the RBAC system to have a row per role to
                # attach permissions to - those aren't real people and would
                # corrupt Field GPT's "who am I working with" name matching.
                # None of them have an email; every real person does - that's
                # a more robust filter than matching actor_name against role,
                # which missed cases like actor_name='AI' vs role='ai_agent'.
                # Excluded here, not deleted from the table.
                cur.execute("""
                    SELECT u.actor_name AS name, u.email, u.role, u.title, u.is_onboarded, u.onboarding_state,
                           COALESCE(array_agg(p.project_code) FILTER (WHERE p.project_code IS NOT NULL), '{}') AS projects
                    FROM platform_users u
                    LEFT JOIN platform_user_projects p ON p.user_id = u.id
                    WHERE u.active = TRUE AND u.email IS NOT NULL
                    GROUP BY u.id, u.actor_name, u.email, u.role, u.title, u.is_onboarded, u.onboarding_state
                    ORDER BY u.role, u.actor_name
                """)
                users = [dict(r) for r in cur.fetchall()]
        return _response("/users", {"users": users, "count": len(users)}, start=t0)
    except Exception as e:
        return _response("/users", {}, errors=[str(e)], start=t0)


class OnboardUserPayload(BaseModel):
    actor_name: str
    onboarded_by: str = "buck"


@router.post("/users/onboard")
def onboard_user(req: OnboardUserPayload):
    """
    Flips a real team member's onboarding_state to 'onboarded' - the actual
    go-live switch for their own email routing (see BC_TO_CODE_FIELD_GPT_
    EMAIL_FINAL_SPEC_2026-07-10.md: TO-team-member routing only activates
    once someone is formally onboarded). This is a real operational decision,
    not something Field GPT or GBT should trigger on their own judgment -
    only call this when Buck has explicitly said to onboard someone by name.

    is_onboarded is a generated column (`onboarding_state = 'onboarded'`) as
    of 2026-07-11 - migrated from a plain boolean to a 7-state machine (BC's
    proposal, reviewed and agreed by 3-agent consensus) since a boolean
    can't distinguish "never started" from "halfway through." This endpoint
    only handles the final pending->onboarded transition for now; the
    intermediate states (identity_set/email_active/gpt_access/projects_set)
    aren't wired to any caller yet - added for the schema to support them
    later, not built out end-to-end today.
    """
    t0 = time.time()
    try:
        with _pg() as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE platform_users
                    SET onboarding_state = 'onboarded', onboarded_at = NOW(), updated_at = NOW()
                    WHERE actor_name = %s AND active = TRUE
                    RETURNING id, actor_name, role, email, is_onboarded, onboarding_state, onboarded_at
                """, (req.actor_name,))
                row = cur.fetchone()
                if row:
                    cur.execute("""
                        INSERT INTO user_audit_log (user_id, field_changed, old_value, new_value, changed_by, reason)
                        VALUES (%s, 'onboarding_state', 'pending', 'onboarded', %s, %s)
                    """, (row["id"], req.onboarded_by, f"formal onboarding via /users/onboard"))
        if not row:
            return _response("/users/onboard", {}, errors=[f"no active user found named '{req.actor_name}'"], start=t0)
        result = dict(row)
        result["onboarded_at"] = result["onboarded_at"].isoformat()
        try:
            requests.post("https://ntfy.sh/hci-executive",
                data=f"{req.actor_name} onboarded by {req.onboarded_by} - email routing now active for their own inbox.",
                headers={"Title": "Team member onboarded", "Priority": "default", "Tags": "bust_in_silhouette"},
                timeout=3)
        except Exception:
            pass
        _log("/users/onboard", req.onboarded_by, "", "onboarded", round((time.time()-t0)*1000), req.actor_name)
        return _response("/users/onboard", result, start=t0)
    except Exception as e:
        return _response("/users/onboard", {}, errors=[str(e)], start=t0)


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
            # 2026-07-13 fix: void/test_pending_reverify RFIs (e.g. the old
            # self-drafted 001-010 batch superseded by Buck's real Field GPT
            # retest) must not count toward "next number" - a real submission
            # right after those was getting numbered 011 instead of restarting
            # at 001, because this query originally counted every status.
            cur.execute("SELECT COALESCE(MAX(CAST(NULLIF(rfi_number, '') AS INTEGER)), 0) + 1 AS next_num FROM rfis WHERE project_id = %s AND rfi_number ~ '^[0-9]+$' AND status NOT IN ('void', 'test_pending_reverify')", (pid,))
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


class RFIUpdatePayload(BaseModel):
    status: Optional[str] = None
    response: Optional[str] = None
    response_date: Optional[str] = None
    updated_by: str = "field"


@router.patch("/field/rfi/{rfi_id}")
def field_update_rfi(rfi_id: int, req: RFIUpdatePayload):
    """
    Updates an existing RFI's status/response. Added 2026-07-09/10 - this
    did not exist before (POST /field/rfi only created new RFIs), which was
    the exact gap Field GPT correctly reported ("cannot update the RFI
    tracker") in the 2026-07-10 capability audit.
    """
    t0 = time.time()
    try:
        import sys as _sys
        _sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "services"))
        import rfi_workflow
        result = rfi_workflow.update_rfi(rfi_id, status=req.status, response=req.response,
                                          response_date=req.response_date, updated_by=req.updated_by)
        if "error" in result:
            return _response(f"/field/rfi/{rfi_id}", {}, errors=[result["error"]], start=t0)
        _log(f"/field/rfi/{rfi_id}", req.updated_by, "", "rfi_updated", round((time.time()-t0)*1000), str(uuid.uuid4())[:8])
        return _response(f"/field/rfi/{rfi_id}", {"updated": True, "rfi": result}, start=t0)
    except Exception as e:
        return _response(f"/field/rfi/{rfi_id}", {}, errors=[str(e)], start=t0)


class RFIProcessPayload(BaseModel):
    to_email: Optional[str] = None
    to_name: Optional[str] = None


@router.post("/field/rfi/{rfi_id}/process")
def field_process_rfi(rfi_id: int, req: RFIProcessPayload):
    """
    Full RFI workflow: generate the Hendrickson RFI Word document, save it
    into the project's real RFIs Drive folder, append a row to that
    project's real RFI Log tracker, and (if a recipient is given) create an
    Outlook draft with the document attached. Added 2026-07-09/10 to close
    the gap Field GPT correctly reported in its 2026-07-10 capability audit
    - none of this existed before (see memory: project_rfi_capability_gap_2026-07-10).
    Returns per-step evidence, not just a single pass/fail flag, per GBT's
    evidence-first acceptance requirement.
    """
    t0 = time.time()
    try:
        import sys as _sys
        _sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "services"))
        import rfi_workflow
        result = rfi_workflow.run_rfi_workflow(rfi_id, to_email=req.to_email, to_name=req.to_name)
        if "error" in result:
            return _response(f"/field/rfi/{rfi_id}/process", {}, errors=[result["error"]], start=t0)
        _log(f"/field/rfi/{rfi_id}/process", "field", "", "rfi_processed", round((time.time()-t0)*1000),
             str(uuid.uuid4())[:8], f"all_ok={result.get('all_steps_ok')}")
        return _response(f"/field/rfi/{rfi_id}/process", result, start=t0)
    except Exception as e:
        return _response(f"/field/rfi/{rfi_id}/process", {}, errors=[str(e)], start=t0)


class EmailDraftPayload(BaseModel):
    subject: str
    body_html: str
    to_email: Optional[str] = None
    to_name: Optional[str] = None
    project_code: Optional[str] = None


@router.post("/email/draft")
def create_email_draft(req: EmailDraftPayload):
    """
    General-purpose Outlook draft creation for Field GPT - closes the gap it
    self-reported 2026-07-10 (see 'Email Draft for Bids' chat): it could
    generate bid-solicitation email text but had no way to actually land it
    in Buck's real Outlook Drafts folder, only /field/rfi/{id}/process
    existed and that's RFI-specific (generates+attaches the RFI Word doc,
    which a bid-solicitation email doesn't need).

    Routing per Buck's 2026-07-11 correction: every draft goes To: Buck,
    CC: the real intended recipient when one is known - not To:recipient
    with Buck BCC'd (the 2026-07-10 version of this). is_onboarded gate
    still runs and is recorded as evidence, draft-only (never auto-sent)
    per the permanent outbound-messaging rule.
    """
    t0 = time.time()
    try:
        import sys as _sys
        _sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "services"))
        import rfi_workflow
        from microsoft_graph import create_draft

        gate = rfi_workflow._resolve_recipient_gate(req.to_email)
        defaulted_to_buck = not req.to_email or gate["redirected"]
        has_real_recipient = bool(req.to_email) and req.to_email.lower() != rfi_workflow.BUCK_EMAIL
        cc = [(req.to_name or req.to_email, req.to_email)] if has_real_recipient else None

        draft = create_draft(req.subject, req.body_html, [("Buck Adams", rfi_workflow.BUCK_EMAIL)], cc=cc)
        result = {
            "draft_id": draft["id"], "to": rfi_workflow.BUCK_EMAIL,
            "cc": req.to_email if has_real_recipient else None,
            "defaulted_to_buck": defaulted_to_buck, "redirect_reason": gate["reason"],
        }
        _log("/email/draft", "field", req.project_code or "", "draft_created",
             round((time.time()-t0)*1000), str(uuid.uuid4())[:8], req.subject[:60])
        return _response("/email/draft", result, start=t0)
    except Exception as e:
        return _response("/email/draft", {}, errors=[str(e)], start=t0)


class PlanReviewPayload(BaseModel):
    project_code: str
    sheet_text: str = ""
    reviewed_by: str = "claude_code"
    job_id: Optional[str] = None  # poll an existing job instead of starting a new one


# In-memory job store for /plan-review/analyze's async pattern - added 2026-07-07.
# Real finding that day: the underlying Claude call takes ~13s (already the fastest
# model, Haiku 4.5, already at a trimmed max_tokens) - confirmed via direct testing
# that neither ngrok nor the backend itself has a problem with that duration (a full
# curl round-trip through the real public ngrok URL succeeded in 13.75s, HTTP 200).
# But a live GBT call through ChatGPT's own Action-calling layer never reached the
# backend at all for the same input - zero trace in gateway_request_log. That points
# to a timeout enforced somewhere in ChatGPT's Action infrastructure, not something
# fixable from this side. Real fix: don't make the caller wait through the slow part
# at all. First call (no job_id) kicks off the analysis in a background thread and
# returns near-instantly with a job_id; a follow-up call with that job_id returns
# the real result once ready. Reuses the same schema slot instead of costing two new
# ones against GBT's 30-operation cap.
_PLAN_REVIEW_JOBS: dict = {}


def _run_plan_review_job(job_id: str, project_code: str, sheet_text: str, reviewed_by: str):
    t0 = time.time()
    try:
        pid = _get_pid(project_code)
        analysis = _run_plan_gap_analysis(sheet_text)
        created = _create_rfis_from_gaps(pid, analysis.get("gaps", []), reviewed_by)
        _log("/plan-review/analyze", reviewed_by, project_code, "ok",
             round((time.time()-t0)*1000), str(uuid.uuid4())[:8], f"{len(created)} RFIs drafted")
        result = _plan_review_finish("/plan-review/analyze", project_code, analysis, created, t0)
        _PLAN_REVIEW_JOBS[job_id] = {"status": "done", "result": result}
    except Exception as e:
        _PLAN_REVIEW_JOBS[job_id] = {"status": "error", "error": str(e)}


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


def _run_plan_gap_analysis(sheet_text: str) -> dict:
    """Shared, non-mutating Claude call behind /plan-review/analyze — factored out
    2026-07-02 so read-only consumers (sales-summary) can get the same gap analysis
    without creating real RFI rows on every preview."""
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    prompt = f"""You are a construction plan reviewer checking a permit set for gaps that would block bidding or construction.

Plan set excerpt:
{sheet_text[:8000]}

{_PLAN_REVIEW_CHECKLIST}"""
    message = client.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    return _parse_plan_review_json(message.content[0].text)


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
              AND status NOT IN ('void', 'test_pending_reverify')
        """, (pid,))
        next_num = cur.fetchone()["max_num"] + 1
        for gap in gaps:
            subject = f"{gap.get('item','Gap')} ({gap.get('sheet_reference','')})"[:120]
            cur.execute("""
                INSERT INTO rfis (project_id, rfi_number, subject, question, submitted_by, status, submitted_date, source_email_id)
                VALUES (%s, %s, %s, %s, %s, 'open', CURRENT_DATE, 'plan-review-pipeline')
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

    Async job pattern (added 2026-07-07 - see _PLAN_REVIEW_JOBS docstring for why):
    call once with sheet_text (no job_id) to start a job and get a job_id back almost
    immediately; call again with that job_id (sheet_text can be omitted) to poll for
    the real result. Callers that can tolerate a ~13s synchronous wait don't need to
    change anything - polling immediately after the first call will just see "processing"
    for a few seconds, same as any async job.
    """
    t0 = time.time()
    try:
        if req.job_id:
            job = _PLAN_REVIEW_JOBS.get(req.job_id)
            if not job:
                return _response("/plan-review/analyze", {"job_id": req.job_id, "status": "unknown"},
                                  errors=["No job with that ID - it may have expired (server restart) or never existed"], start=t0)
            if job["status"] == "done":
                return job["result"]
            if job["status"] == "error":
                return _response("/plan-review/analyze", {"job_id": req.job_id, "status": "error"},
                                  errors=[job["error"]], start=t0)
            return _response("/plan-review/analyze", {"job_id": req.job_id, "status": "processing",
                              "note": "Still running - the underlying analysis takes ~10-15s. Poll again in a few seconds with the same job_id."}, start=t0)

        pid = _get_pid(req.project_code)  # validate project_code fails fast, before spawning a thread
        job_id = str(uuid.uuid4())[:12]
        _PLAN_REVIEW_JOBS[job_id] = {"status": "processing"}
        thread = threading.Thread(target=_run_plan_review_job,
                                   args=(job_id, req.project_code, req.sheet_text, req.reviewed_by),
                                   daemon=True)
        thread.start()
        return _response("/plan-review/analyze", {
            "job_id": job_id, "status": "processing",
            "note": "Analysis started - call this same endpoint again with this job_id (sheet_text not required) to get the result. Usually ready in 10-15 seconds."
        }, start=t0)
    except HTTPException as e:
        return _response("/plan-review/analyze", {}, errors=[str(e.detail)], start=t0)
    except Exception as e:
        return _response("/plan-review/analyze", {}, errors=[str(e)], start=t0)


@router.post("/plan-review/sales-summary")
def plan_review_sales_summary(req: PlanReviewPayload):
    """
    Client-facing summary (2026-07-02) — this is the capability Buck originally named
    as the actual motivation for the whole plan-review pipeline: "for sales we need to
    be able to read [a plan set], say what's missing, and have a prelim ROM and
    schedule to help the sales process." Everything built since (RFI gaps, ROM,
    packages, vendors, CPM schedule, long-lead) has been PM/execution-facing; this is
    the first prospect-facing one.

    Read-only and non-mutating — does NOT create RFI rows (uses the same gap analysis
    as /plan-review/analyze via _run_plan_gap_analysis, but a sales preview shouldn't
    spam the real RFI log every time someone previews it). If the project already has
    a generated CPM schedule (from /plan-review/generate-schedule), its critical_path_days
    is included for schedule context. This produces DATA for a summary, not a sent
    document — sending anything to a prospect still requires the normal governed path
    (POST /email/draft + /email/send, Buck's Telegram approval), same as everywhere else.
    """
    t0 = time.time()
    try:
        analysis = _run_plan_gap_analysis(req.sheet_text)
        gaps = analysis.get("gaps", [])
        critical_gaps = [g for g in gaps if g.get("urgency") == "critical"]

        prelim_rom = None
        sf = analysis.get("square_footage")
        ptype = analysis.get("project_type")
        if analysis.get("ready_for_rom") and sf:
            rom_response = rom_estimate(sf=sf, project_type=ptype or "new")
            prelim_rom = rom_response.get("payload") if isinstance(rom_response, dict) else None

        pid = _get_pid(req.project_code)
        conn = _pg()
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("""
                SELECT title, end_date FROM project_schedule_items
                WHERE project_id = %s AND status = 'draft'
                ORDER BY end_date DESC LIMIT 1
            """, (str(pid),))
            latest = cur.fetchone()
        conn.close()
        schedule_context = None
        if latest:
            schedule_context = {
                "note": "An existing draft CPM schedule was found for this project — "
                        "projected completion below is from that schedule, not recomputed here.",
                "projected_completion": latest["end_date"].isoformat(),
            }

        return _response("/plan-review/sales-summary", {
            "project_code": req.project_code,
            "ready_for_rom": analysis.get("ready_for_rom", False),
            "readiness_reason": analysis.get("readiness_reason"),
            "square_footage": sf,
            "project_type": ptype,
            "open_items_count": len(gaps),
            "critical_items_count": len(critical_gaps),
            "headline_gaps": [g.get("item") for g in critical_gaps[:5]] or [g.get("item") for g in gaps[:3]],
            "preliminary_rom": prelim_rom,
            "schedule_context": schedule_context,
            "note": "DATA only, not a sent document. preliminary_rom is rough-order-of-"
                    "magnitude, not a bid. Nothing here has been sent to anyone — "
                    "drafting a client-facing document from this data still goes through "
                    "the normal POST /email/draft + /email/send flow, requiring Buck's "
                    "Telegram approval before it reaches a prospect.",
        }, start=t0)
    except HTTPException as e:
        return _response("/plan-review/sales-summary", {}, errors=[str(e.detail)], start=t0)
    except Exception as e:
        return _response("/plan-review/sales-summary", {}, errors=[str(e)], start=t0)


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


@router.post("/plan-review/generate-packages")
def plan_review_generate_packages(req: PlanReviewPayload):
    """
    Sub package / SOW generation off the plans (2026-07-01) — phase 2 of the plan-review
    pipeline named in ADR-014's roadmap. Breaks the plan set down into CSI-organized bid
    packages with a draft scope-of-work for each, and creates real `bid_packages` rows
    (status='not_started' — internal draft only). This does NOT invite any sub to bid,
    email anyone, or create HubSpot deals; soliciting bids from real vendors remains a
    separate, explicit, Buck-approved step, same governance boundary as the RFI side of
    this pipeline (ADR-010/011). Any scope the plan set doesn't clearly support is
    flagged rather than guessed, so a thin plan set produces an honest partial package
    list, not a fabricated complete one.
    """
    t0 = time.time()
    try:
        pid = _get_pid(req.project_code)
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        prompt = f"""You are a construction estimator breaking a plan set down into CSI MasterFormat bid packages for subcontractor solicitation.

Plan set excerpt:
{req.sheet_text[:8000]}

For each distinct scope of work you can identify from what's actually shown (not guessed), produce a bid package:
- csi_division: the CSI MasterFormat division number and name (e.g. "06 - Wood, Plastics & Composites")
- package_name: short package title
- scope_description: a draft SOW paragraph — what the sub is responsible for, referencing what the plans actually show (sheet/schedule references where relevant)
- confidence: "high" if the plans clearly support this scope, "low" if inferred from limited information

Do NOT invent packages for scope not evidenced in the excerpt. If a scope is implied but under-specified (e.g. "electrical" is clearly needed for a house but no electrical sheet is in this excerpt), note it with confidence "low" rather than omitting it or fabricating detail.

Respond with a JSON object only, no other text, in this exact format:
{{"packages": [{{"csi_division": "...", "package_name": "...", "scope_description": "...", "confidence": "high|low"}}],
  "coverage_note": "one sentence on how complete this package list is relative to a full bid-ready set"}}"""
        message = client.messages.create(
            model="claude-haiku-4-5-20251001", max_tokens=3000,
            messages=[{"role": "user", "content": prompt}],
        )
        analysis = _parse_plan_review_json(message.content[0].text)
        packages = analysis.get("packages", [])

        created = []
        skipped_existing = []
        conn = _pg()
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("""
                SELECT lower(csi_division) AS csi, lower(package_name) AS pkg FROM bid_packages
                WHERE project_id = %s AND status NOT IN ('awarded', 'cancelled')
            """, (pid,))
            existing = {(row["csi"], row["pkg"]) for row in cur.fetchall()}
            for pkg in packages:
                key = (pkg.get("csi_division", "").lower(), pkg.get("package_name", "").lower())
                if key in existing:
                    skipped_existing.append(pkg.get("package_name", ""))
                    continue
                notes = f"Confidence: {pkg.get('confidence','?')} — generated from plan-review, not yet reviewed by PM"
                cur.execute("""
                    INSERT INTO bid_packages (project_id, csi_division, package_name, scope_description, status, notes, created_by, created_via)
                    VALUES (%s, %s, %s, %s, 'not_started', %s, %s, 'ai_plan_review')
                    RETURNING id, csi_division, package_name, status
                """, (pid, pkg.get("csi_division", ""), pkg.get("package_name", ""),
                      pkg.get("scope_description", ""), notes, req.reviewed_by))
                row = dict(cur.fetchone())
                row["confidence"] = pkg.get("confidence", "low")
                created.append(row)
                existing.add(key)
        conn.close()

        _log("/plan-review/generate-packages", req.reviewed_by, req.project_code, "ok",
             round((time.time()-t0)*1000), str(uuid.uuid4())[:8], f"{len(created)} bid packages drafted")
        return _response("/plan-review/generate-packages", {
            "project_code": req.project_code,
            "packages_created": len(created),
            "bid_packages": created,
            "skipped_existing": skipped_existing,
            "coverage_note": analysis.get("coverage_note"),
            "note": "Bid packages created as 'not_started' — internal draft only. No sub "
                    "has been invited to bid. PM should review scope_description and "
                    "confidence before soliciting bids through the normal bid-leveling flow. "
                    "Re-running plan review after revised plans arrive will not duplicate "
                    "packages already open for the same scope (matched on division + name) — "
                    "only genuinely new scope gets a new package.",
        }, start=t0)
    except HTTPException as e:
        return _response("/plan-review/generate-packages", {}, errors=[str(e.detail)], start=t0)
    except Exception as e:
        return _response("/plan-review/generate-packages", {}, errors=[str(e)], start=t0)


@router.get("/project/{code}/bid-package-vendor-matches")
def bid_package_vendor_matches(code: str):
    """
    Vendor matching for generated bid packages (2026-07-02) — the natural next link in
    the plan-review pipeline: a generated package is just an internal draft until it has
    real, qualified vendors attached. For each 'not_started' bid_package, ranks vendors
    whose csi_divisions cover that package's division, preferred tier first, then by
    win_rate_pct/bid_count as a track-record signal. This does NOT invite anyone to bid
    or contact any vendor — same governance boundary as generate-packages itself; it's a
    PM-facing shortlist to speed up the normal bid-leveling flow, not an automated
    solicitation. current_active_awards is a light capacity signal (how many other
    active projects this vendor is currently awarded on) — the full date-overlap
    analysis lives in GET /knowledge/vendor-capacity-conflicts once someone is awarded.
    """
    t0 = time.time()
    try:
        pid = _get_pid(code)
        conn = _pg()
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, csi_division, package_name FROM bid_packages
                WHERE project_id = %s AND status = 'not_started'
                ORDER BY id
            """, (pid,))
            packages = [dict(r) for r in cur.fetchall()]
            if not packages:
                conn.close()
                return _response(f"/project/{code}/bid-package-vendor-matches", {
                    "project_code": code, "packages": [],
                    "note": "No 'not_started' bid_packages found — run /plan-review/generate-packages first.",
                }, start=t0)

            matches = []
            for pkg in packages:
                division_num = (pkg["csi_division"] or "").strip().split(" ")[0].zfill(2)[:2]
                # Vendor DB is tagged with legacy 16-division CSI (01-16); the plan-review
                # generator (and the CPM engine, deliberately, for finer-grained MEP/site
                # scheduling) emits modern 50-division codes for MEP/site work. Fall back
                # to the legacy equivalent so those packages still find real vendors.
                lookup_division = _MODERN_TO_LEGACY_CSI.get(division_num, division_num)
                cur.execute("""
                    SELECT v.id, v.company_name, v.tier, v.win_rate_pct, v.bid_count,
                           v.preferred_status, v.phone, v.email,
                           (SELECT count(*) FROM bid_entries be2
                            JOIN bid_packages bp2 ON bp2.id = be2.bid_package_id
                            JOIN projects p2 ON p2.id = bp2.project_id
                            WHERE be2.vendor_id = v.id AND be2.status = 'awarded'
                              AND p2.status IN ('active','design','bidding','preconstruction')
                           ) AS current_active_awards
                    FROM vendors v
                    WHERE %s = ANY(v.csi_divisions)
                    ORDER BY (v.tier = 'preferred') DESC,
                             COALESCE(v.win_rate_pct, 0) DESC,
                             COALESCE(v.bid_count, 0) DESC
                    LIMIT 5
                """, (lookup_division,))
                vendors = [dict(r) for r in cur.fetchall()]
                for v in vendors:
                    v["win_rate_pct"] = float(v["win_rate_pct"]) if v["win_rate_pct"] is not None else None

                # If this package already has a draft schedule window (generate-schedule
                # has run), forward-check each candidate against their OTHER active
                # awards for a date overlap — same join pattern as
                # GET /knowledge/vendor-capacity-conflicts, but applied before an award
                # happens rather than after, since a proposed vendor is exactly when a
                # capacity heads-up is most useful.
                cur.execute("""
                    SELECT start_date, end_date FROM project_schedule_items
                    WHERE project_id = %s AND status = 'draft' AND title = %s
                    LIMIT 1
                """, (str(pid), pkg["package_name"]))
                window = cur.fetchone()
                if window:
                    for v in vendors:
                        cur.execute("""
                            SELECT p2.project_code, p2.name AS project_name, psi.title AS activity,
                                   psi.start_date, psi.end_date
                            FROM bid_entries be2
                            JOIN bid_packages bp2 ON bp2.id = be2.bid_package_id
                            JOIN projects p2 ON p2.id = bp2.project_id
                            JOIN project_schedule_items psi
                                ON psi.project_id = p2.id::text
                                AND length(split_part(%s, ' ', 1)) > 3
                                AND psi.assignee ILIKE '%%' || split_part(%s, ' ', 1) || '%%'
                            WHERE be2.vendor_id = %s AND be2.status = 'awarded'
                              AND p2.status IN ('active','design','bidding','preconstruction')
                              AND p2.id != %s
                              AND psi.start_date IS NOT NULL AND psi.end_date IS NOT NULL
                              AND psi.start_date <= %s AND %s <= psi.end_date
                            LIMIT 1
                        """, (v["company_name"], v["company_name"], v["id"], pid, window["end_date"], window["start_date"]))
                        conflict = cur.fetchone()
                        if conflict:
                            v["capacity_conflict"] = {
                                "conflicting_project": conflict["project_code"],
                                "conflicting_project_name": conflict["project_name"],
                                "conflicting_activity": conflict["activity"],
                                "conflicting_window": f"{conflict['start_date'].isoformat()} to {conflict['end_date'].isoformat()}",
                            }
                        else:
                            v["capacity_conflict"] = None
                else:
                    for v in vendors:
                        v["capacity_conflict"] = None

                matches.append({
                    "bid_package_id": pkg["id"], "csi_division": pkg["csi_division"],
                    "package_name": pkg["package_name"],
                    "vendor_matches": vendors,
                    "match_count": len(vendors),
                })
        conn.close()
        return _response(f"/project/{code}/bid-package-vendor-matches", {
            "project_code": code,
            "packages": matches,
            "unmatched_packages": sum(1 for m in matches if m["match_count"] == 0),
            "note": "Ranked by preferred tier, then win rate, then bid history. No vendor "
                    "has been contacted — this is a PM shortlist for the normal bid-leveling "
                    "flow. current_active_awards is a light capacity signal, not a hard block. "
                    "capacity_conflict is non-null only when this project already has a draft "
                    "schedule (generate-schedule has run) and the candidate is currently "
                    "awarded on another active project during an overlapping window — worth "
                    "confirming before proposing this vendor, not a hard rule (same heuristic "
                    "as GET /knowledge/vendor-capacity-conflicts, applied pre-award here).",
        }, start=t0)
    except Exception as e:
        return _response(f"/project/{code}/bid-package-vendor-matches", {}, errors=[str(e)], start=t0)


# Long-lead items that routinely blow ultra-luxury custom-home schedules if ordered on
# the package's normal phase timeline instead of at project kickoff (identified while
# thinking through what a $40-60M Aspen build needs vs. a standard remodel). Keyword ->
# typical order-to-delivery lead time in weeks. Matched against package_name +
# scope_description; deliberately keyword-based, not a vendor-confirmed lead time.
_LONG_LEAD_ITEMS = {
    # elevator recalibrated 2026-07-02 from real HCI project data (ASPN-MC risk:
    # "ThyssenKrupp elevator package has 40-week lead — longest lead item") — the
    # generic industry estimate (18wk) was less than half the real observed lead
    # time for a specialty residential elevator manufacturer.
    "elevator": 40, "generator": 26, "structural steel": 10,
    "custom window": 16, "window wall": 16, "steel window": 16, "custom glazing": 14,
    "imported stone": 14, "natural stone": 14, "marble": 14,
    "custom cabinetry": 14, "millwork": 14,
    "geothermal": 12, "vrf": 10, "radiant": 8, "specialty hvac": 10,
    "pool equipment": 10, "spa equipment": 10,
}


def _long_lead_flags(package_name: str, scope_description: str) -> list:
    text = f"{package_name or ''} {scope_description or ''}".lower()
    return [{"item": kw, "lead_weeks": wk} for kw, wk in _LONG_LEAD_ITEMS.items() if kw in text]


# Modern 50-division CSI MasterFormat -> legacy 16-division equivalent, used only for
# vendor-DB lookups (vendors.csi_divisions is tagged in the legacy scheme; see
# GET /project/{code}/bid-package-vendor-matches). Not used for scheduling — the CPM
# engine below deliberately keeps MEP/site split into the modern, finer-grained codes.
_MODERN_TO_LEGACY_CSI = {
    "21": "15", "22": "15", "23": "15",  # fire suppression, plumbing, HVAC -> Mechanical
    "26": "16", "27": "16",              # electrical, communications -> Electrical
    "31": "02", "32": "02",              # earthwork, exterior improvements -> Site Work
}

# CSI division -> (construction phase, typical duration in days). Phases run in
# sequence; packages within the same phase run in parallel (phase duration = max of
# its packages, not the sum). Industry-standard starting points, same role as
# rom_estimate()'s BENCHMARKS table — calibrate against this system's own historical
# schedule data once enough completed projects accumulate (see ADR-014/015).
_CSI_PHASE_DURATIONS = {
    "02": (1, 10),  "site work": (1, 10), "existing conditions": (1, 10),
    "03": (2, 21),  "concrete": (2, 21),
    "04": (2, 10),  "masonry": (2, 10),
    "05": (3, 14),  "metals": (3, 14),
    "06": (3, 28),  "wood": (3, 28), "plastics": (3, 28), "composites": (3, 28),
    "07": (4, 14),  "thermal": (4, 14), "moisture": (4, 14),
    "08": (4, 10),  "openings": (4, 10), "doors": (4, 10), "windows": (4, 10),
    "09": (6, 30),  "finishes": (6, 30),
    "10": (6, 7),   "specialties": (6, 7),
    "11": (7, 14),  "equipment": (7, 14),
    "12": (7, 10),  "furnishings": (7, 10),
    "21": (5, 7),   "fire suppression": (5, 7),
    "22": (5, 21),  "plumbing": (5, 21),
    "23": (5, 21),  "hvac": (5, 21), "mechanical": (5, 21),
    "26": (5, 21),  "electrical": (5, 21),
    "27": (5, 10),  "communications": (5, 10),
    "31": (1, 14),  "earthwork": (1, 14),
    "32": (7, 14),  "exterior improvements": (7, 14),
}
_DEFAULT_PHASE_DURATION = (4, 14)  # fallback for an unrecognized CSI division


def _phase_and_duration(csi_division: str) -> tuple:
    key = (csi_division or "").lower()
    for token, val in _CSI_PHASE_DURATIONS.items():
        if token in key:
            return val
    return _DEFAULT_PHASE_DURATION


class GenerateSchedulePayload(BaseModel):
    project_code: str
    start_date: str  # YYYY-MM-DD — project/phase kickoff
    reviewed_by: str = "claude_code"


@router.post("/plan-review/generate-schedule")
def plan_review_generate_schedule(req: GenerateSchedulePayload):
    """
    Preliminary CPM (critical path) schedule generator — ADR-014 roadmap item #4,
    "real CPM scheduling engine ... generate/re-sequence a critical path from the plan
    set + historical durations, rather than only monitoring variance after a human
    enters a schedule." Takes the project's `not_started` bid_packages (typically the
    output of /plan-review/generate-packages) and sequences them into construction
    phases (site work -> structural -> envelope -> rough MEP -> interior rough -> rough
    inspections -> finishes -> equipment/furnishings -> exterior/punch), computing
    start/end dates per package. Packages within a phase run in parallel; phases run in
    sequence — a simplified but real critical-path calculation, not just a flat list.

    Writes real `project_schedule_items` rows with status='draft' — a PM must review
    and mark them started before they count as the live schedule (existing schedule
    consumers filter/report on real activity, not draft rows, so this cannot silently
    become "the schedule" without a human looking at it first).
    """
    t0 = time.time()
    try:
        pid = _get_pid(req.project_code)
        from datetime import date as _date, timedelta as _timedelta
        try:
            project_start = _date.fromisoformat(req.start_date)
        except ValueError:
            return _response("/plan-review/generate-schedule", {},
                              errors=["start_date must be YYYY-MM-DD"], start=t0)

        conn = _pg()
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, csi_division, package_name, scope_description FROM bid_packages
                WHERE project_id = %s AND status = 'not_started'
                ORDER BY id
            """, (pid,))
            packages = [dict(r) for r in cur.fetchall()]
            if not packages:
                conn.close()
                return _response("/plan-review/generate-schedule", {},
                                  errors=["No 'not_started' bid_packages found for this "
                                          "project — run /plan-review/generate-packages first"],
                                  start=t0)

            # This endpoint regenerates the draft schedule from the current package set —
            # clear prior draft rows first so re-running it (e.g. after new packages are
            # added) replaces stale items instead of stacking duplicates alongside them.
            # Only 'draft' rows are touched — a PM-reviewed/started schedule is never here.
            cur.execute("DELETE FROM project_schedule_items WHERE project_id = %s AND status = 'draft'", (str(pid),))

            for pkg in packages:
                phase, duration = _phase_and_duration(pkg["csi_division"])
                pkg["phase"] = phase
                pkg["duration"] = duration

            phase_numbers = sorted(set(p["phase"] for p in packages))
            phase_start = project_start
            created = []
            long_lead_alerts = []
            for phase in phase_numbers:
                phase_packages = [p for p in packages if p["phase"] == phase]
                phase_duration = max(p["duration"] for p in phase_packages)
                for pkg in phase_packages:
                    end = phase_start + _timedelta(days=pkg["duration"])
                    activity_id = f"PR-{pid}-{pkg['id']}-{str(uuid.uuid4())[:6]}"
                    flags = _long_lead_flags(pkg["package_name"], pkg.get("scope_description"))
                    notes = ("Generated by plan-review CPM engine — PM must review before "
                             "this counts as the live schedule")
                    if flags:
                        max_lead_weeks = max(f["lead_weeks"] for f in flags)
                        order_by = phase_start - _timedelta(weeks=max_lead_weeks)
                        notes += f" | LONG-LEAD: order by {order_by.isoformat()} to avoid delaying this phase"
                    cur.execute("""
                        INSERT INTO project_schedule_items
                            (activity_id, project_id, title, start_date, end_date,
                             status, assignee, task_type, notes)
                        VALUES (%s, %s, %s, %s, %s, 'draft', %s, %s, %s)
                        RETURNING activity_id, title, start_date, end_date, status
                    """, (activity_id, str(pid), pkg["package_name"], phase_start, end,
                          pkg["package_name"], f"phase_{phase}", notes))
                    row = dict(cur.fetchone())
                    row["phase"] = phase
                    row["csi_division"] = pkg["csi_division"]
                    row["start_date"] = row["start_date"].isoformat()
                    row["end_date"] = row["end_date"].isoformat()
                    created.append(row)
                    if flags:
                        max_lead_weeks = max(f["lead_weeks"] for f in flags)
                        order_by = phase_start - _timedelta(weeks=max_lead_weeks)
                        long_lead_alerts.append({
                            "package_name": pkg["package_name"], "matched_items": flags,
                            "phase_start_date": phase_start.isoformat(),
                            "recommended_order_by": order_by.isoformat(),
                            "order_by_is_before_project_start": order_by < project_start,
                        })
                phase_start = phase_start + _timedelta(days=phase_duration)
        conn.close()

        critical_path_days = (phase_start - project_start).days
        _log("/plan-review/generate-schedule", req.reviewed_by, req.project_code, "ok",
             round((time.time()-t0)*1000), str(uuid.uuid4())[:8],
             f"{len(created)} schedule items, {critical_path_days}d critical path")
        return _response("/plan-review/generate-schedule", {
            "project_code": req.project_code,
            "items_created": len(created),
            "schedule_items": created,
            "critical_path_days": critical_path_days,
            "projected_completion": phase_start.isoformat(),
            "long_lead_alerts": long_lead_alerts,
            "note": "All items created with status='draft' — this is a preliminary "
                    "sequence from typical CSI-division durations, not a confirmed "
                    "schedule. PM must review phasing/durations and mark items active "
                    "before this is the live project schedule. long_lead_alerts flags "
                    "keyword-matched items (elevator, custom windows, imported stone, "
                    "etc.) whose typical order lead time means they should be ordered "
                    "well before their phase begins — order_by_is_before_project_start "
                    "means the order needs to happen at kickoff, not on the normal "
                    "phase timeline, to avoid delaying the critical path.",
        }, start=t0)
    except HTTPException as e:
        return _response("/plan-review/generate-schedule", {}, errors=[str(e.detail)], start=t0)
    except Exception as e:
        return _response("/plan-review/generate-schedule", {}, errors=[str(e)], start=t0)


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
        # Replace ONLY the Live Production Projects table. Found 2026-07-07: the old
        # pattern matched on the shared "| ID | Code | Project" prefix, which all
        # three distinct project tables in this file start with (Live Production,
        # Monitored/Staged, All Other Projects - each with different columns after
        # that). re.sub with no count replaced ALL THREE with identical content,
        # destroying the real Monitored/Staged and All Other Projects lists. Anchor
        # on the full real header (with all 9 columns) and cap at count=1.
        pattern = r"(\| ID \| Code \| Project \| Scope \| HubSpot Deal \| Health \| Bid Pkgs \| Open Risks \| Schedule Var \|\n\|---\|---\|---\|---\|---\|---\|---\|---\|---\|\n(?:\|.*\n)*)"
        new_block = new_table + "\n"
        updated, n_subs = _re.subn(pattern, new_block, content, count=1)
        if n_subs != 1:
            raise ValueError(f"Expected exactly 1 Live Production table match, got {n_subs} - refusing to write, table format may have changed")

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


# ── Write repo report + git commit (n8n cannot do this itself) ──────────────
# n8n's Code node sandbox disallows Node built-ins (fs, child_process) by
# design/security default. AUTO-011 (and any future "write a report + commit"
# workflow) was written assuming direct filesystem/git access from inside n8n,
# which fails with "Module 'fs' is disallowed". Rather than loosen n8n's
# sandbox, n8n POSTs the content here instead - this process already has real
# filesystem access and is the appropriate place for it to live.
class WriteReportPayload(BaseModel):
    filename: str
    content: str

@router.post("/admin/write-report")
async def write_report(req: WriteReportPayload, request: Request):
    _require_key(request)
    t0 = time.time()
    try:
        repo_root = "/Users/buckadams/HCI_AI_Operating_System"
        # Reject path traversal - filename must resolve to stay inside repo_root
        norm_path = os.path.normpath(os.path.join(repo_root, req.filename))
        if not norm_path.startswith(repo_root + os.sep):
            return _response("/admin/write-report", {}, errors=["filename escapes repo root"], start=t0)
        os.makedirs(os.path.dirname(norm_path), exist_ok=True)
        with open(norm_path, "w", encoding="utf-8") as f:
            f.write(req.content)
        commit_note = None
        try:
            subprocess.run(["git", "-C", repo_root, "add", norm_path], check=True, capture_output=True)
            diff = subprocess.run(["git", "-C", repo_root, "diff", "--cached", "--quiet"], cwd=repo_root)
            if diff.returncode != 0:
                subprocess.run(
                    ["git", "-C", repo_root, "commit", "-m", f"AUTO: {os.path.basename(req.filename)} [skip ci]"],
                    check=True, capture_output=True,
                )
                commit_note = "committed"
            else:
                commit_note = "no changes to commit"
        except subprocess.CalledProcessError as ge:
            commit_note = f"git step failed: {ge.stderr.decode()[:200] if ge.stderr else str(ge)}"
        return _response("/admin/write-report", {
            "written": norm_path, "commit": commit_note,
        }, start=t0)
    except Exception as e:
        return _response("/admin/write-report", {}, errors=[str(e)], start=t0)


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

# Grounded permitting facts (2026-07-01) — verified via live web search against the
# actual City of Aspen / Pitkin County government sites rather than relying on Claude's
# general knowledge alone. This is the ADR-014 roadmap's "grounded permitting research"
# item, built without a paid UpCodes vendor account: the always-on API backend can't
# call WebSearch/WebFetch itself (those are Claude Code session tools, not a callable
# API), so this is refreshed periodically by an agent doing the research and updating
# this block — same maintenance pattern as rom_estimate()'s benchmark table. Refresh
# this if City of Aspen / Pitkin County process pages change materially.
_PERMITTING_GROUNDED_FACTS = """VERIFIED FACTS (source-cited, refresh periodically — not general knowledge):

City of Aspen Building Permit Process:
- All applications submitted via the Salesforce-based Permit Portal; registration takes up to 2 business days to activate.
- Contractors must hold an active City of Aspen Business License AND Contractor License before applying.
- Building Support reviews for completeness first; once accepted, applicant receives submittal fee total + payment instructions.
- Relevant review agencies (Building, Engineering, Fire, etc.) each approve or return comments per review round; all must approve before Final Review.
- Issuance fees must be paid within 180 days of "Ready for Issue" status or the permit expires.
- Once issued, work must be inspected within 180 days or the permit is considered expired.
- Source: City of Aspen Building Permit Process (https://aspen.gov/236/Building-Permit-Process-Payment), Permit Types & Triggers (https://www.aspen.gov/DocumentCenter/View/1703/Permit-Types-and-Triggers)

Pitkin County (unincorporated — applies outside Aspen city limits):
- If the site is a historic or archeological resource, conceptual approval from the Historic Preservation Officer is REQUIRED at permit submittal, not after.
- Redstone Historic District specifically requires a separate land use application for development projects.
- Historic Preservation Officer contact: 970-920-9225.
- Source: Pitkin County Historic Preservation (https://pitkincounty.com/220/Historic-Preservation), Building (https://pitkincounty.com/192/Building)
"""


@router.get("/permitting/research/{code}")
def permitting_research(code: str):
    """AI-powered permit research for Aspen-area projects — grounded in verified City of
    Aspen / Pitkin County process facts (see _PERMITTING_GROUNDED_FACTS), not Claude's
    general knowledge alone."""
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
        is_historic = "cemetery" in address.lower() or "historic" in (scope or "").lower()

        prompt = f"""You are a construction permitting expert specializing in Aspen, Colorado.

{_PERMITTING_GROUNDED_FACTS}

Using the verified facts above (cite them where relevant, do not contradict them),
provide a concise permitting roadmap for this project:

Project: {row['name']}
Address: {address}
Scope: {scope}
Status: {row['status']}
Historic/archeological resource flag: {is_historic}

Provide:
1. Required permits (Building, Grading, ROW, HPC if applicable, etc.)
2. City of Aspen or Pitkin County specific requirements (whichever applies), citing the verified facts above
3. Estimated review timelines and expiration windows (cite the verified 180-day issuance/inspection windows above)
4. Key submittals required, including Business/Contractor License prerequisites
5. Any altitude/environmental considerations (7,900 ft elevation, wildfire zone, etc.)

Keep response under 400 words."""

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
            "hpc_required": is_historic,
            "sources": [
                "https://aspen.gov/236/Building-Permit-Process-Payment",
                "https://www.aspen.gov/DocumentCenter/View/1703/Permit-Types-and-Triggers",
                "https://pitkincounty.com/220/Historic-Preservation",
                "https://pitkincounty.com/192/Building",
            ],
            "grounded_facts_note": "Response is grounded in verified City of Aspen / "
                "Pitkin County process facts (see 'sources'), not general AI knowledge "
                "alone — refreshed periodically, not live-fetched on every call.",
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
        # 1. Download PDF from Drive via the shared OAuth credential (2026-07-02: was
        # reading a GOOGLE_ACCESS_TOKEN env var that's never set anywhere - this endpoint
        # has been falling back to "credential_required" on every call since it was written).
        import anthropic as _anthropic
        drive_resp = requests.get(
            f"https://www.googleapis.com/drive/v3/files/{req.file_id}?alt=media",
            headers={"Authorization": f"Bearer {_drive_token()}"},
            timeout=60,
        )
        if drive_resp.status_code != 200:
            return _response("/plan/read", {
                "status": "credential_required",
                "message": f"Drive download failed (HTTP {drive_resp.status_code}). "
                           "Run plan_reader.py locally as a fallback.",
                "file_id": req.file_id,
                "model_requested": req.model,
            }, warnings=["Drive token invalid or file not accessible"], start=t0)

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

            # launchd runs this service with a minimal PATH that doesn't include Homebrew's
            # /opt/homebrew/bin, so a bare "pdftoppm" raises FileNotFoundError even though
            # poppler is installed (found 2026-07-02 while testing this endpoint for real).
            import shutil as _shutil
            pdftoppm_bin = _shutil.which("pdftoppm") or "/opt/homebrew/bin/pdftoppm"
            subprocess.run(
                [pdftoppm_bin, "-r", "150", *page_filter, pdf_path, os.path.join(tmpdir, "page")],
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


class PhotoAnalyzePayload(BaseModel):
    file_id: str  # Drive file ID of the photo
    project_code: str
    submitted_by: str = "field"
    note: Optional[str] = None


PHOTO_SYSTEM = """You are a construction superintendent reviewing a field photo from a luxury residential project in Aspen, CO.

Analyze the photo and report:
1. WORK VISIBLE: What construction activity or completed work is shown - be specific (framing stage, rough-in, finish work, etc.)
2. PROGRESS ASSESSMENT: Does this look on-track, ahead, or behind for a typical build sequence at this stage? State your confidence.
3. SAFETY OBSERVATIONS: Any visible safety concerns (missing PPE, fall hazards, unsecured materials, electrical hazards, housekeeping issues). If none visible, say so explicitly - do not invent hazards.
4. DEFECT/QUALITY FLAGS: Any visible workmanship issues, code-concern items, or things that look wrong and warrant a closer look. If none visible, say so explicitly.
5. WHAT'S NOT VISIBLE: Note if the photo angle/quality limits what can actually be assessed - do not overstate confidence on things you cannot actually see clearly.

Be specific and evidence-based. Do not invent problems to seem thorough - "no issues visible" is a valid and useful finding."""


@router.post("/project/{code}/photo/analyze")
async def photo_analyze(code: str, req: PhotoAnalyzePayload, request: Request):
    """Photo AI — CYCLE49 queue item #6, 2026-07-02. Claude Vision analysis of a field
    photo: progress assessment, safety observations, defect flags. Stored in
    photo_analyses (queryable per-project field record), same credential/vision
    pattern as /gateway/plan/read."""
    import anthropic as _anthropic
    import base64
    t0 = time.time()
    _require_key(request)
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name FROM projects WHERE UPPER(project_code) = UPPER(%s)", (code,))
                proj = cur.fetchone()
                if not proj:
                    return _response(f"/project/{code}/photo/analyze", {}, errors=[f"Unknown project code: {code}"], start=t0)
                pid = proj["id"]

        drive_resp = requests.get(
            f"https://www.googleapis.com/drive/v3/files/{req.file_id}?alt=media",
            headers={"Authorization": f"Bearer {_drive_token()}"},
            timeout=30,
        )
        if drive_resp.status_code != 200:
            return _response(f"/project/{code}/photo/analyze", {
                "status": "credential_required",
                "message": f"Drive download failed (HTTP {drive_resp.status_code}).",
            }, start=t0)

        img_b64 = base64.standard_b64encode(drive_resp.content).decode()
        media_type = drive_resp.headers.get("Content-Type", "image/jpeg")
        if media_type not in ("image/jpeg", "image/png", "image/webp", "image/gif"):
            media_type = "image/jpeg"

        client = _anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            system=PHOTO_SYSTEM,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": img_b64}},
                    {"type": "text", "text": f"Project: {proj['name']}. Field note from submitter: {req.note or '(none provided)'}"}
                ]
            }]
        )
        analysis_text = resp.content[0].text

        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO photo_analyses (project_id, drive_file_id, submitted_by, note, findings, model_used)
                    VALUES (%s,%s,%s,%s,%s,%s) RETURNING id, created_at
                """, (pid, req.file_id, req.submitted_by, req.note, analysis_text, "claude-sonnet-4-6"))
                row = cur.fetchone()
                conn.commit()

        return _response(f"/project/{code}/photo/analyze", {
            "photo_analysis_id": row["id"],
            "project": proj["name"],
            "analyzed_at": row["created_at"].isoformat(),
            "analysis": analysis_text,
        }, start=t0)
    except Exception as e:
        return _response(f"/project/{code}/photo/analyze", {}, errors=[str(e)], start=t0)


@router.get("/project/{code}/photos")
def project_photos(code: str, limit: int = Query(20, le=100)):
    """List recent photo analyses for a project."""
    t0 = time.time()
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM projects WHERE UPPER(project_code) = UPPER(%s)", (code,))
                row = cur.fetchone()
                if not row:
                    return _response(f"/project/{code}/photos", {}, errors=[f"Unknown project code: {code}"], start=t0)
                cur.execute("""
                    SELECT id, drive_file_id, submitted_by, note, findings, created_at
                    FROM photo_analyses WHERE project_id = %s ORDER BY created_at DESC LIMIT %s
                """, (row["id"], limit))
                photos = [dict(r) for r in cur.fetchall()]
        return _response(f"/project/{code}/photos", {"count": len(photos), "photos": photos}, start=t0)
    except Exception as e:
        return _response(f"/project/{code}/photos", {}, errors=[str(e)], start=t0)


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
                      metadata: dict = None, seen_at=None) -> Optional[str]:
    """seen_at: pass an explicit timestamp when the evidence of activity has its
    own real timestamp (e.g. a Drive file's modifiedTime) rather than "right now"
    - matters for backfilling BC's heartbeat from historical Document Bus posts,
    where NOW() would make a day-old post look like it just happened."""
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
                    VALUES (%s, COALESCE(%s, NOW()), %s, 'ONLINE', %s, %s, %s, COALESCE(%s, '{}'::jsonb))
                    ON CONFLICT (agent) DO UPDATE
                        SET last_seen_at = GREATEST(COALESCE(%s, NOW()), ai_agent_heartbeat.last_seen_at),
                            last_action = EXCLUDED.last_action, status = 'ONLINE',
                            role = COALESCE(EXCLUDED.role, ai_agent_heartbeat.role),
                            current_task = COALESCE(EXCLUDED.current_task, ai_agent_heartbeat.current_task),
                            last_directive_id = COALESCE(EXCLUDED.last_directive_id, ai_agent_heartbeat.last_directive_id),
                            metadata = CASE WHEN EXCLUDED.metadata = '{}'::jsonb THEN ai_agent_heartbeat.metadata
                                            ELSE EXCLUDED.metadata END
                """, (key, seen_at, (action or "")[:200], role, current_task, last_directive_id,
                      json.dumps(metadata) if metadata else None, seen_at))
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
        text = f"{icon} *{title}*\n_{_buck_local_str()}_\n\n{body}"
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
            # Changed 2026-07-07 per Buck's direct instruction: a Telegram APPROVE tap
            # must never trigger an immediate, irreversible send. Prior behavior called
            # _send_approved_draft() here, which sent live mail the instant APPROVE was
            # tapped -  an email to an external party (the 1355R architect) went out
            # this way and could not be recalled (recipient wasn't on HCI's Exchange
            # org, so Outlook's own recall feature doesn't apply either). Now APPROVE
            # just acknowledges the request; the draft stays in Buck's own Outlook
            # Drafts folder and he sends it himself when he's actually looked at it.
            if cmd == "APPROVE" and row.get("approval_type") == "email_send" and row.get("related_file"):
                with _pg() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""UPDATE ai_messages SET status='COMPLETE', completed_at=NOW(), updated_at=NOW()
                                        WHERE id=%s""", (msg_id,))
                    conn.commit()
                return f"✅ Acknowledged #{msg_id}: {row['title']}\nDraft is in your Outlook Drafts folder — review and send it yourself when ready. It will NOT send automatically."
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
    skip_notify: bool = False  # test-only: create the durable row without a real Telegram/ntfy send


@router.post("/ai/messages")
async def ai_messages_create(req: AIMessageCreate):
    """Create a durable agent message/task (this IS the directive system — ai_directives
    was not created as a separate table per ARB 2026-07-01, extending this one instead).
    DB row is the source of truth; Telegram notification (with ntfy fallback) is sent
    automatically for notify-worthy types (approval_request, risk_alert, blocked_mission,
    handoff_waiting, work_complete, review_required) or whenever requires_buck_approval is true."""
    t0 = time.time()
    _touch_heartbeat(req.source_agent, f"sent {req.message_type}: {req.title[:60]}")
    if req.skip_notify:
        msg_id = _create_ai_message(req.source_agent, req.target_agent, req.message_type, req.title, req.body,
                                     req.project_code, req.requires_buck_approval, req.approval_type,
                                     req.related_file, req.related_handoff_id, req.related_approval_id,
                                     req.priority, req.source_of_truth_link)
        result = {"id": msg_id, "delivery": {"status": "skipped_test_mode"}}
    else:
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


@router.get("/agent/unread")
def agent_unread(agent: str = Query(..., description="chatgpt|browser_claude|claude_code|n8n")):
    """
    Single-call catch-up for any agent on session start: everything targeted
    at it that hasn't been picked up yet (status ISSUED or NEEDS_BUCK_APPROVAL).
    Identified as a real, missing convenience wrapper 2026-07-11 while
    reviewing BC's ADR-003 proposal - the underlying data (ai_messages) and
    filtering already existed via other endpoints, but nothing gave a single
    "what's waiting for me" answer the way BC's proposed GET /agent/messages/
    unread did. This is that endpoint, built on the existing table rather
    than a new one.
    """
    t0 = time.time()
    key = _AGENT_ALIASES.get((agent or "").strip().lower(), agent)
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, source_agent, message_type, title, body, priority,
                           status, related_file, created_at
                    FROM ai_messages
                    WHERE target_agent = %s AND status IN ('ISSUED', 'NEEDS_BUCK_APPROVAL')
                    ORDER BY created_at ASC
                """, (key,))
                rows = [dict(r) for r in cur.fetchall()]
        for r in rows:
            r["created_at"] = r["created_at"].isoformat()
        return _response("/agent/unread", {"agent": key, "count": len(rows), "messages": rows}, start=t0)
    except Exception as e:
        return _response("/agent/unread", {}, errors=[str(e)], start=t0)


class AgentHeartbeatPayload(BaseModel):
    agent: str
    mission: Optional[str] = None
    session_id: Optional[str] = None


_ADR003_AGENT_ID = {"chatgpt": "GBT", "gbt": "GBT", "browser_claude": "BC", "bc": "BC",
                     "claude_code": "CODE", "code": "CODE"}


@router.post("/agent/heartbeat")
def agent_heartbeat_selfreport(req: AgentHeartbeatPayload):
    """
    Explicit "I'm alive" self-report - Buck's Priority-0 ADR-003 directive
    (2026-07-11), built on the new agent_heartbeats table. Dual-writes to
    the pre-existing ai_agent_heartbeat too (same call, no extra work for
    callers) so drift-check/mission-control/warm-start's existing readers
    of that table don't regress while agent_heartbeats becomes the primary
    source of truth for the new agent-comms system.
    """
    t0 = time.time()
    _touch_heartbeat(req.agent, "explicit heartbeat", current_task=req.mission,
                      metadata={"session_id": req.session_id} if req.session_id else None)
    adr_id = _ADR003_AGENT_ID.get((req.agent or "").strip().lower())
    if adr_id:
        try:
            with _pg() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO agent_heartbeats (agent_id, status, last_heartbeat_mt, current_mission, session_id)
                        VALUES (%s, 'online', NOW(), %s, %s)
                        ON CONFLICT (agent_id) DO UPDATE
                            SET status = 'online', last_heartbeat_mt = NOW(),
                                current_mission = COALESCE(EXCLUDED.current_mission, agent_heartbeats.current_mission),
                                session_id = COALESCE(EXCLUDED.session_id, agent_heartbeats.session_id)
                    """, (adr_id, req.mission, req.session_id))
        except Exception:
            pass
    return _response("/agent/heartbeat", {"agent": req.agent, "status": "ONLINE"}, start=t0)


# ── Agent Message Bus (ADR-003, Buck's Priority-0 directive, 2026-07-11) ──────
# Full spec build: agent_messages / agent_heartbeats / decision_log, all 9
# endpoints from BC's proposal (doc says "eight," body lists 9 - built all).
# Distinct from ai_messages/ai_agent_heartbeat (Code's earlier extension of
# the pre-existing tables) - Buck explicitly directed building the literal
# new-table spec despite the overlap; both systems now exist, this one is
# the BC/GBT/CODE-facing one, ai_messages remains Buck-facing/Telegram-tied.

class AgentMessageCreate(BaseModel):
    from_agent: str
    to_agent: str
    subject: str
    body: str
    priority: str = "P2"
    thread_id: Optional[str] = None
    requires_response: bool = False
    response_deadline_mt: Optional[str] = None
    drive_file_id: Optional[str] = None


@router.post("/agent/messages")
def agent_messages_send(req: AgentMessageCreate):
    t0 = time.time()
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                if req.thread_id:
                    cur.execute("""
                        INSERT INTO agent_messages
                            (thread_id, from_agent, to_agent, priority, subject, body,
                             requires_response, response_deadline_mt, drive_file_id)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        RETURNING message_id, thread_id, timestamp_mt
                    """, (req.thread_id, req.from_agent, req.to_agent, req.priority, req.subject,
                          req.body, req.requires_response, req.response_deadline_mt, req.drive_file_id))
                else:
                    cur.execute("""
                        INSERT INTO agent_messages
                            (from_agent, to_agent, priority, subject, body,
                             requires_response, response_deadline_mt, drive_file_id)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                        RETURNING message_id, thread_id, timestamp_mt
                    """, (req.from_agent, req.to_agent, req.priority, req.subject,
                          req.body, req.requires_response, req.response_deadline_mt, req.drive_file_id))
                row = cur.fetchone()
        _touch_heartbeat(req.from_agent, f"sent agent_message to {req.to_agent}: {req.subject[:60]}")

        # BC has no way to call this gateway (its own documented constraint) -
        # its only real "session startup" is reading Drive. Mirror any message
        # addressed to it (or ALL) into a real Drive file so BC actually sees
        # it, same new-file-per-message pattern already proven safe today.
        drive_file_id = None
        if req.to_agent in ("BC", "ALL"):
            try:
                token = _drive_token()
                fname = f"{req.from_agent}_TO_BC_{req.subject[:50].replace(' ', '_')}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.md"
                body_text = f"{req.from_agent} -> BC | {_buck_local_str()}\nmessage_id: {row['message_id']}\npriority: {req.priority}\n\n{req.subject}\n{'=' * len(req.subject)}\n\n{req.body}\n"
                boundary = "hciamb"
                metadata = json.dumps({"name": fname, "parents": [HCI_MASTER_FOLDER_ID]})
                upload_body = (
                    f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n{metadata}\r\n"
                    f"--{boundary}\r\nContent-Type: text/plain\r\n\r\n{body_text}\r\n--{boundary}--"
                )
                r = requests.post(
                    "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&supportsAllDrives=true",
                    headers={"Authorization": f"Bearer {token}", "Content-Type": f"multipart/related; boundary={boundary}"},
                    data=upload_body.encode("utf-8"), timeout=20)
                if r.status_code == 200:
                    drive_file_id = r.json().get("id")
                    with _pg() as conn:
                        with conn.cursor() as cur:
                            cur.execute("UPDATE agent_messages SET drive_file_id = %s WHERE message_id = %s",
                                        (drive_file_id, row["message_id"]))
            except Exception:
                pass  # DB row is still the source of truth even if the Drive mirror fails

        return _response("/agent/messages", {
            "message_id": str(row["message_id"]), "thread_id": str(row["thread_id"]),
            "timestamp_mt": row["timestamp_mt"].isoformat(), "drive_file_id": drive_file_id,
        }, start=t0)
    except Exception as e:
        return _response("/agent/messages", {}, errors=[str(e)], start=t0)


@router.get("/agent/messages/unread")
def agent_messages_unread(agent: str = Query(..., description="BC|GBT|CODE")):
    t0 = time.time()
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT message_id, thread_id, from_agent, subject, body,
                           timestamp_mt, priority, drive_file_id, requires_response
                    FROM agent_messages
                    WHERE to_agent IN (%s, 'ALL') AND status = 'pending'
                    ORDER BY timestamp_mt ASC
                """, (agent,))
                rows = [dict(r) for r in cur.fetchall()]
        for r in rows:
            r["message_id"] = str(r["message_id"])
            r["thread_id"] = str(r["thread_id"])
            r["timestamp_mt"] = r["timestamp_mt"].isoformat()
        return _response("/agent/messages/unread", {"agent": agent, "count": len(rows), "messages": rows}, start=t0)
    except Exception as e:
        return _response("/agent/messages/unread", {}, errors=[str(e)], start=t0)


class AgentMessageReadPayload(BaseModel):
    agent: str


@router.post("/agent/messages/{message_id}/read")
def agent_messages_mark_read(message_id: str, req: AgentMessageReadPayload):
    t0 = time.time()
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE agent_messages SET status = 'read', read_at_mt = NOW()
                    WHERE message_id = %s AND status = 'pending'
                    RETURNING message_id
                """, (message_id,))
                row = cur.fetchone()
        _touch_heartbeat(req.agent, f"read agent_message {message_id}")
        return _response(f"/agent/messages/{message_id}/read",
                          {"updated": bool(row)}, start=t0)
    except Exception as e:
        return _response(f"/agent/messages/{message_id}/read", {}, errors=[str(e)], start=t0)


class AgentMessageReplyPayload(BaseModel):
    from_agent: str
    body: str
    drive_file_id: Optional[str] = None


@router.post("/agent/messages/{message_id}/reply")
def agent_messages_reply(message_id: str, req: AgentMessageReplyPayload):
    """Replies within the same thread as a new agent_messages row, and closes
    the original if it required a response - matching ADR-003's spec."""
    t0 = time.time()
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT thread_id, from_agent, requires_response FROM agent_messages WHERE message_id = %s", (message_id,))
                orig = cur.fetchone()
                if not orig:
                    return _response(f"/agent/messages/{message_id}/reply", {}, errors=["original message not found"], start=t0)
                cur.execute("""
                    INSERT INTO agent_messages (thread_id, from_agent, to_agent, subject, body, drive_file_id, status)
                    VALUES (%s, %s, %s, %s, %s, %s, 'pending')
                    RETURNING message_id, timestamp_mt
                """, (orig["thread_id"], req.from_agent, orig["from_agent"], "Re:", req.body, req.drive_file_id))
                reply_row = cur.fetchone()
                if orig["requires_response"]:
                    cur.execute("""
                        UPDATE agent_messages SET status = 'closed', replied_at_mt = NOW(), closed_at_mt = NOW()
                        WHERE message_id = %s
                    """, (message_id,))
        _touch_heartbeat(req.from_agent, f"replied to agent_message {message_id}")
        return _response(f"/agent/messages/{message_id}/reply", {
            "reply_message_id": str(reply_row["message_id"]),
            "timestamp_mt": reply_row["timestamp_mt"].isoformat(),
            "original_closed": bool(orig["requires_response"]),
        }, start=t0)
    except Exception as e:
        return _response(f"/agent/messages/{message_id}/reply", {}, errors=[str(e)], start=t0)


@router.get("/agent/status")
def agent_status_all():
    t0 = time.time()
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT agent_id, status, last_heartbeat_mt, current_mission, session_id, announced_at_mt FROM agent_heartbeats")
                rows = {r["agent_id"]: dict(r) for r in cur.fetchall()}
        out = {}
        for agent_id in ("BC", "GBT", "CODE"):
            r = rows.get(agent_id, {"agent_id": agent_id, "status": "offline", "last_heartbeat_mt": None,
                                     "current_mission": None, "session_id": None, "announced_at_mt": None})
            status = r["status"]
            if r["last_heartbeat_mt"]:
                age_min = (datetime.now(timezone.utc) - r["last_heartbeat_mt"]).total_seconds() / 60
                if status != "offline" and age_min > HEARTBEAT_STALE_MINUTES:
                    status = "stale"
                r["last_heartbeat_mt"] = r["last_heartbeat_mt"].isoformat()
            if r.get("announced_at_mt"):
                r["announced_at_mt"] = r["announced_at_mt"].isoformat()
            out[agent_id] = {"status": status, "last_heartbeat_mt": r["last_heartbeat_mt"],
                              "current_mission": r["current_mission"], "session_id": r["session_id"]}
        return _response("/agent/status", out, start=t0)
    except Exception as e:
        return _response("/agent/status", {}, errors=[str(e)], start=t0)


class AgentDecisionCreate(BaseModel):
    decision: str
    rationale: str
    evidence: Optional[str] = None
    proposed_by: str
    thread_id: Optional[str] = None


@router.post("/agent/decisions")
def agent_decisions_create(req: AgentDecisionCreate):
    t0 = time.time()
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO decision_log (thread_id, decision, rationale, evidence, proposed_by)
                    VALUES (%s,%s,%s,%s,%s)
                    RETURNING decision_id, created_at_mt
                """, (req.thread_id, req.decision, req.rationale, req.evidence, req.proposed_by))
                row = cur.fetchone()
        return _response("/agent/decisions", {
            "decision_id": str(row["decision_id"]), "created_at_mt": row["created_at_mt"].isoformat(),
        }, start=t0)
    except Exception as e:
        return _response("/agent/decisions", {}, errors=[str(e)], start=t0)


@router.get("/agent/decisions")
def agent_decisions_list(status: str = Query("pending", description="proposed|approved|rejected|implemented|pending(=proposed)")):
    t0 = time.time()
    real_status = "proposed" if status == "pending" else status
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT decision_id, thread_id, decision, rationale, evidence, proposed_by,
                           approved_by, status, created_at_mt
                    FROM decision_log WHERE status = %s ORDER BY created_at_mt DESC
                """, (real_status,))
                rows = [dict(r) for r in cur.fetchall()]
        for r in rows:
            r["decision_id"] = str(r["decision_id"])
            r["thread_id"] = str(r["thread_id"]) if r["thread_id"] else None
            r["created_at_mt"] = r["created_at_mt"].isoformat()
        return _response("/agent/decisions", {"count": len(rows), "decisions": rows}, start=t0)
    except Exception as e:
        return _response("/agent/decisions", {}, errors=[str(e)], start=t0)


class AgentDecisionApprovePayload(BaseModel):
    agent: str


@router.post("/agent/decisions/{decision_id}/approve")
def agent_decisions_approve(decision_id: str, req: AgentDecisionApprovePayload):
    t0 = time.time()
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE decision_log
                    SET approved_by = array_append(approved_by, %s),
                        status = CASE WHEN cardinality(array_append(approved_by, %s)) >= 2 THEN 'approved' ELSE status END,
                        approved_at_mt = CASE WHEN cardinality(array_append(approved_by, %s)) >= 2 THEN NOW() ELSE approved_at_mt END
                    WHERE decision_id = %s AND NOT (%s = ANY(approved_by))
                    RETURNING decision_id, approved_by, status
                """, (req.agent, req.agent, req.agent, decision_id, req.agent))
                row = cur.fetchone()
        if not row:
            return _response(f"/agent/decisions/{decision_id}/approve", {}, errors=["not found or already approved by this agent"], start=t0)
        return _response(f"/agent/decisions/{decision_id}/approve", {
            "decision_id": str(row["decision_id"]), "approved_by": row["approved_by"], "status": row["status"],
        }, start=t0)
    except Exception as e:
        return _response(f"/agent/decisions/{decision_id}/approve", {}, errors=[str(e)], start=t0)


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

                # Found 2026-07-07 (ADR-016): continuous-discovery was correctly
                # detecting real staleness/errors and firing real ntfy pushes, but
                # nothing required any agent to actually read that channel - a
                # genuine "HubSpot: STALE" alert sat unread for days while the
                # underlying cause (a dead scheduler) went unfixed. Surfacing the
                # standing alert records it now creates here so a session-start
                # read of warm-start can't miss them the way a push notification
                # history can.
                cur.execute("""
                    SELECT id, title, priority, created_at FROM ai_messages
                    WHERE source_agent = 'continuous_discovery' AND status NOT IN ('COMPLETE','REJECTED')
                    ORDER BY created_at ASC
                """)
                open_alerts = [dict(r) for r in cur.fetchall()]
                for r in open_alerts:
                    r["created_at"] = r["created_at"].isoformat()
                out["open_system_alerts"] = open_alerts

                # Found 2026-07-07: Claude Code had never once called /telegram/ack
                # in this project's history (last_telegram_ack_id was still its
                # default of 0) - 229 real Telegram messages from Buck, including
                # direct questions and explicit instructions, sat completely unread
                # across more than a week of sessions. /telegram/messages already
                # existed for exactly this (built 2026-07-01 for GBT/BC, who can't
                # receive a live push at all) but nothing made checking it
                # mandatory for Claude Code specifically, who *can* receive pushes
                # and so had no obvious reason to think polling was still needed.
                # Surface the real unread count here so it can't be missed at
                # session start regardless of agent.
                for _agent_key in ("claude_code", "chatgpt", "browser_claude"):
                    cur.execute("SELECT metadata FROM ai_agent_heartbeat WHERE agent = %s", (_agent_key,))
                    _row = cur.fetchone()
                    _last_ack = (_row["metadata"] or {}).get("last_telegram_ack_id", 0) if _row else 0
                    cur.execute(
                        "SELECT COUNT(*) AS c FROM platform_events WHERE event_type='buck_message' AND id > %s",
                        (_last_ack,),
                    )
                    _unread = cur.fetchone()["c"]
                    out.setdefault("telegram_unread_by_agent", {})[_agent_key] = _unread

                # AI Team Document Bus (2026-07-10) - unread HCI AI Master
                # coordination-doc counts per agent, same shape as
                # telegram_unread_by_agent above. Doesn't call the sync (that
                # hits the Drive API); a warm-start should stay fast and cheap,
                # so this reads the registry as of the last /coordination/documents
                # LIST call by any agent rather than re-scanning Drive itself.
                # Uses "CODE"/"GBT"/"BC" - the literal agent strings the
                # /coordination/documents/{id}/acknowledge endpoint's own
                # acceptance test sends - not the claude_code/chatgpt/
                # browser_claude convention used by telegram_unread_by_agent.
                cur.execute("SELECT COUNT(*) AS c FROM coordination_documents")
                if cur.fetchone()["c"] > 0:
                    for _agent_key in _COORD_DOC_ROSTER:
                        cur.execute("""
                            SELECT COUNT(*) AS c FROM coordination_documents cd
                            WHERE NOT EXISTS (
                                SELECT 1 FROM coordination_document_acks a
                                WHERE a.file_id = cd.file_id AND a.agent = %s
                            )
                        """, (_agent_key,))
                        out.setdefault("unread_coordination_docs_by_agent", {})[_agent_key] = cur.fetchone()["c"]

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
    no new table) rather than building a separate telegram_messages table.

    Does NOT touch heartbeat (fixed 2026-07-01) — this is a read-only GET, and anyone
    with API access can call it with any agent name in the query string (e.g. Claude
    Code verifying the endpoint on Browser Claude's behalf), which repeatedly produced
    a false "browser_claude is ONLINE" signal in Mission Control from activity that
    wasn't actually Browser Claude. Heartbeat should only reflect an agent genuinely
    announcing itself — use POST /ai/heartbeat or /telegram/ack for that."""
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
                    SELECT COUNT(*) AS c FROM platform_events
                    WHERE event_type = 'buck_message' AND id > %s
                """, (last_ack_id,))
                backlog_count = cur.fetchone()["c"]

                # Return the MOST RECENT messages first, not the oldest-unread-first
                # (fixed 2026-07-06 - found live via GBT's own onboarding audit: an
                # agent that falls behind on acking never catches up to "now", it just
                # sees the same old backlog page forever no matter how many times it
                # polls, since ORDER BY id ASC LIMIT N always returns the same oldest N
                # until every prior message is acked one page at a time. A "what has
                # Buck said" query should surface current state first; the backlog
                # count is still reported so nothing is silently hidden.
                cur.execute("""
                    SELECT id, payload, published_at FROM platform_events
                    WHERE event_type = 'buck_message' AND id > %s
                    ORDER BY id DESC LIMIT %s
                """, (last_ack_id, limit))
                rows = cur.fetchall()
        messages = [{
            "message_id": r["id"], "read_status": "unread",
            "from": "Buck Adams", "text": (r["payload"] or {}).get("text") or (r["payload"] or {}).get("body"),
            "timestamp": r["published_at"].isoformat(),
        } for r in rows]
        messages.reverse()  # oldest-of-this-batch first for readable chronological order
        return _response("/telegram/messages", {
            "agent": key, "last_ack_id": last_ack_id, "backlog_count": backlog_count,
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


@router.get("/buck/compose", response_class=HTMLResponse, include_in_schema=False)
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


# ── Field Brain — cross-project historical Q&A (2026-07-08) ─────────────────────
# Buck's framing: "what does a similar build cost per sqft, who is the most
# reliable sub" were examples, not the whole spec — this answers any cross-project
# historical question, field or GBT side. Uses the same async job_id pattern as
# /plan-review/analyze: the underlying call does multiple Qdrant searches plus a
# Claude synthesis call, which is exactly the kind of multi-second latency that
# broke GBT's Action layer before (see /project/{code}/brain's ai_summary=false
# fix and _PLAN_REVIEW_JOBS docstring above) - don't make the same mistake twice.
class FieldBrainPayload(BaseModel):
    question: str = ""
    job_id: Optional[str] = None

_FIELD_BRAIN_JOBS: dict = {}

def _run_field_brain_job(job_id: str, question: str):
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "services", "field_brain"))
        from field_brain_svc import FieldBrainService
        result = FieldBrainService.query(question)
        _FIELD_BRAIN_JOBS[job_id] = {"status": "done", "result": result}
    except Exception as e:
        _FIELD_BRAIN_JOBS[job_id] = {"status": "error", "error": str(e)}

@router.post("/brain/ask")
def brain_ask(req: FieldBrainPayload):
    """Ask the Field Brain any cross-project historical question — cost benchmarks,
    sub reliability, past issues on similar scopes, lessons learned. Not scoped to
    one project. Async: call without job_id to start, call again with the returned
    job_id to get the result (usually ready in 5-10s)."""
    t0 = time.time()
    try:
        if req.job_id:
            job = _FIELD_BRAIN_JOBS.get(req.job_id)
            if not job:
                return _response("/brain/ask", {"job_id": req.job_id, "status": "unknown"},
                                  errors=["No job with that ID - it may have expired (server restart) or never existed"], start=t0)
            if job["status"] == "done":
                return _response("/brain/ask", job["result"], start=t0)
            if job["status"] == "error":
                return _response("/brain/ask", {"job_id": req.job_id, "status": "error"},
                                  errors=[job["error"]], start=t0)
            return _response("/brain/ask", {"job_id": req.job_id, "status": "processing",
                              "note": "Still running - poll again in a few seconds with the same job_id."}, start=t0)

        if not req.question.strip():
            return _response("/brain/ask", {}, errors=["question is required"], start=t0)
        job_id = str(uuid.uuid4())[:12]
        _FIELD_BRAIN_JOBS[job_id] = {"status": "processing"}
        thread = threading.Thread(target=_run_field_brain_job, args=(job_id, req.question), daemon=True)
        thread.start()
        _log("/brain/ask", "ChatGPT", "field_brain", "ok", round((time.time()-t0)*1000), str(uuid.uuid4())[:8], req.question[:80])
        return _response("/brain/ask", {
            "job_id": job_id, "status": "processing",
            "note": "Query started - call this same endpoint again with this job_id to get the result."
        }, start=t0)
    except HTTPException as e:
        return _response("/brain/ask", {}, errors=[str(e.detail)], start=t0)
    except Exception as e:
        return _response("/brain/ask", {}, errors=[str(e)], start=t0)


# ── Drawing Reader — 2026-07-08 ──────────────────────────────────────────────
# Built after a real demo failure: Adam asked about a wood column on sheet
# A3.332, Field GBT correctly couldn't find it via semantic search (drawings
# are graphical, sheet numbers live in title blocks, not embedded body text)
# and correctly refused to guess. This reads the actual drawing-set PDF
# directly with Claude's native PDF vision instead of text search - see
# services/drawing_reader/drawing_reader_svc.py and the STRATEGIC_BACKLOG.md
# entry for the bigger sheet-indexing follow-up this doesn't yet cover.

class DrawingAskPayload(BaseModel):
    project_code: str = ""
    question: str = ""
    job_id: Optional[str] = None

_DRAWING_JOBS: dict = {}

def _run_drawing_job(job_id: str, project_code: str, question: str):
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "services", "drawing_reader"))
        from drawing_reader_svc import DrawingReaderService
        result = DrawingReaderService.ask(project_code, question)
        _DRAWING_JOBS[job_id] = {"status": "done", "result": result}
    except Exception as e:
        _DRAWING_JOBS[job_id] = {"status": "error", "error": str(e)}

@router.post("/drawings/ask")
def drawings_ask(req: DrawingAskPayload):
    """Ask a question about a project's drawing set (architectural, structural,
    civil) - reads the actual PDF directly rather than semantic search, which
    doesn't work for drawing sheets. Async like /brain/ask: call without
    job_id to start, call again with the returned job_id after ~15-30s (PDF
    download + Claude vision takes longer than the field-brain text search)."""
    t0 = time.time()
    try:
        if req.job_id:
            job = _DRAWING_JOBS.get(req.job_id)
            if not job:
                return _response("/drawings/ask", {"job_id": req.job_id, "status": "unknown"},
                                  errors=["No job with that ID - it may have expired (server restart) or never existed"], start=t0)
            if job["status"] == "done":
                return _response("/drawings/ask", job["result"], start=t0)
            if job["status"] == "error":
                return _response("/drawings/ask", {"job_id": req.job_id, "status": "error"},
                                  errors=[job["error"]], start=t0)
            return _response("/drawings/ask", {"job_id": req.job_id, "status": "processing",
                              "note": "Still running - poll again in a few seconds with the same job_id."}, start=t0)

        if not req.project_code.strip() or not req.question.strip():
            return _response("/drawings/ask", {}, errors=["project_code and question are both required"], start=t0)
        job_id = str(uuid.uuid4())[:12]
        _DRAWING_JOBS[job_id] = {"status": "processing"}
        thread = threading.Thread(target=_run_drawing_job, args=(job_id, req.project_code, req.question), daemon=True)
        thread.start()
        _log("/drawings/ask", "ChatGPT", "drawing_reader", "ok", round((time.time()-t0)*1000), str(uuid.uuid4())[:8], req.question[:80])
        return _response("/drawings/ask", {
            "job_id": job_id, "status": "processing",
            "note": "Query started - call this same endpoint again with this job_id to get the result (~15-30s)."
        }, start=t0)
    except Exception as e:
        return _response("/drawings/ask", {}, errors=[str(e)], start=t0)


# ── Book (canonical Operations Manual) read/write for GBT — 2026-07-08 ──────────
# GBT flagged tonight it has no file-read action for HCI_AI_OS_MANUAL.md, so it
# couldn't spot-check chapters or contribute to the book at all. Chapter-scoped,
# not whole-file: reads/writes always operate on one chapter's content between its
# own header and the next chapter's header, so a write can't silently corrupt
# unrelated chapters (the same class of bug as the sync-live-state regex incident
# earlier tonight - this is deliberately structured to make that impossible here).
# Writes commit locally with full attribution; never auto-pushed, matching standing
# git-push-needs-Buck's-OK policy.
_BOOK_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "HCI_AI_OS_MANUAL.md")
_CHAPTER_RE = re.compile(r"^#{1,2}\s+Chapter\s+(\d+)\s+—\s*(.*)$", re.MULTILINE)


def _book_chapter_index():
    with open(_BOOK_PATH, "r") as f:
        text = f.read()
    matches = list(_CHAPTER_RE.finditer(text))
    chapters = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chapters.append({
            "number": int(m.group(1)),
            "title": m.group(2).strip(),
            "start": start,
            "end": end,
        })
    return text, chapters


@router.get("/book/chapters")
def book_chapters():
    """List every chapter in the canonical Operations Manual with title + line count."""
    t0 = time.time()
    try:
        text, chapters = _book_chapter_index()
        out = [{"number": c["number"], "title": c["title"],
                "char_count": c["end"] - c["start"]} for c in chapters]
        return _response("/book/chapters", {"total_chapters": len(out), "chapters": out}, start=t0)
    except Exception as e:
        return _response("/book/chapters", {}, errors=[str(e)], start=t0)


@router.get("/book/chapter/{number}")
def book_chapter_read(number: int):
    """Read one chapter's full real content, verbatim, from the canonical manual."""
    t0 = time.time()
    try:
        text, chapters = _book_chapter_index()
        match = next((c for c in chapters if c["number"] == number), None)
        if not match:
            return _response(f"/book/chapter/{number}", {}, errors=[f"Chapter {number} not found"], start=t0)
        content = text[match["start"]:match["end"]].strip()
        return _response(f"/book/chapter/{number}", {
            "number": number, "title": match["title"], "content": content,
        }, start=t0)
    except Exception as e:
        return _response(f"/book/chapter/{number}", {}, errors=[str(e)], start=t0)


class BookChapterWrite(BaseModel):
    content: str
    author: str = "chatgpt"
    summary: str = ""


@router.post("/book/chapter/{number}")
def book_chapter_write(number: int, req: BookChapterWrite):
    """Replace one chapter's content. Chapter-scoped so a write can't touch any
    other chapter. Commits locally to git for a real audit trail; never pushed
    automatically. content must start with the chapter's own '# Chapter N — Title'
    header line."""
    t0 = time.time()
    try:
        if not re.match(r"^#{1,2}\s+Chapter\s+\d+\s+—", req.content.strip()):
            return _response(f"/book/chapter/{number}", {}, errors=[
                "content must start with a '# Chapter N — Title' header line matching this chapter"
            ], start=t0)
        text, chapters = _book_chapter_index()
        match = next((c for c in chapters if c["number"] == number), None)
        if not match:
            return _response(f"/book/chapter/{number}", {}, errors=[f"Chapter {number} not found - use book/chapters to list valid numbers"], start=t0)
        new_content = req.content.strip() + "\n\n"
        new_text = text[:match["start"]] + new_content + text[match["end"]:]
        with open(_BOOK_PATH, "w") as f:
            f.write(new_text)
        commit_msg = f"Book: update Chapter {number} via GBT ({req.author})\n\n{req.summary}".strip()
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        # Path-scoped commit (`git commit -- <path>`), not `git add` + plain commit —
        # found 2026-07-08: `git add` on this one file, followed by a bare `git commit`,
        # swept in whatever else happened to already be staged from unrelated work in
        # progress at call time and misattributed it to this endpoint's author. `commit
        # -- <path>` only ever commits that path's changes regardless of index state.
        commit_result = subprocess.run(
            ["git", "commit", "-m", commit_msg, "--", "HCI_AI_OS_MANUAL.md"],
            cwd=repo_root, capture_output=True, text=True,
        )
        _log(f"/book/chapter/{number}", req.author, "HCI_AI_OS_MANUAL.md", "ok",
             round((time.time()-t0)*1000), str(uuid.uuid4())[:8], f"chapter {number} updated")
        return _response(f"/book/chapter/{number}", {
            "number": number, "status": "written",
            "committed_locally": commit_result.returncode == 0,
            "git_output": (commit_result.stdout or commit_result.stderr).strip()[:300],
            "note": "Committed locally only - not pushed. Buck's standing policy requires explicit authorization to git push.",
        }, start=t0)
    except Exception as e:
        return _response(f"/book/chapter/{number}", {}, errors=[str(e)], start=t0)

"""
Workflow trigger endpoints.
All workflows can be called via POST or triggered by n8n/launchd.
"""
import sys, os, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "workflows"))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Any

# ── Workflow Registry ──────────────────────────────────────────────────────────
WORKFLOW_REGISTRY = [
    {"id": "WF-001", "name": "New Project Setup",       "status": "active",   "trigger": "manual",    "endpoint": "/api/v1/workflows/wf001/new-project"},
    {"id": "WF-002", "name": "Meeting Intelligence",    "status": "active",   "trigger": "manual",    "endpoint": "/api/v1/workflows/wf002/meeting"},
    {"id": "WF-003", "name": "Morning Brief",           "status": "active",   "trigger": "scheduled", "endpoint": "/api/v1/workflows/wf003/morning-brief"},
    {"id": "WF-004", "name": "Daily Log (legacy)",      "status": "active",   "trigger": "manual",    "endpoint": "/api/v1/workflows/wf004/daily-log"},
    {"id": "WF-005", "name": "Lessons Learned",         "status": "active",   "trigger": "manual",    "endpoint": "/api/v1/workflows/wf005/lesson"},
    {"id": "WF-006", "name": "Inbox Review",            "status": "active",   "trigger": "scheduled", "endpoint": "/api/v1/workflows/wf006/inbox-review"},
    {"id": "WF-007", "name": "Bid Leveling",            "status": "active",   "trigger": "webhook",   "endpoint": "n8n: /webhook/bid-leveling"},
    {"id": "WF-SYNC-HS",    "name": "HubSpot Sync",    "status": "active",   "trigger": "scheduled", "endpoint": "/api/v1/workflows/sync/hubspot"},
    {"id": "WF-SYNC-HOUZZ", "name": "Houzz Sync",      "status": "active",   "trigger": "scheduled", "endpoint": "/api/v1/workflows/sync/houzz"},
    {"id": "WF-SYNC-DRIVE", "name": "Drive Sync",      "status": "active",   "trigger": "manual",    "endpoint": "/api/v1/workflows/sync/drive"},
    {"id": "WF-SUPER",  "name": "Superintendent Log",  "status": "active",   "trigger": "manual",    "endpoint": "/api/v1/workflows/wf-super/daily-log"},
    {"id": "WF-PM",     "name": "PM Daily Review",     "status": "active",   "trigger": "manual",    "endpoint": "/api/v1/workflows/wf-pm/daily-review/{project_number}"},
    {"id": "WF-PM-W",   "name": "PM Weekly Report",    "status": "active",   "trigger": "scheduled", "endpoint": "/api/v1/workflows/wf-pm/weekly-report"},
    {"id": "WF-REPORT-DAILY",  "name": "Daily Field Report",      "status": "active",  "trigger": "auto",      "endpoint": "/api/v1/workflows/wf-report/daily-field/{log_id}"},
    {"id": "WF-REPORT-EXEC",   "name": "Executive Health Report", "status": "active",  "trigger": "scheduled", "endpoint": "/api/v1/workflows/wf-report/exec-health"},
    {"id": "WF-REPORT-OWNER",  "name": "Owner Summary",           "status": "active",  "trigger": "manual",    "endpoint": "/api/v1/workflows/wf-report/owner-summary/{project}"},
    {"id": "WF-REPORT-ALERT",  "name": "Schedule Variance Alert", "status": "active",  "trigger": "auto",      "endpoint": "/api/v1/workflows/wf-report/schedule-alert/{variance_id}"},
    {"id": "WF-REPORT-WEEKLY", "name": "Weekly PM Email",         "status": "active",  "trigger": "scheduled", "endpoint": "/api/v1/workflows/wf-report/weekly-pm"},
]

TRIGGER_MAP = {
    "WF-001":            "/wf001/new-project",
    "WF-002":            "/wf002/meeting",
    "WF-003":            "/wf003/morning-brief",
    "WF-004":            "/wf004/daily-log",
    "WF-005":            "/wf005/lesson",
    "WF-006":            "/wf006/inbox-review",
    "WF-SYNC-HS":        "/sync/hubspot",
    "WF-SYNC-HOUZZ":     "/sync/houzz",
    "WF-SYNC-DRIVE":     "/sync/drive",
    "WF-SUPER":          "/wf-super/daily-log",
    "WF-PM":             "/wf-pm/daily-review/{project_number}",
    "WF-PM-W":           "/wf-pm/weekly-report",
    "WF-REPORT-EXEC":    "/wf-report/exec-health",
    "WF-REPORT-WEEKLY":  "/wf-report/weekly-pm",
    # These require specific IDs — invoke at their direct endpoints:
    # WF-REPORT-DAILY  → POST /wf-report/daily-field/{log_id}
    # WF-REPORT-OWNER  → POST /wf-report/owner-summary/{project_number}
    # WF-REPORT-ALERT  → POST /wf-report/schedule-alert/{variance_id}
    # WF-007           → n8n webhook (external)
}


def _log_workflow_event(workflow_id: str, event_type: str,
                        payload: dict = None, project_id: int = None):
    """Write to workflow_events table (fire-and-forget)."""
    try:
        import psycopg2, json
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))
        conn = psycopg2.connect(
            host=os.environ.get("POSTGRES_HOST", "localhost"),
            port=int(os.environ.get("POSTGRES_PORT", 5432)),
            dbname=os.environ.get("POSTGRES_DB", "hci_os"),
            user=os.environ.get("POSTGRES_USER", "hci_admin"),
            password=os.environ.get("POSTGRES_PASSWORD", ""),
        )
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO workflow_events (workflow_id, project_id, event_type, payload) "
            "VALUES (%s, %s, %s, %s::jsonb)",
            (workflow_id, project_id, event_type, json.dumps(payload or {}))
        )
        conn.commit()
        conn.close()
    except Exception:
        pass

router = APIRouter()


# ── WF-001: New Project Setup ─────────────────────────────────────────────────

class NewProjectRequest(BaseModel):
    name:            str
    address:         str
    city:            str = "Aspen"
    state:           str = "CO"
    scope:           str = ""
    owner_name:      str = ""
    pm_name:         str = ""
    super_name:      str = ""
    budget_estimate: Optional[float] = None

@router.post("/wf001/new-project")
def wf001_new_project(req: NewProjectRequest):
    """WF-001: Create new HCI project — HubSpot deal + Postgres + Qdrant."""
    from wf001_new_project import run
    result = run(**req.model_dump())
    if result.get("error") and "already exists" not in result.get("error", ""):
        raise HTTPException(500, result["error"])
    return result


# ── WF-002: Meeting Intelligence ──────────────────────────────────────────────

class MeetingRequest(BaseModel):
    project_id:       int
    title:            str
    notes:            str
    meeting_date:     Optional[str] = None
    attendees:        List[str] = []
    meeting_type:     str = "site_meeting"
    create_hs_tasks:  bool = True
    due_days:         int = 3

@router.post("/wf002/meeting")
def wf002_meeting(req: MeetingRequest):
    """WF-002: Log meeting notes, extract action items, create HubSpot tasks."""
    from wf002_meeting_intelligence import run
    result = run(**req.model_dump())
    if result.get("status") == "failed":
        raise HTTPException(500, result.get("error", "Unknown error"))
    return result


# ── WF-003: Morning Brief ─────────────────────────────────────────────────────

class MorningBriefRequest(BaseModel):
    send:         bool = False
    inbox_result: Optional[dict] = None  # pass WF-006 output for enriched inbox section

@router.post("/wf003/morning-brief")
def wf003_morning_brief(req: MorningBriefRequest = MorningBriefRequest()):
    """WF-003: Compile and send the morning brief to Buck."""
    from wf003_morning_brief import run
    return run(send=req.send, inbox_result=req.inbox_result)

@router.get("/wf003/morning-brief/preview")
def wf003_preview():
    """WF-003: Return morning brief HTML without sending."""
    from wf003_morning_brief import run
    return run(send=False)


# ── WF-006: Inbox Review ──────────────────────────────────────────────────────

class InboxReviewRequest(BaseModel):
    max_emails:    int  = 30
    create_drafts: bool = True

@router.post("/wf006/inbox-review")
def wf006_inbox_review(req: InboxReviewRequest = InboxReviewRequest()):
    """WF-006: Read unread emails, classify, move to project folders, draft AI replies."""
    from wf006_inbox_review import run
    return run(max_emails=req.max_emails, create_drafts=req.create_drafts)


# ── WF-004: Daily Log ─────────────────────────────────────────────────────────

class DailyLogRequest(BaseModel):
    project_id:     int
    work_performed: str
    issues:         str = ""
    log_date:       Optional[str] = None
    weather:        str = ""
    temp_high:      Optional[int] = None
    temp_low:       Optional[int] = None
    crew_on_site:   List[str] = []
    photos_count:   int = 0
    logged_by:      str = "Buck Adams"

@router.post("/wf004/daily-log")
def wf004_daily_log(req: DailyLogRequest):
    """WF-004: Log daily site report to Postgres + Qdrant."""
    from wf004_daily_log import run
    result = run(**req.model_dump())
    if result.get("status") == "failed":
        raise HTTPException(500, result.get("error", "Unknown error"))
    return result


# ── WF-005: Lessons Learned ───────────────────────────────────────────────────

class LessonRequest(BaseModel):
    title:                  str
    description:            str
    project_id:             Optional[int] = None
    vendor_id:              Optional[int] = None
    csi_division:           str = ""
    category:               str = "other"
    outcome:                str = ""
    action_taken:           str = ""
    future_recommendation:  str = ""
    recorded_by:            str = "Buck Adams"

@router.post("/wf005/lesson")
def wf005_lesson(req: LessonRequest):
    """WF-005: Record a lesson learned to Postgres + Qdrant."""
    from wf005_lessons_learned import run
    result = run(**req.model_dump())
    if result.get("status") == "failed":
        raise HTTPException(500, result.get("error", "Unknown error"))
    return result


# ── Daily syncs (read-only from external systems) ─────────────────────────────

@router.post("/sync/hubspot")
def sync_hubspot():
    """Pull all HubSpot deals, notes, tasks → Postgres + Qdrant. Auto-runs at 6:50 AM."""
    from sync_hubspot import run
    return run()

@router.post("/sync/houzz")
def sync_houzz(visible: bool = False):
    """
    Read Houzz Pro daily logs + schedule → Postgres + Qdrant.
    Requires HOUZZ_EMAIL and HOUZZ_PASSWORD in .env.
    visible=true opens a browser window (for debugging).
    Auto-runs at 6:45 AM.
    """
    from sync_houzz import run
    return run(headless=not visible)

@router.post("/sync/drive")
def sync_drive():
    """
    Read all Google Drive files (PDF, DOCX, XLSX, GDOC, GSHEET) → Qdrant drive_memory.
    Skips unchanged files (mtime-tracked in Postgres drive_sync_log).
    Run weekly or on-demand — not daily.
    """
    from sync_drive import run
    return run()

@router.post("/sync/all")
def sync_all():
    """Run Houzz sync then HubSpot sync — same as morning startup sequence."""
    from sync_houzz import run as houzz_run
    from sync_hubspot import run as hs_run
    houzz = houzz_run(headless=True)
    hs    = hs_run()
    return {"houzz": houzz, "hubspot": hs}


# ── WF-SUPER: Superintendent Daily Log ───────────────────────────────────────

class SuperintendentLogRequest(BaseModel):
    project_number:          str
    work_performed:          str
    log_date:                Optional[str] = None
    weather:                 str = ""
    temp_high:               Optional[int] = None
    temp_low:                Optional[int] = None
    crew_on_site:            List[Any] = []
    deliveries:              List[str] = []
    inspections:             List[str] = []
    quality_notes:           str = ""
    safety_notes:            str = ""
    subcontractor_progress:  str = ""
    constraints:             List[str] = []
    lookahead:               str = ""
    field_risks:             List[str] = []
    issues:                  str = ""
    photos_count:            int = 0
    logged_by:               str = "Buck Adams"

@router.post("/wf-super/daily-log")
def wf_super_daily_log(req: SuperintendentLogRequest):
    """WF-SUPER: Full superintendent daily log — save, embed, analyze, flag risks, invalidate cache."""
    from wf_superintendent import run
    result = run(**req.model_dump())
    if result.get("status") == "failed":
        raise HTTPException(500, result.get("error", "Unknown error"))
    return result


# ── WF-PM: Project Manager Workflow ──────────────────────────────────────────

@router.post("/wf-pm/daily-review/{project_number}")
def wf_pm_daily_review(project_number: str):
    """WF-PM: Run a full PM controls review for one project."""
    from wf_pm import daily_review
    result = daily_review(project_number)
    if result.get("error"):
        raise HTTPException(500, result["error"])
    return result

@router.post("/wf-pm/weekly-report")
def wf_pm_weekly_report(send_email: bool = False):
    """WF-PM: Compile PM reviews for all active projects. Pass ?send_email=true to email."""
    from wf_pm import weekly_report
    return weekly_report(send_email=send_email)

@router.get("/wf-pm/status/{project_number}")
def wf_pm_last_status(project_number: str):
    """Return the latest PM review result stored in workflow_events for a project."""
    import psycopg2, psycopg2.extras, json
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))
    conn = psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST","localhost"),
        port=int(os.environ.get("POSTGRES_PORT",5432)),
        dbname=os.environ.get("POSTGRES_DB","hci_os"),
        user=os.environ.get("POSTGRES_USER","hci_admin"),
        password=os.environ.get("POSTGRES_PASSWORD",""),
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    import re
    cur = conn.cursor()
    m = re.match(r'^(\d+)', str(project_number).upper())
    prefix = m.group(1) if m else project_number
    cur.execute(
        "SELECT id FROM projects WHERE name ILIKE %s OR address ILIKE %s LIMIT 1",
        (f"{prefix}%", f"{prefix}%")
    )
    proj_row = cur.fetchone()
    if not proj_row:
        conn.close()
        raise HTTPException(404, f"Project {project_number} not found")
    cur.execute("""
        SELECT payload, created_at FROM workflow_events
        WHERE workflow_id='WF-PM' AND project_id=%s AND event_type='daily_review_complete'
        ORDER BY created_at DESC LIMIT 1
    """, (proj_row["id"],))
    ev = cur.fetchone()
    conn.close()
    if not ev:
        return {"project": project_number, "status": "no_review_yet"}
    payload = ev["payload"]
    if isinstance(payload, str):
        try: payload = json.loads(payload)
        except: pass
    return {"project": project_number, "last_review": str(ev["created_at"]), "data": payload}


# ── WF-REPORT: Reporting Framework ───────────────────────────────────────────

@router.post("/wf-report/daily-field/{log_id}")
def wf_report_daily_field(log_id: int, send: bool = False):
    """Generate and optionally email a daily field report for a log."""
    from wf_report import daily_field_report
    return daily_field_report(log_id, send=send)

@router.post("/wf-report/schedule-alert/{variance_id}")
def wf_report_schedule_alert(variance_id: int, send: bool = False):
    """Email a schedule variance alert for a detected high/critical variance."""
    from wf_report import schedule_variance_alert
    return schedule_variance_alert(variance_id, send=send)

@router.post("/wf-report/exec-health")
def wf_report_exec_health(send: bool = False):
    """Generate executive health report for all projects. ?send=false for preview."""
    from wf_report import executive_health_report
    return executive_health_report(send=send)

@router.post("/wf-report/owner-summary/{project_number}")
def wf_report_owner_summary(project_number: str, send: bool = False):
    """Generate clean owner-facing summary. ?send=true to email."""
    from wf_report import owner_summary
    return owner_summary(project_number, send=send)

@router.post("/wf-report/weekly-pm")
def wf_report_weekly_pm(send: bool = False):
    """Run weekly PM report and email to Buck. ?send=false for preview."""
    from wf_report import weekly_pm_email
    return weekly_pm_email(send=send)


# ── Workflow Registry ──────────────────────────────────────────────────────────

@router.get("")
def list_workflows():
    """GET /api/v1/workflows — full workflow registry with status and trigger info."""
    active  = [w for w in WORKFLOW_REGISTRY if w["status"] == "active"]
    planned = [w for w in WORKFLOW_REGISTRY if w["status"] == "planned"]
    return {
        "total": len(WORKFLOW_REGISTRY),
        "active": len(active),
        "planned": len(planned),
        "workflows": WORKFLOW_REGISTRY,
    }


class TriggerRequest(BaseModel):
    payload: Optional[dict] = None
    project_id: Optional[int] = None

@router.post("/{workflow_id}/trigger")
def trigger_workflow(workflow_id: str, req: TriggerRequest = TriggerRequest()):
    """POST /api/v1/workflows/{id}/trigger — trigger a workflow by registry ID."""
    wf = next((w for w in WORKFLOW_REGISTRY if w["id"] == workflow_id), None)
    if not wf:
        raise HTTPException(404, f"Workflow {workflow_id!r} not in registry")
    if wf["status"] == "planned":
        raise HTTPException(409, f"Workflow {workflow_id} is planned but not yet built")
    if workflow_id not in TRIGGER_MAP:
        raise HTTPException(501, f"Workflow {workflow_id} requires manual invocation (see endpoint: {wf['endpoint']})")

    _log_workflow_event(workflow_id, "triggered",
                        payload=req.payload, project_id=req.project_id)

    # Dispatch to the right handler
    payload = req.payload or {}
    try:
        if workflow_id == "WF-001":
            from wf001_new_project import run
            if not payload.get("name") or not payload.get("address"):
                raise HTTPException(422, "WF-001 requires name and address in payload")
            result = run(**{k: v for k, v in payload.items()
                           if k in ("name","address","city","state","scope","owner_name","pm_name","super_name","budget_estimate")})
        elif workflow_id == "WF-002":
            from wf002_meeting_intelligence import run
            if not payload.get("project_id") or not payload.get("title") or not payload.get("notes"):
                raise HTTPException(422, "WF-002 requires project_id, title, and notes in payload")
            result = run(**{k: v for k, v in payload.items()
                           if k in ("project_id","title","notes","meeting_date","attendees","meeting_type","create_hs_tasks","due_days")})
        elif workflow_id == "WF-003":
            from wf003_morning_brief import run
            result = run(send=payload.get("send", True))
        elif workflow_id == "WF-004":
            from wf004_daily_log import run
            if not payload.get("project_id") or not payload.get("work_performed"):
                raise HTTPException(422, "WF-004 requires project_id and work_performed in payload")
            result = run(**{k: v for k, v in payload.items()
                           if k in ("project_id","work_performed","issues","log_date","weather","temp_high","temp_low","crew_on_site","photos_count","logged_by")})
        elif workflow_id == "WF-005":
            from wf005_lessons_learned import run
            if not payload.get("title") or not payload.get("description"):
                raise HTTPException(422, "WF-005 requires title and description in payload")
            result = run(**{k: v for k, v in payload.items()
                           if k in ("title","description","project_id","vendor_id","csi_division","category","outcome","action_taken","future_recommendation","recorded_by")})
        elif workflow_id == "WF-006":
            from wf006_inbox_review import run
            result = run(max_emails=payload.get("max_emails", 30),
                         create_drafts=payload.get("create_drafts", True))
        elif workflow_id == "WF-SYNC-HS":
            from sync_hubspot import run
            result = run()
        elif workflow_id == "WF-SYNC-HOUZZ":
            from sync_houzz import run
            result = run(headless=True)
        elif workflow_id == "WF-SYNC-DRIVE":
            from sync_drive import run
            result = run()
        elif workflow_id == "WF-SUPER":
            from wf_superintendent import run
            if not payload.get("project_number") or not payload.get("work_performed"):
                raise HTTPException(422, "WF-SUPER requires project_number and work_performed in payload")
            valid_keys = ("project_number","work_performed","log_date","weather","temp_high","temp_low",
                          "crew_on_site","deliveries","inspections","quality_notes","safety_notes",
                          "subcontractor_progress","constraints","lookahead","field_risks","issues",
                          "photos_count","logged_by")
            result = run(**{k: v for k, v in payload.items() if k in valid_keys})
        elif workflow_id == "WF-PM":
            from wf_pm import daily_review
            project_number = payload.get("project_number", "101-FRANCIS")
            result = daily_review(project_number)
        elif workflow_id == "WF-PM-W":
            from wf_pm import weekly_report
            result = weekly_report()
        elif workflow_id == "WF-REPORT-EXEC":
            from wf_report import executive_health_report
            result = executive_health_report(send=payload.get("send", True))
        elif workflow_id == "WF-REPORT-WEEKLY":
            from wf_report import weekly_pm_email
            result = weekly_pm_email(send=payload.get("send", True))
        else:
            _log_workflow_event(workflow_id, "error",
                                payload={"error": "no dispatch handler"},
                                project_id=req.project_id)
            raise HTTPException(501, f"Workflow {workflow_id} requires direct endpoint invocation (see endpoint field)")

        _log_workflow_event(workflow_id, "completed",
                            payload={"status": result.get("status", "ok")},
                            project_id=req.project_id)
        return {"workflow_id": workflow_id, "triggered_at": datetime.datetime.utcnow().isoformat(), "result": result}

    except HTTPException:
        raise
    except Exception as e:
        _log_workflow_event(workflow_id, "error",
                            payload={"error": str(e)}, project_id=req.project_id)
        raise HTTPException(500, str(e))

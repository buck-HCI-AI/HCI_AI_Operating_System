"""
Workflow trigger endpoints.
All workflows can be called via POST or triggered by n8n/launchd.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "workflows"))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

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
    send:         bool = True
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

@router.post("/sync/all")
def sync_all():
    """Run Houzz sync then HubSpot sync — same as morning startup sequence."""
    from sync_houzz import run as houzz_run
    from sync_hubspot import run as hs_run
    houzz = houzz_run(headless=True)
    hs    = hs_run()
    return {"houzz": houzz, "hubspot": hs}

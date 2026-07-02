# CYCLE24 — Sprint 6 Priority 4: Mobile Field UX Architecture
**Cycle:** 24
**Sprint:** 6
**Priority:** 4
**Date:** 2026-07-02
**Author:** GBT (HCI Chief Architect)
**Status:** SPEC COMPLETE — Ready for Code Implementation

---

## Overview

The mobile field experience must be designed for a Superintendent standing on a jobsite, not a person sitting at a desk.

**Design Reality:**
- Muddy hands, loud environment, no desk
- Poor signal in some areas
- Phone in one hand, tool in the other
- 60 seconds maximum for any action
- Photos are the primary form of documentation

**The 5 actions that matter most:**
1. Submit daily field report
2. Upload a job site photo
3. Create a punch item
4. Report a field issue / RFI candidate
5. Record a voice note

---

## 1) What a Superintendent Must Do in Under 60 Seconds

### A. Submit a Quick Daily Field Report

Minimum fields:
- project
- date
- crew_count (can be voice: "18 guys today")
- work_summary (voice or text note)

The system auto-populates:
- weather (from weather_alerts)
- report_date (today)

Optional (can be added later):
- activities_performed
- materials_delivered
- safety_incidents
- visitors

**Draft status first.** Superintendent submits. PM approves later.

### B. Upload a Job Site Photo

Minimum fields:
- project
- photo
- optional location tag
- optional voice/text note
- optional linked entity (daily_report / punch / RFI)

Photo is uploaded to MinIO. Gemini Vision processes asynchronously.

Client-visible only after PM approval.

### C. Create a Punch Item

Minimum fields:
- project
- location_description
- description
- photo optional but strongly encouraged
- trade/vendor optional

### D. Report a Field Issue / RFI Candidate

Minimum fields:
- project
- description
- drawing_ref (optional)
- photo (optional)

Creates a draft RFI submitted_to = "PM Review". PM reviews and promotes to official RFI.

### E. Record a Voice Note

Superintendent speaks into phone.

Client receives text transcript.

System stores:
- raw transcript
- optional audio file path (MinIO)
- linked entity (if applicable)
- flagged for human review

Voice input is **field evidence**, not final structured data.

---

## 2) Voice-to-Text Pattern

**Principle:** Voice input should be treated as **field evidence**, not final structured data.

**The system stores:**
- The raw transcript exactly as spoken
- Audio file path (if recorded)
- A flag: `voice_note_pending_review = true`
- The associated entity (daily report, punch, RFI, etc.)

**The system does NOT:**
- Auto-create RFIs from voice without PM review
- Auto-update schedule based on spoken content
- Override structured data with voice input
- Send voice transcripts to clients

**Voice Payload Example:**
```json
{
  "project_id": "101F",
  "user_id": "jim",
  "submission_type": "voice_note",
  "payload": {
    "transcript": "Second floor west wall has missing blocking at the stair header. Needs framing to come back before drywall.",
    "audio_path": "optional/minio/path/audio.m4a",
    "linked_entity_type": "daily_report",
    "linked_entity_id": null,
    "pending_review": true
  }
}
```

**Future Phase 2:**
- Whisper API (OpenAI) for transcription quality
- Gemini summarization of voice note content
- Auto-suggest: "This sounds like a punch item. Create one?"

---

## 3) Offline Capability

### Principle

The mobile app should work when signal is poor or absent.

Local device queue holds submissions until reconnect.

### What Can Be Cached Locally

| Data Type | Offline Cache |
|-----------|--------------|
| Project list | Yes — readonly |
| Today's field report draft | Yes — local storage |
| Photo queue | Yes — local file system |
| Punch queue | Yes — local storage |
| Voice notes | Yes — local audio + transcript |
| Historical data | No — read-only, requires network |
| Weather data | Partial — last known |

### Offline → Online Flow

```
When offline: device writes to local queue
On reconnect: POST /mobile/queue/flush
Server creates official records
Client marks local items synced
```

### Conflict Rules

If duplicate daily report exists for today:
- If server record is draft: update it
- If server record is approved: return 400 with message
- Client shows: "Your report for today was already approved. Contact PM."

If duplicate photo is uploaded:
- Store both — duplicates are acceptable

If punch item is duplicated:
- Store both — deduplication is PM responsibility

---

## 4) PostgreSQL DDL — field_submissions_queue

This table represents **server-side receipt** of mobile/offline submissions.

```sql
CREATE TABLE IF NOT EXISTS field_submissions_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    submission_type TEXT NOT NULL,
    -- allowed:
    -- daily_report
    -- photo
    -- punch
    -- rfi
    -- voice_note

    project_id TEXT NOT NULL,

    user_id TEXT NOT NULL,

    payload JSONB NOT NULL DEFAULT '{}'::jsonb,

    status TEXT NOT NULL DEFAULT 'pending',
    -- allowed: pending | submitted | failed

    client_submission_id TEXT,
    -- Optional: client-generated ID for idempotency

    processed_entity_type TEXT,
    processed_entity_id UUID,

    error_message TEXT,

    submitted_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_field_queue_submission_type CHECK (
        submission_type IN (
            'daily_report',
            'photo',
            'punch',
            'rfi',
            'voice_note'
        )
    ),

    CONSTRAINT chk_field_queue_status CHECK (
        status IN ('pending', 'submitted', 'failed')
    )
);

CREATE INDEX IF NOT EXISTS idx_field_queue_project_id
    ON field_submissions_queue(project_id);

CREATE INDEX IF NOT EXISTS idx_field_queue_user_id
    ON field_submissions_queue(user_id);

CREATE INDEX IF NOT EXISTS idx_field_queue_status
    ON field_submissions_queue(status);

CREATE INDEX IF NOT EXISTS idx_field_queue_created_at
    ON field_submissions_queue(created_at DESC);
```

---

## 5) Pydantic Schemas

```python
from datetime import date, datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field

class MobileFieldReportQuick(BaseModel):
    project_id: str
    user_id: str
    report_date: date
    crew_count: int = Field(default=0, ge=0)
    work_summary: Optional[str] = None
    issues: Optional[str] = None
    safety_incidents: Optional[str] = None
    notes: Optional[str] = None

class MobilePhotoQuick(BaseModel):
    project_id: str
    user_id: str
    location_tag: Optional[str] = None
    linked_entity_type: Optional[str] = None
    linked_entity_id: Optional[UUID] = None
    notes: Optional[str] = None

class MobilePunchQuick(BaseModel):
    project_id: str
    user_id: str
    location_description: str
    description: str
    trade: Optional[str] = None
    assigned_to_vendor: Optional[str] = None
    priority: str = Field(default="medium", pattern="^(critical|high|medium|low)$")
    linked_photo_ids: list[UUID] = Field(default_factory=list)

class MobileRFIQuick(BaseModel):
    project_id: str
    user_id: str
    description: str
    title: Optional[str] = None
    drawing_ref: Optional[str] = None
    spec_ref: Optional[str] = None

class MobileQueueItem(BaseModel):
    client_submission_id: Optional[str] = None
    submission_type: str
    project_id: str
    user_id: str
    payload: dict[str, Any]

class MobileQueueFlushRequest(BaseModel):
    items: list[MobileQueueItem]

class MobileQueueFlushResponse(BaseModel):
    submitted: int
    failed: int
    results: list[dict[str, Any]]
```

---

## 6) FastAPI Endpoints

Router: `app/api/routers/mobile_field.py`

```python
router = APIRouter(prefix="/mobile", tags=["Mobile Field"])
```

### POST /mobile/field-report/quick
```python
@router.post("/field-report/quick", status_code=201)
def mobile_quick_field_report(
    payload: MobileFieldReportQuick,
    db: Session = Depends(get_db),
):
    # Check if report already exists for today
    existing = (
        db.query(DailyFieldReport)
        .filter(
            DailyFieldReport.project_id == payload.project_id,
            DailyFieldReport.report_date == payload.report_date,
        )
        .first()
    )

    if existing and existing.status == "approved":
        raise HTTPException(
            status_code=400,
            detail="Approved field report cannot be modified. Contact PM.",
        )

    weather = build_weather_summary(payload.project_id)

    if existing:
        # Update draft
        existing.crew_count = payload.crew_count
        existing.issues = payload.issues
        existing.notes = payload.notes or existing.notes
        if payload.safety_incidents:
            existing.safety_incidents = "Reported"
        if payload.work_summary:
            existing.activities_performed = [
                {
                    "activity_id": None,
                    "description": payload.work_summary,
                    "percent_complete": None,
                }
            ]
        db.commit()
        db.refresh(existing)
        return {"status": "updated", "report_id": existing.id}

    report = DailyFieldReport(
        project_id=payload.project_id,
        report_date=payload.report_date,
        superintendent_id=payload.user_id,
        weather_summary=weather.get("weather_summary"),
        weather_condition=weather.get("weather_condition"),
        temperature_high=weather.get("temperature_high"),
        temperature_low=weather.get("temperature_low"),
        crew_count=payload.crew_count,
        crew_by_trade=[],
        activities_performed=[
            {
                "activity_id": None,
                "description": payload.work_summary,
                "percent_complete": None,
            }
        ] if payload.work_summary else [],
        materials_delivered=[],
        issues=payload.issues,
        visitors=[],
        safety_incidents="Reported" if payload.safety_incidents else None,
        notes=payload.notes,
        status="draft",
    )

    db.add(report)
    db.commit()
    db.refresh(report)
    return {"status": "created", "report_id": report.id, "message": "Draft field report created"}
```

### POST /mobile/photo/quick
```python
@router.post("/photo/quick", status_code=201)
async def mobile_quick_photo(
    background_tasks: BackgroundTasks,
    project_id: str = Form(...),
    user_id: str = Form(...),
    file: UploadFile = File(...),
    location_tag: str | None = Form(None),
    linked_entity_type: str | None = Form(None),
    linked_entity_id: UUID | None = Form(None),
    notes: str | None = Form(None),
    db: Session = Depends(get_db),
):
    # Delegate to shared photo upload service
    # Triggers Photo Intelligence pipeline WF-PHOTO-001
    # Do not duplicate storage logic
    # Reuse MinIO/photo service
    ...
```

**Implementation requirement:**
- do not duplicate storage logic
- reuse MinIO/photo service
- trigger WF-PHOTO-001

### POST /mobile/punch/quick
```python
@router.post("/punch/quick", status_code=201)
def mobile_quick_punch(
    payload: MobilePunchQuick,
    db: Session = Depends(get_db),
):
    punch = PunchItem(
        project_id=payload.project_id,
        location_description=payload.location_description,
        description=payload.description,
        trade=payload.trade,
        assigned_to_vendor=payload.assigned_to_vendor,
        priority=payload.priority,
        linked_photo_ids=[str(id) for id in payload.linked_photo_ids],
        created_by=payload.user_id,
        status="open",
    )
    db.add(punch)
    try:
        db.commit()
        db.refresh(punch)
        return {"status": "created", "punch_id": punch.id, "message": "Punch item created"}
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Mobile punch creation failed: {str(exc)}")
```

### POST /mobile/rfi/quick
```python
@router.post("/rfi/quick", status_code=201)
def mobile_quick_rfi(
    payload: MobileRFIQuick,
    db: Session = Depends(get_db),
):
    generated_number = generate_mobile_rfi_number(payload.project_id, db)
    rfi = RFI(
        project_id=payload.project_id,
        rfi_number=generated_number,
        title=payload.title or "Field Issue / RFI Candidate",
        description=payload.description,
        drawing_ref=payload.drawing_ref,
        spec_ref=payload.spec_ref,
        submitted_by=payload.user_id,
        submitted_to="PM Review",
        status="open",
    )
    db.add(rfi)
    try:
        db.commit()
        db.refresh(rfi)
        return {"status": "created", "rfi_id": rfi.id, "rfi_number": generated_number}
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Mobile RFI candidate failed: {str(exc)}")
```

### POST /mobile/queue/flush
```python
@router.post("/queue/flush", response_model=MobileQueueFlushResponse)
def flush_mobile_queue(
    payload: MobileQueueFlushRequest,
    db: Session = Depends(get_db),
):
    results = []
    for item in payload.items:
        queue_record = FieldSubmissionQueue(
            submission_type=item.submission_type,
            project_id=item.project_id,
            user_id=item.user_id,
            payload=item.payload,
            client_submission_id=item.client_submission_id,
            status="pending",
        )
        db.add(queue_record)
        db.flush()

        try:
            processed = process_mobile_queue_item(item=item, queue_id=queue_record.id, db=db)
            queue_record.status = "submitted"
            queue_record.submitted_at = datetime.now(timezone.utc)
            queue_record.processed_entity_type = processed.get("entity_type")
            queue_record.processed_entity_id = processed.get("entity_id")
            results.append({
                "client_submission_id": item.client_submission_id,
                "queue_id": queue_record.id,
                "status": "submitted",
                "processed_entity_type": processed.get("entity_type"),
                "processed_entity_id": processed.get("entity_id"),
                "error_message": None,
            })
        except Exception as exc:
            queue_record.status = "failed"
            results.append({
                "client_submission_id": item.client_submission_id,
                "queue_id": queue_record.id,
                "status": "failed",
                "error_message": str(exc),
            })

    db.commit()

    submitted = sum(1 for r in results if r["status"] == "submitted")
    failed = sum(1 for r in results if r["status"] == "failed")

    return MobileQueueFlushResponse(
        submitted=submitted,
        failed=failed,
        results=results,
    )
```

---

## 7) Mission Control — Pending Mobile Submissions Alert

**Query:**
```sql
SELECT project_id, COUNT(*)
FROM field_submissions_queue
WHERE status IN ('pending', 'failed')
GROUP BY project_id;
```

**If pending/failed > threshold:**
- Notify PM
- Show Mission Control alert
- Alert Superintendent only if failed submissions belong to them

---

## 8) n8n Workflows

### WF-MOBILE-001 Queue Staleness Monitor
**Schedule:** Every 15 minutes

**Logic:**
- Find queue items with status = pending older than 30 minutes
- Alert PM
- Log for retry

### WF-MOBILE-002 Voice Note Review Queue
**Schedule:** Daily 06:30

**Logic:**
- Find voice notes with `pending_review = true`
- Surface to PM for action
- PM reviews: discard / promote to punch / promote to RFI / add to daily report notes

---

## 9) Mobile Authentication

**MVP:** Bearer token or existing superintendent user credentials.

Field workers should not have a complex login.

**Recommended Flow:**
1. HCI issues superintendent a numeric PIN or magic link
2. Device stores auth_token locally
3. No password re-entry on jobsite

**Phase 2:**
- Biometric auth (Face ID / fingerprint)
- Project QR code for first-time pairing

---

## 10) Mobile UX Rules

### One-Hand Interface

Top actions only:
```
Daily Report
Photo
Punch
Field Issue
Voice Note
```

No dropdowns with 50 options. No nested menus. No form validation that blocks submission.

### Never Block Submission

If data is incomplete, submit as draft and surface flag.

Do not show validation errors in the field. Save everything. Let PM clean up.

### Photo First

Assume the superintendent will take a photo.

Default camera open on photo action.

Location tag auto-populated if GPS available.

### Voice as Primary Input

All text fields should support voice input via device native voice-to-text.

Do not require keyboard for notes.

---

## 11) Tests Required

Claude Code should implement tests for:
1. Quick field report creates draft record
2. Quick field report updates existing draft (idempotency)
3. Quick field report blocked if existing is approved
4. Photo quick upload stores record and triggers WF-PHOTO-001
5. Punch quick creates open punch item
6. RFI quick creates draft RFI submitted to PM Review
7. Queue flush processes multiple items in one call
8. Queue flush marks failed items with error message
9. Queue items with unknown submission_type return error
10. Mission Control surfaces pending queue items

---

## 12) Definition of Done

Mobile Field UX Phase 1 is complete when:
- [ ] `field_submissions_queue` table exists
- [ ] Superintendents can submit quick daily report drafts
- [ ] Superintendents can upload photos through mobile quick endpoint
- [ ] Superintendents can create punch items from mobile
- [ ] Superintendents can create RFI/field issue candidates from mobile
- [ ] Offline queue flush is implemented
- [ ] Failed queue items are preserved
- [ ] Mission Control shows pending/failed mobile submissions
- [ ] Voice transcripts are stored as field evidence, not final governed records
- [ ] Tests pass

---

## GBT Chief Architect Assessment

> "This gives HCI a field interface that matches the reality of construction work: fast, mobile, voice-friendly, photo-first, and resilient when the jobsite has poor signal."

---

*Spec committed by Browser Claude — Operations Intelligence*
*GBT Cycle 24 complete — Sprint 6 Priority 4 spec delivered*

# CYCLE 15 - GBT DAILY FIELD INTELLIGENCE ARCHITECTURE
**Date:** 2026-07-01
**Cycle:** 15
**Priority:** Sprint 5 #2
**Status:** SPEC COMPLETE - Awaiting Claude Code implementation
**Author:** HCI Chief Architect (GBT) via BC Operations Intelligence

---

## Overview

Daily Field Reports are the field record of truth. They connect the Superintendent's daily observations to: Project Brain, Mission Control, Weather Intelligence, CPM Schedule Intelligence, Cost Forecasting, RFI/Submittal Management, Safety and Quality tracking, Executive Morning Brief.

**Goal:** Every workday leaves behind a complete, structured field record that feeds schedule, risk, weather, safety, quality, and executive reporting without forcing Superintendents to become software operators.

---

## 1. PostgreSQL DDL - daily_field_reports Table

```sql
CREATE TABLE IF NOT EXISTS daily_field_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id TEXT NOT NULL,
    report_date DATE NOT NULL,
    superintendent_id TEXT NOT NULL,

    -- Weather (auto-populated from weather_alerts on create)
    weather_summary TEXT,
    weather_condition TEXT,
    temperature_high NUMERIC(6, 2),
    temperature_low NUMERIC(6, 2),

    -- Crew
    crew_count INTEGER NOT NULL DEFAULT 0,
    crew_by_trade JSONB NOT NULL DEFAULT '[]'::jsonb,
    -- Example: [{"trade": "Electrical", "count": 4, "company": "Smith Electric"}]

    -- Activities
    activities_performed JSONB NOT NULL DEFAULT '[]'::jsonb,
    -- Example: [{"activity_id": "A120", "description": "Installed main level wall framing", "percent_complete": 65}]

    -- Materials
    materials_delivered JSONB NOT NULL DEFAULT '[]'::jsonb,
    -- Example: [{"item": "LVL beams", "quantity": "12", "supplier": "Pacific Lumber"}]

    issues TEXT,

    visitors JSONB NOT NULL DEFAULT '[]'::jsonb,
    -- Example: [{"name": "John Smith", "company": "Engineer Co.", "purpose": "Site inspection"}]

    safety_incidents TEXT,
    notes TEXT,

    status TEXT NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'submitted', 'approved')),
    submitted_at TIMESTAMPTZ,
    approved_by TEXT,
    approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_daily_field_project_date UNIQUE (project_id, report_date),
    CONSTRAINT chk_daily_field_status CHECK (status IN ('draft','submitted','approved')),
    CONSTRAINT chk_daily_field_crew_count CHECK (crew_count >= 0)
);

CREATE INDEX IF NOT EXISTS idx_daily_field_project_id
    ON daily_field_reports(project_id);

CREATE INDEX IF NOT EXISTS idx_daily_field_report_date
    ON daily_field_reports(report_date DESC);

CREATE INDEX IF NOT EXISTS idx_daily_field_project_date
    ON daily_field_reports(project_id, report_date DESC);
```

---

## 2. Business Rules

**Rule 1 - One Report Per Project Per Date:**
- UNIQUE constraint: (project_id, report_date)
- If Superintendent submits a second report for same day: return 409 Conflict
- Instruct them to update the existing draft/report

**Rule 2 - Weather Auto-Populated:**
- When report is created, system auto-populates weather fields from Weather Intelligence
- Source priority: 1. weather_alerts for project/date, 2. Weather API current/daily forecast, 3. empty values (manual entry)
- Fields auto-populated: weather_summary, weather_condition, temperature_high, temperature_low
- Weather should remain editable before submission (Superintendent corrects if needed)

**Rule 3 - Submit by 6 PM:**
- Superintendent must submit DFR before 18:00 local project time
- If not submitted by 6 PM: create Mission Control alert, notify PM/Superintendent, mark report as overdue in daily dashboard
- This should be a scheduled n8n check: WF-FIELD-001 Daily Field Report Deadline Check

**Rule 4 - PM Approves:**
- Submitted report is not final until PM approval
- PM approval confirms: field conditions adequately documented, schedule updates reasonable, safety issues acknowledged, cost/schedule impacts flagged, required RFIs or tasks created

**Rule 5 - Submitted Reports Locked:**
- Once submitted, report cannot be edited without PM un-submitting it
- Once approved, report is fully locked

**Rule 6 - Safety Incidents Escalate:**
- If safety_incidents is non-empty: Mission Control alert created, PM and Buck notified depending on severity, report cannot be auto-approved

**Rule 7 - Issues Create Follow-Up Items:**
- If issues is non-empty: GBT or PM review determines whether to create: RFI, task, risk, weather delay record, schedule variance note, or change exposure

---

## 3. FastAPI Endpoints

### Route Architecture Note
GET /field-reports/{project_id} and GET /field-reports/{id} conflict. GBT recommendation:
- GET /field-reports/project/{project_id} - list by project
- GET /field-reports/id/{report_id} - get single report
- This avoids routing ambiguity between UUID and project_id text

### 3.1 POST /field-reports
Creates a draft report with weather auto-populated.

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.daily_field_reports import DailyFieldReport
from app.schemas.daily_field_reports import (
    DailyFieldReportCreate, DailyFieldReportOut, DailyFieldReportApproveRequest
)
from app.services.daily_field_report_service import (
    calculate_crew_count, build_weather_summary
)

router = APIRouter(prefix='/field-reports', tags=['Daily Field Intelligence'])

@router.post('', response_model=DailyFieldReportOut, status_code=201)
def create_daily_field_report(
    payload: DailyFieldReportCreate,
    db: Session = Depends(get_db),
):
    try:
        weather = build_weather_summary(
            project_id=payload.project_id,
            report_date=payload.report_date,
            db=db,
        )
        crew_by_trade = [item.model_dump() for item in payload.crew_by_trade]
        activities = [item.model_dump() for item in payload.activities_performed]
        materials = [item.model_dump() for item in payload.materials_delivered]
        visitors = [item.model_dump() for item in payload.visitors]
        report = DailyFieldReport(
            project_id=payload.project_id,
            report_date=payload.report_date,
            superintendent_id=payload.superintendent_id,
            weather_summary=weather.get('weather_summary') or payload.weather_summary,
            weather_condition=payload.weather_condition or weather.get('weather_condition'),
            temperature_high=payload.temperature_high or weather.get('temperature_high'),
            temperature_low=payload.temperature_low or weather.get('temperature_low'),
            crew_count=calculate_crew_count(crew_by_trade),
            crew_by_trade=crew_by_trade,
            activities_performed=activities,
            materials_delivered=materials,
            issues=payload.issues,
            visitors=visitors,
            safety_incidents=payload.safety_incidents,
            notes=payload.notes,
            status='draft',
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409,
            detail='Daily field report already exists for this project and date')
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500,
            detail=f'Failed to create field report: {str(exc)}')
```

### 3.2 GET /field-reports/project/{project_id}

```python
@router.get('/project/{project_id}', response_model=list[DailyFieldReportOut])
def list_project_field_reports(
    project_id: str,
    status: str | None = None,
    limit: int = 30,
    db: Session = Depends(get_db),
):
    valid_statuses = {'draft', 'submitted', 'approved'}
    query = db.query(DailyFieldReport).filter(
        DailyFieldReport.project_id == project_id
    )
    if status:
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail='Invalid status filter')
        query = query.filter(DailyFieldReport.status == status)
    return (
        query
        .order_by(DailyFieldReport.report_date.desc())
        .limit(limit)
        .all()
    )
```

### 3.3 GET /field-reports/id/{report_id}

```python
@router.get('/id/{report_id}', response_model=DailyFieldReportOut)
def get_field_report(report_id: UUID, db: Session = Depends(get_db)):
    report = db.query(DailyFieldReport).filter(
        DailyFieldReport.id == report_id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail='Daily field report not found')
    return report
```

### 3.4 PATCH /field-reports/{id}/submit

```python
@router.patch('/{report_id}/submit', response_model=DailyFieldReportOut)
def submit_field_report(report_id: UUID, db: Session = Depends(get_db)):
    report = db.query(DailyFieldReport).filter(
        DailyFieldReport.id == report_id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail='Daily field report not found')
    if report.status != 'draft':
        raise HTTPException(status_code=400,
            detail='Only draft reports can be submitted')
    report.status = 'submitted'
    report.submitted_at = datetime.now(timezone.utc)
    try:
        db.commit()
        db.refresh(report)
        # Phase 2: create Mission Control event
        # Phase 2: create safety alert if safety_incidents non-empty
        # Phase 2: update CPM activity percent completion from activities_performed
        return report
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500,
            detail=f'Failed to submit field report: {str(exc)}')
```

### 3.5 PATCH /field-reports/{id}/approve

```python
@router.patch('/{report_id}/approve', response_model=DailyFieldReportOut)
def approve_field_report(
    report_id: UUID,
    payload: DailyFieldReportApproveRequest,
    db: Session = Depends(get_db),
):
    report = db.query(DailyFieldReport).filter(
        DailyFieldReport.id == report_id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail='Daily field report not found')
    if report.status != 'submitted':
        raise HTTPException(status_code=400,
            detail='Only submitted reports can be approved')
    report.status = 'approved'
    report.approved_by = payload.approved_by
    report.approved_at = datetime.now(timezone.utc)
    try:
        db.commit()
        db.refresh(report)
        # Phase 2: update Project Brain daily log
        # Phase 2: push approved progress into schedule intelligence
        # Phase 2: update morning brief rollup
        return report
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500,
            detail=f'Failed to approve field report: {str(exc)}')
```

---

## 4. Service Logic

**File:** `app/services/daily_field_report_service.py`

```python
def calculate_crew_count(crew_by_trade: list[dict]) -> int:
    return sum(int(item.get('count', 0)) for item in crew_by_trade)

def build_weather_summary(project_id: str, report_date, db) -> dict:
    # Source priority:
    # 1. weather_alerts for project/date
    # 2. latest weather current/forecast service
    # 3. empty values
    alerts = get_weather_alerts_for_date(project_id, report_date, db)
    if alerts:
        highest = max(alerts, key=lambda a: severity_rank(a))
        return {
            'weather_summary': f'{len(alerts)} weather alert(s) active',
            'weather_condition': highest.alert_type,
            'temperature_high': highest.condition_value,
            'temperature_low': None,
        }
    current = get_cached_or_live_weather(project_id, db)
    if current:
        return {
            'weather_summary': 'Weather auto-populated from OpenWeatherMap',
            'weather_condition': current.get('condition'),
            'temperature_high': current.get('temperature_high'),
            'temperature_low': current.get('temperature_low'),
        }
    return {'weather_summary': None, 'weather_condition': None,
            'temperature_high': None, 'temperature_low': None}
```

---

## 5. n8n Workflow - WF-FIELD-001 Daily Deadline Monitor

**Workflow Name:** WF-FIELD-001 Daily Field Report Deadline Check
**Trigger:** Daily at 18:00 local project time

**Logic:**
1. Query active projects
2. For each project: check if daily_field_reports exists for today with status != draft
3. If no report or status = draft: create alert
4. Notify: Superintendent, PM, Mission Control dashboard alert

---

## 6. CPM Activity Percent Completion Integration

When a DFR is approved and activities_performed contains percent_complete values:
```json
{"activity_id": "A120", "percent_complete": 75}
```
- Phase 2 should update or recommend update to cpm_activities
- Do NOT auto-mark complete unless PM approves
- If percent_complete advances, show progress in Mission Control
- If no progress on scheduled critical activity, flag schedule risk

---

## 7. Tests Required

Claude Code should add tests for:
1. Create daily field report
2. Duplicate project/date returns 409
3. Weather auto-populates from weather alerts
4. Crew count sums from crew_by_trade
5. List reports by project
6. Get report by ID
7. Submit draft report
8. Cannot submit already-submitted report
9. Approve submitted report
10. Reject approve when report is still draft
11. Safety incident report creates escalation hook or flag
12. Invalid status filter returns 400

---

## 8. Definition of Done

Daily Field Intelligence Phase 1 is complete when:
- [ ] daily_field_reports table exists
- [ ] One report per project/date is enforced
- [ ] Weather fields auto-populate from Weather Intelligence when available
- [ ] Superintendent can create draft and submit
- [ ] PM can approve submitted report
- [ ] Reports are queryable by project and ID
- [ ] Mission Control can display report status and missed-report alerts
- [ ] WF-FIELD-001 n8n deadline monitor is specified or implemented
- [ ] Tests pass (12 test cases)

---
*Generated by HCI Chief Architect (GBT) Cycle 15 | Captured by BC Operations Intelligence | 2026-07-01*

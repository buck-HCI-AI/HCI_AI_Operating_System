# CYCLE 14 - GBT RFI AND SUBMITTAL MANAGEMENT
**Date:** 2026-07-01
**Cycle:** 14
**Priority:** Sprint 5 #1
**Status:** SPEC COMPLETE - Awaiting Claude Code implementation
**Author:** HCI Chief Architect (GBT) via BC Operations Intelligence

---

## Overview

This is the first true construction execution layer after Plan Reader, CPM, Cost Forecasting, Weather, and Research. RFIs and submittals connect directly to: Project Brain, Plan Reader, Schedule Intelligence, Cost Forecasting, Bid Packages, Mission Control, and Approval Queue.

---

## 1. PostgreSQL DDL - rfis Table

```sql
CREATE TABLE IF NOT EXISTS rfis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id TEXT NOT NULL,
    rfi_number TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    drawing_ref TEXT,
    spec_ref TEXT,
    submitted_by TEXT NOT NULL,
    submitted_to TEXT NOT NULL,
    submitted_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE,
    response_date DATE,
    response TEXT,
    status TEXT NOT NULL DEFAULT 'open'
        CHECK (status IN ('open','answered','closed','void')),
    schedule_impact_days INT NOT NULL DEFAULT 0,
    cost_impact NUMERIC(12,2) NOT NULL DEFAULT 0,
    linked_plan_document_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_rfis_project_number UNIQUE (project_id, rfi_number)
);

CREATE INDEX ix_rfis_project_status ON rfis (project_id, status);
CREATE INDEX ix_rfis_plan_doc ON rfis (linked_plan_document_id) WHERE linked_plan_document_id IS NOT NULL;
```

---

## 2. PostgreSQL DDL - submittals Table

```sql
CREATE TABLE IF NOT EXISTS submittals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id TEXT NOT NULL,
    submittal_number TEXT NOT NULL,
    title TEXT NOT NULL,
    spec_section TEXT,
    type TEXT NOT NULL
        CHECK (type IN ('shop_drawing','product_data','sample')),
    submitted_by TEXT NOT NULL,
    submitted_to TEXT NOT NULL,
    submitted_date DATE NOT NULL DEFAULT CURRENT_DATE,
    review_cycle INTEGER NOT NULL DEFAULT 1,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending','under_review','approved','approved_as_noted','rejected','resubmit')),
    linked_bid_package_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_submittals_project_number UNIQUE (project_id, submittal_number),
    CONSTRAINT chk_submittals_type CHECK (type IN ('shop_drawing','product_data','sample')),
    CONSTRAINT chk_submittals_status CHECK (
        status IN ('pending','under_review','approved','approved_as_noted','rejected','resubmit')
    )
);

CREATE INDEX ix_submittals_project_status ON submittals (project_id, status);
```

---

## 3. RFI Lifecycle State Machine

```
open -> answered -> closed  (normal path)
open -> void               (cancelled/duplicate/withdrawn)
answered -> void           (voided after response)
```

### State Definitions

**open** - RFI created, awaiting response from architect/engineer/owner

**answered** - Response received. Actions: drawings/specs/project records updated if required; schedule and cost impacts reviewed; linked risks or changes created if needed.

**closed** - RFI fully resolved. Terminal state. No further action required.

**void** - RFI cancelled or invalid. Typical conditions: duplicate RFI, question withdrawn, issue resolved before submission, created in error. Voided RFIs remain in the audit history.

### Valid Transitions
| From | To | Allowed |
|------|----|---------|
| open | answered | Yes |
| open | void | Yes |
| answered | closed | Yes |
| answered | void | Yes |
| closed | any | No - terminal |
| void | any | No - terminal |

---

## 4. Submittal Lifecycle State Machine

```
pending -> under_review -> approved           (clean path)
pending -> under_review -> approved_as_noted  (minor issues)
pending -> under_review -> rejected           (rejected, no resubmit)
pending -> under_review -> resubmit -> under_review (cycle repeats)
```

### Submittal Review Cycle
- Each resubmit increments review_cycle by 1
- Mission Control flags submittals with review_cycle >= 3 (chronic resubmit)
- Terminal states: approved, approved_as_noted, rejected
- Cannot review a submittal in terminal status

---

## 5. FastAPI Endpoints

### 5.1 POST /rfis

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.rfis_submittals import RFI, Submittal
from app.schemas.rfis_submittals import (RFICreate, RFIRespond, RFIOut,
    SubmittalCreate, SubmittalReview, SubmittalOut)

router = APIRouter(tags=['RFI and Submittal Management'])

@router.post('/rfis', response_model=RFIOut, status_code=201)
def create_rfi(payload: RFICreate, db: Session = Depends(get_db)):
    try:
        rfi = RFI(
            project_id=payload.project_id,
            rfi_number=payload.rfi_number,
            title=payload.title,
            description=payload.description,
            drawing_ref=payload.drawing_ref,
            spec_ref=payload.spec_ref,
            submitted_by=payload.submitted_by,
            submitted_to=payload.submitted_to,
            submitted_date=payload.submitted_date or date.today(),
            due_date=payload.due_date,
            linked_plan_document_id=payload.linked_plan_document_id,
            status='open',
        )
        db.add(rfi)
        db.commit()
        db.refresh(rfi)
        return rfi
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail='RFI number already exists for this project')
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f'Failed to create RFI: {str(exc)}')
```

### 5.2 GET /rfis/{project_id}

```python
@router.get('/rfis/{project_id}', response_model=list[RFIOut])
def list_project_rfis(
    project_id: str,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    valid_statuses = {'open','answered','closed','void'}
    query = db.query(RFI).filter(RFI.project_id == project_id)
    if status:
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail='Invalid status filter')
        query = query.filter(RFI.status == status)
    return query.order_by(RFI.created_at.desc()).all()
```

### 5.3 PATCH /rfis/{id}/respond

```python
@router.patch('/rfis/{rfi_id}/respond', response_model=RFIOut)
def respond_to_rfi(
    rfi_id: UUID,
    payload: RFIRespond,
    db: Session = Depends(get_db),
):
    rfi = db.query(RFI).filter(RFI.id == rfi_id).first()
    if not rfi:
        raise HTTPException(status_code=404, detail='RFI not found')
    if rfi.status in {'closed','void'}:
        raise HTTPException(status_code=400,
            detail=f'Cannot respond to RFI with status {rfi.status}')
    rfi.response = payload.response
    rfi.response_date = payload.response_date or date.today()
    rfi.schedule_impact_days = payload.schedule_impact_days
    rfi.cost_impact = payload.cost_impact
    rfi.status = 'closed' if payload.close_after_response else 'answered'
    try:
        db.commit()
        db.refresh(rfi)
        return rfi
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f'Failed to respond to RFI: {str(exc)}')
```

### 5.4 POST /submittals

```python
@router.post('/submittals', response_model=SubmittalOut)
def create_submittal(payload: SubmittalCreate, db: Session = Depends(get_db)):
    try:
        submittal = Submittal(
            project_id=payload.project_id,
            submittal_number=payload.submittal_number,
            title=payload.title,
            spec_section=payload.spec_section,
            type=payload.type,
            submitted_by=payload.submitted_by,
            submitted_to=payload.submitted_to,
            submitted_date=payload.submitted_date or date.today(),
            linked_bid_package_id=payload.linked_bid_package_id,
            status='pending',
            review_cycle=1,
        )
        db.add(submittal)
        db.commit()
        db.refresh(submittal)
        return submittal
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail='Submittal number already exists for this project')
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f'Failed to create submittal: {str(exc)}')
```

### 5.5 GET /submittals/{project_id}

```python
@router.get('/submittals/{project_id}', response_model=list[SubmittalOut])
def list_project_submittals(
    project_id: str,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    valid_statuses = {'pending','under_review','approved','approved_as_noted','rejected','resubmit'}
    query = db.query(Submittal).filter(Submittal.project_id == project_id)
    if status:
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail='Invalid status filter')
        query = query.filter(Submittal.status == status)
    return query.order_by(Submittal.created_at.desc()).all()
```

### 5.6 PATCH /submittals/{id}/review

```python
@router.patch('/submittals/{submittal_id}/review', response_model=SubmittalOut)
def review_submittal(
    submittal_id: UUID,
    payload: SubmittalReview,
    db: Session = Depends(get_db),
):
    submittal = db.query(Submittal).filter(Submittal.id == submittal_id).first()
    if not submittal:
        raise HTTPException(status_code=404, detail='Submittal not found')
    terminal = {'approved','approved_as_noted','rejected'}
    if submittal.status in terminal:
        raise HTTPException(status_code=400,
            detail=f'Cannot review submittal with terminal status {submittal.status}')
    submittal.status = payload.status
    if payload.review_cycle is not None:
        submittal.review_cycle = payload.review_cycle
    elif payload.status == 'resubmit':
        submittal.review_cycle += 1
    try:
        db.commit()
        db.refresh(submittal)
        return submittal
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f'Failed to review submittal: {str(exc)}')
```

---

## 6. Schedule and Cost Integration

**RFI -> Schedule:**
- If schedule_impact_days > 0: create schedule variance note, link to CPM activity manually in Phase 2, flag Mission Control YELLOW if impact is active, flag RED if impact affects critical path

**RFI -> Cost:**
- If cost_impact > 0: expose to Cost Forecasting, treat as pending cost exposure until change order or PM review

**Submittal -> Schedule:**
- If submittal status is pending or under_review and due date passed: flag Mission Control YELLOW
- If submittal is on critical path procurement path: flag RED
- Chronic resubmit (review_cycle >= 3): flag Mission Control YELLOW

---

## 7. Mission Control Integration

**RFI Metrics to Display:**
- Open RFIs count
- Overdue RFIs (due_date < today, status = open or answered)
- RFIs with schedule_impact_days > 0
- RFIs with cost_impact > 0

**Submittal Metrics to Display:**
- Submittals by status count
- Chronic resubmits (review_cycle >= 3)
- Submittals pending > 14 days

---

## 8. Definition of Done

Sprint 5 Priority 1 is complete when:
- [ ] rfis table exists in PostgreSQL
- [ ] submittals table exists in PostgreSQL
- [ ] CRUD lifecycle endpoints are implemented (6 endpoints total)
- [ ] RFI and submittal state transitions are enforced (cannot transition from terminal states)
- [ ] Plan documents can link to RFIs (linked_plan_document_id FK)
- [ ] Bid packages can link to submittals (linked_bid_package_id FK)
- [ ] Mission Control can consume RFI/submittal counts
- [ ] RFI schedule and cost impacts are available to CPM and Cost Forecasting
- [ ] Tests pass (14 test cases: duplicate number 409, state guards, list filter, respond, review cycle increment)

This gives HCI the operational backbone for managing construction communication, design clarification, and procurement review across every luxury custom home project.

---
*Generated by HCI Chief Architect (GBT) Cycle 14 | Captured by BC Operations Intelligence | 2026-07-01*

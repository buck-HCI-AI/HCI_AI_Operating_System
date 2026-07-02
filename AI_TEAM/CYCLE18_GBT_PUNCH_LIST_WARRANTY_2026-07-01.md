# CYCLE 18 — Sprint 5 Priority 5: Punch List & Warranty Management
**GBT Cycle:** 18 | **Date:** 2026-07-01 | **Status:** SPEC COMPLETE
**Sprint:** 5 | **Priority:** 5 of 6 | **Depends on:** Cycles 14 (RFI), 15 (Daily Field), 17 (Photos)

---

## Architecture Overview

Punch List and Warranty Management closes the construction lifecycle.
This layer connects: field photos, daily reports, subcontractor accountability, client turnover, warranty obligations, closeout readiness.
Goal: every deficiency is owned, tracked, inspected, and resolved before client handover.

---

## 1) PostgreSQL DDL

### punch_items

```sql
CREATE TABLE IF NOT EXISTS punch_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id TEXT NOT NULL,
    unit_number TEXT,
    location_description TEXT NOT NULL,
    trade TEXT,
    assigned_to_user_id TEXT,
    assigned_to_vendor TEXT,
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open',
    -- allowed: open, in_progress, ready_for_inspection, closed, voided
    priority TEXT NOT NULL DEFAULT 'medium',
    -- allowed: critical, high, medium, low
    due_date DATE,
    completed_date DATE,
    inspected_by TEXT,
    inspection_notes TEXT,
    linked_photo_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_by TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_punch_status CHECK (status IN ('open','in_progress','ready_for_inspection','closed','voided')),
    CONSTRAINT chk_punch_priority CHECK (priority IN ('critical','high','medium','low'))
);

CREATE INDEX IF NOT EXISTS idx_punch_items_project_id ON punch_items(project_id);
CREATE INDEX IF NOT EXISTS idx_punch_items_status ON punch_items(status);
CREATE INDEX IF NOT EXISTS idx_punch_items_priority ON punch_items(priority);
CREATE INDEX IF NOT EXISTS idx_punch_items_assigned_vendor ON punch_items(assigned_to_vendor);
CREATE INDEX IF NOT EXISTS idx_punch_items_due_date ON punch_items(due_date);
```

### warranty_items

```sql
CREATE TABLE IF NOT EXISTS warranty_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id TEXT NOT NULL,
    unit_number TEXT,
    trade TEXT,
    vendor_name TEXT,
    description TEXT NOT NULL,
    warranty_start DATE NOT NULL,
    warranty_end DATE NOT NULL,
    warranty_type TEXT NOT NULL,
    -- allowed: workmanship, material, equipment, structural
    status TEXT NOT NULL DEFAULT 'active',
    -- allowed: active, expiring_soon, expired, claimed
    linked_punch_item_id UUID,
    documents JSONB NOT NULL DEFAULT '[]'::jsonb,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_warranty_type CHECK (warranty_type IN ('workmanship','material','equipment','structural')),
    CONSTRAINT chk_warranty_status CHECK (status IN ('active','expiring_soon','expired','claimed')),
    CONSTRAINT chk_warranty_dates CHECK (warranty_end >= warranty_start),
    CONSTRAINT fk_warranty_punch_item FOREIGN KEY (linked_punch_item_id)
        REFERENCES punch_items(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_warranty_items_project_id ON warranty_items(project_id);
CREATE INDEX IF NOT EXISTS idx_warranty_items_status ON warranty_items(status);
CREATE INDEX IF NOT EXISTS idx_warranty_items_warranty_end ON warranty_items(warranty_end ASC);
CREATE INDEX IF NOT EXISTS idx_warranty_items_vendor ON warranty_items(vendor_name);
```

### closeout_checklists (Future — Phase 2)

```sql
CREATE TABLE closeout_checklists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id TEXT NOT NULL,
    checklist_type TEXT NOT NULL DEFAULT 'pre_close',
    status TEXT NOT NULL DEFAULT 'open',
    items JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

Phase 1: calculate closeout readiness dynamically from punch/warranty records.

---

## 2) Business Rules

**Rule 1 — Punch Item Lifecycle:**
open -> in_progress -> ready_for_inspection -> closed (or voided at any non-terminal state)
State machine enforced in service layer. Invalid transitions raise ValueError -> 400.

**Punch Item State Definitions:**
- `open`: deficiency recorded and assigned. Photos attached, trade/vendor assigned, due date set.
- `in_progress`: responsible party has begun corrective work.
- `ready_for_inspection`: assigned party reports complete, awaiting PM/Superintendent verification.
- `closed`: PM, Superintendent, or authorized inspector has accepted the work.
- `voided`: item was created in error or is no longer applicable.

**Rule 2 — Warranty Auto-Status:**
Calculated dynamically from warranty_end date:
- `active`: warranty_end > today + 30 days
- `expiring_soon`: warranty_end <= today + 30 days AND warranty_end >= today
- `expired`: warranty_end < today
- `claimed`: set explicitly when warranty claim is filed (never auto-calculated)

**Rule 3 — Critical Punch Priority:**
`critical` punch items: immediate escalation. Mission Control alert. Cannot be set to in_progress without assigned_to_vendor or assigned_to_user_id.

**Rule 4 — Overdue Detection:**
Punch item is overdue when: due_date < today AND status NOT IN (closed, voided).
WF-CLOSEOUT-001 runs daily to flag overdue punch items.

**Rule 5 — Closeout Readiness Criteria (Phase 1 — dynamic calculation):**
Project is closeout-ready when:
- No critical punch items with status NOT IN (closed, voided)
- No high-priority punch items overdue
- All ready_for_inspection items reviewed
- All warranty records created for required scopes
- All linked photos reviewed
- All O&M / warranty documents uploaded
- Client turnover package complete

---

## 3) Punch Status Transition Map

```python
VALID_PUNCH_TRANSITIONS = {
    "open": {"in_progress", "voided"},
    "in_progress": {"ready_for_inspection", "voided"},
    "ready_for_inspection": {"closed", "in_progress", "voided"},
    "closed": set(),  # terminal
    "voided": set(),  # terminal
}
```

---

## 4) Pydantic Schemas (app/schemas/punch_warranty.py)

```python
from datetime import date, datetime
from typing import Any, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

class PunchItemCreate(BaseModel):
    project_id: str
    unit_number: Optional[str] = None
    location_description: str
    trade: Optional[str] = None
    assigned_to_user_id: Optional[str] = None
    assigned_to_vendor: Optional[str] = None
    description: str
    priority: str = "medium"
    due_date: Optional[date] = None
    linked_photo_ids: List[str] = Field(default_factory=list)
    created_by: str

class PunchItemOut(BaseModel):
    id: UUID
    project_id: str
    unit_number: Optional[str] = None
    location_description: str
    trade: Optional[str] = None
    assigned_to_user_id: Optional[str] = None
    assigned_to_vendor: Optional[str] = None
    description: str
    status: str
    priority: str
    due_date: Optional[date] = None
    completed_date: Optional[date] = None
    inspected_by: Optional[str] = None
    inspection_notes: Optional[str] = None
    linked_photo_ids: List[Any] = Field(default_factory=list)
    created_by: str
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class PunchStatusUpdate(BaseModel):
    status: str
    completed_date: Optional[date] = None
    inspected_by: Optional[str] = None
    inspection_notes: Optional[str] = None

class WarrantyCreate(BaseModel):
    project_id: str
    unit_number: Optional[str] = None
    trade: Optional[str] = None
    vendor_name: Optional[str] = None
    description: str
    warranty_start: date
    warranty_end: date
    warranty_type: str = Field(pattern='^(workmanship|material|equipment|structural)$')
    linked_punch_item_id: Optional[UUID] = None
    documents: List[dict[str, Any]] = Field(default_factory=list)
    notes: Optional[str] = None

class WarrantyOut(BaseModel):
    id: UUID
    project_id: str
    unit_number: Optional[str] = None
    trade: Optional[str] = None
    vendor_name: Optional[str] = None
    description: str
    warranty_start: date
    warranty_end: date
    warranty_type: str
    status: str
    linked_punch_item_id: Optional[UUID] = None
    documents: List[Any] = Field(default_factory=list)
    notes: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True
```

---

## 5) FastAPI Router (app/api/routers/punch_warranty.py)

```python
from datetime import date
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.punch_warranty import PunchItem, WarrantyItem
from app.schemas.punch_warranty import (
    PunchItemCreate, PunchStatusUpdate, PunchItemOut,
    WarrantyCreate, WarrantyOut,
)
from app.services.punch_warranty_service import (
    validate_punch_transition, calculate_warranty_status,
)

router = APIRouter(tags=["Punch List and Warranty"])


@router.post("/punch", response_model=PunchItemOut, status_code=201)
def create_punch_item(payload: PunchItemCreate, db: Session = Depends(get_db)):
    try:
        punch = PunchItem(
            project_id=payload.project_id,
            unit_number=payload.unit_number,
            location_description=payload.location_description,
            trade=payload.trade,
            assigned_to_user_id=payload.assigned_to_user_id,
            assigned_to_vendor=payload.assigned_to_vendor,
            description=payload.description,
            priority=payload.priority,
            due_date=payload.due_date,
            linked_photo_ids=[str(pid) for pid in payload.linked_photo_ids],
            created_by=payload.created_by,
        )
        db.add(punch)
        db.commit()
        db.refresh(punch)
        return punch
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create punch item: {str(exc)}")


@router.get("/punch/{project_id}", response_model=list[PunchItemOut])
def list_project_punch_items(
    project_id: str,
    status: str | None = None,
    priority: str | None = None,
    db: Session = Depends(get_db),
):
    valid_statuses = {"open","in_progress","ready_for_inspection","closed","voided"}
    valid_priorities = {"critical","high","medium","low"}
    if status and status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    if priority and priority not in valid_priorities:
        raise HTTPException(status_code=400, detail=f"Invalid priority: {priority}")
    query = db.query(PunchItem).filter(PunchItem.project_id == project_id)
    if status:
        query = query.filter(PunchItem.status == status)
    if priority:
        query = query.filter(PunchItem.priority == priority)
    return query.order_by(PunchItem.due_date.asc().nullslast(), PunchItem.created_at.desc()).all()


@router.patch("/punch/{punch_id}/status", response_model=PunchItemOut)
def update_punch_status(punch_id: UUID, payload: PunchStatusUpdate, db: Session = Depends(get_db)):
    punch = db.query(PunchItem).filter(PunchItem.id == punch_id).first()
    if not punch:
        raise HTTPException(status_code=404, detail="Punch item not found")
    try:
        validate_punch_transition(punch.status, payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if payload.status == "ready_for_inspection":
        punch.completed_date = payload.completed_date or date.today()
    punch.status = payload.status
    if payload.inspected_by:
        punch.inspected_by = payload.inspected_by
    if payload.inspection_notes:
        punch.inspection_notes = payload.inspection_notes
    try:
        db.commit()
        db.refresh(punch)
        return punch
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update punch status: {str(exc)}")


@router.post("/warranty", response_model=WarrantyOut, status_code=201)
def create_warranty_item(payload: WarrantyCreate, db: Session = Depends(get_db)):
    status = calculate_warranty_status(payload.warranty_end)
    try:
        warranty = WarrantyItem(
            project_id=payload.project_id,
            unit_number=payload.unit_number,
            trade=payload.trade,
            vendor_name=payload.vendor_name,
            description=payload.description,
            warranty_start=payload.warranty_start,
            warranty_end=payload.warranty_end,
            warranty_type=payload.warranty_type,
            status=status,
            linked_punch_item_id=payload.linked_punch_item_id,
            documents=payload.documents,
            notes=payload.notes,
        )
        db.add(warranty)
        db.commit()
        db.refresh(warranty)
        return warranty
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create warranty item: {str(exc)}")


@router.get("/warranty/{project_id}", response_model=list[WarrantyOut])
def list_project_warranties(
    project_id: str,
    status: str | None = None,
    warranty_type: str | None = None,
    db: Session = Depends(get_db),
):
    valid_statuses = {"active","expiring_soon","expired","claimed"}
    valid_types = {"workmanship","material","equipment","structural"}
    if status and status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    if warranty_type and warranty_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid warranty_type: {warranty_type}")
    query = db.query(WarrantyItem).filter(WarrantyItem.project_id == project_id)
    if status:
        query = query.filter(WarrantyItem.status == status)
    if warranty_type:
        query = query.filter(WarrantyItem.warranty_type == warranty_type)
    return query.order_by(WarrantyItem.warranty_end.asc(), WarrantyItem.created_at.desc()).all()
```

---

## 6) Endpoint Summary

| Method | Path | Description |
|--------|------|-------------|
| POST | /punch | Create punch item (status=open) |
| GET | /punch/{project_id} | List punch items (filter: status, priority) |
| PATCH | /punch/{id}/status | Advance punch lifecycle (state machine enforced) |
| POST | /warranty | Create warranty item (auto-status from dates) |
| GET | /warranty/{project_id} | List warranties (filter: status, warranty_type) |

---

## 7) Service Logic (app/services/punch_warranty_service.py)

```python
from datetime import date

VALID_PUNCH_TRANSITIONS = {
    "open": {"in_progress", "voided"},
    "in_progress": {"ready_for_inspection", "voided"},
    "ready_for_inspection": {"closed", "in_progress", "voided"},
    "closed": set(),
    "voided": set(),
}

def validate_punch_transition(current_status: str, next_status: str):
    if next_status == current_status:
        return
    allowed = VALID_PUNCH_TRANSITIONS.get(current_status, set())
    if next_status not in allowed:
        raise ValueError(f"Invalid punch transition from {current_status} to {next_status}. Allowed: {allowed}")

def calculate_warranty_status(warranty_end: date) -> str:
    today = date.today()
    days_remaining = (warranty_end - today).days
    if days_remaining < 0:
        return "expired"
    elif days_remaining <= 30:
        return "expiring_soon"
    else:
        return "active"
```

---

## 8) Mission Control Output

```json
{
  "project_id": "101F",
  "punch_summary": {
    "open": 12,
    "in_progress": 5,
    "ready_for_inspection": 3,
    "closed": 48,
    "critical_open": 0,
    "overdue": 2
  },
  "warranty_summary": {
    "active": 18,
    "expiring_soon": 3,
    "expired": 8,
    "claimed": 1
  },
  "closeout_readiness": {
    "critical_punch_open": 0,
    "high_punch_open": 2,
    "warranty_records_created": true,
    "photo_documentation_reviewed": false,
    "ready_for_owner_turnover": false
  }
}
```

---

## 9) n8n Workflows

**WF-CLOSEOUT-001 — Punch Overdue Monitor**
Trigger: Daily at 07:00 (before Supers arrive at 7:00 AM)
Action: Query punch_items WHERE due_date < today AND status NOT IN (closed, voided)
Output: Create Mission Control alert per overdue item. Notify assigned vendor/user via Telegram (when available).

**WF-WARRANTY-001 — Expiring Warranty Monitor**
Trigger: Daily at 07:00
Action: Query warranty_items WHERE warranty_end between today and today + 30 days AND status = active
Action: Update status to expiring_soon. Notify PM via Telegram.

---

## 10) Test Cases

| # | Test | Expected |
|---|------|----------|
| 1 | Create punch item | 201, status=open |
| 2 | Create punch item invalid priority | 400 |
| 3 | GET punch items for project | 200 list |
| 4 | GET punch items with status filter | Only matching status |
| 5 | GET punch items with invalid status filter | 400 |
| 6 | GET punch items with priority filter | Only matching priority |
| 7 | PATCH punch open -> in_progress | 200 |
| 8 | PATCH punch invalid transition (open -> closed) | 400 |
| 9 | PATCH punch non-existent ID | 404 |
| 10 | PATCH punch closed -> in_progress (terminal state) | 400 |
| 11 | Create warranty warranty_end >= warranty_start | 201, status auto-calculated |
| 12 | Create warranty warranty_end < warranty_start | 400 (DB constraint) |
| 13 | Create warranty with end date < today | 201, status=expired |
| 14 | Create warranty expiring within 30 days | 201, status=expiring_soon |
| 15 | List warranties by project | 200 ordered by warranty_end asc |
| 16 | Filter warranties by status | Only matching status returned |

---

## 11) Cross-System Integration

**Photo Intelligence (Cycle 17):** linked_photo_ids on punch_items references project_photos. Punch list photos use linked_entity_type="punch_item" on project_photos.

**Daily Field Intelligence (Cycle 15):** Field issues from daily_field_reports can create punch items. Phase 2: auto-create punch item from flagged field issue.

**RFI (Cycle 14):** Resolved RFIs with corrective work may create punch items to verify implementation.

**Cost Forecasting (Cycle 11):** Warranty claims and rework costs can be added as change orders and tracked through cost_forecast.

---

## 12) Router Registration

In app/main.py:
```python
from app.api.routers import punch_warranty
app.include_router(punch_warranty.router)
```

---

## Definition of Done

Punch List and Warranty Management Phase 1 complete when:
- [ ] punch_items table exists
- [ ] warranty_items table exists
- [ ] Punch lifecycle transitions enforced (state machine)
- [ ] Warranty auto-status calculated from dates
- [ ] Punch items link to project_photos
- [ ] Warranty items link to punch items
- [ ] Mission Control shows punch, warranty, and closeout readiness metrics
- [ ] WF-CLOSEOUT-001 overdue punch monitor specified
- [ ] WF-WARRANTY-001 expiring warranty monitor specified
- [ ] 16 test cases pass

---

*Spec generated by GBT Cycle 18 | BC Operations Intelligence | 2026-07-01*

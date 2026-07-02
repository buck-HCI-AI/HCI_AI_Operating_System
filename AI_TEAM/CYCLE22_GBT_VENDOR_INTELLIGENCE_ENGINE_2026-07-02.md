# CYCLE22 — Sprint 6 Priority 2: Vendor Intelligence Engine
**Cycle:** 22
**Sprint:** 6
**Priority:** 2
**Date:** 2026-07-02
**Author:** GBT (HCI Chief Architect)
**Status:** SPEC COMPLETE — Ready for Code Implementation

---

## Overview

The Vendor Intelligence Engine turns vendor performance into a measurable, compounding asset.

Instead of relying on institutional memory ("they're usually good"), HCI AI OS builds objective scorecards from actual project outcomes.

**Design Principles:**
- One canonical vendor record across all projects
- Performance is measured from operational data, not opinions
- Scores are explainable and traceable
- AI summarizes trends but does not override the underlying metrics
- Historical scores are preserved; scores are never overwritten

---

## 1) PostgreSQL DDL — vendors

```sql
CREATE TABLE IF NOT EXISTS vendors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name TEXT NOT NULL,

    trade_primary TEXT NOT NULL,
    trade_secondary TEXT,

    contact_name TEXT,
    contact_email TEXT,
    contact_phone TEXT,

    license_number TEXT,

    insurance_expiry DATE,

    notes TEXT,

    active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_vendor_name UNIQUE (name)
);

CREATE INDEX IF NOT EXISTS idx_vendors_trade
    ON vendors(trade_primary);

CREATE INDEX IF NOT EXISTS idx_vendors_active
    ON vendors(active);

CREATE INDEX IF NOT EXISTS idx_vendors_insurance
    ON vendors(insurance_expiry);
```

### Future Normalization

Eventually replace free-text vendor references in purchase_orders, punch_items, warranty_items with FK to vendors.id:

```sql
-- Phase 2 migrations
ALTER TABLE purchase_orders ADD COLUMN IF NOT EXISTS vendor_id UUID REFERENCES vendors(id);
ALTER TABLE punch_items ADD COLUMN IF NOT EXISTS vendor_id UUID REFERENCES vendors(id);
ALTER TABLE warranty_items ADD COLUMN IF NOT EXISTS vendor_id UUID REFERENCES vendors(id);
```

---

## 2) PostgreSQL DDL — vendor_performance_scores

```sql
CREATE TABLE IF NOT EXISTS vendor_performance_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    vendor_id UUID NOT NULL
        REFERENCES vendors(id)
        ON DELETE CASCADE,

    project_id TEXT NOT NULL,

    score_date DATE NOT NULL,

    bid_competitiveness NUMERIC(4,2),
    -- 1-10: how competitive bids are relative to market

    schedule_performance NUMERIC(4,2),
    -- 1-10: delivery/completion on time

    quality_score NUMERIC(4,2),
    -- 1-10: quality of work as observed

    punch_frequency INTEGER NOT NULL DEFAULT 0,
    -- count of punch items assigned to this vendor on project

    warranty_callbacks INTEGER NOT NULL DEFAULT 0,
    -- count of warranty items linked to this vendor on project

    rfi_response_time_days NUMERIC(6,2),
    -- average days to respond to RFIs

    change_order_frequency INTEGER NOT NULL DEFAULT 0,
    -- count of change orders attributable to vendor on project

    communication_score NUMERIC(4,2),
    -- 1-10: responsiveness, clarity, professionalism

    overall_score NUMERIC(5,2),
    -- computed weighted average

    notes TEXT,

    scored_by TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_vendor_scores_vendor_id
    ON vendor_performance_scores(vendor_id);

CREATE INDEX IF NOT EXISTS idx_vendor_scores_project_id
    ON vendor_performance_scores(project_id);

CREATE INDEX IF NOT EXISTS idx_vendor_scores_date
    ON vendor_performance_scores(score_date DESC);

CREATE INDEX IF NOT EXISTS idx_vendor_scores_overall
    ON vendor_performance_scores(overall_score DESC);
```

---

## 3) Overall Score Calculation

The score should be transparent rather than AI-generated.

### Weighted Formula

| Metric | Weight |
|--------|--------|
| Quality | 30% |
| Schedule | 25% |
| Communication | 15% |
| Bid Competitiveness | 15% |
| Punch Frequency (penalty) | 5% |
| Warranty Callbacks (penalty) | 5% |
| RFI Response Time | 5% |

```python
def calculate_overall_score(
    quality_score: float | None,
    schedule_performance: float | None,
    communication_score: float | None,
    bid_competitiveness: float | None,
    punch_frequency: int,
    warranty_callbacks: int,
    rfi_response_time_days: float | None,
) -> float:
    base_score = (
        (quality_score or 5.0) * 0.30 +
        (schedule_performance or 5.0) * 0.25 +
        (communication_score or 5.0) * 0.15 +
        (bid_competitiveness or 5.0) * 0.15 +
        score_from_rfi_response(rfi_response_time_days) * 0.05
    )

    # Penalty deductions
    punch_penalty = min(punch_frequency * 0.2, 2.0)  # max 2 point deduction
    warranty_penalty = min(warranty_callbacks * 0.5, 2.0)  # max 2 point deduction

    overall_score = max(1.0, min(10.0, base_score - punch_penalty - warranty_penalty))
    return round(overall_score, 2)
```

Keep individual metrics visible. Never hide them behind one score.

---

## 4) Automatic Score Inputs

### Punch Items
Source: `punch_items.assigned_to_vendor`

Metrics:
- Total punch items assigned
- Open punch items
- Average close duration
- Punch density per project

Penalty: >10 punch items/project = moderate deduction. >20 = major deduction.

### Warranty Callbacks
Source: `warranty_items.vendor_name` + `warranty_status = 'claimed'`

Metrics:
- Total claims
- Repeat failures

### Procurement (Schedule Performance)
Source: `purchase_orders` + `long_lead_materials`

Metrics:
- Acknowledged quickly
- Delivered on time
- Average delay
- Missed delivery commitments

Formula:
```
schedule_performance = 1 - (late deliveries / total deliveries)
Scaled to 1-10.
```

### RFI Response Time
Source: `rfis.submitted_to = vendor` + `rfis.response_date`

Scoring table:
| Response Time | Score |
|--------------|-------|
| 2 days | 10 |
| 5 days | 8 |
| 10 days | 6 |
| 15 days | 4 |
| >20 days | 2 |

### Change Orders
Source: `change_orders` (future table)

Measure: COs attributable to vendor / contract size. Normalize by project size.

---

## 5) Score Service

File: `app/services/vendor_score_service.py`

Responsibilities:
- Aggregate metrics
- Calculate overall score
- Produce score history
- Identify trends
- Expose rankings

```python
from decimal import Decimal
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.vendors import Vendor, VendorPerformanceScore

def score_from_rfi_response(days: float | None) -> float:
    if days is None:
        return 5.0
    if days <= 2: return 10.0
    if days <= 5: return 8.0
    if days <= 10: return 6.0
    if days <= 15: return 4.0
    return 2.0

def calculate_overall_score(
    quality_score,
    schedule_performance,
    communication_score,
    bid_competitiveness,
    punch_frequency,
    warranty_callbacks,
    rfi_response_time_days,
) -> float:
    base_score = (
        (quality_score or 5.0) * 0.30 +
        (schedule_performance or 5.0) * 0.25 +
        (communication_score or 5.0) * 0.15 +
        (bid_competitiveness or 5.0) * 0.15 +
        score_from_rfi_response(rfi_response_time_days) * 0.05
    )
    punch_penalty = min(punch_frequency * 0.2, 2.0)
    warranty_penalty = min(warranty_callbacks * 0.5, 2.0)
    return round(max(1.0, min(10.0, base_score - punch_penalty - warranty_penalty)), 2)

def get_vendor_scorecard(vendor_id: UUID, db: Session) -> dict:
    scores = (
        db.query(VendorPerformanceScore)
        .filter(VendorPerformanceScore.vendor_id == vendor_id)
        .order_by(VendorPerformanceScore.score_date.desc())
        .all()
    )
    if not scores:
        return {"vendor_id": str(vendor_id), "score_count": 0, "scores": []}

    latest = scores[0]
    trend = "stable"
    if len(scores) >= 2:
        delta = float(latest.overall_score or 0) - float(scores[-1].overall_score or 0)
        if delta > 0.5:
            trend = "improving"
        elif delta < -0.5:
            trend = "declining"

    return {
        "vendor_id": str(vendor_id),
        "latest_overall_score": float(latest.overall_score or 0),
        "trend": trend,
        "score_count": len(scores),
        "scores": scores,
    }
```

---

## 6) Pydantic Schemas

```python
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

class VendorCreate(BaseModel):
    name: str
    trade_primary: str
    trade_secondary: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    license_number: Optional[str] = None
    insurance_expiry: Optional[date] = None
    notes: Optional[str] = None

class VendorOut(BaseModel):
    id: UUID
    name: str
    trade_primary: str
    trade_secondary: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    license_number: Optional[str] = None
    insurance_expiry: Optional[date] = None
    notes: Optional[str] = None
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class VendorScoreCreate(BaseModel):
    vendor_id: UUID
    project_id: str
    score_date: date
    bid_competitiveness: Optional[Decimal] = None
    schedule_performance: Optional[Decimal] = None
    quality_score: Optional[Decimal] = None
    punch_frequency: int = 0
    warranty_callbacks: int = 0
    rfi_response_time_days: Optional[Decimal] = None
    change_order_frequency: int = 0
    communication_score: Optional[Decimal] = None
    notes: Optional[str] = None
    scored_by: Optional[str] = None

class VendorScoreOut(BaseModel):
    id: UUID
    vendor_id: UUID
    project_id: str
    score_date: date
    bid_competitiveness: Optional[Decimal] = None
    schedule_performance: Optional[Decimal] = None
    quality_score: Optional[Decimal] = None
    punch_frequency: int
    warranty_callbacks: int
    rfi_response_time_days: Optional[Decimal] = None
    change_order_frequency: int
    communication_score: Optional[Decimal] = None
    overall_score: Optional[Decimal] = None
    notes: Optional[str] = None
    scored_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class VendorScorecardOut(BaseModel):
    vendor_id: UUID
    vendor_name: str
    trade_primary: str
    latest_overall_score: Optional[float] = None
    trend: str  # improving / stable / declining
    score_count: int
    recent_scores: list[VendorScoreOut]
```

---

## 7) FastAPI Endpoints

Router: `app/api/routers/vendors.py`

```python
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.vendors import VendorCreate, VendorOut, VendorScorecardOut
from app.models.vendors import Vendor, VendorPerformanceScore
from app.services.vendor_score_service import get_vendor_scorecard, calculate_overall_score

router = APIRouter(prefix="/vendors", tags=["Vendor Intelligence"])
```

### POST /vendors
```python
@router.post("", response_model=VendorOut, status_code=201)
def create_vendor(payload: VendorCreate, db: Session = Depends(get_db)):
    existing = db.query(Vendor).filter(Vendor.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=409, detail="Vendor name already exists")
    vendor = Vendor(**payload.dict())
    db.add(vendor)
    try:
        db.commit()
        db.refresh(vendor)
        return vendor
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc))
```

### GET /vendors
Supports query params:
- `?trade=framing`
- `?active=true`
- `?min_score=8`
- `?insurance_valid=true`

```python
@router.get("", response_model=list[VendorOut])
def list_vendors(
    trade: str | None = None,
    active: bool | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Vendor)
    if trade:
        query = query.filter(Vendor.trade_primary.ilike(f"%{trade}%"))
    if active is not None:
        query = query.filter(Vendor.active == active)
    return query.order_by(Vendor.name).all()
```

### GET /vendors/{id}/scorecard
```python
@router.get("/{vendor_id}/scorecard", response_model=VendorScorecardOut)
def get_scorecard(vendor_id: UUID, db: Session = Depends(get_db)):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    scorecard = get_vendor_scorecard(vendor_id=vendor_id, db=db)
    return VendorScorecardOut(
        vendor_id=vendor.id,
        vendor_name=vendor.name,
        trade_primary=vendor.trade_primary,
        latest_overall_score=scorecard.get("latest_overall_score"),
        trend=scorecard.get("trend", "stable"),
        score_count=scorecard.get("score_count", 0),
        recent_scores=scorecard.get("scores", [])[:5],
    )
```

### GET /vendors/{id}/history
```python
@router.get("/{vendor_id}/history", response_model=list[VendorScoreOut])
def get_score_history(vendor_id: UUID, db: Session = Depends(get_db)):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return (
        db.query(VendorPerformanceScore)
        .filter(VendorPerformanceScore.vendor_id == vendor_id)
        .order_by(VendorPerformanceScore.score_date.desc())
        .all()
    )
```

---

## 8) n8n Workflow — WF-VENDOR-001

**Name:** WF-VENDOR-001 Vendor Score Update
**Runs:** Nightly

**Steps:**
1. Read active vendors
2. Aggregate punch metrics from `punch_items`
3. Aggregate warranty metrics from `warranty_items`
4. Aggregate PO delivery metrics from `purchase_orders`
5. Aggregate RFI response metrics from `rfis`
6. Compute overall score using weighted formula
7. Insert new historical score (append-only)
8. Update vendor summary cache (if any)
9. Refresh Mission Control

**Scores should be append-only for historical analysis.**

---

## 9) Mission Control Output

```json
{
  "vendor_intelligence": {
    "total_active_vendors": 47,
    "vendors_with_insurance_expiring_30_days": 3,
    "top_performers_by_trade": [
      {
        "trade": "framing",
        "vendor": "Summit Framing LLC",
        "overall_score": 9.2,
        "trend": "stable"
      },
      {
        "trade": "electrical",
        "vendor": "Peak Electric",
        "overall_score": 8.8,
        "trend": "improving"
      }
    ],
    "at_risk_vendors_on_active_projects": [
      {
        "vendor": "Valley Tile",
        "project_id": "101F",
        "overall_score": 5.1,
        "open_punch_items": 7,
        "trend": "declining",
        "risk": "HIGH"
      }
    ]
  }
}
```

---

## 10) Insurance Expiry Monitoring

n8n workflow: WF-VENDOR-002 Insurance Expiry Monitor

**Schedule:** Weekly Monday 07:00

**Logic:**
- Find vendors with `insurance_expiry <= today + 30 days`
- Notify Buck/PM via Mission Control
- Flag vendor as requiring update

---

## 11) Knowledge Graph Integration

Vendor entities participate in the Project Brain knowledge graph.

**Vendor link types for project_entity_links:**
```
vendor_completed_activity
vendor_resolved_punch
vendor_subject_of_warranty
vendor_caused_schedule_delay
vendor_caused_cost_variance
vendor_documented_by_photo
vendor_responded_to_rfi
```

**This enables traversals like:**
```
Vendor
→ Purchase Order
→ Long Lead Material
→ CPM Activity
→ Schedule Delay
→ Cost Forecast
→ Punch Item
→ Warranty Claim
```

---

## 12) Tests Required

Claude Code should implement tests for:
1. Create vendor
2. Reject duplicate vendor name (409)
3. List vendors by trade
4. Filter active vendors
5. Compute overall score from metrics
6. Verify score history is append-only
7. Scorecard returns latest score + trend
8. Insurance expiry filter returns correct vendors
9. Vendor with no scores returns empty scorecard
10. Score deductions for high punch frequency
11. Score deductions for warranty callbacks

---

## 13) Definition of Done

Vendor Intelligence Engine Phase 1 is complete when:
- [ ] `vendors` and `vendor_performance_scores` tables exist
- [ ] Existing procurement, punch, warranty, and RFI data can be associated with vendors
- [ ] Overall scores are calculated from transparent, explainable metrics
- [ ] Historical scores are retained (append-only)
- [ ] `/vendors`, `/vendors/{id}/scorecard`, and `/vendors/{id}/history` endpoints are implemented
- [ ] Nightly score aggregation workflow is defined
- [ ] Mission Control surfaces top-performing vendors and active project risks
- [ ] Vendor entities participate in the Project Brain knowledge graph
- [ ] Tests pass

---

## GBT Chief Architect Assessment

> "Once this is in place, every completed project improves future vendor selection, making procurement decisions progressively more data-driven across HCI's portfolio."

---

*Spec committed by Browser Claude — Operations Intelligence*
*GBT Cycle 22 complete — Sprint 6 Priority 2 spec delivered*

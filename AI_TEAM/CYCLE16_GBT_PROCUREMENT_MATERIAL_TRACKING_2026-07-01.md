# CYCLE 16 — Sprint 5 Priority 3: Procurement & Material Tracking
**GBT Cycle:** 16 | **Date:** 2026-07-01 | **Status:** SPEC COMPLETE
**Sprint:** 5 | **Priority:** 3 of 6 | **Depends on:** Cycles 4 (bid packages), 9 (CPM), 11 (cost forecast)

---

## Architecture Overview

Procurement Intelligence connects estimating, buyout, cost forecasting, CPM scheduling, and field execution.

Buyout chain: Bid Package Awarded -> PO Issued -> Vendor Acknowledged -> Long-Lead Ordered -> Material Delivered -> Installed / Activity Complete

---

## 1) PostgreSQL DDL

### purchase_orders

```sql
CREATE TABLE IF NOT EXISTS purchase_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id TEXT NOT NULL,
    po_number TEXT NOT NULL,
    vendor_name TEXT NOT NULL,
    vendor_contact TEXT,
    description TEXT NOT NULL,
    amount NUMERIC(14,2) NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'draft',
    -- allowed: draft, sent, acknowledged, fulfilled, cancelled
    bid_package_id UUID,
    issued_date DATE,
    expected_delivery DATE,
    actual_delivery DATE,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_purchase_orders_project_po UNIQUE (project_id, po_number),
    CONSTRAINT chk_purchase_orders_status CHECK (status IN ('draft','sent','acknowledged','fulfilled','cancelled'))
);
CREATE INDEX IF NOT EXISTS idx_purchase_orders_project_id ON purchase_orders(project_id);
CREATE INDEX IF NOT EXISTS idx_purchase_orders_status ON purchase_orders(status);
CREATE INDEX IF NOT EXISTS idx_purchase_orders_expected_delivery ON purchase_orders(expected_delivery);
CREATE INDEX IF NOT EXISTS idx_purchase_orders_bid_package_id ON purchase_orders(bid_package_id);
-- FK to bid_packages (confirm PK name with Code):
-- ALTER TABLE purchase_orders ADD CONSTRAINT fk_purchase_orders_bid_package
-- FOREIGN KEY (bid_package_id) REFERENCES bid_packages(id) ON DELETE SET NULL;
```

### long_lead_materials

```sql
CREATE TABLE IF NOT EXISTS long_lead_materials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id TEXT NOT NULL,
    material_name TEXT NOT NULL,
    supplier TEXT,
    lead_time_weeks INTEGER,
    order_date DATE,
    expected_delivery DATE,
    actual_delivery DATE,
    linked_cpm_activity_id UUID REFERENCES cpm_activities(id) ON DELETE SET NULL,
    status TEXT NOT NULL DEFAULT 'not_ordered',
    -- allowed: not_ordered, ordered, in_transit, delivered, installed
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_long_lead_materials_status CHECK (status IN ('not_ordered','ordered','in_transit','delivered','installed'))
);
CREATE INDEX IF NOT EXISTS idx_long_lead_project_id ON long_lead_materials(project_id);
CREATE INDEX IF NOT EXISTS idx_long_lead_status ON long_lead_materials(status);
CREATE INDEX IF NOT EXISTS idx_long_lead_expected_delivery ON long_lead_materials(expected_delivery);
CREATE INDEX IF NOT EXISTS idx_long_lead_cpm_activity ON long_lead_materials(linked_cpm_activity_id);
```

---

## 2) Business Rules

**Rule 1 — Long-Lead CPM Links (Examples):**

| Material | Linked CPM Activity |
|----------|---------------------|
| Custom windows/doors | Rough framing complete |
| Structural steel | Foundation complete |
| Elevator equipment | Core rough-in |
| Custom millwork/cabinets | Drywall complete |
| Specialty stone | Stone install |

System surfaces schedule exposure BEFORE the material becomes a field problem.

**Rule 2 — Procurement Risk Logic:**
- expected_delivery > linked_cpm_activity.start_planned = SCHEDULE RISK
- status in (not_ordered, ordered) AND activity start <= today + lead_time_weeks * 7 days = YELLOW
- expected_delivery null AND linked activity within 30 days = RISK

**Rule 3 — PO Status Progression:**
draft -> sent -> acknowledged -> fulfilled (or cancelled at any stage)
Status transitions are one-directional. Cannot un-fulfill a PO.

**Rule 4 — Long-Lead Status Progression:**
not_ordered -> ordered -> in_transit -> delivered -> installed
Cannot un-install a material.

**Rule 5 — Cost Forecasting Integration:**
- sent/acknowledged/fulfilled = committed_cost
- draft = NOT committed
- cancelled = excluded

**Rule 6 — PO Approval:**
- draft creation allowed without approval
- draft->sent above configured threshold requires approval
- record approval_id (future column) on approval

---

## 3) Buyout Log View

```sql
-- vw_procurement_buyout_log
-- Bid Package -> PO -> Long-Lead Materials -> CPM Activity
SELECT
    po.project_id,
    po.po_number,
    po.vendor_name,
    po.description AS po_description,
    po.amount,
    po.status AS po_status,
    po.issued_date,
    po.expected_delivery AS po_expected_delivery,
    po.actual_delivery AS po_actual_delivery,
    llm.material_name,
    llm.supplier,
    llm.lead_time_weeks,
    llm.status AS material_status,
    llm.expected_delivery AS material_expected_delivery,
    cpm.name AS linked_activity_name,
    cpm.start_planned AS activity_start_planned,
    cpm.is_critical,
    CASE WHEN llm.expected_delivery IS NOT NULL
         AND cpm.start_planned IS NOT NULL
         AND llm.expected_delivery > cpm.start_planned
    THEN TRUE ELSE FALSE
    END AS schedule_risk
FROM purchase_orders po
LEFT JOIN long_lead_materials llm ON llm.project_id = po.project_id
LEFT JOIN cpm_activities cpm ON cpm.id = llm.linked_cpm_activity_id;
```

> Note: Phase 1 lacks direct PO-to-material link. Future: add po_id UUID column on long_lead_materials.

---

## 4) FastAPI Router (app/api/routers/procurement.py)

```python
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.procurement import PurchaseOrder, LongLeadMaterial
from app.schemas.procurement import (
    PurchaseOrderCreate, PurchaseOrderOut, PurchaseOrderStatusUpdate,
    LongLeadMaterialCreate, LongLeadMaterialOut,
)

router = APIRouter(prefix="/procurement", tags=["Procurement"])

VALID_PO_STATUSES = ["draft", "sent", "acknowledged", "fulfilled", "cancelled"]
VALID_LL_STATUSES = ["not_ordered", "ordered", "in_transit", "delivered", "installed"]


@router.post("/po", response_model=PurchaseOrderOut, status_code=201)
def create_purchase_order(payload: PurchaseOrderCreate, db: Session = Depends(get_db)):
    try:
        po = PurchaseOrder(
            project_id=payload.project_id,
            po_number=payload.po_number,
            vendor_name=payload.vendor_name,
            vendor_contact=payload.vendor_contact,
            description=payload.description,
            amount=payload.amount,
            bid_package_id=payload.bid_package_id,
            issued_date=payload.issued_date,
            expected_delivery=payload.expected_delivery,
            notes=payload.notes,
            status="draft",
        )
        db.add(po)
        db.commit()
        db.refresh(po)
        return po
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="PO number already exists for this project")
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create purchase order: {str(exc)}")


@router.get("/po/{project_id}", response_model=list[PurchaseOrderOut])
def get_purchase_orders(project_id: str, status: str = None, db: Session = Depends(get_db)):
    if status and status not in VALID_PO_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status filter: {status}")
    query = db.query(PurchaseOrder).filter(PurchaseOrder.project_id == project_id)
    if status:
        query = query.filter(PurchaseOrder.status == status)
    return query.order_by(PurchaseOrder.created_at.desc()).all()


@router.patch("/po/{po_id}/status", response_model=PurchaseOrderOut)
def update_po_status(po_id: UUID, payload: PurchaseOrderStatusUpdate, db: Session = Depends(get_db)):
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    if payload.status not in VALID_PO_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status: {payload.status}")
    po.status = payload.status
    if payload.actual_delivery:
        po.actual_delivery = payload.actual_delivery
    if payload.notes:
        po.notes = (po.notes or "") + "\n" + payload.notes
    try:
        db.commit()
        db.refresh(po)
        return po
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update PO: {str(exc)}")


@router.post("/long-lead", response_model=LongLeadMaterialOut, status_code=201)
def create_long_lead_material(payload: LongLeadMaterialCreate, db: Session = Depends(get_db)):
    if payload.status == "installed" and payload.actual_delivery is None:
        raise HTTPException(status_code=400, detail="Cannot mark material installed without actual_delivery date")
    try:
        item = LongLeadMaterial(
            project_id=payload.project_id,
            material_name=payload.material_name,
            supplier=payload.supplier,
            lead_time_weeks=payload.lead_time_weeks,
            order_date=payload.order_date,
            expected_delivery=payload.expected_delivery,
            actual_delivery=payload.actual_delivery,
            linked_cpm_activity_id=payload.linked_cpm_activity_id,
            status=payload.status,
            notes=payload.notes,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create long-lead material: {str(exc)}")


@router.get("/long-lead/{project_id}", response_model=list[LongLeadMaterialOut])
def get_long_lead_materials(project_id: str, status: str = None, db: Session = Depends(get_db)):
    if status and status not in VALID_LL_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status filter: {status}")
    query = db.query(LongLeadMaterial).filter(LongLeadMaterial.project_id == project_id)
    if status:
        query = query.filter(LongLeadMaterial.status == status)
    return query.order_by(LongLeadMaterial.expected_delivery.asc().nullslast(), LongLeadMaterial.created_at.desc()).all()
```

---

## 5) Endpoint Summary

| Method | Path | Description |
|--------|------|-------------|
| POST | /procurement/po | Create purchase order (status=draft) |
| GET | /procurement/po/{project_id} | List POs for project |
| PATCH | /procurement/po/{id}/status | Advance PO lifecycle status |
| POST | /procurement/long-lead | Register long-lead material |
| GET | /procurement/long-lead/{project_id} | List long-lead materials |

---

## 6) Procurement Risk Service (app/services/procurement_risk_service.py)

```python
from datetime import date
from typing import Optional

def evaluate_long_lead_risk(item, linked_activity) -> Optional[dict]:
    """Evaluate schedule risk for a long-lead material.
    Returns risk dict {severity, type, message} or None if no risk."""
    if linked_activity is None:
        return None
    today = date.today()
    # RED/YELLOW: delivery expected after activity start
    if (item.expected_delivery is not None
            and linked_activity.start_planned is not None
            and item.expected_delivery > linked_activity.start_planned):
        severity = "RED" if linked_activity.is_critical else "YELLOW"
        return {
            "severity": severity,
            "type": "LONG_LEAD_DELIVERY_AFTER_ACTIVITY_START",
            "message": (f"{item.material_name} expected delivery {item.expected_delivery}"
                        f" is after linked activity start {linked_activity.start_planned}."),
        }
    # YELLOW: not yet ordered but within lead-time window
    if item.status in ("not_ordered", "ordered") and linked_activity.start_planned:
        days_until_activity = (linked_activity.start_planned - today).days
        if item.lead_time_weeks is not None:
            lead_days = item.lead_time_weeks * 7
            if days_until_activity <= lead_days:
                return {
                    "severity": "YELLOW",
                    "type": "LONG_LEAD_NOT_ORDERED_WITHIN_LEAD_TIME",
                    "message": (f"{item.material_name} is not ordered"
                                f" within its {item.lead_time_weeks}-week lead time window."),
                }
    return None
```

Mission Control consumes these as procurement risks per project.

---

## 7) Test Cases

| # | Test | Expected |
|---|------|----------|
| 1 | Create PO with valid data | 201, status=draft |
| 2 | Create duplicate PO (same project_id + po_number) | 409 |
| 3 | GET POs for project | 200 list |
| 4 | GET POs with valid status filter | Only matching status |
| 5 | GET POs with invalid status filter | 400 |
| 6 | PATCH PO status draft -> sent | 200, status=sent |
| 7 | PATCH PO with invalid status | 400 |
| 8 | PATCH non-existent PO | 404 |
| 9 | Create long-lead with linked CPM activity | 201 |
| 10 | Create long-lead status=installed without actual_delivery | 400 |
| 11 | GET long-lead for project | 200 ordered by expected_delivery asc nulls last |
| 12 | Risk service: delivery after critical activity start | RED |
| 13 | Risk service: delivery after non-critical activity start | YELLOW |
| 14 | Risk service: not ordered within lead-time window | YELLOW |
| 15 | Buyout log view: schedule_risk=TRUE when delivery > activity start | Correct |

---

## 8) Cross-System Integration

**CPM (Cycle 9):** linked_cpm_activity_id creates hard link to schedule. Risk service evaluates delivery vs activity start. Phase 2: /procurement/risks/{project_id} endpoint.

**Cost Forecasting (Cycle 11):** PO amounts with status in (sent, acknowledged, fulfilled) feed into committed_cost. Prevents double-counting if PO linked to bid_package.

**Daily Field Intelligence (Cycle 15):** When materials delivered, field report can reference delivery. Phase 2: auto-update long_lead status to delivered on field report confirmation.

---

## 9) Router Registration

In app/main.py:
```python
from app.api.routers import procurement
app.include_router(procurement.router)
```

---

## Definition of Done

Procurement and Material Tracking Phase 1 complete when:
- [ ] purchase_orders table exists
- [ ] long_lead_materials table exists
- [ ] PO lifecycle endpoints implemented (POST, GET, PATCH status)
- [ ] Long-lead material endpoints implemented (POST, GET)
- [ ] Long-lead materials link to CPM activities via FK
- [ ] Schedule risk detection for delivery/activity conflicts
- [ ] Buyout log view vw_procurement_buyout_log created
- [ ] Cost Forecasting can consume committed PO values
- [ ] Mission Control can display procurement risk flags
- [ ] 15 test cases pass

---

*Spec generated by GBT Cycle 16 | BC Operations Intelligence | 2026-07-01*

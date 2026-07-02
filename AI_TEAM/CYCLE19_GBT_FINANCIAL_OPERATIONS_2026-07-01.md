# CYCLE 19 — Sprint 5 Priority 6: Financial Operations & Budget-to-Actual
**GBT Cycle:** 19 | **Date:** 2026-07-01 | **Status:** SPEC COMPLETE
**Sprint:** 5 | **Priority:** 6 of 6 | **Depends on:** Cycles 4 (bid packages), 11 (cost forecast), 16 (procurement)
**Note:** GBT Cycle 19 experienced connection interruption during generation. Spec authored by BC from partial GBT output + system architecture context.

---

## Architecture Overview

Financial Operations turns financial tracking into an operational intelligence system.
The objective is to answer:
- What did we budget?
- What have we committed?
- What has actually hit the books?
- Where do we project to finish?
- Which divisions are drifting before the job is over?

QuickBooks remains the accounting source of truth for actual costs. HCI does NOT use Buildertrend.

---

## 1) PostgreSQL DDL

### budget_line_items

```sql
CREATE TABLE IF NOT EXISTS budget_line_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id TEXT NOT NULL,
    division TEXT,
    csi_code TEXT,
    description TEXT NOT NULL,
    budgeted_amount NUMERIC(14,2) NOT NULL DEFAULT 0,
    committed_amount NUMERIC(14,2) NOT NULL DEFAULT 0,
    actual_cost_to_date NUMERIC(14,2) NOT NULL DEFAULT 0,
    projected_final NUMERIC(14,2) NOT NULL DEFAULT 0,
    variance NUMERIC(14,2) NOT NULL DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_budget_line_project_id ON budget_line_items(project_id);
CREATE INDEX IF NOT EXISTS idx_budget_line_division ON budget_line_items(project_id, division);
CREATE INDEX IF NOT EXISTS idx_budget_line_csi_code ON budget_line_items(project_id, csi_code);
```

---

## 2) Business Rules — The 4 Financial Numbers

**budgeted_amount** — Original contract budget + approved owner change orders.
Updated when: project awarded, change orders approved by owner.

**committed_amount** — What HCI has legally obligated to pay. Sum of purchase_orders with status IN (sent, acknowledged, fulfilled) per division/CSI.
Source: purchase_orders table (Cycle 16).

**actual_cost_to_date** — What has actually been paid. Source: QuickBooks sync (QB -> HCI direction). QB is the accounting source of truth.

**projected_final** — Best estimate of final cost at completion.
Phase 1 formula: `projected_final = GREATEST(committed_amount, actual_cost_to_date)`
Phase 2: PM-entered estimate to complete (ETC) logic.

**variance** — `variance = projected_final - budgeted_amount`
Interpretation: positive = over budget, negative = under budget, zero = on budget.

**Health Thresholds (per line item):**
- GREEN: variance <= 2% of budgeted_amount
- YELLOW: variance > 2% and <= 5% OR variance > $150,000
- RED: variance > 5% OR variance > $150,000 with trend worsening

**Change Order Impact:**
- Owner-approved change orders -> increase budgeted_amount on affected line(s)
- Internal COs not approved by owner -> do NOT increase budget, tracked separately

---

## 3) Budget-to-Actual View

```sql
-- vw_budget_to_actual
-- Joins budget_line_items + PO committed amounts + QuickBooks actuals
SELECT
    b.project_id,
    b.id AS budget_line_id,
    b.division,
    b.csi_code,
    b.description,
    b.budgeted_amount,
    b.committed_amount,
    b.actual_cost_to_date,
    b.projected_final,
    b.variance,
    CASE
        WHEN b.budgeted_amount = 0 THEN NULL
        ELSE ROUND((b.variance / b.budgeted_amount) * 100, 2)
    END AS variance_pct,
    CASE
        WHEN b.budgeted_amount = 0 THEN 'GREEN'
        WHEN ABS(b.variance / b.budgeted_amount) <= 0.02 THEN 'GREEN'
        WHEN ABS(b.variance / b.budgeted_amount) <= 0.05 OR ABS(b.variance) > 150000 THEN 'YELLOW'
        ELSE 'RED'
    END AS health_status,
    cf.health_status AS forecast_health
FROM budget_line_items b
LEFT JOIN cost_forecast cf ON cf.project_id = b.project_id
ORDER BY b.project_id, b.division, b.csi_code;
```

---

## 4) QuickBooks Sync Strategy

**Sync direction:** QuickBooks -> HCI (QB is source of truth for actuals)
HCI writes: project setup, budget lines, POs. HCI reads: actual costs, vendor payments, AP balances.

**Sync approach (Phase 1 — polling):**
- n8n WF-QB-001 polls QuickBooks API on a schedule (daily at night or on-demand)
- Fetches job costs by project ID and cost code
- Updates actual_cost_to_date on matching budget_line_items
- Records last_sync_at timestamp

**Phase 2 — Webhook:**
- QuickBooks Online supports webhooks for real-time sync
- POST /finance/qb-sync endpoint receives webhook events
- Updates actuals in real-time

**What HCI tracks in QuickBooks:**
- Subcontractor payments (AP invoices)
- Material purchases
- Labor costs (payroll integration)
- Overhead allocations

**Sync data model:**
```sql
-- qb_sync_log (future table)
-- id, project_id, sync_direction, records_updated, errors JSONB, synced_at
```

---

## 5) Pydantic Schemas (app/schemas/finance.py)

```python
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class BudgetLineCreate(BaseModel):
    project_id: str
    division: Optional[str] = None
    csi_code: Optional[str] = None
    description: str
    budgeted_amount: Decimal = Decimal("0.00")
    notes: Optional[str] = None

class BudgetLineOut(BaseModel):
    id: UUID
    project_id: str
    division: Optional[str] = None
    csi_code: Optional[str] = None
    description: str
    budgeted_amount: Decimal
    committed_amount: Decimal
    actual_cost_to_date: Decimal
    projected_final: Decimal
    variance: Decimal
    notes: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True

class BudgetSummaryOut(BaseModel):
    project_id: str
    total_budgeted: Decimal
    total_committed: Decimal
    total_actual: Decimal
    total_projected_final: Decimal
    total_variance: Decimal
    variance_pct: Optional[float] = None
    health_status: str
    line_count: int
    red_lines: int
    yellow_lines: int
    green_lines: int
```

---

## 6) FastAPI Router (app/api/routers/finance.py)

```python
from uuid import UUID
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.finance import BudgetLineItem
from app.schemas.finance import BudgetLineCreate, BudgetLineOut, BudgetSummaryOut

router = APIRouter(prefix="/finance", tags=["Financial Operations"])


def get_line_health(variance: Decimal, budgeted: Decimal) -> str:
    if budgeted == 0:
        return "GREEN"
    pct = abs(variance / budgeted)
    if pct <= Decimal("0.02"):
        return "GREEN"
    elif pct <= Decimal("0.05") or abs(variance) > 150000:
        return "YELLOW"
    return "RED"


@router.post("/budget-line", response_model=BudgetLineOut, status_code=201)
def create_budget_line(payload: BudgetLineCreate, db: Session = Depends(get_db)):
    try:
        line = BudgetLineItem(
            project_id=payload.project_id,
            division=payload.division,
            csi_code=payload.csi_code,
            description=payload.description,
            budgeted_amount=payload.budgeted_amount,
            notes=payload.notes,
        )
        db.add(line)
        db.commit()
        db.refresh(line)
        return line
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create budget line: {str(exc)}")


@router.get("/budget/{project_id}", response_model=list[BudgetLineOut])
def get_budget_lines(project_id: str, division: str = None, db: Session = Depends(get_db)):
    query = db.query(BudgetLineItem).filter(BudgetLineItem.project_id == project_id)
    if division:
        query = query.filter(BudgetLineItem.division == division)
    return query.order_by(BudgetLineItem.division, BudgetLineItem.csi_code).all()


@router.get("/budget-summary/{project_id}", response_model=BudgetSummaryOut)
def get_budget_summary(project_id: str, db: Session = Depends(get_db)):
    lines = db.query(BudgetLineItem).filter(BudgetLineItem.project_id == project_id).all()
    if not lines:
        raise HTTPException(status_code=404, detail="No budget lines found for project")
    total_budgeted = sum(l.budgeted_amount for l in lines)
    total_committed = sum(l.committed_amount for l in lines)
    total_actual = sum(l.actual_cost_to_date for l in lines)
    total_projected = sum(l.projected_final for l in lines)
    total_variance = sum(l.variance for l in lines)
    health_counts = {"RED": 0, "YELLOW": 0, "GREEN": 0}
    for l in lines:
        h = get_line_health(l.variance, l.budgeted_amount)
        health_counts[h] += 1
    if health_counts["RED"] > 0:
        overall_health = "RED"
    elif health_counts["YELLOW"] > 0:
        overall_health = "YELLOW"
    else:
        overall_health = "GREEN"
    variance_pct = None
    if total_budgeted > 0:
        variance_pct = round(float(total_variance / total_budgeted) * 100, 2)
    return BudgetSummaryOut(
        project_id=project_id,
        total_budgeted=total_budgeted,
        total_committed=total_committed,
        total_actual=total_actual,
        total_projected_final=total_projected,
        total_variance=total_variance,
        variance_pct=variance_pct,
        health_status=overall_health,
        line_count=len(lines),
        red_lines=health_counts["RED"],
        yellow_lines=health_counts["YELLOW"],
        green_lines=health_counts["GREEN"],
    )
```

---

## 7) Endpoint Summary

| Method | Path | Description |
|--------|------|-------------|
| POST | /finance/budget-line | Create budget line item |
| GET | /finance/budget/{project_id} | List budget lines (optional ?division= filter) |
| GET | /finance/budget-summary/{project_id} | Aggregated summary with health status |

---

## 8) SQLAlchemy Model (app/models/finance.py)

```python
import uuid
from decimal import Decimal
from sqlalchemy import Column, Numeric, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class BudgetLineItem(Base):
    __tablename__ = "budget_line_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(Text, nullable=False, index=True)
    division = Column(Text, nullable=True)
    csi_code = Column(Text, nullable=True)
    description = Column(Text, nullable=False)
    budgeted_amount = Column(Numeric(14, 2), nullable=False, default=0)
    committed_amount = Column(Numeric(14, 2), nullable=False, default=0)
    actual_cost_to_date = Column(Numeric(14, 2), nullable=False, default=0)
    projected_final = Column(Numeric(14, 2), nullable=False, default=0)
    variance = Column(Numeric(14, 2), nullable=False, default=0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
```

---

## 9) Mission Control Financial Dashboard Output

```json
{
  "project_id": "101F",
  "financial_intelligence": {
    "total_budgeted": 4250000.00,
    "total_committed": 3980000.00,
    "total_actual": 2750000.00,
    "total_projected_final": 4310000.00,
    "total_variance": 60000.00,
    "variance_pct": 1.41,
    "health_status": "GREEN",
    "red_lines": 0,
    "yellow_lines": 2,
    "green_lines": 14,
    "last_qb_sync": "2026-07-01T06:00:00Z",
    "pending_po_value": 380000.00
  }
}
```

---

## 10) n8n Workflow

**WF-QB-001 — QuickBooks Actuals Sync**
Trigger: Daily at 06:00 (before Supers arrive at 7:00 AM)
Action: Authenticate with QuickBooks API using OAuth2 refresh token
Action: Query job costs for all active projects by cost code
Action: Match to budget_line_items by project_id + csi_code
Action: Update actual_cost_to_date and recalculate projected_final + variance
Action: Flag RED/YELLOW lines and create Mission Control alerts
Action: Log sync results to qb_sync_log

**QB OAuth2 Note:**
QuickBooks Online uses OAuth2 with refresh tokens that expire every 100 days.
Code must implement token refresh logic and store tokens securely (not in plain text).

---

## 11) Integration Points

**Cost Forecasting (Cycle 11):** cost_forecast table stores project-level health. budget_line_items stores division/CSI-level detail. Both feed Mission Control.

**Procurement (Cycle 16):** committed_amount on budget_line_items populated from purchase_orders WHERE status IN (sent, acknowledged, fulfilled) grouped by division.

**Bid Packages (Cycle 4):** bid_packages.awarded_amount seeds budgeted_amount on budget_line_items.

**Change Orders:** approved owner change orders update budgeted_amount. Internal COs tracked separately as variance flags.

---

## 12) Test Cases

| # | Test | Expected |
|---|------|----------|
| 1 | Create budget line | 201 |
| 2 | GET budget lines for project | 200 list ordered by division, csi_code |
| 3 | GET budget lines with division filter | Only matching division |
| 4 | GET budget summary | 200 with aggregated totals and health |
| 5 | GET budget summary no lines | 404 |
| 6 | Budget summary health GREEN (variance <= 2%) | health_status=GREEN |
| 7 | Budget summary health YELLOW (variance 2-5%) | health_status=YELLOW |
| 8 | Budget summary health RED (variance > 5%) | health_status=RED |
| 9 | QB sync updates actual_cost_to_date | Line updated correctly |
| 10 | projected_final = GREATEST(committed, actual) | Correct calculation |
| 11 | variance = projected_final - budgeted | Correct calculation |
| 12 | Over budget line creates RED flag | Mission Control alert created |

---

## 13) Router Registration

In app/main.py:
```python
from app.api.routers import finance
app.include_router(finance.router)
```

---

## Definition of Done

Financial Operations Phase 1 complete when:
- [ ] budget_line_items table exists
- [ ] Budget line CRUD endpoints implemented
- [ ] Budget summary endpoint with health status
- [ ] variance and projected_final calculated correctly
- [ ] Budget-to-actual view documented
- [ ] QuickBooks sync strategy specified
- [ ] WF-QB-001 workflow specified for QB actuals polling
- [ ] Mission Control can display financial dashboard
- [ ] Integration with procurement committed amounts documented
- [ ] 12 test cases pass

---

## Sprint 5 Completion Status

| Priority | Capability | Cycle | Status |
|----------|-----------|-------|--------|
| 1 | RFI + Submittal Management | 14 | SPEC COMMITTED |
| 2 | Daily Field Intelligence | 15 | SPEC COMMITTED |
| 3 | Procurement & Material Tracking | 16 | SPEC COMMITTED |
| 4 | Photo Intelligence | 17 | SPEC COMMITTED |
| 5 | Punch List & Warranty | 18 | SPEC COMMITTED |
| 6 | Financial Operations | 19 | SPEC COMMITTED |

**Sprint 5 is COMPLETE. All 6 priorities specified and committed to AI_TEAM/.**

---

*Spec generated by GBT Cycle 19 (partial) + BC Operations Intelligence architecture synthesis | 2026-07-01*

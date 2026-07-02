# CYCLE 11 — GBT COST FORECASTING INTELLIGENCE
**Date:** 2026-07-01
**Cycle:** 11
**Priority:** Sprint 4 #3
**Status:** SPEC COMPLETE — Awaiting Claude Code implementation
**Author:** HCI Chief Architect (GBT) via BC Operations Intelligence

---

## 1. PostgreSQL DDL — cost_forecast Table

```sql
CREATE TABLE cost_forecast (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      VARCHAR(64) NOT NULL,
    forecast_date   DATE NOT NULL DEFAULT CURRENT_DATE,
    original_budget NUMERIC(14,2) NOT NULL,
    committed_cost  NUMERIC(14,2) NOT NULL DEFAULT 0,
    pending_changes NUMERIC(14,2) NOT NULL DEFAULT 0,
    approved_changes NUMERIC(14,2) NOT NULL DEFAULT 0,
    projected_final NUMERIC(14,2) GENERATED ALWAYS AS
        (committed_cost + pending_changes + approved_changes) STORED,
    variance_to_budget NUMERIC(14,2) GENERATED ALWAYS AS
        (committed_cost + pending_changes + approved_changes - original_budget) STORED,
    forecast_confidence NUMERIC(5,2) CHECK (forecast_confidence BETWEEN 0 AND 100),
    health           VARCHAR(10) NOT NULL DEFAULT 'GREEN'
                     CHECK (health IN ('GREEN','YELLOW','RED')),
    notes            TEXT,
    created_by       VARCHAR(128) NOT NULL DEFAULT 'system',
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_cost_forecast_project_date
    ON cost_forecast (project_id, forecast_date DESC);

-- Snapshot history: never delete, always insert new row
-- Latest snapshot = ORDER BY forecast_date DESC LIMIT 1
```

---

## 2. Forecast Calculation Logic

### 2.1 Core Formula

```
projected_final = committed_cost + pending_changes + approved_changes
variance_to_budget = projected_final - original_budget
variance_pct = (variance_to_budget / original_budget) * 100
```

### 2.2 Health Thresholds

| Condition | Health |
|-----------|--------|
| variance_pct < 2% | GREEN |
| 2% <= variance_pct < 5% OR pending_changes > $150k | YELLOW |
| variance_pct >= 5% OR variance_to_budget > $150,000 | RED |

### 2.3 Confidence Scoring

```
base_confidence = 95
if pending_changes > 0:
    base_confidence -= min(20, (pending_changes / original_budget) * 100)
if days_since_last_update > 30:
    base_confidence -= 10
if approved_changes > original_budget * 0.1:
    base_confidence -= 5
forecast_confidence = max(0, base_confidence)
```

### 2.4 Data Source Priority

| Field | Primary Source | Fallback |
|-------|---------------|---------|
| original_budget | projects.budget | project_budget.original_budget → latest approved estimate |
| committed_cost | sum(bid_packages.awarded_amount) WHERE status='awarded' | accounts_payable ledger |
| pending_changes | sum(change_orders.amount) WHERE status='pending' | procurement_requests |
| approved_changes | sum(change_orders.amount) WHERE status='approved' | signed amendments |

### 2.5 Snapshot Strategy

- **Never overwrite** — every forecast run creates a new row
- **Latest** = SELECT * WHERE project_id = ? ORDER BY forecast_date DESC LIMIT 1
- **Trend** = SELECT * WHERE project_id = ? ORDER BY forecast_date (last 90 days)
- Enables historical EAC (Estimate at Completion) trending

---

## 3. FastAPI Endpoints

### 3.1 GET /cost/{project_id}/forecast

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.cost_forecast import CostForecast
from app.schemas.cost_forecast import CostForecastOut
from app.services.cost_service import calculate_cost_forecast

router = APIRouter(prefix='/cost', tags=['cost'])

@router.get('/{project_id}/forecast', response_model=CostForecastOut)
def get_latest_forecast(project_id: str, db: Session = Depends(get_db)):
    forecast = (
        db.query(CostForecast)
        .filter(CostForecast.project_id == project_id)
        .order_by(CostForecast.forecast_date.desc())
        .first()
    )
    if not forecast:
        raise HTTPException(status_code=404, detail=f'No forecast found for project {project_id}')
    return forecast
```

**Response Schema:**
```json
{
  "id": "uuid",
  "project_id": "HCI-2026-001",
  "forecast_date": "2026-07-01",
  "original_budget": 4500000.00,
  "committed_cost": 2100000.00,
  "pending_changes": 85000.00,
  "approved_changes": 42000.00,
  "projected_final": 2227000.00,
  "variance_to_budget": -2273000.00,
  "forecast_confidence": 91.5,
  "health": "GREEN",
  "notes": null,
  "created_by": "system",
  "created_at": "2026-07-01T08:00:00Z"
}
```

### 3.2 POST /cost/{project_id}/update-forecast

```python
from app.schemas.cost_forecast import CostForecastUpdateRequest
import decimal

class CostForecastUpdateRequest(BaseModel):
    committed_cost: Optional[Decimal] = None
    pending_changes: Optional[Decimal] = None
    approved_changes: Optional[Decimal] = None
    notes: Optional[str] = None
    created_by: str = 'system'

@router.post('/{project_id}/update-forecast', response_model=CostForecastOut)
def update_forecast(
    project_id: str,
    request: CostForecastUpdateRequest,
    db: Session = Depends(get_db),
):
    try:
        result = calculate_cost_forecast(project_id=project_id, db=db, created_by=request.created_by)
        notes = result['notes']
        if request.notes:
            notes = f'{notes} | Manual note: {request.notes}'
        forecast = CostForecast(
            project_id=project_id,
            forecast_date=date.today(),
            original_budget=result['original_budget'],
            committed_cost=result['committed_cost'],
            pending_changes=result['pending_changes'],
            approved_changes=result['approved_changes'],
            projected_final=result['projected_final'],
            variance_to_budget=result['variance_to_budget'],
            forecast_confidence=result['forecast_confidence'],
            health=result['health'],
            notes=notes,
            created_by=request.created_by,
        )
        db.add(forecast)
        db.commit()
        db.refresh(forecast)
        return forecast
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f'Failed to update cost forecast: {str(exc)}')
```

---

## 4. Cost Forecast Service (calculate_cost_forecast)

```python
from decimal import Decimal
from sqlalchemy.orm import Session

def get_original_budget(project_id: str, db: Session) -> Decimal:
    # Source priority:
    # 1. projects.budget or projects.contract_value
    # 2. project_budget.original_budget
    # 3. latest approved estimate
    pass  # Claude Code implements from existing tables

def get_committed_cost(project_id: str, db: Session) -> Decimal:
    # Sum of bid_packages.awarded_amount WHERE status='awarded'
    # Fallback: accounts_payable ledger sum
    pass

def get_pending_changes(project_id: str, db: Session) -> Decimal:
    # Sum of change_orders.amount WHERE status='pending'
    pass

def get_approved_changes(project_id: str, db: Session) -> Decimal:
    # Sum of change_orders.amount WHERE status='approved'
    pass

def determine_cost_health(original_budget, variance_to_budget, pending_changes, forecast_confidence) -> str:
    variance_pct = abs(float(variance_to_budget) / float(original_budget)) * 100 if original_budget else 0
    if variance_pct >= 5.0 or abs(float(variance_to_budget)) >= 150000:
        return 'RED'
    if variance_pct >= 2.0 or float(pending_changes) > 150000:
        return 'YELLOW'
    return 'GREEN'

def calculate_cost_forecast(project_id: str, db: Session, created_by: str = 'system') -> dict:
    original_budget = get_original_budget(project_id, db)
    committed_cost = get_committed_cost(project_id, db)
    pending_changes = get_pending_changes(project_id, db)
    approved_changes = get_approved_changes(project_id, db)
    projected_final = committed_cost + pending_changes + approved_changes
    variance_to_budget = projected_final - original_budget
    # Confidence scoring
    confidence = Decimal('95')
    if pending_changes > 0 and original_budget > 0:
        pct_pending = (pending_changes / original_budget) * 100
        confidence -= min(Decimal('20'), pct_pending)
    health = determine_cost_health(original_budget, variance_to_budget, pending_changes, confidence)
    return {
        'original_budget': original_budget,
        'committed_cost': committed_cost,
        'pending_changes': pending_changes,
        'approved_changes': approved_changes,
        'projected_final': projected_final,
        'variance_to_budget': variance_to_budget,
        'forecast_confidence': float(confidence),
        'health': health,
        'notes': f'Auto-calculated {date.today()} by {created_by}',
    }
```

---

## 5. Definition of Done

Cost Forecasting Phase 1 is complete when:
- [ ] cost_forecast table exists in PostgreSQL
- [ ] Forecast service calculates projected_final and variance_to_budget correctly
- [ ] GET /cost/{project_id}/forecast returns latest snapshot
- [ ] POST /cost/{project_id}/update-forecast creates new snapshot row
- [ ] Yellow/Red health triggers fire at correct thresholds (2%/5% and $150k)
- [ ] Forecast snapshots are persisted historically (never overwritten)
- [ ] Mission Control can consume forecast output
- [ ] Tests pass

---

## 6. Integration Points

| System | Integration |
|--------|------------|
| bid_packages | Source for committed_cost (awarded_amount) |
| change_orders | Source for pending + approved changes |
| projects | Source for original_budget |
| cpm_activities | CPM schedule delays trigger forecast review |
| Mission Control | Consumes GET /cost/{id}/forecast for dashboard |
| Telegram | RED health alert → instant Buck notification |

---
*Generated by HCI Chief Architect (GBT) Cycle 11 | Captured by BC Operations Intelligence | 2026-07-01*

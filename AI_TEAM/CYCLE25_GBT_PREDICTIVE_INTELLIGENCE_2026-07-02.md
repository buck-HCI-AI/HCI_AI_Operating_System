# CYCLE25 — Sprint 6 Priority 5: Predictive Intelligence Architecture
**Cycle:** 25
**Sprint:** 6
**Priority:** 5
**Date:** 2026-07-02
**Author:** GBT (HCI Chief Architect)
**Status:** SPEC COMPLETE — Ready for Code Implementation

---

## Overview

Predictive Intelligence moves HCI AI OS from:

```
What happened?
```

to:

```
What is likely to happen next, when, and how do we prevent it?
```

**Phase 1 is deterministic and explainable — not machine learning.**

Every prediction is derived from observable data using documented rules. No black-box models.

---

## 1) PostgreSQL DDL — schedule_risk_predictions

```sql
CREATE TABLE IF NOT EXISTS schedule_risk_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    project_id TEXT NOT NULL,

    prediction_date DATE NOT NULL DEFAULT CURRENT_DATE,

    predicted_by TEXT NOT NULL DEFAULT 'system',

    risk_type TEXT NOT NULL,
    -- allowed:
    -- material_delay
    -- weather_impact
    -- rfi_delay
    -- vendor_risk
    -- labor_shortage

    affected_activity_id UUID
        REFERENCES cpm_activities(id)
        ON DELETE SET NULL,

    probability NUMERIC(5,4) NOT NULL,
    -- 0.0000 to 1.0000

    predicted_delay_days INTEGER NOT NULL DEFAULT 0,

    confidence_level TEXT NOT NULL DEFAULT 'medium',
    -- allowed: low | medium | high

    contributing_factors JSONB NOT NULL DEFAULT '[]'::jsonb,

    status TEXT NOT NULL DEFAULT 'active',
    -- allowed: active | resolved | expired

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_schedule_risk_type CHECK (
        risk_type IN (
            'material_delay',
            'weather_impact',
            'rfi_delay',
            'vendor_risk',
            'labor_shortage'
        )
    ),

    CONSTRAINT chk_schedule_risk_confidence CHECK (
        confidence_level IN ('low', 'medium', 'high')
    ),

    CONSTRAINT chk_schedule_risk_status CHECK (
        status IN ('active', 'resolved', 'expired')
    ),

    CONSTRAINT chk_schedule_risk_probability CHECK (
        probability >= 0.0 AND probability <= 1.0
    ),

    FOREIGN KEY (affected_activity_id)
        REFERENCES cpm_activities(id)
        ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_schedule_risk_project_id
    ON schedule_risk_predictions(project_id);

CREATE INDEX IF NOT EXISTS idx_schedule_risk_type
    ON schedule_risk_predictions(risk_type);

CREATE INDEX IF NOT EXISTS idx_schedule_risk_status
    ON schedule_risk_predictions(status);

CREATE INDEX IF NOT EXISTS idx_schedule_risk_probability
    ON schedule_risk_predictions(probability DESC);

CREATE INDEX IF NOT EXISTS idx_schedule_risk_date
    ON schedule_risk_predictions(prediction_date DESC);

CREATE INDEX IF NOT EXISTS idx_schedule_risk_activity
    ON schedule_risk_predictions(affected_activity_id);
```

### Upsert Logic

Unique key: `project_id + risk_type + affected_activity_id`

If active prediction exists for the same combination:
- Update probability, contributing factors, predicted_delay_days
- Keep original `created_at` (or add `updated_at` later)

---

## 2) Risk Detection Rules

**Phase 1 is deterministic and explainable.**

Every prediction must include:
- risk type
- affected activity
- probability (numeric)
- predicted delay days
- contributing factors (list of reasons)
- confidence level

### A. Material Delay Risk

**Trigger when:**
```sql
long_lead_materials.expected_delivery
    WITHIN 14 days of linked cpm_activity.start_planned
AND long_lead_materials.status NOT IN ('delivered', 'installed')
```

Also trigger if:
- material is not yet ordered and activity starts within lead_time_weeks * 7 days

**Probability Table:**

| Delivery Timing | Probability |
|----------------|-------------|
| expected_delivery after activity start | 0.90 |
| 0–3 days buffer and not delivered | 0.75 |
| 4–7 days buffer and not delivered | 0.60 |
| 8–14 days buffer and not delivered | 0.40 |

**Predicted Delay Days (if delivered late):**
```python
predicted_delay_days = max(
    0,
    (material.expected_delivery - activity.start_planned).days
)
```

**If not ordered:**
```python
predicted_delay_days = max(
    3,
    material.lead_time_weeks * 7 - days_until_activity
)
```

**Confidence:**
```
high = expected_delivery known and linked activity confirmed
medium = expected_delivery known but activity non-critical
low = missing expected delivery or missing lead_time_weeks
```

### B. Weather Impact Risk

**Trigger when:**
- Weather alert severity is RED or YELLOW
- Linked cpm_activity is weather-sensitive (trade: concrete / roofing / excavation / exterior)
- Activity is scheduled to start within 7 days

**Probability:**
```
RED alert + critical activity = 0.85
RED alert + non-critical activity = 0.65
YELLOW alert + critical activity = 0.55
YELLOW alert + non-critical activity = 0.35
```

**Predicted Delay Days:**
```
RED = 2 days default
YELLOW = 1 day default
Override if forecast event duration is longer.
```

**Confidence:**
```
high = official alert + critical activity
medium = forecast threshold exceeded
low = weather-sensitive activity without exact forecast
```

### C. RFI Delay Risk

**Rule:** Trigger when:
```sql
rfis.status = 'open'
AND due_date < today
AND linked to schedule activity through project_entity_links
```

Also trigger if:
- RFI has no due date but has been open more than 7 days

**Probability:**
```
overdue > 14 days and critical path = 0.90
overdue > 7 days = 0.80
overdue 1–7 days = 0.60
open no due date > 7 days = 0.45
```

**Predicted Delay Days (Python):**
```python
days_overdue = today - rfi.due_date

if activity.is_critical:
    predicted_delay_days = min(days_overdue, 10)
else:
    predicted_delay_days = min(max(days_overdue - activity.float_days, 0), 10)
```

**Confidence:**
```
high = RFI linked to critical CPM activity
medium = RFI linked to non-critical CPM activity
low = RFI not explicitly linked but project phase suggests risk
```

### D. Vendor Risk

**Rule:** Trigger when:
```sql
vendor_performance_scores.overall_score < 6
AND vendor has active purchase_orders on project
AND purchase_order.status IN ('sent', 'acknowledged', 'fulfilled')
```

Also trigger if vendor has:
- Multiple open punch items (> 5) on current project
- Any warranty callback in last 6 months
- RFI response time > 10 days on current project

**Probability:**
```
score < 4 = 0.80
score 4–5.9 = 0.65
score 6–6.9 = 0.40 (warning only)
```

**Predicted Delay Days:**
- Vendor risk does not predict specific delay — flags exposure
- predicted_delay_days defaults to 3 (conservative estimate)

**Confidence:**
```
high = vendor score < 6 + active PO + open punches
medium = vendor score < 6 + active PO only
low = vendor score borderline (6.0–6.9)
```

### E. Labor Shortage Risk (Phase 1 Stub)

**Rule:** Flag when daily field reports for a project show:
- crew_count < expected_crew_count for 3+ consecutive days
- expected_crew_count source: project settings or historical average

**Phase 1:** Stub detection only. No formula implementation required.

---

## 3) Prediction Service

File: `app/services/predictive_intelligence_service.py`

```python
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.schedule_risk_predictions import ScheduleRiskPrediction

def generate_schedule_predictions(project_id: str, db: Session) -> list[ScheduleRiskPrediction]:
    predictions = []

    # A. Material delay detection
    predictions.extend(detect_material_delay_risks(project_id, db))

    # B. Weather impact detection
    predictions.extend(detect_weather_risks(project_id, db))

    # C. RFI delay detection
    predictions.extend(detect_rfi_delay_risks(project_id, db))

    # D. Vendor risk detection
    predictions.extend(detect_vendor_risks(project_id, db))

    # Upsert all predictions
    for pred in predictions:
        upsert_prediction(pred, db)

    db.commit()

    return get_active_schedule_predictions(project_id, db)

def get_active_schedule_predictions(project_id: str, db: Session) -> list[ScheduleRiskPrediction]:
    return (
        db.query(ScheduleRiskPrediction)
        .filter(
            ScheduleRiskPrediction.project_id == project_id,
            ScheduleRiskPrediction.status == "active",
        )
        .order_by(
            ScheduleRiskPrediction.probability.desc(),
            ScheduleRiskPrediction.predicted_delay_days.desc(),
        )
        .all()
    )

def build_budget_exposure_forecast(project_id: str, db: Session) -> dict | None:
    # Pull latest cost_forecast
    # Pull budget_line_items
    # Pull RFI cost impacts
    # Pull vendor risk from predictions
    # Compute additional_risk_exposure and risk_adjusted_projected_final
    ...
```

---

## 4) Budget Prediction Logic

Budget prediction uses:
- `cost_forecast`
- `budget_line_items`
- `purchase_orders`
- `rfis.cost_impact`
- `long_lead_materials`
- `vendor_performance_scores`

**additional_risk_exposure = sum of:**
- Open RFI cost_impact values where status = 'open'
- Vendor risk exposure = active PO amounts from low-score vendors × risk factor
- Long-lead material premium risk (if material delayed by >14 days)

**risk_adjusted_projected_final:**
```
= current_projected_final + additional_risk_exposure
```

---

## 5) Pydantic Schemas

```python
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID
from pydantic import BaseModel

class ScheduleRiskPredictionOut(BaseModel):
    id: UUID
    project_id: str
    prediction_date: date
    predicted_by: str
    risk_type: str
    affected_activity_id: Optional[UUID] = None
    probability: Decimal
    predicted_delay_days: int
    confidence_level: str
    contributing_factors: list[Any]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class SchedulePredictionResponse(BaseModel):
    project_id: str
    generated_at: datetime
    risk_count: int
    top_risks: list[ScheduleRiskPredictionOut]

class BudgetPredictionResponse(BaseModel):
    project_id: str
    forecast_health: str
    current_projected_final: Decimal
    current_variance_to_budget: Decimal
    additional_risk_exposure: Decimal
    risk_adjusted_projected_final: Decimal
    risk_adjusted_variance: Decimal
    confidence_level: str
    contributing_factors: list[dict[str, Any]]
```

---

## 6) SQLAlchemy Model

```python
class ScheduleRiskPrediction(Base):
    __tablename__ = "schedule_risk_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(Text, nullable=False, index=True)
    prediction_date = Column(Date, nullable=False, server_default=func.current_date())
    predicted_by = Column(Text, nullable=False, default="system")
    risk_type = Column(Text, nullable=False, index=True)
    affected_activity_id = Column(UUID(as_uuid=True), ForeignKey("cpm_activities.id", ondelete="SET NULL"), nullable=True)
    probability = Column(Numeric(5, 4), nullable=False)
    predicted_delay_days = Column(Integer, nullable=False, default=0)
    confidence_level = Column(Text, nullable=False, default="medium")
    contributing_factors = Column(JSONB, nullable=False, default=list)
    status = Column(Text, nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    __table_args__ = (
        CheckConstraint("risk_type IN ('material_delay','weather_impact','rfi_delay','vendor_risk','labor_shortage')", name="chk_schedule_risk_type"),
        CheckConstraint("confidence_level IN ('low','medium','high')", name="chk_schedule_risk_confidence"),
        CheckConstraint("status IN ('active','resolved','expired')", name="chk_schedule_risk_status"),
        CheckConstraint("probability >= 0.0 AND probability <= 1.0", name="chk_schedule_risk_probability"),
    )
```

---

## 7) FastAPI Endpoints

Router: `app/api/routers/predictive_intelligence.py`

```python
router = APIRouter(prefix="/predict", tags=["Predictive Intelligence"])

@router.get("/schedule/{project_id}", response_model=SchedulePredictionResponse)
def get_schedule_predictions(
    project_id: str,
    refresh: bool = True,
    db: Session = Depends(get_db),
):
    try:
        if refresh:
            predictions = generate_schedule_predictions(project_id=project_id, db=db)
        else:
            predictions = get_active_schedule_predictions(project_id=project_id, db=db)

        return SchedulePredictionResponse(
            project_id=project_id,
            generated_at=datetime.now(timezone.utc),
            risk_count=len(predictions),
            top_risks=predictions[:10],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate schedule predictions: {str(exc)}",
        )

@router.get("/budget/{project_id}", response_model=BudgetPredictionResponse)
def get_budget_prediction(
    project_id: str,
    db: Session = Depends(get_db),
):
    try:
        result = build_budget_exposure_forecast(project_id, db)
        if result is None:
            raise HTTPException(
                status_code=404,
                detail="No cost forecast or budget data found for project",
            )
        return result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
```

---

## 8) Mission Control Integration

### Top 3 Risks Per Project

```json
{
  "project_id": "101F",
  "predictive_intelligence": {
    "top_schedule_risks": [
      {
        "rank": 1,
        "risk_type": "material_delay",
        "summary": "Window delivery is expected after planned install start.",
        "probability": 0.90,
        "predicted_delay_days": 4,
        "confidence_level": "high",
        "affected_activity": "Window Install"
      },
      {
        "rank": 2,
        "risk_type": "rfi_delay",
        "summary": "RFI-014 is overdue and linked to critical path Interior Framing.",
        "probability": 0.85,
        "predicted_delay_days": 3,
        "confidence_level": "high",
        "affected_activity": "Interior Framing"
      },
      {
        "rank": 3,
        "risk_type": "weather_impact",
        "summary": "Concrete pour has RED weather alert in 2 days.",
        "probability": 0.80,
        "predicted_delay_days": 2,
        "confidence_level": "medium",
        "affected_activity": "Garage Slab Pour"
      }
    ],
    "budget_prediction": {
      "forecast_health": "YELLOW",
      "additional_risk_exposure": 42000.00,
      "risk_adjusted_projected_final": 5647000.00
    }
  }
}
```

---

## 9) n8n Workflows

### WF-PREDICT-001 Schedule Risk Refresh
**Schedule:** Daily 05:30 (before morning brief)

**Logic:**
1. For each active project: call `generate_schedule_predictions()`
2. Mark resolved predictions as `expired`
3. Refresh Mission Control summary
4. Surface high-probability predictions in morning brief

---

## 10) Prediction Lifecycle

| Status | Meaning |
|--------|---------|
| active | Risk is current and unresolved |
| resolved | Risk condition no longer exists (material delivered, RFI answered, etc.) |
| expired | Prediction date has passed without resolution |

**Auto-resolution rules:**
- material_delay: resolve when `long_lead_materials.status IN ('delivered','installed')`
- rfi_delay: resolve when `rfis.status IN ('answered','closed')`
- weather_impact: resolve when alert expires or activity date passes
- vendor_risk: resolve when vendor score improves above 6 OR PO is fulfilled

---

## 11) Tests Required

Claude Code should implement tests for:
1. Material delay risk detected for undelivered long-lead within 14 days
2. Material delay probability scales correctly by buffer
3. Weather impact detected for RED alert + concrete activity
4. RFI delay risk detected for overdue linked RFI
5. Vendor risk detected for score < 6 with active PO
6. Predictions sorted by probability descending
7. Resolved predictions excluded from active list
8. Budget exposure includes open RFI cost impacts
9. Risk-adjusted projected final = current + exposure
10. Mission Control top 3 risks correctly ranked

---

## 12) Definition of Done

Predictive Intelligence Phase 1 is complete when:
- [ ] `schedule_risk_predictions` table exists
- [ ] Rule-based schedule prediction service detects material, weather, RFI, vendor, and labor risks
- [ ] Budget exposure forecast returns risk-adjusted projected final cost
- [ ] FastAPI endpoints are implemented
- [ ] Mission Control shows top three predicted risks per project
- [ ] Morning Brief can include high-probability/high-impact predictions
- [ ] Resolved/expired predictions are excluded from active risk list
- [ ] Tests pass

---

## GBT Chief Architect Assessment

> "This is the transition from HCI AI OS as a reporting platform to HCI AI OS as an early-warning system."

---

*Spec committed by Browser Claude — Operations Intelligence*
*GBT Cycle 25 complete — Sprint 6 Priority 5 spec delivered*

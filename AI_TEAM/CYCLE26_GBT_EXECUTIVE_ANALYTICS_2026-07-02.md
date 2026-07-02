# CYCLE26 — Sprint 6 Priority 6: Executive Analytics Architecture
**Cycle:** 26
**Sprint:** 6
**Priority:** 6
**Date:** 2026-07-02
**Author:** GBT (HCI Chief Architect)
**Status:** SPEC COMPLETE — Ready for Code Implementation

---

## Overview

The Executive layer is the final layer of HCI AI OS.

Everyone else uses the system to **enter, manage, and analyze** information.

Buck should use it to **make decisions.**

He should never need to ask:
- "What's going on today?"
- "Which project needs me?"
- "Am I over budget?"
- "What is slipping?"

The system should answer those questions before he asks.

---

## Design Principles

- Buck's time is the most valuable resource in HCI
- Every briefing should be under 5 minutes to consume
- Never show raw data — show synthesized intelligence
- Every number should have a direction (better, worse, stable)
- Every risk should have an owner or action
- The morning brief is the most important feature

---

## 1) PostgreSQL DDL — executive_morning_brief

```sql
CREATE TABLE IF NOT EXISTS executive_morning_brief (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    project_id TEXT NOT NULL,

    brief_date DATE NOT NULL,

    generated_at TIMESTAMPTZ NOT NULL,

    health_summary TEXT NOT NULL,
    -- Human-readable, written for Buck
    -- Example: "101F is healthy. 1355R needs your attention on window buyout."

    top_risks JSONB NOT NULL DEFAULT '[]'::jsonb,
    -- Top 3 from schedule_risk_predictions
    -- [{rank, risk_type, summary, probability, predicted_delay_days, affected_activity}]

    decisions_needed JSONB NOT NULL DEFAULT '[]'::jsonb,
    -- Pending approvals + client decisions
    -- [{type: "approval|client_decision", title, deadline, source}]

    budget_status JSONB NOT NULL DEFAULT '{}'::jsonb,
    -- {health, variance_dollars, variance_percent, projected_final}

    schedule_status JSONB NOT NULL DEFAULT '{}'::jsonb,
    -- {critical_path_health, variance_days, next_milestone, next_milestone_date}

    notable_activities TEXT,
    -- Optional: "Framing complete. Three inspections passed."

    generated_by TEXT NOT NULL DEFAULT 'WF-BRIEF-001',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_executive_brief_project_date
        UNIQUE (project_id, brief_date)
);

CREATE INDEX IF NOT EXISTS idx_executive_brief_project_id
    ON executive_morning_brief(project_id);

CREATE INDEX IF NOT EXISTS idx_executive_brief_date
    ON executive_morning_brief(brief_date DESC);
```

---

## 2) PostgreSQL DDL — executive_kpis

```sql
CREATE TABLE IF NOT EXISTS executive_kpis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    project_id TEXT NOT NULL,

    kpi_date DATE NOT NULL,

    days_to_estimated_completion INTEGER,

    schedule_variance_days INTEGER,
    -- negative = ahead, positive = behind

    budget_variance_dollars NUMERIC(14,2),
    -- negative = under budget, positive = over budget

    budget_variance_percent NUMERIC(8,4),

    open_rfis INTEGER NOT NULL DEFAULT 0,

    overdue_rfis INTEGER NOT NULL DEFAULT 0,

    open_punch_items INTEGER NOT NULL DEFAULT 0,

    critical_punch_items INTEGER NOT NULL DEFAULT 0,

    photos_this_week INTEGER NOT NULL DEFAULT 0,

    pending_client_decisions INTEGER NOT NULL DEFAULT 0,

    vendor_risk_flags INTEGER NOT NULL DEFAULT 0,
    -- count of vendors with score < 6 on active POs

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_executive_kpis_project_date
        UNIQUE (project_id, kpi_date)
);

CREATE INDEX IF NOT EXISTS idx_executive_kpis_project_id
    ON executive_kpis(project_id);

CREATE INDEX IF NOT EXISTS idx_executive_kpis_date
    ON executive_kpis(kpi_date DESC);
```

---

## 3) Morning Brief Generation — WF-BRIEF-001

### Schedule

Daily at **06:30** — before Buck's working day starts at 7:00 AM.
(Note: Superintendents on site at 7:00 AM — brief must be ready before then.)

### Generation Steps

**Step 1 — Load Active Projects**
```
SELECT all projects WHERE status = 'active'
```

**Step 2 — Project Health**

Read:
- LIVE_PROJECT_STATE
- Project Brain
- Latest project status

Generate:
- GREEN (healthy, no flags)
- YELLOW (one or more warnings)
- RED (immediate attention required)

With one-sentence explanation.

**Step 3 — Predictive Intelligence**

Call: `GET /predict/schedule/{project}`

Return: Top three predicted risks with probability, delay, activity.

**Step 4 — Budget Status**

Call: `GET /predict/budget/{project}`

Return: Health, variance, risk-adjusted forecast.

**Step 5 — Schedule Status**

Read: `cpm_activities` for critical path status and next milestone.

**Step 6 — Decisions Required Today**

Query:
- Approval Queue (status = pending, deadline <= today + 3 days)
- Client Decisions (status = pending, deadline <= today + 3 days)
- Outstanding Buck approvals

Return: "Decisions Required Today" list.

**Step 7 — RFIs**

Summarize:
- open
- overdue
- critical

**Step 8 — Procurement**

Check:
- long lead items
- delayed materials
- critical deliveries

**Step 9 — Notable Activities (optional)**

Pull any milestones completed, inspections passed, safety record, and positive progress notes from daily field reports.

**Step 10 — Write Health Summary**

Write one paragraph in plain English summarizing the project:
- What is going well
- What needs Buck's attention
- What risks exist
- What decisions are needed

Not JSON. Not data. A brief.

**Step 11 — Store and Notify**

Store in `executive_morning_brief`.
Update `executive_kpis`.
Notify Buck via Telegram (when active) or Mission Control.

---

## 4) Executive Brief Format

Buck should never receive raw JSON.

He should receive something like:

```
Morning Brief
Thursday, July 2

Portfolio
🟢 3 Healthy
🟡 1 Needs Attention
🔴 0 Critical

Decisions Requiring Your Input (3)
— Approve Window Buyout — 101F (today)
— Review bid for 64EW framing — due Friday
— 2 owner decisions pending

Project: 101 Francis (101F) — YELLOW
Budget: $5.6M projected | $135K over | +2.5%
Schedule: On track | Framing 8/15
Risks:
  • Windows arriving late — 4-day delay predicted (HIGH)
  • RFI-014 overdue, Interior Framing at risk (HIGH)

Project: 64 Eastwood (64EW) — GREEN
Budget: $2.1M projected | Under budget $22K
Schedule: Ahead 2 days
Risks: None active

Weather
Roofing safe
Concrete delay Thursday

Good News
Framing completed
Three inspections passed
No safety incidents yesterday

One screen.
Five minutes.
Done.
```

---

## 5) JSON Structure for API Response

```json
{
  "project_id": "101F",
  "brief_date": "2026-07-02",
  "health_summary": "101F has a predicted 4-day delay from window delivery and an overdue RFI on critical path. Budget is YELLOW at +$135K. Window buyout approval is required today.",
  "health": "YELLOW",
  "top_risks": [
    {
      "rank": 1,
      "risk_type": "material_delay",
      "summary": "Marvin windows expected after install start",
      "probability": 0.90,
      "predicted_delay_days": 4,
      "confidence": "high"
    }
  ],
  "decisions_needed": [
    {
      "type": "approval",
      "title": "Approve Window Buyout",
      "deadline": "2026-07-02"
    }
  ],
  "budget_status": {
    "health": "YELLOW",
    "variance": 135000.00,
    "projected_final": 5605000.00
  },
  "schedule_status": {
    "critical_path": "Healthy",
    "variance_days": -2
  }
}
```

---

## 6) FastAPI Endpoints

Router: `app/api/routers/executive.py`

```python
router = APIRouter(prefix="/executive", tags=["Executive Analytics"])

@router.get("/morning-brief/{project_id}")
def get_morning_brief(project_id: str, db: Session = Depends(get_db)):
    brief = (
        db.query(ExecutiveMorningBrief)
        .filter(
            ExecutiveMorningBrief.project_id == project_id,
            ExecutiveMorningBrief.brief_date == date.today(),
        )
        .first()
    )
    if not brief:
        raise HTTPException(status_code=404, detail="No brief generated for today yet")
    return brief

@router.get("/kpis/{project_id}")
def get_project_kpis(project_id: str, days: int = 30, db: Session = Depends(get_db)):
    cutoff = date.today() - timedelta(days=days)
    return (
        db.query(ExecutiveKPI)
        .filter(
            ExecutiveKPI.project_id == project_id,
            ExecutiveKPI.kpi_date >= cutoff,
        )
        .order_by(ExecutiveKPI.kpi_date.desc())
        .all()
    )

@router.get("/portfolio-summary")
def get_portfolio_summary(db: Session = Depends(get_db)):
    # Returns today's briefs for all active projects
    # Computes portfolio-level health summary
    today = date.today()
    briefs = (
        db.query(ExecutiveMorningBrief)
        .filter(ExecutiveMorningBrief.brief_date == today)
        .all()
    )
    return build_portfolio_summary(briefs)
```

---

## 7) Portfolio Health Calculation

Project Health should be derived rather than manually assigned.

**Suggested precedence:**

1. Any critical predictive risk with probability ≥ 0.8 and delay ≥ 3 days → **RED**
2. Budget variance ≥ 5% or schedule variance beyond configured threshold → **RED**
3. Otherwise, any significant warning (predictive, budget, schedule, overdue RFIs, critical punch items, vendor risk) → **YELLOW**
4. Otherwise → **GREEN**

This keeps the portfolio status explainable and consistent.

---

## 8) KPI Trend Tracking

`executive_kpis` should be populated daily.

Trend direction for each KPI:
- Compare today vs 7 days ago
- Compute delta
- Label: improving / stable / worsening

**KPI Health Thresholds:**

| KPI | Warning | Critical |
|-----|---------|---------|
| schedule_variance_days | > 2 days | > 5 days |
| budget_variance_percent | > 2% | > 5% |
| overdue_rfis | > 2 | > 5 |
| critical_punch_items | > 0 | > 3 |
| vendor_risk_flags | > 1 | > 3 |

---

## 9) Portfolio Summary Output

A portfolio header should summarize:
- Active projects
- RED / YELLOW / GREEN counts
- Total approvals awaiting Buck
- Total predicted schedule impact across the portfolio
- Aggregate budget variance
- Highest-priority decision today

---

## 10) Future Enhancements

Once enough historical data exists, Executive Analytics can expand to include:
- Trend charts over weeks and months
- Portfolio forecast (cash flow, schedule confidence)
- "What changed since yesterday?" summaries
- Cross-project benchmarking
- AI-generated recommended actions with links back to Project Brain
- Role-specific executive digests (Owner, COO, PM, Director)

---

## 11) Tests Required

Claude Code should implement tests for:
1. Create daily executive brief
2. Reject duplicate brief for same project/date
3. Morning brief returns today's record
4. KPIs populate correctly from operational data
5. Portfolio summary aggregates all active projects
6. Portfolio health RED when predictive risk ≥ 0.8 and delay ≥ 3 days
7. Portfolio health YELLOW for budget variance ≥ 2%
8. Decisions list populated from approval queue + client decisions
9. KPI trend shows improving/stable/worsening correctly
10. Brief generated before 7:00 AM (WF-BRIEF-001 timing test)

---

## 12) Definition of Done

Executive Analytics Phase 1 is complete when:
- [ ] `executive_morning_brief` and `executive_kpis` tables exist
- [ ] WF-BRIEF-001 generates a morning brief for every active project before the business day
- [ ] `/executive/morning-brief/{project_id}`, `/executive/kpis/{project_id}`, and `/executive/portfolio-summary` are implemented
- [ ] Portfolio health is derived from transparent rules
- [ ] Mission Control presents a concise portfolio view with actionable insights rather than raw data
- [ ] KPI trends are available
- [ ] Tests pass

---

## GBT Chief Architect Assessment

> "Buck's daily interaction with HCI AI OS shifts from searching for information to reviewing a short, prioritized briefing that highlights the decisions only he can make. That is the intended executive experience."

---

## Sprint 6 Complete

| Priority | Capability | Cycle | Status |
|----------|-----------|-------|--------|
| 1 | Project Brain 2.0 (Knowledge Graph) | 21 | ✅ SPEC COMPLETE |
| 2 | Vendor Intelligence Engine | 22 | ✅ SPEC COMPLETE |
| 3 | Client Portal (Luxury Experience) | 23 | ✅ SPEC COMPLETE |
| 4 | Mobile Field UX (Voice-First, Offline) | 24 | ✅ SPEC COMPLETE |
| 5 | Predictive Intelligence | 25 | ✅ SPEC COMPLETE |
| 6 | Executive Analytics | 26 | ✅ SPEC COMPLETE |

**Sprint 6 is 100% SPEC COMPLETE.**

---

*Spec committed by Browser Claude — Operations Intelligence*
*GBT Cycle 26 complete — Sprint 6 Priority 6 spec delivered*
*Sprint 6: ALL 6 PRIORITIES COMPLETE*

# HCI AI — KPI and Executive Intelligence Standard

**Version:** 1.0 | **Date:** 2026-06-25 | **Directive:** HCI_AI_Business_Operating_Layer_BOOK01_Decision_KPI_Master_Directive_v1.0

---

## Purpose

This document defines the KPI data model, calculation rules, threshold behavior, and API contract for the KPI Intelligence service. All KPI thresholds are configurable in the Operating Rules Engine — not hardcoded here.

---

## KPI Data Model

### PostgreSQL Table: `kpi_snapshots`

```sql
CREATE TABLE kpi_snapshots (
    id              SERIAL PRIMARY KEY,
    kpi_code        VARCHAR(50) NOT NULL,
    scope           VARCHAR(10) NOT NULL CHECK (scope IN ('company', 'project')),
    project_id      INTEGER REFERENCES projects(id),  -- null if scope='company'
    value           NUMERIC(15,4) NOT NULL,
    unit            VARCHAR(20),           -- %, days, $, count
    period_start    DATE NOT NULL,
    period_end      DATE NOT NULL,
    status          VARCHAR(10) NOT NULL CHECK (status IN ('green', 'yellow', 'red', 'none')),
    threshold_low   NUMERIC(15,4),         -- yellow threshold
    threshold_high  NUMERIC(15,4),         -- red threshold
    source_service  VARCHAR(50),           -- which service calculated this
    calculated_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_kpi_snapshots_code ON kpi_snapshots(kpi_code);
CREATE INDEX idx_kpi_snapshots_project ON kpi_snapshots(project_id);
CREATE INDEX idx_kpi_snapshots_date ON kpi_snapshots(period_end);
```

---

## Company-Level KPI Definitions

| KPI Code | Name | Unit | Calculation | Yellow | Red | Source |
|----------|------|------|-------------|--------|-----|--------|
| `BID_WIN_RATE` | Bid Win Rate | % | wins / total bids (rolling 12 mo) | < 25% | < 15% | bid_intelligence |
| `BID_MARGIN_AVG` | Average Bid Margin | % | avg margin on submitted bids (rolling 12 mo) | < 7% | < 5% | bid_intelligence |
| `REVENUE_AT_RISK` | Revenue at Risk | % of backlog | sum of red-flag projects / total backlog | > 10% | > 20% | budget + risk |
| `CO_REVENUE_PCT` | CO Revenue as % of Contract | % | total approved CO value / original contract | > 6% | > 10% | change_orders |
| `CLOSEOUT_AVG_DAYS` | Avg Closeout Days from SC | days | avg (closeout_date - SC_date) | > 30 | > 60 | closeout_tracker |
| `SUB_NONCOMPLIANCE` | Sub Non-Compliance Events | count | count of compliance gates failed | > 0 | > 2 | procurement |
| `MARGIN_VARIANCE` | Project Margin vs. Bid Margin | % pts | avg (final_margin - bid_margin) | > 2 pts below | > 4 pts below | budget_vs_actual |
| `ON_TIME_COMPLETION` | Project On-Time Rate | % | projects completing on/before contract date / total | < 85% | < 70% | schedule_tracker |

---

## Project-Level KPI Definitions

| KPI Code | Name | Unit | Calculation | Yellow | Red | Source |
|----------|------|------|-------------|--------|-----|--------|
| `BUDGET_VAR_MAX` | Max Budget Variance (any line) | % | max variance across all scope lines | > 5% | > 10% | project_budgets |
| `BUDGET_VAR_TOTAL` | Total Project Budget Variance | % | (budget - current_cost_at_complete) / budget | > 3% | > 7% | project_budgets |
| `SCHED_VAR_DAYS` | Schedule Variance (critical path) | days | actual_progress vs. planned_progress on CP | > 3 | > 7 | schedule_intelligence |
| `OPEN_RFI_AGE` | Oldest Open RFI | days | max(today - submitted_date) for open RFIs | > 10 | > 14 | rfis |
| `LOG_COMPLETION` | Daily Log Completion Rate | % | logs submitted / working days in period | < 95% | < 85% | daily_logs |
| `CO_PENDING_DAYS` | Oldest Pending Change Order | days | max(today - identified_date) for pending COs | > 7 | > 14 | change_orders |
| `PUNCH_OPEN_AGE` | Oldest Open Punch Item | days | max(today - created_date) for open punch items | > 20 | > 30 | punch_items |
| `SUB_COMPLIANCE` | Sub Compliance on Site | % | compliant subs / total active subs | < 100% | < 95% | procurement |

---

## KPI Calculation Schedule

| Frequency | KPIs Recalculated | Trigger |
|-----------|-------------------|---------|
| Real-time | Budget variance, compliance gates | On data change |
| Daily (6 AM) | All project-level KPIs | Cron job |
| Weekly (Friday noon) | All company-level KPIs | Cron job |
| Monthly (1st) | Trend analysis, rolling averages | Cron job |

---

## Threshold Behavior

When a KPI crosses a threshold:

1. `kpi_snapshots` record is written with `status = 'yellow'` or `'red'`
2. Operating Rules Engine evaluates the KPI code against alert rules
3. If alert rule matches: notification sent to configured recipients
4. Alert appears in morning brief (if project-level) or executive summary (if company-level)
5. Alert remains active in dashboard until KPI returns to green or is manually acknowledged with reason

---

## API Contract

### `GET /api/v1/kpis/company`
Returns current company-level KPI snapshot: all codes, values, status, trend direction.

### `GET /api/v1/kpis/project/{project_id}`
Returns current project-level KPI snapshot for specified project.

### `GET /api/v1/kpis/alerts`
Returns all currently active KPI threshold breaches (yellow or red) across all projects.

Response:
```json
{
  "alerts": [
    {
      "kpi_code": "OPEN_RFI_AGE",
      "project_id": 2,
      "project_name": "101 Francis",
      "value": 16,
      "unit": "days",
      "status": "red",
      "threshold": 14,
      "action_required": "PM to follow up on RFI-007 immediately"
    }
  ]
}
```

### `GET /api/v1/kpis/trend?kpi_code={code}&project_id={id}&period_days={n}`
Returns historical KPI values for trend chart. `project_id` optional — omit for company-level.

---

## Executive Dashboard Assembly

The executive dashboard calls `/api/v1/kpis/company` + `/api/v1/kpis/alerts` + one `/api/v1/kpis/project/{id}` per active project. The dashboard assembles:
- Company header row (all company KPIs with traffic lights)
- Project card grid (one card per active project — budget, schedule, compliance lights)
- Alert feed (all red items requiring action)
- Trend sparklines (last 12 weeks)

---

*Service: `03_Source_Code/services/kpi_intelligence/`*  
*BOOK_01 Volume 13: `BOOK_01/13_KPI_AND_EXECUTIVE_INTELLIGENCE.md`*  
*Thresholds: `03_Source_Code/services/operating_rules/`*

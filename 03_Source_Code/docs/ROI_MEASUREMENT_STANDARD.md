# ROI Measurement Standard

**Table:** `roi_log`  
**Endpoint:** `GET /api/v1/mvp/roi-summary`  

---

## Purpose

Every workflow run logs ROI data. This lets Buck see exactly how much time HCI AI is saving across all projects and workflows — in real numbers, not estimates.

---

## Schema

```sql
CREATE TABLE roi_log (
    id                    SERIAL PRIMARY KEY,
    workflow              VARCHAR(100) NOT NULL,
    project_id            INTEGER REFERENCES projects(id),
    project_code          VARCHAR(50),
    baseline_minutes      NUMERIC(8,2) DEFAULT 0,
    ai_assisted_minutes   NUMERIC(8,2) DEFAULT 0,
    minutes_saved         NUMERIC(8,2) GENERATED ALWAYS AS (baseline_minutes - ai_assisted_minutes) STORED,
    steps_removed         INTEGER DEFAULT 0,
    documents_processed   INTEGER DEFAULT 0,
    errors_caught         INTEGER DEFAULT 0,
    missing_scope_found   INTEGER DEFAULT 0,
    schedule_risks_detected INTEGER DEFAULT 0,
    reporting_time_saved_min NUMERIC(8,2) DEFAULT 0,
    notes                 TEXT,
    actor                 VARCHAR(100) DEFAULT 'system',
    created_at            TIMESTAMPTZ DEFAULT NOW()
);
```

`minutes_saved` is a PostgreSQL `GENERATED ALWAYS AS` computed column — never set it directly.

---

## Per-Workflow Baselines

| Workflow              | baseline_min | ai_min | saved |
|-----------------------|-------------|--------|-------|
| project_brain_init    | 30          | 2      | 28    |
| bid_management        | 45          | 3      | 42    |
| daily_log             | 30          | 3      | 27    |
| pm_weekly_review      | 90          | 3      | 87    |
| schedule_status       | 30          | 2      | 28    |
| executive_report      | 60          | 1      | 59    |

These are conservative estimates based on actual manual process timing.

---

## ROI Summary Endpoint

`GET /api/v1/mvp/roi-summary?project_code=101F`

Returns:
```json
{
  "project_code": "101F",
  "total_runs": 24,
  "total_baseline_minutes": 1080,
  "total_ai_minutes": 48,
  "total_minutes_saved": 1032,
  "total_steps_removed": 120,
  "total_schedule_risks_detected": 3,
  "by_workflow": [...]
}
```

---

## How Baselines Were Set

Each baseline represents the real manual process:
- **Project Brain Init (30 min):** Open HubSpot + Drive + Houzz + 2 internal reports, cross-reference, format
- **Bid Management (45 min):** Receive bid, enter into tracker, validate scope, flag issues, file
- **Daily Log (30 min):** Write up log, enter into system, manually scan for risks, file
- **PM Weekly Review (90 min):** Pull 5 systems, compile metrics, write status memo
- **Schedule Status (30 min):** Review schedule, compare actuals, identify variances, document
- **Executive Report (60 min):** Pull PM reports from all 3 projects, synthesize, format

---

## Sprint-Level ROI

`GET /api/v1/mvp/sprint-status` returns `total_minutes_saved` across all workflow runs in the session.

Projected annual savings (1355R alone, daily use): ~8,000+ minutes = ~133+ hours.

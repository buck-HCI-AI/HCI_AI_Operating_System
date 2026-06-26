# PM Weekly Review Workflow

**Workflow 4: PM Weekly Review**  
**Endpoint:** `GET /api/v1/mvp/projects/{code}/pm-weekly-review`  
**Mode:** Read-only  

---

## Purpose

Synthesize the week's construction data across bid packages, daily logs, risks, RFIs, submittals, and schedule variance into a single health status report. Replaces 60–90 minutes of manual data aggregation with a 2-minute AI pull.

---

## Data Sources Queried

| Table               | Data Retrieved                                           |
|---------------------|----------------------------------------------------------|
| `bid_packages`      | Total / active / closed bids                             |
| `daily_logs`        | Last 7 logs (work performed, constraints, safety)        |
| `risks`             | Open risks with type, description, severity              |
| `rfis`              | Open RFIs                                                |
| `submittals`        | Pending (not approved/closed)                            |
| `schedule_variance` | Recent variance items (detected_at, risk_level, cause)   |

---

## Health Status Logic

| Condition                          | Status  |
|------------------------------------|---------|
| No issues                          | green   |
| open_risks > 3                     | yellow  |
| open_rfis > 2                      | yellow  |
| schedule_variance items exist      | yellow  |
| No daily logs in 7 days            | yellow  |
| Critical schedule variance (high/critical risk_level) | red |

---

## Response Example

```json
{
  "project": "1355 Riverside",
  "project_code": "1355R",
  "period": "Last 7 days",
  "health": "yellow",
  "alerts": ["2 schedule variance items", "No daily logs in 7 days"],
  "bid_packages": {"total": 12, "active": 8, "closed": 4},
  "open_risks": 2,
  "open_rfis": 1,
  "pending_submittals": 3,
  "schedule_variance_items": 2,
  "recent_logs_count": 0,
  "mode": "read_only",
  "roi": {
    "baseline_minutes": 90,
    "ai_minutes": 3,
    "saved": 87
  }
}
```

---

## ROI Baseline

| Metric          | Manual | AI-Assisted | Saved |
|-----------------|--------|-------------|-------|
| Minutes per run | 90     | 3           | 87    |
| Steps removed   | 12     |             |       |

Manual: open 5 separate systems, pull reports, cross-reference, write summary. AI: one call returns synthesized health status.

---

## Run Frequency

Recommended: weekly (Monday AM) per project. Buck reviews health status and opens any red/yellow alerts.

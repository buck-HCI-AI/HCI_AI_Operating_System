# Executive Reporting MVP

**Workflow 6: Executive Reporting**  
**Endpoint:** `GET /api/v1/mvp/executive-report`  
**Mode:** Read-only  

---

## Purpose

One-call executive summary across all 3 pilot projects. Returns health status, risk totals, RFI counts, and ROI for Buck's morning briefing or board reporting.

---

## What It Does

Runs Project Brain init for all 3 pilot projects simultaneously and synthesizes a cross-project summary with:
- Per-project health (green/yellow/red)
- Portfolio-level risk count
- Total open RFIs
- Total schedule variance items
- ROI savings across all projects

---

## Response Example

```json
{
  "as_of": "2026-06-26T08:00:00Z",
  "pilot_projects": ["64EW", "101F", "1355R"],
  "projects": {
    "64EW": {
      "name": "64 Eastwood",
      "health": "green",
      "open_risks": 0,
      "open_rfis": 0,
      "schedule_variance_items": 0
    },
    "101F": {
      "name": "101 Francis",
      "health": "yellow",
      "open_risks": 2,
      "open_rfis": 1,
      "schedule_variance_items": 1
    },
    "1355R": {
      "name": "1355 Riverside",
      "health": "green",
      "open_risks": 0,
      "open_rfis": 0,
      "schedule_variance_items": 0
    }
  },
  "summary": {
    "total_open_risks": 2,
    "total_open_rfis": 1,
    "total_schedule_variance_items": 1,
    "projects_at_risk": ["101F"],
    "projects_on_track": ["64EW", "1355R"]
  },
  "mode": "read_only",
  "roi": {
    "baseline_minutes": 60,
    "ai_minutes": 1,
    "saved": 59,
    "note": "Replaces pulling 3 separate PM status reports"
  }
}
```

---

## ROI Baseline

| Metric              | Manual | AI-Assisted | Saved |
|---------------------|--------|-------------|-------|
| Minutes per report  | 60     | 1           | 59    |
| Steps removed       | 15     |             |       |

Manual: log into each system per project, pull status reports, compare data, format summary. AI: one endpoint call.

---

## Run Frequency

Recommended: daily AM (7–8am) as morning briefing. Can be added to a cron for automatic generation.

# Project Brain Pilot Setup

**MVP Sprint 1 — Pilot Configuration**  
**Projects:** 64 Eastwood, 101 Francis, 1355 Riverside  

---

## What is Project Brain Init?

Workflow 1: Project Brain Init queries the DB for all baseline data on a project and returns it in a single structured response. Used as the starting point for all other workflows.

Endpoint: `GET /api/v1/mvp/projects/{code}/init`

---

## Setup Checklist per Project

### 1. DB Record Exists
The project must exist in the `projects` table. Current pilot IDs:

| Code  | DB ID | Name            |
|-------|-------|-----------------|
| 64EW  | 1     | 64 Eastwood     |
| 101F  | 2     | 101 Francis     |
| 1355R | 3     | 1355 Riverside  |

### 2. Connector Registry Initialized
Run once: `POST /api/v1/services/connector-registry/init-pilots`

Registers 9 connectors (3 per project: hubspot, google_drive, houzz), all read_only=True.

### 3. Background Learning Discovery
Run: `POST /api/v1/services/background-learning/discover/all`

Scans hubspot_deals, drive_sync_log, and houzz_projects tables and registers any matching records.

### 4. Validate with Sprint Status
Check: `GET /api/v1/mvp/sprint-status`

Confirms connector registry, background learning pipeline, and approval queue are all active.

---

## Project Brain Init Response

```json
{
  "project": "101 Francis",
  "project_code": "101F",
  "project_id": 2,
  "as_of": "2026-06-26T...",
  "bid_packages": {...},
  "daily_log_count": 0,
  "open_risks": 0,
  "open_rfis": 0,
  "pending_submittals": 0,
  "schedule_variance_items": 0,
  "workflows_available": ["bid_management", "daily_log", "pm_weekly_review", ...],
  "mode": "read_only",
  "roi": {
    "baseline_minutes": 30,
    "ai_minutes": 2,
    "saved": 28
  }
}
```

---

## ROI Baseline: Project Brain Init

| Metric          | Manual | AI-Assisted | Saved |
|-----------------|--------|-------------|-------|
| Minutes per run | 30     | 2           | 28    |
| Steps removed   | 8      |             |       |

Manual process: open HubSpot, open Drive, open Houzz, pull 5 separate reports, cross-reference, format summary. AI: one API call.

---

## Next Steps After Init

1. Run Daily Log workflow to capture field data
2. Run PM Weekly Review for health status
3. Run Schedule/Status Intelligence for variance detection
4. Review Background Learning pipeline for new intelligence candidates
5. Review Approval Queue for any queued write actions

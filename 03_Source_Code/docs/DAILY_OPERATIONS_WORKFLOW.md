# Daily Operations Workflow

**Workflow 3: Daily Log + Field Intelligence**  
**Endpoint:** `POST /api/v1/mvp/projects/{code}/daily-log`  
**Mode:** Dry-run (default) or queue for approval  

---

## Purpose

Capture field data from the job site and run automatic field intelligence analysis — detecting delays, weather impacts, safety flags, and schedule risks from daily log notes without manual review.

---

## Request Body

```json
{
  "date": "2026-06-26",
  "crew_size": 8,
  "work_performed": "Framing north wall — delayed due to lumber delivery issue",
  "schedule_progress": "North wall pour complete",
  "weather": "Clear, 72F",
  "constraints": "Material delivery delayed 2 hours",
  "safety_notes": "All crew PPE compliant",
  "dry_run": true
}
```

---

## Field Intelligence Detection

The AI analyzes `work_performed`, `constraints`, and `safety_notes` for:

| Signal           | Keywords                                          | Risk Level |
|------------------|---------------------------------------------------|------------|
| Delay            | delayed, delay, waiting, behind, slow             | schedule   |
| Weather impact   | rain, wind, storm, weather, hold                  | schedule   |
| Safety flag      | incident, injury, unsafe, hazard, OSHA            | safety     |
| Missing material | material, delivery, lumber, concrete, no supply   | schedule   |
| Scope gap        | not in scope, extra, change, unforeseen           | cost       |

---

## Dry-Run Response

```json
{
  "project": "101 Francis",
  "mode": "dry_run",
  "proposed_log": {
    "project_id": 2,
    "log_date": "2026-06-26",
    "crew_size": 8,
    "work_performed": "...",
    "weather": "Clear, 72F",
    "constraints": "...",
    "safety_notes": "..."
  },
  "intelligence": {
    "delays_detected": ["delayed due to lumber delivery issue"],
    "weather_impacts": [],
    "safety_flags": [],
    "schedule_risks": ["lumber delivery delay"],
    "missing_scope": [],
    "action_items": ["Follow up on lumber delivery ETA"]
  },
  "roi": {
    "baseline_minutes": 30,
    "ai_minutes": 3,
    "saved": 27
  }
}
```

---

## Live Mode (dry_run=false)

When `dry_run=false`, the log entry is NOT written directly. Instead, it is placed in the approval queue:

```json
{
  "queue_id": 42,
  "status": "pending",
  "message": "Action queued for Buck approval. No changes made to database."
}
```

Buck reviews and approves in the approval queue before any data is written.

---

## ROI Baseline

| Metric          | Manual | AI-Assisted | Saved |
|-----------------|--------|-------------|-------|
| Minutes per run | 30     | 3           | 27    |
| Steps removed   | 5      |             |       |

Manual: write up log in notebook, type into system, manually flag issues. AI: speak or type once, analysis runs automatically.

---

## Daily Log Schema

Table: `daily_logs`  
Key columns: `log_date` (not `date`), `work_performed` (not `notes`), `crew_size`, `weather`, `constraints`, `safety_notes`

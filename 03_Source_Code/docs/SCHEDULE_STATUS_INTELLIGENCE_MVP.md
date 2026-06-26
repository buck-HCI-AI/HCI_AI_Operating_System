# Schedule / Status Intelligence MVP

**Workflow 5: Schedule/Status Intelligence**  
**Endpoint:** `GET /api/v1/mvp/projects/{code}/schedule-status`  
**Mode:** Read-only  

---

## Purpose

Detect schedule status changes, variance items, and decision points from existing data — without requiring anyone to manually check multiple systems. Returns an overall project status with actionable intelligence.

---

## Data Sources Queried

| Table               | Columns Used                                          |
|---------------------|-------------------------------------------------------|
| `schedule_variance` | `detected_at`, `risk_level`, `cause`, `decision_needed`, `activity_name`, `variance_days` |
| `daily_logs`        | `log_date`, `constraints`, `safety_notes`             |
| `risks`             | `risk_type`, `description`, `severity`, `status`      |
| `rfis`              | `total`, `open_count`                                 |

---

## Overall Status Logic

| Condition                                        | Status          |
|--------------------------------------------------|-----------------|
| No variance, no risks, no open RFIs              | on_track        |
| Variance items with risk_level = high/critical   | at_risk         |
| open_risks > 3 OR open_rfis > 3                 | needs_attention |

---

## Response Example

```json
{
  "project": "1355 Riverside",
  "project_code": "1355R",
  "as_of": "2026-06-26T...",
  "overall_status": "on_track",
  "schedule_variance_items": 0,
  "critical_items": [],
  "decision_needed": [],
  "open_risks": [],
  "rfi_summary": {"total": 0, "open_count": 0},
  "recent_constraints": [],
  "mode": "read_only",
  "roi": {
    "baseline_minutes": 30,
    "ai_minutes": 2,
    "saved": 28
  }
}
```

---

## Schedule Variance Schema

Table: `schedule_variance`  
Key: `detected_at` (timestamp) — NOT `created_at`  
Risk levels: `low`, `medium`, `high`, `critical`  
`decision_needed` field: text description of what decision is required, or NULL  

---

## ROI Baseline

| Metric              | Manual | AI-Assisted | Saved |
|---------------------|--------|-------------|-------|
| Minutes per run     | 30     | 2           | 28    |
| Steps removed       | 6      |             |       |
| Risks auto-detected | Manual | Auto        | —     |

---

## Run Frequency

Recommended: daily for active projects, or triggered by new daily log submission.

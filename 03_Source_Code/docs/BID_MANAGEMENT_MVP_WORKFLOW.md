# Bid Management MVP Workflow

**Workflow 2: Bid Management**  
**Endpoint:** `POST /api/v1/mvp/projects/{code}/bids/import`  
**Mode:** Dry-run (default) or queue for approval  

---

## Purpose

Import and validate a new bid package, auto-detect missing scope, flag pricing anomalies, and queue the record for approval before any write to the DB.

---

## Request Body

```json
{
  "vendor_name": "Acme Framing",
  "trade": "Framing",
  "bid_amount": 85000,
  "scope_description": "Rough framing all floors per plans",
  "submission_date": "2026-06-25",
  "dry_run": true
}
```

---

## Validation Rules

| Check                    | Condition                           | Flag               |
|--------------------------|-------------------------------------|--------------------|
| Missing vendor           | `vendor_name` is blank              | validation_error   |
| Missing trade            | `trade` is blank                    | validation_error   |
| Zero bid                 | `bid_amount` <= 0                   | validation_error   |
| Scope too short          | `scope_description` < 20 chars      | scope_warning      |
| High bid                 | `bid_amount` > 500,000              | pricing_flag       |

---

## Dry-Run Response

```json
{
  "project": "101 Francis",
  "mode": "dry_run",
  "proposed_bid": {
    "project_id": 2,
    "vendor_name": "Acme Framing",
    "trade": "Framing",
    "amount": 85000,
    "scope_description": "...",
    "status": "received"
  },
  "validation": {
    "passed": true,
    "warnings": [],
    "flags": []
  },
  "intelligence": {
    "missing_scope_detected": [],
    "pricing_anomalies": []
  },
  "roi": {
    "baseline_minutes": 45,
    "ai_minutes": 3,
    "saved": 42
  }
}
```

---

## Live Mode (dry_run=false)

Queues bid to `approval_queue` — does NOT write to `bid_packages`:

```json
{
  "queue_id": 43,
  "status": "pending",
  "message": "Action queued for Buck approval. No changes made to database."
}
```

After Buck approves, the bid is written to `bid_packages`.

---

## ROI Baseline

| Metric            | Manual | AI-Assisted | Saved |
|-------------------|--------|-------------|-------|
| Minutes per bid   | 45     | 3           | 42    |
| Steps removed     | 7      |             |       |
| Missing scope found | Manual hunt | Auto-flagged | — |

---

## Bid Package Schema

Table: `bid_packages`  
Key columns: `project_id`, `vendor_name`, `trade`, `amount`, `scope_description`, `status`, `submission_date`

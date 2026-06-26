# BOOK 01 — Chapter 19: Daily Operations Using HCI AI

**For:** Buck Adams / HCI Field & PM Use  
**Sprint:** MVP Sprint 1  
**Status:** Active — Gate 5 Pilot in progress  

---

## Your 6 Daily Workflows

These are the 6 things you can do with HCI AI right now on any of the 3 pilot projects (64 Eastwood, 101 Francis, 1355 Riverside).

---

### 1. Morning Project Brain Init

Get the current state of any project in 2 minutes instead of 30.

```
GET /api/v1/mvp/projects/1355R/init
```

Returns: bid status, log count, open risks, open RFIs, pending submittals, schedule variance items.

---

### 2. Import a Bid (Dry-Run First)

When a sub sends a bid:

```
POST /api/v1/mvp/projects/101F/bids/import
{
  "vendor_name": "Acme Framing",
  "trade": "Framing",
  "bid_amount": 85000,
  "scope_description": "Rough framing all floors per plans",
  "dry_run": true
}
```

Review the proposed bid + AI validation. When ready to log it:
- Change `dry_run: false`
- It goes to your approval queue
- You approve → it gets written

---

### 3. Submit a Daily Log

From the field or end of day:

```
POST /api/v1/mvp/projects/1355R/daily-log
{
  "date": "2026-06-26",
  "crew_size": 8,
  "work_performed": "Installed window headers on north elevation",
  "weather": "Clear, 75F",
  "constraints": "Window delivery pushed to Friday",
  "safety_notes": "All crew in harnesses",
  "dry_run": true
}
```

AI auto-detects: delays, weather impacts, safety flags, schedule risks, missing scope. Review the intelligence, then set `dry_run: false` to queue for approval.

---

### 4. PM Weekly Review

Monday morning, check all 3 projects at once:

```
GET /api/v1/mvp/projects/101F/pm-weekly-review
GET /api/v1/mvp/projects/1355R/pm-weekly-review
GET /api/v1/mvp/projects/64EW/pm-weekly-review
```

Returns: health status (green/yellow/red), alerts, open items count, recent log summary.

---

### 5. Schedule/Status Intelligence

Check for schedule variances and decision points:

```
GET /api/v1/mvp/projects/1355R/schedule-status
```

Returns: overall_status, critical items, decision_needed items, open risks, RFI summary.

---

### 6. Executive Report (Morning Briefing)

One call for all 3 projects:

```
GET /api/v1/mvp/executive-report
```

Returns: per-project health, portfolio risk summary, projects at risk vs. on track.

---

## Your Approval Queue

Review items waiting for your approval:

```
GET /api/v1/services/approval-queue/queue?status=pending
```

To approve an item:
```
POST /api/v1/services/approval-queue/items/{id}/approve
```

To reject:
```
POST /api/v1/services/approval-queue/items/{id}/reject
{"reason": "wrong trade"}
```

---

## Background Learning — What It's Doing

HCI AI is continuously scanning Drive, HubSpot, and Houzz for new documents and data. Nothing is written — it's read-only. When it finds something worth reviewing, it creates an intelligence candidate.

Check what's been found:
```
GET /api/v1/services/background-learning/summary
```

Items in `Human Review Needed` status need your eyes.

---

## ROI — How Much Time You're Saving

```
GET /api/v1/mvp/roi-summary
```

Shows cumulative minutes saved across all workflow runs. Each workflow logs its savings automatically.

---

## Sprint Dashboard

```
GET /api/v1/mvp/sprint-status
```

Full system health: connector status, background learning pipeline, approval queue, total minutes saved.

---

## API Base URL

All endpoints: `http://localhost:8000/api/v1/`  
Header required: `X-API-Key: hci-01253a2b0f87dbd03346bba60f0c31d7350e5c75b17c866c`

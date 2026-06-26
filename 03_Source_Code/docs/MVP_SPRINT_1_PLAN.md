# MVP Sprint 1 — Daily Operations, Background Learning & Approval Controls

**Status:** COMPLETE ✅  
**Sprint Period:** 2026-06  
**Test Result:** 48/48 PASS  

---

## Objective

Move HCI AI from platform architecture into tested daily-use construction operations for 3 pilot projects. Use the existing platform foundation — no redesign.

---

## Pilot Projects

| Code  | Project             | Role                          |
|-------|---------------------|-------------------------------|
| 64EW  | 64 Eastwood         | Historical reference          |
| 101F  | 101 Francis         | PM / bid / daily ops          |
| 1355R | 1355 Riverside      | Primary advanced pilot        |

DB IDs: 64EW=1, 101F=2, 1355R=3, 83SB=4

---

## 6 MVP Workflows

| # | Workflow                      | Endpoint                                    | ROI Baseline |
|---|-------------------------------|---------------------------------------------|-------------|
| 1 | Project Brain Init            | `GET /mvp/projects/{code}/init`             | 30 min      |
| 2 | Bid Management                | `POST /mvp/projects/{code}/bids/import`     | 45 min      |
| 3 | Daily Log + Field Intelligence| `POST /mvp/projects/{code}/daily-log`       | 30 min      |
| 4 | PM Weekly Review              | `GET /mvp/projects/{code}/pm-weekly-review` | 90 min      |
| 5 | Schedule/Status Intelligence  | `GET /mvp/projects/{code}/schedule-status`  | 30 min      |
| 6 | Executive Reporting           | `GET /mvp/executive-report`                 | 60 min      |

---

## Background Learning Pipeline

Read-only data pipeline. 13 statuses:

```
Discovered → Access Confirmed → Indexed → Classified → Extracted →
Embedded → Linked to Project Brain → Intelligence Candidate Created →
Human Review Needed → Approved | Rejected | Archived | Error
```

Sources: Google Drive, HubSpot, Houzz, Outlook  
All discovery is read-only. Zero writes to source systems.

---

## Approval Queue

Every proposed write action is held in the `approval_queue` table:

- Status starts as `pending` — no system has been changed
- Buck reviews and approves or rejects
- After approval, caller explicitly marks `executed` — system never auto-executes
- Every action logged to `platform_audit_log` with correlation ID

---

## New DB Tables (applied to live DB)

| Table                       | Purpose                                       |
|-----------------------------|-----------------------------------------------|
| `background_learning_records` | Pipeline tracking for all discovered docs   |
| `connector_registry`         | Source connections per project (read_only)   |
| `approval_queue`             | All proposed write actions awaiting approval |
| `roi_log`                    | Per-workflow ROI metrics, auto-computes savings |

---

## Safety Rules (non-negotiable)

- All integrations begin read-only
- HubSpot updates queued as approval items — never written directly
- Google Drive writes use test folders or dry-run mode only
- Houzz updates remain draft-only until explicitly approved
- Client comms, bid awards, contracts, change orders, financial commitments require human approval
- Every write action logged with who/what/when/why/workflow/source/approval evidence/rollback path

---

## API Prefix

All MVP endpoints: `/api/v1/mvp/`  
All service endpoints: `/api/v1/services/`

Router: `api/routers/mvp_ops.py`  
Services: `services/background_learning/`, `services/approval_queue/`, `services/connector_registry/`

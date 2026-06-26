# BOOK 00 — Chapter 19: MVP Sprint 1 — Daily Operations

**Status:** COMPLETE ✅  
**Test Result:** 48/48 PASS  
**Sprint:** MVP Sprint 1 — Daily Operations, Background Learning & Approval Controls  

---

## What Was Built

Phase 6 of the HCI AI build sequence. MVP Sprint 1 moves the system from platform architecture into active daily construction operations for 3 pilot projects.

---

## New API Layer (`api/routers/mvp_ops.py`)

Prefix: `/api/v1/mvp/`

| Endpoint                                    | Workflow              |
|---------------------------------------------|-----------------------|
| `GET /mvp/projects/{code}/init`             | Project Brain Init    |
| `POST /mvp/projects/{code}/bids/import`     | Bid Management        |
| `POST /mvp/projects/{code}/daily-log`       | Daily Log / Field Intel |
| `GET /mvp/projects/{code}/pm-weekly-review` | PM Weekly Review      |
| `GET /mvp/projects/{code}/schedule-status`  | Schedule/Status Intel |
| `GET /mvp/executive-report`                 | Executive Reporting   |
| `GET /mvp/roi-summary`                      | ROI Summary           |
| `GET /mvp/sprint-status`                    | Sprint Dashboard      |
| `GET /mvp/`                                 | MVP Overview          |

---

## New Services

| Service               | Path                                              | Purpose                       |
|-----------------------|---------------------------------------------------|-------------------------------|
| Background Learning   | `services/background_learning/`                   | Read-only doc discovery       |
| Approval Queue        | `services/approval_queue/`                        | Write action gating           |
| Connector Registry    | `services/connector_registry/`                    | Source connection tracking    |

Service endpoints: `/api/v1/services/{service-name}/`

---

## New DB Tables

| Table                        | Purpose                                       |
|------------------------------|-----------------------------------------------|
| `background_learning_records`| Pipeline tracking for discovered docs        |
| `connector_registry`         | Source connections (always read_only at start)|
| `approval_queue`             | All proposed writes held for Buck approval   |
| `roi_log`                    | Per-workflow ROI metrics                      |

Schema file: `database/mvp_sprint_1_schema.sql`

---

## Pilot Projects

| Code  | DB ID | Project         |
|-------|-------|-----------------|
| 64EW  | 1     | 64 Eastwood     |
| 101F  | 2     | 101 Francis     |
| 1355R | 3     | 1355 Riverside  |

---

## Safety Architecture

- All integrations read-only by default
- All write workflows default to `dry_run=true`
- When `dry_run=false`, action goes to `approval_queue` — never written directly
- Approval queue requires explicit `approve()` then `mark_executed()` — system never auto-executes
- Every action audited in `platform_audit_log`

---

## Documentation

| File                                  | Contents                              |
|---------------------------------------|---------------------------------------|
| `docs/MVP_SPRINT_1_PLAN.md`           | Sprint objectives and architecture    |
| `docs/MVP_SPRINT_1_TEST_PLAN.md`      | 48-test test plan                     |
| `docs/MVP_SPRINT_1_TEST_RESULTS.md`   | 48/48 pass results                    |
| `docs/LIVE_PILOT_PROJECT_MATRIX.md`   | Pilot project configuration           |
| `docs/BACKGROUND_LEARNING_STANDARD.md`| BL pipeline standard                  |
| `docs/PROJECT_BRAIN_PILOT_SETUP.md`   | Pilot setup checklist                 |
| `docs/DAILY_OPERATIONS_WORKFLOW.md`   | Workflow 3 reference                  |
| `docs/PM_WEEKLY_REVIEW_WORKFLOW.md`   | Workflow 4 reference                  |
| `docs/BID_MANAGEMENT_MVP_WORKFLOW.md` | Workflow 2 reference                  |
| `docs/SCHEDULE_STATUS_INTELLIGENCE_MVP.md` | Workflow 5 reference            |
| `docs/EXECUTIVE_REPORTING_MVP.md`     | Workflow 6 reference                  |
| `docs/READ_ONLY_AND_APPROVAL_CONTROLS.md` | Safety architecture              |
| `docs/ROI_MEASUREMENT_STANDARD.md`    | ROI tracking standard                 |
| `docs/BACKGROUND_JOB_MONITORING_REGISTER.md` | Job monitoring register        |

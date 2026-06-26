# HCI AI — SOP Dashboard Requirements

**Version:** 1.0 | **Date:** 2026-06-25 | **Directive:** HCI_AI_SOP_to_Software_Execution_Layer_Master_Directive_v1.0

---

## Dashboard Purpose

The SOP Execution dashboard gives Buck and the PM a real-time view of every active SOP instance across all projects. It shows status, blockers, approvals pending, and cycle time — without anyone having to compile a report.

---

## Dashboard Views

### View 1: Company-Level SOP Status Board

**Audience:** Buck (daily review)  
**Data source:** `sop_instances` joined to `projects`

**Columns:**
| Column | Source |
|--------|--------|
| SOP | sop_number |
| Project | project name |
| Status | current status with color: 🟢 active-progressing, 🟡 blocked or stalled, 🔴 overdue/error |
| Owner | owner_name |
| Days in Status | NOW() - status_changed_at |
| Due Date | target_issue_date |
| Days Until Due | target_issue_date - NOW() |
| Blocked? | stop_events where resolved_at IS NULL |
| Approval Pending? | status = 'Approval Required' |
| Action Required | computed: what is needed next |

**Filters:** Project, SOP number, status, owner, approval pending Y/N

**Sort default:** Days in Status descending (longest-stalled at top)

---

### View 2: Project-Level SOP Chain View

**Audience:** PM (daily/weekly)  
**Shows:** All SOP instances for one project, in lifecycle sequence

**Display:**
```
Project: 101 Francis

Preconstruction Chain:
  SOP 01  [Archived ✅]  Closed 2025-11-01
  SOP 02  [Archived ✅]  Closed 2025-11-01
  SOP 03  [Archived ✅]  Closed 2025-11-01
  SOP 04  [Archived ✅]  Closed 2025-11-15
  SOP 05  [Archived ✅]  Closed 2025-11-15
  SOP 06  [Archived ✅]  Closed 2025-11-15
  SOP 07  [Archived ✅]  Closed 2025-12-01
  SOP 08  [N/A        ]  —
  SOP 09  [Archived ✅]  Closed 2025-12-01
  SOP 10  [Archived ✅]  Closed 2025-12-10
  SOP 11  [Issued ✅  ]  Issued 2026-01-15 → Handed Off to SOP 15
  SOP 15  [Approved ✅]  Awarded 2026-02-01 → Handed Off to SOP 16
  SOP 16  [In Progress 🔵] Owner: Buck | Day 3 | Due 2026-02-15
```

---

### View 3: Approval Queue

**Audience:** Buck  
**Shows:** All SOP instances with status = Approval Required

| SOP | Project | Trade/Scope | Days Waiting | What Needs Approval |
|-----|---------|------------|--------------|---------------------|
| SOP 11 | 64 Eastwood | Concrete | 2 | Bid package issue (Gate 11-C) |
| SOP 15 | 101 Francis | Electrical | 1 | Award decision (Gate 15-C) |

Buck can drill into each row to see the full leveling sheet or bid package before approving.

---

### View 4: Stop Event Log

**Audience:** PM, Buck  
**Shows:** All active (unresolved) stop events across all projects

| Stop Condition | SOP | Project | Triggered | Days Open | Resolution Required |
|---------------|-----|---------|-----------|-----------|---------------------|
| SC-01 Missing Inputs | SOP 11 | 1355 Riverside | 2026-06-20 | 5 | PM to upload structural drawings |
| SC-03 Risk Flag Open | SOP 15 | 64 Eastwood | 2026-06-24 | 1 | PM to disposition contract qualification |

---

### View 5: SOP Cycle Time KPIs

**Audience:** Buck (monthly review)  
**Shows:** Cycle time metrics for completed SOP instances

| Metric | SOP 11 | SOP 15 |
|--------|--------|--------|
| Avg days from Not Started → Issued | — | — |
| Avg days from In Progress → Internal Review | — | — |
| Avg days in Approval Required | — | — |
| % completed on or before target_issue_date | — | — |
| Stop events per instance (avg) | — | — |
| Revision cycles per instance (avg) | — | — |

*Data populates as instances complete.*

---

## API Endpoints Required for Dashboard

| Endpoint | Description |
|---------|-------------|
| `GET /api/v1/sop/instances` | All active instances with status, project, owner, days |
| `GET /api/v1/sop/instances/{project_id}` | All instances for one project |
| `GET /api/v1/sop/approvals/pending` | All instances awaiting approval |
| `GET /api/v1/sop/stop_events/active` | All unresolved stop events |
| `GET /api/v1/sop/kpis/cycle_time` | Cycle time metrics by SOP number |
| `GET /api/v1/sop/instances/{id}` | Full detail view of one instance |

---

## Status Color Rules

| Color | Condition |
|-------|-----------|
| 🟢 Green | Status is progressing; days in status < SLA |
| 🟡 Yellow | Days in status > SLA; or status = Blocked with open stop event |
| 🔴 Red | Days in status > 2x SLA; or status = Approval Required > 3 days; or SC-04/SC-06 triggered |

---

## SLA Targets by Status

| Status | SLA (days) | Action if Exceeded |
|--------|-----------|-------------------|
| Inputs Missing | 3 | PM reminder |
| Internal Review | 2 | PM reminder |
| Approval Required | 3 | Buck reminder + PM escalation |
| Revision Required | 3 | PM reminder to owner |
| Blocked | 2 | PM + Buck notification |

---

*SOP status data: `sop_instances` table*  
*Stop events: `sop_stop_events` table*  
*Approval gates: `sop_approval_gates` table*

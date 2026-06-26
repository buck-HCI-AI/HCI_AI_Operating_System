# HCI AI — Business Process Library Standard

**Version:** 1.0 | **Date:** 2026-06-25 | **Directive:** HCI_AI_Business_Operating_Layer_BOOK01_Decision_KPI_Master_Directive_v1.0

---

## Purpose

This document defines the Business Process Library data model, process registration standard, maturity framework, and API contract. The Business Process Library is the master index connecting every HCI business process to its SOPs, workflows, data, KPIs, and approval gates.

---

## Process Data Model

### PostgreSQL Table: `business_processes`

```sql
CREATE TABLE business_processes (
    id                  SERIAL PRIMARY KEY,
    process_code        VARCHAR(50) UNIQUE NOT NULL,
    process_name        VARCHAR(200) NOT NULL,
    phase               VARCHAR(50) NOT NULL,   -- preconstruction, field, change, closeout
    description         TEXT NOT NULL,
    trigger_event       TEXT NOT NULL,
    required_inputs     JSONB,
    required_outputs    JSONB,
    related_sop_ids     TEXT[],                 -- SOP numbers: ['11', '13']
    related_workflows   TEXT[],                 -- workflow IDs: ['WF-001', 'SOP-11']
    primary_table       TEXT,                   -- main PostgreSQL table for this process
    related_tables      TEXT[],
    kpi_codes           TEXT[],                 -- KPI codes tracked for this process
    approval_gate_ids   TEXT[],                 -- gate IDs from SOP_APPROVAL_GATE_REGISTER
    owner_role          VARCHAR(100),           -- who owns this process
    reviewer_role       VARCHAR(100),
    approver_role       VARCHAR(100),
    maturity_level      SMALLINT CHECK (maturity_level BETWEEN 0 AND 4),
    active              BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Maturity Level Definitions

| Level | Name | Criteria |
|-------|------|----------|
| 0 | Ad Hoc | No SOP; work done from memory; no data produced |
| 1 | Defined | SOP exists; process is documented but not digitized |
| 2 | Executed | SOP converted to workflow; structured data is produced |
| 3 | Measured | KPIs track quality and cycle time; alerts on thresholds |
| 4 | Optimized | AI assists; learnings from past projects feed the process |

---

## Current Process Registry

### Preconstruction Processes

| Process Code | Name | SOPs | Workflows | Data Tables | KPIs | Maturity |
|-------------|------|------|-----------|------------|------|---------|
| `PC-INTAKE` | Project Intake | 01, 02, 03 | WF-001 | projects | — | 2 |
| `PC-PLAN-REVIEW` | Plan Review and Risk ID | 04, 05, 06 | Project Brain | scope_checklist, risk_log | — | 1 |
| `PC-BUDGET` | Budgeting | 07, 08, 09, 10 | Bid Intelligence | project_budgets | BUDGET_VAR_MAX | 2 |
| `PC-BID-PKG` | Bid Package Assembly | 11, 13 | SOP-11 | bid_packages, sop_instances | — | 2* |
| `PC-SUB-OUTREACH` | Sub Outreach and Follow-Up | 12, 14 | Bid Intelligence | vendor_contacts, bid_log | — | 2 |
| `PC-LEVELING` | Bid Leveling | 15 | SOP-15 | bid_leveling_records, sop_instances | — | 2* |
| `PC-BUYOUT` | Buyout | 16, 19 | Procurement | awards, subcontracts | — | 2 |

*In progress — Phase C service build underway

### Field Execution Processes

| Process Code | Name | SOPs | Workflows | Data Tables | KPIs | Maturity |
|-------------|------|------|-----------|------------|------|---------|
| `FX-STARTUP` | Project Startup | 23 | WF-001 | projects | — | 2 |
| `FX-DAILY` | Daily Field Operations | 24, 25 | WF-SUPER | daily_logs | LOG_COMPLETION | 3 |
| `FX-SCHEDULE` | Schedule Management | 17 | Schedule Intel | schedule_activities | SCHED_VAR_DAYS | 3 |
| `FX-QC` | Quality Control | 27, 28, 30 | WF-SUPER | inspections, nc_work | — | 2 |
| `FX-SAFETY` | Safety | 29 | WF-SUPER | safety_incidents | — | 2 |
| `FX-LONGEAD` | Long-Lead Tracking | 18 | Procurement | long_lead_items | — | 2 |

### Change Management Processes

| Process Code | Name | SOPs | Workflows | Data Tables | KPIs | Maturity |
|-------------|------|------|-----------|------------|------|---------|
| `CM-RFI` | RFI Management | 32 | WF-002 context | rfis | OPEN_RFI_AGE | 3 |
| `CM-CO` | Change Order Management | 31, 33 | Change service | change_orders | CO_PENDING_DAYS | 2 |
| `CM-SUBMITTAL` | Submittal Management | — | Submittal service | submittals | — | 2 |

### Communication Processes

| Process Code | Name | SOPs | Workflows | Data Tables | KPIs | Maturity |
|-------------|------|------|-----------|------------|------|---------|
| `CO-MEETINGS` | Meeting Notes | 35 | WF-002 | meeting_notes, action_items | — | 3 |
| `CO-WEEKLY` | Weekly Status Report | 37 | WF-PM-W | weekly_reports | — | 3 |
| `CO-DECISION` | Decision Log | 36 | Decision Intel | decision_records | — | 2* |
| `CO-CLIENT` | Client Communication | 34 | — | comm_log | — | 1 |

*In progress — Phase A service build queued

### Closeout Processes

| Process Code | Name | SOPs | Workflows | Data Tables | KPIs | Maturity |
|-------------|------|------|-----------|------------|------|---------|
| `CL-PUNCH` | Punch List | 39 | Punch service | punch_items | PUNCH_OPEN_AGE | 2 |
| `CL-CLOSEOUT` | Closeout Documents | 40 | Doc tracker | closeout_checklist | CLOSEOUT_AVG_DAYS | 2 |
| `CL-WARRANTY` | Warranty Management | 41 | Warranty service | warranty_claims | — | 1 |
| `CL-REVIEW` | Post-Project Review | 42 | Lessons Learned | lessons_learned | — | 2 |

---

## API Contract

### `GET /api/v1/processes`
List all registered processes with maturity levels and status.

### `GET /api/v1/processes/{process_code}`
Get a full process definition with all linked SOPs, workflows, tables, and KPIs.

### `GET /api/v1/processes/maturity`
Company-wide maturity assessment: processes by level, count, and target.

### `POST /api/v1/processes/`
Register a new process definition (admin only).

---

*BOOK_01 Volume 15: `BOOK_01/15_BUSINESS_PROCESS_LIBRARY.md`*  
*Service: `03_Source_Code/services/business_process_library/`*

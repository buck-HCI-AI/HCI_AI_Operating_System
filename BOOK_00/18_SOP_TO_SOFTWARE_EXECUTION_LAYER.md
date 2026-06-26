# BOOK_00 — Volume 18: SOP-to-Software Execution Layer

**Version:** 1.0 | **Date:** 2026-06-25 | **Directive:** HCI_AI_SOP_to_Software_Execution_Layer_Master_Directive_v1.0  
**Status:** Phase A+B Complete — Phase C (Pilot Build: SOP 11 + SOP 15) IN PROGRESS

---

## 1. Purpose

This volume defines how HCI's Standard Operating Procedures are converted into executable software logic within the HCI AI Operating System. It is the implementation standard for the SOP-to-Software Execution Layer.

**Governing principle:** A great project is created before it is built. The preconstruction and buyout chain is the first conversion priority.

---

## 2. What This Layer Does

The SOP Execution Layer takes HCI's 42 SOPs and converts each one into four aligned artifacts:

| Layer | Audience | Purpose |
|-------|----------|---------|
| Layer 1 — Executive SOP | Leadership, process owners | Business purpose, trigger, accountable owner, required outputs, non-skippable controls, approval gates, KPIs, handoff |
| Layer 2 — Employee Training Script | New employees, role backups | Role-based step-by-step instructions; what good work looks like; common mistakes; handoff |
| Layer 3 — AI Agent Script | AI/software build | Role prompt, allowed inputs, required outputs, risk flags, stop conditions, prohibited actions, human-review rule |
| Layer 4 — Templates / Data Fields | Operations, software builders | Forms, DB fields, tracker columns, workflow statuses, dashboard fields, API payloads, approval evidence |

---

## 3. Universal Workflow Spine

Every SOP module must follow this spine — no exceptions:

```
Trigger → Required Inputs → Input Validation → Work Step Execution →
AI Assistance → Human Review → Approval Gate → Handoff →
Data Record → Dashboard Status → Audit Trail
```

---

## 4. Universal Stop Conditions

Any of these conditions must halt the workflow until resolved:

1. Required inputs missing or outdated
2. Output depends on an unapproved assumption
3. Scope, pricing, schedule, or contract risk is unclear
4. Deliverable would create external commitment without required approval
5. Reviewer marked work "Revision Required"
6. Workflow owner is attempting to bypass an approval gate
7. Handoff destination is missing or not confirmed

---

## 5. Standard Status Model

All SOP workflow instances use exactly these statuses — no others without adding to the SOP status dictionary:

| Status | Meaning |
|--------|---------|
| Not Started | Trigger exists; owner has not begun |
| Inputs Missing | Required source docs/fields/approvals absent |
| Ready to Start | All inputs confirmed; work can begin |
| In Progress | Owner executing work steps |
| AI Drafted | AI produced a draft output for human review |
| Internal Review | PM/estimator/principal reviewing |
| Revision Required | Reviewer found gaps; work must be corrected |
| Approval Required | Technical review done; awaiting authority approval |
| Approved | Required reviewer/approver signed off |
| Issued / Completed | Approved deliverable sent/handed off |
| Handed Off | Passed to next SOP owner |
| Blocked | Waiting on external input/decision |
| Exception Approved | Normal gate bypassed with documented exception |
| Cancelled | Workflow ended without completion |
| Archived | Closed and stored; no further action |

---

## 6. AI Capability Boundary

**AI may:** draft, extract, compare, summarize, flag risks, identify gaps, generate structured outputs, check scope, normalize pricing data, classify risks, produce checklists.

**AI may NOT:** issue external commitments, approve awards, approve contracts, approve change orders, update HubSpot writeback, approve client-facing communications, or make final decisions without human approval.

Any bypass must create an exception record: owner, reason, risk, mitigation, approver, date, expiration.

---

## 7. SOP Conversion Inventory and Priority

**Source documents (Google Drive):**
- SOP 00: `1efBEqMKiYtWs_UlbriotYsoHF8VDPIE0`
- 42-SOP Pack: `17e2QFuD_ikFLVv8fpkdyNdY1PkA27rUw`
- SOP 2.0: `1uurAdx-BUHll__nvA3MUMl74NXFiMYAf`

**Conversion sequence (per directive §7):**

| Priority | SOP | Status |
|----------|-----|--------|
| 1 | SOP 11 — Bid Package | 🔵 IN PROGRESS (Phase C) |
| 2 | SOP 15 — Bid Leveling | 🔵 IN PROGRESS (Phase C) |
| 3 | SOP 13 — Bid Distribution | ⬜ Next |
| 4 | SOP 14 — Bid Follow-Up | ⬜ Next |
| 5 | SOP 10 — Allowances / Alternates / Exclusions | ⬜ Next |
| 6 | SOP 16 — Buyout | ⬜ Next |
| 7 | SOP 04/05/06/07 — Plan Review, Narrative, Risk, ROM | ⬜ Backfill |
| 8 | SOP 12/19 — Sub CRM, Subcontract Agreement | ⬜ Close loop |

Full inventory: `docs/SOP_CONVERSION_INVENTORY.md`

---

## 8. Data Model

The SOP Execution Layer uses a shared data model — not isolated tracker fields per workflow.

**Core objects (PostgreSQL):**
- `sop_instances` — one record per SOP execution
- `sop_tasks` — individual work steps within an instance
- `sop_inputs` — required source documents and field values
- `sop_outputs` — deliverables produced
- `sop_approval_gates` — approval events and evidence
- `sop_stop_conditions` — triggered stop events and resolutions
- `sop_exceptions` — bypass events with required fields
- `sop_handoffs` — inter-SOP transfer records
- `sop_workflow_events` — audit log of all status changes
- `sop_kpi_records` — cycle time, quality, compliance metrics

**Every SOP instance links to:** Project, Project Phase, Owner Role, Responsible Person, Due Date, Status, Inputs, Outputs, Approval Status, Blockers, Exceptions, Related Documents, Related Vendors, Related Budget Items, Related Schedule Activities, Related Risks.

Schema: `05_Database/sop_execution_schema.sql`

---

## 9. Integration Points

The SOP Execution Layer uses existing HCI AI shared services — it does not duplicate them:

| Integration | How Used |
|-------------|----------|
| PostgreSQL | SOP instance records, approval logs, KPI data |
| MinIO | Document storage for bid packages, leveling sheets, award memos |
| Qdrant | Semantic search across bid packages, scope documents |
| Redis | Workflow state cache |
| Project Brain | Q&A against SOP outputs and project intelligence |
| AI_TEAM | Status tracking, next-session handoff |
| API Layer v1 | `/api/v1/sop/` router exposes all SOP endpoints |
| n8n | Workflow orchestration for automated triggers |
| HubSpot (read-only) | Vendor/contact lookups; no writeback without human approval |
| Google Drive | Document routing and source file access |

---

## 10. Repository Structure

```
services/sop_execution/
├── shared/
│   ├── __init__.py
│   ├── base_sop.py           — Base class for all SOP modules
│   ├── sop_data_model.py     — Core data objects
│   ├── approval_engine.py    — Approval gate logic
│   ├── stop_condition.py     — Stop condition enforcement
│   └── sop_kpi.py            — KPI tracking
├── sop_11_bid_package/
│   ├── __init__.py
│   ├── sop_11_service.py     — SOP 11 execution logic (4 layers)
│   ├── sop_11_agent.py       — AI agent script implementation
│   └── sop_11_templates.py   — Data fields and templates
└── sop_15_bid_leveling/
    ├── __init__.py
    ├── sop_15_service.py     — SOP 15 execution logic (4 layers)
    ├── sop_15_agent.py       — AI agent script implementation
    └── sop_15_templates.py   — Data fields and templates

docs/
├── SOP_2_0_CONVERSION_STANDARD.md
├── SOP_CONVERSION_INVENTORY.md
├── SOP_WORKFLOW_STATUS_MATRIX.md
├── SOP_DATA_FIELD_DICTIONARY.md
├── SOP_APPROVAL_GATE_REGISTER.md
├── SOP_STOP_CONDITION_REGISTER.md
├── SOP_AI_AGENT_SCRIPT_LIBRARY.md
├── SOP_EMPLOYEE_SCRIPT_LIBRARY.md
├── SOP_TEMPLATE_BACKLOG.md
├── SOP_TEST_MATRIX.md
├── SOP_DASHBOARD_REQUIREMENTS.md
└── PRECONSTRUCTION_CHAIN_IMPLEMENTATION_PLAN.md
```

---

## 11. Testing Requirements

No SOP conversion is marked complete until:
- Unit test: each layer function works in isolation
- Workflow test: full happy-path execution from trigger to handoff
- Integration test: data records written to PostgreSQL, documents to MinIO, vectors to Qdrant
- UAT scenario: Buck runs a real workflow and confirms output is correct and useful

Evidence: `docs/SOP_TEST_MATRIX.md`

---

## 12. Current Phase Status

| Phase | Description | Status |
|-------|-------------|--------|
| A — Inventory | SOP_CONVERSION_INVENTORY.md created; all 42 SOPs indexed | ✅ 2026-06-25 |
| B — Standard | SOP_2_0_CONVERSION_STANDARD.md created | ✅ 2026-06-25 |
| C — Pilot Build | SOP 11 + SOP 15 four-layer modules | 🔵 In Progress |
| D — Test | SOP 11 + SOP 15 test scenarios | ⬜ |
| E — Chain Expansion | SOP 13, 14, 10, 16 | ⬜ |
| F — Backfill | SOP 04, 05, 06, 07 | ⬜ |
| G — Close Loop | SOP 12, 19 | ⬜ |
| H — Report | BOOK_00, AI_TEAM, dashboards updated | ⬜ |

---

*Cross-references: `docs/SOP_CONVERSION_INVENTORY.md` | `docs/SOP_2_0_CONVERSION_STANDARD.md` | `BOOK_01/03_ESTIMATING_AND_BID_MANAGEMENT.md` | `BOOK_00/17_QUALITY_ASSURANCE_AND_VALIDATION.md`*

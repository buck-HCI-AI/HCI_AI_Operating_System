# HCI AI — SOP 2.0 Conversion Standard
**Version:** 1.0 | **Date:** 2026-06-25 | **Source:** HCI_SOP_2_0_Scripted_Operating_System_Framework.docx (`1uurAdx-BUHll__nvA3MUMl74NXFiMYAf`)

This is the format standard every SOP conversion must follow. No SOP is complete until all four layers exist and pass testing.

---

## The Four-Layer Model

Every converted SOP must produce exactly four aligned artifacts. The layers must describe the same workflow — leadership intent, employee action, AI execution, and data controls must all be consistent.

### Layer 1 — Executive SOP

**Audience:** Leadership, managers, process owners.

Required sections:
- **Why this SOP exists** — business risk it controls
- **Trigger** — exact condition that starts the workflow
- **Owner** — accountable person/role (not just department)
- **Supporting roles** — who assists/reviews
- **Required outputs** — deliverable that proves SOP was completed
- **Cannot be skipped** — non-negotiable controls before handoff
- **Approval authority** — who must approve before external issue/commitment
- **Handoff** — what goes to the next SOP and who receives it
- **KPIs** — how success is measured

### Layer 2 — Employee Training Script

**Audience:** New employees, role backups, cross-trained staff.

Format: Direct second-person role script. Begin with role and business context.

Required sections:
- Role statement: "You are the [Role]. Your job is to..."
- Before you start: source documents to collect; confirmations required
- Step-by-step process: numbered, in required execution order
- Finished work looks like: quality standard and review criteria
- Common mistakes: known failure modes
- Handoff instructions: what to pass, to whom, with what confirmation

### Layer 3 — AI Agent Script

**Audience:** AI workflow development, automation prompts, software logic.

Format: Role-based system instruction beginning with "Act as HCI's [Role]..."

Required sections:
- Role, context, and permitted inputs
- What to do if inputs are missing (return Inputs Missing report — do not proceed)
- Mandatory outputs in exact structured format
- Risk flags: classified by scope, cost, schedule, contract, coverage, document control
- Stop conditions: conditions that halt work and require human intervention
- Prohibited actions (always include): unsupported assumptions, hidden scope changes, external commitments without approval, award/contract decisions without human approval
- Human-review rule: explicit statement of what requires human approval before output is used

AI outputs must be structured enough to:
- Store in PostgreSQL (defined fields)
- Link documents in MinIO (file paths/IDs)
- Embed/search in Qdrant (semantic search)
- Display in dashboards (defined metrics)

### Layer 4 — Templates / Required Data Fields

**Audience:** Operations, project controls, software builders.

Required elements:
- Named data record with all required fields
- Input checklist (pass/fail, with owner for each failed item)
- Approval gate evidence fields
- Dashboard metrics fields
- Integration fields (IDs linking to related systems)
- File naming and folder standards

---

## Required SOP File Format

Every converted SOP lives in `services/sop_execution/sop_{nn}_{name}/` and must include:

```
sop_{nn}_{name}/
├── __init__.py
├── sop_{nn}_service.py     — Execution logic (Layer 1+2 implemented as methods)
├── sop_{nn}_agent.py       — AI agent script (Layer 3 as Claude prompt + handler)
└── sop_{nn}_templates.py   — Data models and field definitions (Layer 4)
```

Plus documentation in `docs/`:
- Referenced in `docs/SOP_AI_AGENT_SCRIPT_LIBRARY.md` (Layer 3)
- Referenced in `docs/SOP_EMPLOYEE_SCRIPT_LIBRARY.md` (Layer 2)
- Referenced in `docs/SOP_TEMPLATE_BACKLOG.md` (Layer 4)
- Test cases in `docs/SOP_TEST_MATRIX.md`

---

## Universal Workflow Spine

Every SOP module enforces this exact sequence:

```
Trigger
  → Required Inputs (block if missing)
  → Input Validation (confirm source docs are current)
  → Work Step Execution (employee or AI drafts)
  → AI Assistance (structured output for human review)
  → Human Review (named reviewer, comments captured)
  → Approval Gate (authority approval logged)
  → Handoff (receiver notified, fields passed)
  → Data Record (PostgreSQL row created)
  → Dashboard Status (metrics updated)
  → Audit Trail (all events logged to sop_workflow_events)
```

---

## Universal Stop Conditions

These conditions must halt the workflow in every SOP — not just show a warning:

| Stop Condition | Required Response |
|----------------|-------------------|
| Required inputs missing or outdated | Return Inputs Missing report; do not proceed |
| Output depends on unapproved assumption | Flag assumption; require owner confirmation before proceeding |
| Scope, pricing, schedule, or contract risk is unclear | Flag risk; require human decision before proceeding |
| Deliverable would create external commitment without approval | Block; route to required approver |
| Reviewer marked work Revision Required | Return to In Progress; capture comments |
| Owner attempting to bypass approval gate | Block; log bypass attempt; require exception record |
| Handoff destination missing | Block Issued status until receiver is named |

---

## Standard Status Model

All SOP instances use exactly these statuses:

| Status | Allowed Transitions |
|--------|-------------------|
| Not Started | → Inputs Missing, → In Progress |
| Inputs Missing | → In Progress (after all blockers resolved) |
| Ready to Start | → In Progress |
| In Progress | → AI Drafted, → Internal Review |
| AI Drafted | → Internal Review |
| Internal Review | → Revision Required, → Approval Required, → Approved |
| Revision Required | → In Progress, → Internal Review |
| Approval Required | → Approved, → Revision Required |
| Approved | → Issued / Completed, → Handed Off |
| Issued / Completed | → Handed Off, → Archived |
| Handed Off | → Archived |
| Blocked | → In Progress (after blocker resolved) |
| Exception Approved | → In Progress, → Approved |
| Cancelled | (terminal) |
| Archived | (terminal) |

---

## Approval Gate Rules

1. The workflow owner may prepare the deliverable but **cannot self-approve** when independent review is required.
2. AI can draft, extract, compare, summarize, and flag — it cannot approve, award, contract, or commit externally.
3. Any gate bypass must create an exception record with: owner, reason, risk, mitigation, named approver, date, expiration date.
4. Approval thresholds are configurable — stored in `operating_rules` service, not hardcoded.

---

## Risk Flag Taxonomy

All SOP modules classify risk flags using these categories:

| Risk Class | Examples |
|------------|---------|
| Scope | Missing scope, ambiguous detail, conflicting documents, excluded trade scope |
| Cost | Budget variance, abnormal unit rate, unpriced alternate, allowance mismatch |
| Schedule | Long lead item, bidder schedule exception, phasing conflict |
| Contract | Unacceptable qualification, nonstandard terms, missing insurance/bond/warranty |
| Coverage | Too few bidders, no responsive bid, single-source exposure |
| Document Control | Old drawings, unincorporated addendum, missing spec section |

---

## Data Architecture Requirements

All SOP modules write to shared PostgreSQL tables — not isolated tracker fields:

```sql
sop_instances        — one per SOP execution
sop_tasks            — individual work steps
sop_inputs           — source documents and field values
sop_outputs          — produced deliverables
sop_approval_gates   — approval events and evidence
sop_stop_events      — triggered stops and resolutions
sop_exceptions       — documented bypass events
sop_handoffs         — inter-SOP transfer records
sop_workflow_events  — full audit log
sop_kpi_records      — cycle time, quality, compliance
```

Schema: `05_Database/sop_execution_schema.sql`

---

## Pilot Review Criteria

Before any SOP conversion is declared complete, answer YES to all:

1. Could a new employee perform the task using only the employee script and templates?
2. Could a developer build the workflow without guessing the sequence?
3. Does the AI script define what to review, produce, flag, and stop?
4. Are fields specific enough to build forms, dashboards, and integrations?
5. Are approval gates clear enough to block issue/award/contract without the right approval?
6. Does the SOP hand off cleanly to the next SOP in the chain?

---

*Cross-references: `BOOK_00/18_SOP_TO_SOFTWARE_EXECUTION_LAYER.md` | `docs/SOP_CONVERSION_INVENTORY.md` | `docs/SOP_APPROVAL_GATE_REGISTER.md`*

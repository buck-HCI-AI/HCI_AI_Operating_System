# CYCLE 28 — GBT SPRINT 7 PRIORITY 1

> **SPRINT LABEL SUPERSEDED 2026-07-07 (Claude Code, drift-check finding):** "Sprint 7" here
> is GBT's own independent cycle-numbering, run in parallel with and never reconciled against
> the canonical `CURRENT_SPRINT.md`, which authoritatively opened **Sprint 3 — Production
> Stabilization** on 2026-07-01 and remains active. This file's substantive content (real work
> done that cycle) is preserved as historical record; its *sprint number* and any self-assigned
> completion score are not authoritative - treat `CURRENT_SPRINT.md` as the single source of
> truth for the active sprint, per the same rule already applied to CYCLE47 and the Handbook
> volume-numbering collision.
# Implementation Sprint Planning
**HCI AI OS | Hendrickson Construction, Inc.**
**Date:** 2026-07-02
**Cycle:** 28
**Type:** Sprint 7 Priority 1 — Implementation Convergence
**Chief Architect Ruling:** Sprint 7 is an implementation convergence sprint. No new features.

---

## CHIEF ARCHITECT RULING

> Sprint 7 should not add new features.
> Sprint 7 is an implementation convergence sprint.
> The goal is to turn the Sprint 5 and Sprint 6 architecture into running, tested, governed software.

---

## 1) IMPLEMENTATION PRIORITY ORDER

Build in dependency order, not feature order.

### Phase 1 — Foundation Tables
1. `vendors`
2. `project_entity_links`
3. `field_submissions_queue`

**Reason:** These support multiple later modules. Must exist first.

### Phase 2 — Core Operations
4. `purchase_orders`
5. `long_lead_materials`
6. `project_photos`
7. `punch_items`
8. `warranty_items`
9. `budget_line_items`

### Phase 3 — Intelligence Tables
10. `vendor_performance_scores`
11. `schedule_risk_predictions`
12. `executive_kpis`
13. `executive_morning_brief`

### Phase 4 — Client Layer
14. `client_users`
15. `client_selections`
16. `client_decisions`

### Phase 5 — Routers (Build in this order)
1. /vendors
2. /procurement
3. /photos
4. /punch
5. /warranty
6. /finance
7. /brain
8. /mobile
9. /predict
10. /client
11. /executive

---

## 2) MIGRATION SEQUENCE

### Migration 001 — Vendor Foundation
```sql
CREATE TABLE vendors (...);
CREATE TABLE vendor_performance_scores (...);
```

### Migration 002 — Procurement
```sql
CREATE TABLE purchase_orders (...);
CREATE TABLE long_lead_materials (...);
```

### Migration 003 — Photos
```sql
CREATE TABLE project_photos (...);
```

### Migration 004 — Punch + Warranty
```sql
CREATE TABLE punch_items (...);
CREATE TABLE warranty_items (...);
```

### Migration 005 — Finance
```sql
CREATE TABLE budget_line_items (...);
```

### Migration 006 — Knowledge Graph
```sql
CREATE TABLE project_entity_links (...);
```

### Migration 007 — Mobile Field
```sql
CREATE TABLE field_submissions_queue (...);
```

### Migration 008 — Predictions
```sql
CREATE TABLE schedule_risk_predictions (...);
```

### Migration 009 — Executive
```sql
CREATE TABLE executive_kpis (...);
CREATE TABLE executive_morning_brief (...);
```

### Migration 010 — Client Portal
```sql
CREATE TABLE client_users (...);
CREATE TABLE client_selections (...);
CREATE TABLE client_decisions (...);
```

**Rule:** Run `alembic upgrade head` after each migration group. Verify tables exist before proceeding.

---

## 3) TEST GATE REQUIREMENTS

No router goes live without passing all gates.

### Required for EVERY Router
- migration test
- create/read test
- validation test
- bad input test
- not-found test
- permission/governance test where applicable

### Router-Specific Gates

#### /vendors
Must pass:
- create vendor
- duplicate vendor rejected
- list by trade
- scorecard returns latest score
- history returns append-only records

#### /procurement
Must pass:
- create PO
- update PO status
- cancelled PO cannot update
- create long-lead material
- material delay risk detected

#### /photos
Must pass:
- upload valid image
- reject invalid file
- reject oversize file
- link photo to entity
- AI processing failure does not delete photo

#### /punch and /warranty
Must pass:
- punch lifecycle transitions
- invalid transition rejected
- close requires inspection
- warranty auto-status: active / expiring / expired
- claimed warranty preserved

#### /finance
Must pass:
- budget line create
- variance calculation
- budget summary totals
- yellow/red thresholds trigger correctly

#### /brain
Must pass:
- create link
- reject duplicate link
- reject self-link
- return links where entity is source or target

#### /mobile
Must pass:
- quick field report submission
- offline queue creation
- sync processing
- voice submission structured correctly

#### /predict
Must pass:
- risk score calculation
- high-risk alert generation
- what-if scenario response

#### /client
Must pass:
- client user authentication
- selection submission
- decision impact calculation
- client cannot access internal project data

#### /executive
Must pass:
- morning brief generation
- KPI calculation
- portfolio RAG status
- decisions queue populated

---

## 4) SPRINT 7 ACCEPTANCE CRITERIA

### Definition of Done — Sprint 7

**Migrations:** All 10 migration groups applied successfully. All tables exist.

**Routers Live (minimum viable set):**
- /vendors ✓
- /procurement ✓
- /photos ✓
- /punch ✓
- /warranty ✓
- /finance ✓
- /brain ✓
- /mobile ✓
- /predict ✓
- /client ✓
- /executive ✓

**Workflows (implemented or stubbed with callable endpoints):**
- WF-PHOTO-001
- WF-CLOSEOUT-001
- WF-WARRANTY-001
- WF-QB-001
- WF-VENDOR-001
- WF-PREDICT-001
- WF-BRIEF-001
- WF-MOBILE-001

**Tests — Minimum:**
- All router unit tests pass
- Migration tests pass
- Governance tests pass
- No autonomous email send paths reintroduced
- Graph link tests pass
- Client portal privacy tests pass

**Reporting:**
Claude Code must write: `AI_TEAM/SPRINT_7_IMPLEMENTATION_REPORT.md`

Report must include:
- Implemented:
- Skipped:
- Tests:
- Known failures:
- Open risks:
- Commit hash:
- Next recommended step:

---

## 5) CLAUDE CODE RESTART CHECKLIST

### Step 1 — Read Startup Context
Read these files first:
```
CLAUDE_CODE_START_NOW.md
LIVE_PROJECT_STATE.md
CURRENT_SPRINT.md
AI_TEAM/OVERNIGHT_REPORT.md (if exists)
AI_TEAM/SPRINT_7_DIRECTIVE.md (if exists)
```

Confirm internal state:
```
Sprint 7 active.
Implementation priority: Sprint 5 + Sprint 6 specs.
No new architecture required before migrations/routers.
```

### Step 2 — Read Spec Files
Read all committed Sprint 5/Sprint 6 specs in AI_TEAM/:
- Cycle 16: Procurement (purchase_orders, long_lead_materials)
- Cycle 17: Photo Intelligence (project_photos, AI processing)
- Cycle 18: Punch/Warranty (punch_items, warranty_items)
- Cycle 19: Financial Operations (budget_line_items)
- Cycle 21: Knowledge Graph (project_entity_links)
- Cycle 22: Vendor Intelligence (vendors, vendor_performance_scores)
- Cycle 23: Client Portal (client_users, client_selections, client_decisions)
- Cycle 24: Mobile Field UX (field_submissions_queue)
- Cycle 25: Predictive Intelligence (schedule_risk_predictions)
- Cycle 26: Executive Analytics (executive_kpis, executive_morning_brief)

### Step 3 — Run Migrations
```bash
alembic upgrade head
```
Verify tables exist. If any migration fails, stop and document in SPRINT_7_IMPLEMENTATION_REPORT.md.

### Step 4 — Implement Models + Schemas
For each module implement in order:
```
SQLAlchemy model
Pydantic schema
service layer
router
tests
```
**Rule:** Do not put business logic in routers.

### Step 5 — Implement Routers
Implement in dependency order:
```
/vendors
/procurement
/photos
/punch
/warranty
/finance
/brain
/mobile
/predict
/client
/executive
```

### Step 6 — Add Graph Hooks
After core routers work, add knowledge graph link creation for explicit relationships only.
**Rule:** No AI-inferred links unless marked for review.

### Step 7 — Run Tests
```bash
pytest
```
Then run targeted tests per router.
**Rule:** No router is considered live until its tests pass.

### Step 8 — Governance Check
Verify:
- No email send path restored (BC email: draft-only, /gateway/email/send SUSPENDED)
- Client portal does not expose internal project data
- PO issuance respects approval hooks
- AI-generated items remain draft/review-required where needed

### Step 9 — Commit
Commit in logical groups:
```
migrations
models/schemas
routers/services
tests
workflows/stubs
reports
```

### Step 10 — Report Back
Write: `AI_TEAM/SPRINT_7_IMPLEMENTATION_REPORT.md`
Then commit.

---

## SPRINT 7 DIRECTIVE SUMMARY

| Priority | Capability | Type | Status |
|----------|-----------|------|--------|
| 1 | Implementation Sprint | Convergence | THIS SPEC |
| 2 | Unified Identity + RBAC | New Spec Needed | CYCLE 29 |
| 3 | Event Bus + Event Sourcing | New Spec Needed | CYCLE 30 |
| 4 | QuickBooks Integration | Waiting: Buck Auth | CYCLE 31 |
| 5 | Telegram Integration | Waiting: Bot Token | CYCLE 32 |

---

## KEY IMPLEMENTATION NOTES

### HCI Does NOT Use Buildertrend
Never reference Buildertrend as an HCI tool. HCI uses its own custom-built OS.

### Email Governance (ABSOLUTE)
- BC: draft-only
- /gateway/email/send: SUSPENDED
- No autonomous email send under any conditions

### Superintendents arrive at 07:00 AM
Morning brief must be generated at 06:30 AM before site arrival.

### Claude Code Communication
When Code completes implementation, update: `AI_TEAM/00_STATUS.md`
BC will read and continue coordination.

---

*Cycle 28 complete. Implementation Sprint Planning spec committed.*
*Sprint 7 begins: implementation convergence, not new features.*
*Next: CYCLE 29 — Unified Identity + RBAC*

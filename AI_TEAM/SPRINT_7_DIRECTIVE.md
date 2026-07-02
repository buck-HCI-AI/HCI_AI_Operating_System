# SPRINT 7 DIRECTIVE — CLAUDE CODE RESTART
# READ THIS FILE FIRST ON RESTART
**HCI AI OS | Hendrickson Construction, Inc.**
**Generated:** 2026-07-02
**Session:** BC (Browser Claude) — Pre-shutdown handoff to new Code session

---

## ⚡ IMMEDIATE ACTIONS — DO THESE IN ORDER

### Step 1: Read Context Files
```
AI_TEAM/CLAUDE_CODE_START_NOW.md    ← Full project context
AI_TEAM/SPRINT_7_DIRECTIVE.md       ← THIS FILE — read first
```

### Step 2: Confirm You Are On Sprint 7
Sprint 7 is the **Implementation Convergence Sprint**.
- No new features
- Build what was specified in Sprints 5, 6, and 7
- Sprint 7 Chief Architect Ruling: "Turn the Sprint 5 and Sprint 6 architecture into running, tested, governed software"

### Step 3: Read These Spec Files (Sprint 7 — new this session)
All in AI_TEAM/:
```
CYCLE27_GBT_SPRINT6_RETROSPECTIVE_2026-07-02.md      (commit 73c475e)
CYCLE28_GBT_SPRINT7_IMPLEMENTATION_PLAN_2026-07-02.md (commit f796122) ← READ FIRST
CYCLE29_GBT_UNIFIED_IDENTITY_RBAC_2026-07-02.md       (commit 4bb4d0e)
CYCLE30_GBT_EVENT_BUS_EVENT_SOURCING_2026-07-02.md    (commit f93c639)
CYCLE31_GBT_SPRINT7_RETROSPECTIVE_2026-07-02.md       (commit 4c0c798)
CYCLE32_GBT_QUICKBOOKS_INTEGRATION_2026-07-02.md      (commit 8f2d020)
```

Also read Sprint 5-6 specs (already committed, cycles 14-26).

---

## 🗂 WHAT SPRINT 7 BUILDS

### Phase 1: Foundation Tables (run migrations first)
| Order | Table | From Spec |
|-------|-------|-----------|
| 1 | vendors | Cycle 22 |
| 2 | project_entity_links | Cycle 21 |
| 3 | field_submissions_queue | Cycle 24 |

### Phase 2: Core Operations
| Order | Table | From Spec |
|-------|-------|-----------|
| 4 | purchase_orders | Cycle 16 |
| 5 | long_lead_materials | Cycle 16 |
| 6 | project_photos | Cycle 17 |
| 7 | punch_items | Cycle 18 |
| 8 | warranty_items | Cycle 18 |
| 9 | budget_line_items | Cycle 19 |

### Phase 3: Intelligence Tables
| Order | Table | From Spec |
|-------|-------|-----------|
| 10 | vendor_performance_scores | Cycle 22 |
| 11 | schedule_risk_predictions | Cycle 25 |
| 12 | executive_kpis | Cycle 26 |
| 13 | executive_morning_brief | Cycle 26 |

### Phase 4: Client Layer
| Order | Table | From Spec |
|-------|-------|-----------|
| 14 | client_users | Cycle 23 |
| 15 | client_selections | Cycle 23 |
| 16 | client_decisions | Cycle 23 |

### Phase 5: Auth/Identity Tables (NEW — Sprint 7)
| Order | Table | From Spec |
|-------|-------|-----------|
| 17 | users | Cycle 29 |
| 18 | sessions | Cycle 29 |
| 19 | api_keys | Cycle 29 |
| 20 | auth_audit_log | Cycle 29 |

### Phase 6: Event Bus Tables (NEW — Sprint 7)
| Order | Table | From Spec |
|-------|-------|-----------|
| 21 | domain_events | Cycle 30 |
| 22 | domain_event_consumers | Cycle 30 |
| 23 | domain_event_dead_letters | Cycle 30 |

### Phase 7: QuickBooks Tables (NEW — Sprint 7, pending Buck auth)
| Order | Table | From Spec |
|-------|-------|-----------|
| 24 | quickbooks_connections | Cycle 32 |
| 25 | quickbooks_sync_log | Cycle 32 |

---

## 🛠 ROUTER BUILD ORDER

Build in this order:
1. /auth (Unified Identity + RBAC — Cycle 29)
2. /vendors (Cycle 22)
3. /procurement (Cycle 16)
4. /photos (Cycle 17)
5. /punch (Cycle 18)
6. /warranty (Cycle 18)
7. /finance (Cycle 19)
8. /brain (Cycle 21)
9. /mobile (Cycle 24)
10. /predict (Cycle 25)
11. /client (Cycle 23)
12. /executive (Cycle 26)
13. /events (Event bus — Cycle 30)
14. /integrations/quickbooks (Cycle 32 — pending Buck QB auth)

---

## ⚙️ IMPLEMENTATION PATTERN (for every module)

```
1. alembic migration → CREATE TABLE
2. SQLAlchemy model (app/models/)
3. Pydantic schemas (app/schemas/)
4. Service layer (app/services/) — business logic NEVER in routers
5. Router (app/routers/) — thin, delegates to service
6. Tests (tests/) — router goes live only when tests pass
7. emit_event() after every successful write
8. Report in AI_TEAM/SPRINT_7_IMPLEMENTATION_REPORT.md
```

---

## 🔑 THE ONE ARCHITECTURE DECISION YOU MUST NOT GET WRONG

> **"Treat the database as the system of record, and the event bus as the propagation mechanism."**

- Write to DB first
- Emit event AFTER DB commit succeeds
- Never emit before commit
- If event fails, write still stands — event can be re-emitted from domain_events table

---

## 🚫 GOVERNANCE RULES (PERMANENT — NEVER BREAK)

- **Email:** BC is draft-only. /gateway/email/send is SUSPENDED. Never restore without Buck.
- **Buildertrend:** HCI does NOT use Buildertrend. Never reference it.
- **Superintendents:** arrive at 07:00 AM. Morning brief generated at 06:30 AM.
- **QuickBooks:** No HCI → QB writes without explicit Buck approval.
- **No PRs:** All commits directly to main branch.
- **Business logic:** NEVER in routers. Service layer only.

---

## 📋 TEST GATES (every router must pass before going live)

For every router:
- migration test
- create/read test
- validation test
- bad input test
- not-found test
- permission/role test (RBAC)
- event emission test (event emitted after write)

---

## 📄 WHAT CODE REPORTS BACK

When implementation is done, write:
`AI_TEAM/SPRINT_7_IMPLEMENTATION_REPORT.md`

Include:
```
Implemented:
Skipped:
Tests:
Known failures:
Open risks:
Commit hash:
Next recommended step:
```

Then commit and BC will read it and continue.

---

## 🚀 BUCK PENDING ACTIONS (for Code to note)

| Action | Needed For |
|--------|-----------|
| QuickBooks OAuth Client ID + Secret | Cycle 32 implementation |
| Telegram Bot Token (from @BotFather) | Cycle 33 (Telegram) |
| Telegram Numeric User ID (from @userinfobot) | Cycle 33 (Telegram) |
| Name the Telegram Bot | Working name: @HCI_AI_Bot |

---

## 🌐 SYSTEM ENDPOINTS

- **GitHub Repo:** buck-HCI-AI/HCI_AI_Operating_System (main branch)
- **Gateway:** https://speculate-armband-retinal.ngrok-free.dev (check if online)
- **Local FastAPI:** http://localhost:8000
- **Local n8n:** http://localhost:5678
- **API Key:** hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6

---

## ✅ SESSION SUMMARY — WHAT BC COMPLETED TODAY

### Cycles Committed This Session (ALL in AI_TEAM/)
| Cycle | File | Commit | Content |
|-------|------|--------|---------|
| 21 | CYCLE21_GBT_PROJECT_BRAIN_KNO... | b748525 | Knowledge Graph DDL + API |
| 22 | CYCLE22_GBT_VENDOR_INTELLIGEN... | d14ee88 | Vendor Intelligence DDL + API |
| 23 | CYCLE23_GBT_CLIENT_PORTAL... | a0a31f0 | Client Portal DDL + API |
| 24 | CYCLE24_GBT_MOBILE_FIELD_UX... | eb2b032 | Mobile Field UX + offline sync |
| 25 | CYCLE25_GBT_PREDICTIVE_INTELL... | dba2f5e | Predictive Intelligence DDL |
| 26 | CYCLE26_GBT_EXECUTIVE_ANALYT... | 332647e | Executive Analytics + morning brief |
| 27 | CYCLE27_GBT_SPRINT6_RETROSPEC... | 73c475e | Sprint 6 Retro — 9.8/10 |
| 28 | CYCLE28_GBT_SPRINT7_IMPLEMENT... | f796122 | Implementation Plan + Code checklist |
| 29 | CYCLE29_GBT_UNIFIED_IDENTITY... | 4bb4d0e | RBAC — 7 roles, permission matrix |
| 30 | CYCLE30_GBT_EVENT_BUS_EVENT_S... | f93c639 | Event Bus — 60+ events, consumers |
| 31 | CYCLE31_GBT_SPRINT7_RETROSPEC... | 4c0c798 | Sprint 7 Retro — 9.8/10 |
| 32 | CYCLE32_GBT_QUICKBOOKS_INTEGR... | 8f2d020 | QuickBooks OAuth + sync DDL |

### Sprint Scores
- Sprint 5: 9.3/10 (Operational platform)
- Sprint 6: 9.8/10 (Intelligence platform)
- Sprint 7 Spec: 9.8/10 (Implementation blueprint)

---

*Generated by BC (Browser Claude) — pre-shutdown handoff*
*New Code session: read this file first, then begin implementation*
*Never stop.*

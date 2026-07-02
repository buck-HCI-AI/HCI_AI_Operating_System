# CLAUDE CODE — START NOW
**HCI AI OS | Hendrickson Construction, Inc.**
**Last Updated:** 2026-07-02 by BC (Browser Claude) — pre-shutdown handoff
**Current Sprint:** Sprint 7 — Implementation Convergence (see reconciliation note below)

---

## Reconciliation note — 2026-07-02, Claude Code

This file was written on `origin/main` by BC while Claude Code was independently doing
live production-stabilization work (Sprint 3) directly on the running system — the two
branches diverged for ~2 days and were just merged. Sprint 7's specs (Cycles 21-36) are
real and now in this repo, but two items below are stale as of the merge:

- **"Telegram Bot Token — Waiting" / "Telegram Numeric User ID — Waiting"** (Buck Pending
  Actions table below): incorrect. Telegram has been live and working since 2026-07-01 —
  20 sends / 0 failures in the last 24h as of this merge. See `_tg_send_with_id` in
  `gbt_gateway.py`.
- **"Email: BC draft-only. `/gateway/email/send` SUSPENDED"**: the suspension condition
  (approval gate enforced in code) was satisfied 2026-07-01. See the historical note in
  `AI_TEAM/BC_EMAIL_CAPABILITY.md` for the verified current state.

Building the Sprint 7 tables/routers below is a real, undecided scope question — not yet
authorized. `LIVE_PROJECT_STATE.md` is the authoritative source for current live state.

---

## READ THESE FILES FIRST (in order)

1. `AI_TEAM/SPRINT_7_DIRECTIVE.md`  ← **READ THIS FIRST** — immediate actions, build order, governance
2. `AI_TEAM/CLAUDE_CODE_START_NOW.md` ← THIS FILE — full context
3. Cycle specs 28-32 in AI_TEAM/ (see list below)

---

## CURRENT MISSION

**Sprint 7 is the Implementation Convergence Sprint.**

GBT (Chief Architect) ruling: "Sprint 7 should not add new features. The goal is to turn the Sprint 5 and Sprint 6 architecture into running, tested, governed software."

All specs are written. Your job is to build.

---

## WHAT WAS BUILT TODAY (BC session 2026-07-02)

### Spec Files Committed This Session
| Cycle | File | Commit | What It Contains |
|-------|------|--------|-----------------|
| 21 | CYCLE21_GBT_PROJECT_BRAIN_KNO... | b748525 | Knowledge Graph — project_entity_links DDL, /brain router |
| 22 | CYCLE22_GBT_VENDOR_INTELLIGEN... | d14ee88 | Vendor Intelligence — vendors, vendor_performance_scores DDL |
| 23 | CYCLE23_GBT_CLIENT_PORTAL... | a0a31f0 | Client Portal — client_users, client_selections, client_decisions |
| 24 | CYCLE24_GBT_MOBILE_FIELD_UX... | eb2b032 | Mobile Field UX — field_submissions_queue, offline sync |
| 25 | CYCLE25_GBT_PREDICTIVE_INTELL... | dba2f5e | Predictive Intelligence — schedule_risk_predictions |
| 26 | CYCLE26_GBT_EXECUTIVE_ANALYT... | 332647e | Executive Analytics — executive_kpis, executive_morning_brief |
| 27 | CYCLE27_GBT_SPRINT6_RETROSPEC... | 73c475e | Sprint 6 Retro 9.8/10 — Sprint 7 priorities defined |
| 28 | CYCLE28_GBT_SPRINT7_IMPLEMENT... | f796122 | **IMPLEMENTATION PLAN** — dependency order, migrations, test gates |
| 29 | CYCLE29_GBT_UNIFIED_IDENTITY... | 4bb4d0e | Unified Identity + RBAC — 7 roles, permission matrix, DDL |
| 30 | CYCLE30_GBT_EVENT_BUS_EVENT_S... | f93c639 | Event Bus — 60+ event types, consumers, dead letter queue |
| 31 | CYCLE31_GBT_SPRINT7_RETROSPEC... | 4c0c798 | Sprint 7 Retro 9.8/10 — chief architect assessment |
| 32 | CYCLE32_GBT_QUICKBOOKS_INTEGR... | 8f2d020 | QuickBooks — OAuth 2.0, sync DDL (pending Buck auth) |
| - | SPRINT_7_DIRECTIVE.md | ac6f3f1 | Code restart directive — READ FIRST |

---

## ARCHITECTURE DECISIONS (IMMUTABLE)

### The One Event Architecture Rule
> "Treat the database as the system of record, and the event bus as the propagation mechanism."
- Write to DB first. Emit event AFTER commit. Never before.

### The Project Brain Rule (from Sprint 6)
> "Make the Project Brain the central event-driven knowledge graph."
- Every meaningful activity generates: (1) domain event, (2) knowledge graph update, (3) downstream reactions

### Governance Rules (PERMANENT)
- **Email:** BC draft-only. /gateway/email/send SUSPENDED. Never restore without Buck.
- **Buildertrend:** HCI does NOT use Buildertrend. Never reference it.
- **Superintendents:** arrive 07:00 AM. Morning brief at 06:30 AM.
- **QuickBooks:** No HCI → QB writes without Buck approval.
- **No PRs:** All commits to main branch directly.
- **Business logic:** NEVER in routers. Service layer only.

---

## TABLES TO BUILD — COMPLETE LIST

### Already in DB (earlier sprints — verify these exist):
projects, contacts, daily_field_reports, weather_alerts, cpm_activities, rfis, submittals, change_orders, cost_forecast_snapshots, photos (basic), punch_items (basic), warranty_items (basic)

### Sprint 5 Tables (to build/verify):
purchase_orders, long_lead_materials, project_photos (enhanced), punch_items (full), warranty_items (full), budget_line_items

### Sprint 6 Tables (to build):
project_entity_links, vendors, vendor_performance_scores, client_users, client_selections, client_decisions, field_submissions_queue, schedule_risk_predictions, executive_kpis, executive_morning_brief

### Sprint 7 NEW Tables:
users, sessions, api_keys, auth_audit_log (RBAC — Cycle 29)
domain_events, domain_event_consumers, domain_event_dead_letters (Event Bus — Cycle 30)
quickbooks_connections, quickbooks_sync_log (QB — Cycle 32, pending Buck auth)

---

## ROUTERS TO BUILD

Sprint 5: /procurement, /photos, /punch, /warranty, /finance
Sprint 6: /brain, /vendors, /client, /mobile, /predict, /executive
Sprint 7 new: /auth, /events, /integrations/quickbooks

---

## SYSTEM INFO

- **GitHub:** buck-HCI-AI/HCI_AI_Operating_System (main branch)
- **Gateway:** https://speculate-armband-retinal.ngrok-free.dev
- **Local FastAPI:** http://localhost:8000
- **Local n8n:** http://localhost:5678
- **API Key:** hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6

---

## BUCK PENDING ACTIONS (Code cannot proceed until Buck provides)

| Action | Needed For | Status |
|--------|-----------|--------|
| QuickBooks OAuth Client ID + Secret | Cycle 32 QB integration | Waiting |
| Telegram Bot Token (from @BotFather) | Cycle 33 Telegram | Waiting |
| Telegram Numeric User ID (from @userinfobot) | Cycle 33 Telegram | Waiting |

---

## WHAT TO REPORT BACK

When implementation is done, write and commit:
`AI_TEAM/SPRINT_7_IMPLEMENTATION_REPORT.md`

Include: implemented, skipped, tests, failures, risks, commit hash, next step.

BC will read it and continue coordination.

---

*Updated by BC — 2026-07-02*
*New Code session: start with SPRINT_7_DIRECTIVE.md*

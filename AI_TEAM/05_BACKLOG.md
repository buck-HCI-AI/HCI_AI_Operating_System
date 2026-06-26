# 05_BACKLOG.md
**All planned work not yet active — prioritized**
Last updated: 2026-06-25 (Phase 13 — QA Framework)

> VALIDATION-FIRST mode is now active. Gates 1-5 must complete before new features ship.
> All backlog items are tagged: VALIDATED (passed Gate 1+) or UNTESTED (built but no formal evidence).

---

## ACTIVE — Phase 13: QA Gates (in progress)

### Gate 1 — Engineering Validation (Claude Code)
- [ ] Run EV-01 through EV-12 from `docs/TEST_PLAN.md`
- [ ] Document all results in `docs/TEST_RESULTS.md`
- [ ] Fix any P0/P1 defects found
- [ ] Create Desktop/HCI_Smoke_Test.command

### Gate 2 — Integration Testing (Claude Code)
- [ ] Run TS-01 through TS-09 from `docs/TEST_PLAN.md`
- [ ] Document results in `docs/TEST_RESULTS.md`
- [ ] Investigate KI-010 (drive_memory persistence)

### Gate 3 — Workflow Acceptance (Claude Code + Buck)
- [ ] Run all ⬜ test cases in `docs/WORKFLOW_TEST_MATRIX.md`
- [ ] Fix KI-003 (vendor embed pipeline)
- [ ] Fix KI-004 (workflow_events for WF-001/002/005/006)

### Gate 4 — UAT (Buck)
- [ ] Walk Buck through `docs/UAT_PLAN.md` Tier 1 (5 scenarios)
- [ ] Collect sign-off in `docs/UAT_RESULTS.md`

### Gate 5 — Pilot + Go-Live Authorization (Buck)
- [ ] Run 5-day pilot on one active project
- [ ] Document in `docs/PILOT_READINESS_REPORT.md`
- [ ] Collect Buck's explicit go-live approval

---

## Validated Components (production-eligible after gates pass)

| Component | Status | Evidence |
|-----------|--------|---------|
| PostgreSQL schema (22 tables) | Validated in Test | Phase 12 audit |
| Redis cache | Validated in Test | Phase 7 testing |
| HubSpot Sync (WF-SYNC-HS) | Validated in Test | Phase 12 — 306 deals synced |
| Drive Sync (WF-SYNC-DRIVE) | Validated in Test | Phase 12 — 2,335 vectors |
| WF-SUPER (superintendent log) | Validated in Test | Phase 9 — all stages confirmed |
| WF-PM daily review | Validated in Test | Phase 9 — synthesis confirmed |
| WF-REPORT-DAILY | Validated in Test | Phase 10 — 2.5KB HTML confirmed |
| WF-REPORT-EXEC | Validated in Test | Phase 10 — 3.3KB HTML confirmed |
| project-brain | Validated in Test | Phase 7 — Q&A working |
| bid-intelligence | Validated in Test | Phase 7 — 119 packages confirmed |
| schedule-intelligence | Validated in Test | Phase 9 — analyze_log working |
| risk-intelligence | Validated in Test | Phase 9 — 35+ flags confirmed |

---

## Untested Components (need Gate 3 before go-live)

> Phases 1-7 complete. Phases 8-11 are the remaining backlog.
> See docs/IMPLEMENTATION_SEQUENCE.md for dependency graph.

---

## ✅ Phase 8: Workflow Engine Core — COMPLETE (2026-06-25)

- BL-008-1 ✅ vendor_id FK: 19/26 matched; 7 unresolvable
- BL-008-2 ✅ Document ingest: ingest_document() → ingest.py pipeline end-to-end
- BL-008-3 ✅ workflow_events table live with 3 indexes
- BL-008-4 ✅ GET /api/v1/workflows + POST /api/v1/workflows/{id}/trigger

---

## ✅ Phase 9: Field and PM Workflows — COMPLETE (2026-06-25)

- BL-009-1 ✅ WF-SUPER: 7-stage pipeline; daily_logs extended with 9 columns
- BL-009-2 ✅ Schedule Intelligence: analyze_log() + schedule_variance table + Claude analysis
- BL-009-3 ✅ WF-PM: daily_review + weekly_report; Claude synthesis of all services
- BL-009-4 ✅ Bid email detection in WF-006; writes to bid_entries
- BL-009-5 ✅ rfis + submittals tables; WF-006 detects and writes both

---

## ✅ Phase 10: Reporting and Dashboards — COMPLETE (2026-06-25)

- BL-010-1 ✅ Reporting Framework: 5 report types, auto-wired into WF-SUPER and WF-PM
- BL-010-2 ✅ Dashboard: /dashboard live; health, bids, risks, daily logs, Q&A; 18KB single-file HTML

---

## ✅ Phase 11: Production Hardening — COMPLETE (2026-06-25)

- BL-011-3 ✅ API key auth: key live, dashboard wired, middleware enforcing on /api/v1/*
- BL-011-4 ✅ Backup: pg_dump + Qdrant snapshots daily 2 AM, 7-day rotation, desktop .command
- BL-011-5 ✅ Monitoring: 5-min health check, auto-restart (3x), disk alert, email on failure
- BL-011-1/2 ⏳ Mac mini migration: playbook at infrastructure/setup_mac_mini.sh — awaiting hardware

### BL-002: GitHub Remote
```bash
# After Buck runs: ! gh auth login
gh repo create HCI_AI_Operating_System --private \
  --source=/Users/buckadams/HCI_AI_Operating_System \
  --remote=origin --push
```

---

## P1 — After Data Stack

### BL-003: Memory Ingestion Pipeline
- Read 3 project bid sheets → insert into `bid_entries` (Postgres)
- Pull HubSpot contacts + deals → insert into `vendors`, `projects`
- Embed and load → Qdrant `vendor_memory` + `bid_memory`
- Script: `/03_Source_Code/ingestion/`
- **Needs:** ChatGPT schema spec first (see 02_ACTIVE_WORK.md)

### BL-004: WF-001 New Project Setup
- Manual/webhook trigger
- Creates: HubSpot deal, Google Sheet (copy template), Drive folder, project doc

### BL-005: WF-002 Meeting Intelligence
- Email trigger
- Parses notes → extracts action items → HubSpot tasks + Qdrant meeting_memory

### BL-006: WF-003 Morning Brief
- Daily 7AM MDT
- Priorities, open bids, project status → email to Buck

### BL-007: WF-004 Daily Log
- Manual or end-of-day trigger
- Site notes, progress, issues → Postgres + Qdrant

### BL-008: WF-005 Lessons Learned
- Project close or manual
- What worked/didn't → `lessons_learned` (Postgres + Qdrant)

---

## P2 — Phase 3 / API Layer

### BL-009: FastAPI Skeleton
- `/03_Source_Code/api/main.py`
- Routers: projects, vendors, bids, memory/search, workflows/trigger

---

## P3 — Agents

### BL-010: Agent Definitions
- Executive, PM, Bid, Procurement, Historian, Relationship
- Prompt library: `/11_Prompts/agents/`
- Agent code: `/10_Agents/`

---

## P4 — Dashboards

### BL-011: Executive Dashboard
### BL-012: PM Dashboard
### BL-013: Universal Search

---

## Icebox (no timeline)

- Google Drive sync / backup automation
- Photo ingestion pipeline (site photos → `photo_memory`)
- SMS/text message integration for field crew
- Subcontractor portal

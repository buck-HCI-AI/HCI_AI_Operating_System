# CHANGELOG
## HCI AI Operating System — Hendrickson Construction, Inc.

All significant changes to the HCI AI Operating System are documented here.
Format: [Agent] Description — Date

---

## [Extended Audit + Data Cleanup] — 2026-06-28 — n8n Restored, Vendor Dedup, Governance

### Claude Code — Extended Audit Pass (Buck directive: "keep mining, keep fixing")
- **n8n API restored**: Docker container restart cleared VirtioFS SQLite I/O error; API key valid (exp 2026-07-15); 42 active / 50 total workflows confirmed via API
- **Approval queue corrected**: 986 entries are LEGITIMATE pending vendor candidate approvals from HubSpot mining (986 unique companies awaiting Buck review); only 9 true dups deleted; total 1,020 remain
- **Vendor registry dedup**: 393 → 274 unique vendors; 119 duplicates removed (caused by multi-contact companies in HubSpot); 1 bid_entry FK ref fixed; Poss Architecture (id=393, Marc Winkler) added
- **seed_postgres.py fixed**: Added company-level ILIKE dedup check before INSERT to prevent future vendor duplicates from seed runs
- **Duplicate n8n workflow archived**: hMIMIUy3fSSVDJcr → "ARCHIVED — AUTO-NIGHTLY-AUDIT (duplicate import 2026-06-27)"
- **AUTOMATION_GOVERNANCE.md completed** (INT-010): Full inventory of all 50 n8n workflows (42 active, 8 inactive) + 18 Python/FastAPI workflows documented in Part 5
- **P0 gaps reconciled**: P0-001/002/003 (stale n8n workflows) already retired from prior session; confirmed via live API audit
- **Schedule variance sign bug**: RESOLVED — gbt_gateway.py already uses MAX(ABS(variance_days)); actual data shows variance_days=0 (test data, no real delays submitted)
- **BOOK_00/03**: vendor count updated 392→274; approval_queue description corrected; bid_entries FK note added
- **AI_TEAM/00_STATUS.md**: n8n API status fixed (restored, not broken); vendor count corrected; P0 gaps updated; Go-Live exceptions updated
- **CURRENT_SPRINT.md**: Gate 5 blockers updated — n8n ✅, approval queue ✅, new blockers: 246GW procurement gaps + schedule variance sign bug
- **Published to Drive:** HCI_AI_OS_RECONCILIATION_REPORT_2026-06-28 (ID: 13SYPMZlo03vi0M_hkSoOQwxMDP3wfU1x394EsR1LjBs)
- **GBT Handoff published:** GBT_HANDOFF_RECONCILIATION_COMPLETE_2026-06-28 (ID: 1XofoXSbfPXSFbXLnAK_ElzoegV6JJ0iC_GrfURUpMWE)

---

## [Deep Reconciliation Audit] — 2026-06-28 — Full System Checks + 11 Corrections

### Claude Code — Reconciliation Audit (Buck directive: "read everything, check everything, correct, publish")
- BOOK_00/08: Updated Stack 2 from "WF-007 only" to full 50-workflow n8n catalog; Stack 1 renamed to "18 Python workflows"
- AI_TEAM/00_STATUS.md: Updated "Workflow Engine" heading from "18 Active" to "68 Active (18 Python + 50 n8n)"; split table into two stacks
- BOOK_00/12: Status updated from "Spec complete — build in Phase 9.2" to ✅ LIVE (schedule intelligence running since 2026-06-26/28)
- BOOK_00/13: Status updated from "Spec complete — build in Phase 10" to ✅ LIVE (reporting via GBT Gateway + n8n)
- BOOK_00/03: All row counts updated to reflect live DB (5 projects, 163 packages, 1,275 schedule items, 1,023 approval queue)
- AI_TEAM/00_STATUS.md: Last Updated, Gate 5 status (3→5 projects), n8n count (0→50), Go-Live verdict added
- CURRENT_SPRINT.md: Gate 5 table updated (added 246GW + 83SB rows; BUILD-1–6; Architecture Freeze)
- hci_os.daily_logs: 6 duplicate rows deleted (101F: 4, 64EW: 2)
- hci_os.kpi_snapshots: 8 duplicate rows deleted
- n8n AUTO-HANDOFF-PROCESSOR Build Notification node fixed (stdout → payload.output)
- api/routers/mvp_ops.py pm_weekly_review(): bid_packages query fixed (status='active'/'closed' → all packages with correct status breakdown)
- **Published to Drive:** HCI_AI_OS_RECONCILIATION_REPORT_2026-06-28 (ID: 13SYPMZlo03vi0M_hkSoOQwxMDP3wfU1x394EsR1LjBs)
- **GBT Handoff:** GBT_HANDOFF_RECONCILIATION_COMPLETE_2026-06-28 (ID: 1XofoXSbfPXSFbXLnAK_ElzoegV6JJ0iC_GrfURUpMWE)
- **Open items flagged:** LIVE_PROJECT_STATE schedule variance sign bug, 1,023 stale approval queue entries, n8n API key rotation needed

---

## [Overnight Build + 246GW Init] — 2026-06-28 — Operational Systems + Project 5

### Claude Code — Overnight Build (BUILD-1 through BUILD-6)
- BUILD-1: `POST /gateway/admin/backfill-kpis` — recalculate KPI snapshots from live DB for all active projects
- BUILD-2: `POST /gateway/admin/backfill-risks` — file missing risk records for high/critical schedule_variance entries; fixed BP-06 silent failure (risk INSERT now isolated in try/except with logging)
- BUILD-3: AUTO-SCHEDULE-VARIANCE-WEEKLY — n8n workflow (ID: jFzQFu9MybnWtrZd), Monday 07:00 MST, GET all project schedules → sync-live-state → backfill-kpis → ntfy push
- BUILD-4: `POST /gateway/drive/export-schedule-csv` — export project schedule items to Drive CSV; 246GW CSV live (file ID: 17-ed2spTt7mVQLc311-VE1qo-BIpb8OG)
- BUILD-5: Mobile approval endpoints — `GET /gateway/approvals/pending`, `POST /gateway/approvals/{id}/approve`, `POST /gateway/approvals/{id}/reject`
- BUILD-6: `POST /gateway/admin/sync-live-state` — pull live DB data, update LIVE_PROJECT_STATE.md table and patch Drive (file ID: 1Jjug6nbx-mGN9v4GrEyofkGXY5nMHvpP)
- LaunchAgent KeepAlive bug fixed: `com.hci.api-server.plist` corrected Python path + WorkingDirectory — was restarting with stale process on every kill
- `_require_key(request)` function added to gbt_gateway.py (was referenced but undefined)
- kpi_snapshots status values corrected: `green/yellow/red` (was `on_track/warning/critical` — check constraint violation)
- approval_queue table name corrected (was `approval_queue_items` — table doesn't exist)
- project_schedule_items column refs corrected: `task_type, assignee, completion_pct` (was `phase, trade`)
- Drive auth corrected: all gateway endpoints use `from integrations.credentials import get_google_token` directly (was calling non-existent `/api/v1/google-auth/token` endpoint)
- bid_packages project_id query corrected: `WHERE project_id = %s` (was `%s::text` on integer column)

### Claude Code — 246 Gallo Way (Project 5 / id=8) Initialization
- Project 246 Gallo Way seeded: id=8, scope=New Construction Chaparral Lot 7, HubSpot deal 321358358216
- 280 schedule items imported from MS Project xlsx (Drive file: 167vMu6cHtBFyCerbCQoH1-Y_E8MzQSqV), activity_id format 246GW-XXXX
- 44 bid packages created across CSI divisions 01–32: 19 awarded ($6,314,913 committed), 18 bids_receiving, 7 not_started
- 246GW code added to PILOT_PROJECTS in mvp_ops.py and CODE_MAP/NAME_MAP/SCOPE_MAP/HS_MAP in gbt_gateway.py
- PM endpoint bid_packages query fixed: now returns full package list with status breakdown (was returning stale count using wrong status values)
- Drive deliverables: 246_Gallo_Way_Project_Analysis.md, 246GW_GBT_PROJECT_BRIEF.md, 246GW_Schedule_Export.csv, 246GW_BID_PACKAGES_GBT_DIRECTIVE.md, 246GW_FULL_JOB_STATUS_REPORT_2026-06-28.md

### Claude Code — Data Integrity + Schema
- `GET /gateway/agent/handoff/document-types` added — 13 valid document_type values exposed for GBT
- document_type enum list `_DOCUMENT_TYPES` defined in gbt_gateway.py (13 types)
- 6 duplicate daily_log rows removed (101F: 4 dups, 64EW: 2 dups on 2026-06-25)
- 8 duplicate kpi_snapshot rows removed
- WF-009 data integrity audit: zero orphan records across all FK relationships
- n8n AUTO-HANDOFF-PROCESSOR Build Notification code fixed: was referencing `.stdout` (undefined), now correctly reads `.payload.output[]` from process-inbox response
- Full system audit written to Drive: HCI_AI_OS_SYSTEM_AUDIT_2026-06-28.md

### Architecture Freeze v1.0 — 2026-06-28
- Foundation declared frozen: 427 endpoints, 47 tables, 40 workflows, GBT Gateway Bridge v1.0
- All structural changes require ACR from GBT + Buck approval
- New endpoints added above are Sprint 2/Overnight build scope — pre-freeze deliverables
- Sprint 3 starts post-Gate 5 (2026-07-01)

---

## [Sprint 0] — 2026-06-26 — Repository Foundation & Governance

### Added by Browser Claude (GitHub Administrator)
- HCI_AI_CONSTITUTION.md — foundational law for all AI agents
- AI_TEAM_CHARTER.md — roles, authorities, and boundaries for every AI
- AUTOMATION_GOVERNANCE.md — rules governing all automations
- APPROVAL_GATES.md — Gate A through Gate H approval framework
- SPRINT_OPERATING_MODEL.md — how sprints run and close
- AI_WORKFLOW_ROLES.md — workflow ownership by agent
- PROJECT.md — canonical project backlog and integration registry
- TASKS.md — 80-task register across Sprint 0 through Sprint 9
- CONTRIBUTING.md, PULL_REQUEST_TEMPLATE.md, CODEOWNERS
- 5 GitHub issue templates (architecture, bug, feature, docs, workflow)
- GitHub Project + Milestones (Sprint 0–10) + 22 labels
- Houzz Browser Intelligence workstream (6 design docs)
- IMPLEMENTATION_INTEGRATION_PLAN.md — integration strategy
- PROGRAM_REPOSITORY_STATUS.md, PROGRAM_REPOSITORY_INVENTORY.md
- REPOSITORY_RELATIONSHIP_MAP.md, LIVE_PROJECT_STATE_TEMPLATE.md
- CURRENT_SPRINT.md — Sprint 1 System Verification plan
- LIVE_PROJECT_STATE.md — activated from template

### Added by Claude Code (Lead Implementation Engineer)
- Data stack live: PostgreSQL 16, Qdrant, Redis (Docker)
- Memory ingestion pipeline: Postgres + Qdrant populated
- FastAPI layer v1 (versioned /api/v1/*) — 427 endpoints, 18 intelligence services
- WF-001 through WF-006: new project, meeting intelligence, morning brief,
  daily log, lessons learned, inbox review
- WF-007: AI Bid Leveling Engine (live, n8n)
- HubSpot integration: deals, contacts, companies
- Google Drive integration: files, folders, uploads
- Google Sheets integration: bid trackers (3 active projects)
- Microsoft 365 / Graph API: email read/send/draft
- MCP server: 26 tools (Phase 1)
- Platform Integration Layer: 27 SOPs (Plan Review → Field Inspection)
- 5 shared platform services: identity, event bus, notifications, audit trail, search
- 48/48 MVP Sprint 1 tests passing — Gate 5 Pilot activated
- 4 active projects seeded: 64 Eastwood, 101 Francis, 1355 Riverside, 83 Sagebrusch
- Vendor registry: 392 vendors, 258 with CSI divisions
- Historical cost: 21 records from 655 S Garmisch
- Lessons learned: 10 records (7 Garmisch, 3 gate tests)
- Business processes: 27 mapped from SOP library
- Qdrant healthcheck fixed (bash TCP — no curl/wget required)
- SQL fallback added to historical cost search
- ProjectMining bug fixed (/candidates → /records)
- P1 data population: business_processes, lessons_learned, historical_cost_records tables

---

## [ACR-001] — 2026-06-26 — MCP Chief Architect Integration Tools

### Added by Claude Code
- 5 new MCP tools for Chief Architect (ChatGPT) integration:
  - ReadLiveProjectState — reads LIVE_PROJECT_STATE.md
  - ReadCurrentSprint — reads CURRENT_SPRINT.md
  - ReadAutomationRegistry — n8n + Python + MCP tool inventory
  - ReadDecisionLog — architecture/implementation decisions from DB
  - ReadRepositoryStatus — git state + service health
- Total MCP tools: 31
- ProjectMining 404 bug fixed

---

## [ACR-002] — 2026-06-26 — Universal Project State Access

### Added by Claude Code
- GET /project-state — public endpoint, no auth required
  Returns LIVE_PROJECT_STATE.md as JSON or raw markdown
  ChatGPT can call this at the start of every session
- GetProjectState MCP tool — live dynamic snapshot from all services
- Total MCP tools: 32
- LIVE_PROJECT_STATE.md uploaded to Google Drive (public, always current)

---

## [Merge] — 2026-06-26 — Repositories Unified

### Claude Code
- Merged feature/data-architecture-document-storage into main
- All implementation code + all governance docs now on single main branch
- GitHub repo made public (after credential cleanup)
- All hardcoded credentials removed from 12 code files → .env
- HCI_API_KEY, POSTGRES_PASSWORD, REDIS_PASSWORD in .env (gitignored)
- reports/ directory structure created
- CHANGELOG.md, TASKS.md, CURRENT_SPRINT.md updated

---

## Pending — Sprint 1

See CURRENT_SPRINT.md and TASKS.md for active task board.
Sprint 1 begins when Buck issues the Sprint 1 ACR.

---

*CHANGELOG.md | HCI AI Operating System | Hendrickson Construction, Inc.*
*Maintained by: all AI agents | Authority: HCI_AI_CONSTITUTION.md*

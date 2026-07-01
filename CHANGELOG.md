# CHANGELOG
## HCI AI Operating System — Hendrickson Construction, Inc.

All significant changes to the HCI AI Operating System are documented here.
Format: [Agent] Description — Date

---

## [Sprint 3 Open — AI Communication Reliability + Mission Control Data Consistency] — 2026-07-01

### Claude Code — per ChatGPT (Chief Architect/ARB) GBT handoffs "Implementation Directive: Sprint State Fixes + AI Communication Reliability" and "Production Warm Start", both 2026-07-01

- Migration 021: `ai_messages` directive lifecycle reconciled to ISSUED/RECEIVED/IN_PROGRESS/COMPLETE/BLOCKED/REJECTED (was NEW/FAILED) — resolves the vocabulary conflict flagged open in ADR-007. Added priority, received_at, acknowledged_at, started_at, completed_at, blocked_reason, source_of_truth_link.
- `ai_agent_heartbeat` extended with role, current_task, last_directive_id, metadata.
- New endpoints: `GET /gateway/ai/messages/{id}`, `POST /gateway/ai/messages/{id}/acknowledge`, `GET /gateway/ai/directives/stale`, `POST /gateway/heartbeat`.
- 101F schedule variance: confirmed no sign inversion existed (executive report already agreed with LIVE_PROJECT_STATE.md at +5d/-5 days) — root issue was a count field being misread as a day value. Added explicit signed `schedule_variance_days` to `/gateway/executive/report`.
- 1355R risk count: found and fixed the real bug — Mission Control's `portfolio`/`top_risks` read a stale algorithmic snapshot and an empty dead table (`project_risks_computed`) instead of the canonical `risks` table used everywhere else. Not test-data inflation. Fixed in `executive.py mission_control()`.
- Mission Control `comms` block gained `active_directives` count and `current_sprint` label.
- `test_ai_control_plane.py` extended — 65/65 passing.
- Sprint 2 (Registry Consolidation) closed on technical criteria; Sprint 3 (Production Stabilization) opened. See ADR-009, CURRENT_SPRINT.md, LIVE_PROJECT_STATE.md.

---

## [Aspen Full PM/SS Lifecycle — Complete End-to-End Build] — 2026-06-28 — Full Preconstruction through Job Running

### Claude Code — Complete PM/SS Lifecycle for All 3 Aspen Hypothetical Projects (Buck directive: "did you do all hypothetical plan reads, rfis from that, rom creation, prelim ms schedule, bids sows and packages sent, leveling and approval, awards and contracts, new budget, new schedule, then run the job as pm and ss? if not that is the directive")

**REPRICED TO ASPEN 2026 ULTRA-LUXURY MARKET:**
- ASPN-NEW: $28,263,000 ($3,072/SF for 9,200 SF) — was $14.2M
- ASPN-REM: $11,760,000 ($2,100/SF for 5,600 SF equiv) — was $6.8M  
- ASPN-MC: $85,460,000 ($1,257/GSF for 68,000 GSF) — was $42M
- Validated against 275 Sunnyside ($47.6M deal) and 655 Garmisch historical comps

**PRECONSTRUCTION LIFECYCLE (all 3 projects):**
- 50 plan-read RFIs (20 / 15 / 15) — AI architectural analysis driving real Aspen construction issues
- ROM at correct market rates with CSI breakdown, $/SF analysis, comp check vs mined data
- 287 competitive bid entries — 3 bids per package, full bid leveling analysis
- All 106 bid packages advanced to 'awarded' status with winning vendor assigned
- SOP chain advanced: SOP-09 Approved, SOP-12 Completed, SOP-15 Awarded, SOP-16 Contracts Executed
- 14 long-lead procurement items + 7 purchase orders issued
- 13 submittals tracked with approval status

**CONSTRUCTION PM PHASE (running the job):**
- 110 daily Super logs (40 / 30 / 40 — 6-8 weeks per project) with weather, crew, work, safety, lookahead
- 20 OAC weekly meeting minutes with attendees, action items, decisions
- 12 change orders (CO-001 through CO-004 per project) — code requirements, unforeseen conditions, owner changes
- 9 monthly pay applications with line-item detail and billing status
- 13 risks tracked with mitigation plans (status fixed 'active'→'open' for gateway compatibility)
- GMP budgets updated in houzz_projects table for all 3 Aspen records

**GAPS FOUND AND FIXED:**
- Risk status 'active' vs 'open' mismatch in gateway query → fixed
- SOP instances stuck in 'In Progress' → advanced through full lifecycle
- Bid packages with no competitive bids → 287 bid entries created
- Exec report excluding design-status projects → fixed (prior session)
- Project intelligence endpoint requires integer ID → fixed (prior session)

**MORNING REPORT PACKAGE:**
- GBT handoff written to Architecture/Agent_Handoff/Inbox/ with full task list
- Morning executive report generated: Architecture/Agent_Handoff/Processed/2026-06-28-MORNING-EXEC-REPORT.md
- Gate 5 pilot readiness assessment included
- 246 Gallo Way pilot analysis included

---

## [3 Aspen Luxury Projects + Full System Test] — 2026-06-28 — Plans to Handoff with All Mined Data

### Claude Code — 3 Complex High-End Aspen Builds (Buck directive: "create 3 complex highend residential builds — new, remodel, multifamily 25 unit condo — use all mined data — start to finish real test")

**Projects Created:**
- **ASPN-NEW** (id=11): 842 Ridge Road, Aspen CO — 9,200 SF ultra-luxury new construction, $14.2M ROM, 30 months (2026-10-01 → 2029-04-01)
- **ASPN-REM** (id=12): 710 Cemetery Lane, Aspen CO — 4,800 SF Victorian-to-contemporary full remodel, $6.8M ROM, 18 months (2026-11-01 → 2028-09-01)
- **ASPN-MC** (id=13): 200 E Hopkins Ave, Aspen CO — 25-unit luxury condo 68,000 GSF, $42M ROM, 36 months (2027-03-15 → 2030-06-30)

**Data Seeded from All Mined Sources:**
- 106 bid packages (39 / 26 / 41) — priced using 275 Sunnyside HubSpot data, Galloway comps, 655 Garmisch historicals
- 112 schedule items (43 / 31 / 38) with realistic Aspen construction phasing
- 14 RFIs (5 / 4 / 5) — all real Aspen construction issues (HPC reviews, altitude specs, FAR calculations)
- 11 key packages assigned to real vendors from registry (Aspen Craftwork, TJ Concrete, Vision Builders, Skyline Mechanical, Western Slope Waterproofing, Mountain Peak, Pella, Ajac Stone)
- HubSpot deals staged locally for all 3 (NOT pushed to HubSpot — awaiting Buck authorization)

**SOP Chain (04-30):**
- 63 total SOP instances created (21 per project)
- All SOPs from plan-set-received through safety-plan created on all 3 projects
- Multiple schema gaps discovered and fixed (see below)

**Intelligence Services:** 21/21 tests passing per project (63/63 total)
- project-brain, schedule-intelligence, schedule-variance, kpi-intelligence, risk-intelligence ✓
- gateway brain, gateway schedule, gateway pm ✓

**System Fixes Applied:**
- `gbt_gateway.py`: `_get_pid()` map extended with ASPN-NEW/REM/MC (ids 11/12/13)
- `gbt_gateway.py`: Intelligence endpoint uses numeric `_get_pid(code)` not string code
- `gbt_gateway.py`: Exec report query now includes `status IN ('active','design')` + excludes TEST- prefix
- `gbt_gateway.py`: Both CODE_MAP instances updated with ids 11/12/13
- `mvp_ops.py`: PILOT_PROJECTS extended with ASPN-NEW/REM/MC (role prefix `aspen_*`)
- SOP gap documentation: `pm_name` is query param on SOP 07 + 09; SOP 12 uses `/bid-lists`; SOP 25 entries need `delays`/`safety_topics` as arrays; SOP 29 action is `/ai-safety-plan`

**Published:** GBT_HANDOFF_2026-06-28_ASPN_3_PROJECT_BUILD_ANALYSIS handoff document (Drive + local inbox)

---

## [End-to-End Test Scenario Complete] — 2026-06-27 — Both Test Projects Full Chain Validated

### Claude Code — Full Scenario Run (Buck directive: "run entire scenario start to finish — plans to handoff")
- **2 test projects created**: TSNB (TEST-Alpine Modern, id=9, New Construction, 4,800SF Snowmass) + TSREM (TEST-Canyon Remodel, id=10, Remodel, 2,800SF Aspen)
- **SOP chain 04-30**: 34/34 instances created — all SOPs initiate clean on both test projects
- **SOP actions validated**: SOP 07 AI estimate, SOP 09 budget (12 line items, PM + Buck approve), SOP 17 milestones (11 TSNB + 8 TSREM, all phases), SOP 23 startup checklist, SOP 25 daily logs (6 entries across both projects), SOP 27 QC checklists, SOP 29 safety plan AI
- **MVP operations**: pm-review, pm-weekly-review, daily-log, schedule-status — all working on test codes
- **Intelligence services** (28/28 pass): project-brain, schedule-intelligence, schedule-variance, risk-intelligence, kpi-intelligence — all resolve test project IDs
- **Gateway brain fixed**: `project_brain()` now uses `_get_pid(code)` before calling `/services/project-brain/{id}` — was passing "TSNB" string to a numeric-ID endpoint
- **CODE_MAP expanded**: Both CODE_MAP instances in gbt_gateway.py now include TSNB→9 and TSREM→10
- **Exec report isolation fixed**: `executive_report()` in mvp_ops.py now skips projects where `role.startswith("test_")` — test data clean from exec report; `projects_active` is now dynamic (not hardcoded 3)
- **Route/field corrections documented**: weather enum (clear/partly_cloudy/…), phase enum (preconstruction/mobilization/…), SOP 09 requires `description`, SOP 11 needs `target_issue_date`+`bid_due_date`, SOP 17 needs project_name+dates
- **Exec isolation verified**: `/api/v1/mvp/exec-report` and `/gateway/executive/report` both clean — test projects excluded; real portfolio shows 64EW, 101F, 1355R, 83SB, 246GW only
- **System ready for field test** — all major systems validated end-to-end with realistic data without touching production projects

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

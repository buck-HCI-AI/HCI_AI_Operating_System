# Architecture Handbook CHANGELOG

> Maintained by: Claude Code (Implementation Engineer)
> Authored by: ChatGPT + Buck Adams (Chief Architect)

---

## v2.2 — 2026-06-27 | BTW-10 — Continuous Discovery Engine (Infrastructure)

**Trigger:** BTW-10 — Continuous Discovery Engine (Strategic Backlog)

**Changes:**
- `services/continuous_discovery/` — new service:
  - `detection.py` — change detection engine: compares connector sync state vs current DB record counts; stale thresholds (HubSpot: 2h, Houzz: 26h); detects: `CHANGES_DETECTED | NO_CHANGES | STALE | ERROR | NO_DATA`; logs scans to `platform_events`
  - `routes.py` — 3 endpoints:
    - `GET /services/continuous-discovery` — service info + schedule + flow description
    - `GET /services/continuous-discovery/detect` — run detection across all connectors
    - `GET /services/continuous-discovery/detect/{name}` — single connector detection
    - `POST /services/continuous-discovery/scan-and-notify` — detect + log to platform_events (used by n8n)
- `workflows/n8n/AUTO-CONTINUOUS-DISCOVERY.json` — dual-trigger workflow:
  - HubSpot: every hour (cron `0 * * * *`)
  - Houzz: nightly 02:00 (cron `0 2 * * *`)
  - Evaluates status → ntfy only if CHANGES_DETECTED / ERROR / STALE
- `api/main.py` — continuous-discovery service registered
- `tests/test_btw10_continuous_discovery.py` — 55/55 tests
- **Deferred (Buck-gated):** Houzz Browser extraction → full delta ingest flow (step 3+ of BTW-10 flow)
- Health maintained: **95/100**

---

## v2.1 — 2026-06-27 | BTW-9 — Company Knowledge Graph

**Trigger:** BTW-9 — Company Knowledge Graph (Strategic Backlog)

**Changes:**
- `services/knowledge_graph/` — new service directory:
  - `graph.py` — entity loaders (projects, vendors, subcontractors, contacts, POs, RFIs, change orders, bids); `build_graph()` returns all nodes + edges; traversal queries: `find_by_vendor()`, `find_similar_issues()`, `find_product_history()`, `cross_project_summary()`
  - `routes.py` — 5 endpoints:
    - `GET /services/knowledge-graph` — service info
    - `GET /services/knowledge-graph/graph` — full graph (?node_type= filter)
    - `GET /services/knowledge-graph/summary` — cross-project relationship summary
    - `GET /services/knowledge-graph/vendor?name=` — all projects vendor worked on (as sub/supplier/bidder)
    - `GET /services/knowledge-graph/issues?q=` — similar RFIs + COs + daily logs matching keywords
    - `GET /services/knowledge-graph/product?q=` — product history across projects (who installed, which POs, tasks)
- `api/main.py` — knowledge-graph service registered in service layer + list_services()
- `tests/test_btw9_knowledge_graph.py` — 60/60 tests
- Health maintained: **95/100**

**Note:** Semantic vector search (Qdrant cosine similarity) deferred to BTW-10 — depends on natural language embeddings and data flowing through connectors.

---

## v2.0 — 2026-06-27 | BTW-7 — Superintendent Field Enhancements (Unblocked Subset)

**Trigger:** BTW-7 — Superintendent Workspace (Strategic Backlog)

**Changes:**
- `api/routers/operations.py`: 4 new superintendent field endpoints:
  - `GET /superintendent/{project_id}/deliveries` — PO delivery tracking (expected today, this week, overdue, confirmed received) from `houzz_purchase_orders`
  - `GET /superintendent/{project_id}/inspections` — inspection scheduling (due today, overdue, upcoming 7d) from `houzz_schedule_items` + `houzz_tasks` LIKE pattern
  - `GET /superintendent/{project_id}/materials` — material tracking by status, value summary, critical-needed-soon (within 3 days) from `houzz_purchase_orders`
  - `POST /superintendent/{project_id}/voice-note` — voice note injection: accepts transcription + note_type + location, formats with tags ([OBS]/[ISSUE]/[DECISION]/[SAFETY]/[INSPECTION]), saves to `houzz_daily_logs`
- `tests/test_btw7_field_enhancements.py`: 97/97 tests across 3 projects + all note types
- **Deferred (Buck-gated):** Photo documentation (`houzz_files`) — requires Houzz Browser extraction first
- Health maintained: **95/100**

---

## v1.9 — 2026-06-27 | BTW-5 — Role Intelligence: 5 New Role Consoles

**Trigger:** BTW-5 — Role Intelligence (Strategic Backlog)

**Changes:**
- `api/routers/operations.py`: 5 new role console endpoints added:
  - `GET /owner/dashboard` — Company-wide command: portfolio health, executive inbox, missions blocked, open bids/RFIs/COs, AI ROI
  - `GET /office/queue` — Admin work queue: pending approvals, overdue RFIs, open bids, pending submittals, upcoming meetings
  - `GET /accounting/{project_id}/financials` — Per-project financial health: budget vs actual (houzz_budget), change order status + amounts, open POs
  - `GET /client/{project_id}/status` — Client-facing project status: schedule milestones, change orders pending signature, open RFIs, open decisions
  - `GET /trade/{project_id}/my-work` — Trade partner work queue (filtered by `?trade=` param): open tasks, 14-day schedule, open POs, RFIs
- All 5 endpoints return structured JSON with health signal (GREEN/YELLOW/RED) + prioritized action list
- `tests/test_btw5_role_consoles.py`: 115/115 tests across 3 projects and multiple trade filters
- Health maintained: **95/100** | 18/18 API endpoints healthy

---

## v1.8 — 2026-06-27 | BTW-6 — Executive Command Center: Weekly + Monthly Reports

**Trigger:** BTW-6 — Executive Command Center (Strategic Backlog)

**Changes:**
- `workflows/n8n/AUTO-WEEKLY-EXEC.json` — Friday 16:00 weekly executive report; pulls company report + missions + inbox in parallel; builds health/mission/approvals summary; writes `reports/weekly/exec-YYYY-MM-DD.md`; ntfy with elevated priority when projects at risk or missions blocked
- `workflows/n8n/AUTO-MONTHLY-REVIEW.json` — 1st of month 09:00 business review; pulls mission-control + autonomy ROI + portfolio in parallel; builds AI ROI table, mission summary, top automation opportunities, next-month priorities; writes `reports/monthly/exec-review-YYYY-MM.md`
- `tests/test_btw6_exec_reports.py` — 40/40 tests: schedule crons, API endpoints, code node content, write + ntfy output, connections, metadata
- Health maintained: **95/100** | Test coverage: 90%

---

## v1.7 — 2026-06-27 | Agent Handoff Bus

**Trigger:** Build Agent Handoff Bus.docx — eliminate manual document relay between agents

**Changes:**
- `Architecture/Agent_Handoff/` — full directory structure (Inbox/Processing/Processed/Failed/Archive/templates/)
- `Architecture/Agent_Handoff/handoff_processor.py` — validator, router, file mover, ntfy notification
- `Architecture/Agent_Handoff/AGENT_HANDOFF_BUS.md` — spec + usage guide
- `Architecture/Agent_Handoff/HANDOFF_INDEX.md` — auto-maintained log
- `Architecture/Agent_Handoff/templates/` — 4 standard templates (browser_discovery, chief_architect_directive, architecture_chapter, implementation_request)
- `workflows/n8n/AUTO-HANDOFF-PROCESSOR.json` — 5-minute polling workflow (check inbox → process → ntfy)
- `tests/test_handoff_processor.py` — 42 tests, all passing
- 10 handoff types supported: browser_discovery, houzz_export, hubspot_export, platform_opportunity_report, business_process_architecture, chief_architect_directive, architecture_chapter, implementation_request, approval_request, executive_brief

---

## v1.6 — 2026-06-27 | Platform Intelligence Ingestion (HCI-OR-001)

**Trigger:** HCI OPPORTUNITY REPORT.docx + Business Process Architecture Ingestion.docx

**Changes:**
- `Architecture/Platform_Intelligence/HCI_BUSINESS_PROCESS_ARCHITECTURE_V1.md` — 38 opportunities structured with process_id, scoring (BV/FI/PM/EX/TC), phase assignments
- `Architecture/Platform_Intelligence/BUSINESS_PROCESS_BACKLOG.md` — 4-phase prioritized roadmap; Phase 1: 17 items; Phase 2: 15 items; Phase 3-4: 6 items
- `Architecture/Platform_Intelligence/PROCESS_AUTOMATION_MATRIX.md` — Tier 1/2/3 automation map; 6 n8n workflow designs
- `Architecture/Platform_Intelligence/SYSTEM_OWNERSHIP_MATRIX.md` — 17 lifecycle phases, data ownership, integration priority matrix
- `Architecture/Platform_Intelligence/AI_OPPORTUNITY_MATRIX.md` — 20 AI opportunities (A: drafting, B: analysis, C: detection); maturity map vs. HCI AI OS
- `Architecture/Platform_Intelligence/FIELD_READINESS_GAPS.md` — SS field score 33/80, PM score 47/80, Executive score 44/80; path to ORR-001 pass (74+/80)
- Critical gap documented: HubSpot Deal ↔ Houzz Pro Project bridge — zero automation today

---

## v1.5 — 2026-06-27 | BTW-8 — PM Workspace: Client Comms + AI Ranked Actions

**Trigger:** BTW-8 — PM Workspace additions (Strategic Backlog)

**Changes:**
- `api/routers/operations.py`: 2 new helpers + wired into `pm_weekly`:
  - `_build_client_comm_queue(deal_id)` — queries HubSpot engagements + notes; returns days_since_contact, urgency label (CURRENT/DUE_SOON/OVERDUE), recent engagements list, recent notes
  - `_rank_pm_actions(...)` — `priority_score = (severity × urgency × financial_impact) / max(days_remaining, 1)` — top 10 ranked actions across Budget, RFI, Procurement, Approval, Change Order, Client Comms categories
- `pm_weekly` response: `client_comms` now live (was stub); `ai_ranked_actions` added (new field)
- `tests/test_pm_workspace_btw8.py`: 69 tests — all passing
- Health maintained: **95/100** | 101 Francis: 12d since contact (DUE_SOON); 1355 Riverside: 17d (OVERDUE)

---

## v1.4 — 2026-06-27 | BTW-4 — Project Brain Extended Memory

**Trigger:** BTW-4 — Project Brain Extended Memory (Strategic Backlog)

**Changes:**
- Migration `016_project_extended_memory.sql`: 4 new tables — `project_events`, `project_ai_conversations`, `project_document_links`, `project_daily_summaries`
- `services/project_brain/routes.py`: 6 new endpoints:
  - `GET /{project_id}/timeline` — chronological event timeline
  - `POST /{project_id}/events` — log project event
  - `GET /{project_id}/conversations` — AI interaction history
  - `GET /{project_id}/document-links` — document-to-entity relationships
  - `POST /{project_id}/document-links` — create document link
  - `GET /{project_id}/daily-summary` — cached daily AI summary (generated + stored)
- `services/project_brain/models.py`: `EventCreate` + `DocumentLinkCreate` models
- `workflows/n8n/AUTO-DAILY-PROJECT-SUMMARY.json`: 5PM daily workflow — generates summaries for all 3 pilot projects + ntfy push
- Conversation memory auto-logged on every non-cached `/query` call
- `tests/test_project_brain_extended.py`: 36 tests — all passing
- Health maintained: **95/100** | Test coverage: 90%

**ADRs Created:** None (consistent with existing patterns)

---

## v1.3 — 2026-06-27 | Definition of Done Codified + BTW-3 Complete

**Trigger:** Directive.docx — Permanent Engineering Standard: 14-step Definition of Done

**Changes:**
- `CLAUDE.md` (root): Definition of Done (14 steps + stop conditions) added as permanent standard
- `memory/feedback_definition_of_done.md`: DoD saved to persistent memory
- `tests/test_architecture_sync.py`: 21 tests added for architecture sync service (all passing)
- `Handbook/AUTHORING_QUEUE.md`: Sections 1.A–1.D marked 🟢 PUBLISHED
- `Handbook/00_Master_Index.md`: Test coverage updated to 90/100
- `architecture/STRATEGIC_BACKLOG.md`: BTW-4 through BTW-10 queued
- `architecture/CHIEF_ARCHITECT_PIPELINE.md`, `AUTHORING_PIPELINE_SPEC.md`, `ARCHITECTURE_SYNC_ENGINE.md`: Authoring pipeline fully specified
- `services/architecture_sync/routes.py`: Full Architecture Sync service (8 endpoints, ADR-006)

**ADRs Created:** ADR-006 (Architecture Sync Service)

**Platform State:** 95/100 HEALTHY | Test coverage 90% | DoD permanently adopted

---

## v1.2 — 2026-06-27 | Chief Architect Pipeline + Volume I Authored

**Trigger:** BTW (Book - 2.docx + One thing I think we almost missed.docx)

**Chapters Created / Modified:**
- `Handbook/Volume_01_Executive_Vision.md`: Sections 1.A–1.D authored by Buck Adams
  — AI Organization, Design Principles, Maturity Model, North Star
- `Handbook/Volume_04_Role_Intelligence.md`: Consolidated SS+PM+Leadership
- `Handbook/Volume_05_Executive_Intelligence.md`: Executive Mission Control
- `Handbook/Volume_09_Roadmap.md`: New volume — CA-reserved
- `Handbook/AUTHORING_QUEUE.md`: 65+ chapters as work items
- `Handbook/00_Master_Index.md`: Master index v2 — 10-volume TOC, ADR table, pipeline table
- `Handbook/CHANGELOG.md`, `Handbook/Published/`, `Handbook/Drafts/`: Pipeline workspace
- `CHIEF_ARCHITECT_PIPELINE.md`, `AUTHORING_PIPELINE_SPEC.md`, `ARCHITECTURE_SYNC_ENGINE.md`: Spec docs
- `services/architecture_sync/routes.py` + `api/main.py` registration: Service live
- `architecture/STRATEGIC_BACKLOG.md`: BTW-4 through BTW-10 queued with dependency analysis

**ADRs Created:** ADR-006 (Architecture Sync)

**Chief Architect Review Items:** Volume I sections 1.1, 1.2, 1.3, 1.5 pending

---

## v1.1 — 2026-06-27 | Browser Discovery & Auditor Fixes

**Trigger:** BTW (Browser .docx) — gap analysis against Browser Agent Standard

**Chapters Affected:**
- Volume 07 (Construction Intelligence Engine) — connector framework bugs fixed
- Volume 08 (Automation Architecture) — migration 015 added
- Volume 09 (Governance) — system health score updated 85→95

**Changes:**
- `houzz_connector.py`: Fixed `ON CONFLICT DO UPDATE` missing conflict target (invalid SQL)
  — correct target: `(houzz_project_id, category, (COALESCE(as_of_date, '1970-01-01'::date)))`
- Migration `015_hubspot_activities.sql`: Created `hubspot_activities` table missing from schema;
  HubSpot connector was in permanent error state without it
- `system_auditor/routes.py`: Fixed Python `0 or 999` falsy bug in data freshness scoring
  — data_freshness score: 11/100 → 100/100; overall health: 85/100 → 95/100
- HubSpot connector_sync_state: cleared error status for contacts/companies (now idle)

**ADRs Created:** None this revision

**Chief Architect Review Items Generated:** See CHIEF_ARCHITECT_REVIEW_QUEUE.md

---

## v1.0 — 2026-06-27 | Initial Architecture Handbook (BTW-3)

**Trigger:** BTW-3 (Execute ONLY after.docx) — Chief Architect Architecture Handbook initiative

**Chapters Created:**
- `00_Master_Architecture_Handbook.md` — master index, TOC, ADR table, platform state
- `Volume_01_Executive_Vision.md` — stub awaiting Chief Architect
- `Volume_02_Construction_Intelligence_Model.md` — 4-layer model, health scoring, prediction types
- `Volume_03_Project_Brain.md` — endpoints, snapshot schema, class hierarchy
- `Volume_04_Superintendent_Intelligence.md` — console layout, safety topics, data model
- `Volume_05_Project_Manager_Intelligence.md` — priority algorithm, endpoints, reports
- `Volume_06_Executive_Mission_Control.md` — 11 sections, approval workflow
- `Volume_07_Construction_Intelligence_Engine.md` — service directory, BaseIntelligenceService
- `Volume_08_Automation_Architecture.md` — n8n workflows, launchd, error handling
- `Volume_09_Governance.md` — approval gates, security standards, test registry
- `Volume_10_Future_Vision.md` — stub awaiting Chief Architect
- `ADRs/ADR-001` through `ADR-005` — 5 architecture decisions recorded

**Platform State at v1.0:**
- 95/100 HEALTHY (post v1.1 fixes)
- 18 services, 427 endpoints
- 107 tests, 89% service coverage
- 15 n8n workflows (7 active)
- 73-table PostgreSQL schema, 15 migrations

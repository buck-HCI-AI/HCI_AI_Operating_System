# Architecture Handbook CHANGELOG

> Maintained by: Claude Code (Implementation Engineer)
> Authored by: ChatGPT + Buck Adams (Chief Architect)

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

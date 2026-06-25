# 01_ROADMAP.md
**HCI AI Operating System — Build Roadmap**
Last updated: 2026-06-24

---

## Phase 0 — Foundation (COMPLETE)

- [x] n8n running in Docker (localhost:5678)
- [x] HubSpot CRM (3 active projects, pipeline, stages)
- [x] Google Sheets bid trackers (3 projects)
- [x] Google Drive integration
- [x] Microsoft 365 / Outlook / Graph API
- [x] Python integration layer (credentials, hubspot, google_sheets, microsoft_graph)
- [x] WF-007 AI Bid Leveling Engine (live — daily + webhook)
- [x] Git repository initialized (`HCI_AI_Operating_System`)
- [x] AI_TEAM file set — Claude Code Operating Charter v0.1 + Collaboration Proposal v1.0
- [x] BOOK_00 canonical engineering manual (seed)
- [x] ChatGPT briefing document

---

## Phase 1 — Data Layer (NEXT — no blockers)

**Goal:** Persistent truth store + semantic memory engine
**Command:** `docker-compose up -d postgres qdrant redis`

- [ ] PostgreSQL 16 running — schema.sql loaded, all tables live
- [ ] Qdrant running — 7 collections accessible
- [ ] Redis 7 running
- [ ] Seed Postgres with current project/vendor/bid data
- [ ] Memory ingestion: HubSpot contacts → `vendor_memory` (Qdrant)
- [ ] Memory ingestion: bid history → `bid_entries` (Postgres) + `bid_memory` (Qdrant)
- [ ] GitHub remote connected (needs Buck `gh auth login`)

---

## Phase 2 — Workflow Expansion

**Goal:** Full operational workflow coverage
**Dependencies:** Phase 1

- [ ] WF-001: New Project Setup — creates HubSpot deal, Sheet, Drive folder, project doc
- [ ] WF-002: Meeting Intelligence — parses notes, creates tasks, logs to Qdrant
- [ ] WF-003: Morning Brief — daily 7AM email with priorities and open bids
- [ ] WF-004: Daily Log — captures site notes → Postgres + Qdrant
- [ ] WF-005: Lessons Learned — project close capture → Postgres + Qdrant

---

## Phase 3 — API Layer

**Goal:** Programmatic access to all HCI AI data
**Dependencies:** Phase 1

- [ ] FastAPI skeleton (`/03_Source_Code/api/`)
- [ ] `/api/v1/projects/` — project status and metadata
- [ ] `/api/v1/vendors/` — vendor intelligence and history
- [ ] `/api/v1/bids/` — bid history, leveling, comparisons
- [ ] `/api/v1/memory/search` — Qdrant semantic search
- [ ] `/api/v1/workflows/trigger` — trigger n8n workflows

---

## Phase 4 — Agents

**Goal:** Autonomous AI agents acting on behalf of HCI
**Dependencies:** Phase 3

- [ ] Executive Agent — daily brief, decision support, exception alerts
- [ ] PM Agent — project status monitoring, milestone tracking
- [ ] Bid Agent — bid analysis, leveling, award recommendations
- [ ] Procurement Agent — vendor outreach, scope clarification, follow-ups
- [ ] Historian Agent — lessons learned retrieval, institutional knowledge
- [ ] Relationship Agent — contact history, health, follow-up prompts

---

## Phase 5 — Dashboards

**Goal:** Visual operational intelligence
**Dependencies:** Phase 4

- [ ] Executive Dashboard — project health, budget vs. actual, critical path
- [ ] PM Dashboard — daily tasks, open issues, bid status
- [ ] Universal Search — semantic search across all HCI knowledge

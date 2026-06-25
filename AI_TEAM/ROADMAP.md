# ROADMAP.md
**HCI AI Operating System — Build Roadmap**
Last updated: 2026-06-24

---

## Phase 0 — Foundation (COMPLETE)
- [x] n8n running in Docker (localhost:5678)
- [x] HubSpot CRM wired (3 active projects, pipeline, stages)
- [x] Google Sheets bid trackers (3 projects)
- [x] Google Drive integration
- [x] Microsoft 365 / Outlook / Graph API integration
- [x] Python integration layer (credentials, hubspot, google_sheets, microsoft_graph)
- [x] WF-007 AI Bid Leveling Engine (live, daily + webhook)
- [x] Git repository initialized (`HCI_AI_Operating_System`)
- [x] ChatGPT briefing document (`CHATGPT_BRIEFING.md`)
- [x] Claude Code Operating Charter adopted
- [x] AI_TEAM file set established

---

## Phase 1 — Data Layer (NEXT)
**Goal:** Persistent truth store + semantic memory
**Target:** Anytime (docker-compose ready, no blockers except running it)

- [ ] `docker-compose up -d postgres qdrant redis`
- [ ] Verify Postgres schema loaded (all tables from schema.sql)
- [ ] Verify Qdrant collections accessible
- [ ] Seed Postgres with current project/vendor data
- [ ] Memory ingestion: HubSpot contacts → `vendor_memory` (Qdrant)
- [ ] Memory ingestion: bid history → `bid_entries` (Postgres) + `bid_memory` (Qdrant)
- [ ] GitHub remote connected (blocked on Buck running `gh auth login`)

---

## Phase 2 — Workflow Expansion
**Goal:** Full operational workflow coverage
**Dependencies:** Phase 1 complete

- [ ] WF-001: New Project Setup
  - Trigger: Manual / new HubSpot deal
  - Creates: Google Sheet, Drive folder, HubSpot deal, project doc
- [ ] WF-002: Meeting Intelligence
  - Trigger: Email with meeting notes
  - Creates: Action items → HubSpot tasks, meeting_memory → Qdrant
- [ ] WF-003: Morning Brief
  - Trigger: Daily 7AM MDT
  - Outputs: Today's priorities, open bids, project status summary → email
- [ ] WF-004: Daily Log
  - Trigger: Manual or end-of-day
  - Captures: Site notes, progress, issues → Postgres + Qdrant
- [ ] WF-005: Lessons Learned
  - Trigger: Project close or manual
  - Captures: What worked, what didn't → `lessons_learned` (Postgres + Qdrant)

---

## Phase 3 — API Layer
**Goal:** Programmatic access to all HCI AI data
**Dependencies:** Phase 1 complete

- [ ] FastAPI application skeleton (`/03_Source_Code/api/`)
- [ ] `/api/v1/projects/` — project status and metadata
- [ ] `/api/v1/vendors/` — vendor intelligence and history
- [ ] `/api/v1/bids/` — bid history, leveling, comparisons
- [ ] `/api/v1/memory/search` — Qdrant semantic search endpoint
- [ ] `/api/v1/workflows/trigger` — trigger n8n workflows via API

---

## Phase 4 — Agents
**Goal:** Autonomous AI agents that act on behalf of HCI
**Dependencies:** Phase 3 complete

- [ ] Executive Agent — daily brief, decision support, exception alerts
- [ ] PM Agent — project status monitoring, milestone tracking
- [ ] Bid Agent — bid analysis, leveling, award recommendations
- [ ] Procurement Agent — vendor outreach, scope clarification, follow-ups
- [ ] Historian Agent — lessons learned retrieval, institutional knowledge
- [ ] Relationship Agent — contact history, relationship health, follow-up prompts

---

## Phase 5 — Dashboards
**Goal:** Visual operational intelligence
**Dependencies:** Phase 4 complete

- [ ] Executive Dashboard — project health, budget vs. actual, critical path
- [ ] PM Dashboard — daily task list, open issues, bid status
- [ ] Universal Search — semantic search across all HCI knowledge

---

## Milestone Dates

| Milestone | Target | Status |
|---|---|---|
| Data layer live | ASAP (no blockers) | 🔜 |
| GitHub remote | After Buck runs `gh auth login` | 🔧 Blocked |
| WF-001 through WF-005 | Phase 2 | 🔜 |
| First agent live | Phase 4 | 🔜 |
| Executive Dashboard | Phase 5 | 🔜 |

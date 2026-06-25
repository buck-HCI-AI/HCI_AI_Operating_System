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

## Phase 1 — Data Layer (COMPLETE ✅)

**Goal:** Persistent truth store + semantic memory engine

- [x] PostgreSQL 16 — hci_os DB, 7 tables, port 5432
- [x] Qdrant — 7 collections, 465 vectors, port 6333
- [x] Redis 7 — port 6379
- [x] Seed Postgres: 3 projects, 392 vendors, 26 bid entries
- [x] Memory ingestion: HubSpot contacts → vendor_memory (392 vectors)
- [x] Memory ingestion: bids → bid_memory (26 vectors)
- [x] GitHub remote: github.com/buck-HCI-AI/HCI_AI_Operating_System

---

## Phase 2 — Workflow Expansion (COMPLETE ✅)

**Goal:** Full operational workflow coverage

- [x] WF-001: New Project Setup — HubSpot deal + Postgres + Qdrant
- [x] WF-002: Meeting Intelligence — notes → action items → HubSpot tasks + Qdrant
- [x] WF-003: Morning Brief — daily email, auto-runs at login + 7AM
- [x] WF-004: Daily Log — site notes → Postgres + Qdrant
- [x] WF-005: Lessons Learned — Postgres + Qdrant lessons_learned collection
- [x] WF-007: AI Bid Leveling Engine — auto-runs at login + 7AM (n8n)

---

## Phase 3 — API Layer (COMPLETE ✅)

**Goal:** Programmatic access to all HCI AI data

- [x] FastAPI 0.138 + Uvicorn — localhost:8000, auto-starts at login (launchd KeepAlive)
- [x] /projects/ — project status, bid packages, budget summary
- [x] /vendors/ — vendor search, CSI filter, bid history
- [x] /bids/ — bid entries, leveling sheet, package list
- [x] /memory/search — semantic search across all 7 Qdrant collections
- [x] /workflows/ — all WF-001 through WF-005 triggers
- [x] Swagger UI at localhost:8000/docs

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

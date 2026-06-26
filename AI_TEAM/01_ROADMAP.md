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

## Phase 4 — SOP Execution Layer (COMPLETE ✅)

**Goal:** 27 SOP workflows enforcing all HCI construction operating procedures
- [x] Shared base layer (base_sop, approval_engine, stop_conditions, sop_kpi)
- [x] 27 SOPs built: Plan Review → Safety → Inspection (SOP 04–30)
- [x] 189 endpoints at `/api/v1/sop/`
- [x] Event auto-emission from every SOP status transition

---

## Phase 5 — Platform Integration Layer (COMPLETE ✅)

**Goal:** Shared services consumed by all workflows and SOPs
- [x] Identity & Permissions — 12 roles, 42 permissions, authority levels
- [x] Event Bus — standardized events, correlation IDs, persistence
- [x] Notification Center — 17 types, escalation, construction-specific notifiers
- [x] Audit Trail — immutable cross-service records (SOP + Workflow + Platform)
- [x] Unified Search Gateway — intent routing (Postgres + Qdrant), confidence, citations
- [x] 33 platform API endpoints; 39/39 tests passing
- [x] BaseSOP auto-emits events to Event Bus on every status transition

---

## Phase 6 — Gate 5 Pilot + Go-Live

**Goal:** Validate full system in production on live projects
- [ ] 5-day pilot: 101 Francis, 64 Eastwood, 1355 Riverside (ends 2026-07-01)
- [ ] Buck sign-off → production go-live authorized
- [ ] Populate Qdrant: vendor_memory + drive_memory embedding run
- [ ] Add launchd for WF-PM daily + exec health report

---

## Phase 7 — Agents (Future)

**Goal:** Autonomous AI agents acting on behalf of HCI
**Dependencies:** Phase 5 Platform Layer (in place)

- [ ] Executive Agent — daily brief, decision support, exception alerts
- [ ] PM Agent — project status monitoring, milestone tracking
- [ ] Bid Agent — bid analysis, leveling, award recommendations
- [ ] Procurement Agent — vendor outreach, scope clarification, follow-ups
- [ ] Historian Agent — lessons learned retrieval, institutional knowledge

---

## Phase 8 — Dashboards (Future)

**Goal:** Visual operational intelligence
**Dependencies:** Phase 6 Go-Live

- [ ] Executive Dashboard — project health, budget vs. actual, critical path
- [ ] PM Dashboard — daily tasks, open issues, bid status
- [ ] Unified Search UI — search across all HCI knowledge with citations

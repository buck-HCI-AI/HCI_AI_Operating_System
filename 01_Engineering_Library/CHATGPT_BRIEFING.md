# HCI AI Operating System — ChatGPT Briefing Document

**Paste this at the start of any ChatGPT architecture session.**
**Last updated: 2026-06-24**

---

## Who You Are in This System

You are the **Principal AI Architect** for the HCI AI Operating System at Hendrickson Construction, Inc. Your role is architecture, documentation, system design, engineering review, and planning. Claude Code is the implementation engineer with direct filesystem access. You do not have direct filesystem access.

Division of labor:
- **ChatGPT:** Architecture, design decisions, documentation authoring, engineering review, planning
- **Claude Code:** Implementation, file editing, workflow building, API integrations, git commits
- **Buck Adams (owner):** Business decisions, approvals, direction

---

## Company & Project Context

**Hendrickson Construction, Inc. (HCI)**
- High-end residential remodels in Aspen, CO
- Owner/operator: Buck Adams (buck@hendricksoninc.com / buck@ahmaspen.com)
- ~3 active projects at any time, 10–30 bid packages per project

**Active Projects (as of 2026-06-24):**
| Project | Address | Scope | Status |
|---|---|---|---|
| 64 Eastwood | 64 Eastwood Dr., Aspen | Exterior & Site | Bidding — 2 bids in of 13 packages |
| 101 Francis | 101 W Francis St., Aspen | Full Interior Remodel | Bidding — 1 bid in, most TBD |
| 1355 Riverside | 1355 Riverside Dr., Aspen | Full Remodel | Bidding — 30 packages |

---

## Repository

**Location (local):** `/Users/buckadams/HCI_AI_Operating_System/`
**GitHub:** TBD (being set up)
**Google Drive:** Sync/backup

```
HCI_AI_Operating_System/
├── 00_Manuscripts/          Book manuscripts
├── 01_Engineering_Library/  Engineering specs & this briefing
├── 02_Architecture/         System architecture docs
├── 03_Source_Code/
│   └── integrations/        credentials.py, hubspot.py, google_sheets.py, microsoft_graph.py
├── 04_Workflows/            n8n JSON exports (WF-007 live)
├── 05_Database/
│   ├── postgres/schema.sql  Full schema (projects, vendors, bids, lessons, meetings)
│   └── qdrant/collections.md 7 collections defined
├── 06_Project_Documentation/ Per-project status docs
├── 07_SOPs/
├── 10_Agents/               Executive, PM, Bid, Procurement, Historian, Relationship
└── 11_Prompts/
```

---

## Technology Stack

| Layer | Technology | Status |
|---|---|---|
| Workflow Automation | n8n (Docker, localhost:5678) | ✅ LIVE |
| CRM | HubSpot | ✅ LIVE |
| Bid Tracking | Google Sheets (3 project sheets) | ✅ LIVE |
| Document Storage | Google Drive | ✅ LIVE |
| Email | Microsoft 365 / Outlook / Graph API | ✅ LIVE |
| Truth Store | PostgreSQL 16 | 🔜 docker-compose ready, not yet started |
| Vector/Memory Store | Qdrant | 🔜 docker-compose ready, not yet started |
| Temp State/Cache | Redis 7 | 🔜 docker-compose ready, not yet started |
| API Layer | FastAPI | 🔜 Planned |
| Agent Orchestration | OpenClaw | 🔜 Planned |
| Dashboards | TBD | 🔜 Planned |

---

## What's Been Built

### WF-007 — AI Bid Leveling Engine (LIVE)
- **Trigger:** Daily 5PM MDT + `POST http://localhost:5678/webhook/bid-leveling`
- **What it does:** Reads bid tracker → builds HTML leveling report → exports xlsx to Drive → saves draft to Outlook
- **Known fix applied 2026-06-24:** Send Draft nodes now reference upstream `Level Bids` node directly

### Integration Layer (Python, direct API calls)
All integrations bypass n8n credential limitations by decrypting OAuth tokens from n8n's SQLite DB:
- `credentials.py` — AES-256-CBC decryption of n8n stored OAuth tokens
- `hubspot.py` — deals, tasks, notes, associations
- `google_sheets.py` — read/write bid trackers
- `microsoft_graph.py` — inbox, drafts, attachments

### HubSpot CRM (live data)
- Pipeline ID: `2203777729`
- Stages: Not Started → Scope Ready → Sent Out → Bids Receiving → Leveling → Awarded → Not Awarded
- All 3 projects have deals, contacts, and tasks in HubSpot

### Postgres Schema (designed, not yet running)
Tables: `projects`, `vendors`, `bid_packages`, `bid_entries`, `lessons_learned`, `meetings`, `daily_logs`
Seed data: 3 active projects pre-loaded

### Qdrant Collections (designed, not yet running)
7 collections: `project_memory`, `vendor_memory`, `meeting_memory`, `lessons_learned`, `bid_memory`, `constitution_memory`, `photo_memory`

---

## What's NOT Built Yet

- PostgreSQL not running (docker-compose configured, needs `docker-compose up -d postgres`)
- Qdrant not running (same — needs `docker-compose up -d qdrant`)
- No memory ingestion pipeline (HubSpot → Qdrant, bids → Qdrant)
- WF-001 New Project, WF-002 Meeting Intelligence, WF-003 Morning Brief, WF-004 Daily Log, WF-005 Lessons Learned
- FastAPI layer
- Agents (Executive, PM, Bid, etc.)
- Dashboards
- GitHub remote not yet connected

---

## Build Sequence (from Constitution)

```
Docker → Postgres → Qdrant → Redis → FastAPI → OpenClaw → n8n → Agents → Dashboards
```

**Completed:**
1. ✅ n8n (Docker)
2. ✅ HubSpot, Google, Microsoft integrations
3. ✅ WF-007 Bid Leveling Engine
4. ✅ HCI_AI_Operating_System git repository

**Next:**
5. 🔜 `docker-compose up -d postgres qdrant redis`
6. 🔜 WF-001 through WF-005
7. 🔜 Memory ingestion (existing data → Qdrant)
8. 🔜 FastAPI layer
9. 🔜 Agents

---

## Engineering Philosophy (from Constitution)

- Memory First. Intelligence Second. Automation Third.
- Repository is the permanent source of truth — not chat history
- Documentation is part of the software
- Improve existing engineering before replacing it
- Think in decades

## Prime Directives

Preserve Knowledge. Protect Relationships. Scale Expertise. Improve Decisions. Document Everything. Think In Decades.

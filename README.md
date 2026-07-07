# HCI AI Operating System

**Hendrickson Construction, Inc.**
Build started: 2026-06-24 | Constitution v1

> **This file was stale from day 1 of the build (2026-06-24) until 2026-07-07 - every
> "Next"/"Planned"/"Not built" status below described the original plan, not current
> reality.** A teammate reading this file from the GitHub remote (which was 33 commits
> behind local `main` at the time) concluded the API layer, database, and vector store
> didn't exist yet. They do - this correction exists specifically because that caused
> real confusion. If you're reading this from a fresh clone, also check how many
> commits behind `origin/main` you are (`git log origin/main..HEAD --oneline`) before
> trusting any status table, here or elsewhere.

## Purpose

Preserve Experience. Scale Expertise. Protect Relationships. Improve Decisions. Compound Wisdom.

This is the HCI AI Operating System — a permanent, production-grade AI platform supporting construction operations, project management, procurement, and organizational knowledge. Not a chatbot. Not a collection of automations. An operating system.

## Architecture

**Philosophy:** Memory First. Intelligence Second. Automation Third.

```
Postgres (truth) + Qdrant (meaning) + Redis (state)
        ↓
FastAPI (API layer)
        ↓
n8n (workflow automation) + OpenClaw (agent orchestration)
        ↓
Agents: Executive · PM · Bid · Procurement · Historian · Relationship
        ↓
Dashboards: Executive · PM · Universal Search
```

## Technology Stack

| Layer | Technology | Status |
|---|---|---|
| Workflow Automation | n8n (Docker, ~60 active workflows) | ✅ Live |
| CRM / Relationship Memory | HubSpot | ✅ Live |
| Project Bid Tracking | Google Sheets + Postgres bid_packages/bid_entries | ✅ Live |
| Document Storage | Google Drive | ✅ Live |
| Email Intelligence | Microsoft 365 / Graph API | ✅ Live |
| Truth Store | PostgreSQL 16 (`hci_postgres` container) | ✅ Live |
| Memory / Vector Store | Qdrant (13 collections, 5000+ vectors incl. a real company knowledge graph) | ✅ Live |
| Temporary State | Redis 7 (`hci_redis` container, `api/dependencies.py:get_redis()`) | ✅ Live |
| API Layer | FastAPI (`03_Source_Code/api`, 65+ registered services under launchd `com.hci.api-server`) | ✅ Live |
| Agent Orchestration | Claude Code (implementation) + ChatGPT "HCI Chief Architect" Custom GPT (architecture/ARB) + Browser Claude (discovery/governance), coordinating via `gateway_request_log`/`ai_messages` and file-based handoffs in `architecture/Agent_Handoff/` | ✅ Live |
| Dashboards | Executive Mission Control, PM Weekly Console, Superintendent Daily, Owner/Office/Accounting/Client/Trade-Partner role consoles | ✅ Live |

## Active Workflows

Representative sample - see `GET /api/v1/workflows` for the full live registry (60+ workflows spanning bid leveling, HubSpot/Houzz sync, drift detection, self-heal, executive/PM reporting, and gate approvals).

| ID | Name | Status |
|---|---|---|
| WF-007 | AI Bid Leveling Engine | ✅ Live — daily 5PM + webhook |
| WF-001 | New Project Setup | ✅ Live |
| WF-002 | Meeting Intelligence | ✅ Live |
| WF-003 | Morning Brief | ✅ Live — daily 6:45-7:00AM |
| WF-004 | Daily Log | ✅ Live |
| WF-005 | Lessons Learned | ✅ Live (`lessons_learned` Postgres table, 40+ real entries) |
| AUTO-DRIFT-CHECK | Weekly system-reality check (dead connectors, stale directives, self-graded-completion claims, docs-vs-code drift) | ✅ Live |
| AUTO-SELFHEAL | 15-min n8n health check + auto-restart | ✅ Live |

## Active Projects

| Project | HubSpot Pipeline | Bid Tracker | Status |
|---|---|---|---|
| 64 Eastwood Dr. | Pipeline 2203777729 | Google Sheets | Bidding |
| 101 Francis St. | Pipeline 2203777729 | Google Sheets | Bidding |
| 1355 Riverside Dr. | Pipeline 2203777729 | Google Sheets | Bidding |

## Repository Structure

```
00_Manuscripts/          Book manuscripts (ChatGPT Architecture AI)
01_Engineering_Library/  Engineering specs and reference docs
02_Architecture/         System architecture, stack docs, docker-compose
03_Source_Code/          Python services, API integrations, agents
04_Workflows/            n8n workflow JSON exports
05_Database/             Postgres schema, Qdrant collection definitions
06_Project_Documentation/ Per-project docs and summaries
07_SOPs/                 Standard operating procedures
08_Assets/               Templates, logos, reference files
09_PDFs/                 Constitution PDFs
10_Agents/               Agent definitions and prompts
11_Prompts/              Prompt library
12_Dashboards/           Dashboard code and configs
13_Security/             Security docs (no secrets committed)
14_Backups/              Backup scripts and schedules
15_Tests/                Test suite
99_Archive/              Deprecated items
```

## Build Sequence

1. ✅ n8n + workflow automation layer
2. ✅ HubSpot, Google, Microsoft integrations
3. ✅ WF-007 Bid Leveling Engine
4. ✅ Git repository (HCI_OS)
5. ✅ PostgreSQL + Qdrant + Redis (Docker stack) - confirmed all three running (`hci_postgres`, `hci_redis` containers + Qdrant) with real code paths (`api/dependencies.py:get_redis()`)
6. ✅ WF-001 through WF-005
7. ✅ Memory ingestion (HubSpot + bid history → Qdrant)
8. ✅ FastAPI layer
9. ✅ Agents (Claude Code, GBT, Browser Claude, multi-agent drift-check/self-heal)
10. ✅ Executive Dashboard + role consoles (Owner, Office, Accounting, Client, Trade Partner, PM, Superintendent) ← you are here
11. 🔜 Company-wide Monthly Business Review report (client satisfaction + AI ROI metrics need a data-source decision first)
12. 🔜 Continuous Discovery Engine full closed-loop (detection logic is live; scheduled auto-triggering + Architecture Sync closed loop not yet wired end-to-end)

## Prime Directives

Preserve Knowledge. Protect Relationships. Scale Expertise. Improve Decisions. Document Everything. Think In Decades.

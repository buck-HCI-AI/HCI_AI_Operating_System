# HCI AI Operating System

**Hendrickson Construction, Inc.**
Build started: 2026-06-24 | Constitution v1

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
| Workflow Automation | n8n (Docker) | ✅ Live |
| CRM / Relationship Memory | HubSpot | ✅ Live |
| Project Bid Tracking | Google Sheets | ✅ Live |
| Document Storage | Google Drive | ✅ Live |
| Email Intelligence | Microsoft 365 / Graph API | ✅ Live |
| Truth Store | PostgreSQL 16 | 🔜 Next |
| Memory / Vector Store | Qdrant | 🔜 Next |
| Temporary State | Redis 7 | 🔜 Next |
| API Layer | FastAPI | 🔜 Planned |
| Agent Orchestration | OpenClaw | 🔜 Planned |
| Dashboards | TBD | 🔜 Planned |

## Active Workflows

| ID | Name | Status |
|---|---|---|
| WF-007 | AI Bid Leveling Engine | ✅ Live — daily 5PM + webhook |
| WF-001 | New Project Setup | 🔜 Not built |
| WF-002 | Meeting Intelligence | 🔜 Not built |
| WF-003 | Morning Brief | 🔜 Not built |
| WF-004 | Daily Log | 🔜 Not built |
| WF-005 | Lessons Learned | 🔜 Not built |

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
4. ✅ Git repository (HCI_OS) ← you are here
5. 🔜 PostgreSQL + Qdrant + Redis (Docker stack)
6. 🔜 WF-001 through WF-005
7. 🔜 Memory ingestion (HubSpot + bid history → Qdrant)
8. 🔜 FastAPI layer
9. 🔜 Agents
10. 🔜 Executive Dashboard

## Prime Directives

Preserve Knowledge. Protect Relationships. Scale Expertise. Improve Decisions. Document Everything. Think In Decades.

# BOOK_00 — HCI AI Operating System Master Specification
**Version:** 2.0 | **Last Updated:** 2026-06-25  
**Status:** Active — single source of implementation truth. PDFs are release artifacts; this is the permanent record.

---

## Purpose

BOOK_00 is the canonical engineering manual for the HCI AI Operating System. It is:
- The document ChatGPT reads at the start of every architecture session
- The document Claude Code consults when architecture questions arise
- The permanent record of how and why this system is built the way it is

It is NOT a status document (that's `AI_TEAM/00_STATUS.md`). It is NOT a task list (that's `AI_TEAM/05_BACKLOG.md`). It is the engineering manual — the "why" behind every major decision.

---

## Sections

| # | File | Title | Status |
|---|------|-------|--------|
| 00 | [00_EXECUTIVE_OVERVIEW.md](00_EXECUTIVE_OVERVIEW.md) | Executive Overview | ✅ |
| 01 | [01_REPOSITORY_GOVERNANCE.md](01_REPOSITORY_GOVERNANCE.md) | Repository Governance and AI Collaboration | ✅ |
| 02 | [02_INFRASTRUCTURE.md](02_INFRASTRUCTURE.md) | Infrastructure Architecture | ✅ |
| 03 | [03_DATA_ARCHITECTURE.md](03_DATA_ARCHITECTURE.md) | Data Architecture | ✅ |
| 04 | [04_STORAGE.md](04_STORAGE.md) | Storage and Document Lifecycle | ✅ |
| 05 | [05_KNOWLEDGE_INGESTION.md](05_KNOWLEDGE_INGESTION.md) | Knowledge Ingestion and Document Intelligence | ✅ |
| 06 | [06_API_LAYER.md](06_API_LAYER.md) | API Layer | ✅ |
| 07 | [07_INTELLIGENCE_SERVICES.md](07_INTELLIGENCE_SERVICES.md) | Construction Intelligence Services | ✅ |
| 08 | [08_WORKFLOW_ENGINE.md](08_WORKFLOW_ENGINE.md) | Workflow Engine | ✅ Spec |
| 09 | [09_STANDARD_WORKFLOWS.md](09_STANDARD_WORKFLOWS.md) | Standard Workflows | ✅ |
| 10 | [10_PM_WORKFLOW.md](10_PM_WORKFLOW.md) | Project Manager Workflow | ✅ Spec |
| 11 | [11_SUPERINTENDENT_WORKFLOW.md](11_SUPERINTENDENT_WORKFLOW.md) | Superintendent Workflow | ✅ Spec |
| 12 | [12_DAILY_LOGS_SCHEDULE.md](12_DAILY_LOGS_SCHEDULE.md) | Daily Logs, Schedule Intelligence, Status Reporting | ✅ Spec |
| 13 | [13_REPORTING.md](13_REPORTING.md) | Reporting and Dashboards | ✅ Spec |
| 14 | [14_DEPLOYMENT.md](14_DEPLOYMENT.md) | Deployment, Backup, and Operations | ✅ |
| 15 | [15_ROADMAP.md](15_ROADMAP.md) | Roadmap and Implementation Status | ✅ |
| 16 | [16_APPENDIX.md](16_APPENDIX.md) | Directive History and Source Artifacts | ✅ |

---

## System Overview

**Company:** Hendrickson Construction, Inc. (HCI) — high-end residential remodels, Aspen CO
**Owner:** Chris Hendrickson (Hendrickson Construction, Inc.) | **PM & Superintendent / HCI-AI Owner:** Buck Adams
**Mission:** Build the permanent AI operating system that runs HCI's construction operations

### Prime Directives
> Preserve Knowledge. Protect Relationships. Scale Expertise. Improve Decisions. Document Everything. Think In Decades.

### Core Philosophy
> Memory First. Intelligence Second. Automation Third.

---

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│                   DASHBOARDS                        │
│        Executive · PM · Universal Search            │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│                    AGENTS                           │
│  Executive · PM · Bid · Procurement · Historian     │
│  Relationship (via OpenClaw)                        │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│             WORKFLOW AUTOMATION                     │
│           n8n (Docker, localhost:5678)              │
└──────────┬─────────────────────────┬────────────────┘
           │                         │
┌──────────▼──────┐       ┌──────────▼──────────────┐
│   FastAPI       │       │   Integration Layer      │
│   (API layer)   │       │   credentials.py         │
│   🔜 Planned    │       │   hubspot.py             │
└──────────┬──────┘       │   google_sheets.py       │
           │              │   microsoft_graph.py     │
           │              └──────────────────────────┘
           │
┌──────────▼────────────────────────────────────────┐
│                  DATA LAYER                        │
│  PostgreSQL 16 · Qdrant (vectors) · Redis (state) │
│  🔜 docker-compose ready — not yet started        │
└────────────────────────────────────────────────────┘

LIVE EXTERNAL SYSTEMS:
  HubSpot CRM · Google Sheets · Google Drive · Microsoft 365
```

---

## Active Projects (as of 2026-06-24)

| Project | Address | Scope | Status |
|---|---|---|---|
| 64 Eastwood | 64 Eastwood Dr., Aspen | Exterior & Site | Bidding — 2 bids in of 13 packages |
| 101 Francis | 101 W Francis St., Aspen | Full Interior Remodel | Bidding — 1 bid in |
| 1355 Riverside | 1355 Riverside Dr., Aspen | Full Remodel | Bidding — 30 packages |

---

## Technology Choices and Rationale

| Layer | Choice | Why |
|---|---|---|
| Workflow automation | n8n | Self-hosted, visual, already live; avoids vendor lock-in |
| CRM | HubSpot | Already in use; vendor/contact history is there |
| Truth store | PostgreSQL 16 | ACID, relational, proven; construction data is structured |
| Vector store | Qdrant | Self-hosted, fast, purpose-built for semantic search |
| Cache | Redis 7 | Industry standard for agent session state |
| Agent orchestration | OpenClaw | TBD — evaluate once data layer is live |
| Integration auth | n8n SQLite decrypt | n8n is the credential store; avoids duplicate secrets |

---

## Build Sequence (from Constitution)

```
Docker → Postgres → Qdrant → Redis → FastAPI → OpenClaw → n8n → Agents → Dashboards
```

Phase 0 (complete): n8n + all integrations + WF-007 + repository
Phase 1 (next): `docker-compose up -d postgres qdrant redis`
Phase 2: WF-001 through WF-005
Phase 3: FastAPI
Phase 4: Agents
Phase 5: Dashboards

---

## Governing Documents (in 01_Engineering_Library/)

- `HCI_AI_Claude_Code_Operating_Charter_v0.1.pdf`
- `HCI_AI_Repository_Collaboration_Proposal_v1.pdf`
- `Workflow_00_AI_Collaboration_Layer_Directive_for_Claude_Code_v1.pdf`
- `CHATGPT_BRIEFING.md`

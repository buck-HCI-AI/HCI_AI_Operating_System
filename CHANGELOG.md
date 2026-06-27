# CHANGELOG
## HCI AI Operating System — Hendrickson Construction, Inc.

All significant changes to the HCI AI Operating System are documented here.
Format: [Agent] Description — Date

---

## [Sprint 0] — 2026-06-26 — Repository Foundation & Governance

### Added by Browser Claude (GitHub Administrator)
- HCI_AI_CONSTITUTION.md — foundational law for all AI agents
- AI_TEAM_CHARTER.md — roles, authorities, and boundaries for every AI
- AUTOMATION_GOVERNANCE.md — rules governing all automations
- APPROVAL_GATES.md — Gate A through Gate H approval framework
- SPRINT_OPERATING_MODEL.md — how sprints run and close
- AI_WORKFLOW_ROLES.md — workflow ownership by agent
- PROJECT.md — canonical project backlog and integration registry
- TASKS.md — 80-task register across Sprint 0 through Sprint 9
- CONTRIBUTING.md, PULL_REQUEST_TEMPLATE.md, CODEOWNERS
- 5 GitHub issue templates (architecture, bug, feature, docs, workflow)
- GitHub Project + Milestones (Sprint 0–10) + 22 labels
- Houzz Browser Intelligence workstream (6 design docs)
- IMPLEMENTATION_INTEGRATION_PLAN.md — integration strategy
- PROGRAM_REPOSITORY_STATUS.md, PROGRAM_REPOSITORY_INVENTORY.md
- REPOSITORY_RELATIONSHIP_MAP.md, LIVE_PROJECT_STATE_TEMPLATE.md
- CURRENT_SPRINT.md — Sprint 1 System Verification plan
- LIVE_PROJECT_STATE.md — activated from template

### Added by Claude Code (Lead Implementation Engineer)
- Data stack live: PostgreSQL 16, Qdrant, Redis (Docker)
- Memory ingestion pipeline: Postgres + Qdrant populated
- FastAPI layer v1 (versioned /api/v1/*) — 427 endpoints, 18 intelligence services
- WF-001 through WF-006: new project, meeting intelligence, morning brief,
  daily log, lessons learned, inbox review
- WF-007: AI Bid Leveling Engine (live, n8n)
- HubSpot integration: deals, contacts, companies
- Google Drive integration: files, folders, uploads
- Google Sheets integration: bid trackers (3 active projects)
- Microsoft 365 / Graph API: email read/send/draft
- MCP server: 26 tools (Phase 1)
- Platform Integration Layer: 27 SOPs (Plan Review → Field Inspection)
- 5 shared platform services: identity, event bus, notifications, audit trail, search
- 48/48 MVP Sprint 1 tests passing — Gate 5 Pilot activated
- 4 active projects seeded: 64 Eastwood, 101 Francis, 1355 Riverside, 83 Sagebrusch
- Vendor registry: 392 vendors, 258 with CSI divisions
- Historical cost: 21 records from 655 S Garmisch
- Lessons learned: 10 records (7 Garmisch, 3 gate tests)
- Business processes: 27 mapped from SOP library
- Qdrant healthcheck fixed (bash TCP — no curl/wget required)
- SQL fallback added to historical cost search
- ProjectMining bug fixed (/candidates → /records)
- P1 data population: business_processes, lessons_learned, historical_cost_records tables

---

## [ACR-001] — 2026-06-26 — MCP Chief Architect Integration Tools

### Added by Claude Code
- 5 new MCP tools for Chief Architect (ChatGPT) integration:
  - ReadLiveProjectState — reads LIVE_PROJECT_STATE.md
  - ReadCurrentSprint — reads CURRENT_SPRINT.md
  - ReadAutomationRegistry — n8n + Python + MCP tool inventory
  - ReadDecisionLog — architecture/implementation decisions from DB
  - ReadRepositoryStatus — git state + service health
- Total MCP tools: 31
- ProjectMining 404 bug fixed

---

## [ACR-002] — 2026-06-26 — Universal Project State Access

### Added by Claude Code
- GET /project-state — public endpoint, no auth required
  Returns LIVE_PROJECT_STATE.md as JSON or raw markdown
  ChatGPT can call this at the start of every session
- GetProjectState MCP tool — live dynamic snapshot from all services
- Total MCP tools: 32
- LIVE_PROJECT_STATE.md uploaded to Google Drive (public, always current)

---

## [Merge] — 2026-06-26 — Repositories Unified

### Claude Code
- Merged feature/data-architecture-document-storage into main
- All implementation code + all governance docs now on single main branch
- GitHub repo made public (after credential cleanup)
- All hardcoded credentials removed from 12 code files → .env
- HCI_API_KEY, POSTGRES_PASSWORD, REDIS_PASSWORD in .env (gitignored)
- reports/ directory structure created
- CHANGELOG.md, TASKS.md, CURRENT_SPRINT.md updated

---

## Pending — Sprint 1

See CURRENT_SPRINT.md and TASKS.md for active task board.
Sprint 1 begins when Buck issues the Sprint 1 ACR.

---

*CHANGELOG.md | HCI AI Operating System | Hendrickson Construction, Inc.*
*Maintained by: all AI agents | Authority: HCI_AI_CONSTITUTION.md*

# LIVE_PROJECT_STATE — Input Document
Generated: 2026-06-26 | Source: Claude Code Implementation Repository
Purpose: Seed data for LIVE_PROJECT_STATE.md to be created in Program Repository by ChatGPT

---

## System Snapshot

**Date:** 2026-06-26
**Pilot:** Gate 5 active — 2026-06-25 to 2026-07-01
**Pilot Projects:** 64 Eastwood, 101 Francis, 1355 Riverside
**Implementation Phase:** Phase 16 complete / P1 data population complete / awaiting architecture review

---

## Infrastructure (All Running)

| Service | URL | Auth |
|---|---|---|
| FastAPI | http://localhost:8000 | X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6 |
| MCP Server | http://localhost:8080 | — |
| MCP (public) | https://speculate-armband-retinal.ngrok-free.dev/mcp | — |
| n8n | http://localhost:5678 | N8N_API_KEY in .env |
| PostgreSQL | localhost:5432 | hci_admin / hci_os (pw in .env) |
| Qdrant | http://localhost:6333 | — |
| Redis | localhost:6379 | pw in .env |

---

## Active Projects

| ID | Name | HubSpot Deal ID | Status |
|---|---|---|---|
| 1 | 64 Eastwood | 331240861419 | Pilot active |
| 2 | 101 Francis | 321401932527 | Pilot active |
| 3 | 1355 Riverside | 321351275210 | Pilot active |
| 4 | 83 Sagebrusch | None (TBD) | Status unclear — Buck to confirm |

---

## Active n8n Workflows

| Workflow | Trigger | Owner |
|---|---|---|
| Bid Receipt Processing v5 | Email/webhook | Automated |
| WF-003 Historical Cost Queue | Manual | Claude Code |
| WF-004 Lessons Learned Engine | Manual | Claude Code |
| WF-005 SOP Registry Sync | Schedule | Automated |
| WF-006 Executive Alerts | Schedule | Automated |
| WF-007 AI Bid Leveling Engine | Webhook | Automated |
| WF-011 Site Superintendent Daily Briefing | Schedule | Automated |

---

## Data State

| Table | Row Count | Notes |
|---|---|---|
| projects | 4 | 3 pilot + 83 Sagebrusch |
| vendors | 392 | 258 with CSI divisions |
| business_processes | 27 | All SOPs mapped |
| lessons_learned | 10 | 3 gate tests + 7 Garmisch |
| historical_cost_records | 21 | Garmisch seed |
| background_learning_records | 50 | Pending pipeline |
| operating_rules | seeded | Active |

---

## What Each AI Is Doing

| AI | Role | Current Task |
|---|---|---|
| Claude Code (this session) | Lead Implementation Engineer | P1 data population complete; awaiting arch review |
| Browser Claude | Governance + Houzz Intelligence Design | Design complete in Program Repo |
| ChatGPT | Chief Architect + Integration Manager | Architecture review pending |

---

## Pending Decisions (Require Buck or Architecture Review)

| Item | Owner | Urgency |
|---|---|---|
| 83 Sagebrusch — active job or prospect? Create HubSpot deal? | Buck | P1 |
| HubSpot connected inbox setup | Buck | P1 |
| ChatGPT Business workspace GPT creation | Buck | P1 |
| Houzz Browser Intelligence — reconcile with existing sync_houzz.py | Architecture Review | P1 |
| WF-008/009/010 staging test approval | Claude Code + Buck | Before pilot close |
| Merge plan for Program Repo + Implementation Repo | Architecture Review | P2 |
| Qdrant vector indexing of DB content | Claude Code | P2 |

---

## Open Duplicate Risks (See DUPLICATE_RISK_REPORT.md)

1. Unversioned API routes — Claude Code can fix immediately
2. AI_TEAM/ vs LIVE_PROJECT_STATE.md — resolve after Program Repo creates controlling doc
3. Houzz double implementation — block on architecture review

---

## Completed This Session (2026-06-26)

- HubSpot deal IDs linked for all 3 pilot projects
- MCP tool paths fixed (SOP + HistCost)
- n8n cleanup (3 workflows archived)
- `business_processes` table created + 27 rows seeded
- `lessons_learned` 7 Garmisch records inserted
- `historical_cost_records` 21 Garmisch records inserted
- Historical cost `/search` SQL fallback added
- Qdrant healthcheck fixed (bash TCP, now healthy)
- Vendor CSI divisions: 258/392 (65.8%) assigned
- All AI_TEAM coordination files updated

---

## Gate 5 Pilot Close Criteria (by 2026-07-01)

- [ ] All 3 pilot projects have at least 1 SOP instance run
- [ ] WF-008 Bid Follow-Up tested on 1 bid package
- [ ] WF-009 New Job Setup tested (or deferred)
- [ ] Executive report at /api/v1/mvp/exec-report reviewed by Buck
- [ ] HubSpot connected inbox confirmed or rescheduled
- [ ] Go/no-go decision logged in decision_records

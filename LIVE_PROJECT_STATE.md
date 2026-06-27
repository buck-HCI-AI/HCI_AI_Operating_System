# LIVE PROJECT STATE — HCI AI Operating System
**Last Updated:** 2026-06-26T23:55 MST
**Updated By:** Claude Code (Lead Implementation Engineer)
**Status:** Gate 5 Pilot LIVE | Architecture Review v1 APPROVED | Holding for Sprint 1 ACR

---

## System Health (Live as of 2026-06-26 23:55 UTC)
| Service | Status | Detail |
|---|---|---|
| FastAPI | HEALTHY | localhost:8000 / ngrok unreachable from ChatGPT cloud |
| PostgreSQL | OK | 4 projects, 47 tables, all seeded |
| Qdrant | OK | 13 collections indexed |
| Redis | OK | Running |
| n8n | RUNNING | 15 workflows total, 7 active |
| MCP Server | RUNNING | 31 tools — Claude Code only (not reachable from ChatGPT cloud) |

---

## AI Team
| AI | Role | Status |
|---|---|---|
| ChatGPT | Chief Architect & Architecture Review Board | Active — awaiting Sprint 1 ACR |
| Claude Code | Lead Implementation Engineer | Holding on Sprint 1 ACR |
| Browser Claude | Program Repository & Governance Manager | Active |
| n8n | Automation Orchestrator | 7 workflows running |
| Future Codex | QA / Test Engineering | Not yet assigned |

---

## Active Projects — Gate 5 Pilot (2026-06-25 → 2026-07-01)
| ID | Project | Scope | HubSpot Deal | Health | Bid Pkgs | Open Risks | Schedule Var |
|---|---|---|---|---|---|---|---|
| 1 | 64 Eastwood | Exterior & Site | 331240861419 | YELLOW | 35 | 2 | +1 day |
| 2 | 101 Francis | Full Interior Remodel | 321401932527 | YELLOW | 26 | 4 | +2 days |
| 3 | 1355 Riverside | Full Remodel | 321351275210 | GREEN | 58 | 0 | 0 days |
| 4 | 83 Sagebrusch | TBD | None — Buck to confirm | — | — | — | — |

**Projects at risk:** 64EW (2 open risks, schedule slipping), 101F (4 open risks, schedule slipping)
**Total open risks across pilot:** 6 | **Open RFIs:** 0

---

## ROI — Pilot to Date (2026-06-26)
| Metric | Value |
|---|---|
| Total minutes saved | **1,784 minutes (29.7 hours)** |
| Baseline (manual) | 1,970 minutes |
| AI-assisted | 186 minutes |
| Documents processed | 62 |
| Risks detected | 31 |
| Schedule risks flagged | Active (64EW + 101F) |

### ROI by Workflow (Top Activities)
| Workflow | Runs | Min Saved/Run | Notes |
|---|---|---|---|
| executive_report | 8+ | 42 | Cross-project morning brief |
| pm_weekly_review | 9+ | 55 | Per project, per week |
| project_brain_init | 9+ | 28 | Automated project baseline |
| schedule_status | 6+ | 28 | Schedule intelligence per project |
| daily_log | 6+ | 16 | Daily log drafts |
| bid_import | 6+ | 12 | Bid processing queue |
| bid_leveling | 1 | 85 | 1355R Div 16 Electrical |

---

## Approval Queue (Live — Needs Buck Action)
**Total:** 11 items | **Pending:** 9 | **Approved:** 2

Key pending approvals:
1. **Drive Upload** — 1355 Riverside Div 16 Electrical Bid Leveling Excel file → `15azXdDg5ACi6iRU3XBD8ozzY2H_eDSd_`
2. **Bid Import** — Pacific Concrete Inc / Concrete / $185,000 → 101 Francis (multiple duplicate queue items from test runs)
3. **Daily Log** — 1355 Riverside 2026-06-26 (concrete pour, crane delay, pump truck issue)

---

## Background Learning Pipeline
| Metric | Value |
|---|---|
| Total records | 190 |
| Pending review | 190 |
| Discovered | 189 |
| Extracted | 1 |
| Awaiting processing | All 190 |

---

## What's Built
### FastAPI REST (427 endpoints, 18 services)
- `project_intelligence` — project registry, health, status
- `vendor_intelligence` — 392 vendors, 258 with CSI divisions
- `bid_intelligence` — bid entries, leveling, comparisons
- `approval_queue` — human-in-loop for all write actions
- `decision_intelligence` — architecture + implementation decisions log
- `background_learning` — document discovery pipeline
- `historical_cost` — 21 records from 655 S Garmisch
- `lessons_learned` — 10 records (7 Garmisch, 3 gate tests)
- `business_process_library` — 27 processes from SOP library
- `sop_library` — 27 SOPs (Plan Review through Field Inspection)
- `schedule_intelligence` — schedule risk detection
- `executive_reporting` — cross-project morning report
- `project_brain` — per-project context engine
- `houzz_intelligence` — Houzz Browser Intelligence (BLOCKED pending architecture decision)
- `hubspot_integration` — deals, contacts, companies
- `google_drive_integration` — files, folders, uploads
- `google_sheets_integration` — bid trackers
- `outlook_integration` — email read/send via Graph API

### MCP Server (31 tools — Claude Code only)
**New tools added in ACR-001:**
- `ReadLiveProjectState` — reads this file
- `ReadCurrentSprint` — reads CURRENT_SPRINT.md
- `ReadAutomationRegistry` — n8n + Python + MCP tool inventory
- `ReadDecisionLog` — architecture/implementation decisions from DB
- `ReadRepositoryStatus` — git state + service health

**Existing 26 tools:**
ReadProjectRegistry, ReadVendorRegistry, ReadConstructionOS,
SearchDrive, ReadDriveFile, SearchHubSpotDeals, SearchCompanies,
SearchContacts, ReadBidTracker, GenerateBidLevel, HistoricalCostLookup,
ProcurementStatus, ScheduleStatus, DraftEmail, CreateTask,
UpdateRegistry, AwardRecommendation, ProjectMining, GetApprovalQueue,
CreateDriveFolder, UploadFileToDrive, ListDriveFolder, ReadSheet,
WriteSheet, ExecutiveReport, GetROISummary

### PostgreSQL (47 tables)
- projects (4 rows) | bid_entries | daily_logs | schedule_items
- vendors (392 rows) | historical_cost_records (21 rows)
- lessons_learned (10 rows) | business_processes (27 rows)
- sop_library (27 rows) | approval_queue (11 rows)
- background_learning (190 rows) | roi_log (60 rows)
- + 35 additional tables

### Connector Registry (18 connectors)
- Google Drive: 6 connectors (registered)
- HubSpot: 6 connectors (registered)
- Houzz: 6 connectors (registered — BLOCKED pending architecture decision)

### n8n Workflows (7 active of 15 total)
All active workflows include approval gates — no auto-write to production.

---

## ACR Log
| ACR | Title | Status | Date |
|---|---|---|---|
| ACR-001 | MCP Chief Architect Integration Tools | COMPLETE | 2026-06-26 |
| ACR-002 | Universal Project State Access | COMPLETE | 2026-06-26 |
| Sprint 1 ACR | Next sprint scope | PENDING — ChatGPT to issue | — |

---

## Open Items
| Item | Owner | Priority | Status |
|---|---|---|---|
| Create CURRENT_SPRINT.md | ChatGPT → Browser Claude | P0 | BLOCKING Sprint 1 |
| Sprint 1 ACR | ChatGPT | P0 | BLOCKING Sprint 1 |
| Approve pending queue items | Buck | P1 | 9 items pending |
| 83 Sagebrusch HubSpot deal | Buck | P1 | Deal ID unknown |
| HubSpot connected inbox | Buck | P1 | Settings → Email → Connect |
| Houzz reconciliation | Architecture Review | P1 | BLOCKED — no ACR yet |
| WF-008/009/010 staging tests | Claude Code | P1 | Blocked on Sprint 1 ACR |
| GitHub remote setup | Buck (optional) | P2 | Enables ChatGPT raw file access |

---

## Sprint 1 Gate Criteria
- [x] Implementation Repository stable and committed
- [x] LIVE_PROJECT_STATE.md created and uploaded to Drive
- [x] ACR-001 complete (31 MCP tools)
- [ ] CURRENT_SPRINT.md created and placed at repo root
- [ ] ChatGPT confirms full picture received
- [ ] Sprint 1 ACR issued by ChatGPT
- [ ] Go-live auth from Buck

---

## How ChatGPT Connects (ACR-002 Complete)
**ngrok is NOT reachable from ChatGPT cloud (confirmed 2026-06-26).**

| Method | Status | URL / Notes |
|---|---|---|
| Public HTTP endpoint | LIVE (ACR-002) | `https://speculate-armband-retinal.ngrok-free.dev/project-state` — no auth needed |
| Google Drive | LIVE | `https://drive.google.com/file/d/1Jjug6nbx-mGN9v4GrEyofkGXY5nMHvpP/view` |
| GitHub raw URL | PENDING Buck push | `https://raw.githubusercontent.com/buck-HCI-AI/HCI_AI_Operating_System/refs/heads/feature/data-architecture-document-storage/LIVE_PROJECT_STATE.md` |
| ChatGPT Custom GPT | Not configured | Requires paid ngrok or hosted URL |
| MCP | NOT for ChatGPT | MCP is Claude-only protocol |

**Primary access:** `GET /project-state` — no API key, no special headers.
**Stable fallback:** Google Drive link (Claude Code re-uploads on every state update).
**GitHub:** Run `Push_To_GitHub.command` from Desktop to activate raw URL access.

---

## Implementation Repository
- **Location:** /Users/buckadams/HCI_AI_Operating_System (local Mac mini M2)
- **Branch:** feature/data-architecture-document-storage
- **Last Commit:** ACR-001 complete — 31 MCP tools (2026-06-26)
- **Remote:** None configured — not pushed to GitHub

## Key Root Files
| File | Purpose |
|---|---|
| LIVE_PROJECT_STATE.md | This file — operational source of truth |
| CURRENT_SPRINT.md | Sprint plan — does not exist yet (Browser Claude to create) |
| IMPLEMENTATION_REPOSITORY_STATUS.md | Full technical status |
| IMPLEMENTATION_INVENTORY.md | All components: KEEP / MERGE / ARCHIVE |
| DUPLICATE_RISK_REPORT.md | 10 identified risks |
| INTEGRATION_RECOMMENDATIONS.md | 6 architectural recommendations |
| MCP_INTEGRATION_REPORT.md | MCP tool inventory + ACR-001 spec |
| HCI_AI_IMPLEMENTATION_HANDOFF_FOR_CHATGPT.md | Full handoff document |

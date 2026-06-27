# LIVE_PROJECT_STATE.md
## HCI AI Operating System — Current Live State

**Organization:** Hendrickson Construction, Inc.
**Owner:** @buck-HCI-AI (Buck Adams)
**Last Updated:** 2026-06-27T01:15 MST
**Updated By:** Claude Code (Lead Implementation Engineer)
**Sprint:** Sprint 1 — System Verification (ACTIVE — Team operating model complete)
**Authority:** LIVE_PROJECT_STATE_TEMPLATE.md v1.0

> **Update Protocol:** Any agent may commit factual, observable updates to this file.
> Always append — never remove history. Tag significant changes with `[STATE CHANGE]`.
> Human owner is the final authority on all state decisions.

---

## 🚦 System Health (Live as of 2026-06-26 23:55 UTC) [STATE CHANGE — Claude Code]

| Service | Status | Last Verified | Agent | Notes |
|---|---|---|---|---|
| FastAPI | 🟢 HEALTHY | 2026-06-26 | Claude Code | localhost:8000 — 427 endpoints, 18 services |
| PostgreSQL | 🟢 OK | 2026-06-26 | Claude Code | 4 projects, 47 tables, all seeded |
| Qdrant | 🟢 OK | 2026-06-26 | Claude Code | 13 collections indexed |
| Redis | 🟢 OK | 2026-06-26 | Claude Code | Running |
| n8n | 🟢 RUNNING | 2026-06-27 | Claude Code | 18 workflows, 10 active (incl. AUTO-001/002/003) |
| MCP Server | 🟢 RUNNING | 2026-06-26 | Claude Code | 32 tools (ACR-001 + ACR-002) |
| GitHub Repo | 🟢 LIVE | 2026-06-26 | Browser Claude | main branch + merged feature branch |
| HubSpot CRM | 🟢 LIVE | 2026-06-26 | Claude Code | 3 active deals connected |
| Google Drive | 🟢 LIVE | 2026-06-26 | Claude Code | API + OAuth active |
| Google Sheets | 🟢 LIVE | 2026-06-26 | Claude Code | Bid trackers active |
| Microsoft 365 | 🟢 LIVE | 2026-06-26 | Claude Code | Graph API — email read/send |
| Houzz (Browser) | 🔴 BLOCKED | — | — | Strategy complete; awaiting architecture ACR |

---

## AI Team
| AI | Role | Status |
|---|---|---|
| ChatGPT | Chief Architect, Integration Director, Architecture Review Board | Active — needs Sprint 1 ACR |
| Claude Code | Lead Implementation Engineer | Active — 44/80 tasks done |
| Browser Claude | Program Repository & Governance Manager, GitHub Admin | Active — governs main |
| n8n | Automation Orchestrator | 10 workflows active (AUTO-001/002/003 live) |
| Future Codex | QA / Test Engineering | Not yet assigned |

### Daily Team Rhythm (Automated)
| Time | Workflow | Output | Who Reads It |
|---|---|---|---|
| 06:00 | AUTO-002 Workflow Health Check | reports/health/YYYY-MM-DD-health-check.md | All agents |
| 07:00 | AUTO-001 Daily Status Report | reports/daily/YYYY-MM-DD-daily-status.md | All agents |
| 08:00 | AUTO-003 Sprint Self-Status | reports/sprint/YYYY-MM-DD-sprint-status.md | AI Team morning brief |

**Each morning:** Every agent starts by reading reports/daily/ and LIVE_PROJECT_STATE.md.
No one asks "what's the status?" — it's committed to GitHub every day automatically.

---

## Active Projects — Gate 5 Pilot (2026-06-25 → 2026-07-01)
| ID | Code | Project | Scope | HubSpot Deal | Health | Bid Pkgs | Open Risks | Schedule Var |
|---|---|---|---|---|---|---|---|---|
| 1 | 64EW | 64 Eastwood | Exterior & Site | 331240861419 | 🟡 YELLOW | 35 | 2 | +1 day |
| 2 | 101F | 101 Francis | Full Interior Remodel | 321401932527 | 🟡 YELLOW | 26 | 4 | +2 days |
| 3 | 1355R | 1355 Riverside | Full Remodel | 321351275210 | 🟢 GREEN | 58 | 0 | 0 days |
| 4 | — | 83 Sagebrusch | TBD | None — Buck to confirm | — | — | — | — |

**Projects at risk:** 64EW (2 open risks), 101F (4 open risks, schedule slipping)
**Total open risks:** 6 | **Open RFIs:** 0

---

## ROI — Pilot to Date (2026-06-26)
| Metric | Value |
|---|---|
| Total minutes saved | **1,784 minutes (29.7 hours)** |
| Baseline (manual) | 1,970 minutes |
| AI-assisted | 186 minutes |
| Documents processed | 62 |
| Risks detected | 31 |

### ROI by Workflow
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

Key pending:
1. **Drive Upload** — 1355 Riverside Div 16 Electrical Bid Leveling Excel
2. **Bid Import** — Pacific Concrete Inc / Concrete / $185,000 → 101 Francis
3. **Daily Log** — 1355 Riverside 2026-06-26 (concrete pour, crane delay)

---

## Background Learning Pipeline
| Metric | Value |
|---|---|
| Total records | 190 |
| Pending review | 190 |
| Discovered | 189 |
| Extracted | 1 |

---

## 🧠 MCP Server Status (ACR-001 + ACR-002 Complete)

**32 total tools** (Claude Code only — not reachable from ChatGPT cloud)

ACR-001 tools (Chief Architect integration):
- `ReadLiveProjectState` — reads this file from repo
- `ReadCurrentSprint` — reads CURRENT_SPRINT.md
- `ReadAutomationRegistry` — n8n + Python + MCP tool inventory
- `ReadDecisionLog` — architecture/implementation decisions from DB
- `ReadRepositoryStatus` — git state + service health

ACR-002 tools:
- `GetProjectState` — live dynamic snapshot from all services

Existing 26 tools: ReadProjectRegistry, ReadVendorRegistry, ReadConstructionOS,
SearchDrive, ReadDriveFile, SearchHubSpotDeals, SearchCompanies, SearchContacts,
ReadBidTracker, GenerateBidLevel, HistoricalCostLookup, ProcurementStatus,
ScheduleStatus, DraftEmail, CreateTask, UpdateRegistry, AwardRecommendation,
ProjectMining, GetApprovalQueue, CreateDriveFolder, UploadFileToDrive,
ListDriveFolder, ReadSheet, WriteSheet, ExecutiveReport, GetROISummary

---

## What's Built (Implementation Repository — Claude Code)

### FastAPI REST (427 endpoints, 18 services)
| Service | Endpoints | Status |
|---|---|---|
| project_intelligence | ~15 | Active |
| vendor_intelligence | ~20 | Active — 392 vendors, 258 with CSI |
| bid_intelligence | ~25 | Active |
| approval_queue | ~10 | Active — human-in-loop enforced |
| decision_intelligence | ~8 | Active |
| background_learning | ~12 | Active — 190 docs queued |
| historical_cost | ~10 | Active — 21 Garmisch records |
| lessons_learned | ~8 | Active — 10 records |
| business_process_library | ~8 | Active — 27 processes |
| sop_library | ~12 | Active — 27 SOPs |
| schedule_intelligence | ~15 | Active |
| executive_reporting | ~10 | Active |
| project_brain | ~20 | Active |
| bid_leveling | ~30 | Active |
| houzz_intelligence | ~15 | BLOCKED — awaiting architecture ACR |
| hubspot_integration | ~40 | Active |
| google_drive_integration | ~30 | Active |
| google_sheets_integration | ~20 | Active |

### PostgreSQL (47 tables, 4 projects)
projects, vendors (392), bid_entries, historical_cost_records (21),
lessons_learned (10), business_processes (27), sop_library (27),
approval_queue (11), background_learning (190), roi_log (60), + 37 more

### n8n Workflows (7 active of 15 total)
All workflows have approval gates — no auto-write to production.

### Governance Layer (Browser Claude — Program Repository)
AI_TEAM_CHARTER.md, AI_WORKFLOW_ROLES.md, APPROVAL_GATES.md,
AUTOMATION_GOVERNANCE.md, HCI_AI_CONSTITUTION.md, CONTRIBUTING.md,
CURRENT_SPRINT.md, TASKS.md, SPRINT_OPERATING_MODEL.md,
REPOSITORY_RELATIONSHIP_MAP.md, PROGRAM_REPOSITORY_INVENTORY.md,
PROGRAM_REPOSITORY_STATUS.md, GOVERNANCE_COMPLETION_REPORT.md,
IMPLEMENTATION_INTEGRATION_PLAN.md + 6 Houzz workstream docs

---

## ACR Log
| ACR | Title | Status | Date |
|---|---|---|---|
| ACR-001 | MCP Chief Architect Integration Tools | COMPLETE | 2026-06-26 |
| ACR-002 | Universal Project State Access | COMPLETE | 2026-06-26 |
| Sprint 1 ACR | Sprint 1 scope authorization | PENDING — ChatGPT to issue | — |

---

## Open Items
| Item | Owner | Priority | Status |
|---|---|---|---|
| Sprint 1 ACR | ChatGPT | P0 | BLOCKING Sprint 1 kickoff |
| Approve pending queue items | Buck | P1 | 9 items pending |
| 83 Sagebrusch HubSpot deal | Buck | P1 | Deal ID unknown |
| HubSpot connected inbox | Buck | P1 | Settings → Email → Connect |
| Houzz reconciliation | Architecture Review | P1 | BLOCKED — no ACR yet |
| WF-008/009/010 staging tests | Claude Code | P1 | On hold — Sprint 1 ACR needed |

---

## How ChatGPT Connects (ACR-002)

| Method | Status | URL |
|---|---|---|
| Public HTTP endpoint | 🟢 LIVE | `https://speculate-armband-retinal.ngrok-free.dev/project-state` (no auth) |
| Google Drive | 🟢 LIVE | `https://drive.google.com/file/d/1Jjug6nbx-mGN9v4GrEyofkGXY5nMHvpP/view` |
| GitHub raw URL | 🟢 LIVE | `https://raw.githubusercontent.com/buck-HCI-AI/HCI_AI_Operating_System/main/LIVE_PROJECT_STATE.md` |
| MCP | ❌ NOT for ChatGPT | Claude-only protocol |

---

## Implementation Repository
- **Location:** /Users/buckadams/HCI_AI_Operating_System (local Mac)
- **GitHub:** https://github.com/buck-HCI-AI/HCI_AI_Operating_System
- **Branch:** main (merged 2026-06-26)
- **GitHub URL:** https://github.com/buck-HCI-AI/HCI_AI_Operating_System
- **GitHub raw (LIVE_PROJECT_STATE):** https://raw.githubusercontent.com/buck-HCI-AI/HCI_AI_Operating_System/main/LIVE_PROJECT_STATE.md
- **Last Commit:** Merge: Implementation + Program Repository unified

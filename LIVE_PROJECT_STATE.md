# LIVE_PROJECT_STATE.md
## HCI AI Operating System — Current Live State

**Organization:** Hendrickson Construction, Inc.
**Owner:** @buck-HCI-AI (Buck Adams)
**Last Updated:** 2026-07-01T05:15 UTC
**Updated By:** Claude Code — Sprint 3 opened per ARB directive. AI communication reliability P0 (directive lifecycle + heartbeat) reconciled. 101F/1355R Mission Control consistency bugs fixed. Live: 64EW/101F/1355R. Monitored: 246GW. All other projects = learning only.
**Sprint:** Sprint 3 — Production Stabilization (ACTIVE — opened 2026-07-01). Sprint 2 — Registry Consolidation CLOSED 2026-07-01 (see CURRENT_SPRINT.md for archived detail; formal ARB close ruling pending Chief Architect review).
**Authority:** LIVE_PROJECT_STATE_TEMPLATE.md v1.0

> **Update Protocol:** Any agent may commit factual, observable updates to this file.
> Always append — never remove history. Tag significant changes with `[STATE CHANGE]`.
> Human owner is the final authority on all state decisions.

---

## 🚦 System Health (Live as of 2026-06-26 23:55 UTC) [STATE CHANGE — Claude Code]

| Service | Status | Last Verified | Agent | Notes |
|---|---|---|---|---|
| FastAPI | 🟢 HEALTHY | 2026-06-29 | Claude Code | localhost:8000 — 96/100 HEALTHY, Constitution 100/100 COMPLIANT |
| PostgreSQL | 🟢 OK | 2026-06-29 | Claude Code | 50 tables (added: drive_file_log, pending_approvals, constitution_compliance column) |
| Qdrant | 🟢 POPULATED | 2026-06-29 | Claude Code | 13 collections — vendor_memory(2880), drive_memory(2347), project_memory(2690), hci_project_docs(5360) + more |
| Redis | 🟢 OK | 2026-06-26 | Claude Code | Running |
| n8n | 🟢 RUNNING | 2026-06-29 | Claude Code | 61 workflows (55 active) — +10 activated this session: AUTO-010/011/012/013, GATE-E/F/G/H, EVENT-HEALTH-CHECK, EVENT-DRIVE-SCAN |
| MCP Server | 🟢 RUNNING | 2026-06-28 | Claude Code | 43 tools |
| GitHub Repo | 🟢 LIVE | 2026-06-26 | Browser Claude | main branch + merged feature branch |
| HubSpot CRM | 🟢 LIVE | 2026-06-26 | Claude Code | 3 active deals connected |
| Google Drive | 🟢 LIVE | 2026-06-29 | Claude Code | API + OAuth active. Drive scan watcher running (15-min). Registered in connector_sync_state. |
| Google Sheets | 🟢 LIVE | 2026-06-26 | Claude Code | Bid trackers active |
| Microsoft 365 | 🟢 LIVE | 2026-06-29 | Claude Code | Graph API — email read/send. Registered in connector_sync_state. |
| Mining Engine | 🟢 LIVE | 2026-06-27 | Claude Code | 8 agents, 03:00 daily |
| Integration Registry | 🟢 LIVE | 2026-06-27 | Claude Code | 8 integrations seeded |
| Houzz Ingestion | 🟢 LIVE | 2026-06-28 | Claude Code | 995 schedule items loaded |
| Houzz Miner | 🟢 ACTIVE | 2026-06-28 | Claude Code | Running with DB data |
| Schedule Intelligence | 🟢 LIVE | 2026-06-28 | Claude Code | /mvp/projects/{code}/schedule-status active |
| Approval Loop | 🟢 LIVE | 2026-06-29 | Claude Code | POST /gateway/approvals → ntfy push → Buck approve/reject |
| Event Triggers | 🟢 LIVE | 2026-06-29 | Claude Code | /events/health-check (30min), /events/new-bid, /events/drive-scan (15min) |
| Constitution Checker | 🟢 LIVE | 2026-06-29 | Claude Code | GET /api/v1/services/system-auditor/constitution — runs nightly |
| Role Intelligence | 🟢 LIVE | 2026-06-29 | Claude Code | 9 role consoles: Owner/Office/Accounting/Client/Trade Partner (5 new) + SS/PM/Leadership/Exec (pre-built) |
| Knowledge Graph | 🟢 LIVE | 2026-06-29 | Claude Code | /api/v1/services/knowledge-graph/ — graph/vendor/issues/product traversal |
| Continuous Discovery | 🟢 LIVE | 2026-06-29 | Claude Code | /services/continuous-discovery + AUTO-CONTINUOUS-DISCOVERY n8n (HubSpot hourly, Houzz nightly) |
| External Drive Backup | 🟢 CONFIGURED | 2026-06-29 | Claude Code | HCI_AI_DEV 931GB drive — daily 2AM rsync + pg_dump. Run SETUP_DAILY_BACKUP.command to activate. |

---

## AI Team
| AI | Role | Status |
|---|---|---|
| ChatGPT | Chief Architect, Integration Director, Architecture Review Board | Active — needs Sprint 1 ACR |
| Claude Code | Lead Implementation Engineer | Active — 65/97 tasks done |
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

## [STATE CHANGE 2026-06-30] Gate 5 GO — AUTHORIZED by Buck Adams

**Gate 5 Verdict: GO — Full Production Authorization**
**Authorization Date:** 2026-06-30
**Authorized By:** Buck Adams (Owner)

### Live Production Projects
| ID | Code | Project | Scope | HubSpot Deal | Health | Bid Pkgs | Open Risks | Schedule Var |
|---|---|---|---|---|---|---|---|---|
| 1 | 64EW | 64 Eastwood | Exterior & Site | 331240861419 | 🟡 YELLOW | 35 | 2 | 0 days |
| 2 | 101F | 101 Francis | Full Interior Remodel | 321401932527 | 🟡 YELLOW | 26 | 2 | -5 days (steel delay) |
| 3 | 1355R | 1355 Riverside | Full Remodel | 321351275210 | 🟢 GREEN | 58 | 0 | 0 days |

### Monitored / Staged
| ID | Code | Project | Scope | HubSpot Deal | Health | Notes |
|---|---|---|---|---|---|---|
| 8 | 246GW | 246 Gallo Way | New Construction — Chaparral Lot 7 | 321358358216 | 🟢 GREEN | Monitored — pending full go-live |

### All Other Projects — Learning & Monitoring Only
| ID | Code | Project | Status |
|---|---|---|---|
| 4 | 83SB | 83 Sagebrusch | Learning/reference |
| 11 | ASPN-NEW | 842 Ridge Road | Learning/reference |
| 12 | ASPN-REM | 710 Cemetery Lane | Learning/reference |
| 13 | ASPN-MC | 200 E Hopkins | Learning/reference |
| 14+ | Various | 18+ additional | Learning/reference — no operational writes |

**Active risks:** 64EW (2 open risks), 101F (steel delay -5 days critical)
**Total open risks:** 4 | **Open RFIs:** 0

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

## 🧠 MCP Server Status (ACR-001 + ACR-002 + ACR-004 Complete)

**35 total tools** (Claude Code only — not reachable from ChatGPT cloud)

ACR-001 tools (Chief Architect integration):
- `ReadLiveProjectState` — reads this file from repo
- `ReadCurrentSprint` — reads CURRENT_SPRINT.md
- `ReadAutomationRegistry` — n8n + Python + MCP tool inventory
- `ReadDecisionLog` — architecture/implementation decisions from DB
- `ReadRepositoryStatus` — git state + service health

ACR-002 tools:
- `GetProjectState` — live dynamic snapshot from all services

ACR-004 tools (mining engine):
- `RunMiner` — trigger any miner or all 8 (dry_run safe default)
- `GetMiningStatus` — engine status + intelligence summary + registered miners
- `GetMiningLog` — last N mining run records

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
| houzz_intelligence | ~3 | 🟢 LIVE — GET /status, POST /ingest, GET / info |
| hubspot_integration | ~40 | Active |
| google_drive_integration | ~30 | Active |
| google_sheets_integration | ~20 | Active |

### PostgreSQL (47 tables, 4 projects)
projects, vendors (392), bid_entries, historical_cost_records (21),
lessons_learned (10), business_processes (27), sop_library (27),
approval_queue (11), background_learning (190), roi_log (60), + 37 more

### n8n Workflows (11 active of 18 total)
All workflows have approval gates — no auto-write to production.

| ID | Workflow | Schedule | Status |
|---|---|---|---|
| AUTO-001 | Daily Repository Status Report | 07:00 daily | 🟢 Active |
| AUTO-002 | Workflow Health Check | 06:00 daily | 🟢 Active |
| AUTO-003 | Sprint Self-Status Report | 08:00 daily | 🟢 Active |
| AUTO-004 | Mining Engine Orchestration | 03:00 daily | 🟢 Active |
| WF-001 through WF-007 | Core construction workflows | Various | 🟢 Active |

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
| ACR-004 | Continuous Mining & Learning Engine | COMPLETE — LIVE | 2026-06-27 |
| Sprint 1 ACR | Sprint 1 scope + Sprint 2 scope authorization | COMPLETE — via GBT Reconnect Directive | 2026-06-27 |

---

## Open Items
| Item | Owner | Priority | Status |
|---|---|---|---|
| Approve mining approval_queue items (vendor candidates) | Buck | P1 | 987+ items queued from HubSpot full sweep |
| Houzz full extraction | Future Sprint | P3 | Browser paused per Chief Architect Directive — full 15-table scope designed in HOUZZ_EXTRACTION_BACKLOG.md |
| Sprint 2 n8n gate workflows | n8n / Claude Code | P1 | AUTO-005, AUTO-006, AUTO-017, AUTO-018 |
| Branch protection on main | Buck | P2 | GitHub Settings → Branches → Require PR review |
| HubSpot connected inbox | Buck | P2 | HubSpot Settings → Email → Connect personal email |
| INT-008: Buck approves LIVE_PROJECT_STATE.md | Buck | P2 | Read this file, confirm accurate |
| 83 Sagebrusch HubSpot deal | Buck | P3 | Deal ID unknown — confirm in HubSpot |

## 🔨 Mining Engine Status (ACR-004 — LIVE 2026-06-27)

**Authorization:** Buck Adams (Owner) — 2026-06-27 | ACR: ChatGPT via GBT Reconnect Directive
**Schedule:** 03:00 daily (n8n AUTO-004)
**Dry-run default:** True (explicit `dry_run=False` required for writes)

| Miner | Status | Last Result |
|---|---|---|
| HubSpotMiner | 🟢 LIVE | 2,849 scanned, 987 extracted, full companies sweep |
| DriveMiner | 🟢 LIVE | Reading drive_sync_log |
| OutlookMiner | 🟢 LIVE | Emails queued for approval only — never auto-reply |
| HistoricalCostMiner | 🟢 LIVE | 21 Garmisch records, bid variance tracking |
| VendorIntelligenceMiner | 🟢 LIVE | 392 vendors, bid stats updating |
| LessonsLearnedMiner | 🟢 LIVE | Dedup via source_reference |
| HouzzMiner | ⏸ PAUSED | Awaiting data load — Browser Claude directive issued 2026-06-27; will activate after first ingest |
| ExecutiveAggregator | 🟢 LIVE | KPI snapshots + LIVE_PROJECT_STATE.md header update |

---

## How ChatGPT Connects (GBT Gateway Bridge — v2.6)

**Primary method: GBT Orchestrator Gateway** — all endpoints return standard JSON envelope.

```
Base: https://speculate-armband-retinal.ngrok-free.dev
Auth: X-API-Key header (hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6) for write endpoints
```

| Endpoint | Method | What GBT Gets |
|---|---|---|
| `/gateway/health` | GET | Gateway health + service count |
| `/gateway/services` | GET | Service registry (all 11 endpoints) |
| `/gateway/project-state` | GET | Full live system state (this file) |
| `/gateway/project/64EW/brain` | GET | 64 Eastwood project brain snapshot |
| `/gateway/project/101F/brain` | GET | 101 Francis project brain snapshot |
| `/gateway/project/1355R/brain` | GET | 1355 Riverside project brain snapshot |
| `/gateway/project/{code}/schedule` | GET | Schedule status for a project |
| `/gateway/project/{code}/bids` | GET | Bid packages and procurement |
| `/gateway/project/{code}/pm` | GET | PM console — health, risks, actions |
| `/gateway/executive/report` | GET | Morning brief across all projects |
| `/gateway/executive/mission-control` | GET | Mission control — all KPIs |
| `/gateway/knowledge/vendor?name=X` | GET | Vendor cross-project lookup |
| `/gateway/knowledge/issues?q=X` | GET | Similar issues semantic search |
| `/gateway/drive/search?q=X` | GET | Search Google Drive |
| `POST /gateway/agent/handoff` | POST | Send implementation request to Claude Code |
| `POST /gateway/drive/write` | POST | Write plain text/markdown directly to Drive — no base64 needed |

**Standard response envelope** (all endpoints):
```json
{
  "status": "ok",
  "timestamp": "2026-06-28T...",
  "execution_time_ms": 120,
  "source_system": "hci-api",
  "payload": { ... },
  "warnings": [],
  "errors": []
}
```

**Fallback read methods:**
| Method | Status | URL |
|---|---|---|
| Project state (direct) | 🟢 LIVE | `https://speculate-armband-retinal.ngrok-free.dev/project-state` (no auth) |
| Google Drive | 🟢 LIVE | `https://drive.google.com/file/d/1Jjug6nbx-mGN9v4GrEyofkGXY5nMHvpP/view` |
| GitHub raw | 🟢 LIVE | `https://raw.githubusercontent.com/buck-HCI-AI/HCI_AI_Operating_System/main/LIVE_PROJECT_STATE.md` |
| MCP | ❌ Claude-only | Not available to ChatGPT |

---

## Implementation Repository
- **Location:** /Users/buckadams/HCI_AI_Operating_System (local Mac)
- **GitHub:** https://github.com/buck-HCI-AI/HCI_AI_Operating_System
- **Branch:** main (merged 2026-06-26)
- **GitHub URL:** https://github.com/buck-HCI-AI/HCI_AI_Operating_System
- **GitHub raw (LIVE_PROJECT_STATE):** https://raw.githubusercontent.com/buck-HCI-AI/HCI_AI_Operating_System/main/LIVE_PROJECT_STATE.md
- **Last Commit:** Merge: Implementation + Program Repository unified

---

## [STATE CHANGE] 2026-06-28 — BTW-4/8/6/9 Build Sprint (Claude Code)

### Built This Session
| Item | Status | Details |
|------|--------|---------|
| BTW-4: Event Timeline | COMPLETE | 379 project events backfilled (daily logs, risks, RFIs, meetings, awards, COs). Gateway endpoint live: `/gateway/project/{code}/timeline` |
| BTW-8: PM Weekly Digest | COMPLETE | New endpoint `/mvp/projects/{code}/weekly-digest` — last 7 days summary, open items, highlights. Gateway route added. |
| BTW-8: Gateway exposure | COMPLETE | 4 BTW-8 endpoints now in gateway: weekly-digest, client-comms, action-list, timeline |
| BTW-6: Pilot Weekly n8n | COMPLETE | AUTO-PILOT-WEEKLY — Monday 07:30 Gate5 Digest (ID: MtJBXUpT8hZX6SvV) pulling from all 3 pilot projects |
| BTW-9: Qdrant Foundation | COMPLETE | 5 collections populated: vendor_intelligence(200), project_memory(2690+), hci_sops(386), lessons_learned(88), hci_historical_costs(300) |
| Field Interface | COMPLETE | 6 field MCP tools (43 total), system prompt designed, 8/8 tests PASS, sent to GBT for parallel testing |

### Decisions Pending Buck
1. **Gate 5 go-live** — authorize before July 1
2. **SS daily log auto-write** — bypass approval queue for field log submissions? (Currently queued_for_approval)
3. **Hendrickson GPT** — create separate Custom GPT for Jim/Buck field access? GBT to advise
4. **1355R** — Jim Hendrickson to enter first daily log before July 1
5. **246GW** — superintendent name needed to activate

### Waiting For GBT
- Field interface test results (8 tests sent)

---

## [STATE CHANGE] 2026-07-01 — Sprint 3 Open: AI Communication Reliability + Data Consistency (Claude Code)

Executed per ChatGPT (Chief Architect/ARB) GBT handoffs "Implementation Directive: Sprint State Fixes + AI Communication Reliability" and "Production Warm Start", both 2026-07-01.

### Built This Session
| Item | Status | Details |
|------|--------|---------|
| Directive lifecycle reconciliation | COMPLETE | Migration 021 — `ai_messages` status vocab reconciled to ISSUED/RECEIVED/IN_PROGRESS/COMPLETE/BLOCKED/REJECTED per ARB (was NEW/FAILED, flagged as unresolved in ADR-007). Extended, not duplicated. |
| Directive required fields | COMPLETE | Added priority, received_at, acknowledged_at, started_at, completed_at, blocked_reason, source_of_truth_link to `ai_messages` |
| New gateway endpoints | COMPLETE | `GET /gateway/ai/messages/{id}`, `POST /gateway/ai/messages/{id}/acknowledge`, `GET /gateway/ai/directives/stale`, `POST /gateway/heartbeat` |
| Heartbeat extension | COMPLETE | `ai_agent_heartbeat` gained role, current_task, last_directive_id, metadata |
| 101F schedule variance | VERIFIED CONSISTENT + CLARIFIED | Executive Report already agreed with LIVE_PROJECT_STATE.md (+5d = -5 days signed) — root "bug" was a count-field (`total_variance_items: 1`) being misread as the day value. Added explicit `schedule_variance_days` signed field to Executive Report so this can't recur. |
| 1355R risk count | ROOT CAUSE FIXED | Mission Control was NOT reading test data — it was reading a stale algorithmic snapshot (`project_brain_snapshots.risk_count=1`, health=GREEN) and an empty/dead table (`project_risks_computed`, 0 rows, so "top risks" was always empty) instead of the canonical `risks` table that Executive Report/PM Console/role_owner use (5 open risks, 2 high severity, health=RED). Fixed `executive.py mission_control()` to reconcile against the canonical table. |
| Tests | COMPLETE | `test_ai_control_plane.py` extended — 65/65 passing, including new 101F/1355R consistency and directive-lifecycle assertions |
| Sprint metadata | COMPLETE | Sprint 2 closed (technical criteria), Sprint 3 opened — see CURRENT_SPRINT.md |

### Decisions Pending Buck / Chief Architect
1. **Sprint 2 formal ARB close ruling** — technical criteria met this session; Chief Architect to review implementation report and issue formal close
2. **Gate 5 Pilot window** (2026-06-25 to 2026-07-01) closes today — pilot review/go-forward decision is Buck's
3. Prior open items unchanged: n8n API connections (AUTO-014/015), Houzz pipeline (HZ-004/005), branch protection (INT-013)
- Field operations architecture design (SS/PM daily workflows, Hendrickson GPT vs GBT)

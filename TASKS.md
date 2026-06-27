# TASKS.md
## HCI AI Operating System — Active Task Register

**Organization:** Hendrickson Construction, Inc.
**Owner:** @buck-HCI-AI
**Last Updated:** 2026-06-27 (Sprint 1 CLOSED. Sprint 2 open — AUTO-016, HZ-003, AUTO-025 done by Claude Code)
**Authority:** SPRINT_OPERATING_MODEL.md
**Parent Document:** PROJECT.md

---

## Status Legend
- `[ ]` Todo
- `[~]` In Progress
- `[x]` Done
- `[!]` Blocked

---

## Active Sprint: Sprint 2 — Registry Consolidation

### Governance Layer (✅ Complete)

| Status | Task ID | Task | Assigned To | Sprint |
|---|---|---|---|---|
| [x] | GOV-001 | GitHub Project created: HCI AI Development | Browser Claude | Sprint 0 |
| [x] | GOV-002 | Milestones created: Sprint 0–10 | Browser Claude | Sprint 0 |
| [x] | GOV-003 | 13 labels created | Browser Claude | Sprint 0 |
| [x] | GOV-004 | 5 issue templates created | Browser Claude | Sprint 0 |
| [x] | GOV-005 | CODEOWNERS created | Browser Claude | Sprint 0 |
| [x] | GOV-006 | CONTRIBUTING.md created | Browser Claude | Sprint 0 |
| [x] | GOV-007 | PULL_REQUEST_TEMPLATE.md created | Browser Claude | Sprint 0 |
| [x] | GOV-008 | HCI_AI_CONSTITUTION.md authored | Browser Claude | Sprint 0 |
| [x] | GOV-009 | AI_TEAM_CHARTER.md authored | Browser Claude | Sprint 0 |
| [x] | GOV-010 | AUTOMATION_GOVERNANCE.md authored | Browser Claude | Sprint 0 |
| [x] | GOV-011 | APPROVAL_GATES.md authored | Browser Claude | Sprint 0 |
| [x] | GOV-012 | SPRINT_OPERATING_MODEL.md authored | Browser Claude | Sprint 0 |
| [x] | GOV-013 | AI_WORKFLOW_ROLES.md authored | Browser Claude | Sprint 0 |
| [x] | GOV-014 | PROJECT.md created | Browser Claude | Sprint 0 |
| [x] | GOV-015 | GOVERNANCE_COMPLETION_REPORT.md created | Browser Claude | Sprint 0 |

### Houzz Browser Intelligence Workstream (✅ Design Complete)

| Status | Task ID | Task | Assigned To | Sprint |
|---|---|---|---|---|
| [x] | HZ-DESIGN-001 | HOUZZ_READ_ONLY_AUDIT.md created | Browser Claude | Sprint 0 |
| [x] | HZ-DESIGN-002 | HOUZZ_DAILY_LOG_WORKFLOW.md created | Browser Claude | Sprint 0 |
| [x] | HZ-DESIGN-003 | HOUZZ_BROWSER_AGENT_STRATEGY.md created | Browser Claude | Sprint 0 |
| [x] | HZ-DESIGN-004 | HOUZZ_APPROVAL_GATES.md created | Browser Claude | Sprint 0 |
| [x] | HZ-DESIGN-005 | HOUZZ_AUTOMATION_BACKLOG.md created | Browser Claude | Sprint 0 |
| [x] | HZ-DESIGN-006 | HOUZZ_BROWSER_AGENT_COMPLETION_REPORT.md created | Browser Claude | Sprint 0 |
| [x] | HZ-DESIGN-007 | TASKS.md created with all Houzz backlog items | Browser Claude | Sprint 0 |
| [x] | HZ-DESIGN-008 | PROJECT.md updated with Houzz workstream | Browser Claude | Sprint 0 |

### Program Repository Integration Layer (✅ Design Complete)

Created by Browser Claude — Integration Planning Phase (Sprint 0 extension).

| Status | Task ID | Task | Assigned To | Sprint |
|---|---|---|---|---|
| [x] | INT-DESIGN-001 | PROGRAM_REPOSITORY_STATUS.md created | Browser Claude | Sprint 0 |
| [x] | INT-DESIGN-002 | PROGRAM_REPOSITORY_INVENTORY.md created | Browser Claude | Sprint 0 |
| [x] | INT-DESIGN-003 | REPOSITORY_RELATIONSHIP_MAP.md created | Browser Claude | Sprint 0 |
| [x] | INT-DESIGN-004 | IMPLEMENTATION_INTEGRATION_PLAN.md created | Browser Claude | Sprint 0 |
| [x] | INT-DESIGN-005 | LIVE_PROJECT_STATE_TEMPLATE.md created | Browser Claude | Sprint 0 |
| [x] | INT-DESIGN-006 | TASKS.md and PROJECT.md updated with integration layer | Browser Claude | Sprint 0 |

---

## Backlog: Sprint 1 — System Verification

### Core Automation Setup

| Status | Task ID | Task | Label | Assigned To | Notes |
|---|---|---|---|---|---|
| [x] | AUTO-001 | Set up n8n daily repository status report workflow | n8n workflow | Claude Code | Active — fires 07:00, writes reports/daily/ |
| [x] | AUTO-002 | Set up n8n workflow health check (daily 06:00) | n8n workflow | Claude Code | Active — fires 06:00, writes reports/health/ |
| [x] | AUTO-003 | Set up n8n self-status report workflow (daily 08:00) | n8n workflow | Claude Code | Active — fires 08:00, writes reports/sprint/ |
| [x] | AUTO-004 | Create reports/ directory structure in repository | workflow | Claude Code | |
| [ ] | AUTO-005 | Implement Gate H: HubSpot write approval workflow in n8n | n8n hubspot | n8n | |
| [ ] | AUTO-006 | Implement Gate G: PR merge notification to human owner | workflow | n8n | |
| [x] | AUTO-007 | Create CURRENT_SPRINT.md for Sprint 1 | documentation | ChatGPT | |
| [x] | AUTO-008 | Create initial CHANGELOG.md | documentation | Claude Code | |

### Integration Activation — Sprint 1
> Requires @buck-HCI-AI architecture review before executing.

| Status | Task ID | Task | Owner | Notes |
|---|---|---|---|---|
| [x] | INT-001 | Confirm: single repo or two repos? | @buck-HCI-AI | Single unified repo — decision made 2026-06-26 |
| [x] | INT-002 | Identify any separate Claude Code implementation repository | @buck-HCI-AI | No separate repo — all merged to main |
| [ ] | INT-003 | Audit 04_Workflows/ for actual workflow count and status | ChatGPT | |
| [x] | INT-004 | Confirm HubSpot and Google Drive API connection status | Claude Code | Both live — HubSpot deals/contacts, Drive confirmed |
| [x] | INT-005 | Confirm Qdrant and Postgres live status | Claude Code | Both live — 190 vectors, 4 projects, all tables healthy |
| [ ] | INT-006 | List all active n8n workflow names and schedules | n8n | |
| [x] | INT-007 | Update TASKS.md with all pre-existing work marked complete | Claude Code | Done 2026-06-26 |
| [ ] | INT-008 | Human owner approves LIVE_PROJECT_STATE.md as shared truth | @buck-HCI-AI | |
| [x] | INT-009 | Create LIVE_PROJECT_STATE.md from template | Claude Code | Drive ID: 1Jjug6nbx-mGN9v4GrEyofkGXY5nMHvpP |
| [ ] | INT-010 | Register all existing workflows in AUTOMATION_GOVERNANCE.md | n8n + ChatGPT | |
| [x] | INT-011 | Register all API connections in PROJECT.md Integration Registry | Claude Code | HubSpot, Drive, Sheets, Graph API, Qdrant, Postgres live |
| [x] | INT-012 | Create CHANGELOG.md with all historical work documented | Claude Code | Done 2026-06-26 |
| [ ] | INT-013 | Enable branch protection on main | @buck-HCI-AI | |

### Houzz Workstream — Sprint 1

| Status | Task ID | Task | Label | Assigned To |
|---|---|---|---|---|
| [ ] | HZ-001 | Houzz Daily Log Reader (Manual extraction test) | workflow n8n | Browser Claude |
| [x] | HZ-002 | Create reports/houzz/ folder structure | workflow documentation | Claude Code |
| [x] | HZ-003 | Register Houzz in Integration Registry (05_Database/) | registry workflow | Claude Code | Done 2026-06-27 — status: pending_data |

Acceptance Criteria — HZ-001:
- Browser Claude reads one complete Houzz daily log (all 10 data categories)
- Output saved to reports/houzz/daily/YYYY-MM-DD-[project]-log-extraction.md
- Extraction log saved
- Zero write actions taken in Houzz
- Passes HOUZZ_READ_ONLY_AUDIT.md compliance checklist

---

## Backlog: Sprint 2 — Registry Consolidation

### Core

| Status | Task ID | Task | Label | Assigned To |
|---|---|---|---|---|
| [ ] | AUTO-010 | Set up weekly sprint review summary workflow | n8n workflow | n8n |
| [ ] | AUTO-011 | Set up weekly registry duplicate check | n8n registry | n8n |
| [ ] | AUTO-012 | Set up weekly broken link check | n8n workflow | n8n |
| [ ] | AUTO-013 | Set up HubSpot/Drive reconciliation report | n8n hubspot drive | n8n |
| [ ] | AUTO-014 | Connect HubSpot API to n8n | hubspot registry | n8n |
| [ ] | AUTO-015 | Connect Google Drive API to n8n | drive registry | n8n |
| [x] | AUTO-016 | Build Integration Registry schema in 05_Database/ | registry | Claude Code | Done 2026-06-27 — 8 integrations seeded |
| [ ] | AUTO-017 | Implement Gate E: client comms approval workflow | n8n workflow | n8n |
| [ ] | AUTO-018 | Implement Gate F: financial action approval workflow | n8n workflow | n8n |

### Houzz Workstream — Sprint 2

| Status | Task ID | Task | Label | Assigned To |
|---|---|---|---|---|
| [ ] | HZ-004 | n8n daily log extraction trigger (5:30 PM, all active projects) | n8n workflow | n8n |
| [ ] | HZ-005 | Houzz-to-HCI-AI Project Health Engine (7 intelligence artifacts) | workflow registry | ChatGPT + n8n |

---

## Backlog: Sprint 3 — HubSpot & Drive Integration

### Houzz Workstream — Sprint 3

| Status | Task ID | Task | Label | Assigned To |
|---|---|---|---|---|
| [ ] | HZ-006 | HubSpot Project Status Write — Gate HZ-H1 implementation | hubspot workflow | n8n |
| [ ] | HZ-007 | Drive Daily Intelligence Filing (auto, AI folder) | drive workflow | n8n |

---

## Backlog: Sprint 4 — Workflow Certification

### Houzz Workstream — Sprint 4

| Status | Task ID | Task | Label | Assigned To |
|---|---|---|---|---|
| [ ] | HZ-008 | Daily Executive Brief from Houzz (portfolio view, 1-pager) | workflow n8n | ChatGPT + n8n |
| [ ] | HZ-009 | PM Action Item Extractor (cross-project ranked list) | workflow | ChatGPT + n8n |

---

## Backlog: Sprint 5 — MCP Implementation

### Houzz Workstream — Sprint 5

| Status | Task ID | Task | Label | Assigned To |
|---|---|---|---|---|
| [ ] | HZ-010 | Houzz Schedule Reader (activity list, variance analysis) | workflow mcp | Browser Claude |
| [ ] | HZ-011 | Houzz Photo Intelligence Extractor (metadata + vision AI) | workflow mcp | Browser Claude + ChatGPT |

---

## Backlog: Sprint 8 — Production Validation

### Houzz Workstream — Sprint 8

| Status | Task ID | Task | Label | Assigned To |
|---|---|---|---|---|
| [ ] | HZ-012 | Superintendent Daily Log Draft Assistant | workflow n8n | ChatGPT + n8n |

---

## Backlog: Sprint 9 — Go Live

### Houzz Workstream — Sprint 9

| Status | Task ID | Task | Label | Assigned To |
|---|---|---|---|---|
| [ ] | HZ-013 | Full Houzz Intelligence Pipeline — Production (end-to-end) | production workflow | n8n + all agents |

---

## ACR-004: Continuous Mining & Learning Engine

| Status | Task ID | Task | Assigned To | Notes |
|---|---|---|---|---|
| [x] | ACR-004-01 | Build BaseMiner abstract class + approval gate routing | Claude Code | base_miner.py — queue_for_approval uses correct approval_queue columns |
| [x] | ACR-004-02 | Build HubSpotMiner (READ-ONLY from DB mirror) | Claude Code | Mines deals, contacts, tasks; never writes to HubSpot |
| [x] | ACR-004-03 | Build DriveMiner (drive_sync_log) | Claude Code | Classifies by doc type, infers project |
| [x] | ACR-004-04 | Build HouzzMiner (houzz_daily_logs, schedule_items) | Claude Code | Framework active; awaiting Browser Agent data |
| [x] | ACR-004-05 | Build OutlookMiner (Graph API read-only) | Claude Code | ALL emails queued for approval — never auto-replies |
| [x] | ACR-004-06 | Build HistoricalCostMiner (bid variance analysis) | Claude Code | Alerts if avg variance > 15% per CSI division |
| [x] | ACR-004-07 | Build VendorIntelligenceMiner (bid stats) | Claude Code | Updates vendors.bid_count, win_rate_pct, etc. |
| [x] | ACR-004-08 | Build LessonsLearnedMiner (meetings + BL records) | Claude Code | Dedup via source_reference; queue-only |
| [x] | ACR-004-09 | Build ExecutiveAggregator (KPIs + LIVE_PROJECT_STATE.md) | Claude Code | Uses correct kpi_snapshots schema (kpi_code, scope, value) |
| [x] | ACR-004-10 | Build MiningOrchestrator + dry_run safety default | Claude Code | dry_run=True; _GO_LIVE_AUTHORIZED=False |
| [x] | ACR-004-11 | Apply schema migration 005 (vendors, hist_cost, lessons, mining_runs) | Claude Code | All additive — no existing columns changed |
| [x] | ACR-004-12 | Dry-run validation — all 8 miners pass | Claude Code | 376 records scanned, 39 intelligence extracted, 0 writes |
| [x] | ACR-004-13 | FastAPI router /api/v1/services/mining/* (6 endpoints) | Claude Code | All endpoints live; lazy import fix applied |
| [x] | ACR-004-14 | Architecture Review Report submitted | Claude Code | ACR-004-ARCHITECTURE-REVIEW.md — awaiting ChatGPT go-live ACR |
| [x] | ACR-004-15 | Add MCP tools: RunMiner, GetMiningStatus, GetMiningLog | Claude Code | Done 2026-06-27 — 35 total MCP tools |
| [x] | ACR-004-16 | Create n8n mining orchestration workflow — AUTO-004 active 03:00 daily | Claude Code | Pending go-live authorization |
| [x] | ACR-004-17 | Enable continuous execution — _GO_LIVE_AUTHORIZED=True, authorized by Buck 2026-06-27 | Claude Code | REQUIRES ChatGPT ACR + Buck confirmation |

---

## Backlog: Sprint 3–4 (Core)

| Status | Task ID | Task | Label | Assigned To |
|---|---|---|---|---|
| [ ] | AUTO-019 | Build HubSpot contact sync workflow | hubspot n8n | n8n |
| [ ] | AUTO-020 | Build Drive file indexing workflow | drive n8n | n8n |
| [ ] | AUTO-021 | Set up production readiness scorecard automation | workflow testing | ChatGPT / n8n |
| [ ] | AUTO-022 | Configure branch protection rules on main | workflow | Human Owner |
| [ ] | AUTO-023 | Implement MCP connectors | mcp | Claude Code |
| [ ] | AUTO-024 | Set up n8n workflow status dashboard | n8n workflow | n8n |
| [x] | AUTO-025 | Gate audit log file structure setup | workflow documentation | Claude Code | Done 2026-06-27 — logs/gates/ created |

---

## Task Count Summary

| Category | Total | Done | In Progress | Todo | Blocked |
|---|---|---|---|---|---|
| Governance (GOV) | 15 | 15 | 0 | 0 | 0 |
| Houzz Design (HZ-DESIGN) | 8 | 8 | 0 | 0 | 0 |
| Integration Planning (INT-DESIGN) | 6 | 6 | 0 | 0 | 0 |
| Core Automation (AUTO) | 25 | 9 | 0 | 16 | 0 |
| Houzz Implementation (HZ) | 13 | 2 | 0 | 10 | 1 |
| Integration Activation (INT) | 13 | 8 | 0 | 5 | 0 |
| Mining Engine (ACR-004) | 17 | 17 | 0 | 0 | 0 |
| **Total** | **97** | **65** | **0** | **31** | **1** |

---

*Governed by SPRINT_OPERATING_MODEL.md | Owner: @buck-HCI-AI | Hendrickson Construction, Inc.*
*TASKS.md is archived at sprint close to reports/sprint/sprint-N-tasks.md*

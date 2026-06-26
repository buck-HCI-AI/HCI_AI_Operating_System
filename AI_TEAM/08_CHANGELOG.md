# Changelog

## 2026-06-26 — MCP Server Live + Full System Audit + HubSpot IDs Linked

**Session:** MCP build, AI team connection, full audit, P0 fixes  

### What Was Built / Fixed

| Change | Detail |
|--------|--------|
| MCP Server — 26 tools | `services/mcp_server/hci_mcp_server.py` — full spec implementation; FastMCP on port 8080 |
| MCP proxy in main.py | `/mcp` and `/mcp/{path}` routes forward to port 8080 via httpx |
| Auth middleware update | `PROTECTED_PREFIXES` includes `/mcp` |
| GBT connection file | `/Users/buckadams/Desktop/HCI_AI_GBT_Connect.txt` |
| Claude.ai directive file | `/Users/buckadams/Desktop/HCI_AI_ClaudeAI_Directive.txt` |
| Full System Audit | 6 deliverables in `HCI_AI_Audit_20260626/` — 27 tests, 30-item backlog, gap report |
| HubSpot deal IDs | Linked all 3 pilot projects in projects table |
| SOP MCP tool fix | `ReadConstructionOS` now calls `/api/v1/sop/registry` for category=sops/all |
| HistCost MCP tool fix | `HistoricalCostLookup` now calls `/search?q=` not `/lookup` |
| 4th project identified | id=4 = "83 Sagebrusch Ln." — no HubSpot deal found |
| n8n workflows audited | 15 total (9 active, 6 inactive); TMP-cl-84994d and Chrome Bridge flagged for retirement |

### Key Endpoint Paths (verified correct)
- Executive report: `/api/v1/mvp/exec-report`
- SOP registry: `/api/v1/sop/registry`
- Historical cost search: `/api/v1/services/historical-cost/search?q=`
- MCP: `https://speculate-armband-retinal.ngrok-free.dev/mcp`

---

## 2026-06-26 — Bid Leveling Service (22/22 tests pass)

**Trigger:** "BTW This should be updated system wide" — Buck authorized system-wide bid leveling service  
**Buck message:** "BTW - this should be in the bid level work flow - and i need gbt to have full bid-level capabilities when it connects as well - full read write etc all files and types - create folders if needed - create files if needed"

### What Was Built

`services/bid_leveling/` — full HCI AI service registered at `/api/v1/services/bid-leveling/`

| Component | Detail |
|-----------|--------|
| `bid_leveling_service.py` | Core service: reads Sheets, parses bid data, generates Excel, manages Drive folders, queues uploads |
| `routes.py` | 11 endpoints: run workflow, dry run, Drive create/upload/list, Sheets read/write, project data |
| Registered in `main.py` | `_load_svc("bid_leveling")` → `/api/v1/services/bid-leveling/` |
| `tests/test_bid_leveling.py` | 22/22 PASS across 6 test groups |
| `docs/BID_LEVELING_SERVICE.md` | Full reference |

### Key Decisions

- **Tab name auto-detection**: 1355 Riverside uses `Sheet1`, 101F/64EW use `Bid Tracking`; service tries both
- **Division number parsing**: regex `\b(\d{1,2})\b` handles both "Division 2 - Site Work" and "06 — Wood..." formats
- **GBT write access**: `/drive/create-folder`, `/drive/upload-file`, `/sheets/write` exposed as direct write endpoints (no approval queue) — for AI agent use with full access
- **Approval queue for HCI workflow**: live run queues via approval queue; Buck approves then executes
- **101 Francis 00_Bids pre-wired**: `KNOWN_BIDS_FOLDERS[2]` = existing folder ID avoids duplicate creation
- **HTTPError 400 = tab not found**: Sheets API returns 400 (not 404) when a tab name doesn't exist

### Test Results

| Group | Tests | Result |
|-------|-------|--------|
| BL-SVC: Service Registration | 3 | ✅ PASS |
| BL-READ: Sheet Reading | 5 | ✅ PASS |
| BL-DRY: Dry Run Workflow | 7 | ✅ PASS |
| BL-EXCEL: Excel Generation | 2 | ✅ PASS |
| BL-DRIVE: Drive Read/Write | 2 | ✅ PASS |
| BL-QUEUE: Approval Queue | 3 | ✅ PASS |
| **Total** | **22** | **✅ 22/22 PASS** |

### Files Created / Modified

- `services/bid_leveling/__init__.py` (NEW)
- `services/bid_leveling/bid_leveling_service.py` (NEW)
- `services/bid_leveling/routes.py` (NEW)
- `api/main.py` (UPDATED — added bid_leveling service)
- `tests/test_bid_leveling.py` (NEW)
- `docs/BID_LEVELING_SERVICE.md` (NEW)
- `AI_TEAM/00_STATUS.md`, `02_ACTIVE_WORK.md`, `05_BACKLOG.md`, `06_NEXT_SESSION.md`, `08_CHANGELOG.md` (UPDATED)

---

## 2026-06-26 — Phase 16: MVP Sprint 1 COMPLETE (48/48 tests pass)

**Trigger:** `HCI_AI_MVP_Sprint_1_Daily_Operations_and_Background_Learning_Directive_for_Claude_Code_v1.pdf`  
**Buck authorization:** "BTW - can you complete without prompting me and run this till complete and we double check work & test in the morning?"

### What Was Built

6 daily operation workflows for 3 pilot projects (64EW, 101F, 1355R) + 3 new background services + 4 new DB tables:

| Workflow | Endpoint | ROI Saved |
|----------|----------|-----------|
| Project Brain Init | `GET /mvp/projects/{code}/init` | 28 min/run |
| Bid Management | `POST /mvp/projects/{code}/bids/import` | 42 min/bid |
| Daily Log + Field Intelligence | `POST /mvp/projects/{code}/daily-log` | 27 min/log |
| PM Weekly Review | `GET /mvp/projects/{code}/pm-weekly-review` | 87 min/week |
| Schedule/Status Intelligence | `GET /mvp/projects/{code}/schedule-status` | 28 min/run |
| Executive Reporting | `GET /mvp/executive-report` | 59 min/run |

New services: Background Learning (13-status pipeline), Approval Queue (all writes gated), Connector Registry (9 pilot connectors, all read_only).

New DB tables: `background_learning_records`, `connector_registry`, `approval_queue`, `roi_log`

### Key Technical Decisions

- **Dry-run default.** All write endpoints default to `dry_run=true`. Nothing is written without explicit `dry_run=false` + approval queue entry + Buck approval.
- **Approval queue is non-executing.** `approve()` marks approved but does NOT execute. Caller must call `mark_executed()` after applying the change. System never auto-executes.
- **ROI `minutes_saved` is a computed column.** PostgreSQL `GENERATED ALWAYS AS (baseline_minutes - ai_assisted_minutes) STORED`. Never set directly.
- **`schedule_variance` uses `detected_at`, not `created_at`.** Table has no `created_at` column and no `date` column. Use `detected_at` for all ORDER BY.
- **`daily_logs` uses `log_date` and `work_performed`**, not `date` and `notes`.
- **Drive sync uses `file_path`/`file_name`**, not `file_hash` — `drive_sync_log` has no `file_hash` column.
- **Test results file uses absolute path** via `os.path.dirname(os.path.abspath(__file__))` — relative path broke when run from project root.

### Files Created

**Code:** `api/routers/mvp_ops.py`, `services/background_learning/`, `services/approval_queue/`, `services/connector_registry/`, `database/mvp_sprint_1_schema.sql`, `tests/test_mvp_sprint_1.py`

**Docs:** 14 docs files (`docs/MVP_SPRINT_1_*.md` + workflow docs), `BOOK_00/19_MVP_SPRINT_1_DAILY_OPERATIONS.md`, `BOOK_01/19_DAILY_OPERATIONS_USING_HCI_AI.md`

**AI_TEAM:** `00_STATUS.md`, `02_ACTIVE_WORK.md`, `05_BACKLOG.md`, `06_NEXT_SESSION.md`, `07_BLOCKERS.md`, `08_CHANGELOG.md`

### Test Results: 48/48 PASS

```
MS-01 Project Brain Init:       4/4 ✅
MS-02 Bid Management:           4/4 ✅
MS-03 Daily Log + Field Intel:  5/5 ✅
MS-04 PM Weekly Review:         3/3 ✅
MS-05 Schedule/Status Intel:    3/3 ✅
MS-06 Executive Reporting:      4/4 ✅
BL-01 Background Learning:      8/8 ✅
AQ-01 Approval Queue:           5/5 ✅
CR-01 Connector Registry:       3/3 ✅
ROI-01 ROI Log:                 3/3 ✅
SP-01 Sprint Status:            3/3 ✅
SC-01 Safety / Approval Controls: 3/3 ✅
TOTAL: 48/48 PASS
```

---

## 2026-06-26 — Phase 15: Platform Integration Layer COMPLETE

**Trigger:** `HCI_AI_Platform_Integration_Sprint_Master_Directive_for_Claude_Code_v1.pdf` + Buck: "ok do it -"

### What Was Built

5 shared platform capabilities — every SOP and workflow can now consume them:

| Capability | Service | Endpoints | Key Features |
|---|---|---|---|
| Identity & Permissions | `services/platform/identity/` | 6 | 12 roles, 42 permissions, authority levels (owner=5 → ai=1) |
| Event Bus | `services/platform/event_bus/` | 3 | 12 event types, correlation UUIDs, retry tracking, persistence |
| Notification Center | `services/platform/notifications/` | 6 | 17 types, escalation thresholds, construction-specific notifiers |
| Audit Trail | `services/platform/audit/` | 5 | 3-source unification (SOP + workflow + platform), project timeline |
| Unified Search | `services/platform/search_gateway/` | 7 | Intent routing (Postgres + Qdrant), confidence scores, citations |

### Key Technical Decisions

- **No external broker.** Event Bus persists to `platform_events` (Postgres). Sufficient at current scale; swap to Redis Streams or Kafka later if needed.
- **sys.path conflict.** Python stdlib `platform` module name collides with our `services/platform/` package. Fix: import `from event_bus.event_bus_service import EventBus` (not `from platform.event_bus...`). This must be maintained in `base_sop.py`.
- **Keyword extraction.** Multi-word search queries broken against LIKE — added `_best_keyword()` to strip stopwords and extract a single useful token before Postgres LIKE match.
- **Correlation IDs.** All Event Bus events and Audit records carry a UUID correlation ID. Pass it explicitly to link related events across services.

### SOP Integration

`BaseSOP.transition_status()` now calls `_emit()` after every DB status update. `_emit()` resolves the platform package path at runtime and publishes `sop.status_changed` to the Event Bus. If the Event Bus is unreachable, the SOP operation continues — Event Bus failure never blocks a SOP.

### Roles Added

`owner`, `administrator`, `pm`, `estimator`, `superintendent`, `accounting`, `contracts`, `architect`, `engineer`, `client`, `ai_agent`, `system` — 12 total, 42+ permissions.

### Files Created

- `05_Database/platform_schema.sql` — 5 tables + 12-role + 42-permission seed
- `services/platform/__init__.py`
- `services/platform/identity/identity_service.py`
- `services/platform/event_bus/event_bus_service.py`
- `services/platform/notifications/notification_service.py`
- `services/platform/audit/audit_service.py`
- `services/platform/search_gateway/search_gateway_service.py`
- `api/routers/platform.py` — 33 endpoints
- `tests/test_platform_integration.py` — 39 tests, **39 PASS, 0 FAIL**

### Files Modified

- `api/main.py` — registered platform router
- `services/sop_execution/shared/base_sop.py` — added `_emit()` + call in `transition_status()`
- `BOOK_00/06_API_LAYER.md` — added SOP + Platform rows to router table
- `AI_TEAM/00_STATUS.md` — phase 15 added; platform routes added to API table
- `AI_TEAM/01_ROADMAP.md` — Phase 4 SOP + Phase 5 Platform marked complete; Phase 6–8 added
- `AI_TEAM/04_ARCHITECTURE.md` — full stack diagram updated with Platform Integration Layer
- `AI_TEAM/08_CHANGELOG.md` — this entry

### Documentation Created

- `docs/PLATFORM_INTEGRATION_PLAN.md`
- `docs/IDENTITY_MODEL.md`
- `docs/EVENT_BUS_STANDARD.md`
- `docs/NOTIFICATION_STANDARD.md`
- `docs/AUDIT_TRAIL_STANDARD.md`
- `docs/SEARCH_ARCHITECTURE.md`
- `docs/INTEGRATION_SEQUENCE.md`

### Test Results

```
PT-00 Platform overview     1 PASS
PT-01 Identity              7 PASS
PT-02 Event Bus             5 PASS
PT-03 Notifications         7 PASS
PT-04 Audit Trail           8 PASS
PT-05 Unified Search        7 PASS
PT-IT Integration flows     4 PASS
─────────────────────────────────
TOTAL                      39 PASS  0 FAIL  0 CONDITIONAL
```

---

## 2026-06-26 — Phase 14h: Phase H Field Execution COMPLETE (SOP 17–18 + 20–30)

**Trigger:** Buck: "do all and test — then work on Platform Integration Sprint"  
**Full chain now live:** SOP 04 → 05 → 06 → 07 → 08 → 09 → 10 → 11 → 12 → 13 → 14 → 15 → 16 → 19 → 17 → 18 → 20 → 21 → 22 → 23 → [24 / 25 / 26 / 27 / 28 / 29 / 30]

### What Was Built

13 new SOPs (all 4 layers each — templates + agent + service + __init__ + router endpoints):

| SOP | Title | Endpoints | Key Rules |
|-----|-------|-----------|-----------|
| SOP 17 | Project Schedule | 7 | AI milestone generation; schedule risk analysis; handoff → SOP 18 |
| SOP 18 | Long-Lead Procurement | 6 | AI item identification; HIGH/CRITICAL risk flagging; supplier search |
| SOP 20 | Contract Setup | 6 | AI setup checklist; blocks approval if items pending |
| SOP 21 | Compliance | 6 | AI permit ID by jurisdiction; clear-to-build gate; handoff → SOP 22 |
| SOP 22 | COI / W-9 / Lien | 7 | HCI insurance minimums enforced on verify; handoff → SOP 23 |
| SOP 23 | Project Startup | 6 | safety/personnel/docs gate; ready-to-build approval; handoff → SOP 24 |
| SOP 24 | Superintendent Dashboard | 4 | Daily metric updates; AI daily brief; RED alert tracking |
| SOP 25 | Daily Log | 5 | AI risk analysis on each entry; PM notifications; weekly summary |
| SOP 26 | Field Coordination | 5 | AI RFI drafts from lessons_learned; open item tracking |
| SOP 27 | Quality Control | 4 | AI QC checklist; SC-03 fires on CRITICAL failure |
| SOP 28 | QC Detail Card | 5 | AI detail card per trade; hold-point tracking |
| SOP 29 | Safety | 5 | SC-03 fires on uncontrolled CRITICAL hazard; work-stop enforcement |
| SOP 30 | Inspection | 4 | AI prep checklist; SC-03 fires on FAIL/CORRECTION_NOTICE |

### Key Business Rules Enforced
- **SOP 21:** clear-to-build blocks unless building_permit + contractor_license are APPROVED
- **SOP 22:** HCI_COI_MINIMUMS: GL $1M, Aggregate $2M, WC $1M, Auto $1M — enforced at `verify_coi()`
- **SOP 23:** ready-to-build blocks if any safety/personnel/documents items still PENDING
- **SOP 27/29/30:** SC-03 stop conditions wired for CRITICAL quality, safety, and inspection failures
- **SOP 28:** hold-point architecture per trade with 5 HOLD_POINT_STATUS states

### API Totals After Phase H
- **27 SOPs active** (SOP 04–30)
- **189 total endpoints** at `/api/v1/sop/`
- **Registry:** `GET /api/v1/sop/registry` returns all 27

---

## 2026-06-25 — Phase 14h: Phase G Close Loop COMPLETE (SOP 12 + SOP 19)

**Trigger:** Buck said "go" (Phase G)  
**Full preconstruction + contract execution chain now live:** SOP 04 → 05 → 06 → 07 → 08 → 09 → 10 → 11 → 12 → 13 → 14 → 15 → 16 → 19

### What Was Built

Both SOPs follow the 4-layer pattern (templates + agent + service + __init__):

| SOP | Title | Agent Methods | Service Methods | Endpoints |
|-----|-------|---------------|-----------------|-----------|
| SOP 12 | Subcontractor CRM | research_sub_candidates, assess_sub_qualification, assess_bid_list_quality | start_bid_list, add_sub_candidate, run_ai_research, assess_sub, pm_approve_sub, pm_approve_list, hand_off_to_sop13, get_full_status | 8 |
| SOP 19 | Subcontract Agreement | draft_scope_section, draft_contract_section, verify_insurance_requirements, review_full_draft | start_agreement, run_ai_draft_all, draft_section, confirm_section, verify_insurance, run_final_review, pm_approve, record_execution, archive, get_full_status | 10 |

### Key Business Rules Enforced
- **SOP 12:** MIN_BIDDERS rule (3 PM-approved, non-DO_NOT_USE subs per trade) enforced at `pm_approve_list()`; SC-01 fires if count < 3
- **SOP 12:** `run_ai_research()` auto-populates candidates from vendor_memory (Qdrant) + Claude analysis; de-dupes against existing list
- **SOP 12:** `pm_approve_list()` runs final AI quality check before transitioning to APPROVED
- **SOP 19:** Gate 19-C (EXECUTION_AUTHORITY = "Principal or PM with written delegation") enforced at `record_execution()`
- **SOP 19:** `pm_approve()` blocks if any of 7 standard CONTRACT_SECTIONS are not yet PM-confirmed
- **SOP 19:** `verify_insurance()` checks 4 HCI minimums (GL $1M, Aggregate $2M, WC $1M, Auto $1M) and flags shortfalls at HIGH severity
- **SOP 19:** `run_ai_draft_all()` drafts all 7 sections in one call with section-type-specific guidance
- **SOP 19:** `archive()` enforces SC-04 gate check before final ARCHIVED status

### Chain Handoffs Wired
- SOP 11 → SOP 12 (optional path: use SOP 12 to build bid list before SOP 13)
- SOP 12 → SOP 13 (`hand_off_to_sop13` auto-creates SOP 13 Distribution instance)
- SOP 16 → SOP 19 (`hand_off_to_sop19` auto-creates SOP 19 Subcontract Agreement instance)

### Files Created (10 new files)
- `sop_12_sub_crm/`: templates, agent, service, __init__
- `sop_19_subcontract_agreement/`: templates, agent, service, __init__

### Files Modified
- `03_Source_Code/api/routers/sop.py` — updated header, imports (14 services), registry (14 SOPs), added 18 new endpoints (total ~100)
- `AI_TEAM/00_STATUS.md` — Phase 14h added; 14-SOP chain documented
- `AI_TEAM/08_CHANGELOG.md` — this entry

### Smoke Tests (Live API)
- SOP registry: 14 SOPs returned ✅
- SOP 12 bid-list create → status "In Progress", trade_name "Concrete" ✅
- SOP 19 instance create → status "In Progress", awarded_sub "Pacific Concrete Inc", award_amount $185,000 ✅

---

## 2026-06-25 — Phase 14g: Phase F Backfill COMPLETE (SOP 04–09)

**Trigger:** Buck said "Phase F — go"  
**Full preconstruction chain now live:** SOP 04 → 05 → 06 → 07 → 08 → 09 → 10 → 11 → 13 → 14 → 15 → 16

### What Was Built

All 6 backfill SOPs follow the 4-layer pattern:

| SOP | Title | Agent Methods | Service Methods | Endpoints |
|-----|-------|---------------|-----------------|-----------|
| SOP 04 | Plan Review | analyze_plan_section, flag_constructibility_risks, generate_rfi_list | start_review, add_plan_section, run_ai_analysis, pm_confirm, hand_off_to_sop05 | 6 |
| SOP 05 | Construction Narrative | draft_narrative_section, review_narrative_completeness | start_narrative, draft_section, run_ai_draft, confirm_section, run_completeness_check, pm_approve, hand_off_to_sop06 | 8 |
| SOP 06 | Missing Information / Risk Log | identify_gaps_from_review, flag_project_risks, prioritize_rfi_list | start_risk_log, add_missing_info, add_risk, resolve_item, run_ai_gap_check, close_log, hand_off_to_sop07 | 8 |
| SOP 07 | ROM Budget | generate_rom_estimate, flag_high_risk_line_items, compare_to_owner_target | start_rom, add_line_item, run_ai_estimate, pm_review, buck_approve (Gate 07-C), hand_off_to_sop09 | 7 |
| SOP 08 | Historical Cost Database | lookup_historical_cost, benchmark_cost_per_sf, add_cost_record | start_lookup, lookup_cost, benchmark_sf, add_cost_record, pm_confirm | 5 |
| SOP 09 | Budget Review | analyze_budget_variance, review_vs_owner_target, generate_buck_review_summary | start_review, revise_line_item, run_ai_review, pm_approve, buck_approve (Gate 09-C), hand_off_to_sop10 | 7 |

### Key Business Rules Enforced
- **SOP 04:** AI cross-trade risk analysis fires SC-03 stop on HIGH-severity constructibility risks
- **SOP 06:** `close_log()` blocks if any CRITICAL missing info items remain unresolved (SC-01)
- **SOP 07:** ROM > $500k triggers Gate 07-C (Buck approval); `hand_off_to_sop09()` enforces gate check
- **SOP 07:** AI auto-saves all generated line items and fires risk flags on LOW-confidence trades
- **SOP 09:** Budget > $500k triggers Gate 09-C (Buck approval); `hand_off_to_sop10()` enforces gate and auto-confirms SOP 10 budget input
- **SOP 09:** AI variance analysis pulls ROM from SOP 07 directly via parent_instance_id chain

### Chain Handoffs Wired
- SOP 04 → SOP 05 (`hand_off_to_sop05` auto-creates SOP 05 instance)
- SOP 05 → SOP 06 (`hand_off_to_sop06` auto-creates SOP 06 instance)
- SOP 06 → SOP 07 (`hand_off_to_sop07` auto-creates SOP 07 instance)
- SOP 07 → SOP 09 (`hand_off_to_sop09` auto-creates SOP 09 instance; skips SOP 08 which is standalone)
- SOP 09 → SOP 10 (`hand_off_to_sop10` auto-creates SOP 10 instance + confirms budget input)

### Files Created (24 new files)
- `sop_04_plan_review/`: templates, agent, service, __init__
- `sop_05_construction_narrative/`: templates, agent, service, __init__
- `sop_06_missing_info/`: templates, agent, service, __init__
- `sop_07_rom_budget/`: templates, agent, service, __init__
- `sop_08_historical_cost/`: templates, agent, service, __init__
- `sop_09_budget_review/`: templates, agent, service, __init__

### Files Modified
- `03_Source_Code/api/routers/sop.py` — updated header, imports (12 services), registry (12 SOPs), added 41 new endpoints (total 78)
- `docs/BOOK01_IMPLEMENTATION_STATUS.md` — Phase F → ✅
- `docs/SOP_CONVERSION_INVENTORY.md` — SOP 04–09 → 🔵 PHASE F BUILT
- `AI_TEAM/00_STATUS.md` — Phase 14g added; 12-SOP chain documented
- `AI_TEAM/08_CHANGELOG.md` — this entry

### Smoke Tests (Live API)
- SOP 04 instance create → id 21 ✅; add section (Concrete) → output_id 42 ✅
- SOP 06 instance create → id 24 ✅; status In Progress ✅
- SOP 07 instance create → id 22 ✅; add line item $42,500 ✅; subtotal correct ✅
- SOP 08 lookup create → id 25 ✅; status In Progress ✅
- SOP 09 instance create → id 23 ✅; status In Progress ✅
- Registry returns all 12 SOPs ✅

---

## 2026-06-25 — Phase 14f: Phase E Chain Expansion COMPLETE (SOP 10, 13, 14, 16)

**Trigger:** Buck said "Phase E — go"  
**Preconstruction chain now live:** SOP 10 → SOP 11 → SOP 13 → SOP 14 → SOP 15 → SOP 16

### What Was Built

All 4 SOPs follow the same 4-layer pattern as SOP 11 and SOP 15:

| SOP | Title | Agent Methods | Service Methods | Endpoints |
|-----|-------|---------------|-----------------|-----------|
| SOP 10 | Allowances / Alternates / Exclusions | suggest_allowances, flag_unusual_alternates, validate_exclusions | start, validate_inputs, start_work, add_allowance, add_alternate, add_exclusion, run_ai_review, pm_approve, buck_approve (Gate 10-C if pool > $50k), hand_off_to_sop11 | 11 |
| SOP 13 | Bid Distribution | draft_outreach_email, check_distribution_coverage, flag_sub_risks | start_distribution, log_sub_sent, confirm_receipt, run_ai_coverage_check, flag_sub_risks, pm_confirm_distribution, hand_off_to_sop14 | 8 |
| SOP 14 | Bid Follow-Up | draft_follow_up_message, summarize_response_status, flag_minimum_bid_risk | start_followup, log_follow_up, update_response_status, run_ai_summary, close_followup, hand_off_to_sop15 | 7 |
| SOP 16 | Buyout | draft_award_memo, check_scope_alignment | start_buyout, set_inputs, draft_award_memo, confirm_scope, initiate_subcontract, pm_confirm_buyout (Gate 16-C), hand_off_to_sop19 | 8 |

### Key Business Rules Enforced
- **SOP 10:** Total allowance pool > $50,000 triggers Gate 10-C (Buck approval required before SOP 11 handoff)
- **SOP 13:** Min 3 subs per trade enforced by `check_distribution_coverage()` with SC-01 stop if gaps remain
- **SOP 14:** `close_followup()` blocks if confirmed bidder count < 3 (MIN_BIDDERS); requires Buck exception
- **SOP 14:** `run_ai_summary()` auto-fires SC-01 stop for HIGH-severity minimum-bid risk (≤3 days until close)
- **SOP 16:** Gate 16-C (PM buyout confirmation) required before `hand_off_to_sop19()` proceeds

### Files Created
- `03_Source_Code/services/sop_execution/sop_10_allowances/sop_10_templates.py`
- `03_Source_Code/services/sop_execution/sop_10_allowances/sop_10_agent.py`
- `03_Source_Code/services/sop_execution/sop_10_allowances/sop_10_service.py`
- `03_Source_Code/services/sop_execution/sop_10_allowances/__init__.py`
- `03_Source_Code/services/sop_execution/sop_13_bid_distribution/sop_13_templates.py`
- `03_Source_Code/services/sop_execution/sop_13_bid_distribution/sop_13_agent.py`
- `03_Source_Code/services/sop_execution/sop_13_bid_distribution/sop_13_service.py`
- `03_Source_Code/services/sop_execution/sop_13_bid_distribution/__init__.py`
- `03_Source_Code/services/sop_execution/sop_14_bid_followup/sop_14_templates.py`
- `03_Source_Code/services/sop_execution/sop_14_bid_followup/sop_14_agent.py`
- `03_Source_Code/services/sop_execution/sop_14_bid_followup/sop_14_service.py`
- `03_Source_Code/services/sop_execution/sop_14_bid_followup/__init__.py`
- `03_Source_Code/services/sop_execution/sop_16_buyout/sop_16_templates.py`
- `03_Source_Code/services/sop_execution/sop_16_buyout/sop_16_agent.py`
- `03_Source_Code/services/sop_execution/sop_16_buyout/sop_16_service.py`
- `03_Source_Code/services/sop_execution/sop_16_buyout/__init__.py`

### Files Modified
- `03_Source_Code/api/routers/sop.py` — updated header, imports (6 services), registry (6 SOPs), added 34 new endpoints
- `docs/BOOK01_IMPLEMENTATION_STATUS.md` — Phase E → ✅
- `docs/SOP_CONVERSION_INVENTORY.md` — SOP 10, 13, 14, 16 → 🔵 PHASE E BUILT
- `AI_TEAM/00_STATUS.md` — Phase 14f added; SOP layer updated
- `AI_TEAM/08_CHANGELOG.md` — this entry

### Smoke Tests (Live API)
- SOP 10 instance create → id 18 ✅; add_allowance → output_id 40 ✅ (pool=$15,000, Buck review=false ✅)
- SOP 13 instance create → id 19 ✅; log_sub_sent → output_id 41 ✅; auto-advance to In Progress ✅
- SOP 16 instance create → id 20 ✅; set_inputs → status=In Progress ✅
- Registry returns all 6 SOPs ✅

---

## 2026-06-25 — Phase 14e: SOP Execution Phase D Testing COMPLETE

**Trigger:** Buck said "go" → Phase D (apply DB schema, run all SOP 11 + 15 tests)

### Phase D Test Results (29 tests total)
- **SOP 11 unit tests (UT-11-01 through UT-11-10):** 10/10 PASS
- **SOP 11 integration tests (IT-11-01 through IT-11-06):** 5/6 PASS, 1 CONDITIONAL (IT-11-04 vendor Qdrant empty — pre-existing KI-003)
- **SOP 15 unit tests (UT-15-01 through UT-15-08):** 8/8 PASS
- **SOP 15 integration tests (IT-15-01 through IT-15-05):** 5/5 PASS
- **Total: 28 PASS, 1 CONDITIONAL, 0 FAIL**
- Test evidence recorded in `docs/TEST_RESULTS.md` Phase 14 section

### Code Fixes Applied During Phase D (10 defects)
- **PD-01:** 4 new service routes.py had relative imports → fixed with sys.path + absolute imports in all 4
- **PD-02:** `sop_11_bid_package/__init__.py` imported non-existent `SOP11Templates` → added class
- **PD-03:** `validate_inputs` re-transitioning to INPUTS_MISSING when already there → added status guard
- **PD-04:** No `start_work` endpoint for SOP 11 → added method + POST /11/instances/{id}/start-work
- **PD-05:** `run_ai_review` re-transitioning to AI_DRAFTED when already there → added status guard
- **PD-06:** `hand_off_to_sop15` used relative import in method body → changed to absolute import
- **PD-07:** Claude API returns markdown-fenced JSON; json.loads failed → added `parse_json_response()` to BaseIntelligenceService
- **PD-08:** `run_ai_leveling` tried READY_TO_START→AI_DRAFTED directly (invalid) → auto-advance through IN_PROGRESS
- **PD-09:** `run_ai_leveling` re-transitioning to AI_DRAFTED when already there → added status guard
- **PD-10:** `log_bid` no auto-transition to INPUTS_MISSING when < MIN_RESPONSIVE_BIDS → added bidcount logic

### Files Modified
- `03_Source_Code/services/decision_intelligence/routes.py` — import fix
- `03_Source_Code/services/kpi_intelligence/routes.py` — import fix
- `03_Source_Code/services/operating_rules/routes.py` — import fix
- `03_Source_Code/services/business_process_library/routes.py` — import fix
- `03_Source_Code/services/sop_execution/sop_11_bid_package/sop_11_templates.py` — added SOP11Templates class
- `03_Source_Code/services/sop_execution/sop_11_bid_package/sop_11_service.py` — validate_inputs guard, start_work, run_ai_review guard, handoff import fix
- `03_Source_Code/services/sop_execution/sop_11_bid_package/sop_11_agent.py` — parse_json_response
- `03_Source_Code/services/sop_execution/sop_15_bid_leveling/sop_15_service.py` — log_bid status logic, run_ai_leveling IN_PROGRESS auto-advance and AI_DRAFTED guard
- `03_Source_Code/services/sop_execution/sop_15_bid_leveling/sop_15_agent.py` — parse_json_response
- `03_Source_Code/api/routers/sop.py` — added start-work endpoint
- `03_Source_Code/services/base.py` — added parse_json_response() static method
- `docs/TEST_RESULTS.md` — Phase 14 section added
- `docs/BOOK01_IMPLEMENTATION_STATUS.md` — Phase D → COMPLETE
- `docs/SOP_CONVERSION_INVENTORY.md` — SOP 11 + 15 → ✅ PHASE D TESTED
- `AI_TEAM/00_STATUS.md` — Phase 14e added
- `AI_TEAM/08_CHANGELOG.md` — this entry

---

## 2026-06-25 — Phase 14: SOP Execution Layer + BOOK_01 + Intelligence Services

**Directives:** HCI_AI_SOP_to_Software_Execution_Layer_Master_Directive_v1.0 | HCI_AI_Business_Operating_Layer_BOOK01_Decision_KPI_Master_Directive_v1.0

### BOOK_01 — HCI Construction Operating Manual (COMPLETE)
- Created all 19 files: README + volumes 00-18
- Covers: executive overview, operating principles, all 11 project phases, decision/KPI/rules/process intelligence, reporting cadence, UAT, continuous improvement

### SOP Execution Layer — Phase A+B Documentation (COMPLETE)
- `BOOK_00/18_SOP_TO_SOFTWARE_EXECUTION_LAYER.md` — BOOK_00 volume 18 (framework)
- `docs/SOP_CONVERSION_INVENTORY.md` — all 42 SOPs indexed
- `docs/SOP_2_0_CONVERSION_STANDARD.md` — 4-layer conversion standard
- `docs/SOP_WORKFLOW_STATUS_MATRIX.md` — 15 statuses + valid transitions
- `docs/SOP_DATA_FIELD_DICTIONARY.md` — all fields for SOP 11 + 15
- `docs/SOP_APPROVAL_GATE_REGISTER.md` — all gates for SOP 11 + 15
- `docs/SOP_STOP_CONDITION_REGISTER.md` — all 7 universal stop conditions
- `docs/SOP_AI_AGENT_SCRIPT_LIBRARY.md` — Layer 3 scripts (SOP 11 + 15)
- `docs/SOP_EMPLOYEE_SCRIPT_LIBRARY.md` — Layer 2 scripts (SOP 11 + 15)
- `docs/SOP_TEMPLATE_BACKLOG.md` — Layer 4 templates (SOP 11 + 15)
- `docs/SOP_TEST_MATRIX.md` — test scenarios (SOP 11 + 15)
- `docs/SOP_DASHBOARD_REQUIREMENTS.md` — dashboard views and API endpoints
- `docs/PRECONSTRUCTION_CHAIN_IMPLEMENTATION_PLAN.md` — full chain plan (SOP 01-16)

### SOP Execution Layer — Phase C Pilot Build (COMPLETE)
- `services/sop_execution/shared/` — base_sop, sop_data_model, approval_engine, stop_condition, sop_kpi
- `services/sop_execution/sop_11_bid_package/` — service, agent, templates (all 4 layers)
- `services/sop_execution/sop_15_bid_leveling/` — service, agent, templates (all 4 layers)
- `05_Database/sop_execution_schema.sql` — 10 tables + seed operating rules
- `api/routers/sop.py` — full API router registered in main.py

### Business Operating Layer Standards (COMPLETE)
- `docs/DECISION_INTELLIGENCE_STANDARD.md`
- `docs/KPI_EXECUTIVE_INTELLIGENCE_STANDARD.md`
- `docs/OPERATING_RULES_ENGINE_STANDARD.md`
- `docs/BUSINESS_PROCESS_LIBRARY.md`
- `docs/BOOK01_IMPLEMENTATION_STATUS.md`

### New Intelligence Services (COMPLETE)
- `services/decision_intelligence/` — create, search, outcome tracking; Qdrant embedded
- `services/kpi_intelligence/` — project + company KPI snapshots; traffic lights
- `services/operating_rules/` — configurable rule engine; evaluate/update/exception
- `services/business_process_library/` — process registry; maturity tracking
- All 4 services registered in `api/main.py`

### Next: Phase D (Test — SOP 11 + 15 test scenarios) | Gate 5 Pilot running through 2026-07-01

---

## 2026-06-25 — Phase 13b: Gate 3 Workflow Acceptance Testing Complete

**Gate 3 PASSED.** All 18 workflows and 9 intelligence services formally tested with documented evidence.

### Test Results
- 16/18 workflows: PASS
- 1/18: FAIL — WF-SYNC-HOUZZ (KI-001 P2, Houzz anti-bot, non-blocking)
- 1/18: SKIP — WF-007 n8n external (KI-002, deferred to UAT)
- 9/9 intelligence services: PASS (vendor-intelligence partial — KI-003 P2)
- All infrastructure: PASS

### Fixes applied during Gate 3
- WF-001 payload field names corrected in test (name/address, not project_name)
- WF-002 payload field names corrected (project_id/title/notes)
- Test projects (id=5,7) cleaned from DB; workflow_events test entries purged
- Confirmed projects table has no project_number column (project lookup uses name pattern matching)

### Gate status after Phase 13b
- Gate 1: ✅ PASSED | Gate 2: ✅ PASSED | Gate 3: ✅ PASSED | Gate 4: ⬜ READY | Gate 5: ⬜ Blocked

**Next:** Buck runs `docs/UAT_PLAN.md` (5 Tier 1 scenarios, ~45 min).

---

## 2026-06-25 — Phase 13: QA Framework and Validation Gates

**Directive:** HCI_AI_QA_Testing_and_No_Go_Live_Master_Directive_v1.0

### Governance Change
- Production go-live is now BLOCKED until 5 validation gates pass + Buck Adams explicitly approves
- System mode changed to VALIDATION-FIRST
- All components assigned honest production status (most are "Built - Untested")

### New Documents Created (12)
- `BOOK_00/17_QUALITY_ASSURANCE_AND_VALIDATION.md` — 19-section master QA volume
- `docs/QA_VALIDATION_STANDARD.md` — operational quick-reference
- `docs/TEST_PLAN.md` — 7 test categories, 9 scenarios, all Gate 1-3 test cases
- `docs/TEST_RESULTS.md` — evidence log template for Gates 1-3
- `docs/WORKFLOW_TEST_MATRIX.md` — all 18 workflows + 9 services + infrastructure
- `docs/KNOWN_ISSUES.md` — 10 open (KI-001 to KI-010); 6 resolved; no P0/P1 open
- `docs/UAT_PLAN.md` — 10 UAT scenarios for Buck with exact commands
- `docs/UAT_RESULTS.md` — UAT evidence log with Buck's sign-off section
- `docs/ROLLBACK_PLAN.md` — 7 rollback scenarios with recovery commands
- `docs/PILOT_READINESS_REPORT.md` — 5-day pilot log + go-live authorization form
- `docs/REGRESSION_TEST_PLAN.md` — 3 regression levels with trigger criteria
- `docs/SYSTEM_DATA_FLOW.md` — 9 major data flows documented end-to-end

### AI_TEAM Updated (6 files)
- 00_STATUS.md, 02_ACTIVE_WORK.md, 05_BACKLOG.md, 06_NEXT_SESSION.md, 07_BLOCKERS.md, 08_CHANGELOG.md

### Production Status Assessment
- Validated in Test: WF-SYNC-HS, WF-SYNC-DRIVE, WF-SUPER, WF-PM, WF-REPORT-DAILY, WF-REPORT-EXEC, project-brain, bid-intelligence, schedule-intelligence, risk-intelligence
- Failed Validation: WF-SYNC-HOUZZ (KI-001 — Houzz anti-bot)
- Built - Untested: 11 remaining workflows + vendor-intelligence + document-intelligence
- No P0 or P1 defects open

---

## 2026-06-25 — Phase 12: Master Validation and Gap Audit

### Bugs Fixed
- Hardcoded DB password `hci_postgres_2026` in 7 files → all now use `POSTGRES_PASSWORD` env var: wf001, wf002, wf003, wf005, sync_hubspot, sync_houzz, sync_drive
- WF-003 `BUCK_EMAIL` hardcoded to @hendricksoninc.com → now reads `BUCK_EMAIL` env var (defaults to @ahmaspen.com)
- `hci_project_documents` Qdrant collection missing → created; also created hci_sops, hci_historical_costs, hci_procurement, hci_vendor_intelligence

### Schema
- `infrastructure/postgres/init.sql` updated: added 8 Phase 8-9 tables (long_lead_items, procurement_items, risks, historical_cost_records, workflow_events, schedule_variance, rfis, submittals) + 9 daily_logs ALTER COLUMN statements
- `05_Database/postgres/schema.sql` synced from init.sql (was Phase 1 only)
- `houzz_projects`, `houzz_daily_logs`, `houzz_schedule_items` created in live DB (were missing despite being in init.sql)

### Deliverables Created (docs/)
- `docs/MASTER_VALIDATION_REPORT.md` — system-wide health report
- `docs/GAP_REGISTER.md` — 13 gaps, 4 fixed in audit, 9 open and prioritized
- `docs/IMPLEMENTATION_RISK_REGISTER.md` — 8 risks, 3 mitigated
- `docs/DEPENDENCY_MAP.md` — service-to-DB, service-to-Qdrant, workflow-to-workflow matrices
- `docs/WORKFLOW_TRACEABILITY_MATRIX.md` — all 18 workflows, event flows, Project Brain integration
- `docs/PRODUCTION_READINESS_CHECKLIST.md` — go/no-go per section; verdict: GO with known gaps

### AI_TEAM Updated
- 00_STATUS.md — full Phase 1-12 status, corrected Qdrant vector counts
- 06_NEXT_SESSION.md — data enrichment priorities replacing Phase 8 tasks
- 07_BLOCKERS.md — 4 current blockers, 5 resolved

### Production Verdict
- **System: 80% production-ready. GO for active use.**
- Primary remaining work: populate Qdrant (drive_memory, vendor_memory), begin real daily log submissions, add WF-PM launchd schedule.

---

## 2026-06-25 — Phase 11: Production Hardening

### Added
- `03_Source_Code/scripts/backup.sh` — Postgres pg_dump (custom format) + Qdrant snapshot API + MinIO manifest; 7-day rotation; primary `/Volumes/HCI_AI_DEV/backups`, fallback `~/HCI_Backups`
- `03_Source_Code/scripts/monitor.sh` — 5-min health check, 3-attempt auto-restart, Docker container status, disk usage threshold, email alert via Graph API
- `~/Library/LaunchAgents/com.hci.backup.plist` — daily 02:00 AM backup; loaded
- `~/Library/LaunchAgents/com.hci.monitor.plist` — every 5 minutes; loaded and running
- `Desktop/HCI_Backup.command` — double-click manual backup trigger
- `infrastructure/setup_mac_mini.sh` — 14-step Mac mini M4 Pro migration playbook: Homebrew, Python, Docker, repo transfer, schema migration, Qdrant restore, Postgres restore, all launchd agents, smoke test

### Updated
- `.env` — added `HCI_API_KEYS`, `BUCK_EMAIL`, `HCI_BACKUP_DIR`
- `api/static/dashboard/index.html` — added `API_KEY` + `HEADERS` constants; all 6 fetch calls send `X-API-Key` header

### Auth Status
- Middleware enforces `X-API-Key` on `/api/v1/*` when `HCI_API_KEYS` is set
- Legacy routes (`/workflows/`, `/health`, `/projects`) bypass auth — morning brief unaffected
- API key: `hci-01253a2b0f87dbd03346bba60f0c31d7350e5c75b17c866c`
- Dashboard and docs/redoc remain open (not behind /api/v1)

### Mac mini Migration (pending hardware)
- Run: `bash infrastructure/setup_mac_mini.sh` — resumes from any step with `--step N`
- Steps 1–3: requires manual Docker Desktop install
- Step 4: requires repo transfer (USB / rsync / git clone)
- Steps 7–9: automatically applies schema and restores from latest backup

---

## 2026-06-25 — Phase 10: Reporting and Dashboards

### Added
- `wf_report.py` — 5 report generators: daily_field_report, schedule_variance_alert, executive_health_report, owner_summary, weekly_pm_email; all support send=True/False
- `03_Source_Code/api/static/dashboard/index.html` — 18KB vanilla JS dashboard; project selector, health cards, bid coverage bar, daily logs, schedule variance, open risks, Project Brain Q&A
- `/dashboard` redirect + StaticFiles mount in FastAPI main.py
- `GET /api/v1/workflows/wf-pm/status/{project}` — returns latest PM review from workflow_events
- 5 new WF-REPORT-* endpoints in workflows router
- Workflow registry: 18 active, 0 planned (was 13 active, 1 planned)

### Updated
- `wf_superintendent.py` — added Stage 8 (schedule_variance_alert on high/critical) + Stage 9 (daily_field_report auto-send after log save)
- `wf_pm.py` — weekly_report() accepts send_email=True to deliver via wf_report.weekly_pm_email()
- `main.py` — list_services() schedule-intelligence → active; StaticFiles mount; /dashboard route
- `wf_pm_weekly_report` router endpoint — accepts ?send_email=true

### Tested
- `/dashboard` serves at localhost:8000/dashboard — all sections load, Q&A works
- daily_field_report(2) preview — 2.5KB HTML, all sections populated
- executive_health_report() preview — 4 projects, 3.3KB HTML
- owner_summary(64EW) preview — clean output, 6% bid coverage shown

---

## 2026-06-25 — Phase 9: Field and PM Workflows

### Added
- `wf_superintendent.py` — WF-SUPER 7-stage pipeline; absorbs WF-004
- `wf_pm.py` — daily_review() + weekly_report() + HTML render helper
- `wf004_daily_log.py` — converted to thin wrapper calling WF-SUPER
- `rfis` table (project_id, rfi_number, subject, question, status, source_email_id + indexes)
- `submittals` table (project_id, submittal_number, spec_section, description, status, source_email_id + indexes)
- `schedule_variance` table (project_id, daily_log_id, activity_name, risk_level, cause, decision_needed, etc.)
- 9 new columns on `daily_logs`: manpower, deliveries, inspections, quality_notes, safety_notes, subcontractor_progress, constraints, lookahead, field_risks

### Updated
- `schedule_intelligence_svc.py` — added analyze_log() (Claude Haiku schedule analysis), recent_variance(), STATUS→active
- `schedule_intelligence/routes.py` — added POST /analyze/{log_id}, GET /variance/{project_number}
- `wf006_inbox_review.py` — bid detection (BID_KEYWORDS + dollar extraction + vendor match), RFI detection, submittal detection; writes to bid_entries/rfis/submittals
- `workflows.py` router — WF-SUPER + WF-PM endpoints; registry updated (13 active, 1 planned)
- `base.py` — added pg_execute() and pg_execute_returning() to BaseIntelligenceService

### Tested
- WF-SUPER: full 7-stage pipeline on 64EW — log saved, embedded, schedule analyzed, risks written, cache invalidated
- WF-PM daily review: 64EW — health=green, 3 action items, Claude synthesis working
- analyze_log: crane delay scenario → medium risk → schedule_variance row written
- Workflow registry: 13 active, 1 planned (WF-REPORT)

---

## 2026-06-25 — Phase 8: Workflow Engine Core

### Completed
- **vendor_id FK** — 19/26 bid_entries matched via token scoring + manual SQL; 7 unresolvable (vendors not in DB)
- **Document ingest wired** — `ingest_document()` → `ingest.py` 6-stage pipeline; fixed `project_number` column bug in `_stage_register()`; added `POST /upload` multipart endpoint
- **workflow_events table** — created with indexes; confirmed writes on trigger call
- **Workflow Registry** — `GET /api/v1/workflows` (14 workflows) + `POST /api/v1/workflows/{id}/trigger`; dispatches to handlers; writes triggered/completed/error events to Postgres

---

## 2026-06-25 — Workflow Consolidation and BOOK_00 v2

### Added
- `docs/WORKFLOW_INVENTORY.md` — complete inventory of 14 workflows (built, planned, spec-only)
- `docs/WORKFLOW_OVERLAP_REVIEW.md` — 6 critical overlaps identified and resolved
- `docs/IMPLEMENTATION_SEQUENCE.md` — phased build plan with dependency graph (Phases 8-11)
- `BOOK_00/` — rebuilt as 17-section master specification (§00 Executive Overview through §16 Appendix)
- Schema migrations: `long_lead_items`, `procurement_items`, `risks`, `historical_cost_records` tables
- `BaseIntelligenceService.resolve_project_id()` — project code → DB id via numeric prefix match

### Fixed (Service Layer)
- Python sys.modules naming collision — renamed `service.py` → `{name}_svc.py` in 8 services
- `svc.include_router(x.router)` → `svc.include_router(x)` (double-dereference on already-extracted router)
- `meetings.notes` → `meetings.summary` (actual column name)
- `hubspot_deals` JOIN: `hd.project_id = p.id` → `hd.hubspot_deal_id = p.hubspot_deal_id`
- `project_number` column references (doesn't exist) → replaced with `resolve_project_id()` in all 4 affected services
- Historical cost service: removed stale "table not yet created" note; query now joins `historical_cost_records`

### Status changes
- Procurement service: partial → active
- Historical Cost service: partial → active
- Risk Intelligence service: partial → active

---

## 2026-06-25 — Construction Intelligence Service Layer v1

### Added
- 9 Construction Intelligence Services under `/api/v1/services/`
- `BaseIntelligenceService` base class (`services/base.py`) with `pg_query`, `pg_one`, `resolve_project_id`, `cache_get/set`, `search`, `ask_claude`
- `resolve_project_id()` helper — converts short project codes (e.g. "64EW") to `projects.id` via numeric prefix ILIKE matching
- **Project Brain** (ACTIVE) — full per-project snapshot, Claude Q&A with multi-collection Qdrant search, 30-min cache
- **Bid Intelligence** (ACTIVE) — package summaries, bid leveling analysis, bid_memory search
- **Vendor Intelligence** (ACTIVE) — 860-vendor roster, performance history, vendor_memory search
- **Document Intelligence** (ACTIVE) — dual-collection document search, classifier, ingest trigger
- **Lessons Learned** (ACTIVE) — CRUD + Qdrant search
- **Procurement** (partial) — graceful fallback when UUID schema tables absent
- **Historical Cost** (partial) — bid vs. actual with awarded bid pull
- **Schedule Intelligence** (partial) — Houzz schedule items + daily log progress
- **Risk Intelligence** (partial) — derives 35 risk flags from bid coverage gaps

### Fixed
- Renamed all `service.py` files to `{service_name}_svc.py` to prevent Python `sys.modules` naming collision when 9 services share the same filename in separate dirs
- Fixed `svc.include_router(x.router, ...)` → `svc.include_router(x, ...)` (double-deref on already-extracted router)
- Fixed `meetings.notes` → `meetings.summary` (actual column name)
- Fixed `hubspot_deals` join: `hd.project_id = p.id` → `hd.hubspot_deal_id = p.hubspot_deal_id`
- Fixed `projects.project_number` references (column doesn't exist) — replaced with `resolve_project_id()` pattern across all services
- Fixed `hubspot_notes` join chain through `hubspot_deals` using correct FK columns

### Docs
- `docs/CONSTRUCTION_INTELLIGENCE_SERVICE_LAYER_v1.md`
- `AI_TEAM/00_STATUS.md` updated to reflect 6 directives complete


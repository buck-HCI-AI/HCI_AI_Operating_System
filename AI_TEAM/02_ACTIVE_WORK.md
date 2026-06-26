# 02_ACTIVE_WORK.md
**What is being implemented right now**
Last updated: 2026-06-26 (MVP Sprint 1 COMPLETE — Gate 5 pilot active)

---

## CURRENT FOCUS: Gate 5 Pilot — System Live, AI Team Connected

**MCP Server:** LIVE ✅ — 26 tools at port 8080 / ngrok `/mcp` endpoint  
**AI Team connected:** GBT via MCP Connector + Claude.ai via Settings → Integrations  
**Full System Audit:** COMPLETE — 6 deliverables in `HCI_AI_Audit_20260626/`  
**HubSpot deal IDs:** Linked ✅ (64EW / 101F / 1355R — see 00_STATUS.md)

---

## PRIOR FOCUS: Bid Leveling Service + Gate 5 Pilot

**Bid Leveling Service:** COMPLETE ✅ (22/22 tests PASS)
- `services/bid_leveling/` registered at `/api/v1/services/bid-leveling/`
- Reads bid tracking sheets from all 3 projects: 86 bids / 17 divisions (1355R), 23 bids / 14 divs (64EW), 5 bids / 11 divs (101F)
- Generates per-division bid leveling Excel (.xlsx) files matching 101 Francis format
- Manages `{Project} 00_Bids/##_Division/` folder structure in Drive
- GBT/AI agent endpoints: Drive create-folder, upload-file, list; Sheets read, write
- All Drive writes go through approval queue (dry_run=True default)

---

## Gate 5 — Pilot (2026-06-25 to 2026-07-01)

**Directive:** HCI_AI_MVP_Sprint_1_Daily_Operations_and_Background_Learning_Directive_for_Claude_Code_v1.pdf  
**Status:** MVP code COMPLETE ✅ | Pilot active on 3 projects | Go-live authorization pending  

Pilot projects: 64 Eastwood, 101 Francis, 1355 Riverside  
All 6 daily operation workflows live and tested (48/48 PASS).

---

## MVP Sprint 1 — COMPLETE ✅ (2026-06-26)

### Built This Session

| Component | File | Status |
|-----------|------|--------|
| MVP Ops Router | `api/routers/mvp_ops.py` | ✅ 6 workflows + 3 utility endpoints |
| Background Learning Service | `services/background_learning/` | ✅ 13-status pipeline, 3 source connectors |
| Approval Queue Service | `services/approval_queue/` | ✅ Enqueue/approve/reject/execute/audit |
| Connector Registry Service | `services/connector_registry/` | ✅ 9 pilot connectors, all read_only |
| MVP Sprint 1 DB Schema | `database/mvp_sprint_1_schema.sql` | ✅ 4 tables, applied to live DB |
| Test Suite | `tests/test_mvp_sprint_1.py` | ✅ 48/48 PASS |
| 14 docs files | `docs/MVP_SPRINT_1_*.md` + workflow docs | ✅ Complete |
| BOOK_00/19 | `BOOK_00/19_MVP_SPRINT_1_DAILY_OPERATIONS.md` | ✅ |
| BOOK_01/19 | `BOOK_01/19_DAILY_OPERATIONS_USING_HCI_AI.md` | ✅ |
| AI_TEAM updates | `00_STATUS, 02, 05, 06, 07, 08` | ✅ |

### Test Coverage

| Group | Tests | Result |
|-------|-------|--------|
| MS-01: Project Brain Init | 4 | ✅ PASS |
| MS-02: Bid Management | 4 | ✅ PASS |
| MS-03: Daily Log / Field Intel | 5 | ✅ PASS |
| MS-04: PM Weekly Review | 3 | ✅ PASS |
| MS-05: Schedule/Status Intel | 3 | ✅ PASS |
| MS-06: Executive Reporting | 4 | ✅ PASS |
| BL-01: Background Learning | 8 | ✅ PASS |
| AQ-01: Approval Queue | 5 | ✅ PASS |
| CR-01: Connector Registry | 3 | ✅ PASS |
| ROI-01: ROI Log | 3 | ✅ PASS |
| SP-01: Sprint Status | 3 | ✅ PASS |
| SC-01: Safety Controls | 3 | ✅ PASS |
| **Total** | **48** | **✅ 48 PASS / 0 FAIL** |

---

## Next: Gate 5 Completion (by 2026-07-01)

- Buck uses the 6 workflows on the 3 pilot projects daily
- Review any approval queue items that need Buck's decision
- At end of pilot: Buck provides explicit go-live authorization
- After authorization: flip connectors from read_only to write mode (one at a time, per approval)

---

## Prior Phases Complete

### Phase 15 ✅ — Platform Integration Layer (2026-06-26)
- 5 platform capabilities: Identity, Event Bus, Notifications, Audit Trail, Unified Search
- 33 endpoints, 39/39 tests pass

### Phase 14i ✅ — SOP Field Execution (SOP 17–30)
- 14 SOPs for field execution (Schedule through Inspection)
- 189 total SOP endpoints at `/api/v1/sop/`

### Phases 1-14h ✅ — Complete
See `AI_TEAM/08_CHANGELOG.md` for full history.

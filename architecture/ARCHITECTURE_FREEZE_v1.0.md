# Architecture Freeze v1.0
## HCI AI Operating System — Foundation Declaration

**Declared:** 2026-06-28
**Declared by:** Buck Adams (PM & Superintendent, Hendrickson Construction, Inc.; Owner, HCI-AI)
**Ratified by:** GBT (Chief Architect) — via handoff directive + audit completion
**Implemented by:** Claude Code (Lead Implementation Engineer)
**Status:** 🔒 FROZEN

---

## Declaration

The HCI AI Operating System foundation is hereby declared **frozen at v1.0**.

This declaration means:
- The core architecture documented below is **locked** — no structural changes without a formal Architecture Change Request (ACR) reviewed by GBT and approved by Buck
- New features are built **on top of** this foundation, not by changing it
- Sprint 3 and beyond proceed within this architecture envelope

---

## What Is Frozen

### Services (18 total — FastAPI, localhost:8000)
| Service | Endpoints | Status |
|---|---|---|
| project_intelligence | ~15 | 🔒 Frozen |
| vendor_intelligence | ~20 | 🔒 Frozen |
| bid_intelligence | ~25 | 🔒 Frozen |
| bid_leveling | ~30 | 🔒 Frozen |
| approval_queue | ~10 | 🔒 Frozen |
| executive_reporting | ~10 | 🔒 Frozen |
| project_brain | ~20 | 🔒 Frozen |
| schedule_intelligence | ~15 | 🔒 Frozen |
| houzz_intelligence | ~3 | 🔒 Frozen |
| hubspot_integration | ~40 | 🔒 Frozen |
| historical_cost | ~10 | 🔒 Frozen |
| lessons_learned | ~8 | 🔒 Frozen |
| business_process_library | ~8 | 🔒 Frozen |
| sop_library | ~12 | 🔒 Frozen |
| background_learning | ~12 | 🔒 Frozen |
| decision_intelligence | ~8 | 🔒 Frozen |
| drive_intelligence | ~10 | 🔒 Frozen |
| system_auditor | ~5 | 🔒 Frozen |

**Total: 427 endpoints**

### GBT Gateway Bridge (v1.0)
| Endpoint | Purpose |
|---|---|
| GET /gateway/health | Live check |
| GET /gateway/project-state | Full system state |
| GET /gateway/executive/report | Morning brief (live DB) |
| GET /gateway/executive/mission-control | All KPIs |
| GET /gateway/project/{code}/brain | Project snapshot |
| GET /gateway/project/{code}/schedule | Schedule + variance |
| GET /gateway/project/{code}/pm | PM console |
| GET /gateway/project/{code}/bids | Bid packages |
| GET /gateway/knowledge/vendor | Vendor lookup |
| GET /gateway/knowledge/issues | Lessons learned search |
| GET /gateway/drive/search | Drive search |
| POST /gateway/drive/write | Write to Drive |
| POST /gateway/agent/handoff | Send task to Claude Code |
| POST /gateway/admin/process-inbox | Trigger handoff processor |

### Database (PostgreSQL — hci_os, 47 tables)
Schema frozen. New tables require ACR. Existing tables:
- `projects`, `project_schedule_items` (995 records), `bid_packages` (119)
- `schedule_variance`, `risks`, `daily_logs`
- `vendors` (392), `hubspot_companies` (1,183)
- `business_processes` (27), `sop_library`, `sop_approval_gates`
- `gateway_request_log`, `approval_queue_items`
- All 47 tables as of 2026-06-28

### n8n Workflows (40 active of 49)
All 40 active workflows frozen. New workflows require Buck approval before activation.
Key frozen workflows: WF-007 Bid Leveling, WF-008 Bid Follow-Up, WF-009 Schedule, WF-011 Daily Log, AUTO-SS-MORNING, AUTO-PM, AUTO-HANDOFF-PROCESSOR.

### SOP Coverage (v1.0 baseline)
Per SOP_WORKFLOW_COMPLIANCE_MAP.md (2026-06-28):
- ✅ 6 fully automated (22%): BP-08, 14, 15, 23, 24, 25
- ⚠️ 10 partial (37%): BP-06, 07, 11, 12, 13, 16, 17, 18, 21, 22
- ❌ 11 none (41%): BP-04, 05, 09, 10, 19, 20, 26, 27, 28, 29, 30

### Agent Infrastructure
- GBT ↔ Claude Code Handoff Protocol v1.0 (AI_TEAM/GBT_CLAUDE_HANDOFF_PROTOCOL.md)
- Agent Handoff Bus: Architecture/Agent_Handoff/ (Inbox → Processed)
- AUTO-HANDOFF-PROCESSOR: active, every 5 minutes
- LIVE_PROJECT_STATE.md: public Drive link, GBT browse fallback
- Custom GPT Actions schema: HCI_AI_CustomGPT_Schema.json v2.0

---

## Freeze Criteria Met

| Criterion | Status | Evidence |
|---|---|---|
| GBT ↔ Claude Code handoff pipeline live | ✅ | 8 handoffs processed, processor active |
| SOP compliance map complete | ✅ | AI_TEAM/SOP_WORKFLOW_COMPLIANCE_MAP.md |
| WF-009 data integrity audit passed | ✅ | AI_TEAM/WF009_DATA_INTEGRITY_AUDIT.md |
| Pilot reporting consistency audit passed | ✅ | AI_TEAM/PILOT_REPORTING_CONSISTENCY_AUDIT.md |
| Executive report pulls live DB data | ✅ | Fixed 2026-06-28, 101F correctly YELLOW |
| Gateway Bridge live and tested | ✅ | ngrok confirmed, GBT connected |
| Drive write path operational | ✅ | POST /gateway/drive/write confirmed |
| Known risks filed to DB | ✅ | 4 risks re-filed, 64EW/101F both YELLOW |
| Gate 5 pilot data loaded | ✅ | 995 schedule items, 3 projects |

---

## Documented Exceptions (Carried Forward to Sprint 3)

| # | Exception | Impact | Sprint 3 Plan |
|---|---|---|---|
| E-001 | kpi_snapshots table empty — no KPI history | Historical trending unavailable | Populate on each schedule_variance write |
| E-002 | variance_days sign convention undocumented | Potential confusion in future analysis | Document: negative = behind, positive = ahead |
| E-003 | AUTO-CONTINUOUS-DISCOVERY inactive | HubSpot hourly sync paused | Buck to authorize reactivation |
| E-004 | 1355R has 0 daily logs | No field data for schedule analysis | Superintendent to begin daily log submissions |
| E-005 | COI expiration dates null for all 1,183 companies | COI engine runs but writes nothing | Data entry / COI data source needed |
| E-006 | 83 Sagebrusch has no HubSpot deal ID | Project not fully initialized | Buck to confirm or exclude |

---

## What This Enables (Sprint 3+)

With the foundation frozen, the OS can now be built out without structural risk:

1. **Mobile Command Center** — GBT's handoff: approval flow accessible from phone
2. **BP-17 Schedule Automation** — n8n loop for weekly schedule variance
3. **BP-06 Risk Auto-Filing** — wire schedule variance → risk log automatically
4. **Houzz Schedule Push** — export project_schedule_items to Houzz CSV format
5. **COI Data Pipeline** — populate coi_expiration_date for 1,183 companies
6. **kpi_snapshots Population** — historical health trending

---

## Change Control (Post-Freeze)

Any structural change to the frozen architecture requires:

1. **GBT files an ACR** (Architecture Change Request) via `POST /gateway/agent/handoff` with `document_type: architecture_change_request`
2. **Claude Code reviews** feasibility and implementation path
3. **Buck approves** before any implementation begins
4. **CHANGELOG updated** with the ACR number and change

Changes that do NOT require an ACR (operational changes):
- Adding new n8n workflow nodes within existing workflow patterns
- New API endpoints that follow existing service patterns
- Data additions (new records, not new tables)
- Bug fixes within existing behavior

---

## Signature

**Buck Adams** — PM & Superintendent, Hendrickson Construction, Inc.; Owner, HCI-AI
**Date:** 2026-06-28
**Gate 5 Pilot Status:** Active through 2026-07-01

*Architecture Freeze v1.0 declared. The foundation is locked. Build on it.*

# HCI AI Operating System — Current Status

**Last Updated:** 2026-06-26 (MCP Server LIVE — 26 tools, ngrok endpoint, GBT+Claude.ai connected; Full System Audit complete; HubSpot deal IDs linked; SOP+HistCost MCP paths fixed)  
**Mode: GATE 5 PILOT — Daily operations active on 3 pilot projects; all writes approval-controlled**  
**API:** http://localhost:8000 (live, launchd-managed, API key enforced)  
**Dashboard:** http://localhost:8000/dashboard  
**Docs:** http://localhost:8000/docs  
**API Key:** hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6

---

## Production Go-Live Status

| Gate | Description | Status |
|------|-------------|--------|
| Gate 1 | Engineering Validation | ✅ PASSED 2026-06-25 |
| Gate 2 | Integration Testing | ✅ PASSED 2026-06-25 |
| Gate 3 | Workflow Acceptance Testing | ✅ PASSED 2026-06-25 |
| Gate 4 | User Acceptance Testing (Buck) | ✅ PASSED 2026-06-25 |
| Gate 5 | Pilot Approval + Buck Sign-Off | 🔄 IN PROGRESS — 2026-06-25 to 2026-07-01; 3 pilot projects active |

**Go-Live verdict: BLOCKED.** See `docs/QA_VALIDATION_STANDARD.md` and `BOOK_00/17_QUALITY_ASSURANCE_AND_VALIDATION.md`.

---

## Infrastructure

| Component | Status | Notes |
|-----------|--------|-------|
| PostgreSQL (hci_os) | ✅ Running | 22 tables, 4 projects, 392 vendors, 306 HubSpot deals |
| Redis | ✅ Running | Project Brain cache active |
| Qdrant | ⚠️ Running | API healthy; docker ps shows "unhealthy" label (cosmetic) |
| MinIO | ✅ Running | hci-raw-documents bucket; 4 app buckets |
| FastAPI | ✅ Running | Port 8000, launchd, X-API-Key enforced |
| ngrok tunnel | ✅ Running | Webhook relay + MCP external access |
| MCP Server (26 tools) | ✅ Running | Port 8080, proxied at :8000/mcp, ngrok at speculate-armband-retinal.ngrok-free.dev/mcp |
| Backup | ✅ Active | Daily 2 AM, 7-day rotation |
| Monitor | ✅ Active | 5-min health check, auto-restart, alert email |
| Mac mini | ⏳ Pending | M4 Pro arriving ~2026-09-17; playbook at infrastructure/setup_mac_mini.sh |

---

## API Layer — /api/v1 (auth-enforced)

| Router | Status |
|--------|--------|
| /projects, /vendors, /bids | ✅ Active |
| /documents, /storage, /search | ✅ Active |
| /system, /auth, /ai | ✅ Active |
| /ingest, /memory, /workflows | ✅ Active |
| /sop/* (27 SOPs, 189 endpoints) | ✅ Active |
| /platform/* (5 capabilities, 33 endpoints) | ✅ Active |
| /mvp/* (6 workflows, 3 pilot projects) | ✅ Active — MVP Sprint 1 |

---

## MVP Operations — /api/v1/mvp (MVP Sprint 1)

| Service | Status | Notes |
|---------|--------|-------|
| Project Brain Init | ✅ ACTIVE | All 3 pilot projects; 28 min/run saved |
| Bid Management | ✅ ACTIVE | Dry-run + approval queue; 42 min/bid saved |
| Daily Log + Field Intelligence | ✅ ACTIVE | Delay/safety/risk detection; 27 min/log saved |
| PM Weekly Review | ✅ ACTIVE | Health: green/yellow/red synthesis; 87 min/week saved |
| Schedule/Status Intelligence | ✅ ACTIVE | Variance detection, decision points; 28 min/run saved |
| Executive Reporting | ✅ ACTIVE | Cross-project morning briefing; 59 min/run saved |
| Background Learning | ✅ ACTIVE | Read-only discovery: Drive, HubSpot, Houzz |
| Approval Queue | ✅ ACTIVE | All writes held pending Buck approval |
| Connector Registry | ✅ ACTIVE | 9 connectors (3 projects × 3 sources), all read_only |
| **Bid Leveling Service** | ✅ ACTIVE | Reads bid sheets, generates per-division Excel, Drive folder management, GBT/AI read-write endpoints; 22/22 tests |

---

## Construction Intelligence Services — /api/v1/services

| Service | Status | Notes |
|---------|--------|-------|
| project-brain | ✅ ACTIVE | Claude Q&A + snapshot; cache 30 min |
| bid-intelligence | ✅ ACTIVE | 119 packages, leveling analysis |
| vendor-intelligence | ✅ ACTIVE | 392 vendors; Qdrant search needs embed run |
| document-intelligence | ✅ ACTIVE | Upload → MinIO + Qdrant (collections now exist) |
| lessons-learned | ✅ ACTIVE | CRUD + search |
| procurement | ✅ ACTIVE | Tables live; 0 rows — needs field data |
| historical-cost | ✅ ACTIVE | Tables live; 0 rows — needs historical data |
| schedule-intelligence | ✅ ACTIVE | analyze_log() + variance table; no Houzz baseline |
| risk-intelligence | ✅ ACTIVE | 35+ risk flags; open risks table live |
| decision-intelligence | ✅ ACTIVE | Decision records + Qdrant search; outcome tracking |
| kpi-intelligence | ✅ ACTIVE | Project + company KPI snapshots; traffic light alerts |
| operating-rules | ✅ ACTIVE | Configurable policy engine; 11 seed rules loaded |
| business-process-library | ✅ ACTIVE | Process registry with maturity tracking |
| **bid-leveling** | ✅ ACTIVE | Bid leveling workflow + Drive/Sheets read-write for GBT/AI agents |

**SOP Execution Layer:** 27 SOPs active — full preconstruction + contract execution + field execution chain. Phase D tested (SOP 11+15; 29 tests: 28 PASS, 1 CONDITIONAL). Phase E–G (SOP 04–16, 19) + Phase H (SOP 17–18, 20–30) COMPLETE. 189 total endpoints at `/api/v1/sop/`. Full chain: Plan Review → Narrative → Risk Log → ROM → Historical Cost → Budget Review → Allowances → Bid Package → Sub CRM → Distribution → Follow-Up → Leveling → Buyout → Subcontract Agreement → Schedule → Long-Lead → Contract Setup → Compliance → COI/W-9 → Startup → [Dashboard / Daily Log / Field Coord / QC / QC Detail / Safety / Inspection].

---

## SOP Execution Layer

| Component | Status |
|-----------|--------|
| Shared base layer (base_sop, data_model, approval_engine, stop_condition, sop_kpi) | ✅ 2026-06-25 |
| SOP 11 — Bid Package (service + agent + templates) | ✅ 2026-06-25 |
| SOP 15 — Bid Leveling (service + agent + templates) | ✅ 2026-06-25 |
| SOP 04 — Plan Review | ✅ 2026-06-25 — Phase F |
| SOP 05 — Construction Narrative | ✅ 2026-06-25 — Phase F |
| SOP 06 — Missing Information / Risk Log | ✅ 2026-06-25 — Phase F |
| SOP 07 — ROM Budget (Gate 07-C) | ✅ 2026-06-25 — Phase F |
| SOP 08 — Historical Cost Database | ✅ 2026-06-25 — Phase F |
| SOP 09 — Budget Review (Gate 09-C) | ✅ 2026-06-25 — Phase F |
| SOP 10 — Allowances / Alternates / Exclusions | ✅ 2026-06-25 — Phase E |
| SOP 13 — Bid Distribution | ✅ 2026-06-25 — Phase E |
| SOP 14 — Bid Follow-Up | ✅ 2026-06-25 — Phase E |
| SOP 16 — Buyout | ✅ 2026-06-25 — Phase E |
| SOP 12 — Subcontractor CRM (Gate: MIN_BIDDERS=3) | ✅ 2026-06-25 — Phase G |
| SOP 19 — Subcontract Agreement (Gate 19-C) | ✅ 2026-06-25 — Phase G |
| SOP 17 — Project Schedule | ✅ 2026-06-26 — Phase H |
| SOP 18 — Long-Lead Procurement | ✅ 2026-06-26 — Phase H |
| SOP 20 — Contract Setup | ✅ 2026-06-26 — Phase H |
| SOP 21 — Compliance (clear-to-build gate) | ✅ 2026-06-26 — Phase H |
| SOP 22 — COI / W-9 / Lien (HCI insurance minimums enforced) | ✅ 2026-06-26 — Phase H |
| SOP 23 — Project Startup (ready-to-build gate) | ✅ 2026-06-26 — Phase H |
| SOP 24 — Superintendent Daily Dashboard | ✅ 2026-06-26 — Phase H |
| SOP 25 — Daily Log (AI risk analysis; PM alerts) | ✅ 2026-06-26 — Phase H |
| SOP 26 — Field Coordination (AI RFI drafts) | ✅ 2026-06-26 — Phase H |
| SOP 27 — Quality Control (SC-03 on CRITICAL fail) | ✅ 2026-06-26 — Phase H |
| SOP 28 — QC Detail Card (hold points) | ✅ 2026-06-26 — Phase H |
| SOP 29 — Safety (SC-03 on uncontrolled CRITICAL) | ✅ 2026-06-26 — Phase H |
| SOP 30 — Inspection (SC-03 on FAIL) | ✅ 2026-06-26 — Phase H |
| SOP execution DB schema (10 tables, 12 seed rules) | ✅ 2026-06-25 (applied to live DB) |
| SOP API router `/api/v1/sop/` | ✅ 2026-06-26 (189 endpoints: SOP 04–30) |
| Phase D — Test (SOP 11 + 15) | ✅ 2026-06-25 (29 tests: 28 PASS, 1 CONDITIONAL) |
| Phase E — Chain Expansion (SOP 10, 13, 14, 16) | ✅ 2026-06-25 (built + smoke-tested) |
| Phase F — Backfill (SOP 04–09) | ✅ 2026-06-25 (built + smoke-tested) |
| Phase G — Close Loop (SOP 12, 19) | ✅ 2026-06-25 (built + smoke-tested) |
| Phase H — Field Execution (SOP 17–18, 20–30) | ✅ 2026-06-26 (built + smoke-tested) |

**To activate SOP schema:** `docker exec -i hci_postgres psql -U hci -d hci_brain < 05_Database/sop_execution_schema.sql`

---

## BOOK_01 — HCI Operating Manual

| Status | Count |
|--------|-------|
| ✅ Complete (all 19 volumes) | 19/19 |

BOOK_01 is complete: `BOOK_01/README.md` + volumes `00` through `18`.

---

## Workflow Engine — 18 Active Workflows

| Category | Workflows | Status |
|----------|-----------|--------|
| Operations | WF-001 New Project, WF-002 Meeting, WF-005 Lessons | ✅ |
| Field | WF-SUPER Superintendent, WF-004 (legacy wrapper) | ✅ |
| Inbox | WF-006 Inbox Review (bids + RFIs + submittals) | ✅ |
| Reporting | WF-003 Morning Brief, WF-PM, WF-PM-W, WF-REPORT-* (5) | ✅ |
| Sync | WF-SYNC-HS, WF-SYNC-DRIVE, WF-SYNC-HOUZZ | ✅ (Houzz tables created 2026-06-25) |
| Bid Leveling | WF-007 (n8n) | ✅ |

---

## Phases Complete

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Infrastructure (Postgres, Redis, MinIO, Qdrant, Docker) | ✅ |
| 2 | Integrations (HubSpot, Drive, Outlook, Graph API) | ✅ |
| 3-7 | Intelligence Service Layer (9 services) | ✅ |
| 8 | Workflow Engine Core | ✅ |
| 9 | Field + PM Workflows | ✅ |
| 10 | Reporting + Dashboard | ✅ |
| 11 | Production Hardening (auth, backup, monitor) | ✅ |
| 12 | Master Validation + Gap Audit | ✅ |
| 13a | Gate 3 Workflow Acceptance Testing | ✅ PASSED 2026-06-25 |
| 13b | Gate 4 UAT + Gate 5 Pilot Launch | ✅ PASSED / ⬜ Pilot Running |
| 14a | BOOK_01 HCI Operating Manual (19 volumes) | ✅ 2026-06-25 |
| 14b | SOP Execution Layer — Phase A+B (docs) | ✅ 2026-06-25 |
| 14c | SOP Execution Layer — Phase C (SOP 11 + 15 code) | ✅ 2026-06-25 |
| 14d | Decision/KPI/Rules/BPL services | ✅ 2026-06-25 |
| 14e | Phase D — SOP 11 + 15 testing (29 tests) | ✅ 2026-06-25 |
| 14f | Phase E — SOP 10, 13, 14, 16 (chain expansion) | ✅ 2026-06-25 |
| 14g | Phase F — SOP 04–09 (backfill) | ✅ 2026-06-25 |
| 14h | Phase G — SOP 12 + SOP 19 (close loop) | ✅ 2026-06-25 |
| 14i | Phase H — SOP 17–18 + 20–30 (field execution) | ✅ 2026-06-26 |
| 15 | Platform Integration Layer (Identity/Events/Notifs/Audit/Search) | ✅ 2026-06-26 |
| 16 | MVP Sprint 1 — Daily Operations, Background Learning & Approval Controls | ✅ 2026-06-26 |

---

## Open Gaps (from Full System Audit 2026-06-26)

See `HCI_AI_Audit_20260626/` for full audit deliverables (6 files).

| Priority | Gap | Status |
|----------|-----|--------|
| P0 | Duplicate Bid Receipt Processing v5 in n8n | OPEN — Buck deactivate duplicate in n8n UI |
| P0 | 83 Sagebrusch (project id=4) — no HubSpot deal found | OPEN — confirm project details |
| P0 | TMP-cl-84994d n8n workflow — unfinished webhook | OPEN — Buck deactivate in n8n UI |
| P0 | ChatGPT Chrome Bridge n8n workflow — old OpenAI webhook | OPEN — Buck retire in n8n UI |
| P0 | HubSpot deal IDs for pilot projects | ✅ Fixed 2026-06-26 (64EW: 331240861419, 101F: 321401932527, 1355R: 321351275210) |
| P0 | SOP MCP tool path wrong | ✅ Fixed 2026-06-26 → /api/v1/sop/registry |
| P0 | HistoricalCost MCP tool path wrong | ✅ Fixed 2026-06-26 → /search not /lookup |
| P1 | Registry Workbook duplicate (2 copies) | OPEN — keep 03 Registries copy, archive Buck AI copy |
| P1 | Lessons Learned — 0 rows in DB | P1 backlog — mine from handoff PDFs |
| P1 | Business Process Library — 0 rows | P1 backlog — populate from SOPs |
| P1 | Historical Cost Database — 0 rows | P1 backlog — mine from Drive |
| P1 | N8N_API_KEY not in .env | OPEN — Buck set in n8n Settings > API |
| P1 | Qdrant docker ps "unhealthy" label | OPEN — cosmetic, functionally serving |
| P1 | vendor_memory + drive_memory Qdrant empty | Re-run Drive sync; build vendor embed |
| P2 | WF-001/002/005/006 don't log workflow_events | Add event writes |
| P2 | No launchd for WF-PM daily / exec health report | Add 2 plists |

See `HCI_AI_Audit_20260626/HCI_AI_Completion_Backlog_v1.csv` for full 30-item backlog.

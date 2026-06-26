# HCI AI Implementation Sequence
**Last Updated:** 2026-06-26  
**Rule:** Do not build a layer before its dependencies are stable.

---

## Current Position: End of SOP Execution + Platform Integration Layer

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | AI_TEAM + repository collaboration layer | ✅ Complete |
| 2 | Infrastructure: PostgreSQL, Redis, MinIO, Qdrant | ✅ Complete |
| 3 | Storage: HCI_AI_DEV drive + launchd watcher | ✅ Complete |
| 4 | Data architecture + document metadata model | ✅ Complete |
| 5 | Knowledge ingestion + document intelligence | ✅ Partial (pipeline built; not fully wired) |
| 6 | API Layer v1 | ✅ Complete |
| 7 | Construction Intelligence Service Layer | ✅ Complete (13 active services) |
| SOP | SOP Execution Layer: SOPs 04–30 (27 SOPs) | ✅ Complete (189 endpoints; test suite 49+71+39 PASS) |
| PIl | Platform Integration Layer: Identity, Events, Notifications, Audit, Search | ✅ Complete (2026-06-26) |
| 8 | Workflow Engine core | 🔜 Next |
| 9 | PM, Superintendent, Daily Log, Schedule, Bid, Procurement, RFI workflows | 🔜 After 8 |
| 10 | Reporting and Dashboards | 🔜 After 9 |
| 11 | Production hardening + Mac mini migration | 🔜 After 10 |

---

## Phase 8 — Workflow Engine Core

**Prerequisite:** All Phase 2-7 items complete. ✅  
**Goal:** Establish a shared workflow execution pattern that all future workflows follow. No more disconnected Python scripts.

### 8.1 — Fix Vendor FK Gap (Before Building New Workflows)
**Why first:** Every workflow that touches bids needs `vendor_id` populated on `bid_entries`. Zero rows currently have it.
- Add vendor name matching in `sync_hubspot.py` during bid_entries upsert
- Match `company_name` in `bid_entry.notes` text to `vendors.company_name`
- Test: `SELECT vendor_id FROM bid_entries WHERE vendor_id IS NOT NULL` should return > 0

### 8.2 — Wire Document Intelligence Ingestion
**Why:** Document ingestion is called by multiple future workflows. Must be end-to-end before they depend on it.
- Connect `document_intelligence_svc.ingest_document()` → `ingest.py` pipeline
- Test: `POST /api/v1/services/document-intelligence/ingest` with a real PDF → returns Qdrant vector ID

### 8.3 — Workflow Event Log Table
**Why:** Workflows need to record what they did for reporting and auditing.
```sql
CREATE TABLE workflow_events (
    id SERIAL PRIMARY KEY,
    workflow_id TEXT NOT NULL,          -- 'wf003', 'wf-super', etc.
    project_id INTEGER REFERENCES projects(id),
    event_type TEXT NOT NULL,           -- 'triggered', 'completed', 'failed', 'data_written'
    payload JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);
```

### 8.4 — Workflow Registry Endpoint
- `GET /api/v1/workflows` → list all workflows with status, last_run, next_run
- `POST /api/v1/workflows/{id}/trigger` → manual trigger for any workflow
- Reads from workflow_events for last_run

---

## Phase 9 — Field and PM Workflows

**Prerequisite:** Phase 8.1-8.4 complete.

### 9.1 — Superintendent Workflow (WF-SUPER)
**Absorbs:** WF-004 Daily Log  
**Build order:**
1. Extend `daily_logs` table: add `manpower`, `deliveries`, `inspections`, `quality_notes`, `safety_notes`, `lookahead`, `field_risks`, `photos` (jsonb array)
2. Build `wf_superintendent.py` — replaces `wf004_daily_log.py`
3. API: `POST /api/v1/workflows/wf-super/daily-log`
4. On save: auto-trigger Schedule Intelligence analysis
5. On save: update Project Brain cache (invalidate + rebuild)
6. Test: submit a daily log → appears in Project Brain snapshot → schedule variance detected if applicable

### 9.2 — Schedule Intelligence Tie-In (WF-SCHED)
**Prerequisite:** 9.1 producing daily log data  
**Build:**
1. `schedule_intelligence_svc.analyze_log(daily_log_id)` — compare log to scheduled activities
2. If variance detected → write to new `schedule_variance` table
3. Generate status-change report (affected activity, baseline, current, variance, cause, responsible party, recovery)
4. Push alert to Morning Brief

### 9.3 — Project Manager Workflow (WF-PM)
**Build order:**
1. `wf_pm.py` — daily PM checklist runner
2. Calls: Project Brain snapshot, Bid Intelligence summary, Procurement status, Risk Intelligence, Schedule variance
3. Produces: PM daily digest (HTML), weekly report (Friday trigger)
4. API: `POST /api/v1/workflows/wf-pm/daily-review/{project_number}`
5. Outputs feed Reporting Framework

### 9.4 — Bid Email → Postgres Pipeline
**Prerequisite:** WF-006 inbox review working  
**Build:**
- Enhance WF-006 to detect bid emails → extract vendor, amount, package → write to `bid_entries` with `vendor_id` FK
- Retire Google Sheets as bid data source for WF-007
- Wire WF-007 to read from `bid_entries` via Bid Intelligence Service

### 9.5 — RFI / Submittal Workflow (WF-RFI) *(lower priority)*
- Classify incoming emails as RFI or submittal
- Create new `rfis` and `submittals` tables
- Track open/closed, response due dates
- Feed Risk Intelligence

---

## Phase 10 — Reporting and Dashboards

**Prerequisite:** Phase 9 workflows producing data.

### 10.1 — Reporting Framework
- Report types: Daily Field, Weekly PM, Schedule Variance, Procurement Risk, Executive Health, Owner Summary
- All reports pull from Project Brain + workflow_events + Postgres
- Delivery: email (Outlook), MinIO storage (PDF), API endpoint

### 10.2 — Dashboard (read-only web UI)
- Single-page: project selector → Project Brain summary → active bids → risks → schedule
- Reads from `/api/v1/services/project-brain/{project}` — no new backend needed
- Tech: simple HTML + JS, served by FastAPI static files

---

## Phase 11 — Production Hardening

- Mac mini migration (always-on server)
- 4 TB storage upgrade path (HCI_AI_DEV → permanent NAS)
- API key authentication enabled for all external callers
- Automated daily backup of Postgres + Qdrant to MinIO
- ngrok → custom domain
- Monitoring + alerting (disk, memory, API latency)

---

## Dependency Graph

```
Phase 2 (infra) ──────────────────────────────────────────┐
Phase 3 (storage) ────────────────────────────────────────┤
Phase 4 (schema) ─────────────────────────────────────────┤
Phase 5 (ingestion) ──────────────────────────────────────┤
Phase 6 (API) ────────────────────────────────────────────┤
Phase 7 (intelligence services) ──────────────────────────┤
                                                           ↓
                                              Phase 8 (workflow engine)
                                                           ↓
                                    Phase 9a (WF-SUPER) ──┐
                                    Phase 9b (WF-SCHED) ──┤ (sequential)
                                    Phase 9c (WF-PM)    ──┤
                                    Phase 9d (bid pipe) ──┘
                                                           ↓
                                         Phase 10 (reporting + dashboards)
                                                           ↓
                                         Phase 11 (production hardening)
```

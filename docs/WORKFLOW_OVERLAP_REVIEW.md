# Workflow Overlap and Duplication Review
**Last Updated:** 2026-06-25

---

## Critical Overlaps — Must Resolve Before Building More

### OVERLAP-01: WF-004 Daily Log ↔ Superintendent Workflow

**Problem:** WF-004 (`wf004_daily_log.py`) captures daily field logs but has no schedule tie-in, no photo pathway, and no mobile input. The Superintendent Workflow (not yet built) requires all of this plus manpower tracking, inspections, quality observations, and look-ahead planning. Building the Superintendent Workflow as a separate module while WF-004 exists creates two parallel daily log systems.

**Resolution:** Deprecate WF-004 as a standalone. Absorb its Postgres write + vector logic into the Superintendent Workflow. WF-004 API endpoint stays as an alias for backward compatibility but calls the Superintendent service internally.

**Action:** When building WF-SUPER, do not create a new `daily_logs` table structure — extend the existing one with new columns as needed.

---

### OVERLAP-02: WF-007 Bid Leveling (n8n/Sheets) ↔ Bid Intelligence Service

**Problem:** WF-007 reads bid data from Google Sheets and generates leveling reports. The Bid Intelligence Service reads from `bid_entries` in Postgres. These are two separate bid data stores for the same bids. WF-007 is live and Buck uses it; Bid Intelligence Service is ready but has no data because bids aren't flowing into Postgres.

**Resolution:** 
1. Establish Postgres `bid_entries` as the single source of truth.
2. Migrate WF-007 to read from `POST /api/v1/services/bid-intelligence/leveling` instead of Google Sheets.
3. Build bid email → `bid_entries` auto-ingestion via WF-006 inbox review.
4. Keep WF-007 n8n workflow as the report generator; change its data source.

**Action:** Wire WF-006 to extract bid amounts from bid emails and write to `bid_entries` with correct `vendor_id` FK. WF-007 then reads Postgres, not Sheets.

---

### OVERLAP-03: Document Ingestion (WORKFLOW_01) ↔ Document Intelligence Service

**Problem:** `workflows/WORKFLOW_01_DOCUMENT_INGESTION.md` defines a full ingestion pipeline. `03_Source_Code/ingestion/` has partial implementation. The Document Intelligence Service has a `/ingest` endpoint that is a stub. Three different entry points for the same operation.

**Resolution:** The Document Intelligence Service endpoint (`POST /api/v1/services/document-intelligence/ingest`) is the canonical trigger. It calls the ingestion pipeline from `03_Source_Code/ingestion/ingest.py`. WORKFLOW_01 spec is superseded by BOOK_00 Section 05.

**Action:** Wire `document_intelligence_svc.ingest_document()` to call `ingest.py` end-to-end. Remove the stub.

---

### OVERLAP-04: Architecture Documentation in Three Places

**Problem:** Architecture docs exist in:
- `BOOK_00/architecture/CURRENT_ARCHITECTURE.md`
- `AI_TEAM/04_ARCHITECTURE.md`
- `architecture/DATA_ARCHITECTURE.md` + `DOCUMENT_INTELLIGENCE_ARCHITECTURE.md`

All are partially outdated (pre-API v1, pre-services layer).

**Resolution:** `AI_TEAM/04_ARCHITECTURE.md` is the live engineering state for Claude Code sessions. `BOOK_00/` sections are the canonical specification. The `architecture/` root folder and `BOOK_00/architecture/` subfolder are retired — content folded into BOOK_00 sections.

**Action:** Update `AI_TEAM/04_ARCHITECTURE.md` to current state. BOOK_00 sections 02-07 become the architecture spec. Do not write new architecture docs outside these two locations.

---

### OVERLAP-05: Reporting — Morning Brief ↔ Reporting Framework

**Problem:** WF-003 Morning Brief sends a daily email with project status. The Reporting Framework (planned) will generate daily field reports, weekly PM reports, schedule variance reports, and owner summaries. Without a clear boundary, these become duplicate report generators.

**Resolution:** Morning Brief = daily operational digest for Buck (internal, 7 AM, lightweight). Reporting Framework = structured project reports for PMs, Sups, and owners (triggered by workflow events, data-driven). They share data sources but serve different audiences and triggers.

**Action:** Do not merge them. Enhance Morning Brief to pull from Project Brain snapshots. Build Reporting Framework as a separate service after PM and Superintendent workflows produce data.

---

### OVERLAP-06: Workflow Specs in Two Locations

**Problem:** `workflows/` (root) has markdown specs (WORKFLOW_01, WORKFLOW_02). `BOOK_00/workflows/` has WORKFLOW_00_AI_COLLABORATION_LAYER.md. These are scattered.

**Resolution:** All workflow specs live in BOOK_00 Sections 08-12. The `workflows/` root folder and `BOOK_00/workflows/` subfolder are retired as spec locations. Code stays in `03_Source_Code/workflows/`.

---

## Minor Overlaps — Monitor

| Overlap | Description | Resolution |
|---------|-------------|------------|
| Schedule Intelligence Service ↔ WF-SCHED | Service queries data; workflow analyzes and alerts | Service = data access; Workflow = analysis + event generation |
| Risk Intelligence ↔ WF-004 field risks | Risk derives from bid coverage; field risks come from daily logs | Add field_risk column to daily_logs; Risk Intelligence aggregates both |
| Vendor Intelligence ↔ WF-007 vendor data | Both track vendor performance | Postgres is truth; both read from it |
| WF-005 Lessons ↔ Project Brain | Lessons feed Brain context | Already wired via Qdrant collection |

---

## What NOT to Build (Prevents New Duplication)

1. Do not build a new storage or ingestion module inside PM or Super workflows — use Document Intelligence Service.
2. Do not add report generation to individual workflows — use the Reporting Framework.
3. Do not add a prompt library to each workflow — shared prompts live in `BaseIntelligenceService.ask_claude()`.
4. Do not create new Qdrant collections per workflow — use existing collections with metadata filters.
5. Do not read from Google Sheets in any new workflow — Postgres is the truth store.

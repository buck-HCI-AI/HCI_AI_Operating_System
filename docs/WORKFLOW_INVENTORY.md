# HCI AI Workflow Inventory
**Last Updated:** 2026-06-25  
**Source of Truth:** This file. PDFs are release artifacts.

---

## Summary Counts

| Category | Count |
|----------|-------|
| Live workflows (running) | 3 (WF-003, WF-006, WF-007) |
| Built, not scheduled | 4 (WF-001, WF-002, WF-004, WF-005) |
| Spec only | 2 (WORKFLOW_01, WORKFLOW_02) |
| Planned / not started | 5 (WF-008, PM, Super, Schedule, Reporting) |

---

## WF-001 — New Project Setup

| Field | Value |
|-------|-------|
| **Status** | Built — not scheduled |
| **Location** | `03_Source_Code/workflows/wf001_new_project.py` |
| **API Endpoint** | `POST /api/v1/workflows/wf001/new-project` |
| **Related Directive** | Infrastructure Phase 1 |
| **Purpose** | Bootstrap all project infrastructure when a new deal is created |
| **Inputs** | project_name, address, scope, hubspot_deal_id |
| **Outputs** | PostgreSQL project row, Qdrant project collection, Drive folder created, HubSpot deal updated |
| **Related Services** | Project Brain, Document Intelligence |
| **Data Dependencies** | projects table, hubspot_deals |
| **API Dependencies** | HubSpot API, Google Drive API |
| **Storage Dependencies** | MinIO project bucket |
| **Schedule** | Manual / webhook trigger on new HubSpot deal |
| **Implementation State** | Python complete; not wired to automatic HubSpot trigger |
| **Gaps** | No automatic trigger from HubSpot deal creation; no Drive folder template copy |
| **Risks** | Running manually means new projects may be missed |
| **Overlap** | None — unique workflow |
| **Next Action** | Wire to HubSpot deal webhook; test with 83 Sagebrusch project |

---

## WF-002 — Meeting Intelligence

| Field | Value |
|-------|-------|
| **Status** | Built — not scheduled |
| **Location** | `03_Source_Code/workflows/wf002_meeting_intelligence.py` |
| **API Endpoint** | `POST /api/v1/workflows/wf002/meeting` |
| **Related Directive** | Infrastructure Phase 1 |
| **Purpose** | Ingest meeting transcripts, summarize, extract action items, store in Postgres + Qdrant |
| **Inputs** | transcript text or file, project_id, meeting_type, date |
| **Outputs** | meetings table row, Qdrant project_memory vector, action item extraction |
| **Related Services** | Project Brain, Document Intelligence, Knowledge Ingestion |
| **Data Dependencies** | meetings table, projects table |
| **API Dependencies** | Anthropic (Claude Haiku for summarization) |
| **Storage Dependencies** | MinIO (transcript file storage) |
| **Schedule** | Manual / on-demand |
| **Implementation State** | Python complete; no Postgres rows exist yet (0 meetings in DB) |
| **Gaps** | No transcript input pathway from real meetings; no auto-vectorization after save |
| **Risks** | Manual-only means meeting intelligence won't accumulate |
| **Overlap** | Overlaps with Superintendent Workflow field coordination notes |
| **Next Action** | Add Teams/Zoom transcript ingestion path; test end-to-end |

---

## WF-003 — Morning Brief

| Field | Value |
|-------|-------|
| **Status** | **LIVE — runs daily at 7 AM** |
| **Location** | `03_Source_Code/workflows/wf003_morning_brief.py` |
| **API Endpoint** | `POST /api/v1/workflows/wf003/morning-brief`, `GET /preview` |
| **Schedule** | launchd: `com.hci.morning-brief.plist` — 7 AM daily |
| **Related Directive** | Infrastructure Phase 1 |
| **Purpose** | Generate and email daily HTML brief: weather, project status, bid activity, inbox summary, HubSpot tasks |
| **Inputs** | Postgres projects/bids, Qdrant search, HubSpot tasks, Outlook unread count |
| **Outputs** | HTML email sent to buck@ahmaspen.com |
| **Related Services** | Project Brain (future: pull snapshots), Bid Intelligence |
| **Data Dependencies** | projects, bid_packages, bid_entries, hubspot_tasks |
| **API Dependencies** | Microsoft Graph (send email), HubSpot (tasks), Anthropic (synthesis) |
| **Storage Dependencies** | None |
| **Gaps** | Does not yet pull Project Brain snapshots; no schedule intelligence integration |
| **Overlap** | Reporting Framework (Section 13) will supersede portions of this |
| **Next Action** | Integrate Project Brain snapshots per project; add schedule variance alerts |

---

## WF-004 — Daily Log

| Field | Value |
|-------|-------|
| **Status** | Built — not scheduled |
| **Location** | `03_Source_Code/workflows/wf004_daily_log.py` |
| **API Endpoint** | `POST /api/v1/workflows/wf004/daily-log` |
| **Related Directive** | Infrastructure Phase 1 |
| **Purpose** | Accept field daily log input, store in Postgres, vectorize, flag schedule variance |
| **Inputs** | project_id, date, weather, crew, work_performed, issues, photos_count |
| **Outputs** | daily_logs table row, Qdrant project_memory vector |
| **Related Services** | Schedule Intelligence, Project Brain, Risk Intelligence |
| **Data Dependencies** | daily_logs table, projects table |
| **API Dependencies** | None (local) |
| **Storage Dependencies** | MinIO (photo storage — planned) |
| **Schedule** | Manual input; Superintendent fills out |
| **Implementation State** | Python complete; 0 rows in daily_logs — never used in production |
| **Gaps** | No schedule tie-in analysis; no photo upload pathway; no mobile input form |
| **Risks** | Without daily logs, Schedule Intelligence and Project Brain have no field data |
| **Overlap** | **CRITICAL OVERLAP** with Superintendent Workflow (same data source); must be merged |
| **Next Action** | Merge into Superintendent Workflow; add schedule analysis on save (see WF-SUPER) |

---

## WF-005 — Lessons Learned

| Field | Value |
|-------|-------|
| **Status** | Built — not scheduled |
| **Location** | `03_Source_Code/workflows/wf005_lessons_learned.py` |
| **API Endpoint** | `POST /api/v1/workflows/wf005/lesson`, `GET /api/v1/services/lessons-learned/lessons` |
| **Related Directive** | Infrastructure Phase 1 |
| **Purpose** | Capture lessons learned from projects, store + embed for future retrieval |
| **Inputs** | title, description, category, csi_division, project_id, outcome, future_recommendation |
| **Outputs** | lessons_learned table row, Qdrant lessons_learned vector |
| **Related Services** | Lessons Learned Intelligence Service, Project Brain |
| **Data Dependencies** | lessons_learned table |
| **API Dependencies** | None (local) |
| **Storage Dependencies** | None |
| **Implementation State** | Complete; 1 row in DB |
| **Gaps** | No automatic trigger (e.g., on project close); no retrieval at bid time |
| **Risks** | Low — works correctly, just underused |
| **Overlap** | Minor overlap with Risk Intelligence derived insights |
| **Next Action** | Add to PM Workflow post-project close checklist |

---

## WF-006 — Inbox Review

| Field | Value |
|-------|-------|
| **Status** | **LIVE — runs daily after morning brief** |
| **Location** | `03_Source_Code/workflows/wf006_inbox_review.py` |
| **API Endpoint** | `POST /api/v1/workflows/wf006/inbox-review` |
| **Schedule** | launchd via `run_morning_brief.sh` |
| **Related Directive** | Infrastructure Phase 1 |
| **Purpose** | Read Outlook inbox, classify emails by project, move to project folders, draft responses |
| **Inputs** | Outlook Graph API — unread inbox messages |
| **Outputs** | Emails moved to project subfolders; draft responses created |
| **Related Services** | Document Intelligence (classify), Project Brain |
| **Data Dependencies** | projects table (for folder matching) |
| **API Dependencies** | Microsoft Graph (read/move/draft), Anthropic (classify + draft) |
| **Storage Dependencies** | None |
| **Gaps** | Bid email extraction not connected to bid_entries; no RFI/submittal detection |
| **Overlap** | Partially overlaps with Document Ingestion (WORKFLOW_01) for attachments |
| **Next Action** | Wire bid emails → bid_entries via LLM extraction; add RFI/submittal classification |

---

## WF-007 — Bid Leveling Engine (n8n)

| Field | Value |
|-------|-------|
| **Status** | **LIVE — n8n, daily at 5 PM + on-demand webhook** |
| **Location** | `04_Workflows/WF-007_Bid_Leveling_Engine.json` |
| **API Endpoint** | n8n webhook: `POST http://localhost:5678/webhook/bid-leveling` |
| **Related Directive** | Phase 0 (pre-infrastructure) |
| **Purpose** | Load bid data from Google Sheets, build HTML leveling report, export to Drive, draft email |
| **Inputs** | project_name (optional), Google Sheets bid tracker |
| **Outputs** | HTML bid leveling report, updated BT xlsx to Drive, Outlook draft |
| **Related Services** | Bid Intelligence Service (parallel implementation) |
| **Data Dependencies** | Google Sheets (not Postgres) |
| **API Dependencies** | Google Sheets, Google Drive, Outlook via n8n |
| **Storage Dependencies** | Google Drive |
| **Gaps** | Uses Google Sheets as truth store — not connected to Postgres bid_entries |
| **Overlap** | **CRITICAL OVERLAP** with Bid Intelligence Service at `/api/v1/services/bid-intelligence` |
| **Next Action** | Migrate WF-007 to read from Postgres bid_entries; retire Google Sheets as source |

---

## WORKFLOW_01 — Document Ingestion

| Field | Value |
|-------|-------|
| **Status** | Spec only — partially implemented |
| **Location** | `workflows/WORKFLOW_01_DOCUMENT_INGESTION.md` (spec), `03_Source_Code/ingestion/` (partial impl) |
| **Purpose** | Full document lifecycle: receive → classify → extract → embed → register → store |
| **Inputs** | File path or binary stream, source_system |
| **Outputs** | MinIO object, Postgres document record, Qdrant vectors |
| **Related Services** | Document Intelligence, Knowledge Ingestion Engine |
| **Implementation State** | `ingest.py`, `classifier.py`, `extractor.py` exist but not wired to API trigger |
| **Overlap** | Overlaps with Document Intelligence Service (`/api/v1/services/document-intelligence/ingest`) |
| **Next Action** | Wire `POST /document-intelligence/ingest` to call ingestion pipeline end-to-end |

---

## WORKFLOW_02 — Registry Writeback (Sync)

| Field | Value |
|-------|-------|
| **Status** | Partially implemented — sync scripts exist |
| **Location** | `workflows/WORKFLOW_02_REGISTRY_WRITEBACK.md` (spec), `03_Source_Code/workflows/sync_*.py` |
| **Purpose** | One-way sync: HubSpot/Drive/Houzz → PostgreSQL |
| **Inputs** | HubSpot API, Google Drive, Houzz Pro |
| **Outputs** | Updated vendors, projects, hubspot_deals, hubspot_notes in Postgres |
| **Related Services** | All Intelligence Services (consume synced data) |
| **API Endpoints** | `POST /api/v1/workflows/sync/hubspot`, `/sync/drive`, `/sync/houzz` |
| **Implementation State** | sync_hubspot.py, sync_drive.py, sync_houzz.py exist; run at startup |
| **Gaps** | vendor_id FK not populated on bid_entries during sync |
| **Next Action** | Add vendor_id matching on bid_entries during HubSpot sync |

---

## WF-PM — Project Manager Workflow *(PLANNED)*

| Field | Value |
|-------|-------|
| **Status** | Not built |
| **Purpose** | Daily project controls: status, budget, procurement, RFIs, change orders, owner comms, risk, schedule |
| **Inputs** | Project Brain snapshot, bid data, procurement items, risks, schedule |
| **Outputs** | PM daily checklist, weekly report, Project Brain update, owner summary |
| **Related Services** | Project Brain, Bid Intelligence, Procurement, Risk Intelligence, Schedule Intelligence |
| **Next Action** | Design in BOOK_00 Section 10 before building |

---

## WF-SUPER — Superintendent Workflow *(PLANNED)*

| Field | Value |
|-------|-------|
| **Status** | Not built — WF-004 Daily Log is the predecessor |
| **Purpose** | Field execution: daily logs, photos, manpower, deliveries, inspections, quality, safety, lookahead |
| **Inputs** | Field input (mobile form or API), photos, subcontractor progress |
| **Outputs** | daily_logs row, schedule analysis, Project Brain update, field risk flags |
| **Related Services** | Schedule Intelligence, Risk Intelligence, Project Brain, Document Intelligence |
| **Merge Note** | WF-004 Daily Log must be absorbed into this workflow — do not run in parallel |
| **Next Action** | Build as replacement for WF-004; design mobile input form |

---

## WF-SCHED — Schedule Intelligence Workflow *(PLANNED)*

| Field | Value |
|-------|-------|
| **Status** | Not built — Schedule Intelligence Service is the foundation |
| **Purpose** | Analyze daily logs against schedule; detect variance; generate alerts |
| **Inputs** | daily_logs rows, schedule baseline (Houzz or manual), WF-SUPER output |
| **Outputs** | schedule_variance records, status-change reports, Project Brain update |
| **Related Services** | Schedule Intelligence, Risk Intelligence, Project Brain |
| **Next Action** | Requires WF-SUPER to produce daily log data first |

---

## WF-REPORT — Reporting Framework *(PLANNED)*

| Field | Value |
|-------|-------|
| **Status** | Not built |
| **Purpose** | Generate daily field, weekly PM, schedule variance, procurement risk, executive health, owner summary reports |
| **Inputs** | Project Brain, Schedule Intelligence, Workflow events, Postgres |
| **Outputs** | HTML/PDF reports, emails, Outlook drafts |
| **Related Services** | All 9 intelligence services |
| **Overlap** | Morning Brief (WF-003) handles a subset — will be enhanced, not replaced |
| **Next Action** | Design report templates; build after PM and Super workflows produce data |

---

## WF-008 — Vendor Scorecard *(PLANNED)*

| Field | Value |
|-------|-------|
| **Status** | Planned — not started |
| **Purpose** | Monthly vendor performance report: bid win/loss, response rate, quality |
| **Related Services** | Vendor Intelligence, Bid Intelligence |
| **Next Action** | Build after vendor_id FK is populated on bid_entries |

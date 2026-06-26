# HCI AI — Dependency Map
**Date:** 2026-06-25 | **Audit:** Master Validation v1.0

---

## System Dependency Graph

```
External Systems
├── Microsoft Graph API (Outlook, email send)
│   └── integrations/microsoft_graph.py
│       ├── WF-006 inbox_review (read + move + draft)
│       ├── WF-003 morning_brief (send)
│       ├── wf_report.py (all 5 report sends)
│       └── monitor.sh (alert email)
│
├── HubSpot API
│   └── integrations/hubspot.py
│       ├── sync_hubspot.py → hubspot_deals, hubspot_notes, hubspot_tasks
│       ├── WF-001 new_project (create_deal)
│       └── WF-002 meeting (create_task)
│
├── Anthropic API (Claude Haiku claude-haiku-4-5-20251001)
│   └── BaseIntelligenceService.ask_claude()
│       ├── ScheduleIntelligenceService.analyze_log()
│       ├── WF-PM daily_review() synthesis
│       ├── WF-006 draft_reply()
│       └── ProjectBrainService.query()
│
├── Google Drive API
│   └── integrations/google_sheets.py + sync_drive.py
│       └── drive_memory (Qdrant)
│
└── Houzz (web scrape)
    └── sync_houzz.py → houzz_projects, houzz_daily_logs [⚠️ tables missing]

Infrastructure
├── PostgreSQL (hci_os) — port 5432
│   ├── api/services/db.py  ← all Intelligence Services
│   ├── Direct psycopg2    ← all Workflow files
│   └── 22 tables (see Database section)
│
├── Redis — port 6379
│   └── api/services/cache.py ← Project Brain 30-min snapshot cache
│
├── MinIO (hci-raw-documents bucket) — port 9000
│   └── ingestion/ingest.py Stage 3 (store raw files)
│
└── Qdrant — port 6333
    └── api/services/vector.py ← all Intelligence Services
        13 collections (see Qdrant section)

API Layer
└── 03_Source_Code/api/main.py
    ├── /api/v1/workflows/* → routers/workflows.py
    │   └── imports from workflows/ at request time
    ├── /api/v1/services/* → services/*/routes.py
    │   └── extends BaseIntelligenceService (services/base.py)
    ├── /api/v1/ingest/* → ingestion/ingest.py
    └── /static/dashboard/* → served directly
```

---

## Service-to-Database Dependency Matrix

| Service / Workflow | projects | vendors | bid_packages | bid_entries | daily_logs | meetings | risks | schedule_variance | rfis | submittals | hubspot_deals | workflow_events |
|-------------------|----------|---------|-------------|-------------|------------|----------|-------|------------------|------|-----------|--------------|----------------|
| Project Brain | R | R | R | R | R | R | R | R | R | R | R | — |
| Bid Intelligence | R | R | R | R | — | — | — | — | — | — | R | — |
| Schedule Intelligence | R | — | — | — | R | — | — | RW | — | — | — | — |
| Risk Intelligence | R | — | — | R | R | — | R | R | — | — | — | — |
| Procurement | R | R | — | — | — | — | — | — | — | — | — | — |
| Historical Cost | R | — | R | R | — | — | — | — | — | — | — | — |
| Vendor Intelligence | — | R | R | R | — | — | — | — | — | — | — | — |
| Lessons Learned | R | R | — | — | — | — | — | — | — | — | — | — |
| Document Intelligence | R | — | — | — | — | — | — | — | — | — | — | — |
| WF-001 | W | — | — | — | — | — | — | — | — | — | W(HS) | — |
| WF-002 | — | — | — | — | — | W | — | — | — | — | — | — |
| WF-SUPER | R | — | — | — | W | — | W | W | — | — | — | W |
| WF-PM | R | — | — | — | — | — | — | — | — | — | — | W |
| WF-006 | R | R | R | W | — | — | — | — | W | W | — | — |
| WF-003 | R | — | R | R | — | — | — | — | — | — | R | — |
| WF-SYNC-HS | — | — | — | — | — | — | — | — | — | — | W | — |
| WF-SUPER (Stage 4) | — | — | — | — | — | — | — | W | — | — | — | — |

R = Read, W = Write, W(HS) = Write to HubSpot external

---

## Service-to-Qdrant Dependency Matrix

| Service / Workflow | project_memory | bid_memory | vendor_memory | meeting_memory | lessons_learned | drive_memory | hci_project_documents |
|-------------------|---------------|-----------|--------------|---------------|----------------|-------------|----------------------|
| Project Brain (snapshot) | R | R | R | R | R | R | — |
| Project Brain (Q&A) | R | R | R | R | R | R | — |
| Bid Intelligence | — | R | — | — | — | — | — |
| Vendor Intelligence | — | — | R | — | — | — | — |
| Lessons Learned | — | — | — | — | RW | — | — |
| Schedule Intelligence | — | — | — | — | — | R | — |
| WF-001 | W | — | — | — | — | — | — |
| WF-002 | — | — | — | W | — | — | — |
| WF-005 | — | — | — | — | W | — | — |
| WF-SUPER (Stage 3) | W | — | — | — | — | — | — |
| ingest.py | — | — | — | — | — | — | W |
| sync_drive.py | — | — | — | — | — | W | — |

---

## Workflow-to-Workflow Dependencies

| Workflow | Depends On | Called By |
|----------|-----------|----------|
| WF-004 (wrapper) | WF-SUPER | API callers using legacy endpoint |
| WF-SUPER Stage 4 | ScheduleIntelligenceService | — |
| WF-SUPER Stage 8 | wf_report.schedule_variance_alert | — |
| WF-SUPER Stage 9 | wf_report.daily_field_report | — |
| WF-PM | ProjectBrain, BidIntelligence, Procurement, Risk, Schedule | — |
| WF-PM-W | WF-PM.daily_review() × all projects | wf_report.weekly_pm_email |
| WF-REPORT-WEEKLY | WF-PM.weekly_report() | — |
| WF-003 | WF-006 result (optional inbox_result enrichment) | morning brief script |
| Morning brief sequence | WF-SYNC-HOUZZ → WF-SYNC-HS → WF-006 → WF-003 | launchd 7 AM |

---

## Critical Path (End-to-End)

**Daily log → intelligence → email:**
```
Buck/field crew → POST /api/v1/workflows/wf-super/daily-log
  → Stage 2: INSERT daily_logs
  → Stage 3: embed → Qdrant project_memory
  → Stage 4: ScheduleIntelligenceService.analyze_log()
      → Claude Haiku analysis
      → INSERT schedule_variance
      → (if high/critical) INSERT risks
  → Stage 5: INSERT risks (field_risks)
  → Stage 6: DELETE Redis cache keys
  → Stage 7: INSERT workflow_events
  → Stage 8: (if high/critical) wf_report.schedule_variance_alert() → email
  → Stage 9: wf_report.daily_field_report() → email to Buck
```

**Morning intelligence sequence (7 AM):**
```
launchd com.hci.morning-brief
  → sync_houzz.py → Postgres houzz_*
  → sync_hubspot.py → Postgres hubspot_*
  → WF-006 inbox_review → bid_entries / rfis / submittals + email drafts
  → WF-003 morning_brief → email to Buck
```

---

## External API Dependency Risk

| Dependency | Availability | Fallback |
|-----------|-------------|---------|
| Microsoft Graph | High (Microsoft cloud) | Template drafts in WF-006; no fallback for sends |
| Anthropic Claude | High (Anthropic cloud) | Intelligence services degrade to raw data; no AI synthesis |
| HubSpot API | High (HubSpot cloud) | WF-001/002 log to Postgres; HubSpot step skipped on error |
| Google Drive API | Medium (requires OAuth token refresh) | Drive sync skips files that fail |
| Houzz (scrape) | Low (fragile, no API) | System runs without schedule data |

# BOOK_00 § 09 — Standard Workflows

**Status:** WF-001 through WF-007 built or live. See `docs/WORKFLOW_INVENTORY.md` for full detail.

---

## WF-001 — New Project Setup
**Status:** Built, not scheduled  
**Trigger:** Manual or HubSpot deal webhook  
**Code:** `03_Source_Code/workflows/wf001_new_project.py`  
**API:** `POST /api/v1/workflows/wf001/new-project`

Creates all project infrastructure: PostgreSQL project row, Qdrant collection, MinIO bucket prefix, Google Drive folder. Must be the first workflow run when a new deal is awarded.

**Inputs:** project_name, address, scope, hubspot_deal_id  
**Gap:** Not yet wired to HubSpot deal webhook — triggered manually only.

---

## WF-002 — Meeting Intelligence
**Status:** Built, not scheduled  
**Trigger:** Manual submission  
**Code:** `03_Source_Code/workflows/wf002_meeting_intelligence.py`  
**API:** `POST /api/v1/workflows/wf002/meeting`

Ingests meeting transcript (text or file), summarizes via Claude, extracts action items, stores in `meetings` table and Qdrant `project_memory`. Makes all meeting context available to Project Brain.

**Inputs:** transcript, project_id, meeting_type, date, attendees  
**Gap:** No Teams/Zoom transcript integration. Manual only. Zero meetings in DB.

---

## WF-003 — Morning Brief ✅ LIVE
**Status:** Live — 7 AM daily  
**Trigger:** launchd `com.hci.morning-brief.plist`  
**Code:** `03_Source_Code/workflows/wf003_morning_brief.py`  
**API:** `POST /api/v1/workflows/wf003/morning-brief`

Generates and emails an HTML daily brief to buck@ahmaspen.com covering: active projects, recent bid activity, HubSpot task due dates, inbox summary, weather (planned).

**Enhancement (Phase 9):** Pull Project Brain snapshots per project; add schedule variance alerts.

---

## WF-004 — Daily Log
**Status:** Built, not scheduled  
**Trigger:** Manual field input  
**Code:** `03_Source_Code/workflows/wf004_daily_log.py`  
**API:** `POST /api/v1/workflows/wf004/daily-log`

**DEPRECATION PLANNED:** WF-004 will be absorbed into the Superintendent Workflow (WF-SUPER) in Phase 9.1. The API endpoint will remain as an alias. Do not build new features on WF-004 — build them on WF-SUPER.

---

## WF-005 — Lessons Learned
**Status:** Built, not scheduled  
**Trigger:** Manual capture  
**Code:** `03_Source_Code/workflows/wf005_lessons_learned.py`  
**API:** `POST /api/v1/workflows/wf005/lesson`

Captures a lesson, stores in `lessons_learned` table, embeds in Qdrant `lessons_learned` collection. Also accessible via Lessons Learned Intelligence Service.

---

## WF-006 — Inbox Review ✅ LIVE
**Status:** Live — runs after morning brief daily  
**Trigger:** launchd + morning startup sequence  
**Code:** `03_Source_Code/workflows/wf006_inbox_review.py`  
**API:** `POST /api/v1/workflows/wf006/inbox-review`

Reads Outlook inbox via Graph API, classifies each email by project, moves to project subfolder, drafts responses where appropriate. 

**Enhancement (Phase 9.4):** Detect bid submission emails → extract vendor, amount, package → write to `bid_entries` with vendor_id FK.

---

## WF-007 — Bid Leveling Engine ✅ LIVE (n8n)
**Status:** Live — n8n, daily 5 PM + webhook  
**Trigger:** Schedule (5 PM MDT) or `POST localhost:5678/webhook/bid-leveling`  
**File:** `04_Workflows/WF-007_Bid_Leveling_Engine.json`

Reads Google Sheets bid tracker, builds HTML leveling report, exports updated BT xlsx to Drive, saves Outlook draft.

**Migration path (Phase 9.4):** After bid_entries is populated via email ingestion, redirect WF-007 to read from `GET /api/v1/services/bid-intelligence/leveling` instead of Google Sheets.

---

## Sync Workflows (WORKFLOW-02 / Registry Writeback)

**Triggers:** Daily at startup + manual  
**Code:** `03_Source_Code/workflows/sync_*.py`  
**APIs:** `POST /api/v1/workflows/sync/{hubspot|drive|houzz}`

| Sync | Source | Target | Frequency |
|------|--------|--------|-----------|
| HubSpot | HubSpot CRM | vendors, hubspot_deals, hubspot_notes | Daily |
| Drive | Google Drive | Qdrant drive_memory, MinIO | Weekly |
| Houzz | Houzz Pro | houzz_projects, houzz_daily_logs | Daily (planned) |

**Rule:** Read-only. Never write back to HubSpot without Buck's approval.

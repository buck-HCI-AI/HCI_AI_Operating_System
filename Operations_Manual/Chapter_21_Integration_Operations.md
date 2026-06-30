# Chapter 21 — Integration Operations
*HCI AI Operations Manual — Part II: AI System Operations*
**Author:** Claude Code | **Version:** 1.0 | **Date:** 2026-06-30

---

## 21.1 Integration Overview

The HCI AI OS connects to five external systems. Each connection is read-heavy (the AI reads and learns continuously) and write-protected (nothing writes back without Buck's approval).

| Integration | Purpose | Sync Direction | Write Gate |
|------------|---------|---------------|------------|
| HubSpot CRM | Contacts, deals, companies | Read continuous | GATE-H (Buck approves) |
| Google Drive | Documents, drawings, specs | Read continuous | GATE-F (Buck approves) |
| Microsoft Outlook | Email read + draft | Read + Draft | GATE-E (Buck approves sends) |
| Houzz | Schedule, budget, change orders | Read nightly | Internal DB only |
| Google Sheets | Bid trackers | Read + Write (low risk) | Auto-approved for bid data |

---

## 21.2 HubSpot CRM

**Purpose:** Source of truth for contacts (860+), companies, and deals (4 active projects).

**How it connects:** HubSpot Private App token stored in `.env` as `HUBSPOT_ACCESS_TOKEN`.

**Sync schedule:**
- Continuous discovery: hourly check for changes
- Full sweep: nightly (03:00 via mining engine)

**What gets synced:**
- Contacts → `contacts` table
- Companies → `companies` table  
- Deals → linked to `projects` table via HubSpot deal ID
- Notes/activities → learning queue

**Active deal IDs:**
| Project | HubSpot Deal ID |
|---------|----------------|
| 64 Eastwood | 331240861419 |
| 101 Francis | 321401932527 |
| 1355 Riverside | 321351275210 |
| 246 Gallo Way | 321358358216 |

**Write rule:** NEVER write to HubSpot without Buck's explicit approval. All proposed writes go through `approval_queue` → GATE-H → ntfy → Buck approves → GATE-H webhook fires → n8n writes to HubSpot.

**Check sync status:**
```bash
docker exec hci_postgres psql -U hci_admin -d hci_os -c "
SELECT connector_name, last_sync_at, records_synced 
FROM connector_sync_state 
WHERE connector_name ILIKE '%hubspot%';"
```

**Manual trigger:**
```bash
curl -s "http://localhost:8000/api/v1/services/continuous-discovery/detect" \
  -H "Content-Type: application/json" \
  -d '{"sources": ["hubspot"]}'
```

---

## 21.3 Google Drive

**Purpose:** Document intelligence — drawings, specs, contracts, bids, photos.

**How it connects:** Google Drive OAuth2 token (n8n credential + Python service token in `.env`).

**Sync schedule:**
- New PDF scan: every 15 minutes (AUTO-EVENT-DRIVE-SCAN)
- Full mining: 03:00 daily (mining engine DriveMiner)

**What gets synced:**
- New PDFs → `background_learning_records` (queued for processing)
- Processed docs → Qdrant `drive_memory` collection (2,347 vectors)
- Folder registry → `drive_file_log` table

**Key folder IDs (from reference memory):**
| Folder | Drive ID |
|--------|---------|
| v3 Contacts | (see reference_hci_drive.md) |
| SOPs | SOP 00 + 42-pack + SOP 2.0 |

**Search Drive from API:**
```bash
curl -s "https://speculate-armband-retinal.ngrok-free.dev/gateway/drive/search?q=1355+Riverside+structural"
```

**Write rule:** Drive writes go through GATE-F. The `/gateway/drive/write` endpoint requires API key and creates files at a specified path. Always dry-run first.

---

## 21.4 Microsoft Outlook / Microsoft 365

**Purpose:** Email intelligence — read incoming project emails, create drafts, track client communications.

**How it connects:** Microsoft Graph API via OAuth2. Token refresh handled by `credentials.py` using `get_ms_token()`.

**What gets synced:**
- Inbox reading: all emails scanned for project references
- Drafts: AI creates drafts for Buck to review and send
- Sent: tracked for client communication history

**Active inbox folders:**
- `Inbox/64 Eastwood` — 64EW project emails
- `Inbox/1355 Riverside` — 1355R project emails
- `Inbox/101 Francis` — 101F project emails
- `Inbox/HCI Admin` — General admin

**Creating an Outlook draft via API:**
```python
# In any Python script with the correct sys.path
import sys
sys.path.insert(0, '/Users/buckadams/HCI_AI_Operating_System/03_Source_Code/integrations')
from credentials import get_ms_token
import requests

token = get_ms_token()
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
draft = requests.post(
    "https://graph.microsoft.com/v1.0/me/messages",
    headers=headers,
    json={
        "subject": "Subject line",
        "body": {"contentType": "HTML", "content": "<p>Body...</p>"},
        "toRecipients": [{"emailAddress": {"address": "recipient@domain.com"}}]
    }
)
```

**SSL note:** Always use `requests` library, not `urllib.request.urlopen` — macOS Python 3.13 has SSL cert verification issues with urllib.

**Write rule:** Drafts are created in Buck's mailbox. No email is sent without Buck manually clicking Send (or GATE-E approval). Never auto-send.

---

## 21.5 Houzz

**Purpose:** Schedule intelligence, budget tracking, change orders, daily logs, photos.

**Important: No public Houzz Pro API.** Houzz blocks programmatic access for non-enterprise accounts. Three workaround paths are in play:

**Path A — Email Notifications (Fastest, Partial)**
Houzz can email Buck for daily log submissions, change orders, schedule changes. These emails flow to buck@hendricksoninc.com (our connected inbox). An n8n email parser ingests them automatically.
- **Requires:** Buck enables notifications in Houzz Pro Settings → Notifications
- **What we get:** Daily logs with weather, change orders, messages — same day, automatically
- **What's missing:** Budget detail, timesheets, files, full schedule
- **Status:** ⚠️ NOT YET ENABLED — Buck needs to turn on Houzz email notifications

**Path B — Zapier Bridge (Evaluate)**
Houzz appears in Zapier. Buck connects Houzz → Zapier → webhook to our gateway. Real-time event stream.
- **Requires:** Buck evaluates available Houzz Zapier triggers; ~1-2 hr setup
- **Status:** ⬜ Not evaluated

**Path C — Browser Extraction (Most Complete, BTW-7)**
Playwright headless script logs into Houzz weekly, extracts all 16 table types.
- **What we get:** Everything — budget, timesheets, tasks, files, photos, full schedule
- **Status:** ⚠️ Paused per Chief Architect Directive 2026-06-27 (anti-bot risk)

**Current DB state:**
- 6 projects, 9 daily logs, 12 change orders, 0 tasks/selections/budget (from prior manual extraction)
- 995 schedule items in `houzz_schedule_items` (separately loaded)

```bash
docker exec hci_postgres psql -U hci_admin -d hci_os -c "
SELECT project_id, count(*) as schedule_items 
FROM houzz_schedule_items 
GROUP BY project_id;"
```

**Note on weather:** Houzz Pro includes weather in daily logs natively. No separate weather API needed — weather comes automatically through Path A or C once active.

**BTW-7 (Superintendent field enhancements)** remains blocked pending Houzz extraction decision. Unlocking Path A (email notifications) is the fastest unblock.

---

## 21.6 Google Sheets

**Purpose:** Bid trackers — the primary source for bid package data across all projects.

**How it connects:** Google Sheets OAuth2 (n8n credential). Python service accesses via `read_sheet` / `write_sheet` MCP tools.

**Active bid tracker spreadsheets:**
- 64 Eastwood bid tracker
- 101 Francis bid tracker
- 1355 Riverside bid tracker
- 246 Gallo Way bid tracker

(Sheet IDs in Drive reference memory)

**Sync:** Bid entries are synced from Sheets → `bid_entries` table during mining runs.

**Write rule:** Bid tracker writes (recording award amounts, sub selections) are auto-approved — low risk. All other Sheet writes require review.

---

## 21.7 Connector Sync State

The `connector_sync_state` table tracks when each integration last ran:

```sql
TABLE connector_sync_state (
    connector_name   TEXT,   -- 'hubspot', 'google_drive', 'outlook', 'houzz', etc.
    entity_type      TEXT,   -- 'contacts', 'deals', 'schedules', etc.
    last_sync_at     TIMESTAMP,
    records_synced   INTEGER,
    status           TEXT    -- 'success', 'error', 'partial'
)
```

Check all connector health:
```bash
docker exec hci_postgres psql -U hci_admin -d hci_os -c "
SELECT connector_name, entity_type, last_sync_at, status
FROM connector_sync_state
ORDER BY last_sync_at DESC;"
```

If a connector shows `status = 'error'`: check n8n execution logs for that workflow. Most common causes:
- OAuth token expired → re-authenticate in n8n credentials
- Rate limit hit → wait 1 hour, will auto-recover
- Network error → verify internet connection + ngrok status

---

## 21.8 Adding a New Integration

To add a new data source:

1. Add credentials to `.env` (never hardcode)
2. Create connector in `03_Source_Code/services/connectors/` extending `BaseConnector`
3. Register in `connector_sync_state` with initial row
4. Add n8n workflow for scheduled sync
5. Add to `integration_registry` table
6. Update this chapter
7. File ACR if schema changes required

**Current integrations in `integration_registry`:** 8 registered (HubSpot, Drive, Sheets, Outlook, Houzz, Qdrant, Redis, n8n)

---

*Cross-reference: Chapter 17 (Architecture), Chapter 22 (Database), Chapter 24 (Approval Queue), Chapter 25 (Troubleshooting)*

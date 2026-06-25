# HCI AI — Workflows

n8n workflow JSON exports. Import via n8n UI or API.
n8n running at: http://localhost:5678

## Active Workflows

### WF-007 — AI Bid Leveling Engine
**File:** `WF-007_Bid_Leveling_Engine.json`
**Status:** Live
**Triggers:**
- Daily at 5 PM MDT (schedule)
- On-demand via webhook: `POST http://localhost:5678/webhook/bid-leveling`

**Payload (webhook):**
```json
{ "project_name": "64 eastwood" }
```
Leave `project_name` empty to run for the first project in registry.

**What it does:**
1. Loads Project Registry from Google Sheets
2. Reads Bid Tracker for the project
3. Builds HTML bid leveling report
4. Exports updated BT xlsx to Google Drive
5. Saves draft email to Outlook Drafts

**Output:** DRAFT BID LEVELING — {Project} — {Date} in Outlook Drafts

---

## Planned Workflows

| ID | Name | Priority | Description |
|---|---|---|---|
| WF-001 | New Project Setup | High | Creates all project infrastructure on new deal |
| WF-002 | Meeting Intelligence | High | Transcribe, summarize, extract action items |
| WF-003 | Morning Brief | Medium | Daily briefing email to Buck at 7AM |
| WF-004 | Daily Log | Medium | Field log intake and memory capture |
| WF-005 | Lessons Learned | Medium | Capture and embed lessons into Qdrant |
| WF-006 | Email Intelligence | High | Route, classify, and respond to bid emails |
| WF-008 | Vendor Scorecard | Low | Monthly vendor performance report |

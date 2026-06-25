# 07_BLOCKERS.md
**Active blockers — things that cannot proceed without an external action**
Last updated: 2026-06-24

---

## BLK-001 — GitHub Remote (RESOLVED per status — verify)
**Status:** 00_STATUS.md shows GitHub ✅ LIVE. Verify with `git remote -v`.
**If still open:** run `! gh auth login` then create remote repo.

---

## BLK-002 — HubSpot Connected Inbox (OPEN)
**Blocked on:** Buck completing browser setup in HubSpot
**Impact:** Emails sent from Outlook don't auto-log in HubSpot deal timelines.
**Steps:**
1. HubSpot → Settings → General → Email → Connect personal email → Microsoft Office 365
2. Sign in with buck@hendricksoninc.com
**Workaround active:** Emails being logged manually via Graph API engagements endpoint.

---

## BLK-003 — Memory Ingestion Schema (OPEN — architecture decision)
**Blocked on:** ChatGPT architecture decision on HubSpot → Qdrant mapping
**Impact:** Cannot build ingestion pipeline until schema is specified.
**Question:** How should HubSpot contact/company/deal data map to Qdrant `vendor_memory` schema? What fields to embed? What metadata to attach?
**Resolution:** ChatGPT writes spec to `01_Engineering_Library/SPEC_memory_ingestion_v1.md`

---

## RESOLVED

| Blocker | Resolution | Date |
|---|---|---|
| WF-007 Send Draft empty body | Fixed: reference upstream `Level Bids` node directly | 2026-06-24 |
| HubSpot 401 auth | Fixed: `cred["value"]` already has `Bearer ` prefix | 2026-06-24 |
| n8n SQLITE_IOERR | Workaround: direct Python + Sheets (n8n not used for report build) | 2026-06-24 |
| Repo named HCI_OS | Renamed to `HCI_AI_Operating_System` | 2026-06-24 |
| `.env.example` gitignored | Fixed `.gitignore` pattern | 2026-06-24 |

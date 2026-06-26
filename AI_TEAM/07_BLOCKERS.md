# 07_BLOCKERS.md
**Active blockers — things that cannot proceed without an external action**
Last updated: 2026-06-25 (Phase 13 — QA Framework)

---

## PRODUCTION GO-LIVE IS BLOCKED

**Reason:** QA directive installed. 5 validation gates must pass + Buck must explicitly approve before any production go-live.  
**Document:** `BOOK_00/17_QUALITY_ASSURANCE_AND_VALIDATION.md`  
**Current gate:** Gate 1 Not Started

| Gate | Status |
|------|--------|
| Gate 1 Engineering Validation | ⬜ Not Started |
| Gate 2 Integration Testing | ⬜ Blocked on Gate 1 |
| Gate 3 Workflow Acceptance | ⬜ Blocked on Gate 2 |
| Gate 4 UAT | ⬜ Blocked on Gate 3 |
| Gate 5 Pilot + Buck Approval | ⬜ Blocked on Gate 4 |

---

## BLK-001 — GitHub Remote (VERIFY)
**Status:** Unverified — run `git remote -v` to confirm  
**If still open:** run `! gh auth login` then `gh repo create HCI_AI_Operating_System --private --source=. --remote=origin --push`

---

## BLK-002 — HubSpot Connected Inbox (OPEN — Buck action)
**Blocked on:** Buck completing browser setup in HubSpot  
**Impact:** Emails sent from Outlook don't auto-log in HubSpot deal timelines.  
**Steps:**
1. HubSpot → Settings → General → Email → Connect personal email → Microsoft Office 365
2. Sign in with buck@ahmaspen.com

---

## BLK-003 — Houzz Tables Missing from Live DB (RESOLVED 2026-06-25)
**Status:** ✅ RESOLVED  
All 3 Houzz tables created in live DB. DB now has 22 tables matching init.sql.

---

## BLK-004 — Qdrant drive_memory and vendor_memory Empty (OPEN)
**Status:** OPEN  
**Impact:** Project Brain Q&A lacks document and vendor context — intelligence quality reduced  
**Fix:**
1. Re-run Drive sync: `curl -X POST http://localhost:8000/api/v1/workflows/sync/drive -H "X-API-Key: hci-01253a2b0f87dbd03346bba60f0c31d7350e5c75b17c866c"`
2. Vendor embed pipeline needed: read vendors table → embed → upsert vendor_memory (Phase 12)

---

## RESOLVED

| Blocker | Resolution | Date |
|---|---|---|
| Hardcoded DB password in 7 workflow files | Fixed: all use POSTGRES_PASSWORD env var | 2026-06-25 |
| WF-003 email to wrong address (@hendricksoninc.com) | Fixed: reads BUCK_EMAIL env var | 2026-06-25 |
| hci_project_documents Qdrant collection missing | Fixed: 5 collections created | 2026-06-25 |
| init.sql missing 8 tables + daily_logs columns | Fixed: init.sql updated | 2026-06-25 |
| Memory Ingestion Schema (BLK-003 prior) | Superseded: vendor_memory now the target; schema well-defined | 2026-06-25 |
| WF-007 Send Draft empty body | Fixed: reference upstream Level Bids node directly | 2026-06-24 |
| HubSpot 401 auth | Fixed: cred["value"] already has Bearer prefix | 2026-06-24 |
| n8n SQLITE_IOERR | Workaround: direct Python + Sheets | 2026-06-24 |
| Repo named HCI_OS | Renamed to HCI_AI_Operating_System | 2026-06-24 |

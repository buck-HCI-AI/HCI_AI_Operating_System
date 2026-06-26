# HCI AI — Known Issues Register
**Version:** 1.0 | **Date:** 2026-06-25 | **Directive:** HCI_AI_QA_Testing_and_No_Go_Live_Master_Directive_v1.0

All defects and known issues are logged here with ID `KI-NNN`. This register is the authoritative source for go-live blockers.

---

## Severity Key

| Level | Definition | Go-Live Impact |
|-------|------------|---------------|
| P0 | Data corruption, security breach, system failure | Hard blocker |
| P1 | Happy-path failure, wrong DB write, email not delivered | Hard blocker |
| P2 | Degrades with workaround available | Must fix before UAT |
| P3 | Cosmetic, logging gap, minor data quality | Backlog only |

---

## Open Issues

| ID | Severity | Component | Title | Description | Workaround | Status | Opened | Target |
|----|----------|-----------|-------|-------------|-----------|--------|--------|--------|
| KI-001 | P2 | WF-SYNC-HOUZZ | Houzz Playwright blocked by anti-bot | Houzz returns 429 rate limit and blocks headless Chromium. No login form detected in headless mode. Visible mode attempted (sync_houzz.py --visible) — Chrome window did not open from Terminal context. | Accept no Houzz schedule baseline for now. WF-SYNC-HOUZZ marked Failed Validation. Schedule Intelligence degrades gracefully (no baseline comparison). | Open | 2026-06-25 | TBD |
| KI-002 | P2 | WF-007 n8n | WF-007 Bid Leveling never formally tested | WF-007 runs in n8n, not FastAPI. The trigger endpoint returns 200 from the registry but the n8n webhook flow has not been formally tested with real bid data since Phase 8 build. | Manual n8n trigger. Review n8n execution history. | Open | 2026-06-25 | Gate 3 |
| KI-003 | P2 | vendor-intelligence | vendor_memory Qdrant collection empty | vendor_memory has 0 vectors. Vendor search returns Postgres results only — no semantic similarity. Embed pipeline (vendors → vendor_memory) was planned but not built. | Postgres-only vendor search (field-match). Build embed pipeline. | Open | 2026-06-25 | Gate 3 |
| KI-004 | P3 | WF-001 WF-002 WF-005 WF-006 | 4 workflows do not write to workflow_events | These 4 workflows are missing `_log_event()` calls. workflow_events table is missing their activity. GAP-008. | Manually check DB for downstream state. | Open | 2026-06-25 | Gate 3 |
| KI-005 | P3 | Dashboard | API key visible in dashboard JS source | Dashboard index.html has the API key in plaintext client-side JS. Acceptable for local-only use; must address before any external/browser deployment. | Local-only access. Do not expose dashboard on public URL. | Open | 2026-06-25 | Before public URL |
| KI-006 | P3 | Infrastructure | Qdrant docker ps shows "unhealthy" label | `docker ps` shows Qdrant container with "unhealthy" status label despite API being fully operational and healthy. This is a cosmetic label from missing healthcheck config in docker-compose. | Confirmed operational via API. | Open | 2026-06-25 | Low priority |
| KI-007 | P2 | Infrastructure | Backup script never verified end-to-end | backup.sh was built and launchd scheduled but has never been run and output verified. We do not know if pg_dump and Qdrant snapshots are actually completing. | Run backup.sh manually; verify files appear in HCI_Backups. | **RESOLVED 2026-06-25** | 2026-06-25 | — |
| KI-008 | P3 | WF-PM | WF-PM-W weekly report never tested | PM weekly report (wf-pm/weekly-report) has not been formally triggered with verified output. | Daily review is tested. Use daily review until weekly verified. | Open | 2026-06-25 | Gate 3 |
| KI-009 | P3 | WF-007 | n8n Bid Leveling writes to Google Sheets only | WF-007 does not write leveling results to Postgres bid_entries. Intelligence services cannot query leveling data from DB. | Review Google Sheets output directly. | Open | 2026-06-25 | Future |
| KI-010 | P2 | drive_memory | drive_memory may not persist across Docker restart | Drive sync was confirmed to write 2,335 vectors but subsequent status checks showed 0. Possible Docker volume persistence issue for Qdrant. Needs investigation. | Re-run sync_drive.py after each restart; check Docker volume config. | Open | 2026-06-25 | Gate 1 |

---

## Resolved Issues (Gate 2)

| ID | Severity | Title | Resolution | Date |
|----|----------|-------|-----------|------|
| KI-R07 | P1 | schedule_intelligence wrong JOIN column (hsi.houzz_project_id) + type mismatch | Fixed: queries use `hsi.project_id = %s::text` directly | 2026-06-25 |
| KI-R08 | P2 | TRIGGER_MAP missing 4 workflows; WF-001/002/004/005 had no dispatch handler | Fixed: added to TRIGGER_MAP + dispatch handlers | 2026-06-25 |
| KI-R09 | P2 | Backup script never verified end-to-end (KI-007) | Resolved: backup ran; 364K pg_dump + 13 Qdrant snapshots confirmed | 2026-06-25 |
| KI-R01 | P1 | Hardcoded DB password in 7 workflow files | All 7 files patched to use POSTGRES_PASSWORD env var | 2026-06-25 |
| KI-R02 | P1 | WF-003 morning brief email to wrong address | Fixed: now reads BUCK_EMAIL env var | 2026-06-25 |
| KI-R03 | P1 | hci_project_documents Qdrant collection missing | 5 Qdrant collections created | 2026-06-25 |
| KI-R04 | P1 | Houzz tables missing from live DB | houzz_projects, houzz_daily_logs, houzz_schedule_items created | 2026-06-25 |
| KI-R05 | P1 | schema.sql out of date | 05_Database/schema.sql synced from init.sql | 2026-06-25 |
| KI-R06 | P2 | ngrok tunneling to n8n port 5678 instead of API 8000 | plist updated; launchd restarted | 2026-06-25 |

---

## Go-Live Hard Blockers (P0/P1 currently open)

**None open.** All P0/P1 issues resolved as of 2026-06-25.

The system may proceed to Gate 1 engineering validation. Go-live remains blocked pending all 5 gates.

---

*To add an issue: increment KI-NNN, fill all columns, set status = Open.*  
*Last updated: 2026-06-25*

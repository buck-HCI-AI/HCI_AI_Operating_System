# Mining Validation Report
## HCI AI Operating System — Post-Extraction Mining Run

**Date:** YYYY-MM-DD
**Run ID:** [mining_run_id]
**Triggered by:** [Claude Code / AUTO-004 / Manual]
**Authorized by:** Buck Adams (Owner)
**Directive:** Chief Architect Directive [ACR reference]

---

## Pre-Run Checklist

- [ ] Browser Claude confirmed extraction complete
- [ ] Row counts verified (see Import Validation below)
- [ ] No active write operations in progress
- [ ] dry_run=False explicitly authorized by Buck
- [ ] Previous mining run reviewed (no unresolved failures)

---

## Import Validation Results

*Run `05_Database/houzz_import_validation.sql` before triggering miner.*

| Check | Result | Count | Status |
|---|---|---|---|
| Duplicate daily logs | — | — | — |
| Duplicate schedule items | — | — | — |
| Orphan daily logs | — | — | — |
| Orphan schedule items | — | — | — |
| Future log dates | — | — | — |
| Invalid schedule date ranges | — | — | — |
| Logs missing project_id | — | — | — |
| Schedule items missing project_id | — | — | — |
| Projects without any logs | — | — | — |
| Orphan child tasks | — | — | — |

**Row Counts at Run Time:**

| Table | Rows |
|---|---|
| houzz_projects | — |
| houzz_daily_logs | — |
| houzz_schedule_items | — |

---

## Mining Run Results

### By Miner

| Miner | Status | Scanned | Discovered | Extracted | Queued | Skipped | Duplicates | Errors |
|---|---|---|---|---|---|---|---|---|
| HubSpotMiner | — | — | — | — | — | — | — | — |
| DriveMiner | — | — | — | — | — | — | — | — |
| OutlookMiner | — | — | — | — | — | — | — | — |
| HouzzMiner | — | — | — | — | — | — | — | — |
| HistoricalCostMiner | — | — | — | — | — | — | — | — |
| VendorIntelligenceMiner | — | — | — | — | — | — | — | — |
| LessonsLearnedMiner | — | — | — | — | — | — | — | — |
| ExecutiveAggregator | — | — | — | — | — | — | — | — |

### Totals

| Metric | Value |
|---|---|
| Total records scanned | — |
| Total intelligence extracted | — |
| Total items queued for review | — |
| Total auto-written | — |
| Total skipped (duplicates) | — |
| Execution time | — seconds |
| Errors encountered | — |

---

## Houzz Intelligence Generated

*Populated by HouzzMiner after successful extraction.*

| Project | Daily Logs Processed | Schedule Items | Intelligence Items | Lessons Extracted |
|---|---|---|---|---|
| 64 Eastwood | — | — | — | — |
| 101 Francis | — | — | — | — |
| 1355 Riverside | — | — | — | — |

---

## Vendor Candidates Discovered

| Source | New Candidates | Duplicates Skipped | Net New |
|---|---|---|---|
| HubSpot Companies | — | — | — |
| HubSpot Contacts | — | — | — |
| Houzz Contacts | — | — | — |

---

## Approval Queue Impact

| Before Run | After Run | Net New Items |
|---|---|---|
| — | — | — |

Top new items for Buck's review:
1. —
2. —
3. —

---

## Errors & Failures

| Miner | Error | Resolution |
|---|---|---|
| — | — | — |

---

## Assessment

**Overall Result:** [ ] ✅ PASS — all miners completed, no critical errors
              [ ] ⚠️ PARTIAL — some miners failed, data incomplete
              [ ] ❌ FAIL — critical errors, review before next run

**Recommendation for Architecture Review Board:**

[Claude Code assessment here]

---

## Sign-Off

| Role | Name | Date | Signature |
|---|---|---|---|
| Owner | Buck Adams | — | ⏳ Pending |
| Chief Architect | ChatGPT | — | ⏳ Pending |
| Lead Implementation Engineer | Claude Code | — | Auto-generated |

---

*Mining Validation Report Template | HCI AI Operating System | Hendrickson Construction, Inc.*
*Authority: Chief Architect Directive | Governed by APPROVAL_GATES.md*

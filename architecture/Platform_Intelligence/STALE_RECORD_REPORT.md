# Stale Record Report
**Date:** 2026-06-28

## Findings
| Table | Count | Status |
|---|---|---|
| bid_entries (>90 days old) | 0 | ✅ |
| houzz_schedule_items | 0 | ⚠️ Empty — extraction needed |
| rfis | 0 | ✅ |
| daily_logs | 12 | ✅ |

## Houzz Data Gap
Houzz schedule, task, and PO tables have no records. Browser extraction required.
**Action:** Browser Claude extraction (Houzz > each pilot project > Schedule + Tasks + POs).

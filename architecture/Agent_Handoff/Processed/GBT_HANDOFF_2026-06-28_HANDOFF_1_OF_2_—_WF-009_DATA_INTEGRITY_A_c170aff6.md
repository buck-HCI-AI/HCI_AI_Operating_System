---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: HANDOFF 1 OF 2 — WF-009 DATA INTEGRITY AUDIT
created_at: 2026-06-28
summary: Handoff from ChatGPT via GBT Gateway
---

Urgent Gate 5 handoff from HCI Chief Architect.

Scope: WF-009 Schedule Variance Checks / Schedule Intelligence data integrity audit.

Objective:
Audit WF-009 end-to-end to confirm schedule intelligence is using accurate, current, non-duplicated, project-scoped data before Architecture Freeze v1.0.

Required audit checks:
1. Verify Houzz ingestion records are correctly loaded and mapped by project:
   - 64EW / 64 Eastwood: expected 336 schedule items per live state
   - 101F / 101 Francis: expected 259 schedule items per live state
   - 1355R / 1355 Riverside: expected 400 schedule items per live state
2. Confirm WF-009 reads from the intended canonical schedule tables or service layer, not stale files or test fixtures.
3. Confirm project code normalization is consistent across all schedule endpoints:
   - 64EW
   - 101F
   - 1355R
   - 83S excluded unless initialized
4. Check for duplicate schedule rows, orphan rows, null critical dates, malformed dates, and cross-project contamination.
5. Reconcile schedule variance outputs against LIVE_PROJECT_STATE.md:
   - 64EW: +1 day variance listed in live state
   - 101F: +2 days variance listed in live state
   - 1355R: 0 days variance listed in live state
6. Investigate discrepancy where executive gateway report showed all projects as 'On track, 0 risks' while LIVE_PROJECT_STATE.md reports 64EW and 101F as YELLOW with open risks and variances.
7. Confirm /mvp/projects/{code}/schedule-status and /gateway/project/{code}/schedule return consistent status, variance, and source metadata.
8. Confirm WF-009 outputs remain read-only or approval-gated and do not perform unauthorized production writes.
9. Produce concise audit report with:
   - pass/fail by check
   - affected tables/endpoints
   - root cause for any discrepancy
   - recommended patch plan
   - whether WF-009 is safe for Architecture Freeze v1.0

Priority: HIGH. Gate 5 closes July 1. This is HANDOFF 1 OF 2 for freeze readiness.

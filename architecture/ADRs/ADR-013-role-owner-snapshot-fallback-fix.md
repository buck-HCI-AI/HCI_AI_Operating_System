---
id: ADR-013
title: role_owner Snapshot Null-Fallback Fix + Full Test/Dummy-Data Sweep
status: accepted
date: 2026-07-01
author: Claude Code (session 2026-07-01)
tags: [data-integrity, snapshot, role-console, incident-followup]
---

## Context

Buck reported (via a message relayed through GBT from Browser Claude) that "we are
still getting info from dummy test in the system" and that the 101F schedule variance
was "showing 0" — the same claims investigated and disproven earlier in this session
(ADR-009: 1355R risks confirmed real, 101F variance confirmed consistent). The claim
recurring with a third different symptom ("1" → confirmed consistent → "0") without
re-verification against live state was itself a signal worth treating seriously: either
a real bug existed that hadn't been found yet, or the AI team was repeating an
unverified claim across handoffs.

## Investigation

Ran a full sweep rather than trusting the directive at face value:
- Re-queried `risks` for 1355R directly: same 5 real risks as before (RFI, procurement,
  cost items), zero test/dummy markers.
- Swept `rfis`, `submittals`, `daily_logs`, `bid_entries`, `vendors` for
  test/dummy/fake/placeholder markers in every text field: zero matches across all
  tables.
- Checked every consumer of 101F's schedule variance (`executive/report`, `project/pm`,
  `role/owner`, `project_brain_snapshots` directly) to find where "0" could plausibly
  come from.

**Found a real bug in `GET /gateway/role/owner`**: its query joined
`project_brain_snapshots` with `snapshot_date = CURRENT_DATE` and no fallback. Until
the nightly snapshot job runs for the current day, that join returns `NULL` for
`health` and `schedule_variance_days` for every project — which reads as blank/zero to
anyone checking before that job fires. `executive/report` already had a Python-level
fallback for this exact gap (added earlier in ADR-009); `role_owner` did not.

This most plausibly explains the recurring "0"/inconsistent-variance claims: whoever
(Browser Claude) checked `role_owner` at a moment before the day's snapshot had run
saw null/blank, read it as a data bug, and that claim propagated across handoffs
without being re-verified against `executive/report` (which was already correct) or
the underlying `risks`/`project_brain_snapshots` tables directly.

## Decision

Changed `role_owner`'s snapshot join from an exact-date match to a `LEFT JOIN LATERAL`
pulling each project's **most recent** snapshot (`ORDER BY snapshot_date DESC LIMIT 1`),
matching the intent of "current known health" rather than "only today's health, blank
otherwise." Verified live: 101F now shows `health: GREEN`, `schedule_variance_days: -5`
instead of `null`/`null`. Regression test added (`test_ai_control_plane.py` §18).
86/86 total suite passing.

## Conclusion for the "dummy data" concern

No test/dummy/fake data was found anywhere in the production tables checked. The
underlying data is clean. The actual defect was a stale-snapshot display bug in one
endpoint (`role_owner`), now fixed, plus a process gap: claims about data problems were
being repeated across AI-team handoffs without re-checking live system state each time.
Recommend treating any future "X is showing wrong/test data" report as a hypothesis to
verify against the live DB/API before acting on it, not as an established fact —
exactly the pattern that caused three different, mutually-inconsistent descriptions of
the same non-existent 101F bug this session.

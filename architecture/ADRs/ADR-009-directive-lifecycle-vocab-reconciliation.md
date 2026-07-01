---
id: ADR-009
title: Directive Lifecycle Vocabulary Reconciliation + Mission Control Risk Source-of-Truth Fix
status: accepted
date: 2026-07-01
author: Claude Code (session 2026-07-01)
tags: [gateway, ai-messages, directive-lifecycle, mission-control, risks, sprint-3]
---

## Context

ADR-007 (2026-06-30) flagged an unresolved vocabulary conflict: `ai_messages.status`
used `NEW/ACKNOWLEDGED/IN_PROGRESS/BLOCKED/COMPLETE/NEEDS_BUCK_APPROVAL/REJECTED/STALE`
in the DB constraint, but the live code path actually used `NEW/RECEIVED/IN_PROGRESS/
BLOCKED/COMPLETE/NEEDS_BUCK_APPROVAL/FAILED/STALE` — ADR-007 said this "needs Chief
Architect reconciliation if a different vocabulary is required going forward."

On 2026-07-01, ChatGPT (Chief Architect/ARB) sent two GBT handoffs
(`GBT_HANDOFF_2026-07-01_Implementation_Directive...md` and
`..._Production_Warm_Start...md`) explicitly requiring the lifecycle
`ISSUED -> RECEIVED -> IN_PROGRESS -> COMPLETE` plus `BLOCKED`/`REJECTED`, with
required fields `priority`, `received_at`, `acknowledged_at`, `started_at`,
`completed_at`, `blocked_reason`, `source_of_truth_link`. Same directive also
raised two data-consistency items: 101F schedule variance (executive report
"1" vs LIVE_PROJECT_STATE.md "-5 days") and 1355R risk count (suspected test-data
inflation).

## Decision

1. **Vocabulary reconciled, not forked.** Migration 021 renames `NEW -> ISSUED` and
   `FAILED -> REJECTED` in `ai_messages` (data + CHECK constraint), matching the
   ARB's literal ask. All code paths (`_handle_buck_command`, `_comms_snapshot`,
   `ai_message_status`, `/ai/queue`, `/ai/warm-start`, `/health`) updated to match.
   No new `ai_directives` table — `ai_messages` remains the one directive/message
   system per "extend before creating."
2. **New required fields added** to `ai_messages`: `priority`, `received_at`,
   `acknowledged_at`, `started_at`, `completed_at`, `blocked_reason`,
   `source_of_truth_link`. `PATCH /ai/messages/{id}/status` now stamps the matching
   timestamp automatically on each transition instead of requiring a separate call.
3. **New endpoints**: `GET /gateway/ai/messages/{id}` (read), `POST
   /gateway/ai/messages/{id}/acknowledge` (explicit ISSUED->RECEIVED, distinct from
   the generic status PATCH), `GET /gateway/ai/directives/stale` (named alias over
   `GET /ai/queue?status=STALE` — same table, no second implementation), `POST
   /gateway/heartbeat` (literal path both ARB directives asked for, aliasing the
   same handler as the pre-existing `POST /gateway/ai/heartbeat`).
4. **Heartbeat extended**: `ai_agent_heartbeat` gained `role`, `current_task`,
   `last_directive_id`, `metadata` (jsonb) — migration 021.
5. **101F schedule variance — investigated, not a bug.** Executive Report's
   `max_variance_days`/`total_variance_items` already agreed with
   LIVE_PROJECT_STATE.md's `-5 days` (`+5d behind` == `abs(-5)`). The ARB's "1" was
   reading `total_variance_items` (a COUNT of flagged schedule_variance rows, which
   is 1 for 101F) as if it were a day value — a naming collision, not a sign
   inversion or stale rollup. Added an explicit signed `schedule_variance_days`
   field to `GET /gateway/executive/report` sourced from
   `project_brain_snapshots.schedule_variance_days` so the ambiguity can't recur.
6. **1355R risk count — real bug found, in the opposite direction than suspected.**
   `GET /gateway/executive/mission-control`'s `portfolio` section read
   `project_brain_snapshots.risk_count` (an algorithmic `detect_risks()` snapshot,
   showing `1`/`GREEN` for 1355R) and its `top_risks` section read
   `project_risks_computed` (permanently empty — 0 rows, dead table), while
   Executive Report / PM Console / `role_owner` all read the persisted `risks`
   table directly (5 open risks for 1355R, 2 high severity, health should be RED).
   None of the 5 `risks` rows are test/dummy data — confirmed by content
   (RFI-001 Axis B beam pocket, procurement bid gaps, cost exposure — all
   real project detail) and by absence of any `test`/`dummy`/`sample`/`simulat`
   markers. Fixed `executive.py mission_control()` to reconcile `portfolio.health`/
   `risk_count` as the worse-of the two signals, and to source `top_risks` from
   the canonical `risks` table instead of the dead one.

## Constraints

- Did not touch the underlying `detect_risks()` algorithmic health-scoring engine
  (ADR-004) — it still runs and still feeds `project_brain_snapshots` for the
  predictive/health-factor use case it was built for. This ADR only stops Mission
  Control from silently disagreeing with the rest of the system on risk counts.
- `project_risks_computed` is left in place (unpopulated) rather than dropped —
  no evidence it's used elsewhere, but removing a table is out of scope for a
  same-day reconciliation patch.
- Test suite: `03_Source_Code/tests/test_ai_control_plane.py`, 65/65 passing
  against the live local API (restarted this session to pick up the code change).

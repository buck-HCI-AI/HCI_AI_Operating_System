---
id: ADR-007
title: AI Operations Control Plane — Durable Comms + Warm Start Recovery
status: accepted
date: 2026-06-30
author: Claude Code (session 2026-06-30)
tags: [gateway, telegram, ai-messages, heartbeat, warm-start, control-plane]
---

## Context

Three directives landed in quick succession on 2026-06-30 (Code Directive, Claude
Dode V2, Code Recovery AI Plan) asking for: durable AI-team communication that
survives Telegram outages or chat restarts, an approval bridge over Telegram, and
a single warm-start recovery sequence. An audit (see
`Architecture/Reviews/2026-06-30_Collaboration_Retrospective_and_Audit.md` and the
comms-path audit that preceded this ADR) found Telegram was unreliable for three
concrete reasons: webhook registration only existed in an unused module
(`integrations/telegram_bot.py`, never imported), `_tg_send()` had no retry and no
fallback at the two alert call sites that actually failed in production that day,
and Markdown `parse_mode` 400 errors were a known recurring failure (commit
`ab14e29`). No existing table modeled agent-task acknowledgement state or
per-agent liveness.

## Decision

1. **`ai_messages`** (migration 018) is the durable source of truth for agent/Buck
   communication. Telegram and ntfy are notification layers only — a failed send
   never loses the message.
2. **`ai_agent_heartbeat`** (migration 018) tracks per-agent liveness:
   `ONLINE`/`OFFLINE`/`STALE` (computed dynamically from `last_seen_at`)/`RECOVERING`/`BLOCKED`.
3. Reused rather than duplicated: the `missions` table (migration 008, already
   live with 15 rows) for the implementation queue; `approval_queue` for
   external-write approvals (untouched); the Agent_Handoff Inbox/`handoff_processor.py`
   bus (already built, just had a 19-item backlog cleared this session) for
   architecture handoffs.
4. New endpoints on `/gateway`: `ai/messages` (create), `ai/queue` (fallback poll),
   `approvals`, `ai/messages/{id}/status` (agent self-report), `ai/heartbeat`,
   `ai/escalation-check` (retry + ntfy escalation for stale approvals),
   `telegram/health` (webhook + 24h send health diagnostic),
   `telegram/register-webhook` (makes webhook registration callable instead of a
   manual, undocumented step), `ai/events` (merged recent-activity feed),
   `ai/warm-start` (single-call recovery snapshot).
5. Telegram replies `APPROVE <id>` / `REJECT <id>` / `HOLD <id>` / `STATUS` /
   `QUEUE` are parsed in the existing webhook handler and update `ai_messages`
   directly — same logic backs the inline-keyboard buttons sent with approval
   requests.
6. `bids/stale/alert` and `schedule/variance/alert` — the two endpoints with
   confirmed silent-failure incidents that day — now route through
   `_notify_agents()` instead of bare `_tg_send()`, so a Telegram failure falls
   back to ntfy instead of being dropped.
7. Mission Control (`/gateway/executive/mission-control`) gained a `comms` block
   (pending approvals, unacked messages, stale items, blocked missions, agent
   heartbeats, Telegram 24h health) without altering its existing business-KPI
   payload shape.

## Vocabulary conflict (flagged, not silently resolved)

The "Claude Dode V2" directive specified message states `NEW/ACKNOWLEDGED/
IN_PROGRESS/BLOCKED/COMPLETE/NEEDS_BUCK_APPROVAL`; the later "Code recovery ai
plan" directive specified `NEW/RECEIVED/IN_PROGRESS/COMPLETE/NEEDS_BUCK_APPROVAL/
FAILED`. The first vocabulary was implemented and live-tested (real Telegram
approve/reject/hold round-trip with Buck, confirmed in this session) before the
second directive arrived. Rather than fork a second status enum mid-build,
`ACKNOWLEDGED` and `REJECTED` stand as the canonical terms covering `RECEIVED`/
`FAILED`. Documented in `AI_TEAM/WARM_START.md` — needs Chief Architect
reconciliation if a different vocabulary is required going forward.

## Constraints

- `ai_messages`/`ai_agent_heartbeat` are intentionally minimal — no project-code
  foreign key enforcement, no soft-delete, no pagination cursor (LIMIT only).
  Matches the "do not overbuild, patch first" instruction in the originating
  directive.
- Heartbeat staleness (`STALE` after `AI_HEARTBEAT_STALE_MINUTES`, default 120)
  and approval staleness (`STALE` after `AI_APPROVAL_STALE_MINUTES`, default 30)
  are computed at read time / by `escalation-check`, not by a background cron —
  no scheduler exists in-process; `ai/escalation-check` is meant to be called by
  n8n on a schedule (not yet wired — see remaining gaps in the session report).
- Test suite: `03_Source_Code/tests/test_ai_control_plane.py`, 32/32 passing
  against the live local API.

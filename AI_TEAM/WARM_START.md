# Warm Start — Restart Recovery Sequence

Goal: any restart (Buck's machine, Claude Code, Browser Claude, a new ChatGPT session,
the gateway, or n8n) recovers full operational state in under 60 seconds.

This does **not** introduce a new state store. It is a recovery *sequence* over
infrastructure that already exists: `projects`/`risks`/`missions` tables, the
`ai_messages` durable queue, `approval_queue`, the Architecture Inbox (Agent_Handoff
bus), and Telegram. See `Architecture/Reviews/2026-06-30_Collaboration_Retrospective_and_Audit.md`
for the audit that confirmed what already existed before this patch.

## One-call shortcut

`GET /gateway/ai/warm-start` returns everything below in a single response:
active projects, top risks, pending Buck approvals, pending Chief Architect
reviews, pending Code/BC tasks (from the `missions` table), blocked missions,
stale handoffs, last successful Telegram send/receive, agent heartbeats, and a
computed `next_recommended_action`. Call this first — read the rest of this
document only if you need the underlying detail or a path is down.

## Startup sequence by agent

### Claude Code (this agent)
1. `GET /gateway/ai/warm-start` — single-call snapshot (above).
2. Read `LIVE_PROJECT_STATE.md`, `CURRENT_SPRINT.md`, `AI_TEAM/WHILE_AWAY_DIRECTIVE.md`.
3. `ls Architecture/Agent_Handoff/Inbox/` — if non-empty, run
   `python3 Architecture/Agent_Handoff/handoff_processor.py` before other work.
4. `GET /gateway/ai/queue?target=claude_code` — durable task queue (works even if
   Telegram/ntfy are down).
5. `POST /gateway/ai/heartbeat {"agent":"claude_code","action":"session start"}`.

### Browser Claude
1. `GET /gateway/ai/warm-start`.
2. `GET /gateway/ai/queue?target=browser_claude`.
3. `GET /gateway/telegram/messages?agent=browser_claude` — Buck's Telegram messages you'd
   otherwise never see (added 2026-07-01 — you're not a Telegram participant, Buck's
   messages only reach you if you poll for them here). `POST /gateway/telegram/ack
   {"agent":"browser_claude","message_id":<id>}` once you've acted on them.
4. `POST /gateway/ai/heartbeat {"agent":"browser_claude","action":"session start"}`.

### ChatGPT (Chief Architect)
1. `GET /gateway/project-state` (full `LIVE_PROJECT_STATE.md`).
2. `GET /gateway/ai/warm-start`.
3. `GET /gateway/ai/queue?target=chatgpt` — items awaiting Chief Architect review.
4. `GET /gateway/telegram/messages?agent=chatgpt` — same gap as Browser Claude above;
   this is the only way you see Buck's Telegram messages. Ack with `POST
   /gateway/telegram/ack {"agent":"chatgpt","message_id":<id>}`.
5. `POST /gateway/ai/heartbeat {"agent":"chatgpt","action":"session start"}`.

### n8n
1. Schedule `POST /gateway/ai/escalation-check` every 15 min (retries stale
   Buck approvals, escalates to ntfy if Telegram fails — see Control Plane patch).
2. Schedule `POST /gateway/ai/heartbeat {"agent":"n8n","action":"cycle"}` on each
   active workflow run.
3. On its own restart: `GET /gateway/telegram/health` — if `webhook_matches_expected`
   is false, call `POST /gateway/telegram/register-webhook` once.

### Buck
1. Telegram is the notification layer, not the source of truth — if a message was
   missed, nothing is lost. Reply `QUEUE` to Telegram any time to see what's pending,
   or `STATUS` for counts by state.
2. `GET /gateway/ai/warm-start` (browser/Mission Control) shows the same picture.
3. `GET /gateway/buck/compose` — phone-bookmarked form to send a message to the system
   if Telegram itself is unreachable.

## Required warm-start reads (mapped to existing infra — nothing new built here)

| # | Read | Source |
|---|---|---|
| 1 | `LIVE_PROJECT_STATE.md` | `GET /gateway/project-state` |
| 2 | `CURRENT_SPRINT.md` | repo file |
| 3 | `AI_TEAM/WHILE_AWAY_DIRECTIVE.md` | repo file |
| 4 | Architecture Inbox | `Architecture/Agent_Handoff/Inbox/` (already built — `handoff_processor.py`, `HANDOFF_INDEX.md`) |
| 5 | Implementation queue | `missions` table (already built, migration 008) — `pending_code_tasks`/`pending_bc_tasks` in warm-start |
| 6 | Approval queue | `approval_queue` table (external-write approvals) + `ai_messages` (`requires_buck_approval`) — `GET /gateway/approvals` |
| 7 | Mission Control | `GET /gateway/executive/mission-control` (now includes a `comms` block) |
| 8 | Buck Telegram / poll instructions | `GET /gateway/poll-instructions`, `GET /gateway/ai/queue` |
| 9 | Gateway health | `GET /gateway/health` |
| 10 | n8n health | n8n `:5678` REST API |
| 11 | Telegram health | `GET /gateway/telegram/health` |
| 12 | Last 20 AI events/handoffs | `GET /gateway/ai/events` |

## Status vocabularies

**Agent online/offline state** (`ai_agent_heartbeat.status`, one row per agent):
`ONLINE` (heartbeat fresh) · `OFFLINE` (no heartbeat yet) · `STALE` (no heartbeat
in `AI_HEARTBEAT_STALE_MINUTES`, default 120) · `RECOVERING` (set manually during
a known restart) · `BLOCKED` (set manually when an agent is known-stuck).

**Directive/message lifecycle state** (`ai_messages.status`): `ISSUED` ·
`RECEIVED` (acknowledged) · `IN_PROGRESS` · `COMPLETE` · `BLOCKED` (see
`blocked_reason`) · `REJECTED` · `NEEDS_BUCK_APPROVAL` · `STALE` (escalation
fired, still unacknowledged). Reconciled 2026-07-01 (migration 021, ADR-009)
per explicit Chief Architect/ARB directive — this is now the canonical
vocabulary; the `NEW`/`FAILED` and `ACKNOWLEDGED` variants ADR-007 flagged as
unresolved are retired. Each transition stamps the matching timestamp
(`received_at`/`started_at`/`completed_at`) automatically via
`PATCH /ai/messages/{id}/status`; use `POST /ai/messages/{id}/acknowledge` for
the explicit ISSUED->RECEIVED step. Records also carry `priority`,
`source_of_truth_link`.

## Telegram — notification only, DB is source of truth

`ai_messages` is written *before* any Telegram send is attempted. If Telegram
fails (confirmed root causes: webhook registration previously lived only in
unused code, no retry logic, Markdown parse-mode 400s), the message still
exists and is visible via `/gateway/ai/queue` and `/gateway/approvals`. Failed
sends fall back to ntfy automatically. `/gateway/ai/escalation-check` retries
and re-escalates anything still unacknowledged past the stale threshold.

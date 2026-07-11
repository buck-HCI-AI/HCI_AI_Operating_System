# ADR-019 — AI Resilience & Recovery Architecture (Canonical)

**Date:** 2026-07-11
**Status:** Accepted, live
**Driver:** Chief Architect directive (relayed by Buck, Telegram msg 1508,
2026-07-11 13:33 MT): "Document this entire incident as the canonical AI
Resilience & Recovery Architecture... Preserve those lessons so they become
part of the operating system, not just something the team remembers."

## Context

Over 2026-07-10 to 2026-07-11 the three-agent team (Claude Code / "CODE",
ChatGPT Custom GPT "HCI Chief Architect" / "GBT", Browser Claude / "BC") went
through a real, not simulated, sequence of outages and recoveries:

1. **Session-death gap (2026-07-10 ~16:10 MT to 2026-07-11 ~10:34 MT).** No
   Claude Code session was running at all — not a crash inside a session, a
   fully dead process with nothing to restart it. Buck had to send 8+ messages
   before a fresh session properly re-engaged and caught up. This is the
   incident that dropped Buck's stated trust to "almost zero" and is the
   direct origin of every fix below.
2. **GBT version-pinning tool loss (this week, exact date in
   `project_gbt_down_root_cause_resolved_2026-07-10` memory).** A live
   ChatGPT chat session got permanently pinned to a stale Actions-schema
   version mid-session after an unrelated schema edit, silently losing tool
   access with no error — it fell back to web search rather than failing
   loudly. Root cause: ChatGPT pins an already-open chat to whatever schema
   version was live when it started; only a brand-new chat picks up a schema
   change. No in-chat recovery path exists — only a fresh chat.
3. **BC's structural non-autonomy.** Browser Claude cannot call the gateway
   API at all, under any circumstance — a hard platform constraint, not a bug.
   It only acts when a human (Buck) opens a chat with it. Any design for BC
   participation has to route around this, not attempt to fix it.

## Decision — the resilience architecture now in place

### 1. Durable, queryable message bus (ADR-003), not chat memory
`agent_messages` / `agent_heartbeats` / `decision_log` (Postgres tables,
`gbt_gateway.py`) hold every inter-agent message, presence signal, and
architecture decision durably. No agent's live chat context is ever the
system of record. A message sent while the recipient is offline simply waits;
there is no "the other agent missed it" failure mode as long as the database
is up.

### 2. BC's Drive-mirror bridge — the answer to "BC can't call the API"
Since BC cannot call the gateway, any message addressed to `BC` (or `ALL`) is
auto-mirrored into a real Google Drive file in "HCI AI Master"
(`_sync_coordination_documents()` / `POST /gateway/coordination/documents`).
BC's actual session-start action — reading Drive — *is* its inbox. This isn't
a workaround bolted onto the real system; for BC specifically, Drive-as-inbox
**is** the real system, because that's the only channel that exists for it.

### 3. Fresh-session-required rule for GBT after any schema edit
Never verify a ChatGPT Actions schema change inside the same chat that
existed before the edit. Always open a new chat. This is now standing
practice (see the Phase 2 verification below) after the version-pinning
incident proved the pinned session shows no error — it just silently can't
see the new tools.

### 3b. GBT Actions calls fail transiently, even mid-session — retry before escalating
Discovered 2026-07-11 during full pairwise matrix verification: a fresh, correctly
schema-bound GBT chat's `readCoordinationDocument` call returned "no response
payload" on the first attempt, then succeeded immediately on retry with correct
data. Curling the same backend endpoint directly returned correctly in 1.3-1.5s
both times — the backend was never the problem. This is a distinct failure mode
from the version-pinning outage (#2): not "tools unavailable," but an
individual Actions call occasionally not completing its round trip. Standing
practice: one retry before concluding a capability is actually broken: A single
failed call is not evidence of a real gap.

### 4. Evidence-over-assertion verification standard
An agent's own report that it did something is not evidence. The standard
now required for any cross-agent capability claim:
- The action must produce a row in a durable table (`agent_messages`,
  `agent_heartbeats`, `decision_log`, `ai_messages`, etc).
- That row must be independently queried (`psql`/API call from a *different*
  agent or a fresh check) and shown to match the claim.
- A ChatGPT/Claude chat "completing" or "looking right" is explicitly **not**
  sufficient — confirmed by Buck/GBT directly in msg 1507 after a screenshot
  of an unrelated mobile-app streaming failure: "Don't use a Claude chat
  completing successfully as the proof that the communications layer works...
  use objective evidence... message stored in the Agent Bus, receiver
  acknowledges it, heartbeat updates, unread count decreases, returning agent
  catches up, audit log records the exchange."
- Applied concretely in the 2026-07-11 Phase 2 Actions-schema update: after
  GBT reported success calling `ambHeartbeat`/`ambGetUnread`/`ambSendMessage`/
  `ambMarkRead` from a fresh chat, every result was independently re-verified
  with a direct `psql` query against `agent_messages`/`agent_heartbeats`
  before being reported to Buck as done.

### 5. Consolidate before you add — respect hard platform caps honestly
ChatGPT Custom GPT Actions have a hard, non-negotiable 30-operation cap. When
GBT's schema hit exactly 30/30, the fix was not to pick something to cut
arbitrarily or force a broken save — it was to find real duplication
(7 near-identical `GET /gateway/project/{code}/X` views) and collapse it into
one parameterized endpoint (`GET /gateway/project/{code}/view?view=X`) with
verified-identical output, freeing room without losing any capability. General
principle: when a platform constraint is hit, look for genuine consolidation
before treating it as a wall to negotiate around.

### 6. Build on the platform, not around it (Chief Architect principle,
2026-07-11 handoff)
Every new capability must consume canonical platform infrastructure rather
than stand up a parallel one: identity comes from the People & Identity
Platform, communications go through the Agent Bus (this ADR), project data
comes from the consolidated Project View (#5 above), decisions are recorded
in `decision_log`. Before building anything new, the question is "can this
reuse the canonical platform," not "what's the fastest thing to build."

## Verification standard going forward

Three-agent sign-off (Chief Architect directive, Phase 3): a capability isn't
"communications infrastructure" until each agent has independently exercised
it from its own real interface — not one agent simulating another's role.
CODE and GBT have each done this for the Agent Bus (2026-07-11, DEC-005/
DEC-006 in `decision_log`). The full pairwise matrix has real evidence as of
2026-07-11 13:48 MT (`decision_log` entry `bf45332d`): CODE<->GBT (Phase 2),
GBT->BC (`ambSendMessage`, real Drive mirror file, content verified by direct
read), BC->GBT (`readCoordinationDocument` on `GBT_INBOX.md`, real content
matched a direct API read). BC's own independent confirmation of its side
(reading/writing/heartbeat/catch-up from its own perspective, not GBT/Code
exercising it on BC's behalf) was requested the same day via the Drive-mirror
bridge (#2 above) and is tracked as the remaining Phase 3 gap as of this
ADR's filing.

## Known, disclosed, unresolved gap

The session-death scenario (#1 above) that caused the original trust
incident is **not fully closed**. The in-session 5-minute check-in loop
(`ScheduleWakeup`/`CronCreate`) only functions while a Claude Code session is
alive; if the session or terminal is fully closed, nothing local restarts it.
A concrete fix — a cloud `RemoteTrigger`/`/schedule` routine as a backstop
layer, since it runs in Anthropic's cloud independent of the local machine —
has been identified but not built, pending Buck's cost/tradeoff call (min
1-hour interval, no local Docker/file access). This is the one open item in
an otherwise-closed resilience story and should not be quietly dropped.

## Why this is an ADR and not just a session note

Buck and the Chief Architect both explicitly asked for this to become part of
the operating system's permanent record, not tribal knowledge that erodes the
next time a session gap happens. Future agents (any of the three, or a fresh
Claude Code session after a restart) should read this ADR to understand *why*
the message bus, the Drive-mirror, the fresh-chat rule, and the evidence
standard exist — they are direct responses to real, dated incidents, not
speculative hardening.

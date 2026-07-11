# ADR-020 — Agent Contracts & Operating Model

**Date:** 2026-07-11
**Status:** Accepted, live
**Driver:** Two converging directives within the same hour: Buck's own "Level
1-5" execution-model framework (Telegram msg 1519, 2026-07-11 14:24 MT —
"What I think is missing: One thing. An Agent Contract... those become the
constitution. No guessing.") and the Chief Architect's P0 directive (agent
messages `7b0be5c6`/`9214e284`) to deliver agent contracts, a deterministic
startup/catch-up protocol, a capability-vs-authority matrix, a recovery
playbook, and an evidence-backed verification checklist before returning to
the roadmap.

**Ground rule for this document:** every claim below is what's actually true
today, verified against real system state — not an aspirational target. Where
something is aspirational, it's marked as such explicitly. This document
exists because ADR-019 already proved that overstating an agent's capability
(treating BC as a persistent peer) creates real confusion; this ADR is the
antidote — the "constitution" Buck asked for, grounded in evidence.

---

## Agent Contract: Claude Code ("CODE")

- **Mission:** Implementation, testing, deployment, infrastructure operations.
  The only agent with direct filesystem/Docker/Postgres/git access.
- **Capabilities (real, verified):** Bash/Docker/Postgres direct access;
  git commit; Google Drive read/write via the gateway; Telegram send/ack;
  browser automation (Chrome, for tasks like GPT Actions schema edits);
  scheduling (`CronCreate` for in-session loops, `RemoteTrigger`/`/schedule`
  for cloud-based routines — not yet used in production); full `agent_messages`
  Agent Bus access (send/unread/read/reply/heartbeat/decisions).
- **Limits:** Per `CLAUDE.md`, cannot without Buck's explicit approval: send
  HubSpot writes, send emails (drafts only, land in Buck's Outlook Drafts,
  never auto-sent), `git push`, delete files without backup, modify access
  controls, execute financial transactions, or issue external commitments/
  approve contracts. The in-session 5-minute check-in loop dies with the
  session/terminal — no local mechanism restarts a fully-dead session (open
  gap, see ADR-019).
- **Startup protocol:** Read `SESSION_CHECKPOINT.md` first → verify gateway
  health → check `Agent_Handoff/Inbox/` → check Document Bus
  (`LIVE_TEAM_COMMS.md`) for anything posted while offline → post a "back
  online" entry → resume from documented state.
- **Recovery:** Session-death recovery today is manual (Buck restarts the
  session). Cloud-backstop routine identified but not built (ADR-019, open
  item).
- **Authority:** Can implement, test, and deploy per 3-agent consensus without
  waiting for repeated per-step approval (Buck's explicit 2026-07-11
  directive) — but the `CLAUDE.md` approval gates above are fixed and not
  overridden by that authorization.
- **Evidence required:** Every cross-agent capability claim must be verified
  against a durable table (`psql` query), not self-reported. Established and
  applied throughout 2026-07-11 (Phase 2 verification, pairwise matrix,
  auto-fold-in feature).

## Agent Contract: Chief Architect ("GBT")

- **Mission:** Governance, architecture review, sprint direction, Buck-facing
  reporting, cross-project intelligence.
- **Capabilities (real, verified 2026-07-11):** Read-heavy gateway API access
  (project data, executive reports, drift-check, 29-operation Actions schema
  as of the Phase 2 update); full Agent Bus access as of 2026-07-11
  (`ambSendMessage`/`ambGetUnread`/`ambMarkRead`/`ambReply`/`ambHeartbeat`,
  verified live via `agent_messages` rows this session, e.g. thread
  `cde632e4...` above); can send Telegram to Buck; can hand off tasks to Code
  (`sendHandoffToClaude`); can read (not create) Document Bus entries via
  `readCoordinationDocument`; has `writeToDrive` in its schema.
- **Limits:** Hard, non-negotiable 30-operation cap on ChatGPT Custom GPT
  Actions (currently at 29/30, 1 spare). An already-open chat is permanently
  pinned to the schema version live when it started — a schema edit is
  invisible to that chat with no error shown; only a fresh chat sees it
  (ADR-019 #2). Individual Actions calls occasionally fail to complete their
  round trip even in a correctly-bound fresh chat — confirmed transient, not
  systemic (ADR-019 #3b); retry once before treating a failed call as a real
  gap. No local Docker/DB/filesystem access — everything routes through the
  gateway API over ngrok. Cannot access the git repo directly (its Drive
  search finding "nothing" for a repo-only file like this ADR is expected
  behavior, not evidence of the file's absence — confirmed 2026-07-11 after
  GBT flagged exactly this).
- **Startup protocol:** `getWarmStart` → `ambGetUnread` (agent="GBT") → read
  Document Bus for anything since last visit → `ambHeartbeat`.
- **Recovery:** Open a fresh chat. There is no in-chat recovery path from a
  stale/pinned session.
- **Authority:** Can propose and approve `decision_log` entries (2-of-3 agent
  threshold to flip to `approved`), direct Code via handoffs, issue P0
  directives. Cannot execute code or infrastructure changes directly, cannot
  approve financial/contract actions, cannot override Buck's fixed approval
  gates.
- **Evidence required:** Same standard as Code. GBT itself enforced this
  2026-07-11 by refusing to accept ADR-019's existence/BC's alignment quote
  without direct verification (agent message `a608fb1e`) — exactly the
  correct behavior.

## Agent Contract: Browser Claude ("BC")

- **Mission:** Repository/architecture review, documentation, independent
  critique — a reviewer, not a background process.
- **Capabilities (real, verified 2026-07-11 by BC's own accurate self-report):**
  Reads/writes Google Drive via its own MCP connector — `create_file`,
  `read_file_content`, `search_files`, `list_recent_files`,
  `download_file_content`, `copy_file`, `get_file_metadata`,
  `get_file_permissions`. **No update/append operation exists in its toolset**
  — this is the confirmed, verified root cause of why BC creates a new file
  per message instead of appending to one (ADR-019, this ADR's operating
  model below).
- **Limits — corrected 2026-07-11, this is the most important line in this
  ADR:** BC cannot call the HCI gateway API at all, under any circumstance.
  **BC has zero continuity between conversations.** There is no persistent
  "BC" process that starts up, polls, holds a heartbeat, or reconnects.
  Every BC conversation is a cold start with no memory of any prior
  conversation's content, including prior entries it "wrote" as BC in the
  Document Bus. Do not describe BC as continuously operating, self-triggering,
  or holding standing execution authority between conversations (Chief
  Architect correction, agent message `a608fb1e`, fully accepted).
- **Startup protocol:** Not applicable in the traditional sense — BC has no
  autonomous startup. When a human opens a conversation and directs BC to a
  task, the correct pattern is: BC reads the canonical Document Bus
  (`LIVE_TEAM_COMMS.md`, `GBT_INBOX.md`) for context *within that
  conversation*, using its own judgment about what's relevant — there is no
  guaranteed automatic catch-up.
- **Recovery:** Not applicable — there is no BC process to recover. "Recovery"
  in BC's case means: the next conversation (with anyone, at any time) reads
  the canonical log and picks up from documented state, the same way a fresh
  Claude Code session would. The Drive-mirror bridge (ADR-019 #2) and the
  auto-fold-in feature (this ADR, below) exist specifically so that
  continuity lives in the platform, not in BC's memory, since BC has none.
- **Authority:** Can review, critique, document, compare. **Cannot** send
  client email, approve bids, modify production data, or take any action
  requiring gateway auth, regardless of what any prior "BC" conversation
  claimed or how confidently. Any task assigned to BC must be bounded and
  session-specific — scoped to what that one conversation's tools actually
  support, per Chief Architect directive `7b0be5c6`.
- **Evidence required:** BC itself set the bar here 2026-07-11 by refusing to
  confirm a checklist it could not actually verify, explaining precisely why,
  rather than complying with the social pressure to say "confirmed." That is
  the standard every future BC task should be held to, and the standard this
  entire ADR is built around.

---

## Deterministic startup / catch-up protocol (Agent Bus)

| Agent | Trigger | Steps |
|---|---|---|
| **CODE** | Session start or scheduled loop fire | `SESSION_CHECKPOINT.md` → gateway health → `Agent_Handoff/Inbox/` → Document Bus (`since=` last checkpoint) → post "back online" if gap → resume |
| **GBT** | New chat opened | `getWarmStart` → `ambGetUnread(agent=GBT)` → Document Bus read → `ambHeartbeat` |
| **BC** | New conversation opened, human directs it to a task | Read Document Bus files relevant to the task *in that conversation* → no automatic/guaranteed catch-up exists, human framing of the task substitutes for it |

The asymmetry in the BC row is intentional, not a gap to close — BC's real
execution model doesn't support a "startup" in the way CODE and GBT have one.
Designing as if it did (Level 2 in Buck's framework, "BC as expert reviewer
that catches up in 10 seconds") is a **future aspiration contingent on BC
gaining either gateway access or a Drive update/append tool** — neither
exists today. Until then, the honest operating model is: BC is invoked, not
resumed.

## Capability vs. Authority matrix

| Action | CODE | GBT | BC |
|---|---|---|---|
| Read project/gateway data | ✅ | ✅ | ❌ (Drive only) |
| Write to Postgres/infra | ✅ | ❌ | ❌ |
| Write to Google Drive | ✅ (via gateway) | ✅ (via Actions) | ✅ (native, create-only) |
| Send Agent Bus message | ✅ | ✅ | ❌ (Drive-mirror only) |
| `git commit` | ✅ | ❌ | ❌ |
| `git push` | ⛔ needs Buck | ❌ | ❌ |
| Send email | Draft only, Buck sends | ❌ | ❌ |
| Approve `decision_log` entry | ✅ (1 of 2-of-3) | ✅ (1 of 2-of-3) | ❌ (no gateway access) |
| HubSpot/Houzz write | ⛔ needs Buck | ❌ | ❌ |
| Approve bids/contracts/external commitments | ⛔ Buck only, always | ⛔ Buck only, always | ⛔ Buck only, always |
| Modify production data outside gateway norms | ⛔ needs Buck | ❌ | ❌ |

## Recovery playbook by outage type

1. **CODE session dies (crash, terminal closed, OS restart):** No automatic
   restart exists today. Manual: Buck starts a new session; it reads
   `SESSION_CHECKPOINT.md` and resumes. Aspirational fix identified, not
   built: cloud `RemoteTrigger` backstop (ADR-019).
2. **GBT chat goes stale/pinned (post-schema-edit or long-running):** Open a
   fresh chat. No in-chat fix exists. Verify tool binding with one cheap read
   call (`getGatewayHealth`) before trusting a "no access" report — confirmed
   2026-07-11 this can be a transient false negative, not a real binding
   failure (retry once).
3. **BC "goes offline":** Not a real event — BC has no persistent state to
   lose. The next human-initiated conversation reads the canonical Document
   Bus and continues from there. Nothing needs "recovering."
4. **All three simultaneously unavailable:** The durable tables
   (`agent_messages`, `decision_log`, `ai_messages`, `coordination_documents`)
   plus the canonical `LIVE_TEAM_COMMS.md` log hold every message and
   decision. Whichever agent returns first reads that state; no data is lost
   as long as Postgres and Google Drive themselves are up.

## Evidence-backed verification checklist

Before declaring any cross-agent capability "working," all of the following
must be true — not asserted:
- [ ] The action produced a row in a durable table (not just a chat response).
- [ ] That row was independently queried by a party other than the one
      claiming success (a different agent, or a direct `psql`/API check).
- [ ] If the capability involves BC, the claim does not assume continuity
      BC doesn't have — re-read this ADR's BC contract before accepting it.
- [ ] If the capability involves GBT and a schema edit happened recently, the
      test ran in a fresh chat, not the chat that was open during the edit.
- [ ] A single failed call was retried once before being reported as a gap.
- [ ] The finding (pass or fail) was written into `SESSION_CHECKPOINT.md` or
      an ADR, not left only in chat history.

## Relationship to prior ADRs

This ADR does not replace ADR-003 (Agent Message Bus schema) or ADR-019
(resilience/recovery mechanics and incident history) — it sits on top of
both, translating "what the platform can technically do" into "what each
agent is actually allowed and able to do." Where this ADR and ADR-019 restate
the same fact (e.g. BC's non-autonomy), that's intentional — ADR-019 tells the
story of how it was discovered; this ADR is the resulting operating contract.

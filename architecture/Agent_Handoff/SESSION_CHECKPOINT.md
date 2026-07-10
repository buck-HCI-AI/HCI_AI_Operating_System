# SESSION_CHECKPOINT.md

Machine- and human-readable snapshot of "where things stand right now" — the
pick-up-where-left-off state GBT's restart-recovery spec asked for
(`GBT_HANDOFF_2026-07-10_PERMANENT_RULE__Self-healing_restart..._4a5ad80f.md`).

**Purpose:** if the current Claude Code session ends (planned OS update, crash,
context exhaustion) before a natural stopping point, whoever picks this up next —
a fresh Claude Code session, Buck, GBT, or BC — reads this file FIRST and knows
what was active, what's blocked, and what NOT to redo. This is distinct from
`LIVE_PROJECT_STATE.md`, which is a narrative history of what already shipped —
this file is only ever the *current* snapshot, overwritten each update, not
appended to.

**Update protocol:** Claude Code updates this at each Telegram/handoff check-in
cycle (currently ~270s during active work) and at any natural task boundary.
Always overwrite in full — this is current state, not a log.

---

## Last updated
2026-07-10, ~14:05 MT, by Claude Code

## Active mission
Restart/recovery system stabilization (Buck's explicit pre-departure priority,
selected via AskUserQuestion over Role Onboarding dry-run and open drift-check
findings). Infra self-heal layer shipped this cycle (ADR-018) — see below for
what's still open in GBT's fuller spec.

## Safe to resume automatically?
**Yes.** No irreversible action was mid-flight when this was last written. All
changes this cycle were local file edits (monitor.sh, a plist, docs) — already
committed to git (`150dcb5`). A fresh session can pick this file up and continue
straight to "Next action" below with no re-briefing needed.

## Pending approvals (awaiting Buck)
- None blocking right now. Buck was asked (via ntfy, 2026-07-10 ~14:01 MT)
  whether he wants GBT's fuller 8-point checkpoint/role-recovery spec built now
  vs. later — not blocking, work continues either way per standing "don't wait
  to be prompted" directive.

## Blocked items (not awaiting Buck, just genuinely blocked)
- External-drive Full Disk Access still not granted to Terminal (System Settings
  > Privacy & Security > Full Disk Access) — blocks reading/writing
  `/Volumes/HCI_AI_DEV ` and `~/Downloads` from shell tools. Not urgent — the
  external-drive storage migration is intentionally deferred, see ADR-018.
- 4 open drift-check findings, explicitly deprioritized by Buck in favor of
  restart/recovery this cycle: 2 failing n8n workflows (AUTO-004, AUTO-HANDOFF-PROCESSOR),
  23 unbacked bulk bid_packages on 275SS/574J (246GW-fabrication-shaped, unresolved),
  20 stale Houzz connector rows.
- Role Onboarding conversational flow (the actual walk-someone-through-activation
  sequence, dry-run on Buck per "test on me first") — built up through the
  `POST /gateway/users/onboard` endpoint, but the flow itself not yet built.

## Last-processed coordination state
- Last GBT handoff read from `architecture/Agent_Handoff/Inbox/`: none pending
  as of this checkpoint — most recent items already in `Processed/`.
- Last ntfy/Telegram send: 2026-07-10 ~14:01 MT, "Restart/recovery: infra layer
  done, evidence attached" (restart/recovery milestone report to hci-executive).
- Git HEAD: `150dcb5` ("Extend monitor.sh with ngrok/mcp-server checks + Docker
  self-heal; fix drive-watcher path bug"), branch `main`, uncommitted changes
  exist from earlier this session (gbt_gateway.py, microsoft_graph.py,
  bid_leveling_service.py, CLAUDE.md, rfi_workflow.py — untouched this cycle,
  not yet reviewed for a commit).

## Next action
Ask Buck (or, if genuinely no blocking issue and time permits, proceed
autonomously per Definition of Done) whether to build the remaining pieces of
GBT's 8-point restart-recovery spec: per-agent role recovery from canonical
config, a detect-diagnose-autocorrect-verify-record self-heal loop beyond the
current infra-only checks, a recovery-evidence manifest, and a controlled
restart drill. If proceeding: start with role recovery, since GBT/BC's "role"
is already defined in their own Project/GPT instructions docs (built in an
earlier session per `feedback_agent_handoff_must_survive_restart.md`) — the
gap is codifying that Claude Code itself reloads role/scope from this file +
CLAUDE.md at every session start, not from conversational memory alone.

## Known-good baseline (for the restart drill, when run)
- API: `curl http://localhost:8000/health` → 200
- Gateway (external, GBT's path in): `curl https://speculate-armband-retinal.ngrok-free.dev/gateway/health` → `service_count: 71`
- Docker: `hci_postgres`, `hci_redis`, `hci_minio`, `hci_qdrant`, `n8n` all `running`
- mcp-server: `curl http://localhost:8080/` → any HTTP response (404 is normal — means it's up)
- monitor.sh: `bash -n scripts/monitor.sh` passes; last live run 2026-07-10 14:00 MT, all 6 checks green, no alert

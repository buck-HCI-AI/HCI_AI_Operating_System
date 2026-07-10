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
2026-07-10, ~14:18 MT, by Claude Code — SHUTDOWN IN PROGRESS
Buck said "go ahead and shut down" then "I want to be sure the team comes back
on line and we pick up as this never happened." Shutdown triggered via
`osascript` at ~14:18 MT. THIS EXACT SESSION ENDS HERE. A fresh Claude Code
session must be started after reboot — it does not resume automatically. That
fresh session should read this file + CLAUDE.md's session-start sequence FIRST,
before anything else, per the wiring done earlier this cycle.

## Active mission
Restart/recovery ADR-018 + checkpoint file shipped and committed. Working tree
is now clean (git HEAD `2bf035a`) — all earlier-session verified work (Role
Onboarding endpoints, RFI workflow, bid-leveling/reply-draft fixes, processed
handoffs) committed as pre-shutdown housekeeping. Next active mission after
restart defaults to: Role Onboarding conversational flow dry-run on Buck
("test on me first") — picked as default since his "those 2 things are the
priority" message is still unclarified; asked him, not blocking on the answer.

## Test-data cleanup this cycle (per feedback_test_data_auto_delete, applied not just flagged)
Deleted on discovery, no approval wait needed per Buck's standing rule: "Jane PM"
leftover test row from platform_users; 5 void test RFIs + 1 test event from
1355R's real tables (genuine RFI 917 left untouched). Re-ran drift-check —
down to 4 real findings: 2 failing n8n workflows (AUTO-004, AUTO-HANDOFF-PROCESSOR),
23 unbacked bulk bid_packages on 275SS/574J (246GW-fabrication-shaped, unresolved,
queued pending Buck's priority call), 20 stale Houzz connector rows.

## Safe to resume automatically?
**Yes.** No irreversible action was mid-flight when this was last written. Git
working tree is fully clean at `2bf035a` — nothing uncommitted, nothing to lose.
A fresh session (or a post-reboot session) can pick this file up and continue
straight to "Next action" below with no re-briefing needed.

## Pre-shutdown readiness (Buck asked to be told when ready — this is that answer)
**Ready.** Verified live at 2:11 PM MT, all green:
- API: HTTP 200 (`localhost:8000/health`)
- Gateway (GBT's external path in): reachable, 71 services (`.../gateway/health`)
- ngrok tunnel: HTTP 200 (`localhost:4040/api/tunnels`)
- mcp-server: responding (`localhost:8080/`)
- Docker: `hci_postgres`, `hci_redis`, `hci_minio`, `hci_qdrant`, `n8n` all `running`
- Disk: 2% used, no pressure
- `monitor.sh`: syntax-clean, extended this session with ngrok/mcp-server/Docker
  self-heal (ADR-018)
- Git: working tree clean, `2bf035a`

**What auto-recovers after the OS update reboot, and why it's expected to work:**
launchd `KeepAlive:true` on api-server/mcp-server (standard macOS mechanism,
survives reboot by design) + Docker Desktop as a login item + all 5 containers
on `restart:unless-stopped` (standard Docker mechanism) + `monitor.sh` running
every 5 min via `RunAtLoad:true` catching anything those miss (now including
ngrok, which was the one real gap closed this session).

**Honest caveat:** this reasoning has NOT been verified with an actual live
restart drill in this session — GBT's spec explicitly calls for one
(restart-drill item, still open) and none has been run. The mechanisms above
are standard, well-understood OS/Docker behavior, not experimental code, so
confidence is reasonably high — but "should auto-recover" is not the same
as "drilled and confirmed." If Buck wants zero risk, the honest ask is either
he do the update now while a monitor session can watch it come back, or accept
this as reasoned-but-undrilled confidence.

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
- Telegram: acked through message_id 1465 (2026-07-10 1:21 PM MT) via
  `POST /gateway/telegram/ack`. Replied asking Buck to clarify "those 2 things
  are the priority" (1463, 1:05 PM MT) — genuinely ambiguous, don't guess.
  Also addressed 1464 (no visible Code/GBT book-vetting coms) — pointed to the
  last confirmed Operating Book audit (CH01-07, complete, no gaps).
- Applied Buck's new standing rule (2026-07-10): sign shared-channel messages
  by agent name ("Code:"/"GBT:"/"BC:") — see [[feedback_agent_identity_signing]].
- Last GBT handoff read from `architecture/Agent_Handoff/Inbox/`: none pending
  as of this checkpoint — most recent items already in `Processed/`.
- Last ntfy/Telegram send: 2026-07-10 ~2:25 PM MT, identity-signed reply re:
  the 3 Telegram messages above.
- Git HEAD: `51922b0` (adds SESSION_CHECKPOINT.md, commits pending 10-min
  alerting rule), branch `main`. Prior commit `150dcb5` = monitor.sh + drive-
  watcher fix. Older uncommitted changes still sitting in the working tree
  from earlier this session (gbt_gateway.py, microsoft_graph.py,
  bid_leveling_service.py, rfi_workflow.py) — untouched this cycle, not yet
  reviewed for a commit.

## Next action (for the fresh session that picks this up post-reboot)
1. Run the pre-shutdown readiness checklist IN REVERSE — verify API/gateway/
   ngrok/mcp-server/all 5 Docker containers actually came back up clean. This
   IS the restart drill GBT's spec asked for and none has been run yet — this
   is the first real one, do it deliberately and record the result (append a
   "post-restart verification" section to this file with what came back clean
   vs. what needed manual intervention).
2. Report the verification result to Buck via Telegram BEFORE anything else —
   he explicitly asked to be sure "the team comes back on line and we pick up
   as this never happened." Be honest: infra (API/DB/ngrok/mcp-server) should
   auto-recover per ADR-018 with no action from him; GBT is an external
   ChatGPT service unaffected by this machine's reboot except brief gateway
   unreachability, resumes automatically; BC (browser-based on this same Mac)
   will need its browser/extension re-established, not fully automatic; this
   Claude Code session itself does NOT auto-resume — a fresh session has to be
   started, which is what's reading this file right now.
3. Once verified, default active mission resumes: Role Onboarding conversational
   flow dry-run on Buck ("test on me first"). If Buck answered "those 2 things
   are the priority" in the interim, that takes precedence.
4. Still open, unblocked, deliberately paused not abandoned: remaining pieces
   of GBT's 8-point restart-recovery spec (per-agent role recovery from
   canonical config, a broader self-heal loop, a recovery-evidence manifest) —
   per [[feedback_route_tradeoffs_through_3agent_review]], loop in GBT/BC
   before building further on this, don't solo it.

## Known-good baseline (for the restart drill, when run)
- API: `curl http://localhost:8000/health` → 200
- Gateway (external, GBT's path in): `curl https://speculate-armband-retinal.ngrok-free.dev/gateway/health` → `service_count: 71`
- Docker: `hci_postgres`, `hci_redis`, `hci_minio`, `hci_qdrant`, `n8n` all `running`
- mcp-server: `curl http://localhost:8080/` → any HTTP response (404 is normal — means it's up)
- monitor.sh: `bash -n scripts/monitor.sh` passes; last live run 2026-07-10 14:00 MT, all 6 checks green, no alert

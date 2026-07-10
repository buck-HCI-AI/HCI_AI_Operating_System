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
2026-07-10, ~15:03 MT, by Claude Code — TWO RBAC GAPS CLOSED, TEAM MOSTLY RECONNECTED

## RBAC gaps closed (2026-07-10 ~15:00 MT, authorized directly by Buck: "go ahead and fix both gaps")
1. **is_onboarded server-side enforcement** — `run_rfi_workflow()` previously
   passed `to_email` straight through with zero awareness of `is_onboarded`,
   despite a docstring elsewhere claiming it gated on it. Added
   `_resolve_recipient_gate()` in `services/rfi_workflow.py`: redirects to
   Buck only when `to_email` matches a known internal `platform_users` row
   that isn't onboarded yet. External RFI recipients (architects/subs, not in
   `platform_users`) pass through unaffected — same as before.
2. **Self-BCC** — `create_draft()` in `integrations/microsoft_graph.py`
   gained `bcc` support; `create_rfi_email_draft()` now BCCs Buck whenever
   the resolved recipient isn't Buck himself.
Verified end-to-end against real RFI 917 with the Graph call intercepted (no
live draft created): unonboarded-recipient case redirects with no redundant
self-BCC; external-recipient case passes through with BCC set correctly.
Committed `bdee17d`. Reported to Buck via Telegram.

## Team reconnection status (checked 2026-07-10 ~14:50-15:00 MT)
- **BC (Browser Claude): alive and active.** Posted a full post-restart audit
  + a 6-step onboarding-test spec to the AI Team Document Bus at 14:50 MT —
  agrees restart was clean, no new systemic problems. Both BC's audit and
  Claude Code's independent one concur.
- **GBT: still unreachable.** Stuck at Telegram `last_ack_id=1453`, 15-message
  backlog, unchanged since before the reboot — consistent with BC's diagnosis
  (session/token issue, not a gateway problem; gateway itself serves 71
  services fine). Cannot be forced to reconnect from here — needs Buck to
  open a fresh GBT chat (reliable known fix, see
  [[project_gbt_reseed_success_2026-07-10]]).
- Filed the **Capability Verification Before Action** permanent rule both BC
  and GBT explicitly asked for, into `CLAUDE.md` (commit `4fd5e91`).
- **New, unresolved: Google Drive WRITE is down.** 4 consecutive failures,
  including a trivial 1-word test file (`create_file` → "Internal error
  encountered" every time). Reads still work (`search_files` fine). This
  blocked posting the findings doc to the shared Document Bus for BC/GBT to
  see — sent everything to Buck via Telegram instead. Stopped retrying after
  4 attempts rather than loop on it per the Capability Verification rule just
  filed — needs either time to recover on its own or Buck's investigation.
  Re-check with a trivial `create_file` call before assuming it's back.

## Post-restart verification (2026-07-10 ~14:44 MT — first real drill, GBT's spec item now closed)
Machine rebooted for OS update as planned. Fresh Claude Code session started
when Buck dropped a `Start up.docx` in Downloads after also messaging Telegram
"you there... dont seem to be responding" (1467, sent 14:32 MT, 15 min before
this session picked it up — first response lag to close going forward).
Verified clean:
- API `localhost:8000/health` → 200
- Gateway (GBT's path in) → reachable, 71 services
- ngrok tunnel → healthy, same static URL
- mcp-server → HTTP 404 (normal/up)
- Docker: `hci_postgres`/`hci_redis`/`hci_minio`/`hci_qdrant`/`n8n` → all healthy, up since reboot
- `monitor.sh` (real path: `03_Source_Code/scripts/monitor.sh`, not `scripts/monitor.sh`
  as previously written here — corrected) → ran automatically post-reboot at 14:42 MT
  via launchd, all 6 checks green, LastExitStatus 0
- **Known non-blocking issue, not a regression:** `com.hci.drive-watcher` errors
  (`/Volumes/HCI_AI_DEV/03_MinIO_Data missing`) — expected, external-drive Full
  Disk Access still not granted, Docker containers start fine independently of
  it, migration is intentionally deferred per ADR-018.
Reported to Buck via Telegram (1468) immediately after verification, per his
explicit "be sure the team comes back on line" ask. ADR-018's self-heal
mechanisms (launchd KeepAlive, Docker restart:unless-stopped, monitor.sh
RunAtLoad) are now drilled-and-confirmed, not just reasoned-about.

## Active mission
Resumed Role Onboarding "test on me first" dry-run per prior checkpoint's
default. Backend confirmed done: `platform_users` row for Buck already shows
`is_onboarded=true`, `onboarded_at` 2026-07-10 1:37 PM MT (raw DB value is
19:37:07 UTC — corrected here 15:xx MT after Buck caught it stated wrong as
"19:37 MT" earlier this cycle; see [[feedback_timezone_mountain_not_utc]])
(flipped via
`POST /gateway/users/onboard` in the pre-shutdown session). No dedicated
"hats" DB table exists — hat-switching (Executive vs PM/Super) is conversational
logic inside Field GPT, confirmed live-tested per
[[project_build1_complete_2026-07-10]], not a gap.
**Open fork, sent to Buck 14:47 MT, awaiting his answer (not blocking other work):**
GBT relayed a screenshot at 20:35 MT showing a stuck/idle `claude.ai` browser
tab titled "Launching Your AI Onboarding Tool" (spinner in composer). This is
almost certainly a separate Browser-Claude (BC) session Buck opened for the
interactive walkthrough, not this CLI session — Claude Code cannot see or
drive that tab. Also ties into the still-open
[[project_possible_concurrent_browser_automation_collision_2026-07-10]]
question (native Claude side panel driving the same browser) — asked Buck
whether the stuck tab is safe to just close/retry, or whether he wants
Claude Code to use browser tools to go look (which would also resolve the
collision question). Do not touch browser automation until he answers.

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
- None blocking. Buck's 2026-07-10 ~14:58 MT message ("do not ask - just go -
  you have full auth - for decisions it's the 3 team agree - if only 2 agree
  it gets escalated to me") supersedes the earlier ask-first posture — the
  stuck-tab question is deprioritized, not answered; not reraising it unless
  it blocks something concrete.
- Carried over, still genuinely unanswered (not urgent): whether he wants
  GBT's fuller 8-point checkpoint/role-recovery spec built now vs. later.

## Blocked items (not awaiting Buck, just genuinely blocked)
- **Google Drive WRITE down** (new, ~14:52 MT) — 4 consecutive `create_file`
  failures ("Internal error encountered"), including a trivial 1-word test
  file. Reads (`search_files`) still work. Blocked posting the RBAC-fix
  status doc to the shared Document Bus for BC/GBT — sent to Buck via
  Telegram instead. Stopped retrying after 4 attempts per the Capability
  Verification rule. Re-check with a trivial `create_file` call, don't assume
  fixed.
- External-drive Full Disk Access still not granted to Terminal (System Settings
  > Privacy & Security > Full Disk Access) — blocks reading/writing
  `/Volumes/HCI_AI_DEV ` and `~/Downloads` from shell tools. Not urgent — the
  external-drive storage migration is intentionally deferred, see ADR-018.
- 4 open drift-check findings, explicitly deprioritized by Buck in favor of
  restart/recovery this cycle: 2 failing n8n workflows (AUTO-004, AUTO-HANDOFF-PROCESSOR),
  23 unbacked bulk bid_packages on 275SS/574J (246GW-fabrication-shaped, unresolved),
  20 stale Houzz connector rows.
- GBT unreachable (session/token issue) — see Team reconnection status above;
  needs Buck to open a fresh chat, not fixable from Claude Code.

## Last-processed coordination state
- Telegram: acked through message_id 1468 ("go get everything back and
  tested... book, onboarding and the 100/100 agreement", 14:52 MT) via
  `POST /gateway/telegram/ack`. Sent 3 replies this cycle (~14:45-15:03 MT),
  all identity-signed "Code:": post-restart verification result, RBAC
  discovery + stuck-tab question, and the two-gaps-fixed confirmation.
- Read HCI AI Master message drop (BC Message Drop doc) in full — nothing new
  beyond already-tracked items (GBT capability-loss self-report, already in
  [[project_gbt_stale_session_tool_loss_recurring_2026-07-10]]).
- Read BC's `BC_TO_TEAM_POST_RESTART_CHECK_ONBOARDING_TEST_GO_2026-07-10.md`
  from the Document Bus (posted 14:50 MT) — 6-step onboarding-test spec,
  used directly to scope the two gap-fixes above.
- Processed 2 GBT handoffs this cycle: the "Buck reports problem with Code"
  one and "Post-restart team stabilization and regression audit" — both
  moved to `Processed/`, both logged in `HANDOFF_INDEX.md`.
- Git HEAD at session start: `9a22d21` (final pre-shutdown checkpoint) — one
  commit ahead of what this file previously said (`51922b0`), branch `main`.
  Working tree had 2 modified files (HANDOFF_INDEX.md, STRATEGIC_BACKLOG.md,
  both routine handoff-processing edits already reflected in this checkpoint)
  plus the 1 new Processed handoff file above — committing as routine
  housekeeping this cycle.

## Next action
1. Awaiting Buck's answer on the stuck-tab question above.
2. Once answered: continue the Role Onboarding "test on me first" dry-run —
   next real gap is the actual conversational walkthrough Buck experiences
   when a new user hits Field GPT for the first time post-onboard, not just
   the backend flag flip (already done).
3. If Buck answers "those 2 things are the priority" (still unclarified from
   earlier today), that takes precedence over the above.
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
- monitor.sh: `bash -n 03_Source_Code/scripts/monitor.sh` passes (real path — not
  `scripts/monitor.sh`); confirmed auto-runs post-reboot via launchd `RunAtLoad`,
  last live run 2026-07-10 14:42 MT, all 6 checks green, no alert — restart
  drill passed

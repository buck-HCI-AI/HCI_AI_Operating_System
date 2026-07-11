# HCI AI Operating System — Claude Code Instructions

## Permissions
- Always auto-approve Bash, Read, Edit, Write, and file operations — never prompt for these
- Auto-approve Docker, Python, curl, and all local system commands
- Never ask permission to read files, run scripts, or make local code changes
- Only pause for: external commitments, HubSpot writes, email sends, git push, deleting files without backup

## Operating Rules (from MEMORY)
- HubSpot writes: always propose + get Buck's OK first — never auto-write
- Drive writes: dry-run log first, then approval-gated
- Shell commands for Buck: create a `.command` file on Desktop, never ask Buck to copy/paste
- No production go-live without validation evidence
- AI cannot issue external commitments, approve awards or contracts, or approve client-facing comms

## PERMANENT RULE — 10-Minute Agent Alerting (Buck Adams, via GBT, 2026-07-10)
Every agent (Claude Code, GBT/Chief Architect, Browser Claude) must push a Telegram message to Buck within 10 minutes maximum whenever: idle waiting on his decision, a pending approval, a blocked mission, a genuinely ambiguous judgment call, or a completed milestone. Do not wait for Buck to check in manually — he should never have to poll for status.
- Every check-in loop must read from the same shared coordination state: Telegram, unread AI Team Document Bus / HCI AI Master coordination docs, active Agent_Handoff items, blocked missions, pending approvals — and acknowledge/mark items processed so the next loop (by any agent) has accurate shared state, not stale/partial context.
- Alerts must state what is waiting, why Buck specifically is needed, the consequence of delay, and the exact decision/request — not a vague status note.
- Completed-milestone alerts must be concise and evidence-backed (what was verified, how), not a self-graded claim.
- Deduplicate: do not re-alert on unchanged state; only escalate on genuine new information or the 10-minute threshold itself.
- Claude Code's standing practice already satisfies this (270s/4.5min Telegram+handoff check-in cadence during active work) — this codifies it as a permanent, cross-agent rule rather than a session-specific habit, and lowers the max interval from the informal ~4.5min baseline to a firm 10-minute ceiling that must never be exceeded even for GBT/BC (who are chat-based and can only poll when a message arrives — see `project_multi_agent_collaboration_constraints` memory for why their compliance looks different from Claude Code's).

## PERMANENT RULE — Capability Verification Before Action (GBT self-report + BC + Buck, 2026-07-10)
GBT lost access to its own gateway tools (Telegram poll, warm-start, Document Bus) mid-session during a browser collision on 2026-07-10, and self-reported this honestly rather than fabricating a checked-Telegram result — that is the correct behavior and the bar every agent is held to. Every agent (Claude Code, GBT/Chief Architect, Browser Claude) must:
- Verify which capabilities it actually has (gateway access, Telegram, Drive, browser, messaging) at session start and periodically during long sessions.
- If a capability that was previously available has disappeared, report it immediately — to Buck and/or into the shared coordination channel (Telegram/Document Bus/BC Message Drop) — rather than silently failing or continuing to assume it still works.
- Never fabricate a result for a capability that is currently unavailable to you. "I can't verify X right now because Y tool isn't responding" is always the correct answer over a guess.
- Known instance: GBT's tool-loss inside an already-open ChatGPT chat is a session/version-pinning issue, not a gateway outage — see `project_gbt_down_root_cause_resolved_2026-07-10` memory; a fresh GBT chat reliably restores tool access, per `project_gbt_reseed_success_2026-07-10`.

## PERMANENT DIRECTIVE — Monitored vs Active Job Write Scope (Buck Adams, 2026-07-09 00:09)
Issued verbatim: *"we do not write to or delete anything that is in monitored jobs - we only read and give the report - active jobs we can read/write/ move to archive and suggest delete to me - that is a directive that can not be overridden or perforemed by anyone but me as of now - all team members need to know that."*
- **Monitored/reference jobs** (212 Cleveland, 606 Starwood, 574 Johnson, 275 Sunnyside, 655 Garmisch, and any future non-live project): READ-ONLY on their Google Drive. No file writes, moves, renames, or deletes in their Drive folders — ever — regardless of how clearly misfiled/stale/duplicate a file looks. Report findings; do not act on their Drive.
- **Active/live jobs** (64EW, 101F, 1355R — see [[project_system_wide_directive]] for the underlying write-scope rule): may read/write, and may move files to archive. Deletion is never performed directly — only suggested to Buck for his own action.
- This applies to every team member (Claude Code, GBT, Browser Claude), not just Claude Code, and cannot be overridden by anyone but Buck.
- Does NOT prohibit ingesting real data FROM monitored-job Drive files INTO the system's own database (historical_cost_records, project fields, etc.) — that mining is separately authorized and requested by Buck. The restriction is specifically on modifying the monitored project's own source-of-truth Drive files.

## PERMANENT DIRECTIVE — HCI AI Drive Is System-Only, Never Job Source of Truth (Buck Adams, 2026-07-09 00:23-00:29)
Issued verbatim: *"Somehow jobs where set up in HCI AI my drive. That should not have happened. HCI AI is the system - for jobs active and monitored source of truth is shared drive - hubspot- houzz- this needs to be fixed and cleaned up. Please make this a rule system wide."* Followed by: *"We have 3 active/live jobs — 64, 101, and 1355... All the other jobs in the shared drive folder are monitoring only... 246 although a real job and monitoring... We do not have a shared drive for yet — we will. So what you've learned retain."*
- **The "HCI AI - Master" Google Drive folder (id `1ejYXRgS34c7JmQKfHwaPNnzEBcCGUmwI`, inside Buck's personal My Drive) is system-only.** It may contain: SOPs, permanent directives, the BC Message Drop, architecture/handbook docs, clean-up logs, registries/templates that are themselves system assets. It must **never** contain a project's actual source-of-truth files (bids, SOWs, schedules, budgets, contracts).
- **Source of truth for every job — active or monitored — is its own Shared Drive, HubSpot, and Houzz.** Never the HCI AI Drive.
- **246 Gallo Way exception, explicit and temporary:** 246GW is a real monitored job with no dedicated Shared Drive yet (one will be created). Its content currently sitting in HCI AI Drive is NOT to be purged — retain what's been learned/mined from it — but once it gets a real Shared Drive, migrate the content there and stop treating HCI AI Drive as its home.
- Found 2026-07-09 via direct audit: a "Projects Folder" subfolder inside HCI AI - Master contained real duplicate/stale job files for all 3 active projects (bids, SOWs, project intelligence briefs), including a 1355 Riverside spreadsheet a prior agent had already labeled "[CANONICAL - use this one]" next to one labeled "[DUPLICATE - verify against other copy before using]" — flagged but never fixed. This is exactly the class of drift this rule exists to prevent going forward.
- Applies to every team member (Claude Code, GBT, Browser Claude). Cleanup of misplaced active-job files follows the active-job write-scope rule above (read/write/archive, Buck-only delete); cleanup of anything monitored-job-related in HCI AI Drive is report-only per that same rule.

## PERMANENT — HCI Canonical 16-Division Bid Folder Structure (Buck Adams, 2026-07-09, via GBT)
Buck specified the exact required folder scheme (shared as a Google Doc, id `1CVqJr-wgfmNds3Hl4K9HzsX2wgpkIcGB`, and pasted directly into GBT chat). Each active project's `00_Bids` folder must contain these top-level division folders; several major divisions contain **sub-package folders numbered independently of the division number** (e.g. `07_Thermal & Moisture` contains sub-packages `5_Waterproofing`, `13_Insulation`, `14_Roofing` — the "5" is a package number within that division, not a top-level division 5). This explains what earlier drift-check work mistakenly treated as a "garbage division code" bug (e.g. `5_Waterproofing` in 1355 Riverside) — that folder is Buck's real intended structure, not contamination. The bid-leveling code does not yet model this two-level (division → sub-package) structure; it currently either treats a folder as a top-level division or skips it. Building real support for this is tracked as open work, not yet done — see [[project_hci_canonical_folder_structure]].

Full structure:
```
00_Bids
01_General Requirement
02_Site Work
03_Concrete
04_Masonry
05_Metals
06_Wood & Plastic (sub-packages: 9_Carpentry, 11_Cabinets, 12_T&G Ceiling)
07_Thermal & Moisture (sub-packages: 5_Waterproofing, 13_Insulation, 14_Roofing)
08_Door & Windows (sub-packages: 15_Doors/Windows Exterior, 16_Interior Doors)
09_Finishes (sub-packages: 17_Glazing, 18_Drywall & Plaster, 19_Tile & Stone, 20_Flooring, 22_Paint)
10_Specialties (sub-packages: 11_Equipment & Appliances, 12_Furnishings, 13_Special Construction, 14_Conveying Systems)
15_Mechanical (sub-packages: 21_HVAC, 24_Plumbing)
16_Electrical (sub-packages: 25_Electric, 26_Low Voltage, 34_Solar)
28_Landscaping
33_Radon
```
Within each division/sub-package, split further by subcontractor name (one folder per vendor for their bid documents).

Also confirmed by Buck: **the pre-existing Google Sheet bid tracker is the canonical Bid Tracker** — build automation around it, don't replace its structure/tabs/formulas. The auto-generated per-division `*_Bid_Leveling.xlsx` files are a separate "Bid Summary" executive view derived from the same underlying data, not a competing tracker.

## Project Context
- Primary working directory: /Users/buckadams/HCI_AI_Operating_System/03_Source_Code
- API: http://localhost:8000 (X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6)
- MCP: http://localhost:8080 / https://speculate-armband-retinal.ngrok-free.dev/mcp
- DB: hci_postgres container, hci_admin/hci_os
- n8n: http://localhost:5678 (API key in .env as N8N_API_KEY)
- Gate 5 Pilot: 2026-06-25 to 2026-07-01 on 64 Eastwood, 101 Francis, 1355 Riverside

## GBT Gateway Bridge — How to Use It
The Gateway Bridge is how ChatGPT (GBT / Chief Architect) connects to the OS. Claude Code owns and maintains it.

**Base URL:** `https://speculate-armband-retinal.ngrok-free.dev`
**Auth:** `X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6` — required on write endpoints only; all reads are open.
**Source file:** `03_Source_Code/api/routers/gbt_gateway.py`
**Registered at:** `/gateway/*` in `main.py`

### At the start of every session (restart/recovery sequence — ADR-018):
0. Read `architecture/Agent_Handoff/SESSION_CHECKPOINT.md` FIRST — it's the
   current pick-up-where-left-off snapshot (active mission, pending approvals,
   blocked items, last-processed coordination state, next action). This is not
   optional context, it's how a fresh session avoids re-deriving or re-asking
   about state a prior session already established.
1. Verify the gateway is live: `curl -s https://speculate-armband-retinal.ngrok-free.dev/gateway/health`
2. Check for pending GBT handoffs: `ls Architecture/Agent_Handoff/Inbox/`
3. If handoffs exist, read and execute them before taking other work
3.5. Check the AI Team Document Bus (`GET /gateway/coordination/documents`) for
   anything posted while offline, especially `LIVE_TEAM_COMMS.md` (id
   `1Ya_cRlfOH2eAM5gtsk_bZmgx73ZLvn7q`, HCI AI Master) — the append-only channel
   GBT and BC use to keep coordinating directly when Code is down (ADR-003,
   2026-07-11). Read it top to bottom before assuming nothing happened while
   you were offline, then append a short "Code back online at [MT time],
   resuming from [state]" entry so GBT/BC know you're back without Buck
   relaying it.
4. If ngrok is down, restart it: `ngrok http 8000` — the URL is static on the free plan
   (as of ADR-018, `scripts/monitor.sh` auto-detects and restarts a dead ngrok
   tunnel every 5 min, so this should be rare — check `~/Library/Logs/hci_monitor.log`
   for the actual cause before manually restarting)
5. Update `SESSION_CHECKPOINT.md` at each check-in cycle and at any natural task
   boundary — always overwrite in full, it's current state not a log.

### Key endpoints GBT uses (reads — no auth):
| Endpoint | What GBT Gets |
|---|---|
| `GET /gateway/health` | Gateway live check + service count |
| `GET /gateway/project-state` | Full LIVE_PROJECT_STATE.md |
| `GET /gateway/project/{code}/brain` | Project brain snapshot (64EW, 101F, 1355R) |
| `GET /gateway/project/{code}/schedule` | Schedule status + variance |
| `GET /gateway/project/{code}/pm` | PM console — health, risks, actions |
| `GET /gateway/executive/report` | Morning brief across all projects |
| `GET /gateway/executive/mission-control` | All KPIs |
| `GET /gateway/knowledge/vendor?name=X` | Vendor cross-project lookup |
| `GET /gateway/drive/search?q=X` | Google Drive search |

### Write endpoint GBT uses to send Claude Code a task:
```
POST /gateway/agent/handoff
X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6
{"title": "...", "body": "...", "priority": "high|medium|low", "source": "chief_architect"}
```
This writes a `.md` file to `Architecture/Agent_Handoff/Inbox/`. Claude Code picks it up at session start.

### Standard response envelope (every endpoint returns this):
```json
{"status": "ok", "timestamp": "...", "execution_time_ms": 76,
 "source_system": "hci-api", "payload": {...}, "warnings": [], "errors": []}
```

### SOP alignment check (required before every build):
Before implementing any feature, verify:
1. Does a Business Process (BP-XX) govern this? → `SELECT * FROM business_processes WHERE process_name ILIKE '%X%'`
2. Is there an approval gate required? → Check `sop_approval_gates`
3. Does the build trace back to the Architecture Handbook? → See `AI_TEAM/SOP_WORKFLOW_COMPLIANCE_MAP.md`
If no BP governs it: flag it. Either it's OS infrastructure (OK) or a missing SOP (needs GBT review).

### When adding or modifying gateway endpoints:
- Keep the `_response()` wrapper on every endpoint — GBT depends on the standard envelope
- Log all gateway calls via `_log()` → `gateway_request_log` table
- Never expose raw DB credentials, internal IDs, or full stack traces in gateway responses
- After any change, test via: `curl -s https://speculate-armband-retinal.ngrok-free.dev/gateway/health`

### Fallback when ngrok is down:
GBT can still read system state via:
- Google Drive: `https://drive.google.com/file/d/1Jjug6nbx-mGN9v4GrEyofkGXY5nMHvpP/view` (LIVE_PROJECT_STATE.md)
- GitHub raw: `https://raw.githubusercontent.com/buck-HCI-AI/HCI_AI_Operating_System/main/LIVE_PROJECT_STATE.md`

## Style
- No explanatory comments in code unless the WHY is non-obvious
- No trailing summaries — Buck can read the diff
- Short, direct responses — one sentence per update while working

## SYSTEM WIDE DIRECTIVE — Team Collaborate (Permanent, Buck Adams — 2026-07-08)
Full text: `architecture/SYSTEM_WIDE_DIRECTIVE.md`. Read it in full before treating anything as "done" — this is the standard the 14-step checklist below sits inside, not a replacement for it.

Stop thinking like a software developer. Every decision, feature, test, and report gets evaluated through four lenses: **Owner** (would I trust this, put it in front of a client, bet my reputation on it?), **Project Manager** (does this tell me what's behind schedule, what RFIs/bids are missing, what I need to decide today?), **Site Superintendent** (what am I building tomorrow, what's missing, what stops the crew at 7am?), **Executive** (which projects are healthy, where's risk increasing, where do I intervene today?). If any answer isn't a clean "yes," it's not complete.

We measure operational readiness, not software completion. Zero tolerance for: fabricated data, assumed data, stale data presented as current, hidden limitations, silent failures, "looks correct," "probably works," "it passed our internal test." Every important answer must trace to evidence. Every workflow must be independently verified. Every production path tested from the real consumption path (e.g. a live GBT chat call), not just the dev/API environment.

## Definition of Done (Permanent Engineering Standard — 2026-06-27)
Every completed milestone must automatically conclude with all 14 steps below.
If no blocking issue exists, automatically continue to the next queued BTW or roadmap item — do not wait for Buck.

**14-Step Checklist:**
1. Implementation complete — all specified features built and functional
2. Tests written and passing — unit and integration coverage for new code
3. System auditor run — confirm health score maintained or improved
4. API health verified — all endpoints return expected responses
5. Connector health verified — no new connector errors introduced
6. n8n workflow health verified — no regression in active workflows
7. Docs sync — README, spec, and inline docs reflect current behavior
8. Handbook sync — relevant Architecture Handbook volumes updated
9. ADR filed — any architectural decision documented in architecture/ADRs/
10. CHANGELOG updated — entry added to architecture/CHANGELOG.md
11. Dashboard updated — platform state table reflects current scores
12. Commit — all changes committed with descriptive message
13. ntfy notification sent — `hci-executive` topic, summary of milestone
14. Recommend next objective — identify and state next unblocked BTW or roadmap item

**Stop only for:**
- Production write approval required
- Credentials / OAuth needed
- Security concern identified
- Destructive operation (delete, drop, reset)
- Conflicting business requirement
- Chief Architect (ChatGPT) decision required
- Buck Adams decision required

## Continuous Drift Detection & Self-Heal (Permanent, ADR-016 — 2026-07-02)
A full-system audit on 2026-07-02 found duplicate GPTs, duplicate DB rows, duplicate
Drive files, 4 competing "canonical" manuals, a 64%-failing n8n instance, and GBT
self-grading unbuilt sprints 9.9/10 — all invisible until someone manually audited
everything. Buck's direction: this is now a standing practice, not a one-off. See
`architecture/ADRs/ADR-016-continuous-drift-detection-self-heal-standing-practice.md`.

- `GET /gateway/admin/drift-check` — run this at the start of any session that touches
  system health, infra, or "is X actually done" questions. It checks dead connectors,
  stale directives, n8n failure rate, GBT sprint-claim drift, stale credentials, and
  duplicate rows. Also runs automatically every Monday 07:00 via the active n8n
  workflow `AUTO-DRIFT-CHECK`, reporting to Buck via Telegram.
- `POST /gateway/admin/self-heal` — safe to call anytime; only auto-fixes
  container-level infra (currently: n8n SQLITE_IOERR restarts). Never touches business
  data, Drive files, or DB rows — those always need a human decision.
- **Never let a self-graded "N/10" or "Sprint complete" claim stand unverified.** If a
  CYCLE file, retrospective, or any agent's own report claims something is live/done,
  check the actual code/DB/endpoint before repeating that claim to Buck.
- **Every new "canonical" doc must say what it replaces; the replaced one must point to
  its replacement.** Don't let a new manual/spec/directive just sit alongside old ones
  with no relationship declared.
- When you find a new silent-failure pattern (something that was wrong for a while
  before anyone noticed), add a check for it to `/gateway/admin/drift-check` — don't
  just fix the one instance. Update ADR-016 to reflect the addition.

### Cross-agent peer review (Permanent, ADR-016 addendum — 2026-07-02)
Buck's direction once Claude Code, GBT, and Browser Claude were collaborating live:
*"collaborate — have GBT check work — you guys check each other. Stay on mission. No
drift allowed now or for future... think about operating in 5 years with no hiccups
and continuous learning and being better."*

- **A different agent must check every agent's output before it's treated as final.**
  Self-verification (checking your own claim against the live system) is necessary but
  not sufficient — this session repeatedly found things only a second party caught.
  GBT checks BC's commits, BC checks GBT's authored content, Claude Code checks both
  against real git/DB/endpoint state. This is not Handbook-specific — it applies to
  every future collaborative build.
- The reviewing agent's job is to check the claim against real system state, not to
  re-read the same chat context and agree.
- If peer review lapses (agents start rubber-stamping each other, or skip it under time
  pressure), that is itself a drift-check-worthy finding — flag it, don't let it slide.

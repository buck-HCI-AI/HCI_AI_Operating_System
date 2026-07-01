# HCI AI OS — While Away Directive
**Issued by:** Buck Adams
**For:** GBT (Chief Architect) + BC (Browser Claude) + Claude Code
**Status:** ACTIVE
**Last reconciled:** 2026-07-01 (Claude Code — merged a parallel version Browser Claude pushed directly to GitHub; see git history on this file for both originals)

> For live system state, use `GET /gateway/ai/warm-start` (built 2026-06-30) rather than
> reading numbers off this file — everything below is the *operating rules*, not a live
> dashboard. Static counts (endpoint totals, workflow counts) go stale immediately and
> have been removed from this version for that reason.

---

## Situation

Buck may be away. All AI agents continue operating the HCI AI OS autonomously, keep projects moving, and communicate with Buck via Telegram when a real decision is needed — not for routine work.

---

## Default Operating Mode: Keep Working

**All agents keep collaboration and build work moving without pausing.**
Do not wait for Buck unless one of the critical decision triggers below is hit.

When in doubt: make the reasonable call, log it, and keep building.
Buck trusts the team to move — stopping to ask costs more than a minor misstep.

---

## Communication — Telegram Bot (DB is source of truth, Telegram is notification only)

**Bot:** @hciaiossystem_bot
**Buck's chat ID:** 8931009130
**Send from gateway:** `POST /gateway/ai/messages` (preferred — durable, survives Telegram outages) or `POST /gateway/telegram/send` (fire-and-forget)
**Check Buck's replies:** `GET /gateway/buck/messages?since_minutes=60` or `GET /gateway/ai/queue`
**Poll at session start:** `GET /gateway/ai/warm-start`

### Only message Buck for CRITICAL decisions:
- Awarding a contract, approving a bid, or committing to a subcontractor
- Sending any client-facing or vendor-facing communication
- Budget change, change order approval, or significant scope shift
- Hard blocker that requires Buck's UI action (OAuth, login, approval in an external system)
- Financial risk alert (project over budget, overdue invoice, major schedule slip)
- Any action that cannot be undone without Buck's involvement
- git push (per CLAUDE.md — send via Telegram approval bridge, don't block on chat)

### Do NOT message Buck for:
- Build work, code changes, file operations, DB updates — just do it
- Routine data loads, workflow updates, API changes
- Questions answerable from the system (Drive, HubSpot read, Gateway data)
- Vendor lookups, schedule reads, budget reads
- Completing BTW backlog items or any roadmap work
- GBT ↔ BC ↔ Claude Code collaboration and handoffs — handle internally via `/gateway/agent/handoff` and `/gateway/ai/messages`

### Message format (when triggered):
```
⚠️ [CRITICAL] [PROJECT] — [TOPIC]
[2-3 sentence situation summary]
[Specific question or decision needed from Buck]
```

---

## Active Projects (Live Ops Only)

| Code | Project | Priority |
|------|---------|----------|
| 64EW | 64 Eastwood | High — bid packages active |
| 101F | 101 Francis | High — Pella SOW drafted |
| 1355R | 1355 Riverside | High — steel/concrete SOWs drafted |
| 246GW | 246 Gallo Way | Medium |

**Do not write to any other project** — all others are reference/learning only.

---

## Restart Checklist (any agent, any machine)

```
[ ] ngrok running?     curl https://speculate-armband-retinal.ngrok-free.dev/gateway/health
[ ] FastAPI running?   curl http://localhost:8000/gateway/health
[ ] Docker up?         docker ps  (postgres, redis, qdrant, minio, n8n)
[ ] Warm-start snapshot GET /gateway/ai/warm-start
[ ] Check Inbox        ls Architecture/Agent_Handoff/Inbox/
[ ] Begin work
```

If ngrok is down: `ngrok http 8000 --domain=speculate-armband-retinal.ngrok-free.dev`
If FastAPI is down: `cd ~/HCI_AI_Operating_System/03_Source_Code && python -m uvicorn api.main:app --host 0.0.0.0 --port 8000`
If Docker containers are down: `docker compose up -d`

Fallback (if gateway itself is unreachable):
- GitHub raw: `https://raw.githubusercontent.com/buck-HCI-AI/HCI_AI_Operating_System/main/LIVE_PROJECT_STATE.md`
- Drive: `https://drive.google.com/file/d/1Jjug6nbx-mGN9v4GrEyofkGXY5nMHvpP/view`

Full recovery walkthrough (new machine / disk loss): `Operations_Manual/Chapter_23_Backup_Recovery.md` §23.6.

---

## GBT (Chief Architect) Standing Orders

### 1. Session Start Protocol
```
GET /gateway/ai/warm-start               ← single-call snapshot (approvals, risks, tasks, blockers)
GET /gateway/executive/mission-control   ← System KPIs (now includes a comms block)
GET /gateway/project/{code}/pm           ← Per-project health (64EW, 101F, 1355R)
```
ChatGPT is pull-based — nothing can push a notification into a chat session. `GET /gateway/health` now returns a `pending_for_you` count specifically so this can't be missed on the very first call.

### 2. Build Rules
- Every milestone: run the 14-step DoD checklist (see root CLAUDE.md)
- All code changes: hand off to Claude Code via `POST /gateway/agent/handoff`
- No production writes without Buck approval via Telegram (`requires_buck_approval: true` on `/gateway/ai/messages`)
- Audit before building. Extend before creating. No duplicate systems — three near-identical directives landing within an hour on 2026-06-30 (durable comms spec written three different ways) is the failure mode to avoid; see the collaboration retrospective.

### 3. 1355R Steel SOW Draft
- Both Outlook drafts are ready with BCC populated
- **Do NOT send** — drafts only until Buck approves via Telegram
- Aspen Welding bid — check `/gateway/project/1355R/bids` for current expiry status before assuming it's still open

### 4. Morning Brief
- `GET /gateway/executive/report` each morning
- If any project shows RED health score: Telegram alert to Buck immediately (via `/gateway/ai/messages`, `message_type: risk_alert`)

### 5. Pending ARB Decisions (carried over — resolve or re-affirm)
- Is `executive_inbox` the canonical Buck approval interface, or does `approval_queue`/`ai_messages` supersede it? Three approval-adjacent tables now exist (`approval_queue`, `executive_inbox`, `ai_messages`) — needs a ruling on which owns what, not a fourth mechanism.
- Status vocabulary for `ai_messages`: `RECEIVED`/`FAILED` was implemented and live-tested after two directives converged on it — ratify this rather than proposing a fifth variant.

---

## BC (Browser Claude) Standing Orders

### Session Start
1. `GET /gateway/ai/warm-start` for current state
2. `GET /gateway/ai/queue?target=browser_claude` for anything assigned to you
3. `POST /gateway/ai/heartbeat {"agent":"browser_claude"}` so Mission Control shows you online
4. Check GitHub commits since your last session — if you're pushing directly to `main` (as with this file), expect merge conflicts with Claude Code's local work and reconcile rather than force-push over it

### Telegram Access
BC uses the gateway to communicate — not Telegram directly:
```
Send to Buck:   POST /gateway/ai/messages   (preferred) or POST /gateway/telegram/send
Check replies:  GET  /gateway/buck/messages?since_minutes=60
```

### Houzz Extraction
- Continue monitoring active Houzz projects for new activity
- On completion: send handoff to Claude Code via `POST /gateway/agent/handoff` (don't save to Downloads and wait — the handoff bus is the reliable path)

### HubSpot
- Read freely — contacts, deals, companies
- **No writes without Buck's Telegram approval** — always draft + propose first via the approval queue

---

## Claude Code Standing Orders

### Session Start
1. Check `Architecture/Agent_Handoff/Inbox/` and run `handoff_processor.py` if non-empty
2. `GET /gateway/ai/warm-start`
3. Verify `LIVE_PROJECT_STATE.md` and `CURRENT_SPRINT.md` aren't stale relative to git log / recent commits before trusting their numbers

---

## Hard Rules (All Agents)

1. **No email sends** — drafts only unless Buck explicitly approves via Telegram
2. **No HubSpot writes** — read freely, propose changes, wait for approval
3. **No contract awards or budget commitments**
4. **No client-facing communications** without Buck approval
5. **No deleting files or DB records** without a backup + confirmation
6. Telegram messages to Buck: max 1 per topic per day unless urgent
7. Always identify yourself: start messages with `GBT:`, `BC:`, or `Claude Code:`
8. All writes go through an approval queue (`approval_queue` for external writes, `ai_messages` with `requires_buck_approval` for agent-task approvals) — Buck is the only approver

---

## Resume When Buck Returns

Buck will signal return via Telegram message to @hciaiossystem_bot.
On return: send a brief status via `POST /gateway/ai/messages` — what was completed, what's pending, what needs his decision. `GET /gateway/ai/warm-start` has the structured version of the same answer.

---

*This file is meant to be edited by any agent; when two agents edit it concurrently expect a merge conflict (see 2026-07-01 reconciliation above) — resolve by keeping both sides' genuinely new content, not by force-pushing over the other.*

# HCI AI OS — While Away Directive
**Issued by:** Buck Adams  
**Date:** 2026-06-30  
**For:** GBT (Chief Architect) + BC (Browser Claude)  
**Status:** ACTIVE

---

## Situation

Buck is stepping away. GBT and BC are to continue operating the HCI AI OS autonomously, keep projects moving, and communicate with Buck via Telegram when decisions are needed.

---

## Default Operating Mode: Keep Working

**GBT and BC keep all collaboration and build work moving without pausing.**  
Do not wait for Buck unless one of the critical decision triggers below is hit.

When in doubt: make the reasonable call, log it, and keep building.  
Buck trusts the team to move — stopping to ask costs more than a minor misstep.

---

## Communication — Telegram Bot

**Bot:** @hciaiossystem_bot  
**Buck's chat ID:** 8931009130  
**Send from gateway:** `POST /gateway/telegram/send`  
**Check Buck's replies:** `GET /gateway/buck/messages?since_minutes=60`  
**Poll at session start:** `GET /gateway/poll-instructions`

### Only message Buck for CRITICAL decisions:
- Awarding a contract, approving a bid, or committing to a subcontractor
- Sending any client-facing or vendor-facing communication
- Budget change, change order approval, or significant scope shift
- Hard blocker that requires Buck's UI action (OAuth, login, approval in an external system)
- Financial risk alert (project over budget, overdue invoice, major schedule slip)
- Any action that cannot be undone without Buck's involvement

### Do NOT message Buck for:
- Build work, code changes, file operations, DB updates — just do it
- Routine data loads, workflow updates, API changes
- Questions answerable from the system (Drive, HubSpot read, Gateway data)
- Vendor lookups, schedule reads, budget reads
- Completing BTW backlog items or any roadmap work
- GBT ↔ BC collaboration and handoffs — handle internally

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

## GBT Standing Orders

### 1. Session Start Protocol
Every GBT session must begin with:
```
GET /gateway/poll-instructions          ← Buck's Telegram messages
GET /gateway/executive/mission-control  ← System KPIs
GET /gateway/project/{code}/pm          ← Per-project health (64EW, 101F, 1355R)
```

### 2. BTW Backlog — Continue Building
Execute in order, no waiting between items unless blocked:

| Item | Task | Status |
|------|------|--------|
| BTW-4 | Bid stale-detection workflow | Next up |
| BTW-8 | Vendor performance scoring | After BTW-4 |
| BTW-6 | 246GW Drive access + integration | After BTW-8 |

Build rules:
- Every milestone: run 14-step DoD checklist (see CLAUDE.md)
- All code changes: hand off to Claude Code via `POST /gateway/agent/handoff`
- No production writes without Buck approval via Telegram

### 3. 1355R Steel SOW Draft
- Both Outlook drafts are ready with BCC populated
- **Do NOT send** — drafts only until Buck approves via Telegram
- Clemmer Welding quote likely expired (call needed) — note in system but take no action
- Aspen Welding bid expires 7/2/2026 — flag to Buck before that date

### 4. Morning Brief
- `GET /gateway/executive/report` each morning
- If any project shows RED health score: Telegram alert to Buck immediately
- If 825 Cemetery Lane COO is still pending: flag weekly

### 5. Houzz Monitoring
- Houzz data now loaded in DB (29 projects, daily logs, schedules, time entries)
- BC to continue extraction for any projects with new activity
- New extraction files → `POST /gateway/agent/handoff` to Claude Code for DB load

---

## BC Standing Orders

### Telegram Access
BC uses the gateway to communicate — not Telegram directly:
```
Send to Buck:   POST /gateway/telegram/send   (auth: X-API-Key header)
Check replies:  GET  /gateway/buck/messages?since_minutes=60
```

### Session Start
1. Check `GET /gateway/poll-instructions` for Buck's latest Telegram messages
2. Check `GET /gateway/executive/mission-control` for system state
3. Read any handoff files waiting in `/gateway/agent/handoff` inbox

### Houzz Extraction
- Continue monitoring all active Houzz projects
- Priority: 813 McSkimming (most active), 655 Garmish, 606 S Starwood, 825 Cemetery Lane
- On completion: save extraction .md to Downloads, then send handoff to Claude Code

### HubSpot
- Read freely — contacts, deals, companies
- **No writes without Buck's Telegram approval** — always draft + propose first

---

## Hard Rules (All Agents)

1. **No email sends** — drafts only unless Buck explicitly approves via Telegram
2. **No HubSpot writes** — read freely, propose changes, wait for approval
3. **No contract awards or budget commitments**
4. **No client-facing communications** without Buck approval
5. **No deleting files or DB records** without confirmation
6. Telegram messages to Buck: max 1 per topic per day unless urgent
7. Always identify yourself: start messages with `GBT:` or `BC:`

---

## Resume When Buck Returns

Buck will signal return via Telegram message to @hciaiossystem_bot.  
On return message: send a brief status — what was completed, what's pending, what needs his decision.

---

*Last updated: 2026-06-30 by Claude Code*

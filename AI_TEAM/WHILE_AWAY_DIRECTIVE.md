# WHILE_AWAY_DIRECTIVE.md
## HCI AI Operating System — Restart & Resume Protocol
**Read this file FIRST on every session start, machine restart, or context reset.**
Last Updated: 2026-06-30 | Maintained By: Browser Claude + AUTO-001 nightly
Authority: Buck Adams (Owner)

---

## CURRENT MISSION

**Sprint 3 — Executive Dashboard + AI Communication Reliability**
Sprint Status: ACTIVE
Gate 5: GO — Full Production Authorization (2026-06-30)
Live Projects: 64EW · 101F · 1355R | Monitored: 246GW

---

## SYSTEM HEALTH (as of 2026-06-30)

| Service | Status |
|---|---|
| FastAPI (427+ endpoints) | LIVE — localhost:8000 |
| PostgreSQL (50+ tables) | LIVE |
| Qdrant (13 collections) | LIVE |
| Redis | LIVE |
| n8n (61 workflows, 55 active) | LIVE |
| MCP Server (43 tools) | LIVE — port 8080 |
| ngrok tunnel | LIVE — speculate-armband-retinal.ngrok-free.dev |
| Mining Engine (8 agents) | LIVE — 03:00 daily |
| Executive Dashboard | LIVE — localhost:8000/executive |
| GitHub repo | LIVE — main branch |

---

## AI TEAM — CURRENT ROLES

| AI | Role | How to Connect |
|---|---|---|
| Buck Adams | Owner / Final Authority | Telegram · ntfy · direct |
| ChatGPT (GBT) | Chief Architect / ARB | New session → paste warm-start prompt |
| Claude Code | Lead Implementation Engineer | Terminal: cd ~/HCI_AI_Operating_System && claude |
| Browser Claude | Operations Intelligence / Governance | Open Claude.ai in browser |
| n8n | Automation Orchestrator | localhost:5678 |

---

## TOP PRIORITY ACTIONS (as of 2026-06-30)

### Buck — Action Required
1. **URGENT TODAY: Aspen Welding steel bid on 101F expires July 2** — decision needed now
2. **5 one-tap approvals ready** at http://localhost:8000/executive (EXEC-001 through EXEC-005)
3. Review 986 pending HubSpot vendor candidates in approval queue

### Claude Code — Start Here
1. Check `Architecture/Agent_Handoff/Inbox/` — 3 directives queued from Chief Architect (IDs: 89e31ede, b02ec94e, b36b9f0c)
2. **Update LIVE_PROJECT_STATE.md** — currently shows Sprint 2, Sprint 3 is live
3. **Update CURRENT_SPRINT.md** — currently shows Sprint 2 as active
4. **Update 06_NEXT_SESSION.md** — stale since June 26
5. Implement AI Communication Reliability patch (P0):
   - WHILE_AWAY_DIRECTIVE nightly auto-update (wire to AUTO-001)
      - Directive acknowledgment tracking (RECEIVED → IN_PROGRESS → COMPLETE)
         - Approval queue escalation (48hr ntfy, 7d email)
            - AI heartbeat endpoint
            6. Fix schedule variance sign bug — 101F shows 0 days when actually -5 days
            7. Fix 1355R risk count — test daily log (crane delay) inflating open risks to 5; should be 0

            ### ChatGPT (Chief Architect) — Start Here
            1. Read this file via gateway: GET /gateway/project-state
            2. Note: gateway is returning Sprint 2 state — Sprint 3 is live. Treat Sprint 2 data as stale.
            3. Three directives are queued to Claude Code inbox — Claude Code needs a session to process them
            4. Pending ARB decisions:
               - Is `executive_inbox` table the new canonical Buck approval interface? (replaces/supersedes approval_queue?)
                  - Sprint 2 formal close — acceptance criteria not fully met (AUTO-014/015, INT-008, HZ-001 blocked)
                     - AI-OCP build scope and authorization

                     ### Browser Claude — Start Here
                     1. Read this file ✓
                     2. Read LIVE_PROJECT_STATE.md
                     3. Check GitHub commits since last session
                     4. Check ChatGPT session for new Chief Architect directives
                     5. Verify Claude Code has processed inbox directives
                     6. Report: completed work, blockers, risks

                     ---

                     ## SPRINT 3 — WHAT WAS BUILT (completed ~3 days ago)

                     - `executive_inbox` table (migration 007) — 5 seeded decisions with approve/reject/defer tokens
                     - `/api/v1/executive/dashboard` — live JSON snapshot
                     - `/api/v1/executive/morning-brief` — 5-item condensed brief
                     - `/api/v1/executive/driving-brief` — voice-safe for Siri/Google
                     - `/api/v1/executive/approve|reject|defer/{exec_id}` — one-tap token approvals
                     - `/executive` — mobile-first HTML dashboard, auto-refresh 60s
                     - BC email send + draft capability (gateway endpoints live)
                     - System email routing to hendricksoninc
                     - .env.save/.env.bak blocked from commits (security)

                     ---

                     ## OPEN BLOCKERS

                     | ID | Blocker | Owner | Since |
                     |---|---|---|---|
                     | BLOCK-001 | Branch protection not enabled on main | Buck | 2026-06-26 |
                     | BLOCK-005 | Houzz tables empty — HZ-001 not complete | Browser Claude | 2026-06-27 |
                     | BLOCK-007 | LIVE_PROJECT_STATE.md stale (Sprint 2 shown) | Claude Code | 2026-06-30 |
                     | BLOCK-008 | CURRENT_SPRINT.md stale | Claude Code | 2026-06-30 |
                     | BLOCK-009 | 3 Chief Architect directives in inbox unprocessed | Claude Code | 2026-06-30 |
                     | BLOCK-010 | Aspen Welding steel bid expires July 2 — no decision | Buck | 2026-06-30 |

                     ---

                     ## KEY CONNECTIONS

                     ```
                     Gateway:  https://speculate-armband-retinal.ngrok-free.dev
                     API Key:  hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6
                     Dashboard: http://localhost:8000/dashboard
                     Executive: http://localhost:8000/executive
                     n8n:      http://localhost:5678
                     Docs:     http://localhost:8000/docs
                     ```

                     Fallback (if gateway down — Buck restarts ngrok):
                     - GitHub raw: https://raw.githubusercontent.com/buck-HCI-AI/HCI_AI_Operating_System/main/LIVE_PROJECT_STATE.md
                     - Drive: https://drive.google.com/file/d/1Jjug6nbx-mGN9v4GrEyofkGXY5nMHvpP/view

                     ---

                     ## RESTART CHECKLIST (Claude Code)

                     ```
                     [ ] ngrok running? → curl https://speculate-armband-retinal.ngrok-free.dev/gateway/health
                     [ ] FastAPI running? → curl http://localhost:8000/health
                     [ ] Docker up? → docker ps (postgres, redis, qdrant, minio, n8n)
                     [ ] Check Inbox → ls Architecture/Agent_Handoff/Inbox/
                     [ ] Read this file
                     [ ] Read LIVE_PROJECT_STATE.md
                     [ ] Begin work
                     ```

                     If ngrok is down: `ngrok http 8000 --domain=speculate-armband-retinal.ngrok-free.dev`
                     If FastAPI is down: `cd ~/HCI_AI_Operating_System/03_Source_Code && python -m uvicorn api.main:app --host 0.0.0.0 --port 8000`
                     If Docker containers down: `docker compose up -d`

                     ---

                     ## OPERATING RULES

                     1. Audit before building. Extend before creating. No duplicate systems.
                     2. All writes go through the approval queue. Buck is the only approver.
                     3. Claude Code checks the handoff inbox at every session start — no exceptions.
                     4. LIVE_PROJECT_STATE.md and CURRENT_SPRINT.md must be updated at session end.
                     5. This file is updated by AUTO-001 nightly and by Browser Claude after major state changes.
                     6. Telegram and ntfy are notification layers only — never the source of truth.

                     ---

                     *Created: 2026-06-30 | Author: Browser Claude | Authorized: Buck Adams*
                     *Next auto-update: 2026-07-01 03:00 (AUTO-001 nightly run)*

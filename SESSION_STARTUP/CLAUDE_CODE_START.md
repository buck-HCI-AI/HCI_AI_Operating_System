# Claude Code Session Startup — HCI AI Operating System
**Run through this checklist at the start of every session.**
Last updated: 2026-06-24

---

## Step 1 — Read AI_TEAM State

```bash
cat /Users/buckadams/HCI_AI_Operating_System/AI_TEAM/00_STATUS.md
cat /Users/buckadams/HCI_AI_Operating_System/AI_TEAM/06_NEXT_SESSION.md
cat /Users/buckadams/HCI_AI_Operating_System/AI_TEAM/02_ACTIVE_WORK.md
```

---

## Step 2 — Verify System Health

```bash
# Full health check (Postgres + Qdrant + Redis)
curl -s http://localhost:8000/health | python3 -m json.tool

# Docker containers
docker ps --format "table {{.Names}}\t{{.Status}}"

# n8n
curl -s http://localhost:5678/healthz

# Git status
git -C /Users/buckadams/HCI_AI_Operating_System log --oneline -5
```

**Expected healthy state:**
- FastAPI `/health` → `"status": "healthy"` for postgres, qdrant, redis
- Docker: `hci_postgres`, `hci_qdrant`, `hci_redis`, `n8n` all Up
- FastAPI server is auto-started by launchd — if down, run: `cd /Users/buckadams/HCI_AI_Operating_System/03_Source_Code/api && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000`

---

## Step 3 — Check Git Log

```bash
git -C /Users/buckadams/HCI_AI_Operating_System log --oneline -10
```

Don't re-implement anything already committed.

---

## Step 4 — Pick Up From Next Session File

Read `AI_TEAM/06_NEXT_SESSION.md` and start the first task listed.

**Tomorrow's priorities (2026-06-25):**
1. Confirm morning startup log ran clean — `cat /tmp/hci_morning_startup.log`
2. Confirm morning brief email arrived at buck@ahmaspen.com
3. Review bid leveling output
4. Build preliminary project schedules in Drive
5. Houzz browser automation (Playwright)

---

## Automation Map — What Runs Automatically vs Manually

### AUTO — Runs at Mac Login + 7 AM Daily (launchd)

| What | How | Log |
|---|---|---|
| FastAPI server (port 8000) | `com.hci.api-server` launchd — KeepAlive | `/tmp/hci_api_server.log` |
| WF-007 Bid Leveling | Morning startup script → n8n webhook | `/tmp/hci_morning_startup.log` |
| WF-003 Morning Brief email | Morning startup script → POST /workflows/wf003 | `/tmp/hci_morning_startup.log` |

### MANUAL — Buck triggers only

| Workflow | Trigger | When to use |
|---|---|---|
| WF-001 New Project | `POST /workflows/wf001/new-project` | New job starts |
| WF-002 Meeting Intelligence | `POST /workflows/wf002/meeting` | After any site/owner/sub meeting |
| WF-004 Daily Log | `POST /workflows/wf004/daily-log` | End of each site day |
| WF-005 Lessons Learned | `POST /workflows/wf005/lesson` | Issue resolved / project closes |

**Swagger UI (all endpoints, testable in browser):** `http://localhost:8000/docs`

---

## Session End Checklist

Update these files before ending:

```
AI_TEAM/00_STATUS.md       — reflect current system state
AI_TEAM/02_ACTIVE_WORK.md  — clear completed, note WIP
AI_TEAM/06_NEXT_SESSION.md — write next session's first task
AI_TEAM/08_CHANGELOG.md    — log all changes made
AI_TEAM/03_DECISIONS.md    — log any engineering decisions
```

Commit and push:
```bash
git -C /Users/buckadams/HCI_AI_Operating_System add -A
git -C /Users/buckadams/HCI_AI_Operating_System commit -m "ops: update AI_TEAM session state"
git -C /Users/buckadams/HCI_AI_Operating_System push origin main
```

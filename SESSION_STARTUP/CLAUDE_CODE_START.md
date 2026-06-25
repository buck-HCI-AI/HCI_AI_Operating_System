# Claude Code Session Startup — HCI AI Operating System
**Run through this checklist at the start of every session.**
Last updated: 2026-06-24

---

## Step 1 — Read AI_TEAM State

```bash
# Quick read order:
cat /Users/buckadams/HCI_AI_Operating_System/AI_TEAM/00_STATUS.md
cat /Users/buckadams/HCI_AI_Operating_System/AI_TEAM/06_NEXT_SESSION.md
cat /Users/buckadams/HCI_AI_Operating_System/AI_TEAM/07_BLOCKERS.md
cat /Users/buckadams/HCI_AI_Operating_System/AI_TEAM/02_ACTIVE_WORK.md
```

Or in VS Code: open `AI_TEAM/` folder and review the files.

---

## Step 2 — Verify System Health

```bash
# n8n
curl -s http://localhost:5678/healthz

# Docker containers
docker ps --format "table {{.Names}}\t{{.Status}}"

# Git status
git -C /Users/buckadams/HCI_AI_Operating_System log --oneline -5
git -C /Users/buckadams/HCI_AI_Operating_System status
```

Expected healthy state:
- n8n: `{"status":"ok"}`
- Docker: `n8n_n8n_1` running (postgres/qdrant/redis not yet started)
- Git: clean working tree, `main` branch

---

## Step 3 — Confirm No Duplicate Work

```bash
git -C /Users/buckadams/HCI_AI_Operating_System log --oneline -10
```

Check the last commits before starting — don't re-implement something already done.

---

## Step 4 — Pick Up Highest Priority Task

From `AI_TEAM/06_NEXT_SESSION.md`. Current highest priority:

**TASK-001:** Start the data stack
```bash
cd /Users/buckadams/HCI_AI_Operating_System
docker-compose up -d postgres qdrant redis
docker ps
docker exec -it hci_postgres psql -U hci -d hci_ai -c "\dt"
curl http://localhost:6333/collections
```

---

## Session End Checklist

Before ending any session, update:

```
AI_TEAM/00_STATUS.md       — reflect current system state
AI_TEAM/02_ACTIVE_WORK.md  — clear completed, note WIP
AI_TEAM/06_NEXT_SESSION.md — write next session's first task
AI_TEAM/07_BLOCKERS.md     — add/resolve blockers
AI_TEAM/08_CHANGELOG.md    — log all changes
AI_TEAM/03_DECISIONS.md    — log any engineering decisions made
```

Then commit and push:
```bash
git -C /Users/buckadams/HCI_AI_Operating_System add AI_TEAM/
git -C /Users/buckadams/HCI_AI_Operating_System commit -m "ops: update AI_TEAM session state"
git -C /Users/buckadams/HCI_AI_Operating_System push origin main
```

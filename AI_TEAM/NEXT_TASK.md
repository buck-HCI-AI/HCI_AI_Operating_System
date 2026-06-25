# NEXT_TASK.md
**Highest-priority unfinished work — read this first at session start**
Last updated: 2026-06-24

---

## IMMEDIATE (next session)

### TASK-001: Start the Data Stack
**Priority:** P0 — everything above this is already live; this is the next foundational layer
**Command:**
```bash
cd /Users/buckadams/HCI_AI_Operating_System
docker-compose up -d postgres qdrant redis
```
**Then verify:**
```bash
docker ps
docker exec -it hci_postgres psql -U hci -d hci_ai -c "\dt"
```
**Expected:** postgres, qdrant, redis containers running; all tables from schema.sql visible.

**Blocker:** None — docker-compose.yml is ready. Just needs to be run.

---

### TASK-002: GitHub Remote Setup
**Priority:** P0 — repo has no remote; risk of data loss
**Prerequisite:** Buck runs `! gh auth login` in Claude Code prompt (browser auth required)
**Command (after auth):**
```bash
gh repo create HCI_AI_Operating_System --private \
  --source=/Users/buckadams/HCI_AI_Operating_System \
  --remote=origin --push
```
**Blocker:** Buck must run `! gh auth login` first.

---

## AFTER DATA STACK IS UP

### TASK-003: Memory Ingestion Pipeline
- Read all 3 project bid sheets → insert into `bid_entries` (Postgres)
- Pull HubSpot contacts + deals → insert into `vendors`, `projects` (Postgres)
- Embed vendor/bid history → Qdrant `vendor_memory` + `bid_memory` collections
- Script location: `/03_Source_Code/ingestion/`

### TASK-004: WF-001 New Project Setup Workflow (n8n)
- Trigger: Manual or webhook
- Actions: Create HubSpot deal → create Google Sheet (copy template) → create Drive folder → create AI_TEAM project doc

### TASK-005: WF-002 Meeting Intelligence Workflow (n8n)
- Trigger: Email with meeting notes
- Actions: Parse → extract action items → create HubSpot tasks → log to Qdrant meeting_memory

### TASK-006: FastAPI Layer
- `/api/v1/bids/` — query bid history
- `/api/v1/vendors/` — vendor intelligence
- `/api/v1/projects/` — project status
- `/api/v1/memory/search` — Qdrant semantic search

---

## BACKLOG

- WF-003 Morning Brief
- WF-004 Daily Log
- WF-005 Lessons Learned
- Executive Dashboard
- Agent definitions (Executive, PM, Bid, Procurement, Historian, Relationship)

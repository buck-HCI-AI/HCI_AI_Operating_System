# 05_BACKLOG.md
**All planned work not yet active — prioritized**
Last updated: 2026-06-24

---

## P0 — Immediate (no blockers)

### BL-001: Start Data Stack
```bash
cd /Users/buckadams/HCI_AI_Operating_System
docker-compose up -d postgres qdrant redis
docker exec -it hci_postgres psql -U hci -d hci_ai -c "\dt"
```

### BL-002: GitHub Remote
```bash
# After Buck runs: ! gh auth login
gh repo create HCI_AI_Operating_System --private \
  --source=/Users/buckadams/HCI_AI_Operating_System \
  --remote=origin --push
```

---

## P1 — After Data Stack

### BL-003: Memory Ingestion Pipeline
- Read 3 project bid sheets → insert into `bid_entries` (Postgres)
- Pull HubSpot contacts + deals → insert into `vendors`, `projects`
- Embed and load → Qdrant `vendor_memory` + `bid_memory`
- Script: `/03_Source_Code/ingestion/`
- **Needs:** ChatGPT schema spec first (see 02_ACTIVE_WORK.md)

### BL-004: WF-001 New Project Setup
- Manual/webhook trigger
- Creates: HubSpot deal, Google Sheet (copy template), Drive folder, project doc

### BL-005: WF-002 Meeting Intelligence
- Email trigger
- Parses notes → extracts action items → HubSpot tasks + Qdrant meeting_memory

### BL-006: WF-003 Morning Brief
- Daily 7AM MDT
- Priorities, open bids, project status → email to Buck

### BL-007: WF-004 Daily Log
- Manual or end-of-day trigger
- Site notes, progress, issues → Postgres + Qdrant

### BL-008: WF-005 Lessons Learned
- Project close or manual
- What worked/didn't → `lessons_learned` (Postgres + Qdrant)

---

## P2 — Phase 3 / API Layer

### BL-009: FastAPI Skeleton
- `/03_Source_Code/api/main.py`
- Routers: projects, vendors, bids, memory/search, workflows/trigger

---

## P3 — Agents

### BL-010: Agent Definitions
- Executive, PM, Bid, Procurement, Historian, Relationship
- Prompt library: `/11_Prompts/agents/`
- Agent code: `/10_Agents/`

---

## P4 — Dashboards

### BL-011: Executive Dashboard
### BL-012: PM Dashboard
### BL-013: Universal Search

---

## Icebox (no timeline)

- Google Drive sync / backup automation
- Photo ingestion pipeline (site photos → `photo_memory`)
- SMS/text message integration for field crew
- Subcontractor portal

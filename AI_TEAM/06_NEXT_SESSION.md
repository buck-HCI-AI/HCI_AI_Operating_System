# 06_NEXT_SESSION.md
**Handoff notes — what the next session (Claude Code or ChatGPT) must do first**
Last updated: 2026-06-24 (end of Session 2)

---

## Claude Code: Start Here

### Step 1 — Read AI_TEAM (always)
```
AI_TEAM/00_STATUS.md     ← system health
AI_TEAM/02_ACTIVE_WORK.md ← what's in flight
AI_TEAM/07_BLOCKERS.md   ← what's blocked
```

### Step 2 — Highest Priority Task (no blockers)

**Start the data stack:**
```bash
cd /Users/buckadams/HCI_AI_Operating_System
docker-compose up -d postgres qdrant redis
```

**Verify:**
```bash
docker ps
docker exec -it hci_postgres psql -U hci -d hci_ai -c "\dt"
curl http://localhost:6333/collections
```

Expected: 3 containers running, all Postgres tables from schema.sql visible, Qdrant responding.

### Step 3 — If Buck ran `gh auth login`

```bash
gh repo create HCI_AI_Operating_System --private \
  --source=/Users/buckadams/HCI_AI_Operating_System \
  --remote=origin --push
```

### Step 4 — After data stack is up

Check 02_ACTIVE_WORK.md for memory ingestion pipeline. If ChatGPT has left a spec in `01_Engineering_Library/` or BOOK_00, implement it. Otherwise, ask Buck to get a spec from ChatGPT.

---

## ChatGPT: Start Here

Read these files in order:
1. `AI_TEAM/00_STATUS.md` — what's live
2. `AI_TEAM/04_ARCHITECTURE.md` — full system design
3. `AI_TEAM/01_ROADMAP.md` — what's next
4. `AI_TEAM/02_ACTIVE_WORK.md` — open engineering questions needing architecture decisions
5. `00_Manuscripts/BOOK_00/00_MASTER.md` — canonical engineering manual

Open architecture question requiring your decision:
- Memory ingestion schema: how should HubSpot contact/company data map to Qdrant `vendor_memory`?
- Should n8n write to Postgres directly (via Postgres node) or go through FastAPI?
- Embedding strategy for bid descriptions?

Write your decision/spec to: `01_Engineering_Library/SPEC_memory_ingestion_v1.md`
Then update `AI_TEAM/03_DECISIONS.md` with the architectural decision.

---

## Known State at Session End (2026-06-24)

- Repo: 4 commits on `main`, no GitHub remote
- n8n: running, WF-007 live
- Postgres/Qdrant/Redis: not started (docker-compose ready)
- AI_TEAM: fully rebuilt to Collaboration Proposal v1.0 spec (9 files)
- BOOK_00: seed document created

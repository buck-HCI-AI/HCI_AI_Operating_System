# BOOK_00 § 08 — Workflow Engine

**Status:** ✅ Complete — Phases 8-12 built and live

---

## Architecture Rule

**No workflow owns its own data model, storage path, prompt library, or reporting logic.** Every workflow is an orchestration layer over the common services. Workflows read from and write to the API layer only.

```
WORKFLOW TRIGGER
    │
    ▼
WORKFLOW FUNCTION (wf_*.py)
    │   ├── reads from: Project Brain, Intelligence Services, Postgres (via API)
    │   ├── calls: document_intelligence/ingest, lessons_learned, risks
    │   └── writes via: API layer only (no direct DB writes)
    │
    ▼
WORKFLOW EVENT LOG (workflow_events table)
    │
    ▼
PROJECT BRAIN CACHE INVALIDATED (if project data changed)
```

---

## Workflow Event Log (Phase 8.3)

```sql
CREATE TABLE workflow_events (
    id          SERIAL PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    project_id  INTEGER REFERENCES projects(id),
    event_type  TEXT NOT NULL,   -- 'triggered','completed','failed','data_written'
    payload     JSONB,
    created_at  TIMESTAMPTZ DEFAULT now()
);
```

Every workflow start, completion, failure, and data write is logged here. This table feeds the Reporting Framework and the Workflow Registry endpoint.

---

## Workflow Registry (Phase 8.4)

`GET /api/v1/workflows` returns:

```json
{
  "workflows": [
    {
      "id": "wf003",
      "name": "Morning Brief",
      "status": "active",
      "last_run": "2026-06-25T07:00:00Z",
      "next_run": "2026-06-26T07:00:00Z",
      "schedule": "7:00 AM daily"
    }
  ]
}
```

`POST /api/v1/workflows/{id}/trigger` — manual trigger for any workflow.

---

## Workflow File Convention

| Layer | Location | Naming |
|-------|----------|--------|
| Implementation | `03_Source_Code/workflows/wf_*.py` | `wf_{name}.py` |
| API endpoint | `03_Source_Code/api/routers/workflows.py` | Registered under `/api/v1/workflows/` |
| n8n automation | `04_Workflows/*.json` | Import to n8n UI |
| Spec | `BOOK_00/09_STANDARD_WORKFLOWS.md` through `12_DAILY_LOGS_SCHEDULE.md` | This book |

---

## Trigger Types

| Type | Mechanism | Example |
|------|-----------|---------|
| Schedule | launchd plist | Morning Brief 7 AM |
| Webhook | n8n webhook node or FastAPI endpoint | WF-007 bid leveling |
| Event-driven | API call from another workflow | Daily log → schedule analysis |
| Manual | `POST /api/v1/workflows/{id}/trigger` | PM runs project review |
| External | HubSpot deal created webhook | WF-001 new project (planned) |

---

## Two Automation Stacks

The system runs two workflow automation stacks:

**Stack 1 — Python/FastAPI** (`03_Source_Code/workflows/`):
- 18 workflows active: WF-001/002/003/004/005/006, WF-SUPER, WF-PM, WF-PM-W, WF-REPORT-* (5), WF-SYNC-* (3)
- Direct Postgres/Qdrant/API access
- Runs as part of FastAPI process or standalone scripts

**Stack 2 — n8n** (`04_Workflows/`):
- WF-007 (Bid Leveling Engine)
- Visual workflow builder
- Accesses HCI system via webhooks and API calls
- Runs at `localhost:5678`

Both stacks coexist. New field and PM workflows are built in Stack 1 (Python). WF-007 stays in n8n until bid data migrates to Postgres.

---

## Phase 8 Build Checklist — COMPLETE

- [x] 8.1 Fix vendor_id FK on bid_entries (match names in sync)
- [x] 8.2 Wire Document Intelligence `/ingest` endpoint to `ingest.py` pipeline end-to-end
- [x] 8.3 Create `workflow_events` table
- [x] 8.4 Add `GET /api/v1/workflows` registry endpoint + `POST /trigger`

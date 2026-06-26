# Construction Intelligence Service Layer v1

**Status:** Active  
**Built:** 2026-06-25  
**API Base:** `http://localhost:8000/api/v1/services`  

---

## Overview

Nine construction-specific intelligence services, each with live Postgres queries, Qdrant vector search, and Claude Haiku synthesis. All services inherit from `BaseIntelligenceService` (at `03_Source_Code/services/base.py`), which provides shared access to PostgreSQL, Redis cache, Qdrant, and Anthropic.

### Project Resolution

All services accept a short project code (e.g., `64EW`, `1355RV`, `101F`). Internally, `BaseIntelligenceService.resolve_project_id()` matches the numeric prefix against `projects.name` or `projects.address` via ILIKE, so no separate `project_number` column is required.

---

## Services

| Service | Status | Path | Description |
|---------|--------|------|-------------|
| Project Brain | **active** | `/services/project-brain` | Unified per-project intelligence — bids, meetings, logs, vectors, Claude Q&A |
| Bid Intelligence | **active** | `/services/bid-intelligence` | Package summaries, bid leveling, spread analysis |
| Vendor Intelligence | **active** | `/services/vendor-intelligence` | 860-vendor roster, performance, bid history |
| Document Intelligence | **active** | `/services/document-intelligence` | Dual-collection search, classifier, ingest trigger |
| Lessons Learned | **active** | `/services/lessons-learned` | Library of captured lessons; add/search |
| Procurement | partial | `/services/procurement` | Long-lead & PO tracking (requires UUID schema migration) |
| Historical Cost | partial | `/services/historical-cost` | Bid vs. actual; benchmarks by CSI division |
| Schedule Intelligence | partial | `/services/schedule-intelligence` | Houzz schedule items + daily log progress |
| Risk Intelligence | partial | `/services/risk-intelligence` | Derived risk flags from bid coverage; full table planned |

---

## Project Brain — Key Endpoints

```
GET  /api/v1/services/project-brain/{project_number}
     → Full snapshot (bids, meetings, logs, HubSpot notes, vendor count, vector count)
     → Cached 30 min in Redis

POST /api/v1/services/project-brain/{project_number}/query
     Body: {"question": "...", "context_hint": "bids|vendors|logs|..."}
     → Claude Haiku synthesized answer with source references
     → Cached 5 min

POST /api/v1/services/project-brain/{project_number}/refresh
     → Clears cache, rebuilds snapshot immediately

GET  /api/v1/services/project-brain/{project_number}/bids
GET  /api/v1/services/project-brain/{project_number}/activity
GET  /api/v1/services/project-brain/{project_number}/vendors
```

---

## Technical Architecture

### File Structure

```
03_Source_Code/services/
├── base.py                         ← BaseIntelligenceService (shared pg/redis/qdrant/claude)
├── project_brain/
│   ├── service.py                  ← ProjectBrainService (ACTIVE)
│   ├── routes.py                   ← FastAPI router
│   └── models.py                   ← Pydantic models (ProjectSnapshot, etc.)
├── bid_intelligence/
│   ├── bid_intelligence_svc.py     ← BidIntelligenceService
│   └── routes.py
├── vendor_intelligence/
│   ├── vendor_intelligence_svc.py  ← VendorIntelligenceService
│   └── routes.py
├── procurement/
│   ├── procurement_svc.py          ← ProcurementService
│   └── routes.py
├── historical_cost/
│   ├── historical_cost_svc.py      ← HistoricalCostService
│   └── routes.py
├── lessons_learned/
│   ├── lessons_learned_svc.py      ← LessonsLearnedService
│   └── routes.py
├── schedule_intelligence/
│   ├── schedule_intelligence_svc.py ← ScheduleIntelligenceService
│   └── routes.py
├── risk_intelligence/
│   ├── risk_intelligence_svc.py    ← RiskIntelligenceService
│   └── routes.py
└── document_intelligence/
    ├── document_intelligence_svc.py ← DocumentIntelligenceService
    └── routes.py
```

### Naming Convention (Critical)
Each service's implementation file is named `{service_name}_svc.py` (not `service.py`) to prevent Python `sys.modules` caching collisions when all nine modules are loaded by the same FastAPI process. `project_brain` is the exception — it keeps `service.py` since it was the first module loaded.

### Loading Mechanism
`main.py` uses `importlib.util.spec_from_file_location(f"svc_{name}", path)` to load each `routes.py` with a unique module name, then includes the returned `APIRouter` directly.

---

## Claude Model

All AI synthesis uses `claude-haiku-4-5-20251001` via `BaseIntelligenceService.ask_claude()`.  
Max tokens: 1024 per query. System prompt: construction PM context.

---

## Qdrant Collections Used

| Collection | Used by |
|-----------|---------|
| `drive_memory` | Project Brain, Schedule, Risk |
| `project_memory` | Project Brain query |
| `bid_memory` | Bid Intelligence |
| `vendor_memory` | Vendor Intelligence |
| `lessons_learned` | Lessons Learned |
| `hci_project_documents` | Document Intelligence |
| `hci_sops` | Document Intelligence |

---

## Next Steps

1. **Apply UUID schema migration** — enables Procurement and full Risk table
2. **Historical cost records table** — activates bid vs. actual tracking  
3. **Procore / MS Project schedule sync** — activates Schedule Intelligence fully
4. **Vector ingestion for meetings and daily logs** — enriches Project Brain answers


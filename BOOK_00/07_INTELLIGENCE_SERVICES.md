# BOOK_00 § 07 — Construction Intelligence Services

**Status:** ✅ 8 active, 1 partial (schedule). All running at `/api/v1/services/`.

---

## Base Class

**File:** `03_Source_Code/services/base.py`  
**Class:** `BaseIntelligenceService`

Provides to every service:
- `pg_query(sql, params)` — Postgres query returning list of dicts
- `pg_one(sql, params)` — single row
- `resolve_project_id(project_number)` — "64EW" → projects.id via numeric prefix match
- `cache_get(key)` / `cache_set(key, value, ttl)` — Redis
- `search(query, collection, limit, project_filter)` — Qdrant semantic search
- `ask_claude(prompt, system, max_tokens)` — Claude Haiku synthesis

**AI Model:** `claude-haiku-4-5-20251001` (fast, cheap, construction-aware)

---

## Services

### Project Brain
**Path:** `/api/v1/services/project-brain/{project_number}`  
**Status:** ✅ Active  
**File:** `services/project_brain/service.py`

The unified intelligence layer per project. Pulls every data source into one queryable context.

| Endpoint | Purpose |
|----------|---------|
| `GET /{project}` | Full snapshot: bids, meetings, logs, HubSpot notes, vendor count, vectors |
| `POST /{project}/query` | Claude Haiku Q&A — answers questions about the project |
| `POST /{project}/refresh` | Clear cache, rebuild snapshot |
| `GET /{project}/bids` | All bid packages and entries |
| `GET /{project}/activity` | Recent meetings + daily logs |
| `GET /{project}/vendors` | Vendors with bid history |

**Caching:** Snapshot = 30 min Redis. Query = 5 min Redis.

---

### Bid Intelligence
**Path:** `/api/v1/services/bid-intelligence`  
**Status:** ✅ Active  
**File:** `services/bid_intelligence/bid_intelligence_svc.py`

| Endpoint | Purpose |
|----------|---------|
| `GET /summary?project_number=` | Package totals: bid count, low/high/avg per package |
| `GET /leveling?package_name=&project_number=` | Spread analysis with pct_over_low |
| `GET /search?question=` | Qdrant bid_memory search |

---

### Vendor Intelligence
**Path:** `/api/v1/services/vendor-intelligence`  
**Status:** ✅ Active — 392 vendors  
**File:** `services/vendor_intelligence/vendor_intelligence_svc.py`

| Endpoint | Purpose |
|----------|---------|
| `GET /vendors` | Full vendor list with tier, trade, contact |
| `GET /vendors/{vendor_id}` | Single vendor detail + bid history |
| `GET /search?q=` | Qdrant vendor_memory search |

---

### Document Intelligence
**Path:** `/api/v1/services/document-intelligence`  
**Status:** ✅ Active  
**File:** `services/document_intelligence/document_intelligence_svc.py`

| Endpoint | Purpose |
|----------|---------|
| `GET /search?q=&project=&category=` | Dual-collection semantic search |
| `GET /classify?filename=&content_preview=` | Classify without storing |
| `POST /ingest` | Full ingestion pipeline (Phase 8.2: needs wiring) |

---

### Lessons Learned
**Path:** `/api/v1/services/lessons-learned`  
**Status:** ✅ Active — 1 lesson  
**File:** `services/lessons_learned/lessons_learned_svc.py`

| Endpoint | Purpose |
|----------|---------|
| `GET /lessons` | All lessons, filterable by category / CSI division |
| `GET /search?q=` | Qdrant lessons_learned search |
| `POST /lessons` | Add a new lesson (stores + embeds) |

---

### Procurement
**Path:** `/api/v1/services/procurement`  
**Status:** ✅ Active (tables exist, no data yet)  
**File:** `services/procurement/procurement_svc.py`

| Endpoint | Purpose |
|----------|---------|
| `GET /long-lead?project_number=` | Long-lead items by project |
| `GET /status?project_number=` | Procurement items by status |
| `GET /search?q=` | Qdrant hci_procurement search |

---

### Historical Cost
**Path:** `/api/v1/services/historical-cost`  
**Status:** ✅ Active (tables exist, no data yet)  
**File:** `services/historical_cost/historical_cost_svc.py`

| Endpoint | Purpose |
|----------|---------|
| `GET /benchmarks?csi_division=` | Cost benchmarks by CSI division |
| `GET /bid-vs-actual/{project_number}` | Awarded bids vs. actual cost (if recorded) |
| `GET /search?q=` | Qdrant hci_historical_costs search |

---

### Risk Intelligence
**Path:** `/api/v1/services/risk-intelligence`  
**Status:** ✅ Active (table exists, no data yet)  
**File:** `services/risk_intelligence/risk_intelligence_svc.py`

| Endpoint | Purpose |
|----------|---------|
| `GET /{project_number}` | Project risks from risks table; derives from bid coverage if empty |
| `GET /search?q=` | Qdrant drive_memory risk search |

---

### Schedule Intelligence
**Path:** `/api/v1/services/schedule-intelligence`  
**Status:** ⚠️ Partial — no schedule data source yet  
**File:** `services/schedule_intelligence/schedule_intelligence_svc.py`

| Endpoint | Purpose |
|----------|---------|
| `GET /{project_number}` | Schedule items (empty — needs Houzz/Procore sync) |
| `GET /search?q=` | Qdrant drive_memory schedule search |

**Activation path:** WF-SUPER daily logs → Phase 9.2 schedule analysis → populates schedule_variance table.

---

## Architecture Rules for Services

1. All services inherit `BaseIntelligenceService` — no private DB connections.
2. All services use `resolve_project_id()` for project lookup — no `project_number` column.
3. Service files named `{service_name}_svc.py` — not `service.py` (avoids Python module cache collision).
4. Services are stateless — state lives in Redis cache, Postgres, or Qdrant.
5. No service generates its own report — that belongs to the Reporting Framework (Section 13).

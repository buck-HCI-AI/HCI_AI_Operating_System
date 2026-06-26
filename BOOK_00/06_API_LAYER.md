# BOOK_00 § 06 — API Layer

**Status:** ✅ Complete and running on port 8000

---

## Overview

FastAPI application at `03_Source_Code/api/main.py`. Versioned at `/api/v1`. All applications, automations, and AI agents communicate through this single interface.

**Base URL:** `http://localhost:8000`  
**Docs:** `http://localhost:8000/docs`  
**Version:** 1.0.0

---

## Router Map

| Prefix | File | Purpose |
|--------|------|---------|
| `/api/v1/projects` | `routers/projects.py` | Project CRUD |
| `/api/v1/vendors` | `routers/vendors.py` | Vendor list and lookup |
| `/api/v1/bids` | `routers/bids.py` | Bid packages and entries |
| `/api/v1/documents` | `routers/documents.py` | Document list, status, download |
| `/api/v1/storage` | `routers/storage.py` | MinIO list, upload, download |
| `/api/v1/search` | `routers/search.py` | Qdrant semantic search |
| `/api/v1/system` | `routers/system.py` | Health check (all 4 services) |
| `/api/v1/auth` | `routers/auth.py` | API key management |
| `/api/v1/ai` | `routers/ai.py` | AI agent stubs + classify |
| `/api/v1/workflows` | `routers/workflows.py` | Workflow triggers + sync |
| `/api/v1/memory` | `routers/memory.py` | Qdrant memory search |
| `/api/v1/ingest` | `routers/ingest.py` | Document ingestion trigger |
| `/api/v1/services/*` | `services/*/routes.py` | 9 Intelligence Services |
| `/api/v1/sop/*` | `routers/sop.py` | 27 SOPs — 189 endpoints |
| `/api/v1/platform/*` | `routers/platform.py` | Platform Integration Layer — 33 endpoints |

**Legacy routes** (backward compat): same endpoints without `/api/v1` prefix.

---

## Configuration

**File:** `03_Source_Code/api/config.py` (Pydantic Settings)  
**Reads from:** Root `.env`

Key settings:
- `app_name`, `app_version`
- `postgres_dsn` — built from POSTGRES_* vars
- `redis_url`, `qdrant_host`, `qdrant_port`
- `minio_endpoint`, `minio_root_user`, `minio_root_password`
- `anthropic_api_key`
- `valid_api_keys` — comma-separated; empty = auth disabled

---

## Middleware

| Middleware | File | Purpose |
|-----------|------|---------|
| CORS | FastAPI built-in | Allow all origins (dev) |
| Request Logging | `middleware/logging.py` | Log method, path, status, duration |
| API Key Auth | `middleware/auth.py` | Enforce X-API-Key on /api/v1/* when keys configured |

---

## Shared Service Layer

| Module | File | Purpose |
|--------|------|---------|
| Database | `api/services/db.py` | `query()`, `query_one()`, `execute()` via psycopg2 |
| Cache | `api/services/cache.py` | Redis get/set/delete with JSON + TTL |
| Storage | `api/services/storage.py` | MinIO operations |
| Vector | `api/services/vector.py` | Qdrant search with collection routing |

---

## Intelligence Service Loading

Services are loaded via `importlib` to avoid Python `sys.modules` naming collisions (all services previously named `service.py`):

```python
def _load_svc(name: str):
    path = os.path.abspath(f"../services/{name}/routes.py")
    spec = importlib.util.spec_from_file_location(f"svc_{name}", path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.router   # returns APIRouter directly
```

Service implementation files are named `{service_name}_svc.py` to prevent collision.

---

## Architecture Rule

**No workflow or agent writes to PostgreSQL, Qdrant, or MinIO directly.** All writes go through the API layer. This ensures consistent logging, validation, and event tracking.

# HCI AI API Layer v1

## Overview

The FastAPI backend is the **single integration point** for all applications, automations, and AI agents. Nothing communicates directly with PostgreSQL, Redis, MinIO, or Qdrant — everything goes through this API.

- **Base URL:** `http://localhost:8000`
- **Versioned:** `http://localhost:8000/api/v1/`
- **Docs (Swagger):** `http://localhost:8000/docs`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`
- **Tailscale:** `http://100.97.100.69:8000`

## Authentication

| Mode | Behavior |
|------|----------|
| Development (default) | No key required — all requests pass |
| Production | `X-API-Key: <key>` header required on `/api/v1/*` |

To enable: set `API_KEYS=key1,key2` in `.env`. Health and docs endpoints always open.

Check current mode:
```bash
curl http://localhost:8000/api/v1/auth/mode
```

## Endpoint Groups

### Health
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Quick liveness check |
| GET | `/api/v1/health` | Same, versioned |

### System Status
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/system` | Full status: all services, latencies, counts |
| GET | `/api/v1/system/collections` | Qdrant collections + vector counts |
| GET | `/api/v1/system/storage` | MinIO buckets + object counts |
| GET | `/api/v1/system/config` | Non-sensitive config summary |

### Projects
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/projects` | List all projects |
| GET | `/api/v1/projects/{id}` | Get project by ID |
| POST | `/api/v1/projects` | Create project (WF-001) |

### Vendors
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/vendors` | List vendors |
| GET | `/api/v1/vendors/{id}` | Get vendor |
| POST | `/api/v1/vendors` | Create vendor |

### Documents
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/documents` | List documents (filter: project, category, status) |
| GET | `/api/v1/documents/{id}` | Get document metadata |
| GET | `/api/v1/documents/{id}/download` | Presigned MinIO download URL |
| PATCH | `/api/v1/documents/{id}/status` | Update processing status |

### Storage (MinIO)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/storage/buckets` | List all buckets |
| GET | `/api/v1/storage/buckets/{bucket}` | List objects in bucket |
| POST | `/api/v1/storage/buckets/{bucket}/upload` | Upload file |
| GET | `/api/v1/storage/buckets/{bucket}/download?key=` | Presigned download URL |
| DELETE | `/api/v1/storage/buckets/{bucket}/objects?key=` | Delete object |

### Knowledge Ingestion
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/ingest/file` | Upload file → full pipeline |
| POST | `/api/v1/ingest/path` | Ingest local file by path |
| POST | `/api/v1/ingest/batch` | Ingest all files in directory |

### Search
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/search` | Semantic search across knowledge base |
| GET | `/api/v1/search/collections` | List searchable collections |

**Search request body:**
```json
{
  "query": "framing bid for 64 Eastwood",
  "collection": null,
  "limit": 10,
  "project_filter": "64EW",
  "category_filter": "bids",
  "score_threshold": 0.3
}
```

### Workflows
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/workflows/wf001/new-project` | New project setup |
| POST | `/api/v1/workflows/wf002/meeting` | Log meeting notes |
| POST | `/api/v1/workflows/wf003/morning-brief` | Send morning brief |
| POST | `/api/v1/workflows/wf004/daily-log` | Daily site log |
| POST | `/api/v1/workflows/wf005/lesson` | Record lesson learned |
| POST | `/api/v1/workflows/wf006/inbox-review` | Inbox review + AI drafts |
| POST | `/api/v1/workflows/sync/hubspot` | Pull HubSpot → Postgres |
| POST | `/api/v1/workflows/sync/houzz` | Pull Houzz → Postgres |
| POST | `/api/v1/workflows/sync/drive` | Pull Google Drive → Qdrant |

### AI Services (Scaffold — Phase 4)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/ai/agents` | List available + planned agents |
| POST | `/api/v1/ai/query` | Executive agent (not yet implemented) |
| POST | `/api/v1/ai/classify` | Classify document by filename + content |

## Service Architecture

```
External Callers
(n8n, ChatGPT, Claude Code, HubSpot, Outlook, dashboards)
        │
        ▼
  FastAPI v1  (:8000/api/v1)
        │
   ┌────┼────┬────┬────┐
   ▼    ▼    ▼    ▼    ▼
  PG  Redis MinIO Qdrant n8n
```

## Response Format

All endpoints return JSON. Standard fields:

```json
{ "status": "ok", "data": {...} }       // success
{ "status": "error", "error": "..." }   // failure
{ "detail": "..." }                      // FastAPI validation error
```

## Module Structure

```
03_Source_Code/api/
├── main.py              — app factory, router registration, middleware
├── config.py            — Pydantic Settings (reads .env)
├── dependencies.py      — FastAPI deps: get_db, get_redis, get_minio, get_qdrant
├── middleware/
│   ├── auth.py          — X-API-Key enforcement on /api/v1/*
│   └── logging.py       — request/response logging with latency
├── schemas/
│   ├── common.py        — SuccessResponse, ErrorResponse, SystemStatusResponse
│   ├── documents.py     — DocumentResponse, DocumentListResponse
│   └── search.py        — SearchRequest, SearchResponse, SearchResult
├── services/
│   ├── db.py            — PostgreSQL query helpers
│   ├── cache.py         — Redis get/set with JSON + TTL
│   ├── storage.py       — MinIO bucket/object operations
│   └── vector.py        — Qdrant semantic search + collection routing
└── routers/
    ├── health.py        — /health
    ├── auth.py          — /api/v1/auth
    ├── projects.py      — /api/v1/projects
    ├── vendors.py       — /api/v1/vendors
    ├── bids.py          — /api/v1/bids
    ├── documents.py     — /api/v1/documents
    ├── storage.py       — /api/v1/storage
    ├── ingest.py        — /api/v1/ingest
    ├── search.py        — /api/v1/search
    ├── system.py        — /api/v1/system
    ├── ai.py            — /api/v1/ai
    ├── workflows.py     — /api/v1/workflows
    └── memory.py        — /api/v1/memory (legacy search)
```

## Backward Compatibility

Legacy routes (pre-v1) remain active for existing integrations:
- `/workflows/*` — morning sequence, launchd scripts
- `/memory/search` — existing search calls
- `/projects`, `/vendors`, `/bids` — existing direct calls

All legacy routes work identically at both `/legacy-path` and `/api/v1/legacy-path`.

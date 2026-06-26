# BOOK_00 § 02 — Infrastructure Architecture

**Status:** ✅ Complete and running

---

## Services

| Service | Image | Port | Purpose | Managed by |
|---------|-------|------|---------|-----------|
| PostgreSQL 16 | postgres:16 | 5432 | Structured data truth store | Docker |
| Qdrant | qdrant/qdrant | 6333/6334 | Vector search | Docker |
| Redis 7 | redis:7-alpine | 6379 | Cache + session state | Docker |
| MinIO | minio/minio | 9000/9001 | Object storage (S3-compatible) | Docker |
| FastAPI | Python 3.13 | 8000 | API layer | launchd |
| n8n | n8nio/n8n | 5678 | Workflow automation | Docker (separate) |
| ngrok | ngrok | — | External tunnel | launchd |

---

## Docker Compose

**File:** `docker-compose.yml` (root)  
**Start:** `docker compose up -d`  
**Stop:** `docker compose down`

All four data services (Postgres, Qdrant, Redis, MinIO) run in Docker with named volumes by default. When HCI_AI_DEV drive is present, `docker-compose.storage.yml` overrides to bind mounts on the drive.

---

## Credentials

All credentials in root `.env` (gitignored). Key variables:

```
POSTGRES_USER=hci_admin
POSTGRES_PASSWORD=hci_postgres_2026
POSTGRES_DB=hci_os
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

REDIS_URL=redis://localhost:6379/0

MINIO_ENDPOINT=localhost:9000
MINIO_ROOT_USER=hci_minio_admin
MINIO_ROOT_PASSWORD=hci_minio_2026_Aspen!

QDRANT_HOST=localhost
QDRANT_PORT=6333

ANTHROPIC_API_KEY=...
```

---

## launchd Agents

| Agent | Plist | Purpose | Schedule |
|-------|-------|---------|---------|
| API Server | `com.hci.api-server.plist` | Run FastAPI on port 8000 | Always-on, KeepAlive |
| Drive Watcher | `com.hci.drive-watcher.plist` | Watch HCI_AI_DEV mount, start Docker with storage | On drive mount |
| Morning Brief | `com.hci.morning-brief.plist` | Run WF-003 + WF-006 | 7 AM daily |
| ngrok | `com.ngrok.hci.plist` | External tunnel | Always-on |

**Logs:** `/tmp/hci_api_server.log`, `/tmp/hci_api_server_err.log`

---

## HCI_AI_DEV Drive (WD My Passport SSD)

**Mount point:** `/Volumes/HCI_AI_DEV`  
**Format:** APFS  
**Capacity:** 1 TB  

**Folder structure:**
```
HCI_AI_DEV/
├── docker_data/        ← Docker named volume data (bind mount override)
├── documents/          ← Raw document storage
├── backups/            ← Postgres + Qdrant dumps
├── projects/           ← Project-specific files
├── ingestion_queue/    ← Files pending ingestion
├── processed/          ← Ingested files archive
├── minio_data/         ← MinIO data directory
├── qdrant_data/        ← Qdrant storage
├── logs/               ← Application logs archive
├── exports/            ← Report exports, bid tabs
└── temp/               ← Scratch space
```

**Future:** 4 TB NAS migration when Mac mini moves to production.

---

## Network Architecture

```
Internet
    │
    └── ngrok tunnel → localhost:8000 (FastAPI)
                              │
                    ┌─────────┴──────────┐
                    │    FastAPI API      │
                    │    port 8000        │
                    └─────────┬──────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
    Postgres:5432       Qdrant:6333         Redis:6379
          │                   │
    MinIO:9000         (vectors/search)
    (object storage)
```

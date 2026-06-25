# HCI AI Infrastructure — Phase 1

Production-ready Docker Compose stack. Runs unchanged on MacBook Air M5 and Mac mini M4 Pro.

## Services

| Service    | Port(s)        | Purpose                                    |
|------------|----------------|--------------------------------------------|
| PostgreSQL | 5432           | Operational truth store (projects, bids, vendors, sync tables) |
| Redis      | 6379           | Workflow cache and queue                   |
| MinIO      | 9000 / 9001    | Object storage (docs, PDFs, photos, backups) |
| Qdrant     | 6333 / 6334    | Vector memory (semantic search, AI recall) |

MinIO console: http://localhost:9001

## First-Time Setup

```bash
# 1. Copy and fill environment variables
cp .env.example .env
# Edit .env — set all passwords

# 2. Start the stack
cd infrastructure/
docker compose up -d

# 3. Verify all services are healthy
docker compose ps
```

All four services must show `healthy` before the application layer starts.

## Daily Operations

```bash
# Start
docker compose up -d

# Check status
docker compose ps

# View logs for a service
docker compose logs -f postgres
docker compose logs -f qdrant

# Stop (keeps data)
docker compose down

# Full reset — DESTROYS ALL DATA
docker compose down -v
```

## MinIO Buckets

Created automatically on first startup by `minio-init`:

| Bucket              | Contents                                      |
|---------------------|-----------------------------------------------|
| `hci-documents`     | Bid PDFs, drawings, scope packages, contracts |
| `hci-ai-artifacts`  | AI outputs, leveling reports, summaries       |
| `hci-backups`       | Postgres dumps, export snapshots              |
| `hci-images`        | Site photos, progress photos, punch list      |

Access via MinIO console at http://localhost:9001 (credentials in `.env`).

## Migrating to Mac Mini M4 Pro

1. `git clone` the repo on the new machine
2. Copy `.env` (never committed — transfer securely)
3. `cd infrastructure && docker compose up -d`
4. Restore Postgres from backup: `psql hci_os < backup.sql`
5. Qdrant data restores from its Docker volume snapshot

## Volumes

All data is persisted in named Docker volumes:

| Volume          | Service    |
|-----------------|------------|
| `postgres_data` | PostgreSQL |
| `redis_data`    | Redis      |
| `minio_data`    | MinIO      |
| `qdrant_data`   | Qdrant     |

Volumes survive `docker compose down`. Only `docker compose down -v` removes them.

## Schema Changes

The PostgreSQL schema lives in two places — keep them in sync:
- `infrastructure/postgres/init.sql` — used by Docker on first container start
- `05_Database/postgres/schema.sql` — canonical reference, committed to repo

For changes to an already-running database, apply migrations directly via psql.

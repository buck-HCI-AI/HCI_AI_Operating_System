# 08_CHANGELOG.md
**Engineering changelog — what changed, when, and why**
Most recent first.

---

## 2026-06-25 — API Layer v1 (Phase 4)

**Engineer:** Claude Code | **Directive:** HCI_AI_API_Layer_v1_Master_Directive_for_Claude_Code.pdf

### Added
- `api/config.py` — Pydantic Settings class; all config from .env
- `api/dependencies.py` — FastAPI deps: get_db, get_redis, get_minio, get_qdrant
- `api/middleware/auth.py` — X-API-Key enforcement on /api/v1/* (dev mode = open)
- `api/middleware/logging.py` — Request logging with latency (X-Response-Time-Ms header)
- `api/schemas/common.py` — SuccessResponse, ErrorResponse, SystemStatusResponse, ServiceStatus
- `api/schemas/documents.py` — DocumentResponse, DocumentListResponse, DocumentIngestResponse
- `api/schemas/search.py` — SearchRequest, SearchResponse, SearchResult
- `api/services/db.py` — PostgreSQL helpers: query, query_one, execute, execute_returning
- `api/services/cache.py` — Redis get/set/delete with JSON + TTL
- `api/services/storage.py` — MinIO: list_buckets, list_objects, put_object, presigned_url, delete
- `api/services/vector.py` — Qdrant: search, list_collections, embed, collection routing
- `api/routers/auth.py` — /api/v1/auth/status, /api/v1/auth/mode
- `api/routers/documents.py` — /api/v1/documents CRUD + presigned download
- `api/routers/storage.py` — /api/v1/storage bucket + object operations
- `api/routers/search.py` — /api/v1/search unified semantic search with Redis caching
- `api/routers/system.py` — /api/v1/system full health + latency + collections + storage
- `api/routers/ai.py` — /api/v1/ai scaffold (agents list, query stub, classify)
- `docs/API_LAYER_v1.md` — full endpoint reference, auth, architecture, module map

### Changed
- `api/main.py` — v1.0.0, RequestLogging + ApiKey middleware, /api/v1 prefix router, legacy routes preserved
- `.env` — added MINIO_*, HCI_STORAGE_ROOT entries
- `AI_TEAM/00_STATUS.md`, `06_NEXT_SESSION.md`, `08_CHANGELOG.md`
- Installed: `pydantic-settings`, `minio` for /usr/local/bin/python3

### Result
`GET http://localhost:8000/api/v1/system` → all 4 services healthy (postgres, redis, minio, qdrant)

---

## 2026-06-25 — Development Storage & Knowledge Ingestion Engine (Phase 3)

**Engineer:** Claude Code | **Directive:** HCI_AI_Master_Directive_Development_Storage_and_Knowledge_Ingestion_v1.pdf

### Added
- `03_Source_Code/ingestion/classifier.py` — project/category/CSI/version/date detection from filename + content
- `03_Source_Code/ingestion/extractor.py` — text extraction module (pdf, docx, xlsx, txt, md, csv)
- `03_Source_Code/ingestion/ingest.py` — 6-stage Knowledge Ingestion Engine (Capture→Classify→Store→Index→Register→Archive)
- `03_Source_Code/api/routers/ingest.py` — FastAPI router: POST /ingest/file, /ingest/path, /ingest/batch
- `infrastructure/docker-compose.storage.yml` — override file for bind mounts to `${HCI_STORAGE_ROOT}`
- `infrastructure/setup_storage_drive.sh` — creates 10-folder structure on HCI_AI_DEV drive
- `infrastructure/migrate_volumes.sh` — migrates named volumes → bind mounts on external drive
- `docs/STORAGE_LAYER_CONFIGURATION_v1.md` — drive setup, compose modes, migration guide
- `docs/KNOWLEDGE_INGESTION_ENGINE_v1.md` — pipeline stages, API endpoints, routing table, error handling

### Changed
- `infrastructure/.env.example` — added `HCI_STORAGE_ROOT` variable with documentation
- `03_Source_Code/api/main.py` — added ingest router at prefix `/ingest`, bumped to v0.2.0

### Buck Action Required
- **Reformat WD My Passport** — currently NTFS; needs APFS + GUID Partition Map + name HCI_AI_DEV
- Then run: `bash infrastructure/setup_storage_drive.sh`

---

## 2026-06-25 — Data Architecture & Document Storage Foundation (Phase 2)

**Engineer:** Claude Code | **Directive:** HCI_AI_Data_Architecture_and_Document_Storage_Master_Directive_for_Claude_Code_v1.pdf

### Added
- `database/schema/001_initial_core_schema.sql` — UUID companies, contacts, projects (5 tables + pgcrypto)
- `database/schema/002_document_storage_schema.sql` — documents, versions, chunks, tags (6 tables)
- `database/schema/003_registry_schema.sql` — vendors, bids, costs, risks, lessons (12 tables)
- `database/schema/004_embedding_metadata_schema.sql` — Qdrant collections, embedding jobs, search log (4 tables)
- `database/seeds/` — CSI divisions, document categories
- `database/validate.py` — 10-point health check script (9/10 pass on legacy DB)
- `docs/` — 5 architecture standards docs
- `architecture/` — 2 data architecture diagrams
- `workflows/` — WORKFLOW_01 (document ingestion), WORKFLOW_02 (registry writeback)

### Changed
- `infrastructure/minio/init_buckets.sh` — updated to Phase 2 bucket names (5 buckets)
- All AI_TEAM files refreshed

---

## 2026-06-25 — Infrastructure Phase 1 + Drive Sync

**Engineer:** Claude Code | **Directive:** HCI_AI_Infrastructure_Phase_1_Master_Directive_for_Claude_Code.pdf

### Added
- `infrastructure/docker-compose.yml` — Postgres 16, Redis 7, MinIO, Qdrant; health checks, persistent volumes
- `infrastructure/.env.example` — all 20 required env vars documented
- `infrastructure/README.md` — setup, operations, Mac mini migration guide
- `infrastructure/postgres/init.sql` — full 14-table schema + seed data (83 Sagebrusch added)
- `infrastructure/redis/redis.conf` — memory limit 256mb, AOF persistence, LRU eviction
- `infrastructure/minio/init_buckets.sh` — auto-creates 4 buckets on first start
- `infrastructure/qdrant/config.yaml` — Qdrant production config
- `workflows/sync_drive.py` — Google Drive full ingestion (PDF/DOCX/XLSX/GDOC/GSHEET → drive_memory)
- `POST /sync/drive` endpoint in FastAPI workflows router
- Drive sync added to morning startup sequence (Mondays only)
- `drive_sync_log` table in Postgres schema
- Installed packages: `python-docx`, `openpyxl`

### Changed
- `AI_TEAM/00_STATUS.md` — full status refresh, MinIO and Drive sync added
- `AI_TEAM/02_ACTIVE_WORK.md` — Phase 1 deliverables logged
- `AI_TEAM/03_DECISIONS.md` — DEC-007 (MinIO), DEC-008 (infrastructure/ canonical IaC)
- `AI_TEAM/04_ARCHITECTURE.md` — data layer updated: 14 tables, 7 Qdrant collections, MinIO added
- `AI_TEAM/06_NEXT_SESSION.md` — next priorities updated
- `AI_TEAM/07_BLOCKERS.md` — BLK-001/BLK-002 status reviewed
- `run_morning_brief.sh` — Drive sync step added (Monday-only gate)
- `api/routers/workflows.py` — /sync/drive endpoint added

### Drive Sync Results (first run)
- 96 files found, 89 successfully ingested, 7 errors (101F xlsx not downloaded locally)
- 2,335 chunks in Qdrant `drive_memory` collection
- All PDFs, GDOC/GSHEET (via Drive API export), DOCX, XLSX from HCI AI - Master Drive

### Decisions
- DEC-007: MinIO added as object store — 4 canonical buckets
- DEC-008: `infrastructure/` is canonical IaC going forward

---

## 2026-06-24 — Session 2 (afternoon)

**Engineer:** Claude Code | **Architect:** ChatGPT (async via CHATGPT_BRIEFING.md)

### Added
- AI_TEAM/ directory — 9 files per Collaboration Proposal v1.0
- BOOK_00 canonical engineering manual seed
- Operating Charter + Collaboration Proposal PDFs → 01_Engineering_Library/

### Changed
- .gitignore — allow PDFs in 01_Engineering_Library/ and 09_PDFs/
- AI_TEAM file names migrated to numbered scheme (00–08)

---

## 2026-06-24 — Session 2 (morning)

**Engineer:** Claude Code

### Added
- `HCI_AI_Operating_System/` git repository — initial structure
- `.env.example`, `.gitignore`, `README.md`, `docker-compose.yml` (root — n8n + Postgres + Qdrant + Redis)
- `03_Source_Code/integrations/` — credentials.py, hubspot.py, google_sheets.py, microsoft_graph.py
- `04_Workflows/WF-007_Bid_Leveling_Engine.json`
- `05_Database/postgres/schema.sql`, `05_Database/qdrant/collections.md`
- `06_Project_Documentation/` — READMEs for 64 Eastwood, 101 Francis, 1355 Riverside
- GitHub CLI (gh 2.95.0)

# HCI AI Data Architecture

## Storage Layer Map

```
┌─────────────────────────────────────────────────────────────────┐
│                     STORAGE LAYER                               │
│                                                                 │
│  PostgreSQL 16          MinIO               Qdrant              │
│  ─────────────          ─────               ──────              │
│  Structured facts       File objects        Vectors             │
│  Registry records       Raw documents       Semantic search     │
│  Metadata index         Processed text      AI retrieval        │
│  Audit trail            AI artifacts        Payload metadata    │
│  port 5432              port 9000/9001       port 6333/6334     │
│                                                                 │
│  Redis                                                          │
│  ─────                                                          │
│  Queue, cache           NOT for:                                │
│  Session state          - files                                 │
│  Rate limits            - structured data                       │
│  port 6379              - long-term facts                       │
└─────────────────────────────────────────────────────────────────┘
```

## PostgreSQL Schema (23 tables across 4 migrations)

### Domain 001 — Core
`companies` → `contacts` ↔ `company_contacts`
`projects` → `project_team_members`

### Domain 002 — Document Storage
`documents` → `document_versions`
`documents` ↔ `document_relationships`
`documents` → `document_tags`
`documents` → `document_processing_events`
`documents` → `document_chunks` → Qdrant

### Domain 003 — Registries
`csi_divisions` → `cost_codes`
`vendors` → `vendor_trade_mappings`, `vendor_project_history`
`bid_packages` → `bid_requests`, `bids`
`procurement_items` → `long_lead_items`
`historical_cost_records`
`risks`, `lessons_learned`

### Domain 004 — Embedding Infrastructure
`qdrant_collections`, `embedding_jobs`, `search_log`, `sync_log`

## MinIO Bucket Architecture

```
hci-raw-documents         ← all incoming files land here first
hci-processed-documents   ← extracted text, normalized content
hci-ai-artifacts          ← AI summaries, reports, leveling outputs
hci-backups               ← Postgres dumps, snapshots
hci-ingestion-quarantine  ← failed or suspicious ingestion
```

## Qdrant Collection Architecture

```
hci_book00              ← BOOK_00 engineering manual
hci_sops                ← Standard Operating Procedures
hci_project_documents   ← all project-level documents
hci_vendor_intelligence ← vendor profiles and history
hci_historical_costs    ← cost benchmarks and records
hci_lessons_learned     ← lessons across all projects
hci_procurement         ← procurement intelligence
```

## Cross-Reference Integrity

The three-way link between systems:

```
PostgreSQL documents.id
    ↕
PostgreSQL document_chunks.document_id + qdrant_point_id
    ↕
Qdrant vector payload.document_id + document_chunk_id
    ↕
MinIO storage_bucket + storage_object_key
```

A search result from Qdrant always resolves to a full document in PostgreSQL and the raw file in MinIO.

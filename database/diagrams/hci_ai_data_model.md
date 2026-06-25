# HCI AI Data Model — Entity Relationship Diagram

## Core Entity Relationships

```
companies ──────────────────────────────────────┐
    │                                            │
    ├── contacts ──── company_contacts ──────────┤
    │                                            │
    └── projects ────────────────────────────────┤
            │                                    │
            ├── project_team_members ─── contacts┘
            │
            ├── bid_packages ─── bid_requests ─── vendors
            │       └── bids ──────────────────── vendors
            │
            ├── procurement_items ─── long_lead_items
            │       └── vendors
            │
            ├── historical_cost_records
            │       ├── csi_divisions
            │       ├── cost_codes
            │       ├── vendors
            │       └── documents (source_document_id)
            │
            ├── risks ─── documents (related_document_id)
            │
            └── lessons_learned ─── documents

vendors ────────────────────────────────────────────
    ├── vendor_trade_mappings ─── csi_divisions
    └── vendor_project_history ─── projects

csi_divisions ──────────────────────────────────────
    └── cost_codes (hierarchical, self-referencing)

documents ──────────────────────────────────────────
    ├── projects (project_id)
    ├── companies (company_id)
    ├── vendors (vendor_id)
    ├── csi_divisions (csi_division_id)
    ├── document_versions (document_id)
    ├── document_relationships (parent ↔ child)
    ├── document_tags (document_id)
    ├── document_processing_events (document_id)
    └── document_chunks ──── Qdrant vector
            └── qdrant_point_id resolves to:
                    document_id → PostgreSQL
                    storage_object_key → MinIO
```

## Storage Layer Routing

```
Every document flows through:

SOURCE ──→ MinIO (hci-raw-documents) ──→ Extractor ──→ MinIO (hci-processed-documents)
                                              │
                                              ▼
                                    PostgreSQL (documents row)
                                              │
                                              ▼
                                    Chunker ──→ document_chunks
                                              │
                                              ▼
                                    Embedder ──→ Qdrant (collection by domain)
                                              │
                                              ▼
                                    document_processing_events (audit trail)
```

## Qdrant Collection → PostgreSQL Payload Mapping

Every Qdrant point payload contains:

| Payload Field       | Resolves To                        |
|---------------------|------------------------------------|
| document_id         | documents.id                       |
| document_chunk_id   | document_chunks.id                 |
| project_id          | projects.id                        |
| vendor_id           | vendors.id                         |
| category            | documents.document_category        |
| csi_division        | csi_divisions.division_code        |
| source_system       | documents.source_system            |
| storage_bucket      | documents.storage_bucket           |
| storage_object_key  | documents.storage_object_key       |
| page_number         | document_chunks.page_number        |
| title               | documents.title                    |
| document_date       | documents.document_date            |
| confidentiality_level | documents.confidentiality_level  |

## MinIO Bucket Usage

| Bucket                    | Contents                              |
|---------------------------|---------------------------------------|
| hci-raw-documents         | All incoming files, unprocessed       |
| hci-processed-documents   | Extracted text, normalized outputs    |
| hci-ai-artifacts          | AI summaries, leveling reports, logs  |
| hci-backups               | Postgres dumps, snapshot exports      |
| hci-ingestion-quarantine  | Failed or suspicious files            |

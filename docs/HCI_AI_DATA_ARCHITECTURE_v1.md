# HCI AI Data Architecture v1.0

## Principle

Every piece of HCI construction intelligence has one home. Files live in MinIO. Structure lives in PostgreSQL. Meaning lives in Qdrant. Speed lives in Redis. Nothing lives only in chat history.

## The Four-Layer Rule

| What | Where | Why |
|------|-------|-----|
| Files (PDFs, DOCX, photos) | MinIO | Binary storage — Postgres is not a file server |
| Structured facts (projects, vendors, bids, costs) | PostgreSQL | Relational queries, reports, audit trail |
| Meaning (semantic search, AI recall) | Qdrant | Vector similarity, document retrieval |
| Temporary state (queues, sessions, rate limits) | Redis | Fast, ephemeral — not for persistence |

## Data Flow

```
SOURCE (Drive / Outlook / Manual)
    ↓
MinIO: hci-raw-documents (store raw file)
    ↓
PostgreSQL: documents (metadata row, processing_status = 'new')
    ↓
Extractor (pdfplumber / python-docx / openpyxl)
    ↓
MinIO: hci-processed-documents (extracted text artifact)
    ↓
Chunker (800 chars, 100 overlap)
    ↓
PostgreSQL: document_chunks (chunk metadata)
    ↓
Embedder (BAAI/bge-small-en-v1.5, 384-dim)
    ↓
Qdrant: domain collection (vector + payload)
    ↓
PostgreSQL: document_chunks.qdrant_point_id (cross-reference)
    ↓
documents.embedding_status = 'embedded'
```

## Integration Sources (read-only daily syncs)

| Source | Sync Table | Qdrant | Frequency |
|--------|-----------|--------|-----------|
| HubSpot | hubspot_deals, hubspot_notes, hubspot_tasks | hci_project_documents | Daily |
| Houzz | houzz_projects, houzz_daily_logs | hci_project_documents | Daily |
| Google Drive | drive_sync_log | hci_project_documents | Weekly (Monday) |

## Object Key Standard

```
{project_number}/{category}/{yyyy}/{yyyymmdd}_{source}_{title}_{version}.{ext}

Examples:
  1355R/bids/2026/260625_sub_xyz_concrete_proposal_v01.pdf
  hci-company/sop/2026/260625_sop_bid_leveling_v01.md
  64EW/drawings/2026/260625_architectural_set_v02.pdf
```

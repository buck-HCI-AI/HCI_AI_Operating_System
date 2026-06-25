# Knowledge Ingestion Engine v1

## Overview

The Knowledge Ingestion Engine (KIE) processes any supported document through a 6-stage pipeline, ensuring every file has: a metadata record in PostgreSQL, a raw copy in MinIO, extracted text in MinIO (processed bucket), and searchable vector chunks in Qdrant.

## Pipeline Stages

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  1. Capture │────▶│ 2. Classify │────▶│  3. Store   │
│             │     │             │     │   (MinIO)   │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
┌─────────────┐     ┌─────────────┐     ┌──────▼──────┐
│ 6. Archive  │◀────│ 5. Register │◀────│  4. Index   │
│  (log)      │     │ (Postgres)  │     │  (Qdrant)   │
└─────────────┘     └─────────────┘     └─────────────┘
```

### Stage 1 — Capture
- Validates file extension against `ALLOWED_EXTENSIONS`
- Enforces 250 MB file size limit
- Returns raw bytes + filename

**Allowed extensions:** `.pdf .docx .xlsx .xls .txt .md .csv .jpg .jpeg .png .tiff`

### Stage 2 — Classify
Extracts metadata from filename + first 2,000 chars of content:
- **project_number** — matches project address/name keywords against active projects in DB
- **document_category** — keyword patterns from `classifier.CATEGORY_PATTERNS`
- **csi_division** — CSI MasterFormat division code from content keywords
- **version_label** — parsed from filename suffix (`v01`, `_v2`, `rev3`, etc.)
- **document_date** — `YYYYMMDD` prefix in filename → ISO date

### Stage 3 — Store
1. Compute SHA-256 checksum
2. Check `documents` table for duplicate (by checksum) — return early if found
3. Upload raw file to `hci-raw-documents` MinIO bucket
4. Object key format: `{project}/{category}/{yyyy}/{yyyymmdd}_{filename}`

### Stage 4 — Index
1. Extract text via `extractor.py` (pdf, docx, xlsx, txt, md, csv)
2. Chunk at 800 chars / 100-char overlap
3. Embed with `BAAI/bge-small-en-v1.5` (384 dims, local)
4. Upsert into Qdrant collection (routed by category — see table below)

### Stage 5 — Register
Insert or upsert row into PostgreSQL `documents` table.
Gracefully skips if the new UUID-keyed schema hasn't been applied yet.

### Stage 6 — Archive
Writes final `document_processing_events` row: `event_type=complete, event_status=completed`.

## Qdrant Collection Routing

| Category | Collection |
|----------|-----------|
| drawings, specifications, bids, contracts, change_orders, rfis, submittals | `hci_project_documents` |
| meeting_minutes, daily_reports, budgets, schedules, client_correspondence | `hci_project_documents` |
| vendor_correspondence | `hci_vendor_intelligence` |
| procurement | `hci_procurement` |
| sop | `hci_sops` |
| historical_project | `hci_historical_costs` |
| template, registry, photos, unknown | `hci_project_documents` |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/ingest/file` | Upload file (multipart form) |
| `POST` | `/ingest/path` | Ingest local file by path |
| `POST` | `/ingest/batch` | Ingest all files in a directory |

### POST /ingest/file
```bash
curl -X POST http://localhost:8000/ingest/file \
  -F "file=@/path/to/doc.pdf" \
  -F "source_system=api" \
  -F "project_hint=64EW"
```

### POST /ingest/path
```bash
curl -X POST "http://localhost:8000/ingest/path?path=/path/to/doc.pdf&project_hint=64EW"
```

### POST /ingest/batch
```bash
curl -X POST "http://localhost:8000/ingest/batch?directory=/Volumes/HCI_AI_DEV/00_Incoming"
```

## Response Format
```json
{
  "status": "ingested",
  "document_id": "uuid",
  "checksum": "sha256hex",
  "minio_object_key": "64EW/bids/2026/20260619_bid_framing.pdf",
  "chunks": 14,
  "qdrant_collection": "hci_project_documents",
  "classification": {
    "project_number": "64EW",
    "document_category": "bids",
    "csi_division": "06",
    "version_label": "v1",
    "document_date": "2026-06-19",
    "original_filename": "20260619_bid_framing.pdf"
  }
}
```

Status values: `ingested` | `duplicate` | `failed`

## Module Files

| File | Purpose |
|------|---------|
| `ingestion/ingest.py` | Pipeline entry point (`ingest_file`, `ingest_bytes`, `ingest_directory`) |
| `ingestion/classifier.py` | Project/category/CSI/version/date detection |
| `ingestion/extractor.py` | Text extraction (pdf/docx/xlsx/txt/md) |
| `api/routers/ingest.py` | FastAPI router — mounts at `/ingest` |

## Error Handling

- Stage failure writes `document_processing_events` row with `event_status='failed'`
- Failed raw files are NOT deleted from MinIO
- Every ingested file returns `document_id` even on partial failure — enables retry
- MinIO unavailable → file still indexed in Qdrant (object_key stored as empty string)
- Postgres `documents` table missing → file indexed in Qdrant only (graceful degradation)

## Batch Ingestion — 00_Incoming

Drop files in `/Volumes/HCI_AI_DEV/00_Incoming/`, then:
```bash
curl -X POST "http://localhost:8000/ingest/batch?directory=/Volumes/HCI_AI_DEV/00_Incoming"
```
Move ingested files to `02_Project_Documents/{project_number}/` when done.

## Future Enhancements (Phase 2)

- Claude Haiku classifier: replace keyword matching with AI-assisted category + project detection
- OCR pipeline for images and scanned PDFs (pytesseract or Azure Document Intelligence)
- Near-duplicate detection via Qdrant cosine similarity threshold
- Outlook attachment auto-ingestion on email arrival (Graph API webhook)
- Automatic move from `00_Incoming` → `02_Project_Documents` after successful ingestion

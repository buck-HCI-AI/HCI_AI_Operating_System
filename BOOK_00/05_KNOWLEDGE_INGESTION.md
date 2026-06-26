# BOOK_00 § 05 — Knowledge Ingestion and Document Intelligence

**Status:** ✅ Pipeline built. API trigger endpoint needs wiring (Phase 8.2).

---

## Purpose

Every document, field note, bid, meeting, and email that enters HCI becomes searchable institutional memory. The ingestion pipeline is the mechanism that makes this happen.

---

## Pipeline Code

| File | Role |
|------|------|
| `03_Source_Code/ingestion/classifier.py` | Determine document category and project from filename + content |
| `03_Source_Code/ingestion/extractor.py` | Extract text from PDF, DOCX, XLSX, images |
| `03_Source_Code/ingestion/ingest.py` | Orchestrate: classify → extract → embed → store → register |
| `03_Source_Code/ingestion/ingest_memory.py` | Vectorize records from Postgres into Qdrant |
| `03_Source_Code/ingestion/create_collections.py` | Initialize Qdrant collections |
| `03_Source_Code/ingestion/run_ingestion.py` | Batch runner script |
| `03_Source_Code/ingestion/seed_postgres.py` | Seed Postgres from HubSpot/Sheets |

---

## Document Intelligence Service (API layer)

**Base path:** `/api/v1/services/document-intelligence`

| Endpoint | Purpose |
|----------|---------|
| `GET /search?q=...` | Semantic search across hci_project_documents + hci_sops |
| `GET /classify?filename=...&content_preview=...` | Classify a document without storing |
| `POST /ingest` | Full pipeline: classify → extract → store → embed → register |

**Gap (Phase 8.2):** `ingest_document()` in the service currently does not call `ingest.py`. It must be wired end-to-end before workflows depend on it.

---

## Qdrant Collection Routing

| Content type | Collection |
|-------------|-----------|
| Google Drive documents | `drive_memory` |
| Project-specific context | `project_memory` |
| Bid documents | `bid_memory` |
| Vendor profiles | `vendor_memory` |
| Lessons learned | `lessons_learned` |
| Classified project docs | `hci_project_documents` |
| SOPs | `hci_sops` |
| Historical costs | `hci_historical_costs` |

---

## Embedding

**Model:** `BAAI/bge-small-en-v1.5` (fastembed, local, no API key)  
**Dimensions:** 384  
**Chunk size:** ~500 tokens with 50-token overlap  
**Metadata stored per vector:** project_id, category, source_path, created_at

---

## Ingestion Sources and Frequency

| Source | Frequency | Method |
|--------|-----------|--------|
| Google Drive | Weekly (Sunday) | `sync_drive.py` |
| Bid emails (attachments) | Real-time (WF-006) | Attachment extraction — Phase 9.4 |
| Field photos | On capture (WF-SUPER) | Photo → MinIO → metadata only |
| Meeting transcripts | On submission (WF-002) | `POST /workflows/wf002/meeting` |
| Daily logs | On submission (WF-SUPER) | Auto-vectorize on save |
| Manual / API | On demand | `POST /document-intelligence/ingest` |

---

## Architecture Rule

**No workflow creates its own ingestion logic.** All document storage and vectorization flows through this pipeline. Workflows call the Document Intelligence Service endpoint — they do not write to MinIO or Qdrant directly.

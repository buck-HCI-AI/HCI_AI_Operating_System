# WORKFLOW 01 — Document Ingestion

## Purpose

Register, store, extract, and embed any document that enters the HCI AI system. Ensure every file has a metadata record in PostgreSQL, a stored object in MinIO, and searchable chunks in Qdrant.

## Trigger Sources

| Source | Mechanism | Status |
|--------|-----------|--------|
| Google Drive | Weekly sync (`sync_drive.py`) | ✅ Built |
| Outlook attachments | Graph API attachment download | 🔜 Planned |
| Manual upload | POST /documents/ingest API | 🔜 Planned |
| Repository files | Batch ingest script | 🔜 Planned |

## Steps

### Step 1 — Receive File
- Accept file path (Drive mount) or binary stream (API)
- Record `source_system`, `source_uri`, `original_filename`
- Check `DOCUMENT_ALLOWED_EXTENSIONS` (pdf, docx, xlsx, pptx, txt, md, csv, jpg, jpeg, png, tiff)
- Check file size ≤ `DOCUMENT_MAX_FILE_SIZE_MB` (250 MB)
- On failure: write to `hci-ingestion-quarantine`, log event, stop

### Step 2 — Compute Checksum
```python
import hashlib
sha256 = hashlib.sha256(file_bytes).hexdigest()
```

### Step 3 — Duplicate Detection
```sql
SELECT id FROM documents
WHERE checksum_sha256 = $sha256
  AND (storage_bucket = 'hci-raw-documents'
       OR google_drive_file_id = $gdrive_id);
```
If duplicate found: log `duplicate_check` event, skip ingestion, return existing `document_id`.

### Step 4 — Classify
- Match filename + content preview against project aliases → `project_id`
- Detect category from filename keywords → `document_category`
- Detect CSI division from content → `csi_division_id`
- Parse version from filename suffix (v01, v02...) → `version_label`
- Parse date from filename YYYYMMDD prefix → `document_date`

### Step 5 — Store Raw File in MinIO
```
bucket:  hci-raw-documents
key:     {project_number}/{category}/{yyyy}/{yyyymmdd}_{source}_{title}_{ver}.{ext}
```
Log `store_raw` event on success/failure.

### Step 6 — Create PostgreSQL Record
```sql
INSERT INTO documents (title, document_category, original_filename, normalized_filename,
    checksum_sha256, storage_bucket, storage_object_key, processing_status, ...)
VALUES (...) RETURNING id;
```
`processing_status = 'extracted'` after successful store.

### Step 7 — Extract Text
| Format | Extractor |
|--------|-----------|
| .pdf | pdfplumber |
| .docx | python-docx |
| .xlsx | openpyxl |
| .txt / .md | direct read |
| .jpg / .png | (future: OCR) |

Set `extracted_text_available = TRUE` on success.

### Step 8 — Store Extracted Text in MinIO
```
bucket:  hci-processed-documents
key:     same path as raw, extension → .txt
```
Log `store_processed` event.

### Step 9 — Chunk Text
```python
CHUNK_SIZE = 800
OVERLAP = 100
# Slide window, preserve word boundaries
```

### Step 10 — Embed and Store in Qdrant
```python
vectors = embedder.embed(chunk_texts)   # BAAI/bge-small-en-v1.5
qdrant.upsert(collection, PointStruct(
    id=...,
    vector=vec,
    payload={
        "document_id": doc_id,
        "document_chunk_id": chunk_id,
        "project_id": ...,
        "category": ...,
        "csi_division": ...,
        ...
    }
))
```

### Step 11 — Update Status
```sql
UPDATE documents SET
    processing_status = 'extracted',
    embedding_status = 'embedded',
    extracted_text_available = TRUE
WHERE id = $doc_id;
```

### Step 12 — Log Completion
Insert final `document_processing_events` row: `event_type = 'complete'`, `event_status = 'completed'`.

## Error Handling

Any step failure:
1. Log `document_processing_events` with `event_status = 'failed'`, `error_details = {error}`
2. Update `documents.processing_status = 'failed'`
3. Do NOT delete raw file from MinIO
4. Return error with `document_id` so retry is possible

## Future Enhancements

- Outlook attachment auto-ingestion on email arrival
- AI-enhanced classifier (Claude Haiku for category/CSI detection)
- OCR for images and scanned PDFs
- Duplicate similarity detection (near-duplicate via Qdrant cosine threshold)

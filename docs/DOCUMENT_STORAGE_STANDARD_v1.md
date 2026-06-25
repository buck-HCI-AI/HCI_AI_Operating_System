# Document Storage Standard v1.0

## MinIO Bucket Assignment

| Bucket | Contents | Who Writes |
|--------|----------|-----------|
| `hci-raw-documents` | All incoming files unmodified | Ingestion pipeline (step 1) |
| `hci-processed-documents` | Extracted text, normalized outputs | Extractor (step 3) |
| `hci-ai-artifacts` | AI summaries, leveling reports, analysis | AI workflows |
| `hci-backups` | Postgres dumps, export snapshots | Backup scripts |
| `hci-ingestion-quarantine` | Failed, suspicious, or unrecognized files | Ingestion error handler |

## Rules

1. Raw file always goes to `hci-raw-documents` first — never skip this step.
2. Processed/extracted files go to `hci-processed-documents` — never overwrite raw.
3. AI outputs (leveling summaries, Claude responses) go to `hci-ai-artifacts`.
4. A `documents` row in PostgreSQL must exist before any MinIO write is finalized.
5. SHA-256 checksum is computed before upload and stored in `documents.checksum_sha256`.
6. Duplicate detection: check `checksum_sha256 + storage_bucket` uniqueness before inserting.
7. Failed ingestion: move file to `hci-ingestion-quarantine` and record error in `document_processing_events`.

## Object Key Format

```
{project_number_or_company}/{document_category}/{yyyy}/{yyyymmdd}_{source}_{normalized_title}_{version}.{ext}
```

- `project_number`: 64EW, 101F, 1355R, 83SB — or `hci-company` for company-level docs
- `document_category`: from the canonical category list (drawings, bids, contracts, etc.)
- `source`: sub (subcontractor), hci, owner, ai, arch (architect), eng (engineer)
- `normalized_title`: lowercase, underscores, no special chars, max 40 chars
- `version`: v01, v02, v03...

## File Size Limit

250 MB per file. Files exceeding this go to quarantine with a size-exceeded event.

## Allowed Extensions

`pdf, docx, xlsx, pptx, txt, md, csv, jpg, jpeg, png, tiff`

# Document Metadata Standard v1.0

## Required Fields (every document)

| Field | Type | Rule |
|-------|------|------|
| `title` | TEXT | Human-readable document title |
| `document_category` | TEXT | Must match canonical category list |
| `original_filename` | TEXT | Exact filename as received |
| `normalized_filename` | TEXT | Formatted per object key standard |
| `checksum_sha256` | TEXT | Computed before upload |
| `storage_bucket` | TEXT | MinIO bucket name |
| `storage_object_key` | TEXT | Full MinIO object path |
| `processing_status` | TEXT | Always set on insert |

## Classification Fields (set during ingestion)

| Field | Populated By | How |
|-------|-------------|-----|
| `project_id` | Classifier | Keyword match on filename/content vs. project aliases |
| `company_id` | Classifier | HubSpot company lookup |
| `vendor_id` | Classifier | Vendor registry lookup |
| `csi_division_id` | Classifier | CSI keyword match in title or content |
| `document_date` | Extractor | Parse from content or filename |
| `version_label` | Parser | Detect from filename suffix |

## Processing Status Flow

```
new → queued → extracting → extracted → chunking → chunked → embedding → embedded
                                                                              ↓
                                                                           failed (any stage)
```

## Embedding Status Flow

```
not_embedded → queued → embedding → embedded
                                  ↓
                               failed
```

## Versioning

- Each new version of a document gets a new `documents` row
- Set `supersedes_document_id` = previous version's UUID
- Set `is_current_version = FALSE` on the superseded row
- `version_label` format: `v01`, `v02`, `v03`

## Confidentiality Levels

| Level | Meaning |
|-------|---------|
| `public` | Can be shared freely |
| `internal` | HCI internal use only (default) |
| `confidential` | Owner/contract-sensitive |

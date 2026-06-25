# Document Intelligence Architecture

## Phase 1 — Foundation (current)

The ingestion pipeline scaffolding and metadata schema exist. Full AI extraction is not built yet (out of scope per directive). The interfaces are defined so the AI extraction engine can be dropped in.

## Ingestion Pipeline Interface

```
┌─────────────────────────────────────────────────────┐
│           DOCUMENT INGESTION PIPELINE                │
│                                                      │
│  1. RECEIVE ──── source: Drive/Outlook/Manual/API    │
│        ↓                                             │
│  2. VALIDATE ─── checksum, size, extension check     │
│        ↓                                             │
│  3. DEDUPLICATE ─ checksum + source_uri lookup       │
│        ↓                                             │
│  4. CLASSIFY ──── project, vendor, category, CSI     │
│        ↓                                             │
│  5. STORE RAW ─── MinIO: hci-raw-documents           │
│        ↓                                             │
│  6. REGISTER ──── PostgreSQL: documents row          │
│        ↓                                             │
│  7. EXTRACT ───── pdfplumber/docx/openpyxl           │
│        ↓                                             │
│  8. STORE TEXT ── MinIO: hci-processed-documents     │
│        ↓                                             │
│  9. CHUNK ──────── 800 chars, 100 overlap            │
│        ↓                                             │
│  10. EMBED ─────── BAAI/bge-small-en-v1.5 (384-dim) │
│        ↓                                             │
│  11. STORE VECTOR ─ Qdrant (domain collection)       │
│        ↓                                             │
│  12. UPDATE STATUS ─ processing_status = embedded    │
│        ↓                                             │
│  13. AUDIT TRAIL ── document_processing_events       │
└─────────────────────────────────────────────────────┘
```

## Classifier Rules (Phase 1 — keyword-based)

### Project Classification
Match against `projects.project_aliases` array:
- `['64 Eastwood Dr', 'Eastwood', '64EW']` → project_id = 64EW
- `['1355 Riverside Dr', 'Riverside', '1355R']` → project_id = 1355R

### Category Classification
| Signal | Category |
|--------|----------|
| "bid", "proposal", "quote" in filename | `bids` |
| "contract", "agreement", "subcontract" | `contracts` |
| "drawing", "plan", "elevation", "section" | `drawings` |
| "sop", "standard operating" | `sop` |
| "daily", "field report", "log" | `daily_reports` |
| "meeting", "minutes" | `meeting_minutes` |

### CSI Classification
Match trade keywords against `csi_divisions.division_name`:
- "framing", "carpentry", "millwork" → Division 06
- "drywall", "tile", "flooring", "paint" → Division 09
- "plumbing", "hvac", "mechanical" → Division 15

## Phase 2 — AI-Enhanced Classification (future)

Drop-in upgrade: replace keyword classifier with Claude API call:
```python
# Future: classify_with_ai(filename, text_preview) → {project, category, csi}
```

All metadata fields already exist. Only the classifier changes.

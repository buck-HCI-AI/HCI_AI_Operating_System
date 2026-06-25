# Embedding and Search Standard v1.0

## Embedding Model

**BAAI/bge-small-en-v1.5** — 384-dimensional vectors, local inference via `fastembed`.
No API key required. Runs on-device (MacBook Air M5, Mac mini M4 Pro).

## Qdrant Collections

| Collection | Domain | What Gets Embedded |
|-----------|--------|-------------------|
| `hci_book00` | BOOK_00 engineering manual | Chapter sections, principles, procedures |
| `hci_sops` | Standard Operating Procedures | SOP steps, checklists, guidance |
| `hci_project_documents` | All project-level docs | Bids, specs, meeting notes, daily logs |
| `hci_vendor_intelligence` | Vendor knowledge | Vendor profiles, performance notes, bid history |
| `hci_historical_costs` | Historical cost data | Cost records, benchmarks, cost summaries |
| `hci_lessons_learned` | Lessons learned | Issue + root cause + recommendation text |
| `hci_procurement` | Procurement intelligence | Long lead items, owner selections, procurement notes |

## Chunking Standard

- Chunk size: **800 characters**
- Overlap: **100 characters**
- Preserve section boundaries when possible
- Include document title + category in chunk metadata

## Required Qdrant Payload Fields

Every point stored in Qdrant must include:

```json
{
  "document_id":          "uuid",
  "document_chunk_id":    "uuid",
  "project_id":           "uuid or null",
  "vendor_id":            "uuid or null",
  "category":             "bids",
  "csi_division":         "06",
  "source_system":        "google_drive",
  "storage_bucket":       "hci-processed-documents",
  "storage_object_key":   "1355R/bids/2026/260625_sub_xyz_framing_v01.txt",
  "page_number":          3,
  "title":                "Rough Framing Bid — XYZ Carpentry",
  "document_date":        "2026-06-25",
  "confidentiality_level": "internal"
}
```

## Search Query Routing

| Query Type | Collection(s) | Notes |
|-----------|--------------|-------|
| "What did framing cost on Eastwood?" | hci_historical_costs, hci_project_documents | Filter by project_id |
| "Show me all bids from XYZ Carpentry" | hci_project_documents, hci_vendor_intelligence | Filter by vendor_id |
| "What's the SOP for bid leveling?" | hci_sops, hci_book00 | No project filter |
| "What lessons learned apply to masonry?" | hci_lessons_learned | Filter by csi_division = '04' |

## Resolving a Search Result

Every Qdrant hit can be fully resolved:
1. `document_id` → `SELECT * FROM documents WHERE id = {document_id}`
2. `storage_object_key` → `mc get hci-processed-documents/{key}`
3. `document_chunk_id` → `SELECT chunk_text FROM document_chunks WHERE id = {chunk_id}`

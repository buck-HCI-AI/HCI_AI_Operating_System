# BOOK_00 § 04 — Storage and Document Lifecycle

**Status:** ✅ MinIO live. Drive configured. Ingestion pipeline partially wired.

---

## Storage Layers

| Layer | Technology | Purpose | Location |
|-------|-----------|---------|---------|
| Object storage | MinIO | All files (docs, photos, reports, backups) | localhost:9000 |
| Dev drive | WD My Passport SSD | Docker volumes, hot data | /Volumes/HCI_AI_DEV |
| Vector store | Qdrant | Searchable document chunks | localhost:6333 |
| Database | PostgreSQL | Document metadata, registry | localhost:5432 |
| External source | Google Drive | Project document source | Cloud (read-only) |

---

## Document Lifecycle

```
SOURCE (Drive / Email / Field / Upload)
    │
    ▼
RECEIVE — file path or binary stream + source metadata
    │
    ▼
CLASSIFY — category, project, CSI division, document type
    │       (03_Source_Code/ingestion/classifier.py)
    ▼
EXTRACT — text content, metadata
    │       (03_Source_Code/ingestion/extractor.py)
    ▼
STORE — MinIO object (hci-documents bucket)
    │
    ▼
REGISTER — PostgreSQL documents row (path, hash, category, project_id)
    │
    ▼
EMBED — Qdrant vectors (384-dim chunks, metadata filter)
    │       (03_Source_Code/ingestion/ingest.py)
    ▼
INDEX — searchable via /api/v1/search or Intelligence Services
```

---

## Trigger Points

| Trigger | Source | Handler |
|---------|--------|---------|
| Drive sync (weekly) | `sync_drive.py` | Batch ingest new Drive files |
| API upload | `POST /api/v1/services/document-intelligence/ingest` | On-demand ingest |
| Email attachment | WF-006 inbox review | Detect attachments, queue for ingest |
| Field photo | WF-SUPER (planned) | Photo → MinIO hci-photos bucket |
| Manual script | `run_ingestion.py` | Bulk ingest from local path |

---

## Document Classification Categories

| Category | Description |
|----------|-------------|
| `bid_proposal` | Subcontractor bid submissions |
| `contract` | Owner and sub contracts |
| `drawing` | Architectural/structural drawings |
| `specification` | Project specifications |
| `submittal` | Material submittals |
| `rfi` | Requests for Information |
| `daily_log` | Field daily logs |
| `meeting_minutes` | Meeting summaries |
| `correspondence` | Emails and letters |
| `invoice` | Invoices and pay apps |
| `photo` | Field photos |
| `report` | Generated reports |
| `sop` | Standard operating procedures |

---

## File Naming Convention

MinIO objects follow: `{project_code}/{category}/{YYYY-MM-DD}_{original_filename}`

Example: `64EW/bid_proposal/2026-06-23_high_con_concrete_proposal.pdf`

---

## Backup

Daily backup (planned, Phase 14):
- `pg_dump hci_os` → MinIO `hci-backups/postgres/YYYY-MM-DD.sql.gz`
- Qdrant snapshot → MinIO `hci-backups/qdrant/YYYY-MM-DD/`
- Retention: 30 days

---

## Future: 4 TB Storage Migration

Current HCI_AI_DEV is 1 TB WD My Passport. When system moves to Mac mini (Phase 11), target is a 4 TB NAS or internal SSD with the same folder structure. Migration: copy `/Volumes/HCI_AI_DEV` to new mount, update `HCI_STORAGE_ROOT` in `.env`, restart.

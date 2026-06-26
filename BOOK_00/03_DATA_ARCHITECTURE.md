# BOOK_00 § 03 — Data Architecture

**Status:** ✅ Core schema live. New tables added 2026-06-25.

---

## PostgreSQL Database: `hci_os`

**User:** `hci_admin`  
**Schema files:** `database/schema/`

### Core Tables

| Table | Rows | Purpose |
|-------|------|---------|
| `projects` | 4 | Master project registry (id, name, address, status, scope, hubspot_deal_id) |
| `vendors` | 392 | HCI vendor roster (company_name, trade, tier, hubspot_contact_id) |
| `bid_packages` | 119 | CSI-organized bid packages per project |
| `bid_entries` | 26 | Actual bids received (amount, status, notes, vendor_id FK) |
| `meetings` | 0 | Meeting records (title, date, summary, action_items, transcript_path) |
| `daily_logs` | 0 | Field daily logs (date, weather, work_performed, issues) |
| `hubspot_deals` | 306 | Synced HubSpot deals |
| `hubspot_notes` | 3 | Synced HubSpot deal notes |
| `hubspot_tasks` | — | Synced HubSpot tasks |
| `lessons_learned` | 1 | Captured lessons (title, category, csi_division, outcome) |
| `risks` | 0 | Project risks (type, severity, description, mitigation, status) |
| `long_lead_items` | 0 | Procurement long-lead tracking |
| `procurement_items` | 0 | PO tracking (vendor, amount, required_date, status) |
| `historical_cost_records` | 0 | Bid vs. actual costs per package |
| `drive_sync_log` | — | Google Drive sync history |

### Key Relationships

```
projects (1) ──── (many) bid_packages
bid_packages (1) ── (many) bid_entries ──── vendors
projects (1) ──── (many) meetings
projects (1) ──── (many) daily_logs
projects (1) ──── (many) risks
projects (1) ──── (many) long_lead_items
projects (1) ──── (many) procurement_items
projects (1) ──── hubspot_deals (via hubspot_deal_id)
```

### Known Gap: vendor_id on bid_entries

All 26 current `bid_entries` rows have `vendor_id = NULL`. Vendor names are in the `notes` text field. This must be fixed in Phase 8.1 by matching vendor names during sync.

---

## Qdrant Vector Store

| Collection | Vectors | Purpose |
|-----------|---------|---------|
| `drive_memory` | ~2,335 | Google Drive documents, all projects |
| `project_memory` | ~310 | Project-specific context |
| `bid_memory` | ~26 | Bid documents and notes |
| `vendor_memory` | ~392 | Vendor profiles and history |
| `lessons_learned` | 1 | Captured lessons |
| `hci_project_documents` | — | Classified project docs |
| `hci_vendor_intelligence` | — | Vendor intelligence |
| `hci_sops` | — | Standard operating procedures |

**Embedding model:** `BAAI/bge-small-en-v1.5` (384 dimensions, local via fastembed)  
**No API key required for embedding.**

---

## MinIO Object Store

| Bucket | Purpose |
|--------|---------|
| `hci-documents` | All project documents |
| `hci-reports` | Generated reports and exports |
| `hci-photos` | Field photos (future) |
| `hci-backups` | Database backups |
| `hci-temp` | Staging / processing |

---

## Project Resolution Convention

Projects are identified in the system by a short code (e.g., `64EW`, `1355RV`, `101F`). The `projects` table has no `project_number` column. All services use `BaseIntelligenceService.resolve_project_id()` which extracts the numeric prefix and does an ILIKE match on `projects.name`.

```python
# "64EW" → extracts "64" → matches "64 Eastwood"
# "1355RV" → extracts "1355" → matches "1355 Riverside"
```

---

## Data Flow Rules

1. **HubSpot → Postgres** (read-only sync): contacts, deals, notes sync into Postgres at startup. Never write back without Buck's approval.
2. **Google Drive → Qdrant/MinIO** (weekly sync): documents extracted, embedded, stored.
3. **Field input → Postgres + Qdrant** (real-time): daily logs, meetings, bid entries go to Postgres first, then queue for vectorization.
4. **Google Sheets → RETIRING**: WF-007 currently reads bid data from Google Sheets. Migration to Postgres `bid_entries` is Phase 9.4.

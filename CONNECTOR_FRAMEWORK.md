# Universal Connector Framework
## HCI AI Operating System

**Authority:** Chief Architect Directive — Phase II (Objective 5)  
**Owner:** Buck Adams  
**Reference Implementation:** Houzz (certified after Sprint 2 data load)

---

## Purpose

Every external system HCI integrates with follows this framework.
No custom one-off integrations. Every connector is a first-class citizen.

---

## The 7-Stage Pipeline

```
External System
      ↓
  1. CONNECTOR         Read-only extraction. Browser or API.
      ↓
  2. VALIDATION        Field types, required fields, referential integrity.
      ↓
  3. NORMALIZATION     Map to HCI canonical schema.
      ↓
  4. PERSISTENCE       Idempotent upsert to PostgreSQL via ingestion endpoint.
      ↓
  5. MINING            Intelligence extraction. Dry-run by default.
      ↓
  6. KNOWLEDGE GRAPH   Relationships, vendor intelligence, project links.
      ↓
  7. EXECUTIVE REPORT  KPIs surfaced in Executive Inbox + Command Center.
```

---

## Connector Registry

| Connector | Stage | Status | Ingestion Endpoint | Miner |
|---|---|---|---|---|
| **Houzz** | All 7 | 🟡 Stage 4 pending data | `POST /api/v1/services/houzz/ingest` | HouzzMiner (paused) |
| **HubSpot** | 1–5 active | 🟢 Live | Native (hubspot_integration service) | HubSpotMiner (live) |
| **Google Drive** | 1–5 active | 🟢 Live | Native (google_drive_integration) | DriveMiner (live) |
| **Microsoft 365** | 1–3 active | 🟢 Live | Native (OutlookMiner) | OutlookMiner (live) |
| QuickBooks | Not started | ⚪ Sprint 5 | TBD | TBD |
| Procore | Not started | ⚪ Sprint 5 | TBD | TBD |
| Autodesk | Not started | ⚪ Sprint 5+ | TBD | TBD |

---

## Stage Specifications

### Stage 1 — Connector

**Rule:** Never writes to the source system. Extraction only.

| Property | Requirement |
|---|---|
| Auth method | API key, OAuth, or Browser extraction |
| Read-only | Enforced — no POST/PUT/DELETE to source |
| Rate limiting | Respect source system rate limits |
| Session handling | Managed by connector, not by Buck |
| Failure behavior | Log failure, continue with other connectors |

**Houzz:** Browser Claude (read-only, no Houzz API)  
**HubSpot:** REST API (`HUBSPOT_API_KEY` from `.env`)  
**Drive:** Google API (`google_oauth_token.json`)  
**365:** Microsoft Graph API (`GRAPH_CLIENT_ID` etc. from `.env`)

---

### Stage 2 — Validation

Every record validated before persistence:

| Check | Rule |
|---|---|
| Required fields | Reject record if missing — add to `validation_errors` |
| ID format | Must be non-empty string |
| Date format | YYYY-MM-DD only |
| Referential integrity | Parent record must exist (e.g., project_id in logs must exist in projects) |
| Duplicate detection | Check via ON CONFLICT — count as `duplicate`, not error |
| Future dates | Flag as warning, do not reject |
| Data type | String, int, float, JSON — coerce where safe |

---

### Stage 3 — Normalization

Map source schema to HCI canonical fields.

**Canonical project fields:** `id`, `name`, `status`, `client_name`, `address`, `project_type`  
**Canonical date fields:** Always `YYYY-MM-DD`  
**Canonical ID:** `{source}_{source_id}` (e.g., `houzz_3218059`, `hs_deal_331240861419`)

Each connector maintains a field mapping document:
- `houzz/HOUZZ_FIELD_MAPPING.md`
- `integrations/hubspot/HUBSPOT_FIELD_MAPPING.md` (future)

---

### Stage 4 — Persistence

**Rule:** Always idempotent. Re-running never corrupts data.

Standard ingestion endpoint pattern:
```
POST /api/v1/services/{connector}/ingest
POST /api/v1/imports/{connector}/ingest  (alias)
Header: X-API-Key: {from .env}
Body: { "source": "connector_name", "{objects}": [...], "extraction_notes": "..." }
Response: { "status": "ok|partial", "total_imported": N, "imported": {...}, "validation_errors": [...] }
```

PostgreSQL pattern: `ON CONFLICT ({id_field}) DO UPDATE SET ... synced_at = NOW()`

---

### Stage 5 — Mining

**Rule:** `dry_run=True` default. Explicit Buck authorization required for production writes.

Each connector has a dedicated miner:
- Reads from normalized tables (not from source system)
- Extracts intelligence: risks, lessons learned, vendor candidates, schedule variances
- Queues items to `approval_queue`
- Returns `MiningResult` with full metrics

---

### Stage 6 — Knowledge Graph

Relationships surfaced in the vector store (Qdrant):
- Project → Vendor relationships (who worked on what)
- Document → Project links
- Contact → Company relationships
- Historical cost → Current bid comparisons

Each mining run updates relevant Qdrant collections.

---

### Stage 7 — Executive Reporting

What surfaces in the Executive Dashboard / Inbox:
- New risks detected (project-level)
- Vendor candidates needing approval
- Schedule variances (days ahead/behind)
- Cost intelligence (bid vs. historical)
- ROI metrics (time saved per connector per week)

---

## Building a New Connector — Checklist

When a new connector is authorized (ACR required):

```
[ ] ACR approved by ChatGPT (Chief Architect)
[ ] Source system access credentials added to .env
[ ] Schema design: what tables get created?
[ ] Connector module: 03_Source_Code/integrations/{connector}/
[ ] Ingestion service: 03_Source_Code/services/{connector}_intelligence/
[ ] Routes registered in main.py
[ ] Miner class: 03_Source_Code/services/mining/{connector}_miner.py
[ ] Field mapping doc: {connector}/FIELD_MAPPING.md
[ ] Added to integration_registry table
[ ] Added to CONNECTOR_FRAMEWORK.md registry table
[ ] Health check included in AUTO-002
[ ] Executive reporting section in generate_command_center.py
[ ] Test: POST sample data, verify counts, dry_run mining
[ ] Gate 5 checklist item completed
```

---

## Houzz — Reference Implementation

The Houzz connector is the canonical example for all future connectors.

| Stage | Implementation | Status |
|---|---|---|
| Connector | Browser Claude (app.houzz.com read-only) | 🟡 Pending re-extraction |
| Validation | `houzz_svc.py` — required fields, date format, orphan check | ✅ |
| Normalization | `houzz_project_id`, `houzz_log_id`, `houzz_item_id` as canonical IDs | ✅ |
| Persistence | `POST /api/v1/services/houzz/ingest` — idempotent upsert | ✅ |
| Mining | `HouzzMiner` — paused until data loads | 🟡 Ready |
| Knowledge Graph | Qdrant `houzz_intelligence` collection — not yet populated | ⚪ After data load |
| Exec Reporting | `generate_command_center.py` includes Houzz section | ✅ |

---

*Universal Connector Framework | HCI AI Operating System | Hendrickson Construction, Inc.*  
*v1.0 — 2026-06-27 | All future integrations follow this standard.*

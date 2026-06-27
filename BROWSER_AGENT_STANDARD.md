# Browser Agent Standard
## HCI AI Operating System | Version 2.0 | 2026-06-27

---

## Core Principle

**Browser Agent = Discovery only. Claude Code = Validator/Persister.**

The Browser Agent never writes directly to the database. It extracts structured data from SaaS platforms (Houzz, HubSpot, QuickBooks, etc.), produces canonical JSON, and calls the ingest API. Claude Code's connector framework validates, normalizes, and persists.

```
Browser Agent (Discovery)
    ↓  canonical JSON
POST /api/v1/services/connectors/{name}/ingest
    ↓
BaseConnector (Validate → Normalize → Persist → Mine)
    ↓
PostgreSQL (via connector, never Browser directly)
    ↓
n8n (events → downstream workflows)
    ↓
Executive Inbox (insights for Buck)
```

---

## Canonical JSON Format

Every Browser extraction MUST produce this wrapper:

```json
{
  "connector": "houzz",
  "extracted_at": "2026-06-27T14:30:00Z",
  "source_url": "https://app.houzz.com/projects/3218059",
  "project_id": "3218059",
  "dry_run": true,
  "extraction_notes": "Extracted 101 Francis St project — all 17 modules",
  "data": {
    "projects": [...],
    "daily_logs": [...],
    "schedule_items": [...],
    "files": [...],
    "time_entries": [...],
    "tasks": [...],
    "messages": [...],
    "budget": [...],
    "estimates": [...],
    "contracts": [...],
    "purchase_orders": [...],
    "change_orders": [...],
    "selections": [...],
    "vendors": [...],
    "contacts": [...],
    "team_members": [...],
    "subcontractors": [...]
  }
}
```

**Rules:**
- Always include `extracted_at` (ISO 8601 UTC)
- Always include `dry_run: true` — Claude Code will flip to `false` after validation
- Only include entity arrays that were actually extracted (omit empty arrays)
- Preserve raw platform data in `raw_data` field alongside normalized fields
- Use `null` for unknown values — never omit required ID fields

---

## Entity Schemas

### projects

```json
{
  "houzz_project_id": "3218059",
  "name": "101 Francis St Renovation",
  "client_name": "Smith Family",
  "status": "active",
  "address": "101 Francis St, Aspen CO 81611",
  "budget": 450000.00,
  "start_date": "2026-03-15",
  "end_date": "2026-09-30",
  "project_type": "residential_renovation",
  "properties": {},
  "raw_data": {}
}
```

### daily_logs

```json
{
  "houzz_log_id": "DL-3218059-20260627",
  "project_id": "3218059",
  "log_date": "2026-06-27",
  "content": "Framing complete on west wall. Electrical rough-in started.",
  "weather": "Sunny, 72F",
  "crew_size": 6,
  "author": "Buck Adams",
  "raw_json": {}
}
```

### schedule_items

```json
{
  "houzz_item_id": "SI-3218059-001",
  "project_id": "3218059",
  "title": "Framing — West Wing",
  "start_date": "2026-06-20",
  "end_date": "2026-07-05",
  "status": "in_progress",
  "parent_item_id": null,
  "assignee": "Mike Rodriguez",
  "completion_pct": 65.0,
  "task_type": "construction",
  "notes": "On schedule"
}
```

### files

```json
{
  "houzz_file_id": "F-3218059-001",
  "houzz_project_id": "3218059",
  "file_name": "West_Wall_Framing_20260627.jpg",
  "file_type": "photo",
  "category": "Progress Photos",
  "url": "https://app.houzz.com/photos/...",
  "thumbnail_url": null,
  "uploaded_by": "Buck Adams",
  "uploaded_at": "2026-06-27T10:15:00Z",
  "room": "Living Room",
  "tags": ["framing", "west-wall"],
  "raw_data": {}
}
```

### time_entries

```json
{
  "houzz_entry_id": "TE-3218059-20260627-001",
  "houzz_project_id": "3218059",
  "date": "2026-06-27",
  "worker_name": "Carlos Mendez",
  "role": "Framer",
  "hours": 8.5,
  "description": "West wall framing and header installation",
  "cost_code": "06-100",
  "billable": true,
  "raw_data": {}
}
```

### tasks

```json
{
  "houzz_task_id": "T-3218059-001",
  "houzz_project_id": "3218059",
  "title": "Install kitchen cabinet hardware",
  "description": "Pull handles on all upper and lower cabinets",
  "status": "open",
  "priority": "medium",
  "assigned_to": "Interior Team",
  "due_date": "2026-07-15",
  "completed_date": null,
  "is_punch_list": false,
  "location": "Kitchen",
  "raw_data": {}
}
```

### messages

```json
{
  "houzz_message_id": "MSG-3218059-001",
  "houzz_project_id": "3218059",
  "sender_name": "Sarah Smith",
  "sender_role": "client",
  "message_text": "Can we add a mudroom bench? Budget permitting.",
  "sent_at": "2026-06-26T16:45:00Z",
  "has_attachments": false,
  "thread_id": "THREAD-001",
  "raw_data": {}
}
```

### budget

```json
{
  "houzz_project_id": "3218059",
  "category": "Framing",
  "budgeted_amount": 85000.00,
  "actual_amount": 72000.00,
  "committed_amount": 85000.00,
  "as_of_date": "2026-06-27",
  "raw_data": {}
}
```

### estimates

```json
{
  "houzz_estimate_id": "EST-3218059-001",
  "houzz_project_id": "3218059",
  "estimate_number": "HCI-EST-001",
  "title": "Phase 1 — Structural & Framing",
  "status": "approved",
  "total_amount": 125000.00,
  "created_date": "2026-02-15",
  "sent_date": "2026-02-20",
  "approved_date": "2026-03-01",
  "client_name": "Smith Family",
  "raw_data": {}
}
```

### contracts

```json
{
  "houzz_contract_id": "CON-3218059-001",
  "houzz_project_id": "3218059",
  "contract_number": "HCI-2026-101F",
  "title": "101 Francis St Renovation Contract",
  "status": "signed",
  "contract_amount": 450000.00,
  "signed_date": "2026-03-10",
  "expiration_date": null,
  "counterparty": "Smith Family",
  "raw_data": {}
}
```

### purchase_orders

```json
{
  "houzz_po_id": "PO-3218059-001",
  "houzz_project_id": "3218059",
  "po_number": "PO-2026-001",
  "vendor_name": "Aspen Lumber Co",
  "description": "Framing lumber — 2x6 Douglas Fir",
  "status": "received",
  "po_amount": 18500.00,
  "issued_date": "2026-06-10",
  "expected_date": "2026-06-20",
  "received_date": "2026-06-21",
  "raw_data": {}
}
```

### change_orders

```json
{
  "houzz_co_id": "CO-3218059-001",
  "houzz_project_id": "3218059",
  "co_number": "CO-001",
  "title": "Add mudroom bench",
  "description": "Client-requested addition — mudroom built-in bench with storage",
  "status": "pending",
  "amount": 4500.00,
  "reason": "client_request",
  "submitted_date": "2026-06-27",
  "approved_date": null,
  "raw_data": {}
}
```

### selections

```json
{
  "houzz_selection_id": "SEL-3218059-001",
  "houzz_project_id": "3218059",
  "category": "Plumbing Fixtures",
  "item_name": "Master Bath Shower Head",
  "description": "Kohler rain head, brushed nickel",
  "status": "approved",
  "selected_option": "Kohler K-10282-BN",
  "allowance_amount": 500.00,
  "actual_amount": 485.00,
  "vendor": "Ferguson HVAC",
  "due_date": "2026-07-01",
  "raw_data": {}
}
```

### vendors

```json
{
  "houzz_vendor_id": "V-3218059-001",
  "houzz_project_id": "3218059",
  "company_name": "Aspen Lumber Co",
  "contact_name": "Tom Harris",
  "email": "tom@aspenlumber.com",
  "phone": "970-555-0101",
  "trade": "lumber",
  "status": "active",
  "raw_data": {}
}
```

### contacts

```json
{
  "houzz_contact_id": "C-3218059-001",
  "houzz_project_id": "3218059",
  "name": "Sarah Smith",
  "role": "client",
  "email": "sarah@smithfamily.com",
  "phone": "970-555-0202",
  "company": null,
  "raw_data": {}
}
```

### team_members

```json
{
  "houzz_member_id": "TM-3218059-001",
  "houzz_project_id": "3218059",
  "name": "Buck Adams",
  "role": "General Contractor",
  "email": "buck@ahmaspen.com",
  "permissions": "admin",
  "joined_date": "2026-03-10",
  "raw_data": {}
}
```

### subcontractors

```json
{
  "houzz_sub_id": "SUB-3218059-001",
  "houzz_project_id": "3218059",
  "company_name": "Rocky Mountain Electric",
  "contact_name": "Jim Dawson",
  "trade": "electrical",
  "email": "jim@rmelec.com",
  "phone": "970-555-0303",
  "license_number": "CO-ELEC-88821",
  "insurance_expiry": "2026-12-31",
  "status": "active",
  "raw_data": {}
}
```

---

## API Calls

### Option 1: Full connector (all 17 entity types)

```bash
# Dry run first — always
curl -X POST http://localhost:8000/api/v1/services/connectors/houzz/ingest \
  -H "X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6" \
  -H "Content-Type: application/json" \
  -d '{
    "dry_run": true,
    "source": "browser_claude",
    "data": {
      "projects": [...],
      "daily_logs": [...],
      ...
    }
  }'

# After validating dry_run output — write to DB
curl -X POST http://localhost:8000/api/v1/services/connectors/houzz/ingest \
  ... -d '{ "dry_run": false, "data": {...} }'
```

### Option 2: Houzz service (legacy + full)

```bash
# Legacy (3 entity types)
POST /api/v1/services/houzz/ingest

# Full (all 17 entity types)
POST /api/v1/services/houzz/ingest/full
```

---

## Browser Agent Extraction Protocol

### Step 1: Project Discovery
Navigate to Houzz Pro → Projects list. Extract all active projects with IDs.

### Step 2: Module Traversal (per project)
For each project, navigate to each module tab:
1. Overview → extract project details, status, budget, dates
2. Daily Logs → scroll all logs, extract content + weather + crew
3. Schedule → extract all items with completion % and assignee
4. Files/Photos → extract file list, URLs, categories
5. Time Tracking → extract all entries with hours and cost codes
6. Tasks / Punch List → extract all items with status
7. Messages → extract all messages with sender and timestamp
8. Financial Overview → extract budget vs. actual by category
9. Estimates → extract all estimates with status and amounts
10. Contracts → extract signed contracts with amounts
11. Purchase Orders → extract POs with status and vendor
12. Change Orders → extract COs with status and amounts
13. Selections → extract all selections with status and actual cost
14. Vendors → extract vendor list with trade and contact
15. Contacts → extract all project contacts
16. Team → extract team members with permissions
17. Subcontractors → extract subs with trade and license

### Step 3: Produce Canonical JSON
Assemble all extracted data into the canonical format above.
- Use `houzz_project_id` from the URL (numeric ID in path)
- Generate stable IDs for records that don't have native IDs: `{TYPE}-{project_id}-{sequence}`
- Include `raw_data: {}` with the original platform fields for audit trail

### Step 4: Call Ingest API
POST to `/api/v1/services/connectors/houzz/ingest` with `dry_run: true`.
Review the response. If `errors` is empty, call again with `dry_run: false`.

### Step 5: Confirm
Report extraction summary to Claude Code:
- Entity types extracted
- Record counts per type
- Any extraction failures or missing modules
- API response (inserted/updated/skipped counts)

---

## Incremental Sync Protocol

On subsequent runs (not first-time extraction):

1. Query sync state: `GET /api/v1/services/connectors/houzz/sync-state?entity_type=daily_logs&external_id=3218059`
2. The response includes `last_synced_at`
3. Browser Agent extracts only records modified after `last_synced_at`
4. Pass `changed_since` in extraction_notes for audit trail

This means: first run extracts everything. Subsequent runs extract only what changed.

---

## Multi-Platform Extension

This same standard applies to all connectors. To extract from a new platform:

| Platform   | Connector Name | Ingest URL                              |
|------------|----------------|-----------------------------------------|
| Houzz      | houzz          | /api/v1/services/connectors/houzz/ingest  |
| HubSpot    | hubspot        | /api/v1/services/connectors/hubspot/ingest |
| Outlook    | outlook        | /api/v1/services/connectors/outlook/ingest |
| QuickBooks | quickbooks     | /api/v1/services/connectors/quickbooks/ingest |
| Google Drive | drive        | /api/v1/services/connectors/drive/ingest  |
| Procore    | procore        | /api/v1/services/connectors/procore/ingest |

All connectors extend `BaseConnector` — same 7-stage pipeline, same canonical JSON format, same sync state tracking.

---

*Browser Agent Standard v2.0 | HCI AI Operating System | 2026-06-27*

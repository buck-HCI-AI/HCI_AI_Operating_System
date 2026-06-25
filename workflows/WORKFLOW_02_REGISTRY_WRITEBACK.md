# WORKFLOW 02 — Registry Writeback

## Purpose

Keep the PostgreSQL vendor, contact, and project registries in sync with HubSpot and other external sources. This workflow flows data INTO PostgreSQL — it never writes back to HubSpot without Buck's explicit approval.

## Direction

```
HubSpot CRM ──READ──→ PostgreSQL (companies, contacts, vendors)
Houzz Pro   ──READ──→ PostgreSQL (houzz_projects, houzz_daily_logs)
Google Drive ──READ──→ PostgreSQL (documents, drive_sync_log)
```

**NEVER:** PostgreSQL → HubSpot (requires Buck approval per operating rules)

## Trigger

Daily at 6:50 AM via morning startup sequence (`run_morning_brief.sh`).
Also available manually: `POST /sync/hubspot`, `POST /sync/houzz`, `POST /sync/drive`.

## HubSpot → PostgreSQL Sync

### Deals → projects
```python
# For each HubSpot deal:
# 1. Upsert hubspot_deals table
# 2. Match to projects by hubspot_deal_id
# 3. Update projects.project_status from deal stage
```

### Contacts → companies + contacts
```python
# For each HubSpot contact with a company:
# 1. Upsert companies (by hubspot_company_id)
# 2. Upsert contacts (by hubspot_contact_id)
# 3. Upsert company_contacts junction
# 4. Upsert vendors (if company has trade data)
```

### Notes → hubspot_notes
```python
# For each HubSpot note associated with a deal:
# 1. Upsert hubspot_notes by hubspot_note_id
```

## Vendor Enrichment Rules

When a HubSpot contact sync creates/updates a vendor record:
- Set `source_system = 'hubspot'`
- Set `source_reference = hubspot_company_id`
- Map `company.company_type` → vendor `preferred_status` (if available)
- DO NOT overwrite manually-set `preferred_status = 'blacklisted'`

## Conflict Resolution

| Field | Rule |
|-------|------|
| preferred_status = 'blacklisted' | Never overwrite with sync data |
| performance_rating | Never overwrite manually set rating |
| insurance_status | Sync can update; manual entry takes precedence |
| All other fields | Last-sync-wins |

## Sync Log

Every sync run writes to `sync_log`:
```sql
INSERT INTO sync_log (source_system, sync_type, records_found, records_synced,
                      records_skipped, errors, status)
VALUES ('hubspot', 'incremental', 300, 285, 10, 5, 'completed');
```

## Status

| Step | Status |
|------|--------|
| HubSpot deals → hubspot_deals | ✅ Built (sync_hubspot.py) |
| HubSpot contacts → vendors | ✅ Built (seed_postgres.py) |
| Houzz → houzz_* tables | ✅ Built (sync_houzz.py) |
| Drive → drive_sync_log | ✅ Built (sync_drive.py) |
| companies/contacts full sync | 🔜 Planned (FastAPI phase) |

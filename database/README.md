# HCI AI Database

PostgreSQL schema, migrations, seeds, and data model documentation.

## Schema Files (apply in order)

```bash
psql -U hci_admin -d hci_os -f schema/001_initial_core_schema.sql
psql -U hci_admin -d hci_os -f schema/002_document_storage_schema.sql
psql -U hci_admin -d hci_os -f schema/003_registry_schema.sql
psql -U hci_admin -d hci_os -f schema/004_embedding_metadata_schema.sql
```

Then load seed data:
```bash
psql -U hci_admin -d hci_os -f seeds/seed_reference_csi_divisions.sql
psql -U hci_admin -d hci_os -f seeds/seed_document_categories.sql
```

## Schema Summary

| File | Tables | Purpose |
|------|--------|---------|
| 001_initial_core_schema.sql | companies, contacts, company_contacts, projects, project_team_members | Core entities |
| 002_document_storage_schema.sql | documents, document_versions, document_relationships, document_tags, document_processing_events, document_chunks | Document intelligence |
| 003_registry_schema.sql | csi_divisions, cost_codes, vendors, vendor_trade_mappings, vendor_project_history, bid_packages, bid_requests, bids, procurement_items, long_lead_items, historical_cost_records, risks, lessons_learned | Registries + bid/cost data |
| 004_embedding_metadata_schema.sql | qdrant_collections, embedding_jobs, search_log, sync_log | Search and AI infrastructure |

**Total: 23 tables**

## Design Rules

- **UUID primary keys** on all tables (`gen_random_uuid()` via pgcrypto)
- **Global columns** on every table: `id`, `created_at`, `updated_at`, `created_by`, `updated_by`, `source_system`, `source_reference`, `status`, `notes`, `metadata JSONB`
- **No binary files in PostgreSQL** — MinIO handles all file storage
- **Every document** must have a row in `documents` before chunks are embedded
- **Every chunk** in Qdrant must have a row in `document_chunks` with `qdrant_point_id`

## Migration Naming Convention

```
{sequence}_{action}_{description}.sql
001_initial_core_schema.sql
002_document_storage_schema.sql
005_add_column_projects_budget.sql   ← future migrations
```

## Rollback

Each migration file should have a corresponding rollback:
```
migrations/rollback/001_rollback_core_schema.sql
```

Rollback convention: `DROP TABLE IF EXISTS {table} CASCADE;` in reverse dependency order.

## Existing vs. New Schema

The running Postgres instance (`hci_os` DB) uses the legacy SERIAL-key schema from `05_Database/postgres/schema.sql`. These canonical UUID-key schema files are the target state for new deployments (Mac mini M4 Pro) and future migrations on the existing DB.

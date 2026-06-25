# Migrations

SQL migration files for schema changes after initial deployment.

## Convention

```
{sequence}_{action}_{description}.sql
```

Example:
```
005_add_column_projects_budget.sql
006_add_index_vendors_trade.sql
007_alter_table_bids_add_leveling_score.sql
```

## Applying a Migration

```bash
psql -U hci_admin -d hci_os -f migrations/005_add_column_projects_budget.sql
```

## Tracking

Log every applied migration in this file or in a `schema_migrations` table (add in a future migration).

## Applied Migrations

| # | File | Applied | Notes |
|---|------|---------|-------|
| 001 | 001_initial_core_schema.sql | schema/ | Initial core |
| 002 | 002_document_storage_schema.sql | schema/ | Document storage |
| 003 | 003_registry_schema.sql | schema/ | Registries |
| 004 | 004_embedding_metadata_schema.sql | schema/ | Embedding metadata |

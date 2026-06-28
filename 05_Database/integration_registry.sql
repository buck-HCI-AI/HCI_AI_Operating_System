-- Integration Registry Schema — HCI AI Operating System
-- AUTO-016 | Sprint 2 — Registry Consolidation
-- All active integrations registered here as single source of truth.
-- Claude Code: read-write | n8n: read-only | ChatGPT: read via /project-state

CREATE TABLE IF NOT EXISTS integration_registry (
    id                  SERIAL PRIMARY KEY,
    integration_key     VARCHAR(64)  NOT NULL UNIQUE,   -- e.g. 'hubspot', 'google_drive', 'houzz'
    display_name        VARCHAR(128) NOT NULL,
    category            VARCHAR(32)  NOT NULL,           -- crm | storage | field | email | analytics
    status              VARCHAR(32)  NOT NULL DEFAULT 'active',
                        -- active | pending_data | degraded | inactive | blocked
    auth_method         VARCHAR(64),                     -- oauth2 | api_key | bearer | browser_agent
    base_url            VARCHAR(512),
    api_key_env_var     VARCHAR(128),                    -- env var name holding the credential
    last_health_check   TIMESTAMPTZ,
    last_sync_at        TIMESTAMPTZ,
    record_count        INTEGER,                         -- last known record count
    owner_agent         VARCHAR(64),                     -- which AI agent owns this integration
    notes               TEXT,
    properties          JSONB        NOT NULL DEFAULT '{}',
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS integration_sync_log (
    id                  SERIAL PRIMARY KEY,
    integration_key     VARCHAR(64)  NOT NULL REFERENCES integration_registry(integration_key),
    sync_type           VARCHAR(64)  NOT NULL,           -- full | incremental | health_check
    status              VARCHAR(32)  NOT NULL,           -- success | failed | partial
    records_synced      INTEGER      DEFAULT 0,
    error_message       TEXT,
    duration_seconds    NUMERIC(8,2),
    triggered_by        VARCHAR(64),                     -- agent name or 'n8n:workflow-id'
    started_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    completed_at        TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_integration_registry_status
    ON integration_registry(status);

CREATE INDEX IF NOT EXISTS idx_integration_sync_log_key_started
    ON integration_sync_log(integration_key, started_at DESC);

-- Seed: all currently live integrations as of Sprint 2 open (2026-06-27)

INSERT INTO integration_registry
    (integration_key, display_name, category, status, auth_method,
     base_url, api_key_env_var, last_health_check, record_count,
     owner_agent, notes, properties)
VALUES
-- HubSpot CRM
(
    'hubspot', 'HubSpot CRM', 'crm', 'active', 'api_key',
    'https://api.hubapi.com', 'HUBSPOT_API_KEY',
    NOW(), 2849,
    'claude_code',
    'Deals, contacts, companies, tasks synced. READ-ONLY from HCI side — no auto-writes.',
    '{"deals_active": 3, "contacts_synced": true, "companies_synced": true, "mining_enabled": true}'
),
-- Google Drive
(
    'google_drive', 'Google Drive', 'storage', 'active', 'oauth2',
    'https://www.googleapis.com/drive/v3', 'GOOGLE_DRIVE_CREDENTIALS',
    NOW(), null,
    'claude_code',
    'Project folders, bid trackers, SOP library. DriveMiner reads drive_sync_log.',
    '{"scopes": ["files.read", "files.write"], "mining_enabled": true}'
),
-- Microsoft 365 (Outlook via Graph API)
(
    'microsoft_365', 'Microsoft 365 / Outlook', 'email', 'active', 'oauth2',
    'https://graph.microsoft.com/v1.0', 'MICROSOFT_GRAPH_TOKEN',
    NOW(), null,
    'claude_code',
    'Email read/send via Graph API. OutlookMiner reads inbox — all suggestions queued for Buck approval.',
    '{"read_enabled": true, "send_enabled": true, "delete_enabled": true, "mining_enabled": true}'
),
-- Google Sheets
(
    'google_sheets', 'Google Sheets', 'storage', 'active', 'oauth2',
    'https://sheets.googleapis.com/v4', 'GOOGLE_SHEETS_CREDENTIALS',
    NOW(), null,
    'claude_code',
    'Bid tracker spreadsheets for active projects.',
    '{"active_trackers": 3}'
),
-- Houzz Pro (Browser Claude)
(
    'houzz', 'Houzz Pro', 'field', 'pending_data', 'browser_agent',
    'https://pro.houzz.com', null,
    null, null,
    'browser_claude',
    'Browser Claude reads daily logs, schedules, photos. Zero writes to Houzz. DB tables pending Browser insert.',
    '{"projects": ["64 Eastwood", "101 Francis", "1355 Riverside"], "tables": ["houzz_projects", "houzz_daily_logs", "project_schedule_items"], "mining_enabled": false}'
),
-- Qdrant vector store
(
    'qdrant', 'Qdrant Vector Store', 'analytics', 'active', 'api_key',
    'http://localhost:6333', 'QDRANT_API_KEY',
    NOW(), 190,
    'claude_code',
    '13 collections. Background learning records indexed for semantic search.',
    '{"collections": 13, "vectors": 190}'
),
-- PostgreSQL
(
    'postgresql', 'PostgreSQL (hci_os)', 'analytics', 'active', 'api_key',
    'localhost:5432', 'POSTGRES_PASSWORD',
    NOW(), null,
    'claude_code',
    'Primary operational DB. 47 tables. Mining engine reads/writes here.',
    '{"tables": 47, "projects": 4, "mining_runs_enabled": true}'
),
-- n8n
(
    'n8n', 'n8n Automation', 'analytics', 'active', 'api_key',
    'http://localhost:5678', 'N8N_API_KEY',
    NOW(), null,
    'n8n',
    '18 workflows, 10 active including AUTO-001/002/003/004. Orchestrates all timed automation.',
    '{"workflows_total": 18, "workflows_active": 10, "auto_mining": "03:00 daily"}'
)
ON CONFLICT (integration_key) DO UPDATE
    SET display_name    = EXCLUDED.display_name,
        status          = EXCLUDED.status,
        last_health_check = EXCLUDED.last_health_check,
        record_count    = EXCLUDED.record_count,
        notes           = EXCLUDED.notes,
        properties      = EXCLUDED.properties,
        updated_at      = NOW();

-- Migration 009: Houzz Connector Framework — Full Entity Schema
-- All Houzz entity types + connector sync state + event bus
-- 2026-06-27 | Autonomous Development Mode

-- ── Connector sync state ──────────────────────────────────────────────────────
-- Tracks last successful sync per entity type per project
-- Enables incremental sync — only fetch records changed since last_synced_at

CREATE TABLE IF NOT EXISTS connector_sync_state (
    id              SERIAL PRIMARY KEY,
    connector_name  VARCHAR(64) NOT NULL,              -- houzz, hubspot, drive, etc.
    entity_type     VARCHAR(64) NOT NULL,              -- projects, daily_logs, etc.
    external_id     VARCHAR(128),                      -- project ID etc.
    last_synced_at  TIMESTAMPTZ,
    last_cursor     VARCHAR(256),                      -- pagination cursor or etag
    records_synced  INTEGER NOT NULL DEFAULT 0,
    status          VARCHAR(16) NOT NULL DEFAULT 'idle', -- idle/running/error
    error_message   TEXT,
    retry_count     INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Unique index uses COALESCE since function calls are not allowed in table UNIQUE constraints
CREATE UNIQUE INDEX IF NOT EXISTS idx_sync_state_unique
    ON connector_sync_state(connector_name, entity_type, COALESCE(external_id,''));

CREATE INDEX IF NOT EXISTS idx_sync_state_connector ON connector_sync_state(connector_name, entity_type);

-- ── Houzz files & photos ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS houzz_files (
    id                  SERIAL PRIMARY KEY,
    houzz_file_id       VARCHAR(128) NOT NULL UNIQUE,
    houzz_project_id    VARCHAR(128) NOT NULL,
    file_name           VARCHAR(512),
    file_type           VARCHAR(64),               -- photo, document, video
    category            VARCHAR(128),
    url                 TEXT,
    thumbnail_url       TEXT,
    uploaded_by         VARCHAR(256),
    uploaded_at         TIMESTAMPTZ,
    room                VARCHAR(128),
    tags                TEXT[],
    raw_data            JSONB NOT NULL DEFAULT '{}',
    synced_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_houzz_files_project ON houzz_files(houzz_project_id);

-- ── Houzz time entries ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS houzz_time_entries (
    id                  SERIAL PRIMARY KEY,
    houzz_entry_id      VARCHAR(128) NOT NULL UNIQUE,
    houzz_project_id    VARCHAR(128) NOT NULL,
    date                DATE,
    worker_name         VARCHAR(256),
    role                VARCHAR(128),
    hours               NUMERIC(6,2),
    description         TEXT,
    cost_code           VARCHAR(64),
    billable            BOOLEAN DEFAULT TRUE,
    raw_data            JSONB NOT NULL DEFAULT '{}',
    synced_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_houzz_time_project ON houzz_time_entries(houzz_project_id, date);

-- ── Houzz tasks & punch list ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS houzz_tasks (
    id                  SERIAL PRIMARY KEY,
    houzz_task_id       VARCHAR(128) NOT NULL UNIQUE,
    houzz_project_id    VARCHAR(128) NOT NULL,
    title               VARCHAR(512),
    description         TEXT,
    status              VARCHAR(64),               -- open, in_progress, complete
    priority            VARCHAR(32),
    assigned_to         VARCHAR(256),
    due_date            DATE,
    completed_date      DATE,
    is_punch_list       BOOLEAN DEFAULT FALSE,
    location            VARCHAR(256),
    raw_data            JSONB NOT NULL DEFAULT '{}',
    synced_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_houzz_tasks_project ON houzz_tasks(houzz_project_id, status);

-- ── Houzz messages ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS houzz_messages (
    id                  SERIAL PRIMARY KEY,
    houzz_message_id    VARCHAR(128) NOT NULL UNIQUE,
    houzz_project_id    VARCHAR(128) NOT NULL,
    sender_name         VARCHAR(256),
    sender_role         VARCHAR(128),
    message_text        TEXT,
    sent_at             TIMESTAMPTZ,
    has_attachments     BOOLEAN DEFAULT FALSE,
    thread_id           VARCHAR(128),
    raw_data            JSONB NOT NULL DEFAULT '{}',
    synced_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_houzz_messages_project ON houzz_messages(houzz_project_id, sent_at DESC);

-- ── Houzz budget ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS houzz_budget (
    id                  SERIAL PRIMARY KEY,
    houzz_project_id    VARCHAR(128) NOT NULL,
    category            VARCHAR(256),
    budgeted_amount     NUMERIC(12,2),
    actual_amount       NUMERIC(12,2),
    committed_amount    NUMERIC(12,2),
    variance            NUMERIC(12,2) GENERATED ALWAYS AS (COALESCE(actual_amount,0) - COALESCE(budgeted_amount,0)) STORED,
    as_of_date          DATE,
    raw_data            JSONB NOT NULL DEFAULT '{}',
    synced_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_houzz_budget_unique
    ON houzz_budget(houzz_project_id, category, COALESCE(as_of_date, '1970-01-01'::date));

CREATE INDEX IF NOT EXISTS idx_houzz_budget_project ON houzz_budget(houzz_project_id);

-- ── Houzz estimates ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS houzz_estimates (
    id                  SERIAL PRIMARY KEY,
    houzz_estimate_id   VARCHAR(128) NOT NULL UNIQUE,
    houzz_project_id    VARCHAR(128) NOT NULL,
    estimate_number     VARCHAR(64),
    title               VARCHAR(512),
    status              VARCHAR(64),               -- draft, sent, approved, declined
    total_amount        NUMERIC(12,2),
    created_date        DATE,
    sent_date           DATE,
    approved_date       DATE,
    client_name         VARCHAR(256),
    raw_data            JSONB NOT NULL DEFAULT '{}',
    synced_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_houzz_estimates_project ON houzz_estimates(houzz_project_id);

-- ── Houzz contracts ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS houzz_contracts (
    id                  SERIAL PRIMARY KEY,
    houzz_contract_id   VARCHAR(128) NOT NULL UNIQUE,
    houzz_project_id    VARCHAR(128) NOT NULL,
    contract_number     VARCHAR(64),
    title               VARCHAR(512),
    status              VARCHAR(64),               -- draft, sent, signed, void
    contract_amount     NUMERIC(12,2),
    signed_date         DATE,
    expiration_date     DATE,
    counterparty        VARCHAR(256),
    raw_data            JSONB NOT NULL DEFAULT '{}',
    synced_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_houzz_contracts_project ON houzz_contracts(houzz_project_id);

-- ── Houzz purchase orders ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS houzz_purchase_orders (
    id                  SERIAL PRIMARY KEY,
    houzz_po_id         VARCHAR(128) NOT NULL UNIQUE,
    houzz_project_id    VARCHAR(128) NOT NULL,
    po_number           VARCHAR(64),
    vendor_name         VARCHAR(256),
    description         TEXT,
    status              VARCHAR(64),               -- draft, sent, received, closed
    po_amount           NUMERIC(12,2),
    issued_date         DATE,
    expected_date       DATE,
    received_date       DATE,
    raw_data            JSONB NOT NULL DEFAULT '{}',
    synced_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_houzz_po_project ON houzz_purchase_orders(houzz_project_id);

-- ── Houzz change orders ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS houzz_change_orders (
    id                  SERIAL PRIMARY KEY,
    houzz_co_id         VARCHAR(128) NOT NULL UNIQUE,
    houzz_project_id    VARCHAR(128) NOT NULL,
    co_number           VARCHAR(64),
    title               VARCHAR(512),
    description         TEXT,
    status              VARCHAR(64),               -- pending, approved, declined, void
    amount              NUMERIC(12,2),
    reason              VARCHAR(256),
    submitted_date      DATE,
    approved_date       DATE,
    raw_data            JSONB NOT NULL DEFAULT '{}',
    synced_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_houzz_co_project ON houzz_change_orders(houzz_project_id);

-- ── Houzz selections ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS houzz_selections (
    id                  SERIAL PRIMARY KEY,
    houzz_selection_id  VARCHAR(128) NOT NULL UNIQUE,
    houzz_project_id    VARCHAR(128) NOT NULL,
    category            VARCHAR(256),
    item_name           VARCHAR(512),
    description         TEXT,
    status              VARCHAR(64),               -- pending, approved, ordered, installed
    selected_option     TEXT,
    allowance_amount    NUMERIC(12,2),
    actual_amount       NUMERIC(12,2),
    vendor              VARCHAR(256),
    due_date            DATE,
    raw_data            JSONB NOT NULL DEFAULT '{}',
    synced_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_houzz_selections_project ON houzz_selections(houzz_project_id, status);

-- ── Houzz project vendors ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS houzz_project_vendors (
    id                  SERIAL PRIMARY KEY,
    houzz_vendor_id     VARCHAR(128) NOT NULL,
    houzz_project_id    VARCHAR(128) NOT NULL,
    company_name        VARCHAR(256),
    contact_name        VARCHAR(256),
    email               VARCHAR(256),
    phone               VARCHAR(64),
    trade               VARCHAR(128),
    status              VARCHAR(64),
    raw_data            JSONB NOT NULL DEFAULT '{}',
    synced_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(houzz_vendor_id, houzz_project_id)
);

CREATE INDEX IF NOT EXISTS idx_houzz_vendors_project ON houzz_project_vendors(houzz_project_id);

-- ── Houzz contacts ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS houzz_contacts (
    id                  SERIAL PRIMARY KEY,
    houzz_contact_id    VARCHAR(128) NOT NULL UNIQUE,
    houzz_project_id    VARCHAR(128),
    name                VARCHAR(256),
    role                VARCHAR(128),              -- client, owner, designer, etc.
    email               VARCHAR(256),
    phone               VARCHAR(64),
    company             VARCHAR(256),
    raw_data            JSONB NOT NULL DEFAULT '{}',
    synced_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_houzz_contacts_project ON houzz_contacts(houzz_project_id);

-- ── Houzz team members ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS houzz_team_members (
    id                  SERIAL PRIMARY KEY,
    houzz_member_id     VARCHAR(128) NOT NULL,
    houzz_project_id    VARCHAR(128) NOT NULL,
    name                VARCHAR(256),
    role                VARCHAR(128),
    email               VARCHAR(256),
    permissions         VARCHAR(64),               -- view, edit, admin
    joined_date         DATE,
    raw_data            JSONB NOT NULL DEFAULT '{}',
    synced_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(houzz_member_id, houzz_project_id)
);

-- ── Houzz subcontractors ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS houzz_subcontractors (
    id                  SERIAL PRIMARY KEY,
    houzz_sub_id        VARCHAR(128) NOT NULL,
    houzz_project_id    VARCHAR(128) NOT NULL,
    company_name        VARCHAR(256),
    contact_name        VARCHAR(256),
    trade               VARCHAR(128),
    email               VARCHAR(256),
    phone               VARCHAR(64),
    license_number      VARCHAR(128),
    insurance_expiry    DATE,
    status              VARCHAR(64),
    raw_data            JSONB NOT NULL DEFAULT '{}',
    synced_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(houzz_sub_id, houzz_project_id)
);

CREATE INDEX IF NOT EXISTS idx_houzz_subs_project ON houzz_subcontractors(houzz_project_id);

-- ── Seed connector sync state for 101 Francis (project 3218059) ───────────────
INSERT INTO connector_sync_state (connector_name, entity_type, external_id, status)
VALUES
  ('houzz', 'projects',         '3218059', 'idle'),
  ('houzz', 'daily_logs',       '3218059', 'idle'),
  ('houzz', 'schedule_items',   '3218059', 'idle'),
  ('houzz', 'files',            '3218059', 'idle'),
  ('houzz', 'time_entries',     '3218059', 'idle'),
  ('houzz', 'tasks',            '3218059', 'idle'),
  ('houzz', 'messages',         '3218059', 'idle'),
  ('houzz', 'budget',           '3218059', 'idle'),
  ('houzz', 'estimates',        '3218059', 'idle'),
  ('houzz', 'contracts',        '3218059', 'idle'),
  ('houzz', 'purchase_orders',  '3218059', 'idle'),
  ('houzz', 'change_orders',    '3218059', 'idle'),
  ('houzz', 'selections',       '3218059', 'idle'),
  ('houzz', 'vendors',          '3218059', 'idle'),
  ('houzz', 'contacts',         '3218059', 'idle'),
  ('houzz', 'team_members',     '3218059', 'idle'),
  ('houzz', 'subcontractors',   '3218059', 'idle')
ON CONFLICT DO NOTHING;

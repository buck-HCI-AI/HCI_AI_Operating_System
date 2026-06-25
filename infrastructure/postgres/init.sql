-- HCI AI Operating System — PostgreSQL Schema
-- Auto-runs on first container start (docker-entrypoint-initdb.d)
-- Source of truth: also maintained in /05_Database/postgres/schema.sql
-- Keep both files in sync when the schema changes.

-- ─────────────────────────────────────────────────────────────────────────────
-- PROJECTS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS projects (
    id                  SERIAL PRIMARY KEY,
    name                TEXT NOT NULL,
    address             TEXT,
    city                TEXT DEFAULT 'Aspen',
    state               TEXT DEFAULT 'CO',
    status              TEXT DEFAULT 'active',
    scope               TEXT,
    hubspot_deal_id     TEXT,
    gsheet_bid_tracker  TEXT,
    drive_folder_id     TEXT,
    pm_name             TEXT,
    super_name          TEXT,
    owner_name          TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- VENDORS / SUBCONTRACTORS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS vendors (
    id                  SERIAL PRIMARY KEY,
    company_name        TEXT NOT NULL,
    contact_name        TEXT,
    email               TEXT,
    phone               TEXT,
    address             TEXT,
    city                TEXT,
    state               TEXT,
    zip                 TEXT,
    csi_divisions       TEXT[],
    trade               TEXT,
    tier                TEXT DEFAULT 'preferred',
    hubspot_contact_id  TEXT,
    hubspot_company_id  TEXT,
    notes               TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- BID PACKAGES
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bid_packages (
    id                  SERIAL PRIMARY KEY,
    project_id          INTEGER REFERENCES projects(id),
    csi_division        TEXT NOT NULL,
    package_name        TEXT,
    scope_description   TEXT,
    hubspot_deal_id     TEXT,
    status              TEXT DEFAULT 'not_started',
    awarded_vendor_id   INTEGER REFERENCES vendors(id),
    awarded_amount      NUMERIC(12, 2),
    notes               TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- BID ENTRIES
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bid_entries (
    id                  SERIAL PRIMARY KEY,
    bid_package_id      INTEGER REFERENCES bid_packages(id),
    vendor_id           INTEGER REFERENCES vendors(id),
    project_id          INTEGER REFERENCES projects(id),
    csi_division        TEXT,
    date_sent           DATE,
    date_received       DATE,
    bid_amount          NUMERIC(12, 2),
    status              TEXT DEFAULT 'sent',
    quote_ref           TEXT,
    inclusions          TEXT,
    exclusions          TEXT,
    notes               TEXT,
    source              TEXT DEFAULT 'email',
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- LESSONS LEARNED
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS lessons_learned (
    id                  SERIAL PRIMARY KEY,
    project_id          INTEGER REFERENCES projects(id),
    vendor_id           INTEGER REFERENCES vendors(id),
    csi_division        TEXT,
    category            TEXT,
    title               TEXT NOT NULL,
    description         TEXT,
    outcome             TEXT,
    action_taken        TEXT,
    future_recommendation TEXT,
    qdrant_vector_id    TEXT,
    recorded_by         TEXT,
    recorded_at         TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- MEETINGS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS meetings (
    id                  SERIAL PRIMARY KEY,
    project_id          INTEGER REFERENCES projects(id),
    meeting_type        TEXT,
    title               TEXT,
    meeting_date        DATE,
    attendees           JSONB,
    agenda              TEXT,
    summary             TEXT,
    action_items        JSONB,
    transcript_path     TEXT,
    qdrant_vector_id    TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- DAILY LOGS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS daily_logs (
    id                  SERIAL PRIMARY KEY,
    project_id          INTEGER REFERENCES projects(id),
    log_date            DATE NOT NULL,
    weather             TEXT,
    temp_high           INTEGER,
    temp_low            INTEGER,
    crew_on_site        JSONB,
    work_performed      TEXT,
    issues              TEXT,
    photos_count        INTEGER DEFAULT 0,
    drive_folder_id     TEXT,
    qdrant_vector_id    TEXT,
    logged_by           TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- HUBSPOT SYNC TABLES
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS hubspot_deals (
    id                  SERIAL PRIMARY KEY,
    hubspot_deal_id     TEXT UNIQUE NOT NULL,
    deal_name           TEXT,
    stage               TEXT,
    amount              NUMERIC(12,2),
    close_date          DATE,
    owner               TEXT,
    pipeline            TEXT,
    properties          JSONB,
    last_modified       TIMESTAMPTZ,
    synced_at           TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS hubspot_notes (
    id                  SERIAL PRIMARY KEY,
    hubspot_note_id     TEXT UNIQUE NOT NULL,
    deal_id             TEXT,
    contact_id          TEXT,
    body                TEXT,
    created_at          TIMESTAMPTZ,
    synced_at           TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS hubspot_tasks (
    id                  SERIAL PRIMARY KEY,
    hubspot_task_id     TEXT UNIQUE NOT NULL,
    subject             TEXT,
    status              TEXT,
    due_date            TIMESTAMPTZ,
    assigned_to         TEXT,
    deal_id             TEXT,
    synced_at           TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- HOUZZ SYNC TABLES
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS houzz_projects (
    id                  SERIAL PRIMARY KEY,
    houzz_project_id    TEXT UNIQUE NOT NULL,
    name                TEXT,
    client_name         TEXT,
    status              TEXT,
    properties          JSONB,
    synced_at           TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS houzz_daily_logs (
    id                  SERIAL PRIMARY KEY,
    houzz_log_id        TEXT UNIQUE NOT NULL,
    project_id          TEXT,
    log_date            DATE,
    content             TEXT,
    synced_at           TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS houzz_schedule_items (
    id                  SERIAL PRIMARY KEY,
    houzz_item_id       TEXT UNIQUE NOT NULL,
    project_id          TEXT,
    title               TEXT,
    start_date          DATE,
    end_date            DATE,
    status              TEXT,
    synced_at           TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- DRIVE SYNC LOG
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS drive_sync_log (
    id          SERIAL PRIMARY KEY,
    file_path   TEXT UNIQUE NOT NULL,
    file_name   TEXT,
    file_type   TEXT,
    mtime       FLOAT,
    chunks      INT DEFAULT 0,
    synced_at   TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- SEED DATA
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO projects (name, address, city, state, status, scope, hubspot_deal_id, gsheet_bid_tracker)
VALUES
    ('64 Eastwood',    '64 Eastwood Dr.',    'Aspen', 'CO', 'active', 'Exterior & Site',      '332246098523', '1yAmLo3IIp3Vqs3BQJ6QB2O4as0KqXMZxcVvjzGBZDcQ'),
    ('101 Francis',    '101 W Francis St.',  'Aspen', 'CO', 'active', 'Full Interior Remodel','332313009897', '1JExX5CeVBedTEFitM8B6hveF4Prhk0Oy6BZSBu058LE'),
    ('1355 Riverside', '1355 Riverside Dr.', 'Aspen', 'CO', 'active', 'Full Remodel',          NULL,          '1-64X4XGc4P_GmYl7DRt8nGsBNfaVdP_G3qwfBLJSsnA'),
    ('83 Sagebrusch',  '83 Sagebrusch Ln.',  'Aspen', 'CO', 'active', 'TBD',                   NULL,          NULL)
ON CONFLICT DO NOTHING;

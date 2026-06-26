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
-- PHASE 8: LONG LEAD ITEMS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS long_lead_items (
    id                      SERIAL PRIMARY KEY,
    project_id              INTEGER REFERENCES projects(id),
    item_name               TEXT,
    vendor                  TEXT,
    lead_time_weeks         INTEGER,
    order_date              DATE,
    required_on_site_date   DATE,
    status                  TEXT DEFAULT 'pending',
    notes                   TEXT,
    created_at              TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- PHASE 8: PROCUREMENT ITEMS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS procurement_items (
    id              SERIAL PRIMARY KEY,
    project_id      INTEGER REFERENCES projects(id),
    item_name       TEXT,
    vendor          TEXT,
    po_number       TEXT,
    amount          NUMERIC,
    required_date   DATE,
    status          TEXT DEFAULT 'pending',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- PHASE 8: RISKS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS risks (
    id              SERIAL PRIMARY KEY,
    project_id      INTEGER REFERENCES projects(id),
    risk_type       TEXT,
    severity        TEXT DEFAULT 'medium',
    description     TEXT,
    mitigation      TEXT,
    status          TEXT DEFAULT 'open',
    identified_date DATE DEFAULT CURRENT_DATE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- PHASE 8: HISTORICAL COST RECORDS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS historical_cost_records (
    id              SERIAL PRIMARY KEY,
    project_id      INTEGER REFERENCES projects(id),
    bid_package_id  INTEGER REFERENCES bid_packages(id),
    csi_division    TEXT,
    awarded_amount  NUMERIC,
    final_cost      NUMERIC,
    variance_pct    NUMERIC,
    completed_date  DATE,
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- PHASE 8: WORKFLOW EVENTS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS workflow_events (
    id          SERIAL PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    project_id  INTEGER REFERENCES projects(id),
    event_type  TEXT NOT NULL,
    payload     JSONB,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_workflow_events_workflow_id ON workflow_events (workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_events_project_id  ON workflow_events (project_id);
CREATE INDEX IF NOT EXISTS idx_workflow_events_created_at  ON workflow_events (created_at DESC);

-- ─────────────────────────────────────────────────────────────────────────────
-- PHASE 9: DAILY LOGS — extended columns (added via ALTER in Phase 9)
-- ─────────────────────────────────────────────────────────────────────────────
ALTER TABLE daily_logs ADD COLUMN IF NOT EXISTS manpower               JSONB;
ALTER TABLE daily_logs ADD COLUMN IF NOT EXISTS deliveries             JSONB;
ALTER TABLE daily_logs ADD COLUMN IF NOT EXISTS inspections            JSONB;
ALTER TABLE daily_logs ADD COLUMN IF NOT EXISTS quality_notes          TEXT;
ALTER TABLE daily_logs ADD COLUMN IF NOT EXISTS safety_notes           TEXT;
ALTER TABLE daily_logs ADD COLUMN IF NOT EXISTS subcontractor_progress TEXT;
ALTER TABLE daily_logs ADD COLUMN IF NOT EXISTS constraints            JSONB;
ALTER TABLE daily_logs ADD COLUMN IF NOT EXISTS lookahead              TEXT;
ALTER TABLE daily_logs ADD COLUMN IF NOT EXISTS field_risks            JSONB;

-- ─────────────────────────────────────────────────────────────────────────────
-- PHASE 9: SCHEDULE VARIANCE
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS schedule_variance (
    id                      SERIAL PRIMARY KEY,
    project_id              INTEGER REFERENCES projects(id),
    daily_log_id            INTEGER REFERENCES daily_logs(id),
    activity_name           TEXT,
    baseline_status         TEXT,
    current_status          TEXT,
    variance_days           INTEGER,
    variance_pct            NUMERIC,
    cause                   TEXT,
    responsible_party       TEXT,
    risk_level              TEXT,
    recovery_action         TEXT,
    decision_needed         TEXT,
    recommended_notification TEXT,
    detected_at             TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_sched_var_project ON schedule_variance (project_id);
CREATE INDEX IF NOT EXISTS idx_sched_var_log     ON schedule_variance (daily_log_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- PHASE 9: RFIS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS rfis (
    id                      SERIAL PRIMARY KEY,
    project_id              INTEGER REFERENCES projects(id),
    rfi_number              TEXT,
    subject                 TEXT,
    submitted_by            TEXT,
    submitted_to            TEXT DEFAULT 'Buck Adams',
    status                  TEXT DEFAULT 'open',
    question                TEXT,
    response                TEXT,
    submitted_date          DATE,
    required_response_date  DATE,
    response_date           DATE,
    source_email_id         TEXT,
    created_at              TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_rfis_project ON rfis (project_id);
CREATE INDEX IF NOT EXISTS idx_rfis_status  ON rfis (status);

-- ─────────────────────────────────────────────────────────────────────────────
-- PHASE 9: SUBMITTALS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS submittals (
    id                      SERIAL PRIMARY KEY,
    project_id              INTEGER REFERENCES projects(id),
    submittal_number        TEXT,
    spec_section            TEXT,
    description             TEXT,
    submitted_by            TEXT,
    status                  TEXT DEFAULT 'pending',
    submitted_date          DATE,
    required_approval_date  DATE,
    approved_date           DATE,
    source_email_id         TEXT,
    created_at              TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_submittals_project ON submittals (project_id);
CREATE INDEX IF NOT EXISTS idx_submittals_status  ON submittals (status);

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

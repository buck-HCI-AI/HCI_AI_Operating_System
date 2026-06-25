-- HCI AI Operating System — PostgreSQL Schema v1
-- Database: hci_os
-- Philosophy: Postgres stores truth.

-- ─────────────────────────────────────────────────────────────────────────────
-- PROJECTS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS projects (
    id                  SERIAL PRIMARY KEY,
    name                TEXT NOT NULL,
    address             TEXT,
    city                TEXT DEFAULT 'Aspen',
    state               TEXT DEFAULT 'CO',
    status              TEXT DEFAULT 'active',   -- active, complete, on_hold
    scope               TEXT,                    -- Interior, Exterior, Full Remodel, etc.
    hubspot_deal_id     TEXT,                    -- Master deal ID in HubSpot
    gsheet_bid_tracker  TEXT,                    -- Google Sheet ID for bid tracker
    drive_folder_id     TEXT,                    -- Google Drive folder ID
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
    csi_divisions       TEXT[],                  -- ['03', '04', '05']
    trade               TEXT,
    tier                TEXT DEFAULT 'preferred', -- preferred, approved, probation, blacklisted
    hubspot_contact_id  TEXT,
    hubspot_company_id  TEXT,
    notes               TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- BID PACKAGES (per project, per CSI division)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bid_packages (
    id                  SERIAL PRIMARY KEY,
    project_id          INTEGER REFERENCES projects(id),
    csi_division        TEXT NOT NULL,           -- '03', '04 — Masonry', etc.
    package_name        TEXT,
    scope_description   TEXT,
    hubspot_deal_id     TEXT,
    status              TEXT DEFAULT 'not_started',
    -- not_started | sent_out | bids_receiving | leveling | awarded | not_awarded
    awarded_vendor_id   INTEGER REFERENCES vendors(id),
    awarded_amount      NUMERIC(12, 2),
    notes               TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- BID ENTRIES (individual bids received)
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
    -- sent | bid_received | leveling | awarded | not_awarded | declined
    quote_ref           TEXT,                    -- Quote number (e.g. QTE-2026-0156)
    inclusions          TEXT,
    exclusions          TEXT,
    notes               TEXT,
    source              TEXT DEFAULT 'email',    -- email | tolteck | houzz | phone
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
    category            TEXT,                    -- procurement | field | design | relationship
    title               TEXT NOT NULL,
    description         TEXT,
    outcome             TEXT,                    -- positive | negative | neutral
    action_taken        TEXT,
    future_recommendation TEXT,
    qdrant_vector_id    TEXT,                    -- ID in Qdrant after embedding
    recorded_by         TEXT,
    recorded_at         TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- MEETINGS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS meetings (
    id                  SERIAL PRIMARY KEY,
    project_id          INTEGER REFERENCES projects(id),
    meeting_type        TEXT,                    -- owner | subcontractor | internal | site_walk
    title               TEXT,
    meeting_date        DATE,
    attendees           JSONB,                   -- [{name, company, role}]
    agenda              TEXT,
    summary             TEXT,
    action_items        JSONB,                   -- [{item, owner, due_date, status}]
    transcript_path     TEXT,                    -- Drive path to raw transcript
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
    crew_on_site        JSONB,                   -- [{company, count, trade}]
    work_performed      TEXT,
    issues              TEXT,
    photos_count        INTEGER DEFAULT 0,
    drive_folder_id     TEXT,
    qdrant_vector_id    TEXT,
    logged_by           TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- SEED DATA — Active Projects
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO projects (name, address, city, state, status, scope, hubspot_deal_id, gsheet_bid_tracker)
VALUES
    ('64 Eastwood', '64 Eastwood Dr.', 'Aspen', 'CO', 'active', 'Exterior & Site',
     '331240861419', '1yAmLo3IIp3Vqs3BQJ6QB2O4as0KqXMZxcVvjzGBZDcQ'),
    ('101 Francis', '101 W Francis St.', 'Aspen', 'CO', 'active', 'Full Interior Remodel',
     NULL, '1JExX5CeVBedTEFitM8B6hveF4Prhk0Oy6BZSBu058LE'),
    ('1355 Riverside', '1355 Riverside Dr.', 'Aspen', 'CO', 'active', 'Full Remodel',
     NULL, '1-64X4XGc4P_GmYl7DRt8nGsBNfaVdP_G3qwfBLJSsnA')
ON CONFLICT DO NOTHING;

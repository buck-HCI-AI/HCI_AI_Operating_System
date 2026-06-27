-- Migration 011: HubSpot Connector Tables
-- Read-only pull from HubSpot API → local cache for mining and executive reporting
-- NEVER writes back to HubSpot without Buck's explicit approval

-- ─────────────────────────────────────────
-- CONTACTS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS hubspot_contacts (
    id                  SERIAL PRIMARY KEY,
    hubspot_id          TEXT NOT NULL UNIQUE,
    firstname           TEXT,
    lastname            TEXT,
    email               TEXT,
    phone               TEXT,
    jobtitle            TEXT,
    company_name        TEXT,
    hs_lead_status      TEXT,
    lifecyclestage      TEXT,
    associated_company_id TEXT,
    raw_properties      JSONB DEFAULT '{}',
    extracted_at        TIMESTAMPTZ,
    synced_at           TIMESTAMPTZ DEFAULT NOW(),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_hs_contacts_email     ON hubspot_contacts(email);
CREATE INDEX IF NOT EXISTS idx_hs_contacts_company   ON hubspot_contacts(associated_company_id);
CREATE INDEX IF NOT EXISTS idx_hs_contacts_lifecycle ON hubspot_contacts(lifecyclestage);

-- ─────────────────────────────────────────
-- COMPANIES
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS hubspot_companies (
    id                  SERIAL PRIMARY KEY,
    hubspot_id          TEXT NOT NULL UNIQUE,
    name                TEXT,
    domain              TEXT,
    phone               TEXT,
    industry            TEXT,
    type                TEXT,
    city                TEXT,
    state               TEXT,
    zip                 TEXT,
    raw_properties      JSONB DEFAULT '{}',
    extracted_at        TIMESTAMPTZ,
    synced_at           TIMESTAMPTZ DEFAULT NOW(),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_hs_companies_domain ON hubspot_companies(domain);
CREATE INDEX IF NOT EXISTS idx_hs_companies_name   ON hubspot_companies(name);

-- ─────────────────────────────────────────
-- DEALS (bid opportunities + active projects)
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS hubspot_deals (
    id                      SERIAL PRIMARY KEY,
    hubspot_id              TEXT NOT NULL UNIQUE,
    dealname                TEXT,
    amount                  NUMERIC(14,2),
    dealstage               TEXT,
    pipeline                TEXT,
    closedate               DATE,
    project_code            TEXT,           -- mapped to HCI project code if matched
    associated_company_id   TEXT,
    associated_contact_ids  TEXT[],         -- array of contact hubspot_ids
    raw_properties          JSONB DEFAULT '{}',
    extracted_at            TIMESTAMPTZ,
    synced_at               TIMESTAMPTZ DEFAULT NOW(),
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_hs_deals_stage        ON hubspot_deals(dealstage);
CREATE INDEX IF NOT EXISTS idx_hs_deals_project_code ON hubspot_deals(project_code);
CREATE INDEX IF NOT EXISTS idx_hs_deals_company      ON hubspot_deals(associated_company_id);
CREATE INDEX IF NOT EXISTS idx_hs_deals_closedate    ON hubspot_deals(closedate);

-- ─────────────────────────────────────────
-- ACTIVITIES (emails, calls, meetings, notes, tasks)
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS hubspot_activities (
    id                      SERIAL PRIMARY KEY,
    hubspot_id              TEXT NOT NULL UNIQUE,
    activity_type           TEXT,   -- EMAIL, CALL, MEETING, NOTE, TASK
    subject                 TEXT,
    body                    TEXT,
    activity_ts             TIMESTAMPTZ,
    duration_ms             INTEGER,
    outcome                 TEXT,
    associated_contact_id   TEXT,
    associated_deal_id      TEXT,
    associated_company_id   TEXT,
    raw_properties          JSONB DEFAULT '{}',
    extracted_at            TIMESTAMPTZ,
    synced_at               TIMESTAMPTZ DEFAULT NOW(),
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_hs_activities_type       ON hubspot_activities(activity_type);
CREATE INDEX IF NOT EXISTS idx_hs_activities_ts         ON hubspot_activities(activity_ts);
CREATE INDEX IF NOT EXISTS idx_hs_activities_contact    ON hubspot_activities(associated_contact_id);
CREATE INDEX IF NOT EXISTS idx_hs_activities_deal       ON hubspot_activities(associated_deal_id);

-- ─────────────────────────────────────────
-- SYNC STATE SEEDS for HubSpot connector
-- ─────────────────────────────────────────
INSERT INTO connector_sync_state (connector_name, entity_type, external_id, status)
VALUES
    ('hubspot', 'contacts',   NULL, 'pending'),
    ('hubspot', 'companies',  NULL, 'pending'),
    ('hubspot', 'deals',      NULL, 'pending'),
    ('hubspot', 'activities', NULL, 'pending')
ON CONFLICT DO NOTHING;

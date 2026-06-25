-- ============================================================
-- HCI AI Operating System — Schema 001: Core (Companies, Contacts, Projects)
-- Migration: 001 | Requires: pgcrypto extension
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ── update trigger helper ──────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = now(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- COMPANIES
-- ============================================================
CREATE TABLE IF NOT EXISTS companies (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name        TEXT NOT NULL,
    legal_name          TEXT,
    hubspot_company_id  TEXT UNIQUE,
    website             TEXT,
    phone               TEXT,
    email               TEXT,
    address_line1       TEXT,
    address_line2       TEXT,
    city                TEXT,
    state               TEXT,
    zip                 TEXT,
    country             TEXT DEFAULT 'US',
    company_type        TEXT,   -- owner | subcontractor | supplier | design | inspection | general
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by          TEXT,
    updated_by          TEXT,
    source_system       TEXT,
    source_reference    TEXT,
    status              TEXT NOT NULL DEFAULT 'active',
    notes               TEXT,
    metadata            JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_companies_type   ON companies(company_type);
CREATE INDEX IF NOT EXISTS idx_companies_status ON companies(status);
CREATE TRIGGER trg_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- CONTACTS
-- ============================================================
CREATE TABLE IF NOT EXISTS contacts (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID REFERENCES companies(id),
    first_name          TEXT NOT NULL,
    last_name           TEXT,
    email               TEXT,
    phone               TEXT,
    mobile              TEXT,
    role_title          TEXT,
    hubspot_contact_id  TEXT UNIQUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by          TEXT,
    updated_by          TEXT,
    source_system       TEXT,
    source_reference    TEXT,
    status              TEXT NOT NULL DEFAULT 'active',
    notes               TEXT,
    metadata            JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_contacts_company ON contacts(company_id);
CREATE INDEX IF NOT EXISTS idx_contacts_hubspot ON contacts(hubspot_contact_id);
CREATE TRIGGER trg_contacts_updated_at BEFORE UPDATE ON contacts
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- COMPANY ↔ CONTACT JUNCTION
-- ============================================================
CREATE TABLE IF NOT EXISTS company_contacts (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(id),
    contact_id          UUID NOT NULL REFERENCES contacts(id),
    relationship_type   TEXT,   -- primary | billing | field | estimating
    is_primary          BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by          TEXT,
    updated_by          TEXT,
    source_system       TEXT,
    source_reference    TEXT,
    status              TEXT NOT NULL DEFAULT 'active',
    notes               TEXT,
    metadata            JSONB NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE(company_id, contact_id)
);
CREATE TRIGGER trg_company_contacts_updated_at BEFORE UPDATE ON company_contacts
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- PROJECTS
-- ============================================================
CREATE TABLE IF NOT EXISTS projects (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_number          TEXT UNIQUE,        -- HCI internal: 64EW, 101F, 1355R, 83SB
    project_name            TEXT NOT NULL,
    project_aliases         TEXT[],             -- alternate names for search
    client_company_id       UUID REFERENCES companies(id),
    address_line1           TEXT,
    city                    TEXT DEFAULT 'Aspen',
    state                   TEXT DEFAULT 'CO',
    zip                     TEXT,
    project_type            TEXT,               -- full_remodel | exterior | interior | new_construction
    project_status          TEXT DEFAULT 'active', -- active | complete | on_hold | cancelled
    project_manager         TEXT,
    superintendent          TEXT,
    hubspot_deal_id         TEXT,
    google_drive_folder_id  TEXT,
    gsheet_bid_tracker      TEXT,
    start_date              DATE,
    target_completion_date  DATE,
    actual_completion_date  DATE,
    gross_sf                NUMERIC(10,2),
    finished_sf             NUMERIC(10,2),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by              TEXT,
    updated_by              TEXT,
    source_system           TEXT,
    source_reference        TEXT,
    status                  TEXT NOT NULL DEFAULT 'active',
    notes                   TEXT,
    metadata                JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_projects_status  ON projects(project_status);
CREATE INDEX IF NOT EXISTS idx_projects_number  ON projects(project_number);
CREATE TRIGGER trg_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- PROJECT TEAM MEMBERS
-- ============================================================
CREATE TABLE IF NOT EXISTS project_team_members (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id  UUID NOT NULL REFERENCES projects(id),
    contact_id  UUID NOT NULL REFERENCES contacts(id),
    company_id  UUID REFERENCES companies(id),
    role        TEXT,   -- owner | pm | superintendent | architect | engineer | inspector
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by  TEXT,
    updated_by  TEXT,
    source_system TEXT,
    source_reference TEXT,
    status      TEXT NOT NULL DEFAULT 'active',
    notes       TEXT,
    metadata    JSONB NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE(project_id, contact_id, role)
);
CREATE TRIGGER trg_project_team_updated_at BEFORE UPDATE ON project_team_members
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- SEED: Active Projects (4 current HCI projects)
-- ============================================================
INSERT INTO projects (project_number, project_name, project_aliases, project_type, project_status,
                      hubspot_deal_id, gsheet_bid_tracker, city, state)
VALUES
    ('64EW',   '64 Eastwood',    ARRAY['64 Eastwood Dr','Eastwood'],       'exterior',      'active', '332246098523', '1yAmLo3IIp3Vqs3BQJ6QB2O4as0KqXMZxcVvjzGBZDcQ', 'Aspen', 'CO'),
    ('101F',   '101 Francis',    ARRAY['101 W Francis St','Francis'],       'full_remodel',  'active', '332313009897', '1JExX5CeVBedTEFitM8B6hveF4Prhk0Oy6BZSBu058LE', 'Aspen', 'CO'),
    ('1355R',  '1355 Riverside', ARRAY['1355 Riverside Dr','Riverside'],    'full_remodel',  'active', NULL,           '1-64X4XGc4P_GmYl7DRt8nGsBNfaVdP_G3qwfBLJSsnA', 'Aspen', 'CO'),
    ('83SB',   '83 Sagebrusch',  ARRAY['83 Sagebrusch Ln','Sagebrusch'],    'tbd',           'active', NULL,           NULL, 'Aspen', 'CO')
ON CONFLICT (project_number) DO NOTHING;

-- ============================================================
-- HCI AI Operating System — Schema 003: Registries
-- Migration: 003 | Requires: 001, 002
-- Covers: CSI, Cost Codes, Vendors, Procurement, Historical Cost, Bids, Risks, Lessons
-- ============================================================

-- ============================================================
-- CSI DIVISIONS (16-Division MasterFormat)
-- ============================================================
CREATE TABLE IF NOT EXISTS csi_divisions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    division_code   TEXT UNIQUE NOT NULL,   -- '01', '02', ... '16'
    division_name   TEXT NOT NULL,
    description     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    status          TEXT NOT NULL DEFAULT 'active',
    notes           TEXT,
    metadata        JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE TRIGGER trg_csi_updated_at BEFORE UPDATE ON csi_divisions
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- COST CODES
-- ============================================================
CREATE TABLE IF NOT EXISTS cost_codes (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cost_code           TEXT UNIQUE NOT NULL,
    cost_code_name      TEXT NOT NULL,
    csi_division_id     UUID REFERENCES csi_divisions(id),
    parent_cost_code_id UUID REFERENCES cost_codes(id),
    active              BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    status              TEXT NOT NULL DEFAULT 'active',
    notes               TEXT,
    metadata            JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_cost_codes_division ON cost_codes(csi_division_id);
CREATE TRIGGER trg_cost_codes_updated_at BEFORE UPDATE ON cost_codes
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- VENDORS (extended — links to companies)
-- ============================================================
CREATE TABLE IF NOT EXISTS vendors (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID REFERENCES companies(id),
    vendor_name         TEXT NOT NULL,
    primary_trade       TEXT,
    csi_division_id     UUID REFERENCES csi_divisions(id),
    service_area        TEXT DEFAULT 'Roaring Fork Valley',
    preferred_status    TEXT DEFAULT 'approved', -- preferred | approved | probation | blacklisted
    active_status       BOOLEAN DEFAULT TRUE,
    risk_rating         TEXT,   -- low | medium | high
    performance_rating  NUMERIC(3,1),   -- 1.0–5.0
    insurance_status    TEXT DEFAULT 'unknown', -- current | expired | unknown
    insurance_expiry    DATE,
    license_number      TEXT,
    last_bid_date       DATE,
    last_award_date     DATE,
    hubspot_company_id  TEXT,
    hubspot_contact_id  TEXT,
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
CREATE INDEX IF NOT EXISTS idx_vendors_company   ON vendors(company_id);
CREATE INDEX IF NOT EXISTS idx_vendors_trade     ON vendors(primary_trade);
CREATE INDEX IF NOT EXISTS idx_vendors_preferred ON vendors(preferred_status);
CREATE TRIGGER trg_vendors_updated_at BEFORE UPDATE ON vendors
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Now add deferred FK from documents.vendor_id
ALTER TABLE documents ADD CONSTRAINT fk_documents_vendor
    FOREIGN KEY (vendor_id) REFERENCES vendors(id);
ALTER TABLE documents ADD CONSTRAINT fk_documents_csi
    FOREIGN KEY (csi_division_id) REFERENCES csi_divisions(id);

-- ============================================================
-- VENDOR TRADE MAPPINGS (multi-trade vendors)
-- ============================================================
CREATE TABLE IF NOT EXISTS vendor_trade_mappings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id       UUID NOT NULL REFERENCES vendors(id),
    csi_division_id UUID NOT NULL REFERENCES csi_divisions(id),
    trade_name      TEXT,
    confidence_score NUMERIC(4,3) DEFAULT 1.0,
    source          TEXT DEFAULT 'manual',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    status          TEXT NOT NULL DEFAULT 'active',
    notes           TEXT,
    metadata        JSONB NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE(vendor_id, csi_division_id)
);

-- ============================================================
-- VENDOR PROJECT HISTORY
-- ============================================================
CREATE TABLE IF NOT EXISTS vendor_project_history (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id           UUID NOT NULL REFERENCES vendors(id),
    project_id          UUID NOT NULL REFERENCES projects(id),
    scope_description   TEXT,
    contract_amount     NUMERIC(14,2),
    performance_notes   TEXT,
    awarded             BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    source_system       TEXT,
    status              TEXT NOT NULL DEFAULT 'active',
    notes               TEXT,
    metadata            JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_vph_vendor  ON vendor_project_history(vendor_id);
CREATE INDEX IF NOT EXISTS idx_vph_project ON vendor_project_history(project_id);
CREATE TRIGGER trg_vph_updated_at BEFORE UPDATE ON vendor_project_history
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- BID PACKAGES
-- ============================================================
CREATE TABLE IF NOT EXISTS bid_packages (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID NOT NULL REFERENCES projects(id),
    package_name        TEXT NOT NULL,
    csi_division_id     UUID REFERENCES csi_divisions(id),
    scope_description   TEXT,
    bid_due_date        DATE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by          TEXT,
    updated_by          TEXT,
    source_system       TEXT,
    source_reference    TEXT,
    status              TEXT NOT NULL DEFAULT 'open',
    -- open | sent | receiving | leveling | awarded | cancelled
    notes               TEXT,
    metadata            JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_bid_packages_project ON bid_packages(project_id);
CREATE INDEX IF NOT EXISTS idx_bid_packages_status  ON bid_packages(status);
CREATE TRIGGER trg_bid_packages_updated_at BEFORE UPDATE ON bid_packages
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- BID REQUESTS (invitations sent to vendors)
-- ============================================================
CREATE TABLE IF NOT EXISTS bid_requests (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bid_package_id      UUID NOT NULL REFERENCES bid_packages(id),
    vendor_id           UUID NOT NULL REFERENCES vendors(id),
    sent_date           DATE,
    due_date            DATE,
    response_status     TEXT DEFAULT 'pending',
    -- pending | received | declined | no_response
    follow_up_count     INTEGER DEFAULT 0,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    source_system       TEXT,
    status              TEXT NOT NULL DEFAULT 'active',
    notes               TEXT,
    metadata            JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_bid_requests_package ON bid_requests(bid_package_id);
CREATE INDEX IF NOT EXISTS idx_bid_requests_vendor  ON bid_requests(vendor_id);
CREATE TRIGGER trg_bid_requests_updated_at BEFORE UPDATE ON bid_requests
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- BIDS (received bid proposals)
-- ============================================================
CREATE TABLE IF NOT EXISTS bids (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bid_package_id          UUID NOT NULL REFERENCES bid_packages(id),
    vendor_id               UUID NOT NULL REFERENCES vendors(id),
    bid_amount              NUMERIC(14,2),
    received_date           DATE,
    scope_complete          BOOLEAN DEFAULT TRUE,
    exclusions              TEXT,
    clarifications_needed   TEXT,
    schedule_concern        BOOLEAN DEFAULT FALSE,
    budget_concern          BOOLEAN DEFAULT FALSE,
    risk_level              TEXT DEFAULT 'low',   -- low | medium | high
    recommendation          TEXT,
    source_document_id      UUID REFERENCES documents(id),
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
CREATE INDEX IF NOT EXISTS idx_bids_package ON bids(bid_package_id);
CREATE INDEX IF NOT EXISTS idx_bids_vendor  ON bids(vendor_id);
CREATE TRIGGER trg_bids_updated_at BEFORE UPDATE ON bids
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- PROCUREMENT ITEMS
-- ============================================================
CREATE TABLE IF NOT EXISTS procurement_items (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id              UUID NOT NULL REFERENCES projects(id),
    item_name               TEXT NOT NULL,
    csi_division_id         UUID REFERENCES csi_divisions(id),
    cost_code_id            UUID REFERENCES cost_codes(id),
    vendor_id               UUID REFERENCES vendors(id),
    procurement_status      TEXT DEFAULT 'not_started',
    -- not_started | identifying | bidding | awarded | released | on_order | received | installed
    required_on_site_date   DATE,
    release_deadline        DATE,
    actual_release_date     DATE,
    lead_time_days          INTEGER,
    risk_level              TEXT DEFAULT 'low',
    owner_selection_required BOOLEAN DEFAULT FALSE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by              TEXT,
    updated_by              TEXT,
    source_system           TEXT,
    status                  TEXT NOT NULL DEFAULT 'active',
    notes                   TEXT,
    metadata                JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_proc_project ON procurement_items(project_id);
CREATE INDEX IF NOT EXISTS idx_proc_status  ON procurement_items(procurement_status);
CREATE TRIGGER trg_procurement_updated_at BEFORE UPDATE ON procurement_items
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- LONG LEAD ITEMS
-- ============================================================
CREATE TABLE IF NOT EXISTS long_lead_items (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    procurement_item_id     UUID NOT NULL REFERENCES procurement_items(id),
    reason                  TEXT NOT NULL,
    mitigation_plan         TEXT,
    decision_required_by    DATE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    status                  TEXT NOT NULL DEFAULT 'open',
    notes                   TEXT,
    metadata                JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE TRIGGER trg_longlead_updated_at BEFORE UPDATE ON long_lead_items
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- HISTORICAL COST RECORDS
-- ============================================================
CREATE TABLE IF NOT EXISTS historical_cost_records (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID REFERENCES projects(id),
    csi_division_id     UUID REFERENCES csi_divisions(id),
    cost_code_id        UUID REFERENCES cost_codes(id),
    vendor_id           UUID REFERENCES vendors(id),
    description         TEXT NOT NULL,
    budget_amount       NUMERIC(14,2),
    actual_amount       NUMERIC(14,2),
    variance_amount     NUMERIC(14,2) GENERATED ALWAYS AS (actual_amount - budget_amount) STORED,
    variance_percent    NUMERIC(8,4),
    cost_per_gross_sf   NUMERIC(14,2),
    cost_per_finished_sf NUMERIC(14,2),
    source_document_id  UUID REFERENCES documents(id),
    confidence_level    TEXT DEFAULT 'medium',  -- high | medium | low | estimated
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
CREATE INDEX IF NOT EXISTS idx_hcr_project  ON historical_cost_records(project_id);
CREATE INDEX IF NOT EXISTS idx_hcr_csi      ON historical_cost_records(csi_division_id);
CREATE TRIGGER trg_hcr_updated_at BEFORE UPDATE ON historical_cost_records
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- RISKS
-- ============================================================
CREATE TABLE IF NOT EXISTS risks (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id              UUID NOT NULL REFERENCES projects(id),
    category                TEXT,   -- schedule | budget | design | vendor | permit | weather | owner
    description             TEXT NOT NULL,
    severity                TEXT DEFAULT 'medium',  -- low | medium | high | critical
    probability             TEXT DEFAULT 'medium',  -- low | medium | high
    owner                   TEXT,
    target_resolution_date  DATE,
    resolution_date         DATE,
    related_document_id     UUID REFERENCES documents(id),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by              TEXT,
    updated_by              TEXT,
    source_system           TEXT,
    status                  TEXT NOT NULL DEFAULT 'open',  -- open | mitigated | closed
    notes                   TEXT,
    metadata                JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_risks_project ON risks(project_id);
CREATE INDEX IF NOT EXISTS idx_risks_status  ON risks(status);
CREATE TRIGGER trg_risks_updated_at BEFORE UPDATE ON risks
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- LESSONS LEARNED
-- ============================================================
CREATE TABLE IF NOT EXISTS lessons_learned (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id              UUID REFERENCES projects(id),
    category                TEXT,   -- procurement | field | design | vendor | schedule | safety
    issue                   TEXT NOT NULL,
    root_cause              TEXT,
    impact                  TEXT,
    recommendation          TEXT NOT NULL,
    related_sop             TEXT,
    related_document_id     UUID REFERENCES documents(id),
    reusable                BOOLEAN DEFAULT TRUE,
    csi_division_id         UUID REFERENCES csi_divisions(id),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by              TEXT,
    updated_by              TEXT,
    source_system           TEXT,
    status                  TEXT NOT NULL DEFAULT 'active',
    notes                   TEXT,
    metadata                JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_ll_project  ON lessons_learned(project_id);
CREATE INDEX IF NOT EXISTS idx_ll_category ON lessons_learned(category);
CREATE TRIGGER trg_ll_updated_at BEFORE UPDATE ON lessons_learned
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- MVP Sprint 1: Daily Operations Schema
-- Background Learning, Connector Registry, Approval Queue, ROI Log
-- Apply: docker exec -i hci_postgres psql -U hci_admin -d hci_os < 05_Database/mvp_sprint_1_schema.sql

-- ── Background Learning Records ───────────────────────────────────────────────
-- Statuses: Discovered → Access Confirmed → Indexed → Classified → Extracted →
--           Embedded → Linked to Project Brain → Intelligence Candidate Created →
--           Human Review Needed → Approved | Rejected | Archived | Error

CREATE TABLE IF NOT EXISTS background_learning_records (
    id                      SERIAL PRIMARY KEY,
    source_system           VARCHAR(50)   NOT NULL,  -- google_drive, hubspot, houzz, outlook
    source_id               VARCHAR(512)  NOT NULL,  -- file ID, deal ID, project ID, message ID
    source_url              TEXT,
    source_name             TEXT,
    project_id              INTEGER REFERENCES projects(id),
    project_association     VARCHAR(255),
    document_type           VARCHAR(100),  -- drawing, spec, bid, budget, schedule, meeting, photo, rfi, submittal, contract, closeout, other
    status                  VARCHAR(60)   NOT NULL DEFAULT 'Discovered',
    confidence              NUMERIC(4,3)  DEFAULT 0.0,
    title                   TEXT,
    summary                 TEXT,
    metadata                JSONB         DEFAULT '{}',
    related_documents       JSONB         DEFAULT '[]',
    related_vendors         JSONB         DEFAULT '[]',
    related_sops            JSONB         DEFAULT '[]',
    intelligence_candidates JSONB         DEFAULT '[]',
    review_status           VARCHAR(50)   DEFAULT 'Pending',
    reviewed_by             VARCHAR(100),
    reviewed_at             TIMESTAMPTZ,
    error_message           TEXT,
    extraction_timestamp    TIMESTAMPTZ   DEFAULT NOW(),
    created_at              TIMESTAMPTZ   DEFAULT NOW(),
    updated_at              TIMESTAMPTZ   DEFAULT NOW(),
    UNIQUE (source_system, source_id)
);

CREATE INDEX IF NOT EXISTS idx_bl_status        ON background_learning_records(status);
CREATE INDEX IF NOT EXISTS idx_bl_source_system ON background_learning_records(source_system);
CREATE INDEX IF NOT EXISTS idx_bl_project_id    ON background_learning_records(project_id);
CREATE INDEX IF NOT EXISTS idx_bl_review_status ON background_learning_records(review_status);

-- ── Connector Registry ────────────────────────────────────────────────────────
-- Tracks which external sources are registered per project

CREATE TABLE IF NOT EXISTS connector_registry (
    id                  SERIAL PRIMARY KEY,
    project_id          INTEGER REFERENCES projects(id),
    project_code        VARCHAR(50),
    source_system       VARCHAR(50)   NOT NULL,  -- google_drive, hubspot, houzz, outlook
    source_reference    VARCHAR(512),            -- Drive folder path, HubSpot deal ID, Houzz project ID
    connection_status   VARCHAR(50)   DEFAULT 'registered',  -- registered, confirmed, error, disconnected
    read_only           BOOLEAN       DEFAULT TRUE,
    last_discovered     TIMESTAMPTZ,
    last_indexed        TIMESTAMPTZ,
    record_count        INTEGER       DEFAULT 0,
    sync_config         JSONB         DEFAULT '{}',
    notes               TEXT,
    created_at          TIMESTAMPTZ   DEFAULT NOW(),
    updated_at          TIMESTAMPTZ   DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cr_project_id    ON connector_registry(project_id);
CREATE INDEX IF NOT EXISTS idx_cr_source_system ON connector_registry(source_system);

-- ── Approval Queue ────────────────────────────────────────────────────────────
-- Holds ALL proposed write actions pending Buck's explicit approval

CREATE TABLE IF NOT EXISTS approval_queue (
    id                      SERIAL PRIMARY KEY,
    workflow                VARCHAR(100)  NOT NULL,
    action_type             VARCHAR(100)  NOT NULL,  -- hubspot_update, drive_write, houzz_update, email_send, db_write
    target_system           VARCHAR(50)   NOT NULL,
    target_id               VARCHAR(512),
    target_description      TEXT,
    proposed_payload        JSONB         DEFAULT '{}',
    source_data             JSONB         DEFAULT '{}',
    reason                  TEXT,
    project_id              INTEGER REFERENCES projects(id),
    actor                   VARCHAR(100)  DEFAULT 'system',
    status                  VARCHAR(50)   DEFAULT 'pending',  -- pending, approved, rejected, executed, error
    priority                VARCHAR(20)   DEFAULT 'normal',   -- urgent, high, normal, low
    approved_by             VARCHAR(100),
    approved_at             TIMESTAMPTZ,
    executed_at             TIMESTAMPTZ,
    rejected_reason         TEXT,
    rollback_path           TEXT,
    audit_correlation_id    UUID,
    expires_at              TIMESTAMPTZ,
    created_at              TIMESTAMPTZ   DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_aq_status     ON approval_queue(status);
CREATE INDEX IF NOT EXISTS idx_aq_project_id ON approval_queue(project_id);
CREATE INDEX IF NOT EXISTS idx_aq_workflow   ON approval_queue(workflow);

-- ── ROI Log ──────────────────────────────────────────────────────────────────
-- Tracks time saved and value created per workflow run

CREATE TABLE IF NOT EXISTS roi_log (
    id                          SERIAL PRIMARY KEY,
    workflow                    VARCHAR(100)  NOT NULL,
    project_id                  INTEGER REFERENCES projects(id),
    project_code                VARCHAR(50),
    baseline_minutes            NUMERIC(8,2)  DEFAULT 0,   -- manual time estimate
    ai_assisted_minutes         NUMERIC(8,2)  DEFAULT 0,   -- actual time with AI
    minutes_saved               NUMERIC(8,2)  GENERATED ALWAYS AS (baseline_minutes - ai_assisted_minutes) STORED,
    steps_removed               INTEGER       DEFAULT 0,
    documents_processed         INTEGER       DEFAULT 0,
    errors_caught               INTEGER       DEFAULT 0,
    missing_scope_found         INTEGER       DEFAULT 0,
    schedule_risks_detected     INTEGER       DEFAULT 0,
    reporting_time_saved_min    NUMERIC(8,2)  DEFAULT 0,
    notes                       TEXT,
    actor                       VARCHAR(100)  DEFAULT 'system',
    created_at                  TIMESTAMPTZ   DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_roi_workflow   ON roi_log(workflow);
CREATE INDEX IF NOT EXISTS idx_roi_project_id ON roi_log(project_id);

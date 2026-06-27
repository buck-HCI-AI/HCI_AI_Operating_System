-- Migration 012: Project Brain Intelligence — Phase 2
-- Adds persistent health scoring, computed risks, and snapshot history

-- ── Project Brain Snapshots (daily health history for trending) ──────────────
CREATE TABLE IF NOT EXISTS project_brain_snapshots (
    id              SERIAL PRIMARY KEY,
    project_id      INTEGER NOT NULL REFERENCES projects(id),
    snapshot_date   DATE NOT NULL DEFAULT CURRENT_DATE,
    health          TEXT NOT NULL DEFAULT 'GREEN',
    health_factors  JSONB DEFAULT '[]',
    risk_count      INTEGER DEFAULT 0,
    budget_exposure NUMERIC(12,2) DEFAULT 0,
    schedule_variance_days INTEGER DEFAULT 0,
    open_decisions  INTEGER DEFAULT 0,
    open_bids       INTEGER DEFAULT 0,
    ai_summary      TEXT,
    data_completeness_pct NUMERIC(5,1) DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS uidx_pb_snapshots_project_date
    ON project_brain_snapshots (project_id, snapshot_date);

-- ── Computed Risks (auto-detected from data patterns) ────────────────────────
CREATE TABLE IF NOT EXISTS project_risks_computed (
    id              SERIAL PRIMARY KEY,
    project_id      INTEGER NOT NULL REFERENCES projects(id),
    risk_code       TEXT NOT NULL,       -- e.g. SCHED-001, BUDGET-002, PROC-003
    risk_type       TEXT NOT NULL,       -- schedule | budget | procurement | vendor | client | permit
    severity        TEXT NOT NULL DEFAULT 'medium',  -- low | medium | high | critical
    title           TEXT NOT NULL,
    description     TEXT,
    evidence        JSONB DEFAULT '{}',  -- supporting data points
    confidence      NUMERIC(3,1) DEFAULT 0.7,  -- 0-1 AI confidence
    mitigation      TEXT,
    status          TEXT NOT NULL DEFAULT 'open',  -- open | mitigated | closed
    detected_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at     TIMESTAMPTZ,
    source_table    TEXT,               -- which table triggered this risk
    source_id       INTEGER             -- FK to source row
);

CREATE INDEX IF NOT EXISTS idx_proj_risks_project ON project_risks_computed (project_id, status);
CREATE INDEX IF NOT EXISTS idx_proj_risks_severity ON project_risks_computed (severity, status);

-- ── Phase 2 Cross-Project Intelligence snapshots ─────────────────────────────
CREATE TABLE IF NOT EXISTS company_intelligence_snapshots (
    id                  SERIAL PRIMARY KEY,
    snapshot_date       DATE NOT NULL DEFAULT CURRENT_DATE,
    company_health      TEXT NOT NULL DEFAULT 'GREEN',
    active_projects     INTEGER DEFAULT 0,
    total_budget_exposure NUMERIC(14,2) DEFAULT 0,
    avg_schedule_variance NUMERIC(5,1) DEFAULT 0,
    open_decisions      INTEGER DEFAULT 0,
    top_risks           JSONB DEFAULT '[]',
    cross_project_alerts JSONB DEFAULT '[]',
    ai_summary          TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS uidx_company_intel_date
    ON company_intelligence_snapshots (snapshot_date);

-- Seed initial sync states for new connectors (idempotent)
INSERT INTO connector_sync_state (connector_name, entity_type, last_synced_at, status)
VALUES
    ('project_brain', 'intelligence_snapshot', NOW() - INTERVAL '24 hours', 'pending')
ON CONFLICT DO NOTHING;

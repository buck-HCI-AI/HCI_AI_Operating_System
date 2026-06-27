-- Migration 013: Predictive Engine
-- Phase 2, Priority 3 — forward-looking risk predictions per project

CREATE TABLE IF NOT EXISTS predictions_computed (
    id                  SERIAL PRIMARY KEY,
    project_id          INTEGER REFERENCES projects(id),
    prediction_type     TEXT NOT NULL,  -- schedule|budget|permit|procurement|trade_conflict|cash_flow|inspection
    risk_level          TEXT NOT NULL,  -- HIGH|MEDIUM|LOW|CLEAR
    confidence          NUMERIC(4,2),   -- 0.00 to 1.00
    title               TEXT,
    description         TEXT,
    predicted_impact    TEXT,
    evidence            JSONB,          -- [{item, weight}, ...]
    recommended_actions JSONB,          -- [string, ...]
    data_sources        TEXT,
    generated_at        TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (project_id, prediction_type)
);

CREATE INDEX IF NOT EXISTS idx_predictions_project ON predictions_computed(project_id);
CREATE INDEX IF NOT EXISTS idx_predictions_type ON predictions_computed(prediction_type);
CREATE INDEX IF NOT EXISTS idx_predictions_risk ON predictions_computed(risk_level);

-- Company-level prediction aggregates
CREATE TABLE IF NOT EXISTS company_predictions_snapshots (
    id              SERIAL PRIMARY KEY,
    snapshot_date   DATE NOT NULL DEFAULT CURRENT_DATE,
    company_risk    TEXT,               -- HIGH|MEDIUM|LOW
    active_projects INTEGER,
    high_risk_projects INTEGER,
    medium_risk_projects INTEGER,
    top_risks       JSONB,              -- [{project, type, title}, ...]
    summary         TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (snapshot_date)
);

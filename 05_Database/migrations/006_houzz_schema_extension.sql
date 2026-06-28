-- Migration 006: Houzz Schema Extension
-- Sprint 2.5 Platform Hardening | Chief Architect Directive 2026-06-27
-- Extends houzz tables to capture all data Browser Claude is extracting.

-- ── project_schedule_items: add hierarchy + assignment columns ────────────────
ALTER TABLE project_schedule_items
    ADD COLUMN IF NOT EXISTS parent_item_id  TEXT,
    ADD COLUMN IF NOT EXISTS assignee        TEXT,
    ADD COLUMN IF NOT EXISTS completion_pct  NUMERIC(5,2),
    ADD COLUMN IF NOT EXISTS task_type       TEXT,
    ADD COLUMN IF NOT EXISTS notes           TEXT;

-- ── houzz_daily_logs: add structured metadata columns ──────────────────────
ALTER TABLE houzz_daily_logs
    ADD COLUMN IF NOT EXISTS weather         TEXT,
    ADD COLUMN IF NOT EXISTS crew_size       INTEGER,
    ADD COLUMN IF NOT EXISTS author          TEXT,
    ADD COLUMN IF NOT EXISTS raw_json        JSONB;

-- ── houzz_projects: add budget + address columns ───────────────────────────
ALTER TABLE houzz_projects
    ADD COLUMN IF NOT EXISTS address         TEXT,
    ADD COLUMN IF NOT EXISTS budget          NUMERIC(12,2),
    ADD COLUMN IF NOT EXISTS start_date      DATE,
    ADD COLUMN IF NOT EXISTS end_date        DATE,
    ADD COLUMN IF NOT EXISTS project_type    TEXT;

-- ── import_metrics: track per-run extraction quality ──────────────────────
CREATE TABLE IF NOT EXISTS import_metrics (
    id                  SERIAL PRIMARY KEY,
    mining_run_id       INTEGER REFERENCES mining_runs(id),
    source_table        VARCHAR(128) NOT NULL,
    rows_attempted      INTEGER DEFAULT 0,
    rows_imported       INTEGER DEFAULT 0,
    rows_skipped        INTEGER DEFAULT 0,
    rows_duplicate      INTEGER DEFAULT 0,
    rows_failed         INTEGER DEFAULT 0,
    execution_seconds   NUMERIC(8,3),
    validation_errors   JSONB DEFAULT '[]',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_import_metrics_run ON import_metrics(mining_run_id);
CREATE INDEX IF NOT EXISTS idx_import_metrics_table ON import_metrics(source_table, created_at DESC);

-- ── Add import metric columns to mining_runs ───────────────────────────────
ALTER TABLE mining_runs
    ADD COLUMN IF NOT EXISTS rows_skipped       INTEGER DEFAULT 0,
    ADD COLUMN IF NOT EXISTS rows_duplicate     INTEGER DEFAULT 0,
    ADD COLUMN IF NOT EXISTS execution_seconds  NUMERIC(8,3);

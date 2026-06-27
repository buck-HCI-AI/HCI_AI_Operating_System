-- ACR-004: Continuous Mining & Learning Engine
-- Adds mining_runs operational log only.
-- All knowledge stores (historical_cost_records, lessons_learned, vendors, etc.) already exist.

-- Add vendor intelligence fields (safe: additive only)
ALTER TABLE vendors ADD COLUMN IF NOT EXISTS bid_count INTEGER DEFAULT 0;
ALTER TABLE vendors ADD COLUMN IF NOT EXISTS win_rate_pct NUMERIC(5,2);
ALTER TABLE vendors ADD COLUMN IF NOT EXISTS last_bid_date DATE;
ALTER TABLE vendors ADD COLUMN IF NOT EXISTS avg_bid_amount NUMERIC(14,2);
ALTER TABLE vendors ADD COLUMN IF NOT EXISTS preferred_status VARCHAR(50);

-- Add scope_description and source to historical_cost_records
ALTER TABLE historical_cost_records ADD COLUMN IF NOT EXISTS scope_description TEXT;
ALTER TABLE historical_cost_records ADD COLUMN IF NOT EXISTS source VARCHAR(100);

-- Add source_reference to lessons_learned for dedup tracking
ALTER TABLE lessons_learned ADD COLUMN IF NOT EXISTS source_reference VARCHAR(200);
ALTER TABLE lessons_learned ADD COLUMN IF NOT EXISTS recorded_at TIMESTAMPTZ DEFAULT NOW();

CREATE TABLE IF NOT EXISTS mining_runs (
    id                  SERIAL PRIMARY KEY,
    miner_name          VARCHAR(100)    NOT NULL,
    started_at          TIMESTAMPTZ     DEFAULT NOW(),
    completed_at        TIMESTAMPTZ,
    status              VARCHAR(50)     DEFAULT 'running',
    records_scanned     INTEGER         DEFAULT 0,
    records_discovered  INTEGER         DEFAULT 0,
    intelligence_extracted INTEGER      DEFAULT 0,
    items_queued_for_review INTEGER     DEFAULT 0,
    items_auto_written  INTEGER         DEFAULT 0,
    summary             JSONB           DEFAULT '{}',
    error_message       TEXT,
    dry_run             BOOLEAN         DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_mining_runs_miner ON mining_runs(miner_name);
CREATE INDEX IF NOT EXISTS idx_mining_runs_started ON mining_runs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_mining_runs_status ON mining_runs(status);

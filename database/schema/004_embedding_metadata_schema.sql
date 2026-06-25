-- ============================================================
-- HCI AI Operating System — Schema 004: Embedding & Search Metadata
-- Migration: 004 | Requires: 001, 002, 003
-- ============================================================
-- This schema tracks Qdrant collections, embedding jobs, and
-- ensures every vector in Qdrant resolves back to PostgreSQL + MinIO.
-- ============================================================

-- ============================================================
-- QDRANT COLLECTION REGISTRY — what collections exist and what they hold
-- ============================================================
CREATE TABLE IF NOT EXISTS qdrant_collections (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_name TEXT UNIQUE NOT NULL,
    description     TEXT,
    domain          TEXT,       -- book00 | sops | project_documents | vendor_intelligence |
                                -- historical_costs | lessons_learned | procurement
    vector_dim      INTEGER DEFAULT 384,
    embedding_model TEXT DEFAULT 'BAAI/bge-small-en-v1.5',
    distance_metric TEXT DEFAULT 'Cosine',
    point_count     BIGINT DEFAULT 0,
    last_synced_at  TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    status          TEXT NOT NULL DEFAULT 'active',
    notes           TEXT,
    metadata        JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE TRIGGER trg_qdrant_coll_updated_at BEFORE UPDATE ON qdrant_collections
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Seed canonical collections (created at runtime in Qdrant itself)
INSERT INTO qdrant_collections (collection_name, description, domain, vector_dim)
VALUES
    ('hci_book00',              'HCI AI BOOK_00 — canonical engineering manual',     'book00',               384),
    ('hci_sops',                'Standard Operating Procedures and checklists',       'sops',                 384),
    ('hci_project_documents',   'Project docs: bids, specs, drawings, daily reports','project_documents',     384),
    ('hci_vendor_intelligence', 'Vendor profiles, history, performance notes',        'vendor_intelligence',  384),
    ('hci_historical_costs',    'Historical cost records and cost benchmarks',        'historical_costs',     384),
    ('hci_lessons_learned',     'Lessons learned across all projects',                'lessons_learned',      384),
    ('hci_procurement',         'Procurement items, long lead, owner selections',     'procurement',          384)
ON CONFLICT (collection_name) DO NOTHING;

-- ============================================================
-- EMBEDDING JOBS — track async batch embedding operations
-- ============================================================
CREATE TABLE IF NOT EXISTS embedding_jobs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type        TEXT NOT NULL,  -- full_ingest | incremental | reindex | single_doc
    collection_name TEXT NOT NULL,
    document_ids    UUID[],
    total_chunks    INTEGER DEFAULT 0,
    embedded_chunks INTEGER DEFAULT 0,
    failed_chunks   INTEGER DEFAULT 0,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at    TIMESTAMPTZ,
    duration_ms     INTEGER,
    embedding_model TEXT DEFAULT 'BAAI/bge-small-en-v1.5',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    status          TEXT NOT NULL DEFAULT 'queued',  -- queued | running | completed | failed
    notes           TEXT,
    metadata        JSONB NOT NULL DEFAULT '{}'::jsonb,
    error_details   JSONB
);
CREATE INDEX IF NOT EXISTS idx_emb_jobs_status     ON embedding_jobs(status);
CREATE INDEX IF NOT EXISTS idx_emb_jobs_collection ON embedding_jobs(collection_name);
CREATE TRIGGER trg_emb_jobs_updated_at BEFORE UPDATE ON embedding_jobs
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- SEARCH LOG — track semantic search queries for analytics
-- ============================================================
CREATE TABLE IF NOT EXISTS search_log (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_text          TEXT NOT NULL,
    collection_names    TEXT[],
    result_count        INTEGER,
    top_score           NUMERIC(6,4),
    response_time_ms    INTEGER,
    triggered_by        TEXT,   -- api | agent | morning_brief | manual
    user_id             TEXT,
    project_context     UUID REFERENCES projects(id),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata            JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_search_log_created ON search_log(created_at DESC);

-- ============================================================
-- SYNC LOG — generic ingest/sync tracking across all sources
-- ============================================================
CREATE TABLE IF NOT EXISTS sync_log (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_system   TEXT NOT NULL,  -- hubspot | houzz | google_drive | outlook | manual
    sync_type       TEXT NOT NULL,  -- full | incremental | single_object
    records_found   INTEGER DEFAULT 0,
    records_synced  INTEGER DEFAULT 0,
    records_skipped INTEGER DEFAULT 0,
    errors          INTEGER DEFAULT 0,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at    TIMESTAMPTZ,
    duration_ms     INTEGER,
    status          TEXT NOT NULL DEFAULT 'running',  -- running | completed | partial | failed
    notes           TEXT,
    metadata        JSONB NOT NULL DEFAULT '{}'::jsonb,
    error_details   JSONB
);
CREATE INDEX IF NOT EXISTS idx_sync_log_source ON sync_log(source_system);
CREATE INDEX IF NOT EXISTS idx_sync_log_status ON sync_log(status);

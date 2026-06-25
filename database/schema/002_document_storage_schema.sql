-- ============================================================
-- HCI AI Operating System — Schema 002: Document Storage
-- Migration: 002 | Requires: 001_initial_core_schema.sql
-- Rule: MinIO stores files. PostgreSQL stores metadata. Qdrant stores vectors.
-- ============================================================

-- ============================================================
-- DOCUMENTS — master metadata record for every stored file
-- ============================================================
CREATE TABLE IF NOT EXISTS documents (
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id                  UUID REFERENCES projects(id),
    company_id                  UUID REFERENCES companies(id),
    vendor_id                   UUID,                           -- FK to vendors added in 003
    title                       TEXT NOT NULL,
    document_category           TEXT NOT NULL,
    -- drawings|specifications|bids|contracts|procurement|submittals|rfis|change_orders|
    -- budgets|schedules|meeting_minutes|daily_reports|photos|client_correspondence|
    -- vendor_correspondence|sop|template|registry|historical_project|ai_artifact|unknown
    document_type               TEXT,
    original_filename           TEXT NOT NULL,
    normalized_filename         TEXT NOT NULL,
    -- format: {project_number}/{category}/{yyyy}/{yyyymmdd}_{source}_{title}_{ver}.{ext}
    file_extension              TEXT,
    mime_type                   TEXT,
    file_size_bytes             BIGINT,
    checksum_sha256             TEXT NOT NULL,
    storage_bucket              TEXT NOT NULL,
    storage_object_key          TEXT NOT NULL,
    source_system               TEXT,               -- google_drive | outlook | manual | repository | api
    source_uri                  TEXT,
    google_drive_file_id        TEXT,
    hubspot_object_id           TEXT,
    received_date               DATE,
    document_date               DATE,
    version_label               TEXT DEFAULT 'v01',
    supersedes_document_id      UUID REFERENCES documents(id),
    is_current_version          BOOLEAN DEFAULT TRUE,
    processing_status           TEXT DEFAULT 'new',
    -- new | queued | extracting | extracted | failed | skipped
    confidentiality_level       TEXT DEFAULT 'internal',
    -- internal | confidential | public
    retention_class             TEXT,
    extracted_text_available    BOOLEAN DEFAULT FALSE,
    embedding_status            TEXT DEFAULT 'not_embedded',
    -- not_embedded | queued | embedding | embedded | failed
    csi_division_id             UUID,               -- FK to csi_divisions added in 003
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by                  TEXT,
    updated_by                  TEXT,
    status                      TEXT NOT NULL DEFAULT 'active',
    notes                       TEXT,
    metadata                    JSONB NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE(checksum_sha256, storage_bucket)
);
CREATE INDEX IF NOT EXISTS idx_documents_project     ON documents(project_id);
CREATE INDEX IF NOT EXISTS idx_documents_category    ON documents(document_category);
CREATE INDEX IF NOT EXISTS idx_documents_status      ON documents(processing_status);
CREATE INDEX IF NOT EXISTS idx_documents_embedding   ON documents(embedding_status);
CREATE INDEX IF NOT EXISTS idx_documents_gdrive      ON documents(google_drive_file_id);
CREATE INDEX IF NOT EXISTS idx_documents_checksum    ON documents(checksum_sha256);
CREATE TRIGGER trg_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- DOCUMENT VERSIONS
-- ============================================================
CREATE TABLE IF NOT EXISTS document_versions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id         UUID NOT NULL REFERENCES documents(id),
    version_label       TEXT NOT NULL,
    storage_bucket      TEXT NOT NULL,
    storage_object_key  TEXT NOT NULL,
    checksum_sha256     TEXT NOT NULL,
    file_size_bytes     BIGINT,
    created_by          TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    notes               TEXT,
    metadata            JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_doc_versions_doc ON document_versions(document_id);

-- ============================================================
-- DOCUMENT RELATIONSHIPS
-- ============================================================
CREATE TABLE IF NOT EXISTS document_relationships (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_document_id      UUID NOT NULL REFERENCES documents(id),
    child_document_id       UUID NOT NULL REFERENCES documents(id),
    relationship_type       TEXT NOT NULL,
    -- supersedes | references | extracted_from | attachment_of | response_to | related_to
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by              TEXT,
    notes                   TEXT,
    metadata                JSONB NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE(parent_document_id, child_document_id, relationship_type)
);

-- ============================================================
-- DOCUMENT TAGS
-- ============================================================
CREATE TABLE IF NOT EXISTS document_tags (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id     UUID NOT NULL REFERENCES documents(id),
    tag             TEXT NOT NULL,
    source          TEXT,       -- ai | manual | system
    confidence_score NUMERIC(4,3),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by      TEXT,
    metadata        JSONB NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE(document_id, tag)
);
CREATE INDEX IF NOT EXISTS idx_document_tags_doc ON document_tags(document_id);
CREATE INDEX IF NOT EXISTS idx_document_tags_tag ON document_tags(tag);

-- ============================================================
-- DOCUMENT PROCESSING EVENTS — audit trail for every ingestion step
-- ============================================================
CREATE TABLE IF NOT EXISTS document_processing_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id     UUID NOT NULL REFERENCES documents(id),
    event_type      TEXT NOT NULL,
    -- received | checksum | duplicate_check | classify | store_raw | extract_text |
    -- store_processed | chunk | embed | complete | error
    event_status    TEXT NOT NULL,  -- started | completed | failed | skipped
    message         TEXT,
    processor_name  TEXT,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at    TIMESTAMPTZ,
    duration_ms     INTEGER,
    error_details   JSONB,
    metadata        JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_proc_events_doc    ON document_processing_events(document_id);
CREATE INDEX IF NOT EXISTS idx_proc_events_type   ON document_processing_events(event_type);
CREATE INDEX IF NOT EXISTS idx_proc_events_status ON document_processing_events(event_status);

-- ============================================================
-- DOCUMENT CHUNKS — each embedded chunk resolves back to doc + Qdrant
-- ============================================================
CREATE TABLE IF NOT EXISTS document_chunks (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id         UUID NOT NULL REFERENCES documents(id),
    chunk_index         INTEGER NOT NULL,
    chunk_text          TEXT NOT NULL,
    token_count         INTEGER,
    page_number         INTEGER,
    section_title       TEXT,
    storage_bucket      TEXT,
    storage_object_key  TEXT,
    qdrant_collection   TEXT NOT NULL,
    qdrant_point_id     TEXT,
    embedding_model     TEXT DEFAULT 'BAAI/bge-small-en-v1.5',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata            JSONB NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE(document_id, chunk_index)
);
CREATE INDEX IF NOT EXISTS idx_chunks_document  ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_qdrant    ON document_chunks(qdrant_collection, qdrant_point_id);

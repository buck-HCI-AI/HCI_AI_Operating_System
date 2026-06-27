-- Migration 016: Project Brain Extended Memory (BTW-4)
-- Event timeline, AI conversation memory, document relationships, daily summaries

-- ── Project Event Timeline ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS project_events (
    id              SERIAL PRIMARY KEY,
    project_id      INTEGER NOT NULL REFERENCES projects(id),
    event_type      TEXT NOT NULL,  -- milestone|risk|decision|change_order|document|issue|resolution|note
    event_date      DATE NOT NULL DEFAULT CURRENT_DATE,
    title           TEXT NOT NULL,
    description     TEXT,
    source_table    TEXT,           -- which table originated this event (meetings, daily_logs, etc.)
    source_id       INTEGER,        -- FK to originating row
    created_by      TEXT NOT NULL DEFAULT 'system',  -- system|claude_code|user
    metadata        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_proj_events_project_date
    ON project_events (project_id, event_date DESC);
CREATE INDEX IF NOT EXISTS idx_proj_events_type
    ON project_events (project_id, event_type);

-- ── AI Conversation Memory ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS project_ai_conversations (
    id              SERIAL PRIMARY KEY,
    project_id      INTEGER NOT NULL REFERENCES projects(id),
    session_id      TEXT,
    question        TEXT NOT NULL,
    answer_summary  TEXT,           -- condensed version of the answer for fast recall
    full_answer     TEXT,           -- full response for retrieval
    context_used    JSONB NOT NULL DEFAULT '[]',  -- [{source, collection, score}]
    tokens_used     INTEGER,
    model_used      TEXT DEFAULT 'claude-haiku-4-5-20251001',
    queried_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_proj_conversations_project
    ON project_ai_conversations (project_id, queried_at DESC);

-- ── Document Relationships ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS project_document_links (
    id                  SERIAL PRIMARY KEY,
    project_id          INTEGER NOT NULL REFERENCES projects(id),
    document_type       TEXT NOT NULL,  -- bid|meeting|daily_log|drive_file|houzz_file|hubspot_note|email
    document_id         TEXT NOT NULL,  -- external ID or internal row ID as text
    document_name       TEXT NOT NULL,
    document_date       DATE,
    linked_entity_type  TEXT NOT NULL,  -- decision|risk|change_order|milestone|issue|vendor
    linked_entity_id    TEXT,           -- ID of the linked entity (flexible)
    linked_entity_name  TEXT,
    relationship        TEXT NOT NULL DEFAULT 'documented',  -- drove|supported|contradicted|documented|resolved
    notes               TEXT,
    linked_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          TEXT NOT NULL DEFAULT 'system'
);

CREATE INDEX IF NOT EXISTS idx_proj_doc_links_project
    ON project_document_links (project_id, document_type);
CREATE INDEX IF NOT EXISTS idx_proj_doc_links_entity
    ON project_document_links (project_id, linked_entity_type);

-- ── Daily Project Summaries ──────────────────────────────────────────────────
-- Reuses project_brain_snapshots for health + adds text summary column (already exists)
-- New table for richer daily summary storage
CREATE TABLE IF NOT EXISTS project_daily_summaries (
    id              SERIAL PRIMARY KEY,
    project_id      INTEGER NOT NULL REFERENCES projects(id),
    summary_date    DATE NOT NULL DEFAULT CURRENT_DATE,
    health          TEXT NOT NULL DEFAULT 'GREEN',
    ai_summary      TEXT NOT NULL,
    key_risks       JSONB NOT NULL DEFAULT '[]',      -- top 3 risks this day
    key_actions     JSONB NOT NULL DEFAULT '[]',      -- top 3 recommended actions
    event_count     INTEGER DEFAULT 0,                -- events logged today
    decisions_open  INTEGER DEFAULT 0,
    generated_by    TEXT NOT NULL DEFAULT 'system',   -- system|scheduled|on_demand
    generated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS uidx_proj_daily_summaries_date
    ON project_daily_summaries (project_id, summary_date);

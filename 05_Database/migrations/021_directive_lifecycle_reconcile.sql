-- Migration 021: Directive lifecycle vocabulary reconciliation + heartbeat fields
-- Per Chief Architect (ChatGPT) ARB directive 2026-07-01 ("Implementation Directive:
-- Sprint State Fixes + AI Communication Reliability"): directive lifecycle must be
-- ISSUED -> RECEIVED -> IN_PROGRESS -> COMPLETE, plus BLOCKED / REJECTED.
-- ADR-007 flagged this exact vocabulary conflict as "not silently resolved, needs
-- Chief Architect reconciliation" — this migration is that reconciliation.
-- Extends ai_messages (migration 018/019) rather than creating a new ai_directives
-- table, per "extend before creating / one source of truth".

BEGIN;

-- Drop the old check constraint before rewriting values
ALTER TABLE ai_messages DROP CONSTRAINT IF EXISTS ai_messages_status_chk;

UPDATE ai_messages SET status = 'ISSUED'   WHERE status = 'NEW';
UPDATE ai_messages SET status = 'REJECTED' WHERE status = 'FAILED';

ALTER TABLE ai_messages ALTER COLUMN status SET DEFAULT 'ISSUED';

ALTER TABLE ai_messages ADD CONSTRAINT ai_messages_status_chk CHECK (status IN
    ('ISSUED','RECEIVED','IN_PROGRESS','BLOCKED','COMPLETE','NEEDS_BUCK_APPROVAL','REJECTED','STALE'));

ALTER TABLE ai_messages
    ADD COLUMN IF NOT EXISTS priority             VARCHAR(20) NOT NULL DEFAULT 'medium',
    ADD COLUMN IF NOT EXISTS received_at           TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS acknowledged_at       TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS started_at            TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS completed_at          TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS blocked_reason        TEXT,
    ADD COLUMN IF NOT EXISTS source_of_truth_link  TEXT;

ALTER TABLE ai_messages
    ADD CONSTRAINT ai_messages_priority_chk CHECK (priority IN ('low','medium','high','critical'));

-- Backfill lifecycle timestamps for existing rows so historical data isn't left null
-- for states that already imply a timestamp happened.
UPDATE ai_messages SET received_at = telegram_acknowledged_at
    WHERE status NOT IN ('ISSUED') AND received_at IS NULL AND telegram_acknowledged_at IS NOT NULL;
UPDATE ai_messages SET completed_at = updated_at
    WHERE status = 'COMPLETE' AND completed_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_ai_messages_priority ON ai_messages (priority, status);

-- Heartbeat: role, current_task, last_directive_id, metadata per ARB spec
ALTER TABLE ai_agent_heartbeat
    ADD COLUMN IF NOT EXISTS role              VARCHAR(100),
    ADD COLUMN IF NOT EXISTS current_task       TEXT,
    ADD COLUMN IF NOT EXISTS last_directive_id   INTEGER,
    ADD COLUMN IF NOT EXISTS metadata            JSONB NOT NULL DEFAULT '{}'::jsonb;

UPDATE ai_agent_heartbeat SET role = CASE agent
    WHEN 'chatgpt' THEN 'Chief Architect / ARB'
    WHEN 'claude_code' THEN 'Implementation'
    WHEN 'browser_claude' THEN 'Repository Governance'
    WHEN 'n8n' THEN 'Automation'
    ELSE role END
WHERE role IS NULL;

COMMIT;

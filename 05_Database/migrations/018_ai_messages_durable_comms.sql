-- Migration 018: AI Messages — Durable Agent Communication + Telegram Approval Bridge
-- Patch (per "Claude Dode V2" urgent directive 2026-06-30): DB is source of truth,
-- Telegram is a notification layer only. Minimal table — audit confirmed no existing
-- table (platform_events, approval_queue, handoff Inbox) covers this state machine.

CREATE TABLE IF NOT EXISTS ai_messages (
    id                      SERIAL PRIMARY KEY,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source                  VARCHAR(50) NOT NULL,   -- buck|chatgpt|claude_code|browser_claude|n8n|system
    target                  VARCHAR(50) NOT NULL,   -- buck|chatgpt|claude_code|browser_claude|n8n|all
    project_code            VARCHAR(20),
    message_type            VARCHAR(50) NOT NULL,   -- approval_request|risk_alert|blocked_mission|handoff_waiting|work_complete|review_required|status|note
    title                   TEXT NOT NULL,
    body                    TEXT NOT NULL,
    status                  VARCHAR(30) NOT NULL DEFAULT 'NEW',
        -- NEW | ACKNOWLEDGED | IN_PROGRESS | BLOCKED | COMPLETE | NEEDS_BUCK_APPROVAL | REJECTED | STALE
    requires_buck_approval  BOOLEAN NOT NULL DEFAULT FALSE,
    approval_type           VARCHAR(50),            -- hubspot_write|drive_write|email_send|contract|external_commitment|other
    telegram_sent_at        TIMESTAMPTZ,
    telegram_message_id     BIGINT,
    telegram_acknowledged_at TIMESTAMPTZ,
    retry_count             INTEGER NOT NULL DEFAULT 0,
    last_error               TEXT,
    related_file             TEXT,
    related_handoff_id       TEXT,
    CONSTRAINT ai_messages_status_chk CHECK (status IN
        ('NEW','ACKNOWLEDGED','IN_PROGRESS','BLOCKED','COMPLETE','NEEDS_BUCK_APPROVAL','REJECTED','STALE'))
);

CREATE INDEX IF NOT EXISTS idx_ai_messages_status        ON ai_messages (status);
CREATE INDEX IF NOT EXISTS idx_ai_messages_target         ON ai_messages (target, status);
CREATE INDEX IF NOT EXISTS idx_ai_messages_project        ON ai_messages (project_code);
CREATE INDEX IF NOT EXISTS idx_ai_messages_approval       ON ai_messages (requires_buck_approval, status);
CREATE INDEX IF NOT EXISTS idx_ai_messages_created        ON ai_messages (created_at DESC);

-- One row per known agent, last-seen timestamp updated on any gateway call that
-- identifies its source. Genuine gap confirmed by audit: zero heartbeat concept existed.
CREATE TABLE IF NOT EXISTS ai_agent_heartbeat (
    agent           VARCHAR(50) PRIMARY KEY,   -- chatgpt|claude_code|browser_claude|n8n
    last_seen_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_action     TEXT,
    status          VARCHAR(20) NOT NULL DEFAULT 'OFFLINE'
        -- ONLINE | OFFLINE | STALE | RECOVERING | BLOCKED (per Warm Start Recovery patch, 2026-06-30)
);

INSERT INTO ai_agent_heartbeat (agent, status, last_action)
VALUES ('chatgpt', 'OFFLINE', 'seed'),
       ('claude_code', 'ONLINE', 'AI Operations Control Plane v1 patch'),
       ('browser_claude', 'OFFLINE', 'seed'),
       ('n8n', 'OFFLINE', 'seed')
ON CONFLICT (agent) DO NOTHING;

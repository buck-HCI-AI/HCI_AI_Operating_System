-- Migration 020: AD-12.1 Approval Queue Cleanup (ratified 2026-06-30)
-- Internal system automation events (drive upload confirmations, health checks,
-- verify loops) were being queued for Buck's approval alongside genuine
-- externally-impacting actions, diluting the queue. Only externally-impacting
-- actions should require human approval; internal events go to activity_log.

CREATE TABLE IF NOT EXISTS activity_log (
    id              SERIAL PRIMARY KEY,
    event_type      VARCHAR(100) NOT NULL,   -- mirrors approval_queue.action_type for these categories
    target_system   VARCHAR(50),
    target_id       VARCHAR(512),
    description     TEXT,
    payload         JSONB DEFAULT '{}',
    actor           VARCHAR(100) DEFAULT 'system',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_activity_log_type    ON activity_log (event_type);
CREATE INDEX IF NOT EXISTS idx_activity_log_created ON activity_log (created_at DESC);

-- Void existing pending internal-noise items (does not touch vendor_candidate or
-- other genuinely external items — AD-12.1 names these four categories only)
UPDATE approval_queue
SET status = 'void', rejected_reason = 'AD-12.1: internal system automation event, not an externally-impacting action'
WHERE status = 'pending'
  AND action_type IN ('drive_upload_file', 'verify_approval_loop', 'system_check', 'health_check');

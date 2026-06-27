-- Migration 008: Missions Table
-- Sprint 4 — AI Program Manager | 2026-06-27
-- Replaces MISSION_QUEUE.md as the authoritative mission store.

CREATE TABLE IF NOT EXISTS missions (
    id              SERIAL PRIMARY KEY,
    mission_id      VARCHAR(32) NOT NULL UNIQUE,   -- e.g. MISSION-001
    title           VARCHAR(256) NOT NULL,
    description     TEXT,
    assigned_to     VARCHAR(64),                    -- claude_code, browser_claude, n8n, system
    status          VARCHAR(16) NOT NULL DEFAULT 'OPEN',
    -- OPEN / IN_PROGRESS / BLOCKED / COMPLETE / CANCELLED
    blocker         TEXT,                           -- why it's blocked
    priority        VARCHAR(8) NOT NULL DEFAULT 'MEDIUM',  -- HIGH / MEDIUM / LOW
    depends_on      VARCHAR(32)[],                  -- array of mission_ids this depends on
    expected_output TEXT,                           -- what done looks like
    auto_retry      BOOLEAN NOT NULL DEFAULT FALSE, -- retry on unblock
    sprint          VARCHAR(32),                    -- e.g. Sprint-4
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    last_activity   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_missions_status      ON missions(status, priority);
CREATE INDEX IF NOT EXISTS idx_missions_assigned_to ON missions(assigned_to);
CREATE INDEX IF NOT EXISTS idx_missions_mission_id  ON missions(mission_id);

-- Notification escalations log — tracks what alerts have been sent
CREATE TABLE IF NOT EXISTS notification_log (
    id              SERIAL PRIMARY KEY,
    event_type      VARCHAR(64) NOT NULL,
    entity_type     VARCHAR(32),                    -- exec_inbox / mission / system
    entity_id       VARCHAR(64),
    severity        VARCHAR(16) NOT NULL,           -- CRITICAL / HIGH / MEDIUM / LOW
    providers_used  TEXT[],
    message         TEXT,
    sent_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    success         BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_notify_log_entity ON notification_log(entity_type, entity_id, sent_at DESC);

-- Seed Sprint 4 missions from MISSION_QUEUE.md
INSERT INTO missions (mission_id, title, description, assigned_to, status, blocker, priority, sprint, expected_output)
VALUES
  ('MISSION-001',
   'Houzz 101 Francis Data Bootstrap',
   'Browser Claude extracts all Houzz data for 101 Francis (project 3218059) and POSTs to /api/v1/services/houzz/ingest. Includes 29+ daily logs and 36+ schedule items.',
   'browser_claude', 'BLOCKED',
   'Waiting for EXEC-002 approval (Houzz write authorization) and Browser Claude session',
   'HIGH', 'Sprint-3',
   'houzz_projects table has 101 Francis record; daily_logs and schedule_items populated; HouzzMiner activates'),

  ('MISSION-002',
   'Sprint 3 Executive Dashboard',
   'Build executive router with dashboard, morning-brief, driving-brief, and one-tap approve/reject/defer endpoints.',
   'claude_code', 'COMPLETE',
   NULL, 'HIGH', 'Sprint-3',
   'All executive endpoints return 200; HTML dashboard live at /executive'),

  ('MISSION-003',
   'Gate 5 Pilot Monitoring',
   'Monitor 64 Eastwood, 101 Francis, 1355 Riverside through pilot close 2026-07-01. No system disruptions.',
   'system', 'IN_PROGRESS',
   NULL, 'HIGH', 'Sprint-3',
   'Pilot closes 2026-07-01 with all 3 projects healthy'),

  ('MISSION-004',
   'Vendor Registry Deduplication',
   'Merge 6 vendor groups (17 → 6 records) after EXEC-001 approval.',
   'claude_code', 'BLOCKED',
   'Waiting for EXEC-001 approval from Buck',
   'MEDIUM', 'Sprint-4',
   'vendor count 392 → 386; no duplicate vendor IDs'),

  ('MISSION-005',
   'Sprint 4 — Executive Operating Cycle',
   'Build EOD brief, batch-approve, auto-escalation, ntfy push, missions API.',
   'claude_code', 'IN_PROGRESS',
   NULL, 'HIGH', 'Sprint-4',
   'EOD brief 200; ntfy push tested; batch-approve 200; escalation n8n active')
ON CONFLICT (mission_id) DO UPDATE SET
    status = EXCLUDED.status,
    blocker = EXCLUDED.blocker,
    sprint = EXCLUDED.sprint,
    updated_at = NOW();

-- Update MISSION-002 as complete
UPDATE missions SET status = 'COMPLETE', completed_at = NOW() WHERE mission_id = 'MISSION-002';

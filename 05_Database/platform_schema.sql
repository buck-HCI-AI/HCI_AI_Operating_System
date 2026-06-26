-- HCI AI Platform Integration Layer — Schema
-- Version: 1.0 | Date: 2026-06-26
-- Shared capabilities: Identity, Event Bus, Notifications, Audit Trail, Search Gateway
--
-- Run after sop_execution_schema.sql:
--   docker exec -i hci_postgres psql -U hci_admin -d hci_os < 05_Database/platform_schema.sql

-- ─────────────────────────────────────────────────────────────────────────────
-- IDENTITY & PERMISSIONS
-- Actor registry maps names/handles to roles and permissions.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS platform_users (
    id          SERIAL PRIMARY KEY,
    actor_name  VARCHAR(100) UNIQUE NOT NULL,   -- "Buck Adams", "pm", "AI", "super"
    role        VARCHAR(50)  NOT NULL DEFAULT 'pm',
    email       TEXT,
    phone       TEXT,
    active      BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_platform_users_actor ON platform_users (actor_name);
CREATE INDEX IF NOT EXISTS idx_platform_users_role  ON platform_users (role);

CREATE TABLE IF NOT EXISTS platform_permissions (
    id          SERIAL PRIMARY KEY,
    role        VARCHAR(50)  NOT NULL,
    permission  VARCHAR(100) NOT NULL,
    UNIQUE (role, permission)
);
CREATE INDEX IF NOT EXISTS idx_platform_perms_role ON platform_permissions (role);

-- Seed: core actors and roles
INSERT INTO platform_users (actor_name, role, email) VALUES
    ('Buck Adams',      'owner',          'buck@ahmaspen.com'),
    ('pm',              'pm',             NULL),
    ('super',           'superintendent', NULL),
    ('AI',              'ai_agent',       NULL),
    ('contracts_team',  'contracts',      NULL),
    ('system',          'system',         NULL)
ON CONFLICT (actor_name) DO NOTHING;

-- Seed: role permissions
INSERT INTO platform_permissions (role, permission) VALUES
    ('owner',          'approve_budget'),
    ('owner',          'approve_award'),
    ('owner',          'approve_contract'),
    ('owner',          'approve_change_order'),
    ('owner',          'approve_exception'),
    ('owner',          'issue_commitment'),
    ('owner',          'view_all'),
    ('pm',             'draft_sop'),
    ('pm',             'confirm_inputs'),
    ('pm',             'approve_internal'),
    ('pm',             'request_approval'),
    ('pm',             'view_project'),
    ('superintendent', 'confirm_field'),
    ('superintendent', 'approve_safety'),
    ('superintendent', 'log_daily'),
    ('superintendent', 'view_project'),
    ('ai_agent',       'draft_content'),
    ('ai_agent',       'read_data'),
    ('contracts',      'initiate_contract'),
    ('contracts',      'confirm_compliance'),
    ('system',         'internal_event')
ON CONFLICT (role, permission) DO NOTHING;

-- ─────────────────────────────────────────────────────────────────────────────
-- EVENT BUS
-- Lightweight in-process publish/subscribe. All domain events stored here.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS platform_events (
    id              SERIAL PRIMARY KEY,
    event_type      VARCHAR(100) NOT NULL,  -- "sop.status_changed", "gate.approved"
    source_service  VARCHAR(50),            -- "sop_16", "workflow_003"
    entity_type     VARCHAR(50),            -- "sop_instance", "project", "vendor"
    entity_id       INTEGER,
    project_id      INTEGER REFERENCES projects(id) ON DELETE SET NULL,
    payload         JSONB,
    actor           VARCHAR(100),
    published_at    TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_platform_events_type       ON platform_events (event_type);
CREATE INDEX IF NOT EXISTS idx_platform_events_entity     ON platform_events (entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_platform_events_project    ON platform_events (project_id);
CREATE INDEX IF NOT EXISTS idx_platform_events_published  ON platform_events (published_at DESC);

-- ─────────────────────────────────────────────────────────────────────────────
-- NOTIFICATION CENTER
-- In-system notifications with optional email delivery.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS platform_notifications (
    id                  SERIAL PRIMARY KEY,
    recipient           VARCHAR(100) NOT NULL,
    notification_type   VARCHAR(50)  NOT NULL,  -- "approval_required", "work_stopped", "ai_ready"
    title               TEXT NOT NULL,
    body                TEXT,
    entity_type         VARCHAR(50),
    entity_id           INTEGER,
    project_id          INTEGER REFERENCES projects(id) ON DELETE SET NULL,
    action_url          TEXT,
    is_read             BOOLEAN DEFAULT FALSE,
    email_sent          BOOLEAN DEFAULT FALSE,
    delivered_at        TIMESTAMPTZ DEFAULT NOW(),
    read_at             TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_platform_notif_recipient ON platform_notifications (recipient);
CREATE INDEX IF NOT EXISTS idx_platform_notif_type      ON platform_notifications (notification_type);
CREATE INDEX IF NOT EXISTS idx_platform_notif_unread    ON platform_notifications (recipient, is_read) WHERE is_read = FALSE;
CREATE INDEX IF NOT EXISTS idx_platform_notif_project   ON platform_notifications (project_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- AUDIT TRAIL
-- Cross-service audit log. Supplements sop_workflow_events for platform-level events.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS platform_audit_log (
    id              SERIAL PRIMARY KEY,
    source          VARCHAR(50) NOT NULL,      -- "sop", "workflow", "notification", "identity"
    entity_type     VARCHAR(50),               -- "sop_instance", "project", "user"
    entity_id       INTEGER,
    project_id      INTEGER REFERENCES projects(id) ON DELETE SET NULL,
    event_type      VARCHAR(100) NOT NULL,     -- "status_changed", "gate_approved", "notif_sent"
    actor           VARCHAR(100),
    summary         TEXT,
    payload         JSONB,
    occurred_at     TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_audit_source       ON platform_audit_log (source);
CREATE INDEX IF NOT EXISTS idx_audit_entity       ON platform_audit_log (entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_project      ON platform_audit_log (project_id);
CREATE INDEX IF NOT EXISTS idx_audit_actor        ON platform_audit_log (actor);
CREATE INDEX IF NOT EXISTS idx_audit_occurred     ON platform_audit_log (occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_event_type   ON platform_audit_log (event_type);

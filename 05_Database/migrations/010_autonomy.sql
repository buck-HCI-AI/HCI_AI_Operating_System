-- Migration 010: Autonomy Backlog + Self-Improvement Loop
-- 2026-06-27 | Autonomous Development Mode

CREATE TABLE IF NOT EXISTS autonomy_opportunities (
    id              SERIAL PRIMARY KEY,
    opportunity_id  VARCHAR(64) NOT NULL UNIQUE,   -- AUTO-001, AUTO-002, etc.
    title           VARCHAR(512) NOT NULL,
    description     TEXT,
    detected_by     VARCHAR(128),                  -- claude_code, buck, mining_engine
    category        VARCHAR(64),                   -- repetitive_task, data_gap, workflow_gap, risk
    current_process TEXT,                          -- what happens manually now
    proposed_automation TEXT,                      -- what AI would do instead
    estimated_minutes_per_week NUMERIC(8,2),       -- manual time saved per week
    frequency_per_week NUMERIC(6,2),               -- how often task occurs
    roi_score       NUMERIC(8,2) GENERATED ALWAYS AS
                        (COALESCE(estimated_minutes_per_week, 0) * COALESCE(frequency_per_week, 1)) STORED,
    feasibility     VARCHAR(16) DEFAULT 'medium',  -- low/medium/high
    status          VARCHAR(32) DEFAULT 'backlog', -- backlog/in_progress/complete/deferred/rejected
    sprint_target   VARCHAR(32),
    implementation_notes TEXT,
    approved_by     VARCHAR(128),
    approved_at     TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_autonomy_status ON autonomy_opportunities(status, roi_score DESC);
CREATE INDEX IF NOT EXISTS idx_autonomy_category ON autonomy_opportunities(category);

-- Initial opportunities detected during system build
INSERT INTO autonomy_opportunities (opportunity_id, title, description, detected_by, category,
    current_process, proposed_automation, estimated_minutes_per_week, frequency_per_week, feasibility, status)
VALUES
(
    'AUTO-001',
    'Houzz daily log extraction',
    'Browser Claude extracts daily logs from Houzz for all active projects',
    'claude_code', 'repetitive_task',
    'Manual: open Houzz → navigate to each project → copy log entries',
    'Browser Agent extracts all logs automatically, sends to /ingest/full endpoint',
    30, 5, 'high', 'backlog'
),
(
    'AUTO-002',
    'Change order status monitoring',
    'Auto-detect new/updated change orders in Houzz and surface to Executive Inbox',
    'claude_code', 'risk',
    'Manual: check Houzz CO tab on each project periodically',
    'Houzz Connector incremental sync → new COs → Executive Inbox with approval request',
    20, 7, 'high', 'backlog'
),
(
    'AUTO-003',
    'Subcontractor insurance expiry alerts',
    'Alert when sub insurance within 30 days of expiring',
    'claude_code', 'risk',
    'Manual: quarterly insurance expiry audit',
    'houzz_subcontractors.insurance_expiry → daily check → ntfy alert + Executive Inbox',
    60, 0.25, 'high', 'backlog'
),
(
    'AUTO-004',
    'Budget vs. actual variance alerts',
    'Auto-detect categories >10% over budget and surface to Executive Inbox',
    'claude_code', 'risk',
    'Manual: review budget tab in Houzz each week',
    'houzz_budget.variance field → weekly scan → HIGH severity inbox item if >10%',
    30, 1, 'high', 'backlog'
),
(
    'AUTO-005',
    'Bid package status aggregation',
    'Auto-aggregate bid statuses across all 3 projects for morning brief',
    'claude_code', 'repetitive_task',
    'Manual: check 3 Google Sheets bid trackers each morning',
    'bid-leveling service → morning brief endpoint → single card in executive dashboard',
    45, 5, 'high', 'backlog'
),
(
    'AUTO-006',
    'Pending selection due date alerts',
    'Alert when client selections are due within 7 days',
    'claude_code', 'workflow_gap',
    'Manual: check Houzz selections tab and filter by due date',
    'houzz_selections daily scan → selections due <7 days → push notification with link',
    15, 7, 'medium', 'backlog'
),
(
    'AUTO-007',
    'HubSpot deal stage sync from project milestones',
    'Auto-update HubSpot deal stage when Houzz project reaches milestone',
    'claude_code', 'data_gap',
    'Manual: update HubSpot after milestone completion',
    'Connector detects milestone → approval_queue → Buck approves → HubSpot write',
    20, 1, 'medium', 'backlog'
)
ON CONFLICT (opportunity_id) DO NOTHING;

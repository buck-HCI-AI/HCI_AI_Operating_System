-- Migration 007: Executive Inbox
-- Sprint 3 — Executive Experience | 2026-06-27
-- Stores structured OWNER-level decisions for the executive dashboard.

CREATE TABLE IF NOT EXISTS executive_inbox (
    id                  SERIAL PRIMARY KEY,
    exec_id             VARCHAR(32) NOT NULL UNIQUE,   -- e.g. EXEC-001
    title               VARCHAR(256) NOT NULL,
    decision            TEXT NOT NULL,
    recommendation      VARCHAR(16) NOT NULL,           -- Approve / Reject / Defer
    confidence          VARCHAR(16) NOT NULL,           -- High / Medium / Low
    business_impact     TEXT,
    risk_description    TEXT,
    deadline            DATE,
    action_type         VARCHAR(64),                    -- vendor_merge, db_write, etc.
    action_payload      JSONB NOT NULL DEFAULT '{}',
    status              VARCHAR(16) NOT NULL DEFAULT 'pending',  -- pending / approved / rejected / deferred
    approve_token       VARCHAR(64) UNIQUE,
    reject_token        VARCHAR(64) UNIQUE,
    defer_token         VARCHAR(64) UNIQUE,
    token_expires_at    TIMESTAMPTZ,
    resolved_at         TIMESTAMPTZ,
    resolved_by         VARCHAR(64),
    approval_queue_id   INTEGER REFERENCES approval_queue(id) ON DELETE SET NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_exec_inbox_status ON executive_inbox(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_exec_inbox_exec_id ON executive_inbox(exec_id);
CREATE INDEX IF NOT EXISTS idx_exec_inbox_tokens ON executive_inbox(approve_token, reject_token, defer_token);

-- Seed current inbox items
INSERT INTO executive_inbox (exec_id, title, decision, recommendation, confidence, business_impact, risk_description, deadline, action_type, action_payload)
VALUES
  ('EXEC-001',
   'Merge 6 vendor groups (17 → 6 records)',
   'Merge 17 duplicate vendor records across 6 groups into 6 clean records. All bid entries remain linked.',
   'Approve', 'High',
   'Vendor count 392 → 386. Reporting becomes accurate. Duplicate vendor intelligence eliminated.',
   'Low. Additive merge with backup before execution. Fully reversible.',
   NULL, 'vendor_merge',
   '{"groups": ["Ajax Mechanical Services x7", "2H Mechanical x2", "AAA Mountain Waterproofing x2", "ANB Bank x2", "Ajac Stone x2", "Ajax Electric x2"]}'
  ),
  ('EXEC-002',
   'Write 101 Francis Houzz project record',
   'Persist 101 Francis project (Houzz ID 3218059) to houzz_projects table.',
   'Approve', 'High',
   'Unlocks Houzz intelligence pipeline. HouzzMiner activates. Daily log + schedule intelligence begins.',
   'Low. Internal database write only. Idempotent.',
   '2026-07-01', 'houzz_write',
   '{"houzz_project_id": "3218059", "name": "101 Francis", "client_name": "Adnan Rawjee", "status": "open", "address": "101 W Francis St, Aspen, CO 81611"}'
  ),
  ('EXEC-003',
   'Import Pacific Concrete bid ($185,000)',
   'Import Pacific Concrete Inc. bid record. Division: Concrete. Amount: $185,000. Project: 101 Francis.',
   'Approve', 'High',
   'Bid visible in HCI bid intelligence, eligible for leveling analysis.',
   'Low. Internal record only. No external notification.',
   NULL, 'bid_import',
   '{"vendor": "Pacific Concrete Inc", "division": "Concrete", "amount": 185000, "project_id": 2}'
  ),
  ('EXEC-004',
   'Upload 1355 Riverside Div 16 bid leveling to Drive',
   'Upload bid leveling Excel for 1355 Riverside Division 16 Electrical to Google Drive.',
   'Approve', 'High',
   'File accessible from Drive for team sharing.',
   'Low. Drive upload only. No external communications triggered.',
   NULL, 'drive_upload',
   '{"project_id": 3, "division": "16", "file_description": "Div 16 Electrical Bid Leveling"}'
  ),
  ('EXEC-005',
   'Commit 1355 Riverside daily log (2026-06-26)',
   'Write daily log entry for 1355 Riverside dated June 26 to HCI database.',
   'Approve', 'High',
   'Log becomes part of project intelligence.',
   'Low. Internal record. Idempotent.',
   NULL, 'db_write',
   '{"project_id": 3, "log_date": "2026-06-26", "approval_queue_id": 2}'
  )
ON CONFLICT (exec_id) DO NOTHING;

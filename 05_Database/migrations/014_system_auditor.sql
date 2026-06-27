-- Migration 014: Autonomous System Auditor
-- Phase 3 — nightly self-evaluation reports

CREATE TABLE IF NOT EXISTS system_audit_reports (
    id                      SERIAL PRIMARY KEY,
    audit_date              DATE NOT NULL DEFAULT CURRENT_DATE,
    overall_health_score    INTEGER,        -- 0-100
    overall_health_label    TEXT,           -- HEALTHY|NEEDS_ATTENTION|DEGRADED|CRITICAL
    api_health              JSONB,
    connector_health        JSONB,
    workflow_health         JSONB,
    test_coverage           JSONB,
    documentation_coverage  JSONB,
    technical_debt          JSONB,
    data_freshness          JSONB,
    security_review         JSONB,
    recommendations         JSONB,          -- [{priority, category, title, action, auto_fixable}, ...]
    next_milestones         JSONB,          -- [{priority, title, description, phase}, ...]
    auto_fixes_applied      JSONB,          -- [{fix, timestamp, result}, ...]
    elapsed_seconds         NUMERIC(6,1),
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (audit_date)
);

CREATE INDEX IF NOT EXISTS idx_audit_date ON system_audit_reports(audit_date DESC);
CREATE INDEX IF NOT EXISTS idx_audit_score ON system_audit_reports(overall_health_score);

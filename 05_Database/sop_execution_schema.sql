-- HCI AI — SOP Execution Layer Schema
-- Version: 1.0 | Date: 2026-06-25
-- Directive: HCI_AI_SOP_to_Software_Execution_Layer_Master_Directive_v1.0
--
-- Run after main schema.sql. All tables use the same postgres container.
-- Command: docker exec -i hci_postgres psql -U hci -d hci_brain < 05_Database/sop_execution_schema.sql

-- ──────────────────────────────────────────────────────────────────────────────
-- SOP INSTANCES
-- One record per SOP execution (e.g., SOP 11 for 101 Francis Concrete scope)
-- ──────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sop_instances (
    id                   SERIAL PRIMARY KEY,
    project_id           INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    sop_number           VARCHAR(5) NOT NULL,
    status               VARCHAR(30) NOT NULL DEFAULT 'Not Started',
    owner_name           VARCHAR(100) NOT NULL,
    owner_role           VARCHAR(50) NOT NULL,
    target_issue_date    DATE,
    bid_due_date         DATE,
    actual_issue_date    DATE,
    parent_instance_id   INTEGER REFERENCES sop_instances(id),
    status_changed_at    TIMESTAMPTZ,
    status_changed_by    VARCHAR(100),
    awarded_sub          VARCHAR(100),
    award_amount         NUMERIC(12,2),
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sop_instances_project    ON sop_instances(project_id);
CREATE INDEX IF NOT EXISTS idx_sop_instances_sop_number ON sop_instances(sop_number);
CREATE INDEX IF NOT EXISTS idx_sop_instances_status     ON sop_instances(status);

-- ──────────────────────────────────────────────────────────────────────────────
-- SOP INPUTS
-- Required source documents and field confirmations per SOP instance
-- ──────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sop_inputs (
    id                 SERIAL PRIMARY KEY,
    sop_instance_id    INTEGER NOT NULL REFERENCES sop_instances(id) ON DELETE CASCADE,
    input_key          VARCHAR(100) NOT NULL,
    input_label        VARCHAR(200),
    confirmed          BOOLEAN NOT NULL DEFAULT FALSE,
    confirmed_by       VARCHAR(100),
    confirmed_at       TIMESTAMPTZ,
    file_path          TEXT,
    notes              TEXT,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (sop_instance_id, input_key)
);

CREATE INDEX IF NOT EXISTS idx_sop_inputs_instance ON sop_inputs(sop_instance_id);

-- ──────────────────────────────────────────────────────────────────────────────
-- SOP OUTPUTS
-- Deliverables produced by each SOP instance (scope sections, leveling sheets, etc.)
-- ──────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sop_outputs (
    id                 SERIAL PRIMARY KEY,
    sop_instance_id    INTEGER NOT NULL REFERENCES sop_instances(id) ON DELETE CASCADE,
    output_type        VARCHAR(50) NOT NULL,
    output_label       VARCHAR(200) NOT NULL,
    content            JSONB,
    file_path          TEXT,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sop_outputs_instance ON sop_outputs(sop_instance_id);
CREATE INDEX IF NOT EXISTS idx_sop_outputs_type     ON sop_outputs(output_type);

-- ──────────────────────────────────────────────────────────────────────────────
-- SOP APPROVAL GATES
-- Approval events — one record per gate approval
-- ──────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sop_approval_gates (
    id                       SERIAL PRIMARY KEY,
    sop_instance_id          INTEGER NOT NULL REFERENCES sop_instances(id) ON DELETE CASCADE,
    gate_id                  VARCHAR(20) NOT NULL,
    gate_name                VARCHAR(200) NOT NULL,
    required_before_status   VARCHAR(30),
    approver_name            VARCHAR(100) NOT NULL,
    approver_role            VARCHAR(50),
    approved_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    method                   VARCHAR(30) DEFAULT 'in-system',
    conditions               TEXT,
    exception_flag           BOOLEAN DEFAULT FALSE,
    exception_id             INTEGER
);

CREATE INDEX IF NOT EXISTS idx_sop_approval_gates_instance ON sop_approval_gates(sop_instance_id);
CREATE INDEX IF NOT EXISTS idx_sop_approval_gates_gate     ON sop_approval_gates(gate_id);

-- ──────────────────────────────────────────────────────────────────────────────
-- SOP STOP EVENTS
-- All triggered stop conditions — resolved and unresolved
-- ──────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sop_stop_events (
    id                   SERIAL PRIMARY KEY,
    sop_instance_id      INTEGER NOT NULL REFERENCES sop_instances(id) ON DELETE CASCADE,
    condition_code       VARCHAR(10) NOT NULL,   -- SC-01 through SC-07
    blocker_description  TEXT NOT NULL,
    resolution_path      TEXT,
    triggered_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at          TIMESTAMPTZ,
    resolved_by          VARCHAR(100),
    exception_flag       BOOLEAN DEFAULT FALSE,
    exception_id         INTEGER
);

CREATE INDEX IF NOT EXISTS idx_sop_stop_events_instance ON sop_stop_events(sop_instance_id);
CREATE INDEX IF NOT EXISTS idx_sop_stop_events_code     ON sop_stop_events(condition_code);

-- ──────────────────────────────────────────────────────────────────────────────
-- SOP EXCEPTIONS
-- Documented bypass events — required when any gate or stop is bypassed
-- ──────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sop_exceptions (
    id                 SERIAL PRIMARY KEY,
    sop_instance_id    INTEGER REFERENCES sop_instances(id) ON DELETE SET NULL,
    project_id         INTEGER REFERENCES projects(id) ON DELETE SET NULL,
    gate_id            VARCHAR(20),
    exception_reason   TEXT NOT NULL,
    risk_accepted      TEXT NOT NULL,
    mitigation         TEXT NOT NULL,
    approver           VARCHAR(100) NOT NULL,
    approved_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at         TIMESTAMPTZ NOT NULL,
    created_by         VARCHAR(100) NOT NULL,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sop_exceptions_instance ON sop_exceptions(sop_instance_id);

-- ──────────────────────────────────────────────────────────────────────────────
-- SOP WORKFLOW EVENTS
-- Full audit log — every status change, input confirmation, and system event
-- ──────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sop_workflow_events (
    id                 SERIAL PRIMARY KEY,
    sop_instance_id    INTEGER NOT NULL REFERENCES sop_instances(id) ON DELETE CASCADE,
    event_type         VARCHAR(50) NOT NULL,
    event_value        TEXT,
    actor              VARCHAR(100),
    notes              TEXT,
    occurred_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sop_workflow_events_instance ON sop_workflow_events(sop_instance_id);
CREATE INDEX IF NOT EXISTS idx_sop_workflow_events_type     ON sop_workflow_events(event_type);

-- ──────────────────────────────────────────────────────────────────────────────
-- SOP KPI RECORDS
-- Cycle time, quality, and compliance metrics per SOP instance
-- ──────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sop_kpi_records (
    id                 SERIAL PRIMARY KEY,
    sop_instance_id    INTEGER NOT NULL REFERENCES sop_instances(id) ON DELETE CASCADE,
    project_id         INTEGER REFERENCES projects(id) ON DELETE SET NULL,
    kpi_code           VARCHAR(50) NOT NULL,
    value              NUMERIC(15,4) NOT NULL,
    unit               VARCHAR(20),
    recorded_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sop_kpi_records_instance ON sop_kpi_records(sop_instance_id);
CREATE INDEX IF NOT EXISTS idx_sop_kpi_records_code     ON sop_kpi_records(kpi_code);

-- ──────────────────────────────────────────────────────────────────────────────
-- DECISION RECORDS
-- Decision Intelligence — captures why decisions were made
-- ──────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS decision_records (
    id                  SERIAL PRIMARY KEY,
    project_id          INTEGER REFERENCES projects(id) ON DELETE SET NULL,
    decision_type       VARCHAR(20) NOT NULL,
    decision_date       DATE NOT NULL,
    decision_maker      VARCHAR(100) NOT NULL,
    approver            VARCHAR(100),
    context             TEXT NOT NULL,
    options_considered  JSONB,
    selected_option     TEXT NOT NULL,
    rationale           TEXT NOT NULL,
    risk_accepted       TEXT,
    cost_impact         NUMERIC(12,2),
    schedule_impact     INTEGER,
    related_rfi_ids     INTEGER[],
    related_co_ids      INTEGER[],
    related_bid_ids     INTEGER[],
    related_doc_ids     TEXT[],
    outcome             TEXT,
    outcome_rating      SMALLINT CHECK (outcome_rating BETWEEN 1 AND 5),
    lessons_learned     TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_decision_records_project ON decision_records(project_id);
CREATE INDEX IF NOT EXISTS idx_decision_records_type    ON decision_records(decision_type);
CREATE INDEX IF NOT EXISTS idx_decision_records_date    ON decision_records(decision_date);

-- ──────────────────────────────────────────────────────────────────────────────
-- KPI SNAPSHOTS
-- KPI Intelligence — point-in-time KPI values with threshold status
-- ──────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS kpi_snapshots (
    id              SERIAL PRIMARY KEY,
    kpi_code        VARCHAR(50) NOT NULL,
    scope           VARCHAR(10) NOT NULL CHECK (scope IN ('company', 'project')),
    project_id      INTEGER REFERENCES projects(id) ON DELETE SET NULL,
    value           NUMERIC(15,4) NOT NULL,
    unit            VARCHAR(20),
    period_start    DATE NOT NULL,
    period_end      DATE NOT NULL,
    status          VARCHAR(10) NOT NULL CHECK (status IN ('green', 'yellow', 'red', 'none')),
    threshold_low   NUMERIC(15,4),
    threshold_high  NUMERIC(15,4),
    source_service  VARCHAR(50),
    calculated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_kpi_snapshots_code    ON kpi_snapshots(kpi_code);
CREATE INDEX IF NOT EXISTS idx_kpi_snapshots_project ON kpi_snapshots(project_id);
CREATE INDEX IF NOT EXISTS idx_kpi_snapshots_date    ON kpi_snapshots(period_end);

-- ──────────────────────────────────────────────────────────────────────────────
-- OPERATING RULES
-- Configurable policy layer — thresholds, approval gates, escalation paths
-- ──────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS operating_rules (
    id              SERIAL PRIMARY KEY,
    rule_code       VARCHAR(50) UNIQUE NOT NULL,
    rule_name       VARCHAR(200) NOT NULL,
    rule_category   VARCHAR(30) NOT NULL,
    applies_to      VARCHAR(100) NOT NULL,
    condition_field VARCHAR(100) NOT NULL,
    condition_op    VARCHAR(10) NOT NULL,
    condition_value TEXT NOT NULL,
    action          VARCHAR(30) NOT NULL,
    action_target   TEXT,
    authority       VARCHAR(100),
    active          BOOLEAN NOT NULL DEFAULT TRUE,
    effective_date  DATE NOT NULL DEFAULT CURRENT_DATE,
    modified_by     VARCHAR(100),
    change_reason   TEXT,
    previous_value  JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_operating_rules_category   ON operating_rules(rule_category);
CREATE INDEX IF NOT EXISTS idx_operating_rules_applies_to ON operating_rules(applies_to);
CREATE INDEX IF NOT EXISTS idx_operating_rules_active     ON operating_rules(active);

-- Operating rule exceptions
CREATE TABLE IF NOT EXISTS operating_rule_exceptions (
    id              SERIAL PRIMARY KEY,
    rule_code       VARCHAR(50) REFERENCES operating_rules(rule_code),
    sop_instance_id INTEGER REFERENCES sop_instances(id) ON DELETE SET NULL,
    project_id      INTEGER REFERENCES projects(id) ON DELETE SET NULL,
    exception_reason TEXT NOT NULL,
    risk_accepted   TEXT NOT NULL,
    mitigation      TEXT NOT NULL,
    approver        VARCHAR(100) NOT NULL,
    approved_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at      TIMESTAMPTZ NOT NULL,
    created_by      VARCHAR(100) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ──────────────────────────────────────────────────────────────────────────────
-- BUSINESS PROCESSES
-- Process Library — connects SOPs, workflows, data, KPIs, and approval gates
-- ──────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS business_processes (
    id                  SERIAL PRIMARY KEY,
    process_code        VARCHAR(50) UNIQUE NOT NULL,
    process_name        VARCHAR(200) NOT NULL,
    phase               VARCHAR(50) NOT NULL,
    description         TEXT NOT NULL,
    trigger_event       TEXT NOT NULL,
    required_inputs     JSONB,
    required_outputs    JSONB,
    related_sop_ids     TEXT[],
    related_workflows   TEXT[],
    primary_table       TEXT,
    related_tables      TEXT[],
    kpi_codes           TEXT[],
    approval_gate_ids   TEXT[],
    owner_role          VARCHAR(100),
    reviewer_role       VARCHAR(100),
    approver_role       VARCHAR(100),
    maturity_level      SMALLINT CHECK (maturity_level BETWEEN 0 AND 4) DEFAULT 0,
    active              BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ──────────────────────────────────────────────────────────────────────────────
-- SEED OPERATING RULES
-- ──────────────────────────────────────────────────────────────────────────────
INSERT INTO operating_rules
    (rule_code, rule_name, rule_category, applies_to, condition_field,
     condition_op, condition_value, action, action_target, authority)
VALUES
    ('BUDGET_VAR_YELLOW', 'Budget Variance Yellow Alert', 'kpi_alert',
     'all_projects', 'budget_variance_pct', '>', '5', 'alert', 'PM', 'PM'),
    ('BUDGET_VAR_RED', 'Budget Variance Red Alert', 'kpi_alert',
     'all_projects', 'budget_variance_pct', '>', '10', 'escalate', 'PM,Buck', 'Buck'),
    ('CO_BUCK_APPROVAL', 'Change Order Buck Approval Required', 'approval',
     'change_orders', 'co_total', '>=', '25000', 'block', 'Buck', 'Buck'),
    ('MIN_BIDDERS', 'Minimum Responsive Bidders', 'minimum_standard',
     'sop_15', 'responsive_bid_count', '<', '3', 'block', 'PM,Buck', 'Buck'),
    ('RFI_ESCALATE_5D', 'RFI No Response at 5 Days', 'escalation',
     'rfis', 'days_open', '>', '5', 'alert', 'PM', 'PM'),
    ('RFI_ESCALATE_10D', 'RFI No Response at 10 Days', 'escalation',
     'rfis', 'days_open', '>', '10', 'escalate', 'PM,Buck', 'Buck'),
    ('SUB_COI_GATE', 'Sub Mobilization Without COI', 'compliance_gate',
     'all_projects', 'coi_on_file', '==', 'false', 'block', 'PM,Buck', 'Buck'),
    ('SCHED_YELLOW', 'Schedule Variance Yellow', 'kpi_alert',
     'all_projects', 'schedule_variance_days', '>', '3', 'alert', 'PM', 'PM'),
    ('SCHED_RED', 'Schedule Variance Red', 'kpi_alert',
     'all_projects', 'schedule_variance_days', '>', '7', 'escalate', 'PM,Buck', 'Buck'),
    ('BID_MARGIN_MIN', 'Bid Margin Below Target', 'minimum_standard',
     'bid_intelligence', 'bid_margin_pct', '<', '8', 'alert', 'Buck', 'Buck'),
    ('SOP11_ISSUE_GATE', 'Bid Package Issue Requires Buck', 'approval',
     'sop_11', 'gate_11c_approved', '==', 'false', 'block', 'Buck', 'Buck'),
    ('SOP15_AWARD_GATE', 'Award Decision Requires Buck', 'approval',
     'sop_15', 'gate_15c_approved', '==', 'false', 'block', 'Buck', 'Buck')
ON CONFLICT (rule_code) DO NOTHING;

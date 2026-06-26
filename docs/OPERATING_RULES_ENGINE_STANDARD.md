# HCI AI — Operating Rules Engine Standard

**Version:** 1.0 | **Date:** 2026-06-25 | **Directive:** HCI_AI_Business_Operating_Layer_BOOK01_Decision_KPI_Master_Directive_v1.0

---

## Purpose

This document defines the data model, rule structure, evaluation contract, and API for the Operating Rules Engine. All configurable policies, thresholds, approval requirements, escalation paths, and stop conditions are stored here — not hardcoded in service logic.

---

## Core Data Model

### PostgreSQL Table: `operating_rules`

```sql
CREATE TABLE operating_rules (
    id              SERIAL PRIMARY KEY,
    rule_code       VARCHAR(50) UNIQUE NOT NULL,
    rule_name       VARCHAR(200) NOT NULL,
    rule_category   VARCHAR(30) NOT NULL,
    applies_to      VARCHAR(100) NOT NULL,   -- 'all', 'sop_11', 'wf_change', etc.
    condition_field VARCHAR(100) NOT NULL,   -- field name being evaluated
    condition_op    VARCHAR(10) NOT NULL,    -- '>', '<', '>=', '<=', '==', '!='
    condition_value TEXT NOT NULL,           -- value to compare against
    action          VARCHAR(30) NOT NULL,    -- 'block', 'alert', 'escalate', 'require_input'
    action_target   TEXT,                    -- who/what receives the action
    authority       VARCHAR(100),            -- who can approve an exception
    active          BOOLEAN DEFAULT TRUE,
    effective_date  DATE DEFAULT CURRENT_DATE,
    modified_by     VARCHAR(100),
    change_reason   TEXT,
    previous_value  JSONB,                   -- stores prior rule state for audit
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_operating_rules_category ON operating_rules(rule_category);
CREATE INDEX idx_operating_rules_applies_to ON operating_rules(applies_to);
CREATE INDEX idx_operating_rules_active ON operating_rules(active);
```

---

## Rule Categories

| Category | What It Controls |
|----------|-----------------|
| `approval` | Who must approve before a status advances or action is taken |
| `kpi_alert` | KPI threshold values and notification behavior |
| `escalation` | Time-based escalation rules (e.g., RFI > 10 days) |
| `stop_condition` | Conditions that halt workflow progress |
| `minimum_standard` | Minimum requirements (bidder count, document completeness) |
| `compliance_gate` | Compliance pre-conditions (COI, W-9, license) |
| `communication` | Who must review before communication is sent |
| `exception` | What evidence is required for any bypass |

---

## Seed Rules (Initial Configuration)

```sql
-- Budget variance alerts
INSERT INTO operating_rules (rule_code, rule_name, rule_category, applies_to, condition_field, condition_op, condition_value, action, action_target, authority)
VALUES 
('BUDGET_VAR_YELLOW', 'Budget Variance Yellow Alert', 'kpi_alert', 'all_projects', 'budget_variance_pct', '>', '5', 'alert', 'PM', 'PM'),
('BUDGET_VAR_RED', 'Budget Variance Red Alert', 'kpi_alert', 'all_projects', 'budget_variance_pct', '>', '10', 'escalate', 'PM,Buck', 'Buck'),

-- Change order approval thresholds
('CO_PM_APPROVAL', 'Change Order PM Approval', 'approval', 'change_orders', 'co_total', '<', '5000', 'alert', 'PM', 'PM'),
('CO_BUCK_APPROVAL', 'Change Order Buck Approval', 'approval', 'change_orders', 'co_total', '>=', '25000', 'block', 'Buck', 'Buck'),

-- Minimum bidders
('MIN_BIDDERS', 'Minimum Responsive Bidders', 'minimum_standard', 'sop_15', 'responsive_bid_count', '<', '3', 'block', 'PM,Buck', 'Buck'),

-- RFI escalation
('RFI_ESCALATE_5D', 'RFI No Response at 5 Days', 'escalation', 'rfis', 'days_open', '>', '5', 'alert', 'PM', 'PM'),
('RFI_ESCALATE_10D', 'RFI No Response at 10 Days', 'escalation', 'rfis', 'days_open', '>', '10', 'escalate', 'PM,Buck', 'Buck'),

-- Sub compliance
('SUB_COI_GATE', 'Sub Mobilization Without COI', 'compliance_gate', 'all_projects', 'coi_on_file', '==', 'false', 'block', 'PM,Buck', 'Buck'),

-- Schedule alerts
('SCHED_YELLOW', 'Schedule Variance Yellow', 'kpi_alert', 'all_projects', 'schedule_variance_days', '>', '3', 'alert', 'PM', 'PM'),
('SCHED_RED', 'Schedule Variance Red', 'kpi_alert', 'all_projects', 'schedule_variance_days', '>', '7', 'escalate', 'PM,Buck', 'Buck'),

-- Bid margin
('BID_MARGIN_MIN', 'Bid Margin Below Target', 'minimum_standard', 'bid_intelligence', 'bid_margin_pct', '<', '8', 'alert', 'Buck', 'Buck'),

-- SOP approval gates
('SOP11_ISSUE_GATE', 'Bid Package Issue Requires Buck', 'approval', 'sop_11', 'gate_11c_approved', '==', 'false', 'block', 'Buck', 'Buck'),
('SOP15_AWARD_GATE', 'Award Decision Requires Buck', 'approval', 'sop_15', 'gate_15c_approved', '==', 'false', 'block', 'Buck', 'Buck');
```

---

## Rule Evaluation

Every SOP service and workflow calls the rules engine before advancing status:

```python
# Example call from sop_11_service.py
from services.operating_rules import evaluate_rule

result = evaluate_rule(
    context="sop_11",
    field="gate_11c_approved",
    value=False
)
if result.action == "block":
    raise WorkflowBlockedError(result.rule_name, result.action_target)
```

The evaluation returns:
```python
@dataclass
class RuleEvalResult:
    matched: bool
    rule_code: str
    rule_name: str
    action: str        # 'block', 'alert', 'escalate', 'require_input', 'pass'
    action_target: str
    authority: str
    message: str
```

---

## Exception Records

When a rule must be bypassed:

```sql
CREATE TABLE operating_rule_exceptions (
    id              SERIAL PRIMARY KEY,
    rule_code       VARCHAR(50) REFERENCES operating_rules(rule_code),
    sop_instance_id INTEGER,
    project_id      INTEGER REFERENCES projects(id),
    exception_reason TEXT NOT NULL,
    risk_accepted   TEXT NOT NULL,
    mitigation      TEXT NOT NULL,
    approver        VARCHAR(100) NOT NULL,
    approved_at     TIMESTAMPTZ NOT NULL,
    expires_at      TIMESTAMPTZ NOT NULL,     -- no permanent exceptions
    created_by      VARCHAR(100) NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

**No exception is permanent.** Every exception requires an expiration date. Expired exceptions are flagged for renewal or permanent rule update.

---

## API Contract

### `GET /api/v1/operating_rules`
List all active rules, grouped by category.

### `GET /api/v1/operating_rules/{rule_code}`
Get a specific rule with full audit history.

### `POST /api/v1/operating_rules/evaluate`
Evaluate rules for a given context.

```json
{
  "context": "sop_11",
  "field": "gate_11c_approved",
  "value": false,
  "project_id": 2
}
```

### `PATCH /api/v1/operating_rules/{rule_code}`
Update a rule. Change is logged with modifier, reason, and prior state.

```json
{
  "condition_value": "30000",
  "change_reason": "Adjusted CO threshold based on project size increase",
  "modified_by": "Buck Adams"
}
```

### `POST /api/v1/operating_rules/exception`
Create an exception record for a bypassed rule.

---

*Service: `03_Source_Code/services/operating_rules/`*  
*BOOK_01 Volume 14: `BOOK_01/14_OPERATING_RULES_ENGINE.md`*  
*Database: `05_Database/sop_execution_schema.sql`*

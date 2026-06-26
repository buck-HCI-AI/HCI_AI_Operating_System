# BOOK_01 — Volume 14: Operating Rules Engine

**Version:** 1.0 | **Date:** 2026-06-25 | **Directive:** HCI_AI_Business_Operating_Layer_BOOK01_Decision_KPI_Master_Directive_v1.0

---

## What the Operating Rules Engine Is

The Operating Rules Engine is the configurable policy layer that governs how HCI AI enforces thresholds, approvals, escalations, and stop conditions. Rules are not hardcoded in the software — they are stored as configurable data so that Buck can change them without a code change.

**Without an Operating Rules Engine:** When HCI's approval threshold changes, a developer must change code. Thresholds are buried in service logic. A rule that applies to one workflow doesn't automatically apply to the next one.

**With an Operating Rules Engine:** All rules are in one place. Buck (or PM with Buck approval) can adjust a threshold, and every workflow that uses that threshold is updated immediately. Audit trail shows when a rule was changed and by whom.

---

## What Rules Control

| Rule Category | Examples |
|--------------|---------|
| Approval thresholds | Change orders > $25K require Buck approval |
| KPI alert thresholds | Budget variance > 10% triggers red alert |
| Escalation rules | RFI > 10 days without response escalates to PM + Buck |
| Stop conditions | Bid package cannot issue if < 3 required scope sections present |
| Minimum bidder rules | < 3 responsive bids before award requires Buck exception |
| Compliance gates | Sub cannot start without COI on file |
| SOP gate rules | Approved status cannot set without named approver |
| Communication rules | Client-facing communication requires PM review |
| Exception rules | What evidence is required for any bypass |

---

## Rule Structure

Every rule in the engine has these fields:

| Field | Description |
|-------|-------------|
| `rule_id` | Unique identifier |
| `rule_name` | Descriptive name (no ambiguity) |
| `rule_category` | Approval / KPI / Escalation / Stop / Minimum / Compliance / Exception |
| `applies_to` | Which workflow, SOP, service, or global |
| `condition` | What triggers the rule (field, operator, value) |
| `action` | What happens when triggered: block / alert / escalate / require_input |
| `authority` | Who can approve an exception to this rule |
| `active` | True/false |
| `effective_date` | When this version of the rule took effect |
| `modified_by` | Who last changed it |
| `change_reason` | Why it was changed |

---

## Rule Examples

**Rule: Budget Variance Red Alert**
```
rule_name: Budget Variance - Red Alert
applies_to: All projects
condition: budget_variance_pct > 10 (any scope line)
action: escalate → PM and Buck; block draw request until review
authority: Buck (to accept or require corrective action)
```

**Rule: Change Order Approval Gate**
```
rule_name: Change Order - Buck Approval Required
applies_to: WF-CHANGE, SOP 31
condition: change_order_total > 25000
action: block submission until Buck approval logged
authority: Buck
```

**Rule: Minimum Bidders Before Award**
```
rule_name: Minimum Responsive Bidders
applies_to: SOP 15 Bid Leveling
condition: responsive_bid_count < 3
action: block SOP 15 Approved status; require Buck exception
authority: Buck (exception record required)
```

**Rule: Sub Start Without COI**
```
rule_name: Compliance - Sub Mobilization Gate
applies_to: All projects, all subs
condition: sub_mobilization_date present AND coi_on_file = false
action: block NTP; notify PM and Buck; require COI before proceeding
authority: Buck (waiver with documentation)
```

---

## How Rules Are Updated

Rules are not changed in code. They are updated in the operating_rules service via:
- `PATCH /api/v1/operating_rules/{rule_id}` — update a rule's condition, action, or active state
- All changes are audit-logged: who, when, what was changed, what it was before

**Who can change rules:** Buck, or PM with Buck's explicit authorization.

**No rules change silently.** Every change is visible in the audit log and the weekly executive report includes a "Rules Changed This Week" section if any rule was modified.

---

## Exceptions to Rules

When a rule is triggered but business context requires an exception:

1. Exception record is created (cannot be skipped)
2. Exception includes: rule bypassed, reason, risk, mitigation, approver, expiration date
3. Exception is logged in `sop_exceptions` table
4. Exception is reported in the next executive summary

No exception is silent. No exception is permanent — every exception has an expiration date.

---

## Operating Rules Service

Service path: `03_Source_Code/services/operating_rules/`

- `GET /api/v1/operating_rules` — list all active rules
- `GET /api/v1/operating_rules/{id}` — get specific rule and history
- `POST /api/v1/operating_rules/evaluate` — evaluate a rule for a given context
- `PATCH /api/v1/operating_rules/{id}` — update rule (logged)
- `POST /api/v1/operating_rules/exception` — create an exception record

---

*Standard: `docs/OPERATING_RULES_ENGINE_STANDARD.md`*  
*Service: `03_Source_Code/services/operating_rules/`*  
*Exceptions table: `sop_exceptions` in PostgreSQL*

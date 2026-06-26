# HCI AI — SOP Data Field Dictionary

**Version:** 1.0 | **Date:** 2026-06-25 | **Directive:** HCI_AI_SOP_to_Software_Execution_Layer_Master_Directive_v1.0

This dictionary defines all data fields for pilot SOPs 11 and 15. Every field has a type, source, validation rule, and required/optional designation.

---

## SOP 11 — Bid Package Fields

### Instance-Level Fields

| Field | Type | Source | Validation | Required |
|-------|------|--------|------------|---------|
| `sop_instance_id` | UUID | System | Auto | Yes |
| `project_id` | INTEGER | User | FK → projects.id | Yes |
| `sop_number` | VARCHAR(5) | System | Always "11" | Yes |
| `status` | VARCHAR(30) | System | Must be in 15-status list | Yes |
| `owner_name` | VARCHAR(100) | User | Not null | Yes |
| `owner_role` | VARCHAR(50) | User | estimator / pm | Yes |
| `created_at` | TIMESTAMPTZ | System | Auto | Yes |
| `target_issue_date` | DATE | User | Must be future date | Yes |
| `actual_issue_date` | DATE | System | Set at Issued status | No |
| `bid_due_date` | DATE | User | Must be after issue_date | Yes |

### Input Fields (from sop_inputs table, SOP 11)

| Field / Input | Input Type | Owner | Fail Action |
|---------------|-----------|-------|------------|
| Architectural drawings (current revision) | Document | PM | SC-01 triggered |
| Structural drawings | Document | PM | SC-01 if applicable |
| MEP drawings | Document | PM | SC-01 if applicable |
| Project specifications — all applicable divisions | Document | PM | SC-01 triggered |
| Geotechnical / soils report | Document | PM | SC-01 if applicable |
| Hazmat assessment | Document | PM | SC-01 if applicable |
| SOP 04 (Plan Review) — Approved status | Status check | System | SC-01 triggered |
| SOP 05 (Construction Narrative) — Complete | Status check | System | SC-01 triggered |
| SOP 06 (Risk Log) — Reviewed | Status check | System | SC-01 triggered |
| SOP 10 (Allowances/Alternates) — Defined | Status check | System | SC-01 triggered |
| SOP 09 (Budget) — Approved | Status check | System | SC-01 triggered |
| Project type | VARCHAR | PM | Enum: commercial / residential / multi-family / industrial / renovation |
| Bid form required | BOOLEAN | PM | Default false |
| Prevailing wage required | BOOLEAN | PM | Default false |
| Bond required | BOOLEAN | PM | Default false |

### Output Fields (from sop_outputs table, SOP 11)

| Output | Type | Stored In | Required |
|--------|------|-----------|---------|
| Bid package document | PDF | MinIO | Yes |
| Scope sections (by trade) | JSONB array | PostgreSQL | Yes |
| Scope gap report | TEXT | PostgreSQL | Yes |
| Risk flags identified | JSONB array | PostgreSQL | Yes |
| Sub invite list | JSONB array | PostgreSQL | Yes |
| Bid form (if required) | PDF | MinIO | Conditional |
| Contract documents list | TEXT[] | PostgreSQL | Yes |
| Addendum log | JSONB array | PostgreSQL | Yes — starts empty |

### Scope Section Fields (per trade)

| Field | Type | Notes |
|-------|------|-------|
| trade_code | VARCHAR(10) | CSI division or custom code |
| trade_name | VARCHAR(100) | Descriptive name |
| scope_text | TEXT | Full scope description |
| drawing_refs | TEXT[] | Drawing numbers referenced |
| spec_refs | TEXT[] | Spec section numbers referenced |
| allowances | JSONB | [{item, amount, basis}] |
| alternates | JSONB | [{item, description, bid_form_line}] |
| exclusions | TEXT[] | Explicit exclusions |
| bid_bond_required | BOOLEAN | Default false |
| ai_gap_flags | JSONB | AI-identified gaps: [{flag, severity, note}] |

---

## SOP 15 — Bid Leveling Fields

### Instance-Level Fields

| Field | Type | Source | Validation | Required |
|-------|------|--------|------------|---------|
| `sop_instance_id` | UUID | System | Auto | Yes |
| `project_id` | INTEGER | User | FK → projects.id | Yes |
| `sop_11_instance_id` | UUID | System | FK → parent SOP 11 | Yes |
| `sop_number` | VARCHAR(5) | System | Always "15" | Yes |
| `status` | VARCHAR(30) | System | 15-status list | Yes |
| `trade_code` | VARCHAR(10) | System | From SOP 11 scope sections | Yes |
| `trade_name` | VARCHAR(100) | System | From SOP 11 | Yes |
| `bid_close_date` | DATE | System | From SOP 11 bid_due_date | Yes |
| `owner_name` | VARCHAR(100) | User | Estimator who does leveling | Yes |
| `recommended_sub` | VARCHAR(100) | User | After leveling complete | No |
| `awarded_sub` | VARCHAR(100) | User | After Buck approves | No |
| `award_amount` | NUMERIC(12,2) | User | After Buck approves | No |

### Bid Record Fields (per bidder, from sop_inputs)

| Field | Type | Source | Notes |
|-------|------|--------|-------|
| `bidder_name` | VARCHAR(100) | Estimator | Vendor name |
| `bidder_id` | INTEGER | System | FK → vendor_intelligence |
| `bid_amount_base` | NUMERIC(12,2) | Estimator | Base bid only |
| `bid_amount_total` | NUMERIC(12,2) | System | Calculated after adjustments |
| `bid_received_date` | DATE | Estimator | Date bid was received |
| `bid_responsive` | BOOLEAN | Estimator | Meets minimum requirements |
| `qualifications_raw` | TEXT | Estimator | Full text of sub's qualifications |
| `qualifications_parsed` | JSONB | AI | Parsed qualifications by category |
| `alternates_included` | JSONB | Estimator | Alternates sub included |
| `alternates_excluded` | JSONB | AI-extracted | Alternates sub excluded |
| `exclusions_list` | TEXT[] | AI-extracted | Items sub explicitly excluded |
| `scope_inclusions` | TEXT[] | AI-extracted | Items sub explicitly included beyond base |
| `adjustment_items` | JSONB | Estimator | [{item, description, amount}] |
| `adjusted_amount` | NUMERIC(12,2) | System | bid_amount_base ± adjustments |
| `risk_flags` | JSONB | AI | [{class, description, impact}] |
| `contract_qualifications` | TEXT[] | AI-extracted | Contract term exceptions sub noted |
| `schedule_exceptions` | TEXT[] | AI-extracted | Schedule qualifications |
| `prior_performance_score` | NUMERIC(3,1) | Vendor Intelligence | 1.0 - 5.0 |
| `recommendation_flag` | VARCHAR(20) | AI | recommended / caution / reject |
| `recommendation_reason` | TEXT | AI | Rationale for flag |

### Leveling Output Fields (from sop_outputs)

| Output | Type | Stored In | Required |
|--------|------|-----------|---------|
| Leveling sheet (all bidders, normalized) | PDF | MinIO | Yes |
| Leveling data record | JSONB | PostgreSQL | Yes |
| Risk flag summary by bidder | JSONB | PostgreSQL | Yes |
| Award recommendation (AI) | TEXT | PostgreSQL | Yes |
| Buck's award decision record | JSONB | PostgreSQL | Yes — at Gate 15-C |
| Award memo | PDF | MinIO | After Buck approves |

---

*Standard: `docs/SOP_2_0_CONVERSION_STANDARD.md`*  
*Database schema: `05_Database/sop_execution_schema.sql`*  
*Templates: `docs/SOP_TEMPLATE_BACKLOG.md`*

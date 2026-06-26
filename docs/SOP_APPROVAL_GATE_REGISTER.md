# HCI AI — SOP Approval Gate Register

**Version:** 1.0 | **Date:** 2026-06-25 | **Directive:** HCI_AI_SOP_to_Software_Execution_Layer_Master_Directive_v1.0

This register lists every approval gate across all converted SOPs. Each gate defines who must approve, what evidence is required, and what is blocked until approval is granted.

---

## Approval Gate Rules (Universal)

1. The workflow owner may not self-approve when independent review is required
2. AI may draft the deliverable but may never approve it
3. Any gate bypass requires an exception record (see `sop_exceptions` table)
4. Approval authority is configured in the Operating Rules Engine — not hardcoded
5. Every approval is logged with: approver name, timestamp, method (in-system or acknowledged), any conditions

---

## SOP 11 — Bid Package Approval Gates

### Gate 11-A: Input Confirmation Gate

| Field | Value |
|-------|-------|
| Gate ID | AG-11-A |
| Description | All source documents present before bid package work begins |
| Required Before | Status → In Progress |
| What Must Be True | All items on SOP 11 input checklist = confirmed |
| Approver | PM (confirms inputs are complete) |
| Evidence Required | Completed input checklist in `sop_inputs` table |
| If Blocked | Status remains Inputs Missing; PM notified of specific blockers |

**Required inputs for SOP 11:**
- [ ] Architectural drawings (current revision)
- [ ] Structural drawings (if applicable)
- [ ] MEP drawings (if applicable)
- [ ] Project specifications (all divisions applicable)
- [ ] Soils report (if applicable)
- [ ] Hazmat report (if applicable)
- [ ] Plan review (SOP 04) marked Complete
- [ ] Construction narrative (SOP 05) complete
- [ ] Risk log (SOP 06) reviewed
- [ ] Allowances/alternates/exclusions (SOP 10) defined
- [ ] Project budget (SOP 09) approved

### Gate 11-B: Scope Review Gate

| Field | Value |
|-------|-------|
| Gate ID | AG-11-B |
| Description | PM confirms scope sections are complete and correct before internal review |
| Required Before | Status → Approval Required |
| What Must Be True | All required scope sections present; AI gap check complete; no open risk flags |
| Approver | PM |
| Evidence Required | PM review record in `sop_approval_gates`; all scope sections marked reviewed |
| If Blocked | PM issues Revision Required; specific gaps noted |

### Gate 11-C: Issue Authority Gate

| Field | Value |
|-------|-------|
| Gate ID | AG-11-C |
| Description | Buck authorizes bid package issue |
| Required Before | Status → Issued / Completed (cannot issue without this) |
| What Must Be True | Gate 11-B complete; all scope sections confirmed; risk log clear or risk accepted |
| Approver | Buck |
| Evidence Required | Buck approval record with timestamp in `sop_approval_gates` |
| If Blocked | Bid package cannot be sent to any sub until Buck approves |
| Exception | Documented exception with risk, reason, Buck sign-off — even if Buck issues verbally, PM logs same day |

---

## SOP 15 — Bid Leveling Approval Gates

### Gate 15-A: Bid Receipt Gate

| Field | Value |
|-------|-------|
| Gate ID | AG-15-A |
| Description | Minimum bidder requirement confirmed before leveling begins |
| Required Before | Status → In Progress |
| What Must Be True | ≥ 3 responsive bids received (configurable in Operating Rules Engine) |
| Approver | PM confirms responsiveness; Buck authorizes exception if < 3 |
| Evidence Required | Bid receipt log in `sop_inputs`; all bids confirmed responsive |
| If Blocked | Status = Inputs Missing; PM conducts follow-up (SOP 14); Buck decides if fewer than 3 are acceptable |

### Gate 15-B: Leveling Review Gate

| Field | Value |
|-------|-------|
| Gate ID | AG-15-B |
| Description | PM confirms leveling sheet is complete and all qualifications reviewed |
| Required Before | Status → Approval Required |
| What Must Be True | All bids normalized to same scope; all qualifications reviewed; risk flags addressed or accepted |
| Approver | PM (and Estimator if different) |
| Evidence Required | PM review record; all risk flag dispositions logged |
| If Blocked | Return to In Progress; specific items to address noted |

### Gate 15-C: Award Authority Gate

| Field | Value |
|-------|-------|
| Gate ID | AG-15-C |
| Description | Buck authorizes award to specific subcontractor |
| Required Before | Status → Approved (Award); award memo can be issued |
| What Must Be True | Gate 15-B complete; leveling sheet with all-in cost comparison present; AI recommendation reviewed |
| Approver | Buck (only Buck can award) |
| Evidence Required | Buck award decision record: sub name, scope, price, basis of decision |
| If Blocked | No sub is notified of award until Buck's record is in the system |
| Exception | None — all awards require Buck approval. No exception permitted. |

---

## Gate Audit Requirements

Every approval gate event is logged to `sop_approval_gates`:

```sql
sop_approval_gates:
  id, sop_instance_id, gate_id, gate_name,
  required_before_status, approver_name, approver_role,
  approved_at, method (in_system / acknowledged / verbal_logged),
  conditions, exception_flag, exception_id
```

**Reporting:** Approval gate completion rate by SOP type and approver — tracked in KPI intelligence.

---

*Standard: `docs/SOP_2_0_CONVERSION_STANDARD.md`*  
*Rules engine: `docs/OPERATING_RULES_ENGINE_STANDARD.md`*  
*Database: `05_Database/sop_execution_schema.sql`*

# HCI AI — SOP Stop Condition Register

**Version:** 1.0 | **Date:** 2026-06-25 | **Directive:** HCI_AI_SOP_to_Software_Execution_Layer_Master_Directive_v1.0

Stop conditions are system-enforced halts. They are not warnings — they block forward progress until the condition is resolved or an exception is formally documented.

---

## Universal Stop Conditions

All 7 universal stop conditions apply to every SOP. They are implemented in `shared/stop_condition.py` and called by every SOP service.

---

### SC-01: Required Inputs Missing or Outdated

| Field | Value |
|-------|-------|
| Stop Condition ID | SC-01 |
| Trigger | At workflow start and at each validation checkpoint: required input field is null, file is missing, or revision date is older than the allowed staleness threshold |
| Block Applied | Status cannot advance past Inputs Missing |
| Required Response | Return structured Inputs Missing report listing each blocker with owner and resolution path |
| Unblocking Condition | All required inputs confirmed; PM re-triggers input validation |
| SOP 11 application | Cannot begin scope assembly without all drawings, specs, and prior SOPs complete |
| SOP 15 application | Cannot begin leveling without all bids received; cannot use drawings not marked current |

### SC-02: Output Depends on Unapproved Assumption

| Field | Value |
|-------|-------|
| Stop Condition ID | SC-02 |
| Trigger | AI or estimator identifies a scope or cost assumption that is not supported by a confirmed source document |
| Block Applied | Status cannot advance from In Progress to AI Drafted or Internal Review |
| Required Response | Assumption is flagged with risk classification; owner must confirm or resolve assumption before proceeding |
| Unblocking Condition | Assumption confirmed by documented source OR converted to a scope exclusion OR scope RFI submitted |
| SOP 11 application | Scope section cannot be issued if it rests on a drawing clarification that has not been received |
| SOP 15 application | Cannot produce all-in cost if any bid includes an unreviewed assumption about scope inclusion |

### SC-03: Scope, Pricing, Schedule, or Contract Risk Unclear

| Field | Value |
|-------|-------|
| Stop Condition ID | SC-03 |
| Trigger | Risk flag identified by AI or human that is classified as Scope / Cost / Schedule / Contract / Coverage / Document Control and is not yet dispositioned |
| Block Applied | Status cannot advance to Approval Required |
| Required Response | Risk flag must be dispositioned: Accepted (with reason) / Resolved (with evidence) / Escalated (to named person) |
| Unblocking Condition | All open risk flags dispositioned by PM; record updated |
| SOP 11 application | Scope gaps and document control risks must be dispositioned before bid package approval |
| SOP 15 application | All bid qualifications and coverage risks must be dispositioned before award recommendation |

### SC-04: External Commitment Without Required Approval

| Field | Value |
|-------|-------|
| Stop Condition ID | SC-04 |
| Trigger | Workflow would issue, send, or communicate something that creates an external commitment (bid package to sub, award to sub, CO to owner) without required approver sign-off |
| Block Applied | Issued / Completed status cannot be set; external communication is blocked |
| Required Response | Route to required approver; do not issue or send until approval record exists |
| Unblocking Condition | Approval gate record created with approver name and timestamp |
| SOP 11 application | Bid package cannot be issued to subs without Gate 11-C (Buck) |
| SOP 15 application | Award cannot be communicated to sub without Gate 15-C (Buck) |

### SC-05: Reviewer Marked Work Revision Required

| Field | Value |
|-------|-------|
| Stop Condition ID | SC-05 |
| Trigger | Reviewer sets status to Revision Required |
| Block Applied | Approval gate is blocked until revision is complete; reviewer comments are attached and visible to owner |
| Required Response | Owner corrects the specific items noted; resubmits for Internal Review |
| Unblocking Condition | Owner sets status back to Internal Review after corrections; reviewer re-reviews |

### SC-06: Approval Gate Bypass Attempted

| Field | Value |
|-------|-------|
| Stop Condition ID | SC-06 |
| Trigger | User attempts to advance a status that requires an approval gate without a gate record present |
| Block Applied | Status change is rejected; bypass attempt logged |
| Required Response | Either the required approver submits their approval, or an exception record is created with required fields |
| Unblocking Condition | Valid approval gate record OR valid exception record with all required fields |
| Logging | Bypass attempt is logged in `sop_workflow_events` with user, timestamp, attempted action |

### SC-07: Handoff Destination Missing

| Field | Value |
|-------|-------|
| Stop Condition ID | SC-07 |
| Trigger | Workflow attempts to advance to Issued/Completed or Handed Off status but no handoff recipient is named |
| Block Applied | Issued and Handed Off statuses cannot be set |
| Required Response | PM names the next SOP owner and confirms they have been notified |
| Unblocking Condition | Handoff record created with recipient name, contact, and confirmation method |
| SOP 11 application | Bid package issue must name who it is being sent to (bid list) |
| SOP 15 application | Leveling handoff to SOP 16 must name who receives the award memo |

---

## Stop Condition Logging

Every stop condition triggered is logged to `sop_stop_events`:

```sql
sop_stop_events:
  id, sop_instance_id, condition_code (SC-01 through SC-07),
  triggered_at, triggered_by (user or system),
  blocker_description, resolution_path, resolved_at, resolved_by,
  exception_flag (bool), exception_id
```

---

## Stop Condition KPIs

| KPI | Target |
|-----|--------|
| SC-01 stops resolved within 2 business days | > 80% |
| SC-02 assumption flags resolved before submission | 100% |
| SC-04 bypass attempts (should be 0) | 0 |
| SC-06 bypass attempts (should be 0) | 0 |
| SC-05 revisions completing within 3 days | > 80% |

---

*Implementation: `03_Source_Code/services/sop_execution/shared/stop_condition.py`*  
*Standard: `docs/SOP_2_0_CONVERSION_STANDARD.md`*  
*Database: `05_Database/sop_execution_schema.sql`*

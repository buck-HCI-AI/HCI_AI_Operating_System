# HCI AI — SOP Test Matrix

**Version:** 1.0 | **Date:** 2026-06-25 | **Directive:** HCI_AI_SOP_to_Software_Execution_Layer_Master_Directive_v1.0

Test scenarios for SOP 11 (Bid Package) and SOP 15 (Bid Leveling). Each scenario must produce the specified result before the SOP is marked complete. Record all results in `docs/TEST_RESULTS.md` Phase 14 section.

---

## Test Environment

- **Database:** Docker `hci_postgres` (dev environment)
- **Test project:** Use project_id = 2 (101 Francis) unless otherwise noted
- **API base:** `http://localhost:8000/api/v1`

---

## SOP 11 — Bid Package Test Scenarios

### Unit Tests

| Test ID | Test Name | Input | Expected Result | Pass/Fail |
|---------|-----------|-------|-----------------|-----------|
| UT-11-01 | Create SOP 11 instance | `POST /api/v1/sop/11/instances` with project_id=2 | 201 Created; instance_id returned; status = Not Started | ⬜ |
| UT-11-02 | Input validation — all inputs missing | Trigger input check on new instance | Status → Inputs Missing; report lists all 11 required inputs | ⬜ |
| UT-11-03 | Input validation — partial inputs | Mark 8 of 11 inputs as confirmed | Status = Inputs Missing; report lists exactly 3 remaining blockers | ⬜ |
| UT-11-04 | Input validation — all inputs confirmed | Mark all 11 inputs as confirmed | Status → Ready to Start | ⬜ |
| UT-11-05 | Status transition — valid | Set status from Ready to Start → In Progress | 200 OK; status updated; event logged | ⬜ |
| UT-11-06 | Status transition — invalid | Attempt to set status from Not Started → Approved | 400 Error; invalid transition message | ⬜ |
| UT-11-07 | Stop condition SC-01 | Attempt to advance to In Progress with missing input | WorkflowBlockedError; SC-01 logged in sop_stop_events | ⬜ |
| UT-11-08 | Stop condition SC-04 | Attempt to set status → Issued without Gate 11-C | WorkflowBlockedError; SC-04 logged | ⬜ |
| UT-11-09 | Approval gate 11-C | Create Gate 11-C record with approver = "Buck Adams" | Gate record created; status → Approved | ⬜ |
| UT-11-10 | Scope section creation | `POST /api/v1/sop/11/{id}/scope_sections` with trade data | 201 Created; section stored with all fields | ⬜ |

### Integration Tests

| Test ID | Test Name | Scenario | Expected Result | Pass/Fail |
|---------|-----------|----------|-----------------|-----------|
| IT-11-01 | Happy-path workflow | Create instance → confirm inputs → add scope sections → AI review → Internal Review → Approval Required → Buck approves → Issued | All status transitions succeed; all events logged; final status = Issued | ⬜ |
| IT-11-02 | Revision cycle | Submit for Internal Review → PM sets Revision Required → owner corrects → resubmit | Status transitions: Internal Review → Revision Required → In Progress → Internal Review; comments attached | ⬜ |
| IT-11-03 | AI gap check | Submit scope sections with known missing drawing reference | AI gap report returns flag for missing reference; severity = HIGH | ⬜ |
| IT-11-04 | Vendor intelligence pull | Request sub invite list for trade = "concrete" project = 2 | Returns ≥ 1 vendor from vendor_intelligence; performance score included | ⬜ |
| IT-11-05 | Audit trail | Run happy-path workflow | sop_workflow_events has one record per status change; all events have timestamp and actor | ⬜ |
| IT-11-06 | Handoff to SOP 15 | Set SOP 11 status → Handed Off | SOP 15 instance created; SOP 15 references sop_11_instance_id | ⬜ |

---

## SOP 15 — Bid Leveling Test Scenarios

### Unit Tests

| Test ID | Test Name | Input | Expected Result | Pass/Fail |
|---------|-----------|-------|-----------------|-----------|
| UT-15-01 | Create SOP 15 instance | `POST /api/v1/sop/15/instances` or triggered from SOP 11 handoff | 201 Created; status = Not Started; parent SOP 11 ID linked | ⬜ |
| UT-15-02 | Input validation — fewer than 3 bids | Submit instance with 2 bids logged | Status → Inputs Missing; SC-01 report specifies minimum bidder rule | ⬜ |
| UT-15-03 | Input validation — 3+ bids | Log 3 responsive bids | Status → Ready to Start | ⬜ |
| UT-15-04 | Bid entry | `POST /api/v1/sop/15/{id}/bids` with bidder data | 201 Created; bid record stored with all fields | ⬜ |
| UT-15-05 | Stop condition SC-04 | Attempt to set status → Approved without Gate 15-C | WorkflowBlockedError; SC-04 logged | ⬜ |
| UT-15-06 | Adjustment calculation | Enter bid with 3 adjustments | adjusted_amount = base_bid ± sum of adjustments | ⬜ |
| UT-15-07 | Risk flag classification | Enter bid with a "no warranty" qualification | AI risk flag: class = Contract, severity = HIGH | ⬜ |
| UT-15-08 | Award record | `POST /api/v1/sop/15/{id}/award` with Buck decision fields | Award record created; status → Approved; timestamp logged | ⬜ |

### Integration Tests

| Test ID | Test Name | Scenario | Expected Result | Pass/Fail |
|---------|-----------|----------|-----------------|-----------|
| IT-15-01 | Happy-path workflow | Create instance → log 3 bids → AI leveling → normalize → Internal Review → Buck awards → Handed Off | All status transitions; leveling sheet output; award record; event log complete | ⬜ |
| IT-15-02 | Minimum bidder exception | < 3 bids; Buck authorizes exception | Exception record created; workflow unblocked; exception_flag = true on instance | ⬜ |
| IT-15-03 | AI leveling output | Log 3 bids with scope exclusions | AI output includes: normalization table, risk flags per bidder, prior performance from vendor intelligence, recommendation | ⬜ |
| IT-15-04 | Scope mismatch flag | Bidder references incorrect drawing revision | AI flags Document Control risk; SC-03 stop on advancement until PM resolves | ⬜ |
| IT-15-05 | Handoff to SOP 16 | Set status → Handed Off | SOP 16 record created (or PM notified to initiate); SOP 15 audit trail complete | ⬜ |

---

## UAT Scenarios (Phase D)

To be run by Buck on the live system after Phase C code is complete.

| UAT ID | Scenario | Pass Criteria |
|--------|----------|--------------|
| UAT-SOP11-01 | Buck assembles a bid package for a real trade on a real project | Bid package issued; all gates logged; package in MinIO |
| UAT-SOP15-01 | Buck reviews a leveling sheet for a real set of bids | AI-normalized leveling sheet produced; risk flags accurate; award record created after Buck decides |

---

*Test evidence recorded in: `docs/TEST_RESULTS.md`*  
*Audit trail verification: `sop_workflow_events` table*

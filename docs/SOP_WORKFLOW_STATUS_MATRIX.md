# HCI AI — SOP Workflow Status Matrix

**Version:** 1.0 | **Date:** 2026-06-25 | **Directive:** HCI_AI_SOP_to_Software_Execution_Layer_Master_Directive_v1.0

This matrix shows the 15 workflow statuses and where each SOP instance can be at any given time. Use it to understand current state, valid transitions, and system behavior at each status.

---

## Status Reference

| # | Status | Who Sets It | System Behavior |
|---|--------|------------|-----------------|
| 1 | Not Started | System (trigger) | Record created; owner notified |
| 2 | Inputs Missing | System (auto-check) | Blocks all work; lists missing inputs |
| 3 | Ready to Start | System (after inputs confirmed) | Owner can begin |
| 4 | In Progress | Owner | Work steps execute; AI available |
| 5 | AI Drafted | System (after AI run) | Output staged for human review |
| 6 | Internal Review | PM or Reviewer | Reviewer comments captured |
| 7 | Revision Required | Reviewer | Returns to owner; comments attached |
| 8 | Approval Required | PM (routes to approver) | Approver notified; work blocked |
| 9 | Approved | Approver (human only) | Approved status logged with name + date |
| 10 | Issued / Completed | PM or System | Deliverable sent/issued externally |
| 11 | Handed Off | System (handoff trigger) | Next SOP owner notified |
| 12 | Blocked | Owner or System | Reason logged; unblocking path specified |
| 13 | Exception Approved | Buck | Bypass documented; expiration set |
| 14 | Cancelled | PM or Buck | Cancellation reason logged |
| 15 | Archived | System (after close) | Record read-only |

---

## Valid Status Transitions

```
Not Started → Inputs Missing (if required inputs absent)
Not Started → In Progress (if inputs present and owner ready)
Inputs Missing → In Progress (after all blockers resolved)
Ready to Start → In Progress
In Progress → AI Drafted (AI produces draft output)
In Progress → Internal Review (owner submits without AI draft)
AI Drafted → Internal Review (PM or reviewer picks up draft)
Internal Review → Revision Required (reviewer finds gaps)
Internal Review → Approval Required (reviewer accepts; routes to approver)
Internal Review → Approved (reviewer IS the approver; combined role)
Revision Required → In Progress (owner corrects)
Revision Required → Internal Review (owner resubmits)
Approval Required → Approved (approver signs off)
Approval Required → Revision Required (approver sends back)
Approved → Issued / Completed (deliverable sent)
Approved → Handed Off (passed to next SOP owner)
Issued / Completed → Handed Off
Issued / Completed → Archived
Handed Off → Archived
Blocked → In Progress (after blocker resolved)
Exception Approved → In Progress
Exception Approved → Approved
(Cancelled) → terminal
(Archived) → terminal
```

---

## SOP Status by Lifecycle Phase

### Phase 4 — Bid Package (SOP 11)

| Step | Status | Trigger |
|------|--------|---------|
| Bid received from Owner/Design team | Not Started | Project accepted for bid |
| Missing drawings or specs | Inputs Missing | Plan review incomplete |
| All scope docs on hand | Ready to Start | Plan review (SOP 04) complete |
| Estimator assembles scope sections | In Progress | Estimator begins work |
| AI reviews scope for gaps, drafts sections | AI Drafted | AI run triggered |
| PM reviews scope completeness | Internal Review | PM review |
| PM finds missing scope item | Revision Required | Gap noted |
| PM approves package for issue | Approval Required | Routes to Buck |
| Buck approves bid package | Approved | Buck logs approval |
| Package issued to subs | Issued / Completed | Bid request sent |
| Bid date passed; hands off to SOP 15 | Handed Off | SOP 15 triggered |
| Project record closed | Archived | Post-project |

### Phase 5 — Bid Leveling (SOP 15)

| Step | Status | Trigger |
|------|--------|---------|
| Handed off from SOP 11 (bids due) | Not Started | Bid date passed |
| Fewer than 3 responsive bids | Inputs Missing | Minimum bidder rule |
| ≥ 3 bids received | Ready to Start | Bid log complete |
| Estimator compiles bids | In Progress | Estimator begins |
| AI normalizes bids, flags qualifications, generates leveling sheet | AI Drafted | AI run triggered |
| PM reviews leveling sheet | Internal Review | PM review |
| PM finds scope gap in leveling | Revision Required | Gap noted; scope check triggered |
| PM recommends award; routes to Buck | Approval Required | Routes to Buck |
| Buck awards | Approved | Buck logs decision |
| Award memo issued to sub | Issued / Completed | Award communication |
| Handed off to SOP 16 (Buyout) | Handed Off | SOP 16 triggered |

---

## SOP Status Dashboard Columns

Every SOP instance shown in dashboards displays:
- `SOP number` | `Project` | `Status` | `Owner` | `Days in Status` | `Blocked?` | `Next Action`

Red flags in dashboard:
- Days in status > SLA for that status-type
- Status = Blocked with no resolution date
- Status = Approval Required with no approver assigned

---

*Cross-references: `docs/SOP_2_0_CONVERSION_STANDARD.md` | `BOOK_00/18_SOP_TO_SOFTWARE_EXECUTION_LAYER.md`*

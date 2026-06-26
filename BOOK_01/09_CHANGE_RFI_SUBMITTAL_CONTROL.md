# BOOK_01 — Volume 09: Change, RFI, and Submittal Control

**Version:** 1.0 | **Date:** 2026-06-25

---

## Why Change Control Matters

Change is where construction projects fail financially. A project that bids at 8% margin can close at 2% or worse if changes are:
- Performed before being documented
- Documented but not priced correctly
- Priced but not submitted to the owner in time
- Submitted but allowed to drag without resolution

HCI AI tracks every potential change from the moment it is identified — not from when the change order is submitted.

---

## Change Management Sequence

```
Change Event Identified (site condition, design change, owner request, unforeseen)
  → Issue Log created (date, description, scope affected, potential impact)
  → PM reviews: is this a change? Is HCI entitled?
  → If yes: RFI submitted if design clarification needed
  → Scope and cost impact analyzed
  → Change order drafted and priced
  → Internal review: PM + Buck (if > threshold)
  → Change order submitted to Owner/Architect
  → Owner reviews: Approved / Rejected / Pending
  → If Approved: budget updated, scope added to subcontract if applicable
  → Change logged and closed
```

---

## Change Order Log

Every change order — from identification to resolution — is tracked:

| Field | Description |
|-------|-------------|
| CO Number | Sequential per project |
| Status | Potential → Drafted → Submitted → Approved / Rejected / Pending |
| Change Source | Owner request / Design change / Site condition / Unforeseen / Other |
| Description | Clear, specific scope description |
| Scope Impact | Drawings and spec sections affected |
| Cost Impact | HCI cost and owner price |
| Schedule Impact | Calendar days impact and critical path effect |
| Related RFIs | RFI numbers that support the change |
| Submitted Date | When sent to owner |
| Response Date | When owner responded |
| Approval Date | When formally approved |
| Budget Update | Automatic after approval |

AI drafts change order narrative from the change event, related RFI responses, and scope documentation. PM reviews and Buck approves before submission.

---

## RFI Process (SOP 32)

RFIs are the formal mechanism for getting design clarifications. Every unanswered question that affects scope, cost, or schedule must have an RFI.

**RFI creation:**
1. PM or Superintendent identifies question
2. AI drafts RFI from: question, drawing reference, spec reference, impact if not answered
3. PM reviews and submits
4. RFI logged with submitted date and required response date

**RFI tracking:**
- Response overdue at 5 business days: PM automated reminder
- Response overdue at 10 business days: Buck notified; PM takes escalation action
- All RFI responses logged with date, responder, and disposition
- Any RFI response that changes scope automatically creates a Potential Change Order entry

---

## Submittal Process (SOP Reference)

Submittals are shop drawings, product data, and samples submitted to the design team for review and approval before fabrication or installation.

**Submittal controls:**
- No fabrication or delivery of materials requiring submittal approval without "Approved" or "Approved as Noted" disposition
- All "Revise and Resubmit" dispositions trigger a new submission cycle with new due date
- "Rejected" dispositions create an issue log and PM notification

**AI role in submittals:** AI flags submittals that are approaching the last-possible submission date given schedule need, lead time, and review time. PM is notified 10 days before the window closes.

---

## Change Authority Thresholds

Configured in the Operating Rules Engine — not hardcoded:

| Change Amount | Internal Authority | Owner Notification |
|--------------|-------------------|-------------------|
| < $5,000 | PM approves | Not required |
| $5,000 - $25,000 | PM + Buck review | Required before submission |
| > $25,000 | Buck approves | Required before submission |
| Any critical path impact | Buck reviews regardless of cost | Required |

These thresholds are configurable. See `docs/OPERATING_RULES_ENGINE_STANDARD.md`.

---

## Change, RFI, and Submittal KPIs

| KPI | Target | Source |
|-----|--------|--------|
| Potential COs identified within 5 days of event | > 90% | CO log event date vs. ID date |
| RFIs submitted within 2 days of question | > 90% | RFI log |
| Open RFIs > 14 days | 0 | RFI age report |
| Submittals submitted before last possible date | 100% | Submittal tracker |
| CO submitted to owner within 10 days of approval to proceed | > 90% | CO log |
| Unapproved change orders worked without authorization | 0 | CO status at field start |

---

*Related SOPs: SOP 31 (Change Order), SOP 32 (RFI), SOP 33 (Schedule Impact)*  
*Database tables: `rfis`, `submittals`, `change_orders` in PostgreSQL*

# Chapter 13 — Submittal Management
**HCI AI Operations Manual | Part I — Business Operations**
*Authority: Buck Adams | Last Updated: 2026-07-01*

---

## 13.1 Overview

A submittal is a sub or supplier's proof that the specific product, material, or shop drawing they intend to install matches the design intent — before it gets installed. Submittals catch the $40,000 wrong-tile-order or the cabinet shop drawing that doesn't match the field dimensions, while it's still cheap to fix.

Every spec section that calls for a submittal must have one logged, tracked, and resolved before that scope proceeds. Skipping submittals to save time is how change orders happen later — at ten times the cost.

---

## 13.2 What the System Tracks

The `submittals` table is the register. Every submittal has:
- `submittal_number` — auto-assigned, sequential per project
- `spec_section` — which CSI division/section calls for this submittal
- `description` — what's being submitted (cabinet shop drawings, window schedule, tile samples, etc.)
- `submitted_by` — which sub or supplier
- `status` — `pending` → `under_review` → `approved` / `rejected` / `revise_and_resubmit`
- `submitted_date`, `required_approval_date`, `approved_date`

```
GET /gateway/project/{code}/submittals
GET /gateway/project/{code}/submittals?status=pending
```

This is the same live register the PM checks, not a separate spreadsheet. If it's not in this table, it doesn't count as submitted.

---

## 13.3 Logging a New Submittal

**Step 1 — Sub or supplier sends the submittal** (shop drawings, cut sheets, samples) via email or Houzz.

**Step 2 — PM logs it in the system same day:**
```
POST /gateway/submittals/create
{
  "project_code": "1355R",
  "spec_section": "06 41 00 — Architectural Wood Casework",
  "description": "Kitchen cabinet shop drawings — Przemek Cabinets",
  "submitted_by": "Przemek Cabinets",
  "required_approval_date": "2026-07-10"
}
```
The system auto-assigns the next submittal number for that project. Do not let submittals sit in an inbox uncounted — an unlogged submittal is functionally the same as one that was never submitted, because nobody is tracking its deadline.

**Step 3 — Route for review.** Architectural/design submittals go to the architect first. Structural or engineering submittals go to the SE. Straightforward product submittals (matching an already-approved allowance item) can be reviewed by the PM directly.

---

## 13.4 Review and Status Workflow

```
PATCH /gateway/submittals/{id}/status
{"status": "under_review"}
```

**Possible outcomes:**
- `approved` — proceed as submitted. `approved_date` auto-stamps to today.
- `rejected` — does not meet spec; sub must submit a compliant alternative from scratch.
- `revise_and_resubmit` — close but not quite (wrong finish, wrong dimension noted) — sub corrects and resubmits under the same submittal number with revision notes.

**Turnaround target:** 5 business days for straightforward submittals, 10 business days for anything requiring architect or SE review. If a submittal is going to blow past its `required_approval_date`, tell the PM and the sub immediately — don't let the deadline pass silently and then explain it after the fact.

**What NOT to do:**
- Do not verbally approve a submittal "so the sub can keep moving" without logging the approval in the system — if it's not in `submittals` as `approved`, it isn't approved.
- Do not let a sub proceed with fabrication on a `revise_and_resubmit` item — that's exactly the situation submittals exist to prevent.

---

## 13.5 Submittals and Schedule / Health

Overdue submittals (past `required_approval_date` with no resolution) are a schedule risk in the same category as overdue RFIs — long-lead items like cabinets, windows, and custom millwork can add months if the submittal cycle stalls. Watch the submittal register the same way you watch the RFI log (Chapter 15).

---

## 13.6 Submittal Record Keeping

Submittal logs and approved documents are filed in Google Drive under the project folder → `Submittals/` subfolder, cross-referenced by submittal number. Keep for the same 10-year minimum retention as contract documents (Chapter 07) — submittal records are frequently the deciding evidence in a defect dispute.

---

*Next: Chapter 14 — Financial Management & Approvals*

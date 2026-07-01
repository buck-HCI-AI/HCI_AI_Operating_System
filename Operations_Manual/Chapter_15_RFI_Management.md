# Chapter 15 — RFI Management
**HCI AI Operations Manual | Part I — Business Operations**
*Authority: Buck Adams | Last Updated: 2026-07-01*

---

## 15.1 Overview

An RFI (Request for Information) is a formal question to the design team when the drawings, specs, or field conditions don't give the sub or PM enough to proceed correctly. RFIs exist because guessing on an ambiguous detail is how a wall ends up in the wrong place or a structural connection gets built wrong.

An open RFI blocking active work is one of the fastest ways a project goes from GREEN to RED — see 101F's steel delay pattern in Chapter 10, and 1355R's Axis B beam pocket RFI below.

---

## 15.2 Where RFIs Originate

- **Field** — superintendent hits a condition that doesn't match the drawings (Chapter 03 daily log flow: `POST /gateway/field/rfi`)
- **PM / drawing review** — a scope gap or conflict found during bid leveling or pre-construction review
- **Sub** — a trade partner identifies something ambiguous or missing before they can price or install their scope

However it originates, it gets logged the same day — do not let a question sit in a text thread or a job-site conversation without becoming a real RFI.

---

## 15.3 What the System Tracks

The `rfis` table is the register:
- `subject` — what's being asked
- `status` — `open` / `answered` / `closed`
- `submitted_date`, `required_response_date`
- Linked `project_id`

```
GET /gateway/project/{code}/action-list        — includes open RFIs for that project
GET /gateway/executive/report                  — open_rfis and overdue_rfis per project
```

`required_response_date` is what turns a routine RFI into an urgent one. Once that date passes with no answer, the RFI counts as **overdue** and becomes a schedule-risk flag on the project's health score — the executive report literally raises the project to RED health when `overdue_rfis > 0` (Chapter 10 risk detection logic).

---

## 15.4 RFI Lifecycle

**Step 1 — Log it.** Field: `POST /gateway/field/rfi`. Office/PM: log directly against the project with a `required_response_date` — typically 5-10 business days out depending on complexity, sooner if it's blocking active work.

**Step 2 — Route to the right party.** Structural questions go to the SE. Design/architectural questions go to the architect. Never let an RFI sit unrouted.

**Step 3 — Follow-up cadence.** Every open RFI gets a follow-up if no response in 3 business days (Chapter 04 §PM daily cycle). Don't wait for `required_response_date` to arrive before checking in.

**Step 4 — AI-drafted responses (design-team-facing questions only).** The AI can draft a proposed response when the answer is derivable from already-approved documents (e.g., confirming a dimension against an approved shop drawing) — but any RFI response that changes scope, cost, or schedule requires PM/Buck review before it goes out. Never let an AI-drafted RFI response reach the design team or a sub without human review.

**Step 5 — Close it out.** Once answered, the response is forwarded to the superintendent the same day it's received (Chapter 04) and the RFI status updates to `answered`/`closed`. If the answer changes scope or cost, it becomes a Change Order (Chapter 07 §7.5) — the RFI itself doesn't authorize extra work or cost.

---

## 15.5 Escalation

**If an RFI is blocking work on site:** escalate immediately — call the designer directly, don't wait for email. A blocked crew costs money every hour.

**Live example (1355R, current):** RFI-001 — Axis B beam pocket, structural — sent to the SE, no response yet as of this writing. Framing cannot proceed at Axis B until it's answered. This is exactly the profile that pushes a project's schedule variance negative and its health to RED — see Chapter 10 and Chapter 09 for how this single open RFI cascades into schedule risk.

---

## 15.6 RFIs and Schedule Impact

Every open RFI should carry an implicit question: **is anything on the schedule waiting on this answer?** If yes, that RFI is critical-path and needs daily follow-up, not the standard 3-day cadence. Cross-reference the project's schedule (Chapter 09) — an RFI tied to a critical-path activity is a different priority than one tied to a finish selection three months out.

**What NOT to do:**
- Do not let field work proceed on an assumption when an RFI is open for that exact condition — that's the definition of the risk RFIs exist to prevent.
- Do not close an RFI as "answered" until the response is actually documented and forwarded to the field.

---

*Next: Chapter 16 — Project Close-Out*

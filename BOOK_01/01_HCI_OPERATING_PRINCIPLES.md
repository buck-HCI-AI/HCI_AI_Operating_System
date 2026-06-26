# BOOK_01 — Volume 01: HCI Operating Principles

**Version:** 1.0 | **Date:** 2026-06-25

---

## The Five Operating Principles

These principles govern every workflow, decision, and tool in HCI AI. They are not aspirational — they are enforced by the system.

---

### Principle 1: Every Project Improves the Company

Every project produces structured data: costs, schedules, risks, decisions, vendor performance, lessons learned. That data is not discarded at closeout — it feeds the historical cost database, the vendor intelligence service, the decision intelligence engine, and the risk library.

The system gets better with every project. A bid leveled today is calibrated by every bid HCI has ever leveled.

**In practice:** Post-project reviews (SOP 42) are not optional. Lessons learned are not filed in a folder — they are indexed, searchable, and applied to the next project.

---

### Principle 2: Decisions Become Knowledge

Construction is a series of decisions: what to include in scope, what vendor to use, how to respond to an RFI, whether to approve a change. Most of these decisions disappear after the project closes.

In HCI AI, every significant decision is captured: what was decided, why, what the alternatives were, what the risk was, who approved it. This decision record is searchable on future projects.

**In practice:** The Decision Intelligence service (SOP 36 / BOOK_01 Volume 12) captures decisions. Decisions are never implied — they are recorded.

---

### Principle 3: Evidence Over Opinion

Reporting, risk assessment, and status updates must come from data, not narrative. The system generates evidence automatically:
- Daily logs generate crew counts, weather records, work-in-place
- Budget tracking generates variance automatically from posted costs
- Schedule analysis identifies actual vs. planned progress
- Bid leveling captures every number and every risk flag

**In practice:** Weekly reports are drafted by AI from the project record. They are reviewed by the PM and signed off by Buck — not assembled from email.

---

### Principle 4: One Source of Truth

Every project has one record. Drawings live in one place. The schedule lives in one place. Costs live in one place. Meeting notes live in one place. No duplication.

When information is in two places, it will diverge. When it diverges, decisions are made on wrong information.

**In practice:** All documents are routed to the project folder in Google Drive via defined naming conventions. All project data writes to PostgreSQL. All search goes through the Project Brain.

---

### Principle 5: SOPs Run Through the System

HCI's 42 Standard Operating Procedures are not a binder on a shelf. They are converted into executable workflows that run through HCI AI. Each SOP has:
- A trigger that starts it
- Required inputs that must be present before work begins
- A workflow spine that enforces the right sequence
- Stop conditions that halt work when something is wrong
- Approval gates that prevent external commitments without authorization
- A data record that proves the SOP was completed correctly

**In practice:** If a bid package goes out without the right scope sections, the system flagged that gap at the approval gate. Evidence is in the record.

---

## What These Principles Prohibit

| Prohibited | Reason |
|-----------|--------|
| Skipping approval gates | The whole point of the gate is that unauthorized commitments don't go out |
| AI making awards, signing contracts, or approving budgets | These require human judgment and authority |
| Updating HubSpot without human review | CRM data is client-facing; errors have external consequences |
| Two versions of the same document | One source of truth |
| Verbal commitments without follow-up records | If it's not in the system, it didn't happen |
| SOP bypasses without exception records | Bypasses are sometimes necessary; undocumented bypasses are not |

---

## How These Principles Are Enforced

Not by policy — by the software:
- Stop conditions block workflow progression when inputs are missing
- Approval gates require a named approver before status advances to Issued
- Dual-entry checks catch budget discrepancies at input
- Audit logs capture every status change, every reviewer, every approval

---

*Volume 02 covers how these principles apply to preconstruction.*

# Houzz Approval Gates
## HCI AI Operating System — Houzz Browser Intelligence Workstream
**Version:** 1.0 | **Created:** 2026-06-26 | **Authority:** APPROVAL_GATES.md + HCI_AI_CONSTITUTION.md  
**Parent Gates:** See /APPROVAL_GATES.md for base gate definitions (F, C, A, E, H, D, P, G)

---

## Purpose

This document extends the master APPROVAL_GATES.md with Houzz-specific gate definitions. Every action the HCI AI system might take as a result of Houzz intelligence extraction — beyond read-only reporting — must pass through a defined gate before execution.

**Absolute Rule:** Reading Houzz data requires NO approval. Acting on Houzz intelligence requires gates.

---

## Houzz Gate Reference Table

| Gate ID | Name | Trigger | Parent Gate | Approver | SLA |
|---|---|---|---|---|---|
| HZ-R | Read | Browser Agent reads any Houzz page | None | No approval needed | Immediate |
| HZ-E1 | Client Communication | AI-drafted message to client based on Houzz intelligence | Gate E | @buck-HCI-AI | 24h |
| HZ-E2 | Client Update | Project update sent to client derived from Houzz log | Gate E | @buck-HCI-AI | 24h |
| HZ-H1 | HubSpot Status Write | Writing Houzz-derived project health to HubSpot deal | Gate H | @buck-HCI-AI | 8h |
| HZ-H2 | HubSpot Activity Write | Logging Houzz field activity as HubSpot CRM activity | Gate H | @buck-HCI-AI | 8h |
| HZ-D1 | Drive Report File | Committing daily intelligence report to project Drive folder | No gate needed (AI folder) | Auto | Auto |
| HZ-D2 | Drive Client Deliverable | Modifying a client-facing document with Houzz data | Gate H | @buck-HCI-AI | 24h |
| HZ-F1 | Procurement Action | Creating/expediting a PO based on Houzz delivery alert | Gate F | @buck-HCI-AI | 24h |
| HZ-S1 | Schedule Write-back | Updating Houzz schedule based on AI analysis | Gate E (if client-visible) | @buck-HCI-AI | 24h |
| HZ-X1 | Houzz Log Edit | Any edit to a Houzz daily log by AI | PROHIBITED | N/A | N/A |
| HZ-X2 | Houzz Message Send | Sending any message via Houzz messaging | PROHIBITED | N/A | N/A |
| HZ-X3 | Houzz Record Delete | Deleting any Houzz record | PROHIBITED | N/A | N/A |

---

## Gate HZ-R — Read (No Approval Required)

**Trigger:** Browser Claude navigating to and reading any Houzz project page.

**Fully autonomous — no approval, no notification, no delay.**

Permitted read actions:
- Navigate to project dashboard
- Read daily log (any date, any project)
- View and note photo metadata
- Read schedule activities
- Read labor and subcontractor entries
- Read materials and delivery records
- Read project overview and status
- Read client message history (view only — do not reply)

**Logging:** Every read session is logged to `reports/houzz/daily/` with timestamp, projects read, and data categories accessed.

---

## Gate HZ-E1 — Client Communication Draft

**Trigger:** HCI AI proposes sending any communication to a Houzz project client.

**This gate extends Gate E from APPROVAL_GATES.md.**

**Process:**
1. ChatGPT drafts client communication based on Houzz intelligence
2. Draft includes: recipient, subject, full message body, context, urgency level
3. n8n routes draft to human owner for review
4. Human owner edits as needed and explicitly approves
5. On approval: message sent via designated channel (NOT via Houzz AI — human sends)
6. Communication logged to `reports/gates/gate-HZ-E1-log.md`

**Prohibited:** AI agent sending any Houzz project communication autonomously.  
**Note:** Houzz has its own client messaging system. AI never sends messages through Houzz directly.

---

## Gate HZ-E2 — Client Project Update

**Trigger:** HCI AI proposes sending a project status update to a client that originated from Houzz daily log data.

**Examples:**
- "Framing is 80% complete based on today's field log"
- "Concrete pour completed today — ahead of schedule"
- "Weather delay today — schedule impact assessment attached"

**Process:** Same as HZ-E1. Human must review, approve, and send.

---

## Gate HZ-H1 — HubSpot Project Status Write

**Trigger:** Houzz daily extraction produces a project health signal (Green/Yellow/Red) that HCI AI wants to write to the HubSpot deal record.

**This is the most common Houzz-triggered gate.**

**Pre-gate AI actions (automatic):**
- Extract daily log
- Generate health signal (Green/Yellow/Red)
- Compute schedule variance
- Summarize field conditions
- Prepare HubSpot write payload: {deal_id, field, current_value, proposed_value, rationale}

**Gate process:**
1. AI prepares update payload with full Houzz context
2. n8n sends approval request: "Update [Project Name] HubSpot status to [Yellow] — schedule delay flagged"
3. Human reviews and approves/modifies/rejects
4. On approval: n8n writes to HubSpot via Gate H process
5. Write logged to `reports/gates/gate-HZ-H1-log.md`

**Batch option:** Human may approve a batch of project status updates in one review.

---

## Gate HZ-H2 — HubSpot Activity Write

**Trigger:** HCI AI wants to log a Houzz field event as an activity on a HubSpot deal (e.g., "Foundation poured," "Framing inspection passed").

**Process:** Same as HZ-H1. Human approves before any HubSpot activity is created.

---

## Gate HZ-D1 — Drive Report File (Auto)

**No approval required.** HCI AI may autonomously commit daily intelligence reports to the designated AI working folder in Google Drive:

`Drive: HCI AI Working / Projects / [Project Name] / Daily Intelligence / YYYY-MM-DD-intelligence.md`

This is not a client-facing folder. Commits here do not require gate approval.

---

## Gate HZ-D2 — Drive Client Deliverable Modification

**Trigger:** HCI AI proposes adding Houzz-derived data to a client-facing document (e.g., owner report, monthly summary).

**Process:** Human reviews proposed changes before any client document is modified.

---

## Gate HZ-F1 — Procurement Action

**Trigger:** Houzz daily log reveals a missing or late material delivery that HCI AI recommends expediting via purchase order or vendor contact.

**Pre-gate AI actions:**
- Extract delivery alert from daily log
- Cross-reference with procurement schedule
- Identify critical vs. non-critical items
- Draft expedite request or PO amendment
- Prepare recommendation with: item, vendor, current status, impact on schedule

**Gate process:**
1. AI delivers procurement recommendation to human owner
2. Human reviews urgency and approves action
3. Human (or designated PM) executes procurement action
4. Action logged with Houzz log reference

---

## Gate HZ-S1 — Schedule Write-Back

**Trigger:** HCI AI analyzes schedule variance and wants to update Houzz schedule activities.

**This gate is rarely triggered.** Standard operation is: Houzz schedule is managed by the superintendent/PM. HCI AI reads and reports; it does not write back to Houzz schedule.

**Exception case:** If human owner explicitly authorizes an AI-assisted schedule update, Gate HZ-S1 applies:
1. AI prepares proposed schedule changes with full justification
2. Human reviews and approves each change
3. Human (or designated superintendent) executes changes in Houzz
4. AI never directly modifies Houzz schedule entries

---

## Absolute Prohibitions (HZ-X Gates)

These gates cannot be opened. They represent permanently prohibited actions.

### HZ-X1 — Houzz Log Edit
**Any AI modification of a submitted or draft Houzz daily log is permanently prohibited.**  
Reason: Daily logs are legal and contractual records. AI editing them without superintendent knowledge is a data integrity and liability violation.

### HZ-X2 — Houzz Message Send
**Any AI-generated message sent through Houzz messaging is permanently prohibited.**  
Reason: Houzz messages are client-visible communications constituting Gate E events. AI cannot autonomously send client communications under any circumstance.

### HZ-X3 — Houzz Record Delete
**Any deletion of Houzz records (logs, photos, messages, files) by AI is permanently prohibited.**  
Reason: Houzz records are project documentation of record. Deletion without superintendent and human owner approval is a destructive action under Gate D — and even with Gate D approval, deletion in Houzz must be executed by a human.

---

## Houzz Gate Audit Trail

All Houzz gate events are logged to:
- `reports/gates/gate-HZ-[ID]-log.md` — per gate type
- `reports/houzz/daily/YYYY-MM-DD-extraction-log.md` — daily read log

Gate logs include: timestamp, project, gate ID, proposed action, human decision, execution status.

---

*Governed by APPROVAL_GATES.md + HCI_AI_CONSTITUTION.md | Houzz Browser Intelligence Workstream | Hendrickson Construction, Inc.*

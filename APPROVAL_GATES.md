# Approval Gates
## HCI AI Operating System — Hendrickson Construction, Inc.
**Version:** 1.0 | **Effective:** 2026-06-26 | **Authority:** HCI_AI_CONSTITUTION.md Article III, Section 3.2

---

## Purpose

Approval Gates are mandatory checkpoints that block AI agent execution until explicit human authorization is received. Each gate has a unique identifier, trigger conditions, required approver, approval mechanism, and timeout behavior.

**The gates are not optional. No AI agent may bypass a gate under any circumstance.**

---

## Gate Reference Table

| Gate ID | Name | Trigger | Approver | Timeout |
|---|---|---|---|---|
| Gate F | Financial | Any monetary transaction | @buck-HCI-AI | 24h then halt |
| Gate C | Contract | Contract create/modify/execute | @buck-HCI-AI | 24h then halt |
| Gate A | Award | Subcontractor or bid award | @buck-HCI-AI | 24h then halt |
| Gate E | External Comms | Client-facing communication | @buck-HCI-AI | 24h then halt |
| Gate H | HubSpot Write | Production CRM record write | @buck-HCI-AI | 8h then halt |
| Gate D | Destructive | Delete, purge, archive | @buck-HCI-AI | 24h then halt |
| Gate P | Production Deploy | Any live system deployment | @buck-HCI-AI | 24h then halt |
| Gate G | GitHub Merge | Merge PR to `main` | @buck-HCI-AI | No timeout |

---

## Gate Definitions

### Gate F — Financial
**Trigger:** Any workflow that initiates, authorizes, or records a financial transaction including: invoice generation, payment processing, purchase order creation, budget adjustment, expense recording.

**Pre-gate AI actions allowed:**
- Generate invoice draft for review
- Summarize payment history
- Flag overdue receivables

**Gate process:**
1. AI generates draft transaction with full context
2. n8n sends approval request to human owner with: amount, payee, purpose, supporting documents
3. Human reviews and approves/rejects via GitHub issue comment or designated approval channel
4. On approval: AI executes transaction and logs confirmation
5. On rejection: AI logs reason, creates follow-up issue, halts

**Audit:** All financial gate events logged to `reports/gates/gate-F-log.md`

---

### Gate C — Contract
**Trigger:** Creation, modification, execution, or termination of any contract, subcontract, or binding agreement.

**Pre-gate AI actions allowed:**
- Draft contract from approved template
- Summarize existing contract terms
- Flag contract expiration dates
- Generate contract comparison report

**Gate process:**
1. AI produces complete contract draft with redline summary if modifying
2. Approval request sent with: parties, scope, value, term, key risks
3. Human reviews and approves/rejects
4. On approval: AI finalizes document and routes for signature
5. On rejection: AI revises per human instructions

**Audit:** `reports/gates/gate-C-log.md`

---

### Gate A — Award
**Trigger:** Selection of a subcontractor, vendor, or bidder; issuance of a notice of award; any binding selection decision.

**Pre-gate AI actions allowed:**
- Score and rank bids against criteria
- Generate bid comparison matrix
- Flag missing compliance documents
- Summarize subcontractor history

**Gate process:**
1. AI produces recommendation with bid analysis and rationale
2. Human reviews recommendation
3. Human issues award decision
4. AI processes award notification and documentation

**Audit:** `reports/gates/gate-A-log.md`

---

### Gate E — External Communications
**Trigger:** Any communication sent to a client, subcontractor, regulatory body, or external party on behalf of Hendrickson Construction, Inc.

**Pre-gate AI actions allowed:**
- Draft all communications
- Suggest response options
- Summarize communication history
- Flag urgent items requiring response

**Gate process:**
1. AI drafts communication with full context and suggested send date
2. Human reviews, edits if needed, and approves
3. AI sends (or human sends) from authorized channel
4. Sent communication logged

**Note:** Internal team communications do not require Gate E approval.

**Audit:** `reports/gates/gate-E-log.md`

---

### Gate H — HubSpot CRM Write (Production)
**Trigger:** Any create, update, or delete operation on production HubSpot records including: contacts, companies, deals, activities, properties.

**Pre-gate AI actions allowed:**
- Read all HubSpot records
- Generate reconciliation reports
- Identify missing or outdated records
- Write to staging/sandbox HubSpot environment

**Gate process:**
1. AI generates proposed CRM write with: record ID, field(s), current value, proposed value, rationale
2. Approval request sent (target: 8-hour SLA due to operational urgency)
3. Human approves/rejects individual or batch writes
4. AI executes approved writes and logs

**Audit:** `reports/gates/gate-H-log.md`

---

### Gate D — Destructive Actions
**Trigger:** Any action that permanently removes, deletes, archives, or makes irrecoverable: records, files, repository content, database entries, workflow history.

**Pre-gate AI actions allowed:**
- Identify candidates for deletion
- Generate deletion impact analysis
- Soft-delete or mark for review (reversible)

**Gate process:**
1. AI produces deletion manifest: item, location, last modified, dependencies, impact
2. Human reviews manifest and confirms each item or batch
3. AI executes deletion only for explicitly confirmed items
4. Deletion logged with confirmation record

**Audit:** `reports/gates/gate-D-log.md`

---

### Gate P — Production Deployment
**Trigger:** Any deployment, release, or activation of code, workflows, or configuration to a live production environment.

**Pre-gate AI actions allowed:**
- Run all automated tests
- Generate production readiness scorecard
- Validate all pre-deployment checklist items
- Deploy to staging environment

**Gate process:**
1. AI produces production readiness scorecard (see AUTOMATION_GOVERNANCE.md)
2. All automated tests must pass (gate auto-blocks if tests fail)
3. Human reviews scorecard and approves deployment
4. Deployment executed in human-supervised window
5. Post-deployment health check run automatically

**Audit:** `reports/gates/gate-P-log.md`

---

### Gate G — GitHub Merge to Main
**Trigger:** Any pull request merge targeting the `main` branch.

**Pre-gate AI actions (automated):**
- Codex: Code review and test run
- CI/CD: Automated test suite
- CODEOWNERS: Automatic reviewer assignment

**Gate process:**
1. PR must have passing CI checks
2. At least 1 human approval required (from @buck-HCI-AI or designated reviewer)
3. No unresolved review comments
4. PR checklist fully completed
5. Human clicks "Merge" — AI agents do not auto-merge to `main`

**No timeout** — PRs remain open until human acts.

**Audit:** GitHub PR history (permanent record)

---

## Gate Timeout Behavior

When a gate times out without human response:
1. Automation halts completely — no partial actions
2. GitHub issue created: `[GATE TIMEOUT] Gate X — [description]` labeled `blocked`
3. n8n sends escalation alert
4. Work item moved to "Blocked" status on sprint board
5. Human owner must re-initiate the gate request after review

---

## Gate Override

In emergencies, the human owner may bypass gate documentation requirements by providing explicit written instruction (GitHub issue comment or commit message). All overrides are logged and reviewed in the next sprint retrospective.

---

*Governed by HCI_AI_CONSTITUTION.md | Hendrickson Construction, Inc.*

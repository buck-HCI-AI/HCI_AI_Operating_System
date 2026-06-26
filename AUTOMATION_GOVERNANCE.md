# Automation Governance
## HCI AI Operating System — Hendrickson Construction, Inc.
**Version:** 1.0 | **Effective:** 2026-06-26 | **Authority:** HCI_AI_CONSTITUTION.md Article III & VI

---

## Purpose

This document defines what may be automated, what requires human approval, all recurring automation workflows, and the rules governing automation behavior across the HCI AI Operating System.

---

## Part 1 — Automation Classification

### 1.1 — Fully Autonomous (No Approval Required)

These actions may be performed by AI agents without human intervention:

| Category | Examples |
|---|---|
| **Reads** | Query HubSpot contacts, read Drive files, fetch GitHub issues, read registry |
| **Searches** | Search across all systems for matching records |
| **Summaries** | Generate reports from existing data |
| **Validation** | Check data integrity, detect duplicates, verify links |
| **Routing** | Move data between staging/internal systems |
| **Drafting** | Create draft documents, issue templates, PR descriptions |
| **Notifications** | Internal Slack/email/GitHub alerts and status updates |
| **GitHub ops** | Create issues, labels, milestones, comments, feature branch commits |
| **Reporting** | Daily, weekly, per-sprint reports committed to repository |
| **Health checks** | Workflow status, registry sync, broken link scans |

### 1.2 — Approval Required (Human Gate)

These actions are blocked until explicit human approval is received:

| Category | Examples | Approval Gate |
|---|---|---|
| **Financial** | Invoicing, payment, budget allocation | APPROVAL_GATES.md — Gate F |
| **Contracts** | Creating, modifying, signing agreements | APPROVAL_GATES.md — Gate C |
| **Awards** | Subcontractor selection, bid awards | APPROVAL_GATES.md — Gate A |
| **Client communications** | Emails, proposals, status updates to clients | APPROVAL_GATES.md — Gate E |
| **CRM writes** | HubSpot contact/deal create or update (production) | APPROVAL_GATES.md — Gate H |
| **Destructive** | Delete records, archive projects, purge data | APPROVAL_GATES.md — Gate D |
| **Production deploy** | Any push to live systems or production environments | APPROVAL_GATES.md — Gate P |
| **Code merge** | Merging PRs to `main` branch | APPROVAL_GATES.md — Gate G |

---

## Part 2 — Recurring Automation Schedule

### 2.1 — Daily Automations

#### Daily Repository Status Report
- **Trigger:** Every day at 07:00 local time
- **Owner:** n8n (Browser Claude on manual trigger)
- **Output:** `reports/daily/YYYY-MM-DD-repo-status.md` committed to repository
- **Contents:**
  - Open issues by label and milestone
  - PRs awaiting review
  - Recent commits (last 24h)
  - Blocked items count
  - Sprint progress summary
- **Escalation:** If >3 blocked items, alert human owner

#### Workflow Health Check
- **Trigger:** Every day at 06:00
- **Owner:** n8n
- **Output:** `reports/daily/YYYY-MM-DD-workflow-health.md`
- **Contents:**
  - n8n workflow execution status (pass/fail)
  - Failed workflow runs with error summary
  - Execution time anomalies
  - System connectivity (HubSpot, Drive, GitHub API)
- **Escalation:** Any failure triggers immediate alert

#### n8n Workflow Status Report
- **Trigger:** Every day at 08:00
- **Owner:** n8n (self-reporting)
- **Output:** `reports/daily/YYYY-MM-DD-n8n-status.md`
- **Contents:**
  - Active workflows and last run status
  - Execution counts (24h)
  - Error rate
  - Queue depth

### 2.2 — Weekly Automations

#### Sprint Review Summary
- **Trigger:** Every Monday at 09:00
- **Owner:** ChatGPT / n8n
- **Output:** `reports/weekly/YYYY-WNN-sprint-review.md`
- **Contents:**
  - Sprint velocity (issues closed vs. planned)
  - Carry-over items
  - Blockers resolved
  - Upcoming sprint priorities
  - AI team performance notes
- **Escalation:** Shared with human owner for review and approval

#### Registry Duplicate Check
- **Trigger:** Every Tuesday at 07:00
- **Owner:** n8n
- **Output:** `reports/weekly/YYYY-WNN-registry-duplicates.md`
- **Contents:**
  - Duplicate records detected in registry (05_Database/)
  - Suggested merge/deduplication actions (requires human approval to execute)
  - Registry record count and health score

#### Broken Link Check
- **Trigger:** Every Wednesday at 07:00
- **Owner:** n8n
- **Output:** `reports/weekly/YYYY-WNN-broken-links.md`
- **Contents:**
  - All internal document cross-references
  - External URLs in documentation
  - GitHub issue/PR references
  - Broken link count and severity classification

#### HubSpot / Drive Reconciliation Report
- **Trigger:** Every Thursday at 07:00
- **Owner:** n8n
- **Output:** `reports/weekly/YYYY-WNN-hubspot-drive-reconciliation.md`
- **Contents:**
  - HubSpot contact records vs. Drive client folders — mismatches
  - Deal stage vs. project status alignment
  - Missing documents for active deals
  - Orphaned Drive folders (no matching HubSpot record)
- **Escalation:** Reconciliation writes require human approval

### 2.3 — Per-Sprint Automations

#### Production Readiness Scorecard
- **Trigger:** Sprint close (manual trigger by ChatGPT or human owner)
- **Owner:** ChatGPT
- **Output:** `reports/sprint/sprint-N-readiness-scorecard.md`
- **Contents:**
  - All acceptance criteria: met / not met
  - Test pass rate
  - Documentation completeness
  - Outstanding blockers
  - Go/No-Go recommendation
- **Authority:** Human owner makes final go/no-go decision

---

## Part 3 — Automation Rules

### 3.1 — Logging Requirement
Every automated action must log: timestamp, agent, action type, inputs, output, success/failure. Logs are stored in `reports/` or the system audit trail.

### 3.2 — Idempotency
All automation workflows must be designed to be safely re-run. Running the same workflow twice must not create duplicate records or side effects.

### 3.3 — Failure Handling
On any workflow failure:
1. Log the full error with context
2. Do NOT retry destructive or write operations automatically
3. Alert the human owner
4. Halt dependent downstream workflows
5. Create a GitHub issue labeled `blocked` with the error summary

### 3.4 — Rate Limiting
AI agents must respect API rate limits for all integrated systems (HubSpot, GitHub, Google Drive). Workflows must include appropriate delays and backoff logic.

### 3.5 — Data Isolation
- Staging data is never mixed with production data
- Draft records are clearly marked and isolated
- No production CRM record is written without passing through Gate H

### 3.6 — Secrets Management
All API keys, tokens, and credentials are stored in GitHub Secrets or a designated secrets manager. No credentials are committed to the repository. No AI agent hardcodes credentials.

---

## Part 4 — Integration Map

| System | Read | Draft Write | Production Write | Auth Required |
|---|---|---|---|---|
| HubSpot CRM | ✅ Auto | ✅ Auto (staging) | ❌ Gate H | Yes |
| Google Drive | ✅ Auto | ✅ Auto (AI folders) | ❌ Gate H | Yes |
| GitHub | ✅ Auto | ✅ Auto (features) | ❌ Gate G (main merge) | Yes |
| n8n | ✅ Auto | ✅ Auto (draft workflows) | ❌ Gate P | Yes |
| Registry (05_DB) | ✅ Auto | ✅ Auto | ❌ Gate D (delete) | No |

---

*Governed by HCI_AI_CONSTITUTION.md | Hendrickson Construction, Inc.*

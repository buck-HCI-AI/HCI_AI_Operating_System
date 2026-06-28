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

---

## Part 5 — Full Workflow Inventory (INT-010 — Completed 2026-06-28)

**Audit date:** 2026-06-28 | **Source:** n8n API + Python workflow files
**Totals:** 50 n8n workflows (42 active, 8 inactive/archived) + 18 Python/FastAPI workflows = 68 total

### 5.1 — n8n Workflows (Stack 2)

#### Active (42)

| n8n ID | Name | Schedule/Trigger | Category |
|--------|------|-----------------|----------|
| 1Blqe9p0iWWimdCs | AUTO-001 Daily Repository Status Report | Daily 07:00 | Reporting |
| 1EbteMeNL7WUoq5F | AUTO-002 Workflow Health Check | Daily 06:00 | Health |
| s1m9fvGkS53Ce2Rt | AUTO-003 Sprint Self-Status Report | Manual | Reporting |
| 67n7ENkCpGIzHgc1 | AUTO-004 Daily Mining Engine | Daily 03:00 | Mining |
| FkiYQVre39L9ElCO | AUTO-005 Gate H: HubSpot Write Approval | Webhook | Gate |
| nMjAbRJ3thgKQq2O | AUTO-006 Gate G: PR Merge Notification | Webhook | Gate |
| Blt32qhKBJvox0SR | AUTO-010 Weekly Sprint Review Summary | Weekly | Reporting |
| 3wAvUsdeVJU98ZR4 | AUTO-011 Weekly Registry Duplicate Check | Weekly Tue 07:00 | Validation |
| AtHXWsAfByeYwnO1 | AUTO-012 Weekly Broken Link Check | Weekly Wed 07:00 | Validation |
| AbP7zYz3zOGdb7mA | AUTO-013 HubSpot/Drive Reconciliation Report | Weekly Thu 07:00 | Reconciliation |
| WWv3euSPYehmjkoi | AUTO-017 Gate E: Client Comms Approval | Webhook | Gate |
| 6bDcqZX2ZGUiaKnx | AUTO-018 Gate F: Financial Action Approval | Webhook | Gate |
| whHMnB1l8kTJE5gz | AUTO-019 Morning Brief Email | Daily 07:00 | Reporting |
| nXXrsQ7eo8JuRG2z | AUTO-020 EOD Brief Email | Daily 19:00 | Reporting |
| fmNSNN797HDT5vcA | AUTO-021 Escalation Check | Daily 10:00 & 18:00 | Alerts |
| A9OAkREoqs4Ke0uu | AUTO-AI-DEAL-SUMMARIZATION | Daily | CRM |
| k6n0FNUF8JoNVLth | AUTO-BID-INVITATION-TASKS | HubSpot deal stage trigger | Bids |
| zgtuaysXDeGa7tIY | AUTO-COI-COMPLIANCE-ENGINE | Daily 07:00 | Compliance |
| vylopikjmX2FIKGq | AUTO-DAILY-PROJECT-SUMMARY | Daily | Reporting |
| fI0LGWhdzopkcmrg | AUTO-HANDOFF-PROCESSOR | Every 5 min | Agent Ops |
| VrRq3XdWLS626UYS | AUTO-MONTHLY-REVIEW | 1st of month 09:00 | Reporting |
| XIihPRTFx27A18Vy | AUTO-NIGHTLY-AUDIT | Nightly 02:00 | Audit |
| DhmrAAEhlzKW8Y3i | AUTO-NOTIFY | Event-driven (HIGH/CRITICAL) | Alerts |
| iCTepJbZuzEORs3z | AUTO-PM | Daily 06:00 | PM Ops |
| 9fsVJ2gBOn54fLnT | AUTO-PM-WEEKLY | Monday 07:00 | PM Ops |
| jFzQFu9MybnWtrZd | AUTO-SCHEDULE-VARIANCE-WEEKLY | Weekly Mon 07:00 | Schedule |
| kraZAzvt5p7GNSE7 | AUTO-SS-MORNING | Daily 06:00 | Field Ops |
| xxjxjznM2lHw9ukj | AUTO-WEEKEND | Saturday 08:00 | Reporting |
| oqMYGwlU2wYmf3BJ | AUTO-WEEKLY-COMPANY | Friday 16:30 | Reporting |
| 6GyIgmZUJOh3ae2D | AUTO-WEEKLY-EXEC | Friday 16:00 | Reporting |
| MRu2VM90cURMdk7q | AUTO-WEEKLY-JOB | Friday 16:00 | Reporting |
| 06sPrar8glcwKRKn | AUTO-WEEKLY-REPORT | Sunday 19:00 | Reporting |
| MQ6ZrG6Jv99GwIaA | Bid Receipt Processing v5 | Webhook (email/Drive) | Bids |
| ffDh9C43mK83qgSp | WF-003 Historical Cost Queue | Event-driven | Data |
| 1HbcdWIT0uytLnIf | WF-004 Lessons Learned Engine | Event-driven | Learning |
| xQzzjmHR48otUQOn | WF-005 SOP Registry Sync | Event-driven | SOPs |
| P4fOHS47k2RrkZJn | WF-006 Executive Alerts | Event-driven | Alerts |
| Q1akV9pVnDkmATIo | WF-007 AI Bid Leveling Engine | Webhook | Bids |
| 4UORmVSvQS4PjJ0B | WF-008 Bid Follow-Up Engine | Scheduled | Bids |
| XLtyF4tDTmVRWjoU | WF-009 New Job Setup | Webhook | Projects |
| flsIMOI21JRgtlMe | WF-010 Outlook Email Router | Email webhook | Inbox |
| wOyGdyLNZKdrth9M | WF-011 Site Superintendent Daily Briefing | Daily | Field Ops |

#### Inactive / Archived (8)

| n8n ID | Name | Reason Inactive |
|--------|------|----------------|
| 20dD4J8YUxko5g0U | ARCHIVED — Bid Leveling (merged into WF-007) | Superseded |
| 8xZkUWgxudrbbgCS | ARCHIVED — Bid Receipt Processing v5 (duplicate) | Duplicate of MQ6ZrG6Jv99GwIaA |
| hMIMIUy3fSSVDJcr | ARCHIVED — AUTO-NIGHTLY-AUDIT (duplicate import 2026-06-27) | Duplicate of XIihPRTFx27A18Vy |
| 2iM1eViWnnQ4I2Xv | AUTO-CONTINUOUS-DISCOVERY — HubSpot Hourly + Houzz Nightly | Paused — Houzz data not ready |
| hMIMIUy3fSSVDJcr | AUTO-NIGHTLY-AUDIT (older copy) | Duplicate |
| KUw5KCchqRiWTOvS | HZ-004 Houzz Daily Log Extraction Trigger | Blocked — Houzz DB empty |
| zUcZtUmiZwWUS72X | Inbox Cleanup — Delete Test Emails | One-time use |
| UCav5gp2W3dNYllG | RETIRED — ChatGPT Chrome Bridge (superseded by MCP) | Retired |
| nihv5r68lbt5QjP3 | RETIRED — TMP-cl-84994d (unused Outlook webhook) | Retired |

### 5.2 — Python/FastAPI Workflows (Stack 1)

Located in `03_Source_Code/workflows/` — all active as part of the FastAPI process.

| Workflow ID | Name | Trigger | Module |
|-------------|------|---------|--------|
| WF-001 | New Project Setup | API call / HubSpot webhook | wf_new_project.py |
| WF-002 | Meeting Intelligence | API call | wf_meeting.py |
| WF-003 | Morning Brief | launchd 07:00 daily | wf_morning_brief.py |
| WF-004 | Legacy Field Wrapper | Superseded by WF-SUPER | wf_field.py |
| WF-005 | Lessons Learned | Event-driven | wf_lessons.py |
| WF-006 | Inbox Review | API call | wf_inbox.py |
| WF-SUPER | Superintendent Daily Log | API call / Houzz | wf_superintendent.py |
| WF-PM | PM Daily Review | launchd | wf_pm.py |
| WF-PM-W | PM Weekly Review | Friday trigger | wf_pm_weekly.py |
| WF-REPORT-EXEC | Executive Health Report | Friday trigger | wf_report_exec.py |
| WF-REPORT-OWNER | Owner Summary | Manual | wf_report_owner.py |
| WF-REPORT-FIELD | Daily Field Report | WF-SUPER trigger | wf_report_field.py |
| WF-REPORT-RISK | Procurement Risk Report | Monday trigger | wf_report_risk.py |
| WF-REPORT-SCHED | Schedule Variance Report | On detection | wf_report_schedule.py |
| WF-SYNC-HS | HubSpot Sync | Startup + hourly | wf_sync_hubspot.py |
| WF-SYNC-DRIVE | Drive Sync | Weekly | wf_sync_drive.py |
| WF-SYNC-HOUZZ | Houzz Sync | Daily | wf_sync_houzz.py |
| WF-009 | New Job Data Setup | WF-009 companion | wf_job_setup.py |

---

*Governed by HCI_AI_CONSTITUTION.md | Hendrickson Construction, Inc.*
*INT-010 COMPLETE — 2026-06-28 by Claude Code*

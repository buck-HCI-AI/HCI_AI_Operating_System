# Volume VII — Automation Architecture
*HCI AI Construction Operating System Architecture Handbook*

---

## 7.0 Automation Philosophy
*Authored by: Chief Architect (ChatGPT) — 2026-07-02*

The HCI AI Operating System treats automation as an operational capability, not a centralized control system. No single scheduler is expected to manage every process, monitor every service, or recover every failure. Instead, automation is distributed across specialized components, each responsible for the work it performs best.

Workflow orchestration manages business processes. Background services monitor platform health, synchronization, indexing, and continuous intelligence. Application services execute domain-specific logic. Together, these components create a resilient operating model in which individual failures are isolated, observable, and recoverable without placing the entire platform at risk.

This architecture favors reliability over centralization. Small, purpose-built automation services are easier to understand, test, maintain, and replace than a single orchestration engine responsible for every operational function. As the platform evolves, automation can expand incrementally without requiring fundamental changes to the operating model.

Automation is expected to detect abnormal conditions and recover automatically whenever recovery is deterministic, repeatable, and carries minimal operational risk. Examples include restarting unhealthy services, resuming interrupted synchronization, retrying transient operations, rebuilding derived indexes, and restoring normal platform operation after temporary failures.

Automation is not expected to make business judgments. When recovery requires interpretation, changes project information, creates external commitments, or could conceal an underlying operational problem, the system stops, records the condition, and requests human review. A visible alert is preferable to an invisible mistake. The objective is dependable operation, not autonomous behavior at any cost.

The self-healing boundary reflects this philosophy. Infrastructure may heal itself when returning to a previously known, healthy state — for example, restarting a failed service or container that has already been validated. The platform does not automatically modify business rules, alter project data, rewrite workflows, or change production behavior without explicit human authorization. Restoring operation is fundamentally different from changing intent.

Automation earns expanded authority through demonstrated reliability rather than assumption. Every new capability begins with observation and recommendation. After proving consistent accuracy, appropriate safeguards, and operational value, it may advance to approval-assisted execution. Only after sustained performance, measurable benefit, and organizational confidence should limited autonomous operation be considered, and only for low-risk activities within established governance boundaries.

The objective is not to automate everything. The objective is to automate repetitive work, reduce operational friction, improve system reliability, and allow construction professionals to focus their time on building successful projects. Every expansion of automation must increase trust, reduce workload, and remain fully accountable to the governance model of the HCI AI Operating System.

---

## 7.1 Automation Stack (✅ Implemented)

```
┌─────────────────────────────────────────────────────┐
│  n8n (port 5678) — Workflow Orchestration           │
│  55 active / 63 total workflows (2026-06-29)        │
├─────────────────────────────────────────────────────┤
│  FastAPI (port 8000) — Intelligence API             │
│  Managed by launchd (com.hci.api-server)            │
├─────────────────────────────────────────────────────┤
│  FastMCP (port 8080) — MCP Server                   │
│  Managed by launchd (com.hci.mcp-server)            │
│  Proxied via FastAPI at /mcp                        │
├─────────────────────────────────────────────────────┤
│  PostgreSQL (hci_postgres docker) — Data Layer      │
│  50+ tables, 17 migrations applied (2026-06-29)     │
├─────────────────────────────────────────────────────┤
│  Redis — Caching Layer                              │
│  TTL-based response caching                         │
├─────────────────────────────────────────────────────┤
│  Qdrant — Vector Search                             │
│  Document + lesson retrieval                        │
├─────────────────────────────────────────────────────┤
│  MinIO — Object Storage                             │
│  Document + file storage                            │
└─────────────────────────────────────────────────────┘
```

---

## 7.2 n8n Workflows (✅ Active)

*Auto-generated from live n8n state by `POST /architecture-sync/refresh-automation-library` — 2026-07-08T00:33:45.676393+00:00. Do not hand-edit this table; it will be overwritten on the next refresh.*

**56 active, 12 inactive/archived, 68 total.**

### Automation Schedule

| Workflow | Trigger |
|----------|---------|
| AI Model Auto-Updater (Weekly) | unknown |
| AUTO-001 Daily Repository Status Report | cron `0 7 * * *` |
| AUTO-002 Workflow Health Check | cron `0 6 * * *` |
| AUTO-003 Sprint Self-Status Report | cron `0 8 * * *` |
| AUTO-004 Daily Mining Engine (03:00) | cron `0 3 * * *` |
| AUTO-005 Gate H: HubSpot Write Approval | webhook (event-driven) |
| AUTO-006 Gate G: PR Merge Notification | webhook (event-driven) |
| AUTO-010 — Monday 07:00 Weekly Sprint Review | cron `0 7 * * 1` |
| AUTO-011 — Monday 07:30 Registry Duplicate Check | cron `30 7 * * 1` |
| AUTO-012 — Monday 08:00 Broken Link Check | cron `0 8 * * 1` |
| AUTO-013 — Monday 08:30 HubSpot/Drive Reconciliation | cron `30 8 * * 1` |
| AUTO-017 Gate E: Client Comms Approval | webhook (event-driven) |
| AUTO-018 Gate F: Financial Action Approval | webhook (event-driven) |
| AUTO-019 Morning Brief Email (07:00) | cron `0 7 * * *` |
| AUTO-020 EOD Brief Email (19:00) | cron `0 19 * * *` |
| AUTO-021 Escalation Check (10:00 & 18:00) | cron `0 10 * * *` |
| AUTO-AGENT-CHECKIN — 30min Team Backlog Ping | unknown |
| AUTO-AI-DEAL-SUMMARIZATION — Daily Active Deal Briefings via Claude API | cron `0 6 * * 1-5` |
| AUTO-BID-INVITATION-TASKS — Sent Out Stage → Auto-Task Creation | cron `0 8,12,16 * * 1-5` |
| AUTO-COI-COMPLIANCE-ENGINE — Daily 07:00 COI Status Refresh | cron `0 7 * * *` |
| AUTO-CONTINUOUS-DISCOVERY — HubSpot Hourly + Houzz Nightly | cron `0 * * * *` |
| AUTO-DAILY-PROJECT-SUMMARY | unknown |
| AUTO-DRIFT-CHECK — Weekly System Reality Check | cron `0 7 * * 1` |
| AUTO-EMAIL-NOISE-PURGE — Weekly System Noise Cleanup | cron `0 6 * * 0` |
| AUTO-EVENT-DRIVE-SCAN — 15-min Shared Drive New File Watcher | unknown |
| AUTO-EVENT-HEALTH-CHECK — 30-min Project Health Poll | unknown |
| AUTO-HANDOFF-PROCESSOR | unknown |
| AUTO-HOUZZ-REMINDER — Daily 07:15 Manual Extraction Prompt | cron `0 7 * * *` |
| AUTO-MONTHLY-REVIEW — 1st of Month 09:00 Business Review | cron `0 9 1 * *` |
| AUTO-NIGHTLY-AUDIT | unknown |
| AUTO-NOTIFY — Urgent Alert Push (HIGH/CRITICAL events) | cron `0 */4 * * *` |
| AUTO-PILOT-WEEKLY — Monday 07:30 Gate5 Digest | cron (legacy node) |
| AUTO-PM — Daily 06:00 AI Program Manager Review | cron `0 6 * * *` |
| AUTO-PM-WEEKLY — Monday 07:00 PM Console Push | cron `0 7 * * 1` |
| AUTO-SCHEDULE-VARIANCE-WEEKLY | cron `0 7 * * 1` |
| AUTO-SELFHEAL — 15min n8n Health Check | unknown |
| AUTO-SS-MORNING — Daily 06:00 SS Console Push | cron `0 6 * * 1-5` |
| AUTO-WEEKEND — Saturday 08:00 Weekly Summary Email | cron `0 8 * * 6` |
| AUTO-WEEKLY-COMPANY — Friday 16:30 Company Report | cron `30 16 * * 5` |
| AUTO-WEEKLY-EXEC — Friday 16:00 Executive Report | cron `0 16 * * 5` |
| AUTO-WEEKLY-JOB — Friday 16:00 Job Reports | cron `0 16 * * 5` |
| AUTO-WEEKLY-REPORT — Sunday 19:00 Autonomy Opportunities | cron `0 19 * * 0` |
| Bid Receipt Processing v5 | email arrival |
| GATE-E — Client Comms Approval (AUTO-017) | webhook (event-driven) |
| GATE-F — Financial Action Approval (AUTO-018) | webhook (event-driven) |
| GATE-G — PR Merge Notification to Buck (AUTO-006) | webhook (event-driven) |
| GATE-H — HubSpot Write Approval (AUTO-005) | webhook (event-driven) |
| WF-003 Historical Cost Queue | unknown |
| WF-004 Lessons Learned Engine | unknown |
| WF-005 SOP Registry Sync | cron `0 6 * * *` |
| WF-006 Executive Alerts | cron `0 7 * * *` |
| WF-007 AI Bid Leveling Engine | webhook (event-driven) |
| WF-008 Bid Follow-Up Engine | cron `0 8 * * *` |
| WF-009 New Job Setup | webhook (event-driven) |
| WF-010 Outlook Email Router | email arrival |
| WF-011 Site Superintendent Daily Briefing | webhook (event-driven) |

### Inactive / Archived

| Workflow |
|----------|
| ARCHIVED — AUTO-NIGHTLY-AUDIT (duplicate import 2026-06-27) |
| ARCHIVED — Bid Leveling (merged into WF-007) |
| ARCHIVED — Bid Receipt Processing v5 (duplicate) |
| AUTO-010 Weekly Sprint Review Summary |
| AUTO-011 Weekly Registry Duplicate Check |
| AUTO-012 Weekly Broken Link Check |
| AUTO-013 HubSpot/Drive Reconciliation Report |
| AUTO-EOD — Daily End-of-Day Email (19:00) |
| HZ-004 Houzz Daily Log Extraction Trigger |
| Inbox Cleanup — Delete Test Emails |
| RETIRED — ChatGPT Chrome Bridge (superseded by MCP) |
| RETIRED — TMP-cl-84994d (unused Outlook webhook) |


## 7.3 Connectors (✅ Partial)

### n8n Credentials Configured

| Credential | Type | Status |
|-----------|------|--------|
| HubSpot Private App | httpHeaderAuth | ✅ Connected |
| OpenAI account | openAiApi | ✅ Connected |
| Google Drive account | googleDriveOAuth2Api | ✅ Connected (OAuth) |
| Google Sheets account | googleSheetsOAuth2Api | ✅ Connected (OAuth) |
| Microsoft Outlook account | microsoftOutlookOAuth2Api | ✅ Connected (OAuth) |

### Connector Sync State

Table: `connector_sync_state` — tracks last sync per connector+entity_type
Table: `integration_registry` — catalog of all integrations

### Known Limitation — HubSpot Email Content Scope (confirmed 2026-07-06/07)

HubSpot's `crm.objects.emails.read` / `crm.schemas.emails.read` scopes are **not
offered as selectable options** on this account's Sales Hub tier at all — confirmed
by two independent investigations. Requesting `sales-email-read` alone still
returns "content has been redacted... app must require the sales-email-read scope"
on both the modern CRM v3 API and the legacy Engagements API. Confirmed via
`account-info/v3/details` showing `accountType: STANDARD`. **This is a genuine
subscription-tier limitation, not a Private App configuration issue** — do not
spend time re-debugging the scopes themselves; the fix (if wanted) is a HubSpot
plan upgrade, a business decision for Buck, not a code fix.

---

## 7.4 Background Services (✅ Implemented)

### launchd Services (macOS)

| Service | Port | Plist | Purpose |
|---------|------|-------|---------|
| com.hci.api-server | 8000 | ~/Library/LaunchAgents/ | FastAPI main API |
| com.hci.mcp-server | 8080 | ~/Library/LaunchAgents/ | FastMCP server |
| com.hci.n8n | 5678 | ~/Library/LaunchAgents/ | n8n workflow engine |

### Background Learning Service
- `services/background_learning/` — processes documents from Drive/Outlook
- Records stored in `background_learning_records` table
- Status: Discovered → Processing → Complete

### Mining Service
- `services/mining/` — periodic data extraction miners
- Logs in `mining_runs` table
- Miners: document intelligence, HubSpot contacts, etc.

---

## 7.5 Error Handling + Retry (✅ Partial)

### API Error Strategy
- All service endpoints wrap queries in try/except
- Persistence operations (snapshot writes) are best-effort — never crash the main response
- HTTP 404 for unknown projects, 400 for invalid params, 500 logged to stderr

### n8n Retry Strategy
- Default: 3 retries with exponential backoff on HTTP errors
- ntfy failures: non-critical, logged only

---

## 7.6 Sections Requiring Chief Architect Input (⚠️)

### 7.6.1 Self-Healing Architecture
*Authored by: Chief Architect (ChatGPT) — 2026-07-02*

Self-healing architecture exists to maintain platform availability by automatically restoring known-good operational states without altering business intent. The HCI AI Operating System distinguishes infrastructure recovery from business decision-making, and this boundary is fundamental to the platform's governance model.

Infrastructure failures that can be safely and deterministically corrected may be recovered automatically. Examples include restarting failed services, restoring container availability, retrying interrupted synchronization, rebuilding temporary indexes, or recovering communication between system components after transient failures.

Self-healing never extends to business information, project records, financial data, approvals, schedules, contracts, or operational workflows. The platform does not modify project data, infer missing business decisions, or rewrite operational history in an attempt to recover from failure. When uncertainty exists, the system preserves evidence, records the condition, and requests human review.

The objective is resilient operation without compromising accountability. Infrastructure may restore itself; business authority always remains with people.

### 7.6.2 Continuous Monitoring Philosophy
*Authored by: Chief Architect (ChatGPT) — 2026-07-02*

Continuous monitoring provides the operational awareness required to maintain a dependable construction intelligence platform. Monitoring is not limited to server availability; it extends across every component whose failure could reduce confidence in project information or system operation.

The platform continuously observes service health, workflow execution, synchronization status, approval queues, scheduled automation, data freshness, integration connectivity, security events, intelligence generation, and operational performance. Monitoring verifies that information continues to flow correctly from source systems to decision-support capabilities.

Certain conditions are non-negotiable and require immediate visibility. Loss of platform availability, failed synchronization, repeated workflow failures, approval bottlenecks, degraded intelligence generation, authentication failures, and persistent integration errors must always be detected, recorded, and surfaced for corrective action.

The objective is not to eliminate failure but to eliminate unnoticed failure. Reliable systems acknowledge problems quickly, preserve operational context, and enable rapid recovery before project operations are affected.

### 7.6.3 Workflow Orchestration Model
*Authored by: Chief Architect (ChatGPT) — 2026-07-02*

Workflow orchestration coordinates operational processes that span multiple systems, users, and stages of execution. It provides predictable movement of information while preserving governance, traceability, and human authority.

Each workflow should perform a single operational objective through clearly defined stages with explicit inputs, outputs, ownership, and completion criteria. Complex business processes are composed from smaller, understandable workflows rather than monolithic automation that is difficult to maintain or validate.

Approval boundaries are designed into workflows rather than added afterward. Automated stages complete deterministic work. Approval stages pause execution until authorized personnel review the proposed action. Human-only stages remain entirely outside automation where professional judgment, contractual authority, or organizational responsibility is required.

Every workflow should be observable, recoverable, and auditable. Execution history, decision points, retries, approvals, failures, and completion status become part of the permanent operational record. Workflows therefore function not only as automation but also as documentation of how the organization consistently executes its construction processes.

The objective is dependable operational coordination through modular, governed automation that can evolve over time without sacrificing transparency or organizational control.

---

*Ref: [architecture/SYSTEM_AUDITOR_SPEC.md](../architecture/SYSTEM_AUDITOR_SPEC.md)*

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

### Automation Schedule

| Workflow | Trigger | Action | Status |
|----------|---------|--------|--------|
| AUTO-SS-MORNING | Mon-Fri 06:00 | SS console → ntfy push | ✅ Active |
| AUTO-PM-WEEKLY | Monday 07:00 | PM console → ntfy push | ✅ Active |
| AUTO-PM | Daily 06:00 | AI Program Manager review | ✅ Active |
| AUTO-WEEKLY-JOB | Friday 16:00 | Job reports → ntfy + disk | ✅ Active |
| AUTO-WEEKLY-COMPANY | Friday 16:30 | Company report → ntfy + disk | ✅ Active |
| AUTO-WEEKLY-EXEC | Friday 16:00 | Executive report (BTW-6) | ✅ Active |
| AUTO-MONTHLY-REVIEW | 1st of month 09:00 | Business review (BTW-6) | ✅ Active |
| AUTO-NIGHTLY-AUDIT | Nightly 02:00 | System audit → ntfy | ✅ Active |
| AUTO-WEEKEND | Weekend 08:00 | Weekend summary → Outlook | ✅ Active |
| AUTO-DAILY-PROJECT-SUMMARY | Daily | Per-project AI summaries (BTW-4) | ✅ Active |
| AUTO-019 MORNING BRIEF | Daily 07:00 | Morning brief email | ✅ Active |
| AUTO-020 EOD BRIEF | Daily 19:00 | End-of-day email | ✅ Active |
| AUTO-CONTINUOUS-DISCOVERY | Hourly/Nightly | HubSpot+Houzz change detection (BTW-10) | ✅ Active |
| AUTO-EVENT-HEALTH-CHECK | Every 30 min | Project health severity crossing detection | ✅ Active |
| AUTO-EVENT-DRIVE-SCAN | Every 15 min | Shared drive new PDF detection | ✅ Active |
| AUTO-COI-COMPLIANCE | Daily 07:00 | COI status refresh | ✅ Active |
| AUTO-SCHEDULE-VARIANCE | Weekly | Schedule variance analysis | ✅ Active |
| AUTO-PILOT-WEEKLY | Monday 07:30 | Gate5 pilot digest | ✅ Active |
| WF-006 Executive Alerts | Event-driven | Cross-threshold risk alerts | ✅ Active |
| WF-011 SS Daily Briefing | Daily 06:00 | Field superintendent daily brief | ✅ Active |
| AUTO-EOD Email | Daily 19:00 | EOD email (⚠️ needs Gmail OAuth — Buck to configure) | ❌ Inactive |

### Gate Workflows (Approval Pattern)
| Workflow | Trigger | Action |
|----------|---------|--------|
| GATE-H | Webhook | HubSpot write-back gate |
| GATE-G | GitHub | GitHub webhook → approval |
| GATE-E | Webhook | Email action gate |
| GATE-F | Webhook | File operation gate |

### Workflow File Structure

```
03_Source_Code/workflows/n8n/
├── AUTO-SS-MORNING.json      ← Superintendent morning push
├── AUTO-PM-WEEKLY.json       ← PM weekly push
├── AUTO-WEEKLY-JOB.json      ← Friday job reports
├── AUTO-WEEKLY-COMPANY.json  ← Friday company report
├── AUTO-NIGHTLY-AUDIT.json   ← Nightly system audit
├── AUTO-WEEKEND.json         ← Weekend summary (Outlook)
├── AUTO-010.json
├── AUTO-011.json
├── AUTO-012.json
├── AUTO-013.json
├── GATE-H.json
├── GATE-G.json
├── GATE-E.json
└── GATE-F.json
```

---

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

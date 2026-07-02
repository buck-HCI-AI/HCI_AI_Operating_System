# Volume VII — Automation Architecture
*HCI AI Construction Operating System Architecture Handbook*

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
*[Chief Architect: Define how the system should detect and recover from failures automatically]*

### 7.6.2 Continuous Monitoring Philosophy
*[Chief Architect: What should the system always be watching? What triggers are non-negotiable?]*

### 7.6.3 Workflow Orchestration Model
*[Chief Architect: How should complex multi-step workflows be designed and governed?]*

---

*Ref: [architecture/SYSTEM_AUDITOR_SPEC.md](../architecture/SYSTEM_AUDITOR_SPEC.md)*

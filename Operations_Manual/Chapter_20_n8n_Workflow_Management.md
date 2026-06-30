# Chapter 20 — n8n Workflow Management
*HCI AI Operations Manual — Part II: AI System Operations*
**Author:** Claude Code | **Version:** 1.0 | **Date:** 2026-06-30

---

## 20.1 What n8n Does

n8n is the automation engine. It's the thing that wakes up at 06:00 and sends Jim's morning brief. It's the thing that checks project health every 30 minutes. It's the thing that reads HubSpot every hour. Every scheduled task in the HCI AI OS goes through n8n.

**n8n runs at:** `http://localhost:5678`
**Login:** Configured on first install (credentials in .env)
**Workflows directory:** `03_Source_Code/workflows/n8n/`

---

## 20.2 Active Workflow Registry

**Total: 55 active / 63 total workflows**

### Daily Operations Workflows

| Workflow ID | Name | Schedule | What It Does |
|-------------|------|---------|-------------|
| AUTO-001 | Daily Repository Status Report | 07:00 daily | Status report to Git/reports |
| AUTO-002 | Workflow Health Check | 06:00 daily | All services health → log |
| AUTO-003 | Sprint Self-Status | 08:00 daily | Sprint status report |
| AUTO-004 | Mining Engine | 03:00 daily | Runs all 8 miners (HubSpot, Drive, Houzz…) |
| AUTO-SS-MORNING | SS Morning Console | Mon-Fri 06:00 | Jim's field brief → ntfy push |
| AUTO-PM | AI Program Manager | Daily 06:00 | Program manager review all projects |
| AUTO-019 MORNING BRIEF | Morning Brief Email | 07:00 daily | Morning brief → Outlook email to Buck |
| AUTO-020 EOD BRIEF | End-of-Day Email | 19:00 daily | EOD summary → Outlook (⚠️ needs Gmail OAuth) |
| AUTO-DAILY-PROJECT-SUMMARY | Daily Project Summaries | Daily | Per-project AI summaries (BTW-4) |

### Weekly Workflows

| Workflow ID | Name | Schedule | What It Does |
|-------------|------|---------|-------------|
| AUTO-PM-WEEKLY | PM Weekly Push | Monday 07:00 | PM weekly console → ntfy |
| AUTO-PILOT-WEEKLY | Gate 5 Pilot Digest | Monday 07:30 | Pilot weekly → ntfy |
| AUTO-WEEKLY-JOB | Weekly Job Reports | Friday 16:00 | Per-project job reports → ntfy + disk |
| AUTO-WEEKLY-COMPANY | Company Weekly Report | Friday 16:30 | Company-wide report → ntfy + disk |
| AUTO-WEEKLY-EXEC | Executive Report | Friday 16:00 | Executive report (BTW-6) |

### Monthly Workflows

| Workflow ID | Name | Schedule | What It Does |
|-------------|------|---------|-------------|
| AUTO-MONTHLY-REVIEW | Business Review | 1st of month 09:00 | Monthly business review (BTW-6) |

### Event-Driven Workflows

| Workflow ID | Name | Trigger | What It Does |
|-------------|------|---------|-------------|
| AUTO-EVENT-HEALTH-CHECK | Project Health Check | Every 30 min | Severity crossing detection → ntfy on change |
| AUTO-EVENT-DRIVE-SCAN | Drive PDF Scan | Every 15 min | New PDFs → learning queue |
| AUTO-COI-COMPLIANCE | COI Status Refresh | Daily 07:00 | Vendor COI compliance check |
| AUTO-SCHEDULE-VARIANCE | Schedule Variance | Weekly | Schedule variance analysis |
| AUTO-CONTINUOUS-DISCOVERY | Continuous Discovery | Hourly/Nightly | HubSpot (hourly) + Houzz (nightly) change detection (BTW-10) |
| AUTO-NIGHTLY-AUDIT | Nightly Audit | 02:00 daily | Full system audit → ntfy if issues |
| AUTO-WEEKEND | Weekend Summary | Weekend 08:00 | Weekend summary → Outlook |
| WF-006 | Executive Alerts | Event-driven | Cross-threshold risk alerts |
| WF-011 | SS Daily Briefing | Daily 06:00 | Field superintendent daily brief |

### Gate Workflows (Approval Gates)

| Workflow | Trigger | Action |
|----------|---------|--------|
| GATE-H | Webhook POST | HubSpot write-back approval gate |
| GATE-G | GitHub webhook | GitHub push approval gate |
| GATE-E | Webhook POST | External email approval gate |
| GATE-F | Webhook POST | File operation approval gate |

---

## 20.3 Managing Workflows in the n8n UI

**Access:** Open browser → `http://localhost:5678`

### Checking Workflow Health
1. Go to Workflows list
2. Verify all 55 workflows show "Active" (green toggle)
3. Click any workflow → Executions tab → verify last run succeeded

### Viewing Execution History
```
n8n UI → Workflow → Executions tab → Click any execution
```
Shows: start time, duration, status (Success/Error), step-by-step output

### Activating a Workflow
Toggle the blue Active switch in the workflow list. If a workflow is inactive and should be active, click it to turn it on.

### Pausing a Workflow
Click the Active toggle to deactivate. The workflow will not fire until reactivated.

---

## 20.4 n8n via API (for Claude Code)

```bash
N8N_API_KEY=$(grep N8N_API_KEY /Users/buckadams/HCI_AI_Operating_System/.env | cut -d= -f2)

# List all workflows
curl -s "http://localhost:5678/api/v1/workflows" \
  -H "X-N8N-API-KEY: $N8N_API_KEY" | \
  python3 -c "import json,sys; d=json.load(sys.stdin); print(f'Total: {len(d[\"data\"])}, Active: {len([w for w in d[\"data\"] if w[\"active\"]])}')"

# Manually trigger a workflow (by ID)
curl -X POST "http://localhost:5678/api/v1/workflows/{ID}/activate" \
  -H "X-N8N-API-KEY: $N8N_API_KEY"

# Get workflow executions
curl -s "http://localhost:5678/api/v1/executions?workflowId={ID}&limit=5" \
  -H "X-N8N-API-KEY: $N8N_API_KEY"
```

---

## 20.5 Known Issues & Workarounds

### AUTO-EOD Email (Gmail OAuth2 — Inactive)
**Status:** ❌ INACTIVE  
**Why:** Needs Gmail OAuth2 credential configured in n8n  
**Fix:** Buck must go to n8n → Settings → Credentials → Add Gmail OAuth2 → re-activate workflow  
**Impact:** End-of-day email is not sending until fixed  
**Workaround:** EOD summary still posted to ntfy at 19:00 via separate workflow  

### Workflow Not Triggering
1. Check the workflow is Active (green toggle)
2. Check n8n is running: `curl -s http://localhost:5678/api/v1/workflows` should return JSON
3. If n8n is down: `docker-compose up -d n8n` 
4. Check execution history for error details

### API Connection Errors in Workflows
n8n workflows call the API at `http://localhost:8000`. If the API is down, workflows will fail.
- Restart API: `launchctl stop com.hci.api-server && launchctl start com.hci.api-server`
- n8n will retry on next scheduled run

### Adding New Workflows
1. Build in n8n UI
2. Export: Workflow → ⋮ → Export → JSON
3. Save to `03_Source_Code/workflows/n8n/{WORKFLOW_NAME}.json`
4. Update this chapter's registry
5. Update Volume VII Automation Architecture Handbook

---

## 20.6 Workflow Authentication

**Credentials configured in n8n (Settings → Credentials):**

| Credential Name | Type | Used By |
|----------------|------|---------|
| HubSpot Private App | httpHeaderAuth | Mining, Sync workflows |
| OpenAI account | openAiApi | AI-assisted workflows |
| Google Drive account | googleDriveOAuth2Api | Drive scan, upload workflows |
| Google Sheets account | googleSheetsOAuth2Api | Bid tracker workflows |
| Microsoft Outlook account | microsoftOutlookOAuth2Api | Email workflows |

**N8N_API_KEY:** Stored in `.env` as `N8N_API_KEY`. This is a JWT — do not share or commit.

---

## 20.7 Workflow File Structure

```
03_Source_Code/workflows/n8n/
├── AUTO-SS-MORNING.json       ← Superintendent morning push
├── AUTO-PM-WEEKLY.json        ← PM weekly push  
├── AUTO-WEEKLY-JOB.json       ← Friday job reports
├── AUTO-WEEKLY-COMPANY.json   ← Friday company report
├── AUTO-NIGHTLY-AUDIT.json    ← Nightly system audit
├── AUTO-WEEKEND.json          ← Weekend summary
├── AUTO-010.json through AUTO-013.json
├── GATE-H.json                ← HubSpot approval gate
├── GATE-G.json                ← GitHub approval gate
├── GATE-E.json                ← Email approval gate
└── GATE-F.json                ← File operation gate
```

Always export workflows from n8n and save here. This is the backup if n8n needs to be rebuilt.

---

*Cross-reference: Chapter 17 (Architecture), Chapter 21 (Integrations), Chapter 25 (Troubleshooting)*

# GBT Gateway Usage Guide
**For: ChatGPT / Chief Architect**
**From: Claude Code / Lead Implementation Engineer**
**Date: 2026-06-28**

You now have a live HTTPS gateway into the HCI AI Operating System. You no longer need Buck to relay state. You can read live project data, check system health, and send implementation tasks directly to Claude Code — all via standard HTTP calls.

---

## Your Connection

```
Base URL:  https://speculate-armband-retinal.ngrok-free.dev
API Key:   hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6
           (required on write endpoints only — all reads are open)
```

Every response comes back in this envelope:
```json
{
  "status": "ok",
  "timestamp": "2026-06-28T...",
  "execution_time_ms": 76,
  "source_system": "hci-api",
  "payload": { ... },
  "warnings": [],
  "errors": []
}
```

---

## Start Here — Verify You're Connected

```
GET https://speculate-armband-retinal.ngrok-free.dev/gateway/health
```
If you get `"status": "ok"` and `"hci_api_reachable": true`, you're in. That's all you need to confirm the OS is live.

---

## Reading System State

### Full live system state (read this first in any session)
```
GET /gateway/project-state
```
Returns the full `LIVE_PROJECT_STATE.md` — service health, active projects, sprint status, team state, open items.

### Morning brief across all projects
```
GET /gateway/executive/report
```
Returns health, risks, schedule status, and open actions for 64 Eastwood, 101 Francis, and 1355 Riverside.

### All KPIs at once
```
GET /gateway/executive/mission-control
```

---

## Reading Project Data

Replace `{code}` with: `64EW`, `101F`, or `1355R`

| What you want | Call |
|---|---|
| Project brain snapshot | `GET /gateway/project/{code}/brain` |
| Schedule status + variance | `GET /gateway/project/{code}/schedule` |
| PM console — health, risks, actions | `GET /gateway/project/{code}/pm` |
| Bid packages + procurement | `GET /gateway/project/{code}/bids` |

Example:
```
GET /gateway/project/64EW/brain
GET /gateway/project/101F/schedule
GET /gateway/project/1355R/pm
```

---

## Searching Knowledge

### Vendor lookup (cross-project)
```
GET /gateway/knowledge/vendor?name=Peterson+Electric
```

### Similar issues / lessons learned
```
GET /gateway/knowledge/issues?q=concrete+delay
```

### Search Google Drive
```
GET /gateway/drive/search?q=1355+Riverside+schedule
```

---

## Sending Tasks to Claude Code

This is how you assign implementation work without going through Buck.

```http
POST /gateway/agent/handoff
X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6
Content-Type: application/json

{
  "title": "Short title — what needs to be built",
  "body": "Full description: what to build, why, decisions already made, constraints",
  "priority": "high",
  "source": "chief_architect",
  "sop_references": ["SOP-14", "BP-15"],
  "acr_number": "ACR-005"
}
```

The gateway writes your request to the Agent Handoff Inbox. Claude Code reads it at the start of every session and executes before taking other work.

**Response tells you the file was queued:**
```json
{
  "payload": {
    "queued": true,
    "filename": "GBT_HANDOFF_2026-06-28_..._abc123.md",
    "request_id": "abc123"
  }
}
```

---

## What to Put in the Handoff Body

Claude Code needs enough context to implement without asking Buck. Include:

- **What:** The specific artifact to build (endpoint, workflow, table, document)
- **Why:** The business rule or SOP it implements
- **Decisions already made:** Any architecture choices you've already resolved
- **Constraints:** Approval gates required, fields that must not be exposed, tables involved
- **SOP reference:** Which BP-XX or SOP-XX this satisfies

Claude Code will flag back if it needs a Buck decision before proceeding.

---

## What Claude Code Will NOT Act On Without Buck

Even if you send it via handoff, Claude Code will pause and wait for Buck's approval on:

- HubSpot writes (any contact, deal, or company update)
- External email sends
- Contract or financial commitments
- Deleting or overwriting production data
- Go-live on any client-facing feature

These are Buck's authority. The handoff will be queued but not executed until Buck approves.

---

## Division of Authority

| You (GBT) | Claude Code | Buck Adams |
|---|---|---|
| Architecture decisions | Implementation | Business decisions |
| Schema design | SQL / code | External commitments |
| API specification | API build | Award/contract approval |
| Workflow design | n8n build | HubSpot writes |
| SOP compliance review | SOP auditing | Final authority on everything |

---

## Fallback — If the Gateway Is Down

The ngrok tunnel requires the local Mac to be running. If you get a connection error:

1. Read system state from Google Drive:
   `https://drive.google.com/file/d/1Jjug6nbx-mGN9v4GrEyofkGXY5nMHvpP/view`

2. Read latest code and docs from GitHub:
   `https://raw.githubusercontent.com/buck-HCI-AI/HCI_AI_Operating_System/main/LIVE_PROJECT_STATE.md`

3. Tell Buck the gateway is down — he restarts ngrok with one command.

---

## What's Live Right Now (2026-06-28)

| System | Status |
|---|---|
| FastAPI (427 endpoints, 18 services) | 🟢 LIVE |
| PostgreSQL (47 tables, 995 schedule items) | 🟢 LIVE |
| n8n (44 active workflows) | 🟢 LIVE |
| Schedule Intelligence — all 3 Gate 5 projects | 🟢 LIVE |
| SOP Compliance Map | 🟢 NEW — see `AI_TEAM/SOP_WORKFLOW_COMPLIANCE_MAP.md` |
| Architecture Freeze v1.0 | 🔴 NOT YET — this is the next milestone |

---

## Your Next Action (Per Your Original Directive)

Your directive from the beginning said the next milestone is **Architecture Freeze v1.0** — not more APIs.

The SOP Compliance Matrix is done (commissioned by you, delivered today).
The AI Team Charter / Handoff Protocol is drafted.
The Gateway Bridge is live.

What remains before Architecture Freeze v1.0:
1. Ratify the `AI_TEAM/GBT_CLAUDE_HANDOFF_PROTOCOL.md` via handoff
2. Define Architecture Freeze criteria — what must be true before we declare v1.0
3. Reconcile the Architecture Handbook against what's actually built

Send a handoff when ready. Claude Code is standing by.

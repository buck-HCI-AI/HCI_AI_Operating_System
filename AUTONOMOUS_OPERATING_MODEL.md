# Autonomous Operating Model
## HCI AI Operating System — How the System Runs Without Buck

**Authority:** Chief Architect Directive — Automation First (2026-06-27)  
**Owner:** Buck Adams  
**Version:** 1.0

---

## Design Principle

> "Buck should be able to step away. The system continues safely, reports status, and only asks Buck for true owner approvals."

This document defines how the HCI AI OS operates autonomously — what runs, when, what it produces, and what it does not touch without explicit authorization.

---

## The Autonomous Stack

```
         ┌─────────────────────────────────────────────┐
         │              BUCK'S VIEW                     │
         │  EXECUTIVE_INBOX.md (morning read — 5 min)  │
         │  Approve / Reject / Defer / Done             │
         └──────────────────────────────────────────────┘
                           ↑ surfaces only
         ┌─────────────────────────────────────────────┐
         │          AI PROGRAM MANAGER LAYER            │
         │  MISSION_QUEUE.md (active work tracking)    │
         │  EVENT_BUS_ARCHITECTURE.md (coordination)   │
         │  AI_TEAM/06_NEXT_SESSION.md (handoffs)      │
         └──────────────────────────────────────────────┘
                    ↑ reads / writes                    
         ┌─────────────────────────────────────────────┐
         │            EXECUTION LAYER                   │
         │  Claude Code     — builds, fixes, scripts   │
         │  Browser Claude  — extracts, governs GitHub │
         │  Mining Engine   — scans, learns, queues    │
         │  n8n Workflows   — schedules, gates, alerts │
         └──────────────────────────────────────────────┘
                    ↓ writes to                        
         ┌─────────────────────────────────────────────┐
         │            DATA LAYER                        │
         │  PostgreSQL — 47 tables, all project data   │
         │  Qdrant — 13 vector collections             │
         │  Redis — cache + session state              │
         │  Google Drive — documents + bid files       │
         │  HubSpot CRM — deals, contacts, companies   │
         └──────────────────────────────────────────────┘
```

---

## Daily Autonomous Operations

### What Happens Every Day (No Buck Action)

| Time | What | Who | Output | Buck Sees |
|---|---|---|---|---|
| 03:00 | Full mining sweep (8 miners) | Mining Engine | Intelligence, queue items | Summary in inbox if new items |
| 06:00 | Infrastructure health check | n8n AUTO-002 | Health report | Alert only if service DOWN |
| 07:00 | Daily status report | n8n AUTO-001 | `reports/daily/` | Command Center report |
| 07:00 | Executive Inbox refresh | Script | `EXECUTIVE_INBOX.md` | Today's decisions |
| 08:00 | Sprint self-status | n8n AUTO-003 | Sprint progress | Only if blockers |

### What Happens Every Week (No Buck Action)

| Day/Time | What | Who |
|---|---|---|
| Mon 07:00 | Sprint review summary | n8n AUTO-010 |
| Mon 07:30 | Registry duplicate check | n8n AUTO-011 |
| Mon 08:00 | Broken link check | n8n AUTO-012 |
| Mon 08:30 | HubSpot/Drive reconciliation | n8n AUTO-013 |

---

## What Agents Do Autonomously

### Claude Code
- Builds and deploys new API endpoints
- Executes database schema migrations
- Creates and updates documentation
- Rotates API keys and security fixes
- Runs mining engine scripts (dry_run by default)
- Updates LIVE_PROJECT_STATE.md, TASKS.md, CURRENT_SPRINT.md
- Commits to git (local only — push requires authorization)

### Browser Claude
- Extracts data from Houzz, HubSpot, Google Drive (read-only)
- Posts extracted data to ingestion endpoints
- Governs GitHub repo files
- Maintains AI_TEAM/ documentation
- Reports in AI_TEAM/06_NEXT_SESSION.md

### Mining Engine (8 Miners, 03:00 daily)
- Scans all connected systems
- Extracts intelligence
- Queues approval items
- Builds vendor intelligence
- Updates background learning records
- **Never writes to HubSpot, Outlook, or Drive without approval**

### n8n
- Runs all scheduled workflows
- Generates daily/weekly reports
- Routes approval items to queue
- Sends gate notifications

---

## What Requires Buck's Approval (Hard Gates)

These NEVER happen automatically, regardless of any directive:

| Gate | Action | Why |
|---|---|---|
| Gate H | HubSpot write | Client data integrity |
| Gate E | Client email or communication | External commitment |
| Gate F | Financial action (award, invoice, budget) | Financial authority |
| Gate G | Merge to main GitHub branch | Code governance |
| Go-Live | Enable production mining writes | System integrity |
| Contracts | Any contract or award approval | Legal commitment |

---

## What Happens When Buck Is Away

**Day 1:**
- Mining engine ran at 03:00 — queue updated
- Health check ran at 06:00 — all green
- Command Center report generated at 07:00
- Executive Inbox updated

**Day 2:**
- Same as Day 1, automatically
- Agents handle routine work from MISSION_QUEUE.md
- Any blockers added to AI_TEAM/07_BLOCKERS.md

**Day 3+:**
- System continues operating
- Intelligence accumulates
- Queue items hold until Buck reviews
- No external commitments made

**What doesn't happen when Buck is away:**
- No HubSpot updates
- No client emails
- No financial actions
- No contract approvals
- No production schema changes

---

## Monitoring

**Primary:** `reports/daily/YYYY-MM-DD-hci-command-center.md`  
**Secondary:** `EXECUTIVE_INBOX.md`  
**Infrastructure:** `reports/health/YYYY-MM-DD-health-check.md`  
**Sprint:** `CURRENT_SPRINT.md`

**Generate on demand:**
```bash
python3 scripts/generate_command_center.py
```

---

## Error Handling

| Scenario | Automatic Response | Buck Notified? |
|---|---|---|
| Service down (FastAPI, DB) | Health check alerts, launchd auto-restarts | Only if restart fails |
| Mining run fails | Logged to mining_runs, next run retries | No |
| Approval queue item expires | Item marked expired, re-queued next mining run | No |
| Agent blocker | Added to AI_TEAM/07_BLOCKERS.md, work continues on other missions | In Executive Inbox if Buck decision needed |
| Security issue detected | Automatic fix if possible (key rotation), immediate flag if not | Yes |

---

## System Boundaries (Never Crossed)

These are permanent constraints enforced in code, not just by convention:

1. Mining engine cannot write to source systems (HubSpot, Drive, Houzz, Outlook are read-only for miners)
2. `_GO_LIVE_AUTHORIZED` flag must be explicitly set — not inherited
3. `_DRY_RUN_DEFAULT = True` on all miners
4. Approval queue cannot auto-approve its own items
5. No email sent without Gate E approval
6. No HubSpot write without Gate H approval

---

## How to Restart the Loop (After Buck Returns)

1. Open Claude Code
2. Say: "Read the command center and continue"
3. Claude Code reads:
   - `EXECUTIVE_INBOX.md` — execute any approved items
   - `MISSION_QUEUE.md` — continue in-progress missions
   - `AI_TEAM/07_BLOCKERS.md` — clear blockers
4. Resume without needing context brief from Buck

---

*Autonomous Operating Model | HCI AI Operating System | Hendrickson Construction, Inc.*  
*Version 1.0 | 2026-06-27 | Chief Architect Directive — Automation First*

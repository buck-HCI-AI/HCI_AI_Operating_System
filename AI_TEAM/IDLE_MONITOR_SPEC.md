# IDLE_MONITOR_SPEC.md
## HCI AI OS - System Idle Monitor + Auto-Resume Specification

**Date:** 2026-07-01
**Requested By:** Buck Adams (HCI-AI Owner; PM & Superintendent at Hendrickson Construction)
**Prepared By:** Browser Claude (Operations Intelligence)
**Status:** IMPLEMENTATION-READY for Claude Code

---

## Purpose

Buck directive: If system is idle for 30 min, check Telegram channels,
send message to tell everyone to resume work and collaborate on what is next.

---

## What "Idle" Means

System is considered idle when ALL true for 30+ minutes:
1. No GitHub commits to main branch
2. No gateway API calls logged (excluding health checks)
3. No active agent heartbeats

System is NOT idle if within 30 minutes:
- BC commits to GitHub
- GBT fires a gateway directive
- Claude Code sends a heartbeat
- Buck sends a Telegram message (processed by gateway)

---

## n8n Workflow: AUTO-IDLE-MONITOR (AUTO-IDLE-001)

Schedule: Every 5 minutes

Node 1: Schedule Trigger - fires every 5 min

Node 2: HTTP GET /gateway/system/last-activity
Returns: last_commit_timestamp, last_gateway_call, last_heartbeat, minutes_idle, idle boolean

Node 3: IF minutes_idle > 30 AND idle == true - continue, else stop

Node 4: IF idle alert sent < 60 min ago - stop (no spam), else continue

Node 5: HTTP GET /gateway/telegram/recent - get Buck recent Telegrams

Node 6: Function - Build resume message
Message: System idle [N] min. Last: [description]. AI Team resume Sprint 3 work.
If unread Buck Telegrams: prepend summary of those.

Node 7: HTTP POST /gateway/telegram/outbound - send to Buck Telegram

Node 8: HTTP POST /gateway/system/idle-alert-log - log alert, create IDLE_LOG.md entry

---

## New Gateway Endpoints Required

GET /gateway/system/last-activity
- Returns: minutes since last commit, API call, or heartbeat
- idle = True if minutes > 30

POST /gateway/telegram/outbound
- Sends message to Buck via Telegram Bot API
- Logs to telegram_messages table

POST /gateway/system/idle-alert-log
- Appends entry to AI_TEAM/IDLE_LOG.md
- Tracks last alert time to prevent spam

---

## Telegram Channel Check on Idle

Before sending idle alert:
1. Read TELEGRAM_LOG.md for unprocessed Buck directives
2. Process any unprocessed directives first
3. Mark as processed
4. If still idle: send alert to Buck

---

## What BC Does on Idle Alert

1. BC reads IDLE_LOG.md for context
2. BC reads TELEGRAM_LOG.md for Buck direction
3. BC resumes highest-priority Sprint 3 work
4. BC fires GBT directive if architectural input needed
5. BC commits work and continues cycle

---

## Implementation Checklist for Claude Code

| Task | Acceptance |
|------|-----------|
| GET /gateway/system/last-activity | Returns minutes_idle accurately |
| POST /gateway/telegram/outbound | Message appears in Buck Telegram |
| POST /gateway/system/idle-alert-log | Entry in IDLE_LOG.md |
| AUTO-IDLE-001 n8n workflow | Fires every 5 min, alerts at 30 min |
| Test: 35 min no activity | Buck gets Telegram idle alert |

---

## Integration with Heartbeat Monitor

AUTO-IDLE-001: detects whole system inactive
Heartbeat monitor: detects specific agent (Code) offline
Both fire Telegram alerts. Both have 60 min cooldown. Both log to AI_TEAM/.

---

IDLE_MONITOR_SPEC.md | HCI AI Operating System | Hendrickson Construction, Inc.
Requested by: Buck Adams | Prepared by: Browser Claude | 2026-07-01

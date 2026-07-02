# TELEGRAM_AUTH_SPEC.md
## HCI AI OS — Telegram Authorization System Specification

**Authored by:** Browser Claude (Operations Intelligence)
**Source:** GBT Cycle 3 + Buck Adams Directive 2026-07-01
**Date:** 2026-07-01
**Status:** Approved for implementation — Sprint 3

---

## Purpose

This specification defines the Telegram-based authorization system that allows Buck Adams to grant, revoke, and manage team member access roles directly from his phone through the Telegram messaging platform.

Buck's directive: "If I have to give an auth to anyone in the team I need to be able to do that through tele as well."

---

## Authorization Commands

The following commands are available exclusively to Buck Adams through his registered Telegram user ID.

### Access Management

**Grant role:**
```
/auth @username role
```
Example: `/auth @jim superintendent`

Grants @jim the superintendent role. Jim can now submit field reports, create RFIs, upload photos, and escalate safety issues.

**Revoke all roles:**
```
/revoke @username
```
Example: `/revoke @jim`

Immediately removes all roles from @jim. All active sessions for @jim are invalidated.

**List active authorizations:**
```
/authlist
```

Returns a formatted list of all current team members, their roles, and when the role was granted.

### Approval Queue Commands

**Approve a queue item:**
```
/approve ITEM_ID
```
Example: `/approve AQ-2026-0142`

Approves the specified Approval Queue item. System executes the authorized action and creates audit record.

**Reject a queue item:**
```
/reject ITEM_ID reason
```
Example: `/reject AQ-2026-0142 Need three bids before award`

Rejects the item and records the rejection reason. Item is returned to originator.

**Escalate a queue item:**
```
/escalate ITEM_ID
```

Manually promotes an item to Critical priority. Useful when Buck wants to flag something for immediate team attention.

### System Control Commands

**Request system status:**
```
/status
```

System returns a full operational status report including: active projects and health scores, open approval queue items, agent heartbeat status, current sprint and open tasks, any items requiring Buck's attention.

**Pause an agent:**
```
/pause agentname
```
Example: `/pause code` (pauses Claude Code workflows)

**Resume an agent:**
```
/resume agentname
```

**Emergency stop all automation:**
```
/emergency stop
```
Immediately pauses all n8n workflows and queues. Does not delete or modify any data.

**Resume from emergency stop:**
```
/emergency resume
```

---

## Role Definitions

### superintendent
**Grant command:** `/auth @username superintendent`
**Authorized actions:**
- Submit daily field reports
- Create and submit RFIs (drafts only — PM reviews before submission)
- Upload site photographs
- Log safety observations and escalations
- Request material deliveries (creates procurement draft for PM review)
- Log weather delays
- Access project schedule (read-only)

**Cannot do:**
- Submit external communications
- Approve change orders
- Access budget or financial data
- Modify project scope

### pm (Project Manager)
**Grant command:** `/auth @username pm`
**Authorized actions:**
- All superintendent actions
- Update project schedule
- Draft change orders (for Buck approval)
- Draft subcontractor communications (for Buck approval)
- Access project financial data (read-only)
- Submit RFIs to design team (after drafting)
- Review and forward field reports
- Add items to Approval Queue

**Cannot do:**
- Award contracts
- Approve change orders (requires Buck)
- Approve financial commitments
- Send external communications without approval

### estimator
**Grant command:** `/auth @username estimator`
**Authorized actions:**
- Access bid packages and scope documents
- Use material cost research tools (including Perplexity)
- Review and compare subcontractor bids
- Access project history and comparable cost data
- Create and update estimate documents

**Cannot do:**
- Access active project financial data
- Communicate with subcontractors directly through the system
- Authorize any procurement

### client
**Grant command:** `/auth @username client`
**Authorized actions:**
- View project status updates (read-only)
- Receive milestone completion notifications
- View approved progress photographs
- Access project schedule summary (read-only)

**Cannot do:**
- Submit any operational requests through the system
- Access financial data
- Access internal communications

### vendor
**Grant command:** `/auth @username vendor`
**Authorized actions:**
- Receive bid invitations
- Submit structured bids through the Subcontractor Portal
- Acknowledge purchase orders
- Confirm delivery commitments
- Submit lien waivers

**Cannot do:**
- Access project documents beyond their own scope
- Communicate through internal channels

---

## Security Architecture

### Sender Validation

All Telegram commands go through a strict validation chain before any action is taken:

1. **Telegram message received** by HCI Bot
2. **Sender ID extracted** from message metadata (Telegram user ID — not username, which can be changed)
3. **Sender ID validated against AUTHORIZED_SENDERS table** in PostgreSQL
4. **If sender is Buck Adams:** proceed to command parsing
5. **If sender is NOT Buck Adams:** reject command, log unauthorized attempt, send rejection message to sender, alert Buck of unauthorized attempt via separate notification
6. **Command parsed and validated** for syntax and parameter correctness
7. **Action executed** against gateway/database
8. **Confirmation sent to Buck** in Telegram
9. **Audit record created** in AUTH_LOG.md and database

### Why Telegram User ID, Not Username

Telegram usernames (@username) can be changed by users. An attacker who knows Buck’s username format could create a similar username. Telegram User ID is a permanent, immutable numeric identifier assigned by Telegram at account creation. It cannot be changed or spoofed.

The AUTHORIZED_SENDERS table stores Buck’s Telegram User ID (numeric), not his username.

### Unauthorized Command Handling

When an unauthorized sender issues a command:
1. Command is rejected silently to the sender (no confirmation that a valid command was received)
2. Attempt is logged: sender ID, command attempted, timestamp
3. Buck receives a separate alert: "Unauthorized command attempt detected. Sender ID: [ID]. Command: [CMD]. Time: [timestamp]"
4. If the same unauthorized sender attempts commands more than 3 times in 24 hours, the Bot sends an escalated alert to Buck

---

## AUTH_LOG.md Format

All authorization actions are committed to `AI_TEAM/AUTH_LOG.md` in the repository. The log is append-only.

**Entry format:**
```
## AUTH_LOG Entry
**Timestamp:** 2026-07-01T14:32:17Z
**Action:** ROLE_GRANTED
**Target:** @jim (Telegram ID: 987654321)
**Role:** superintendent
**Granted by:** Buck Adams (Telegram ID: 123456789)
**Channel:** Telegram command `/auth @jim superintendent`
**Gateway Request ID:** auth-abc123
**Confirmation sent:** Yes

---
```

**Action types in log:**
- ROLE_GRANTED
- ROLE_REVOKED
- QUEUE_ITEM_APPROVED
- QUEUE_ITEM_REJECTED
- QUEUE_ITEM_ESCALATED
- SYSTEM_PAUSED
- SYSTEM_RESUMED
- EMERGENCY_STOP
- UNAUTHORIZED_ATTEMPT

---

## Database Schema

### Table: telegram_authorized_users
```sql
CREATE TABLE telegram_authorized_users (
  id SERIAL PRIMARY KEY,
  telegram_user_id BIGINT UNIQUE NOT NULL,  -- Immutable Telegram ID
  telegram_username TEXT,                    -- For display only, not used for auth
  name TEXT NOT NULL,
  role TEXT NOT NULL,
  granted_by BIGINT NOT NULL,               -- Buck's Telegram User ID
  granted_at TIMESTAMP DEFAULT NOW(),
  revoked_at TIMESTAMP,
  is_active BOOLEAN DEFAULT TRUE
);
```

### Table: telegram_auth_log
```sql
CREATE TABLE telegram_auth_log (
  id SERIAL PRIMARY KEY,
  timestamp TIMESTAMP DEFAULT NOW(),
  action TEXT NOT NULL,
  target_telegram_id BIGINT,
  target_username TEXT,
  role TEXT,
  performed_by BIGINT NOT NULL,
  command_text TEXT,
  gateway_request_id TEXT,
  success BOOLEAN DEFAULT TRUE,
  notes TEXT
);
```

---

## Gateway Endpoints Required

The following FastAPI gateway endpoints must be implemented by Claude Code:

```
POST /gateway/telegram/auth
  Body: {telegram_user_id, role, granted_by}
  Action: Insert into telegram_authorized_users, log to telegram_auth_log

POST /gateway/telegram/revoke
  Body: {telegram_user_id, revoked_by}
  Action: Set is_active=False, update revoked_at, log action

POST /gateway/telegram/validate
  Body: {telegram_user_id}
  Returns: {is_authorized, role, name}

GET /gateway/telegram/authlist
  Returns: All active authorized users with roles

POST /gateway/telegram/log
  Body: {action, target_id, command_text, success}
  Action: Insert into telegram_auth_log, append to AUTH_LOG.md
```

---

## n8n Workflow: AUTH_COMMAND_ROUTER

**Workflow ID:** WF-TELE-001
**Trigger:** Telegram webhook (any message to HCI Bot)
**Steps:**
1. Receive message
2. Extract sender ID and message text
3. Validate sender ID against AUTHORIZED_SENDERS (Buck only)
4. If unauthorized: log attempt, alert Buck, end workflow
5. Parse command (first word: /auth, /revoke, /approve, /reject, /status, etc.)
6. Route to appropriate command handler sub-workflow
7. Execute action via gateway endpoint
8. Send confirmation to Buck in Telegram
9. Commit audit record

---

## Setup Requirements

To activate this system, Buck must provide:
1. **Telegram Bot Token** — Created via BotFather in Telegram. The token authorizes the n8n workflow to send and receive messages as the HCI Bot.
2. **Buck's Telegram User ID** — The numeric User ID from Buck's Telegram account. Can be retrieved by messaging a bot like @userinfobot in Telegram. This ID is stored as the sole authorized command sender.

Claude Code implements the n8n webhook, gateway endpoints, and database tables.
Browser Claude configures the integration once the token and User ID are provided.

---

## Implementation Checklist

- [ ] Buck provides Telegram Bot Token
- [ ] Buck provides his Telegram User ID (numeric)
- [ ] Claude Code: Create telegram_authorized_users table
- [ ] Claude Code: Create telegram_auth_log table
- [ ] Claude Code: Implement /gateway/telegram/* endpoints
- [ ] Claude Code: Build WF-TELE-001 in n8n (webhook + command router)
- [ ] Claude Code: Configure Bot webhook URL in Telegram
- [ ] Test: Send /auth @testuser superintendent — verify database entry and AUTH_LOG.md entry
- [ ] Test: Send /revoke @testuser — verify is_active=False in database
- [ ] Test: Send /status — verify system report returned
- [ ] Test: Unauthorized command attempt — verify rejection, logging, and Buck alert
- [ ] Commit results to AI_TEAM/TELEGRAM_AUTH_TEST_RESULTS.md

---

*Specification authored by Browser Claude | Per Buck Adams directive 2026-07-01 | 2026-07-01*

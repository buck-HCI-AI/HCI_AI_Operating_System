# TELEGRAM_ARCHITECTURE_SPEC.md
## HCI AI OS - Telegram Integration Architecture Specification
## Implementation-Ready Design for Claude Code

**Date:** 2026-07-01
**Prepared By:** Browser Claude (Operations Intelligence)
**Source:** GBT Chief Architect - Cycle 3 Response
**Status:** READY FOR IMPLEMENTATION

---

## Architecture Objective

Make Buck Adams operational Telegram messages a durable, governed input into HCI AI OS.

Key principle: Telegram is not the source of truth. It is an ingress channel.
The gateway and GitHub commit log are the source of truth.

---

## Architecture Diagram (Text)

Buck sends Telegram message
-> Telegram Bot API receives message
-> n8n Telegram Trigger node fires
-> n8n processes: extract sender, text, timestamp
-> n8n validates: is sender Buck? (check Telegram user ID)
-> n8n routes: is this a command or a note?
-> n8n POST to /gateway/agent/telegram-inbound
-> Gateway creates TELEGRAM_LOG entry in DB
-> Gateway commits to AI_TEAM/TELEGRAM_LOG.md (append)
-> Gateway returns 200 OK to n8n
-> n8n sends Telegram confirmation: "Received: [summary]"

BC reads TELEGRAM_LOG.md on each session start.
BC does not poll in real-time - reads the committed log.

---

## Component 1: Telegram Bot Setup

**Prerequisite (Buck must do):**
1. Create Telegram bot via @BotFather if not done
2. Get bot token: BOT_TOKEN
3. Get Buck Telegram user ID: BUCK_TELEGRAM_USER_ID
4. Store both in system secrets (not in GitHub)

**Verification:**
Buck sends /start to bot -> Bot responds "HCI AI OS connected"

---

## Component 2: n8n Workflow - TELEGRAM_INBOUND

**Workflow ID:** TEL-INBOUND-001
**Trigger:** Telegram Trigger node (webhook, listens for messages)

**n8n Node Sequence:**

Node 1: Telegram Trigger
- Credential: BOT_TOKEN
- Trigger on: message, channel_post
- Returns: message object with from.id, text, date

Node 2: IF - Validate Sender
- Condition: message.from.id == BUCK_TELEGRAM_USER_ID
- If TRUE: continue to Node 3
- If FALSE: stop (no response - security)

Node 3: Function - Parse Message
Output object:
{
  "sender": "buck",
  "telegram_id": message.from.id,
  "text": message.text,
  "timestamp": new Date(message.date * 1000).toISOString(),
  "message_type": detect_type(message.text),
  "raw": message
}

Message types:
- "command": starts with / (e.g., /status, /projects)
- "note": free text note for log
- "directive": starts with "DO:" or "ACTION:"
- "question": ends with ?

Node 4: HTTP Request - POST to Gateway
URL: https://speculate-armband-retinal.ngrok-free.dev/gateway/telegram/inbound
Method: POST
Headers: X-API-Key: [API_KEY]
Body: parsed message object from Node 3

Node 5: Telegram - Send Confirmation
Send to: message.from.id
Text: "Received [message_type]: [first 50 chars of text]"

---

## Component 3: Gateway Endpoint - /gateway/telegram/inbound

**New endpoint needed in FastAPI:**

POST /gateway/telegram/inbound
Auth: X-API-Key required

Request body:
{
  "sender": "buck",
  "telegram_id": 123456789,
  "text": "Check 101F status",
  "timestamp": "2026-07-01T21:00:00Z",
  "message_type": "command",
  "raw": {}
}

Actions:
1. Insert row in telegram_messages table (create if not exists)
2. Append entry to AI_TEAM/TELEGRAM_LOG.md in GitHub repo
3. If message_type == "command": route to appropriate endpoint, return result
4. Return {"status": "logged", "log_entry_id": N}

---

## Component 4: Database Table - telegram_messages

CREATE TABLE telegram_messages (
  id SERIAL PRIMARY KEY,
  sender VARCHAR(50) NOT NULL,
  telegram_id BIGINT NOT NULL,
  message_text TEXT NOT NULL,
  message_type VARCHAR(20),
  received_at TIMESTAMPTZ DEFAULT NOW(),
  processed BOOLEAN DEFAULT FALSE,
  response_text TEXT
);

---

## Component 5: TELEGRAM_LOG.md Format

File: AI_TEAM/TELEGRAM_LOG.md
Location: GitHub repo main branch
Updated by: Gateway on each message received

Format per entry:

## [TIMESTAMP] - [message_type]
**From:** Buck Adams (@buck_telegram)
**Received:** [ISO timestamp]
**Message:** [full text]
**Type:** [command | note | directive | question]
**Response:** [system response if any]
**Logged by:** Gateway v[version]
---

Example:
## 2026-07-01T21:05:00Z - command
**From:** Buck Adams
**Received:** 2026-07-01T21:05:00Z
**Message:** /status
**Type:** command
**Response:** "3 active projects. 64EW: YELLOW (2 risks). 101F: YELLOW (-5 days). 1355R: GREEN."
**Logged by:** Gateway v1.0
---

---

## Component 6: Command Router

When message_type == "command", gateway routes to:

| Command | Routes To | Returns |
|---------|----------|---------|
| /status | /gateway/executive/mission-control | KPI summary |
| /101F | /gateway/project/101F/brain | Project summary |
| /64EW | /gateway/project/64EW/brain | Project summary |
| /1355R | /gateway/project/1355R/brain | Project summary |
| /246GW | /gateway/project/246GW/brain | Project summary |
| /risks | All project risks | Risk summary |
| /morning | /gateway/executive/report | Morning brief |
| /help | Static message | Command list |

---

## BC Read Pattern

BC cannot receive Telegram in real-time (no browser Telegram access).
BC reads TELEGRAM_LOG.md from GitHub on each session start.

BC workflow:
1. Navigate to AI_TEAM/TELEGRAM_LOG.md
2. Read entries since last BC session
3. For each new entry:
   a. Note if it is a directive (type="directive")
   b. Action on directive if within BC authority
   c. Flag for Buck if it requires Buck action
4. Report to Buck in chat: "I read N new Telegram messages since last session"

---

## Implementation Checklist for Claude Code

| # | Task | Acceptance Criteria |
|---|------|---------------------|
| 1 | Create telegram_messages table | SQL committed to 05_Database/ |
| 2 | Build POST /gateway/telegram/inbound endpoint | Returns 200 with log_entry_id |
| 3 | Build TELEGRAM_LOG.md append logic | New entry appears in GitHub within 30s |
| 4 | Create TEL-INBOUND-001 n8n workflow | Trigger fires on Buck message |
| 5 | Add sender validation | Non-Buck messages silently dropped |
| 6 | Build command router | /status returns project KPI summary |
| 7 | End-to-end test | Buck sends "test" -> appears in TELEGRAM_LOG.md |
| 8 | Commit TEST_TELEGRAM_2026-07-01.md | Test results documented |

**Prerequisites (Buck must provide):**
- Telegram bot token (BOT_TOKEN)
- Buck Telegram user ID (BUCK_TELEGRAM_USER_ID)

---

## Security Rules

1. Only messages from BUCK_TELEGRAM_USER_ID are processed
2. All messages logged to DB and GitHub before any action taken
3. Gateway directives from Telegram follow same approval rules as other directives
4. Telegram cannot override existing governance - approval queue still required
5. No email sent based on Telegram message without Buck approval in chat

---

TELEGRAM_ARCHITECTURE_SPEC.md | HCI AI Operating System | Hendrickson Construction, Inc.
Prepared by: Browser Claude (Operations Intelligence) | 2026-07-01
Source: GBT Chief Architect Cycle 3 | Authority: HCI_AI_CONSTITUTION.md
Status: IMPLEMENTATION-READY - Claude Code begin immediately on restart

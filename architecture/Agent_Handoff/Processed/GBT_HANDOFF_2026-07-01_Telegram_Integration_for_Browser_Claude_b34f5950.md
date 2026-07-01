---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: Telegram Integration for Browser Claude
created_at: 2026-07-01
summary: Handoff from ChatGPT via GBT Gateway
---

Buck sends operational messages via Telegram that Browser Claude currently cannot see. Build: (1) GET /gateway/telegram/messages endpoint that returns unread Telegram messages sent to the HCI bot, with fields: message_id, from, text, timestamp, read_status. (2) POST /gateway/telegram/ack to mark messages read. (3) n8n workflow or scheduled task that polls Telegram bot API every 60 seconds and stores new messages to gateway DB table telegram_messages. (4) Browser Claude workflow: at start of each session, BC calls GET /gateway/telegram/messages to surface any unread messages from Buck before proceeding. This makes Buck Telegram messages visible in BC operational loop. Use existing Telegram bot token from environment. No new external accounts. Commit all. Return report.

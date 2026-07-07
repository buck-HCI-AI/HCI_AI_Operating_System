---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: Implement recurring 30-minute Chief Architect check-in automation
created_at: 2026-07-07
summary: Handoff from ChatGPT via GBT Gateway
---

Implement an automated workflow (preferred: n8n cron every 30 minutes) that performs: (1) getWarmStart, (2) getBuckTelegramMessages(agent=chatgpt), (3) if unread Telegram messages OR pending_chief_architect_reviews OR blocked missions needing Chief Architect input exist, invoke the review workflow and send a status back via sendMessageToBuck using work_complete or review_required as appropriate. Must not require Buck to open a new ChatGPT conversation. Include heartbeat, deduplication, and idempotency protections.

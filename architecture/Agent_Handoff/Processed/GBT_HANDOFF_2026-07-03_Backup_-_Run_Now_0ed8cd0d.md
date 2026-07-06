---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: Backup - Run Now
created_at: 2026-07-03
summary: Handoff from ChatGPT via GBT Gateway
---

Run SETUP_DAILY_BACKUP.command or rsync+pg_dump immediately. Do not wait for 2AM cron. Verify backup completed and report timestamp and destination via ai/messages.

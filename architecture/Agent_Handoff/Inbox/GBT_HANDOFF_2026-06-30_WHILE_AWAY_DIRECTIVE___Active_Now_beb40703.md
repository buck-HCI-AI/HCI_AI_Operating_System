---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: WHILE AWAY DIRECTIVE — Active Now
created_at: 2026-06-30
summary: Handoff from ChatGPT via GBT Gateway
---

Buck is stepping away. Full directive at AI_TEAM/WHILE_AWAY_DIRECTIVE.md

Key rules:
- DEFAULT: Keep all build and collaboration work moving — do NOT wait for Buck
- Only message Buck via Telegram for: contract awards, client-facing sends, budget decisions, hard blockers requiring Buck UI action
- BTW backlog order: BTW-4 → BTW-8 → BTW-6
- 1355R SOW drafts: populated, hold for Buck Telegram approval before sending
- Aspen Welding bid expires 7/2 — flag to Buck before that
- Telegram: POST /gateway/telegram/send (X-API-Key required), check replies GET /gateway/buck/messages
- BC can also send via gateway — identify messages with GBT: or BC: prefix

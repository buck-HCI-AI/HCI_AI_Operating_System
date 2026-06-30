---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: GBT + BC — ADVANCE DIRECTIVE — Read This First
created_at: 2026-06-30
summary: Handoff from ChatGPT via GBT Gateway
---

Full directive now live at GET /gateway/directive — read it before anything else.

Key points:
- Default: ALWAYS ADVANCE. Never stop between BTW items.
- BTW order: BTW-4 (bid stale-detection) → BTW-8 (vendor scoring) → BTW-6 (246GW)
- 1355R is RED — highest priority project. Steel SOW sent today, Aspen bid expires 7/2.
- Double-check each others work: BC confirms data before GBT directs Claude Code to load it.
- Lessons learned in the directive — read them, dont repeat the same bugs.
- Telegram for Buck: POST /gateway/telegram/send — critical decisions only.

GBT: Start with GET /gateway/directive then GET /gateway/executive/mission-control
BC: Start with GET /gateway/directive then pull any new Houzz activity on 1355R and 64EW

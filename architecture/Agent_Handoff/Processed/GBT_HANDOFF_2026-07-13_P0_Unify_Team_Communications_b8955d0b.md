---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: P0 Unify Team Communications
created_at: 2026-07-13
summary: Handoff from ChatGPT via GBT Gateway
---

Implement a single canonical communications layer. Current state is fragmented across ADR-003 bus, Drive coordination files, Telegram, and handoff inboxes, causing GBT and other agents to miss active work. Build automatic synchronization so every coordination message is visible through one canonical interface. Requirements: mirror Drive coordination into ADR-003 (or vice versa), acknowledge P0/P1 messages automatically, detect stale/unanswered directives, include daily brief generation, and add regression tests proving all agents see identical communication state. This is a P0 blocker for the 100/100 initiative.

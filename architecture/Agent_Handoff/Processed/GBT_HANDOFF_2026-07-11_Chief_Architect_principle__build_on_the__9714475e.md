---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: Chief Architect principle: build on the platform, not around it
created_at: 2026-07-11
summary: Handoff from ChatGPT via GBT Gateway
---

Team directive from Chief Architect: Buck is intentionally stepping out of the loop. Operate as an engineering team. One architectural principle now governs all implementation: EVERY new capability must consume the platform, not create another platform. Identity comes from the People & Identity Platform. Communications go through the Agent Bus. Project data comes from the consolidated Project View. Decisions are recorded in the canonical decision log. Do not introduce parallel identity stores, communications paths, startup sequences, or project APIs. Before implementing a feature, ask: 'Can this reuse the canonical platform?' If yes, extend the platform rather than creating new infrastructure. Continue under three-agent consensus. Only pause for a genuine technical blocker, governance restriction, or a decision that truly requires Buck's judgment. Otherwise, keep moving, verify with evidence, and leave the platform stronger after every change.

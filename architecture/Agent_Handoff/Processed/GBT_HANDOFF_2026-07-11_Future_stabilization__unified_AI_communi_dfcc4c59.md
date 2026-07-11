---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: medium
status: pending
related_system: 
title: Future stabilization: unified AI communications architecture
created_at: 2026-07-11
summary: Handoff from ChatGPT via GBT Gateway
---

Architecture proposal for implementation after current priorities: build a durable agent communications layer to eliminate human relay. Recommended design: generic Agent Bus rather than agent-specific endpoints. Components: (1) AI Agent Directory (agent id, role, capabilities, heartbeat, inbox/outbox); (2) generic sendAgentMessage(from,to,type,priority,thread,requires_response,payload) API; (3) shared message store with status (pending/read/replied/closed); (4) optional compatibility wrappers such as sendHandoffToClaude() and future sendHandoffToBrowserClaude() built on the generic bus; (5) audit trail and message threading; (6) startup catch-up from unread messages. Temporary workaround while Code is offline: maintain one LIVE_TEAM_COMMS.md append-only coordination document in HCI AI Master. Please evaluate architecture, implementation effort, migration path, and backward compatibility, then prepare an ADR before implementation.

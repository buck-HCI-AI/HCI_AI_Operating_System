---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: Architectural requirement: resilient team communications with degraded-mode operation
created_at: 2026-07-11
summary: Handoff from ChatGPT via GBT Gateway
---

Additional Chief Architect directive: Treat resilient team communications as core infrastructure, not a convenience feature. Design and implement a communications layer that allows work to continue if any single agent (including Claude Code) goes offline. Requirements: (1) persistent shared message store with threading, acknowledgements, unread state, and audit trail; (2) direct communication paths between Chief Architect and Browser Claude without requiring Buck as relay; (3) offline catch-up so a returning agent automatically ingests missed messages and decisions; (4) heartbeats and agent status (online/stale/offline); (5) durable decision log recording consensus and rationale; (6) graceful degraded mode where remaining agents continue work and queue implementation tasks until Code returns. Verify the design by simulating a Code outage and confirming Chief Architect and Browser Claude can continue coordinating. Produce an ADR and implementation plan before declaring the communications layer complete.

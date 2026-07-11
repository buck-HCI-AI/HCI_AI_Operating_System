---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: P0 Build ADR-003 Agent Message Bus now
created_at: 2026-07-11
summary: Handoff from ChatGPT via GBT Gateway
---

Buck directive: Read ADR-003_AGENT_MESSAGE_BUS_FOUNDATIONAL_INFRA_2026-07-11.md (Drive ID 1ooF63jQL5s8VmFT1dVrGp-J6hcqI17IB) and build it now. This is P0. Implement the three tables exactly as specified: agent_messages, agent_heartbeats, decision_log. Implement the eight endpoints in the ADR. Add all endpoints to GBT's Actions schema using a controlled update that preserves tool continuity. Wire Code's monitoring loop to heartbeat, unread polling, offline detection, and reconnect catch-up. Wire Browser Claude startup/warm-start to unread polling, heartbeat, and read acknowledgements. Seed DEC-001 through DEC-004. Preserve/migrate links to existing ai_messages, ai_agent_heartbeat, and ADR records as needed so historical data is not lost, but ADR-003's AMB becomes the canonical coordination interface per Buck's explicit direction. When done, send one real message TO BC and one TO GBT through the new system. Do not resume other work until all four ADR verification scenarios pass with recorded evidence: Code offline, Code return/catch-up, BC offline/catch-up, and GBT tool-loss fallback. Report schema changes, endpoints, Actions schema result, test evidence, and any remaining risks.

---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: P0 ADR-003 Mirror Implementation
created_at: 2026-07-13
summary: Handoff from ChatGPT via GBT Gateway
---

Proceed with the agreed communications architecture. Make ai_messages (ADR-003) the canonical machine bus. Implement automatic mirroring: when Browser Claude Drive coordination files are detected and folded into LIVE_TEAM_COMMS.md, also insert corresponding ai_messages records so GBT immediately receives them via unread polling. LIVE_TEAM_COMMS.md becomes a human-readable projection of the bus. Telegram remains Buck-only alerts. Also proceed with Bid Leveling Option B: infer unclassified divisions from scope_summary for display only, mark '[inferred]', do not modify underlying project data. Provide regression tests proving BC->CODE->GBT message visibility and Option B behavior.

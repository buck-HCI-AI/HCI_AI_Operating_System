---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: Fix GBT session tool call limit — business blocker
created_at: 2026-06-28
summary: Handoff from ChatGPT via GBT Gateway
---

Priority: CRITICAL — HIGHEST PRIORITY IN SYSTEM.

The current effective limit of approximately 3 gateway tool calls per GBT session makes the system unusable for field operations. Superintendents are expected to check status at least 5 times per day and PMs 10+ times per day. Requiring a new GBT session after only a few interactions is a major adoption risk.

Required implementation:
- Increase supported gateway interactions to a minimum of 15 consecutive tool calls per session.
- Implement server-side session persistence so tool slots do not degrade during normal field use.
- Prioritize this work before Adam and Traff go live.

Business impact: This is a release-blocking UX issue. Without this change, field adoption is at significant risk.

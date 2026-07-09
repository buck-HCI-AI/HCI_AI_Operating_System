---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: TEAM DIRECTIVE: Production quality and bid-folder governance expectations
created_at: 2026-07-09
summary: Handoff from ChatGPT via GBT Gateway
---

Effective immediately for Claude Code and Browser Claude:

Buck's expectation is that the AI team eliminates confusion, not creates it. Team members and project staff should not be asking Buck why duplicate folders suddenly appeared.

New engineering expectations:

1. One canonical bid-folder structure per project (64EW, 101F, 1355R). No process may recreate duplicate or legacy folder trees.
2. If an automation cannot prove it is creating the canonical structure, it must fail safely and raise an internal alert instead of writing to Drive.
3. Every cleanup must include regression protection. 'Fixed once' is not acceptable if the issue can return.
4. Before claiming a fix is complete, verify the actual Shared Drive, generated outputs, and user-visible results—not just logs or API success.
5. Any regression that recreates duplicate folders or contaminates bid-leveling output is to be treated as a production incident with root cause, timeline, corrective action, and permanent prevention.
6. Reduce questions to Buck. Resolve uncertainty internally whenever possible and escalate only for genuine business decisions, not avoidable technical confusion.

Apply these standards immediately to the current bid-leveling investigation and include evidence of compliance in the incident report.

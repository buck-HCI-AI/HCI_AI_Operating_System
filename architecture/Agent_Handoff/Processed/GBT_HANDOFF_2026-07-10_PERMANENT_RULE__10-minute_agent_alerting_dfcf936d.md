---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: PERMANENT RULE: 10-minute agent alerting + shared coordination state
created_at: 2026-07-10
summary: Handoff from ChatGPT via GBT Gateway
---

Buck has updated the alerting requirement. Implement this as a permanent cross-agent rule for Claude Code, GBT/Chief Architect, and Browser Claude.

Alert threshold:
- Every 10 minutes maximum.
- If any agent is idle waiting on Buck for a decision, pending approval, blocked mission, ambiguous judgment call, or has completed a milestone, that agent must push a Telegram message to Buck within 10 minutes.
- Do not wait for Buck to check in manually.

Shared-state requirement:
- All three agents must read from the same coordination history and stay aligned.
- No agent should continue working from stale or partial context if another agent has newer information.
- Use the AI Team Document Bus / canonical message drop as the shared coordination record.
- On each loop, agents should check: Telegram, unread coordination docs, active handoffs, blocked missions, and pending approvals.
- Acknowledge or mark processed items so the next loop has an accurate shared state.

Implementation requirements:
1. Extend Code's existing loop so every 10 minutes it checks:
   - new Telegram messages,
   - new Document Bus/message-drop items,
   - pending approvals,
   - blocked/ambiguous missions,
   - completed milestones requiring Buck notification.
2. Apply the same 10-minute rule to GBT and BC via the shared architecture and documented operating standard.
3. Add deduplication so Buck is not spammed with repeated unchanged alerts.
4. Alerts should include: what is waiting, why Buck is needed, consequence of delay, and the exact decision/request.
5. Completed milestones should send concise evidence-backed updates, not vague status notes.
6. Persist this in CLAUDE.md, the Standards Registry, and the Operating Book / team operating rules.
7. Add regression tests or a live proof showing an agent enters a blocked/waiting state and Buck receives a Telegram within 10 minutes.

Acceptance criteria:
- A blocked or waiting agent never sits silently for more than 10 minutes.
- All three agents see the same current coordination state.
- No repeated alerts unless state changes or 10-minute escalation policy explicitly requires a reminder.
- Buck no longer has to poll agents for status.

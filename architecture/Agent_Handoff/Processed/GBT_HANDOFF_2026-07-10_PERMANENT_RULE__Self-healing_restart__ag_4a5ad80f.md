---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: PERMANENT RULE: Self-healing restart, agent role recovery, and pick-up-where-left-off
created_at: 2026-07-10
summary: Handoff from ChatGPT via GBT Gateway
---

Buck directed this as a permanent system rule, consistent with the HCI AI Operating Book principles (learning system, governance-first, evidence over claims, resilience, role-based operating model, 100/100 standard).

Build a full shutdown/restart recovery system for planned OS updates and unplanned restarts.

Required behavior:
1. Pre-shutdown checkpoint
- Persist active missions, current task, project context, pending approvals, blocked decisions, open browser/GPT work, current evidence, and next action for each agent (GBT, BC, Claude Code, n8n).
- Persist last-read Telegram message ID and last-acknowledged Document Bus item per agent.
- Record whether work is safe to resume automatically or requires human approval.

2. Automatic startup sequence
On workstation boot/restart, automatically start required local services/containers/tunnels/workflows where technically possible.
Each agent/session must begin with:
- gateway health check,
- project state,
- Telegram catch-up,
- warm-start,
- unread Document Bus/message-drop review,
- agent role/authority reload,
- current mission recovery,
- heartbeat registration.

3. Role recovery
Every agent must reload and state its role, boundaries, and current responsibilities from canonical configuration—not memory alone:
- GBT: Chief Architect / governance / review
- Claude Code: Builder / deployer
- Browser Claude: browser/GPT configuration / independent verification / repo governance
- n8n: automation

4. Pick-up-where-left-off rule
After restart, each agent resumes the most recent safe, authorized action from its checkpoint without Buck reconstructing context.
- No duplicate execution.
- No replay of irreversible actions.
- Any uncertain/ambiguous state becomes BLOCKED and triggers Telegram within 10 minutes.

5. Self-healing rule
Every failure must follow this loop:
- detect,
- diagnose,
- safely auto-correct if the issue is known and reversible,
- verify live,
- add/update regression test,
- record lesson/provenance,
- notify Buck only when blocked, approval is needed, or a milestone is complete.
Unknown or consequential failures must never be auto-fixed through destructive or externally committing actions.

6. Recovery evidence
Create a restart manifest showing:
- services expected,
- services restored,
- agents online,
- messages caught up,
- missions resumed,
- anything blocked,
- tests run.

7. Testing
Before the upcoming OS update, run a controlled restart drill if possible:
- checkpoint state,
- restart services/environment,
- verify all required components auto-start,
- verify each agent recovers role/state,
- verify no directives/messages are lost,
- verify no duplicate work occurs,
- verify 10-minute alert rule works.

8. Documentation
Add this permanently to:
- Operating Book (new restart/self-healing section),
- Standards Registry,
- CLAUDE.md,
- role onboarding/welcome guides,
- runbook/SOP.

Acceptance standard:
After a shutdown, Buck should not need to explain where the system was or what each agent was doing. The AI team should reassemble from canonical state, verify itself, and safely continue from the last checkpoint.

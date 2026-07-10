---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: medium
status: pending
related_system: 
title: Add rollout step: Share Adam Email GPT with Adam after acceptance
created_at: 2026-07-10
summary: Handoff from ChatGPT via GBT Gateway
---

Chief Architect rollout requirement: once Adam Email GPT has passed acceptance testing, include a deployment step to share it with Adam Malmgren.

Before sharing:
- Verify acceptance tests pass.
- Confirm governance and permissions are correct.
- Confirm draft-only email behavior and no direct-send capability.
- Confirm project context and source-of-truth behavior.

After sharing:
- Provide Adam with a short onboarding guide covering capabilities, limitations, workflow, and how to report issues.
- Record the rollout in the project documentation.

Do not share before acceptance criteria are met.

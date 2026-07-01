---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: DISABLE /gateway/email/send — P0 lockdown
created_at: 2026-07-01
summary: Handoff from ChatGPT via GBT Gateway
---

Root cause of 101F unauthorized email confirmed: BC_EMAIL_CAPABILITY.md documents a /gateway/email/send endpoint with a rule allowing direct send for bid invitations without approval. This violates standing directive. IMMEDIATE: (1) Disable or remove /gateway/email/send endpoint entirely. (2) /gateway/email/draft remains active — draft creation is permitted. (3) /gateway/email/draft/{id}/send must require email_approved=true in approval queue before executing — if not approved, return 403 and create approval queue item. (4) Remove the rule in BC_EMAIL_CAPABILITY.md that says bid invitations are OK to send directly — update to say ALL emails require Buck approval before sending. (5) Update BC_EMAIL_CAPABILITY.md with corrected rules. Commit all. This is non-negotiable — no autonomous email sending under any circumstances.

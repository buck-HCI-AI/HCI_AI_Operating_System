---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: START NOW: Build Adam Email GPT end-to-end
created_at: 2026-07-10
summary: Handoff from ChatGPT via GBT Gateway
---

Buck has now authorized active build of Adam Email GPT. Begin implementation now using the previously issued architecture and rollout requirements.

Build sequence:
1. Draft the final system instructions for Adam Email GPT.
2. Define the minimal Actions schema and capability matrix.
3. Verify gateway endpoints for email read, thread summary, project match, attachment inspection/carry-forward, task extraction, and draft creation.
4. Enforce draft-only behavior; no direct send.
5. Enforce source-of-truth and provenance rules.
6. Build Adam onboarding/discovery flow so he can describe how he wants inbox organization, triage, follow-ups, project grouping, draft review, attachments, dashboards, and automation.
7. Use Browser Claude for GPT Builder/browser configuration and live publishing verification where needed.
8. Run a fresh-chat end-to-end test with a real project email containing attachments.
9. Confirm original thread preserved, attachments surfaced/carried forward, project context matched, actions extracted, and Outlook draft created only.
10. After acceptance, share the GPT with Adam Malmgren and provide a short onboarding guide.

Return evidence: prompt/instructions, Actions schema, capability matrix, live test result, governance checks, sharing confirmation, and any remaining blockers.

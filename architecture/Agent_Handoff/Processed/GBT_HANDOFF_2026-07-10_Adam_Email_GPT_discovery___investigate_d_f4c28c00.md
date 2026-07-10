---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: Adam Email GPT discovery + investigate draft emails landing in Junk
created_at: 2026-07-10
summary: Handoff from ChatGPT via GBT Gateway
---

Chief Architect follow-up.

1) Adam Email GPT discovery session:
Before finalizing the build, meet with Adam and treat him as the product owner for his workflow. Walk him through how to describe:
- His ideal inbox organization.
- Daily email workflow from start to finish.
- Triage views.
- Follow-up workflow.
- Project organization.
- Vendor/client communication preferences.
- Draft review flow.
- Attachments and plan handling.
- Task extraction.
- Search and recall.
- Dashboards and summaries.
- Any repetitive work he wants automated.
Capture his desired screens, flows, naming, organization, and pain points. Feed that into the design before locking the GPT.

2) Investigate Junk mail issue:
Buck reports AI-created draft emails are still ending up in Junk. Investigate root cause rather than treating symptoms.
Determine whether this is due to Outlook/Microsoft Graph draft creation, sender metadata, MIME construction, headers, categories, automation path, or another issue.
Provide evidence, reproduce the issue, identify the root cause, implement a durable fix if possible, and add a regression test so drafts consistently appear in Drafts rather than Junk. If the behavior is controlled by the mail platform, document the limitation and any mitigation.

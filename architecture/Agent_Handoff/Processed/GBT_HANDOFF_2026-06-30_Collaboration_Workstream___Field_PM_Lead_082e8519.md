---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: Collaboration Workstream — Field/PM/Leadership Collaboration Operating Layer
created_at: 2026-06-30
summary: Handoff from ChatGPT via GBT Gateway
---

Buck asked ChatGPT Chief Architect to continue HCI AI OS work, pick up with Code, and return to the collaboration workstream.

Chief Architect directive:

Build/design the next collaboration layer for HCI AI Construction OS around the existing Gate 5 live environment.

Context from live state:
- Gate 5 GO authorized on 2026-06-30.
- Live production projects: 64EW, 101F, 1355R. 246GW monitored/staged.
- Field GPT exists and is read-only for SS/PMs.
- Role intelligence is live with 9 role consoles.
- Gateway, approval loop, ntfy, Drive watcher, event triggers, project brain, schedule intelligence, bid intelligence, and knowledge graph are live.
- Shared Drive/HubSpot/Houzz writes require Buck explicit approval.
- driveWrite session logs and Code handoffs are pre-authorized.

Deliverable requested from Claude Code:
1. Audit current collaboration-related endpoints, workflows, tables, and docs already built.
2. Propose and/or implement a Collaboration Operating Layer v1 with these roles:
   - Buck / Owner command
   - PM console
   - Superintendent / Field GPT read-only console
   - Office/Admin coordination
   - Trade partner/client-safe outbound draft layer
   - Claude Code implementation queue
   - ChatGPT Chief Architect governance queue
3. Define collaboration objects:
   - action item
   - decision
   - approval request
   - RFI/email draft
   - field note/daily log
   - risk/escalation
   - project status update
   - Code handoff
4. Confirm existing approval gates are enforced:
   - no Shared Drive writes without Buck approval
   - no live bid-leveling writes unless explicit go-live
   - no outbound email/send action without approval
   - Field GPT stays read-only except queued submissions
5. If implementation is appropriate, add minimal endpoints/tables/workflows only where gaps exist. Prefer extending existing systems over creating duplicates.
6. Return a concise implementation report with:
   - existing assets found
   - gaps
   - recommended architecture
   - completed changes, if any
   - required Buck approvals
   - test results

Priority focus:
- 101F urgent bid due July 3 collaboration path
- 1355R email/RFI directive collaboration flow
- 64EW/101F full folder scan plan-analysis follow-up
- approval queue cleanup support

Do not write to Shared Drive, HubSpot, Houzz, or send external emails without Buck approval. Use approval queue/draft-only patterns.

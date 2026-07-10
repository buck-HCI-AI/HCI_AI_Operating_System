---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: Adam Email GPT role update: Daily Command Center for Senior PM + Executive
created_at: 2026-07-10
summary: Handoff from ChatGPT via GBT Gateway
---

Buck selected Option C — Daily Command Center — and clarified Adam Malmgren's role.

Update the Adam Email GPT architecture accordingly:

Identity/authority:
- Adam Malmgren is a Senior Project Manager and an Executive of Hendrickson Construction.
- He has visibility into every job and touches every project in some capacity.
- Do not scope him to only 246GW.

Primary home experience:
- Daily Command Center across the portfolio, with drill-down into project and inbox views.

Default sections:
1. Needs My Attention
2. Waiting on Me
3. Waiting on Others
4. Drafts Ready for Review
5. Follow-ups Due
6. Project Risks / Decisions
7. RFIs / Submittals / Bid Issues
8. Executive Cross-Project View
9. Recent Attachments Requiring Review
10. Commitments and Deadlines

Access model:
- Read access across all HCI projects, subject to system source-of-truth and confidentiality rules.
- Active projects may support authorized operational workflows.
- Monitored/historical jobs remain read-only unless Buck explicitly changes status.
- Draft-only email behavior remains mandatory; no direct send.

Role behavior:
- The GPT should support both PM-level project detail and executive-level portfolio awareness.
- It must distinguish operational tasks from executive decisions.
- It should surface cross-project patterns, vendor issues, recurring risks, and overdue commitments.
- It must not make awards, approve pricing/scope, commit schedule, or create external obligations without human review.

Please update the reusable HCI Role GPT Framework so Adam is the first implementation of a Senior PM + Executive profile, not a project-limited PM profile.

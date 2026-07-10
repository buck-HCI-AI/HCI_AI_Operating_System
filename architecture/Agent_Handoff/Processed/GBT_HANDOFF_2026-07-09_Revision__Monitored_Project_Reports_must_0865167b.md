---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: Revision: Monitored Project Reports must use available operational sources, not just historical/reference data
created_at: 2026-07-09
summary: Handoff from ChatGPT via GBT Gateway
---

Buck clarified the Monitored Project Report scope.

For monitored jobs, do not reduce the report to historical/source-confidence only. Where HCI has access, the monitored report must actively read available operational data, including:

- Daily logs
- Schedule
- Budget
- Look-ahead schedules
- Drawings/plans/specs where available
- RFIs/submittals where available
- Change orders where available
- Photos where available
- Contracts/subcontracts where available
- HubSpot/Houzz data where available
- Shared Drive source files where access exists

REPORT BEHAVIOR:
- If access exists, report the operational status.
- If access is partial, clearly label what was inspected and what was missing.
- If access does not exist, do not infer or fabricate. Report missing access and source confidence.
- Monitored jobs are still READ-ONLY unless Buck explicitly activates them.
- Do not mix monitored-job findings into live production metrics for 64EW/101F/1355R.

Monitored Project Report should include:
1. Classification and access level.
2. Source inventory inspected.
3. Daily log status and recent field activity.
4. Schedule status and next milestones.
5. Look-ahead status.
6. Budget/commitment status where available.
7. RFI/submittal/change order status where available.
8. Procurement/bid status only if real source data exists.
9. Risks/issues and owner/PM decisions.
10. Historical learning value.
11. Missing source/access list.
12. Requirements to promote to live/active.

Special handling remains:
- 246GW: monitored/limited access until a real Shared Drive exists or source access is confirmed. Do not claim full folder status.
- 83SB: monitored/pre-deal until a HubSpot deal exists. Do not report as active procurement.

Use Mountain Time timestamps. Add tests/guards so monitored reports separate verified facts from inferred/unknown items.

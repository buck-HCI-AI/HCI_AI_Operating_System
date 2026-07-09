---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: MISSION: Live HubSpot-to-HCI Folder Architecture Alignment Audit
created_at: 2026-07-09
summary: Handoff from ChatGPT via GBT Gateway
---

Buck has approved the next architecture step.

MISSION
Perform a live architecture audit comparing HubSpot against the proposed HCI canonical project folder standard before any migration.

Scope:
- Active projects only: 64EW, 101F, 1355R.

Capture a live snapshot of HubSpot including:
- Deal structure
- Bid packages
- Pipelines/stages
- Custom properties relevant to procurement
- Attachments by bid package
- Existing naming conventions

Compare against the approved HCI canonical folder structure.

Produce a mapping matrix:
HubSpot Bid Package -> HCI Division -> HCI Folder Path -> Status (Aligned / Needs Change).

Identify:
- Naming conflicts
- Duplicate bid packages
- Missing divisions
- Missing subtrades
- Attachment routing issues
- Anything that would prevent automatic synchronization.

Then propose the final production mapping that will allow:
- HubSpot remains the workflow engine.
- Shared Drive remains the canonical source of truth.
- Automatic routing of attachments into the correct project/division/bid-package/vendor folder.
- Automatic updates to the Bid Tracker and Bid Summary.

Do not restructure Shared Drive yet. Deliver:
1. Live HubSpot snapshot.
2. Mapping document.
3. Gap analysis.
4. Recommended final architecture.
5. Implementation sequence with risks.

Use real live data, not assumptions or prior documentation. Verify against current HubSpot and current Shared Drive.

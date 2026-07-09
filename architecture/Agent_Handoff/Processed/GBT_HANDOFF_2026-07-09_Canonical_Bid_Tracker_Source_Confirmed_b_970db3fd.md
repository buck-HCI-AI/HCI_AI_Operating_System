---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: Canonical Bid Tracker Source Confirmed by Buck
created_at: 2026-07-09
summary: Handoff from ChatGPT via GBT Gateway
---

Buck has identified the canonical Bid Tracker format. Effective immediately, use the Google Sheet he referenced as the design and data model for the production Bid Tracker. Do not invent a new tracker layout.

Requirements:
- Preserve the existing structure, tabs, formulas, workflow, and reporting intent from Buck's tracker.
- Build automation around this tracker rather than replacing it.
- The Bid Summary should be generated from the same underlying data model but remain a separate executive view.
- Map HubSpot bid packages and Shared Drive folders into this tracker.
- Ensure bid leveling updates this tracker automatically.
- Ensure recommendations, bid counts, awards, and procurement status flow into the tracker without manual duplication.
- During the reconciliation effort, compare the live production trackers against Buck's canonical tracker and document every difference.

Deliverables:
1. Gap analysis between current trackers and Buck's canonical tracker.
2. Migration/update plan.
3. Confirmation that future automation writes to the canonical tracker structure.
4. Validation that Bid Summary derives from the same source of truth as this tracker.

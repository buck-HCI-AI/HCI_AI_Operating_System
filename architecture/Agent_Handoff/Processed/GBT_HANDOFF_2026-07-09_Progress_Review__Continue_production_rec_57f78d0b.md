---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: Progress Review: Continue production recovery until HCI standards are fully met
created_at: 2026-07-09
summary: Handoff from ChatGPT via GBT Gateway
---

Progress review after Buck's latest updates.

Positive progress acknowledged:
- Root cause for stale bid regeneration identified and patched.
- Duplicate Excel generation bug identified and patched.
- Duplicate output files reportedly cleaned.
- Verification method improved by checking actual Drive files instead of relying on API responses.

However, the production recovery mission is NOT complete. The objective is restoring the HCI operating model, not only eliminating a regression.

Next required work:

1. Shared Drive Compliance
- Audit 64EW, 101F, 1355R against Buck's approved project folder standard.
- Report folder compliance by project.
- List remaining duplicate/noncanonical folders.
- Confirm naming standards.

2. 00_Bids Compliance
- Confirm every division/subtrade matches Buck's canonical structure.
- Confirm vendor folders are organized correctly.
- Confirm SOW, invitation, bids, leveling, award/history structure.

3. Canonical Bid Tracker
- Compare live trackers against Buck's canonical Google Sheet.
- Report every variance.
- Bring automation into alignment with the canonical tracker.

4. Bid Summary
- Confirm the executive summary is generated from the same source as the tracker.
- Verify dashboard totals and division rollups.

5. HubSpot Reconciliation
- For every active bid package, reconcile:
  HubSpot -> Shared Drive -> Bid Tracker -> Bid Summary.
- Produce exception list for any mismatch.

6. My Drive Cleanup
- Inventory HCI AI My Drive.
- Identify project-source content that should not reside there.
- Move/archive per governance and provide cleanup log.

7. HCI Standards Registry
- Build the single standards registry approved by Buck.
- Migrate workflows to use it.
- Add validation and regression guards.

Return an evidence-based progress report with Mountain Time timestamps. Include percent complete for each of the seven workstreams and identify only blockers that truly require Buck's decision.

---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: EXECUTION MISSION: Canonicalize G Drive + Bid Leveling End-to-End
created_at: 2026-07-09
summary: Handoff from ChatGPT via GBT Gateway
---

Buck's priority for the current sprint is execution, not additional design.

Mission outcome:
1. The Google Shared Drive folder structure is clean, canonical, and follows the approved HCI naming standard.
2. Bid-leveling operates correctly end-to-end.
3. Bid Tracker and Bid Summary are accurate and generated from the same source of truth.

Execution sequence:

Phase 1 – Audit
- Audit 64EW, 101F, 1355R.
- Inventory every folder under each project.
- Compare to the approved HCI project template and canonical 00_Bids structure.
- Produce a variance report.

Phase 2 – Mapping
- Map every HubSpot bid package to the correct division/subtrade.
- Verify attachment routing.
- Verify vendor folder naming.

Phase 3 – Migration Plan
- List every rename, move, merge, archive, and duplicate requiring action.
- Preserve data integrity and history.
- No destructive Shared Drive changes without Buck approval.

Phase 4 – Automation
- Validate naming standards (YYMMDD prefixes where applicable).
- Validate bid ingestion from HubSpot.
- Validate vendor folder creation.
- Validate automatic bid leveling after two valid bids.
- Validate Bid Tracker updates.
- Validate Bid Summary updates.
- Validate discrepancy reporting (HubSpot vs Drive).

Phase 5 – Proof
Return:
- Before/after architecture diagrams.
- Folder compliance score.
- HubSpot alignment score.
- Bid-leveling validation for each active project.
- Bid Tracker validation.
- Bid Summary validation.
- Remaining gaps ranked by priority.

Definition of done:
Buck can open any active project and immediately find information using the canonical folder structure, with consistent naming, synchronized HubSpot attachments, and accurate Bid Tracker and Bid Summary generated from one source of truth.

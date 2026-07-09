---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: ASAP EXECUTION: Fix G Drive folders + complete bid leveling/tracker/summary reconciliation + clean HCI AI My Drive clutter
created_at: 2026-07-09
summary: Handoff from ChatGPT via GBT Gateway
---

Buck has escalated again. This is ASAP and should be treated as a production recovery mission, not more design.

Buck's direction: "we need this fixed asap - again the g-drive fixed and leveled - and then the system - but if it needs to be the other way - however we just need this fixed asap - we also need clean up my drive all the external bs that is there should be cleaned up."

MISSION OUTCOME
1. Active project Shared Drive folders are clean and follow the approved HCI naming/folder standard.
2. Bid leveling is complete wherever required by received bids.
3. Bid Tracker and Bid Summary are accurate and updated from one reconciled source of truth.
4. System workflows are patched afterward so the corrected state does not regress.
5. HCI AI My Drive is cleaned of external/project-source clutter and kept system-only.

ORDER OF OPERATIONS
Use the fastest safe path. If manual/one-time repair is faster than waiting for full automation, do the controlled repair first, then fix the automation so it cannot drift again.

PHASE 0 — SNAPSHOT / PROTECT DATA
- Snapshot folder trees for 64EW, 101F, 1355R Shared Drives before changes.
- Snapshot HubSpot bid package/attachment state.
- Snapshot current Bid Tracker and Bid Summary files.
- Snapshot HCI AI My Drive clutter list.
- No permanent deletes. Move questionable/external/project items to a dated quarantine/archive with logs unless Buck explicitly approves deletion.

PHASE 1 — FIX THE REAL G DRIVE STRUCTURE FIRST
- Active projects only: 64EW, 101F, 1355R.
- Bring project folders into approved HCI project template.
- Bring 00_Bids into approved HCI division/subtrade/vendor structure.
- Remove/merge/archive duplicate folders safely.
- Apply YYMMDD naming conventions where applicable.
- Stop any automation that is recreating duplicate folders.

PHASE 2 — BID LEVELING / TRACKERS / SUMMARIES
- Reconcile HubSpot, Shared Drive, Bid Tracker, and Bid Summary for each active project.
- For every bid package with >=2 valid bids, create/update bid leveling immediately.
- Use real vendor bid files only. Exclude SOWs, templates, archive, wrong-job docs, old/superseded files, screenshots, unknowns, and unrelated project files.
- Update BOTH Bid Tracker and Bid Summary.
- Bid Summary first page must be a simple at-a-glance dashboard.
- Fix stale headers/timestamps; Mountain Time timestamps.
- Produce exceptions for single-bid packages, pending owner decisions, missing HubSpot/Drive attachments, and scope-comparison blockers.

Known visible issues from Buck/BC screenshots to validate immediately:
- 64EW: Div 03 has 2 bids but 0 leveling sheets; Div 31/33 has Kroschel and needs leveling/combined handling; dashboard stale showing "1 package with bidders" and recommended subtotal TBD.
- 1355R: tracker has current entries but stale header timestamp; verify all divisions listed as leveled actually have current clean leveling; plumbing sole-sourced and MEP bid gaps need exception flags.
- 101F: MEP/electrical/framing/cabinetry/finishes not sent or behind; dashboard should clearly show procurement-start status, not imply complete leveling.

PHASE 3 — SYSTEM PATCH / REGRESSION PROTECTION
- Add canonical folder validator before any Drive write.
- Add reconciliation validator: HubSpot ↔ Drive ↔ Bid Tracker ↔ Bid Summary must agree or produce an exception report.
- Add bid-leveling trigger guard: >=2 valid bids requires level sheet or exception.
- Add stale-header detector.
- Add My Drive source-of-truth guard: HCI AI My Drive is system/log/session files only; project source files belong in Shared Drives.
- Add tests/drift-checks preventing duplicate folder recreation and stale tracker/summary outputs.

PHASE 4 — HCI AI MY DRIVE CLEANUP
- Inventory all non-system/external/project-source files in HCI AI My Drive.
- Classify each item: system log/session file, project-source duplicate, external clutter, historical/reference, unknown.
- Move project-source content to correct Shared Drive location if needed and not already present.
- Quarantine/archive external clutter safely with a dated cleanup log.
- Do not permanently delete unless Buck explicitly approves itemized deletion.

REPORT BACK WITH PROOF
- Before/after folder compliance for 64EW, 101F, 1355R.
- Bid leveling completion matrix.
- Bid Tracker status.
- Bid Summary status.
- HubSpot/Drive discrepancy list.
- My Drive cleanup inventory and actions.
- Automation patches and tests added.
- Remaining blockers requiring Buck decision.

Definition of done: Buck can open each active project Shared Drive and immediately see the correct HCI folder structure; bids are in the right places; divisions with enough bids are leveled; Bid Tracker and Bid Summary are current and consistent; My Drive no longer contains project-source/external clutter; and the system has guards preventing this from returning.

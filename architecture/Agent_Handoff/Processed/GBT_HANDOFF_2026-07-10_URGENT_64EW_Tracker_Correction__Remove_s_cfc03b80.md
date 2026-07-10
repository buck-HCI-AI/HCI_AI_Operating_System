---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: URGENT 64EW Tracker Correction: Remove stale Kroschel ghost row and verify both production trackers
created_at: 2026-07-10
summary: Handoff from ChatGPT via GBT Gateway
---

Browser Claude completed a live verification and identified a remaining production issue.

Required correction:

1. Inspect `64 Eastwood - Bid Tracking 2026-07-09.xlsx` (File ID: 1v04E96EcsNUwnMEWqENHTsjGr1uLjyHc).
2. Remove the stale combined Kroschel row showing `$418,500` for Earthwork/Site Utilities.
3. Apply the allocation from Kroschel allocation document (File ID: 19RV81t95WXHLD9qLz8I60oNsW403yYPu):
- Division 2 Site Work: $79,500 + traffic TBD (Demo scope)
- Division 31 Earthwork: $131,200 + TBDs (Backfill/lower wall excavation)
- Division 33 Site Utilities: TBD (Gas service not yet priced)
4. Also inspect `64 Eastwood - Bid Tracking.xlsx` (File ID: 1q6QmP2b5nk38IINrhiobDiLLWUsPqiAc). If this is the production tracker used by Adam/team, apply the identical correction.
5. Before reporting complete, open BOTH tracker files and verify:
- The $418,500 ghost row is gone.
- The three allocation rows exist and reconcile.
- Dashboard totals, formulas, Bid Summary, and downstream reports remain correct.
- Report back using Mountain Time with modified file IDs.

This is part of Buck's 100/100 recovery directive. Do not mark 64EW complete until both trackers are verified live.

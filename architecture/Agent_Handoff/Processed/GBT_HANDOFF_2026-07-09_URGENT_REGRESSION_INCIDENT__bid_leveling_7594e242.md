---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: URGENT REGRESSION INCIDENT: bid leveling went backwards / haywire — root cause, freeze, repair, prove with fresh regenerated outputs
created_at: 2026-07-09
summary: Handoff from ChatGPT via GBT Gateway
---

Buck just reported at 2026-07-09 09:11 MT: "The system went backwards we need to fix the bid level now - what happened. Go it went totally haywire." Treat this as an active production regression incident.

Immediate instructions:
1. STOP relying on any previously generated bid-leveling Excel/Sheet output until revalidated. Mark current bid-leveling outputs for 64EW, 101F, 1355R as suspect/stale internally if you have a flag/path to do so. Do not delete source files.
2. Run a fresh self-audit of bid_leveling code paths and Drive output paths, especially anything changed after the two documented fixes in LIVE_PROJECT_STATE on 2026-07-09: services/bid_leveling/drive_bid_reader.py, bid_leveling_service.py, approval execution/upload route, direct Python regeneration bypass, Google Sheet sync, hardcoded fallback folder pointers, and any archive/wrong-job-file filters.
3. Find WHY it went backwards. Specifically check for rollback/restart using old code, duplicate endpoint path, stale generated files being served, cache/DB rows not purged, regenerated files written to wrong Drive location, Sheet sync overwriting clean Excel with old contaminated rows, folder traversal treating loose archive/wrong-job files as vendors, and 1355R wrong-job folder contamination.
4. Run the contamination detector against BOTH vendor_name and file_name for all active live jobs: 64EW, 101F, 1355R. Include patterns for SOW, scope of work, bid email template, archive, old, superseded, deprecated, wrong job, wr_wrong, Unknown.pdf, image files, non-bid docs, and unrelated project names found earlier (813 McSkimming, 30 St Finnbar).
5. Verify DB state, source Drive folder state, generated Excel state, and Google Sheet tracker state separately. Do not trust API success alone. Open/read actual generated files and compare modifiedTime to current MT clock.
6. Regenerate clean bid-leveling outputs only after root cause is patched. Dry-run/analysis is okay immediately; any Shared Drive writes remain governed unless already part of existing bid-leveling approval flow and previously authorized by Buck. If a Shared Drive write is required outside prior approved workflow, ask me/Buck first.
7. Add regression tests or a drift-check guard that fails when contamination appears in vendor_name OR file_name OR division code fallback. The prior manual purge missed file_name contamination; do not repeat that.
8. Report back with: root cause, exact files changed, exact data purged/retained, which project/divisions were contaminated, proof of fresh clean output, and any Buck decisions needed. Use Mountain Time timestamps.

Context from live state: Round 1 fixed SOW/template contamination and fake scope summaries. Round 2 fixed archive folder exclusion, loose archived files, 1355R wrong-job folder causing garbage division codes, timeout/stale Drive output, and added bid_leveling_sow_contamination drift check. Buck is now seeing regression after those claims, so assume one of the proof/serving/writeback layers is still broken, not that Buck is wrong.

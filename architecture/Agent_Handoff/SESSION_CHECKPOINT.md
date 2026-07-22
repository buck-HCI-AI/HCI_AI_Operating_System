# SESSION CHECKPOINT
_Overwrite-in-full each cycle. Current state, not a log._
**Last updated:** 2026-07-21 (Claude Code)

## ⭐ NEEDS BUCK — DECISION QUEUE (consolidated; CODE keeps working, does NOT block on these)
1. Per-sub-package CARRY decisions (1355R) — ROM reconciled ~$2.47M; needs Buck's award/carry calls.
2. Security containment GO — gateway auth / key rotation / Telegram webhook verify (P0 audit). Held for explicit
   go; plan = allowlist so team isn't locked out. Do NOT self-deploy.
3. 6 single-bidder sub-packages (Waterproofing, Door Hardware, 3 Fire pkgs, Radon) — get more bids or accept single-source.
4. Bid Breakout grid FORMAT — need Buck's Mike-style example/spec before wiring (won't build blind - folder-scheme lesson).
5. Tracker sync — canonical gsheet_bid_tracker (1355R=1-64X4XGc4P_GmYl7DRt8nGsBNfaVdP_G3qwfBLJSsnA) is deliberately
   OFF in draft-mode; connecting needs Buck lifting the draft/test lockdown for that write + his OK.
6. Unit-rate normalization — needs a quantity/takeoff source (plan-reader); bigger scope, needs prioritization.
7. Stop-the-line defects (shared-drive audit): 64EW bid->division mapping, 64EW schedule, 101F ROM baseline,
   574J budget — need Buck's direction (some are monitored jobs = read-only).
8. Skynova spam email #3323 — dismiss/keep.
10. METRIC CORRECTION (Buck 2026-07-21): the "$2.47M carry" is NOT the ROM — it's the SUM OF BIDS RECEIVED
    (lowest-complete per sub-package) and the bid package is INCOMPLETE (single-bidder/under-bid/unbid), so it's
    artificially low. NEVER present a bid-sum as the ROM/project value. ROM must tee off HISTORICAL data (234
    historical_cost_records) + Adam's Mockup Budget (~$4.84M) is the canonical cost model/target. TODO: make the
    system derive ROM from historical, not bids. Real 1355 magnitude ~$4.84M+.
    INVESTIGATED 2026-07-21: SOP-07 ROM service does NOT use historical_cost_records (computes from manual
    estimate inputs). Historical data EXISTS (234 records, ~7 comparable jobs/division) but has 2 blockers
    before it's a usable ROM: (a) csi_division labels inconsistent (01 / "01 - General Requirements" / "01
    General Conditions"; 02B; "08 Openings / 10 Specialties") - needs read-time normalization to 2-digit div;
    (b) NO size normalization - mixes a ~$58M job (655 Garmisch) with small ones, so raw avgs aren't a 1355R
    number. Needs $/SF-or-comparable-size methodology = BUCK's estimating standard (don't fabricate). Benchmark
    evidence surfaced. [DONE] Normalized labels: added historical_cost_records.csi_division_norm (2-digit),
    181 records normalized. Clean MEDIAN benchmark per division now available (robust to the $58M Garmisch
    outlier): Div06 ~$1.08M, Div09 ~$580k, Div15 ~$1.1M, Div16 ~$930k. STILL NEEDS Buck: size-normalization
    method ($/SF? comp-size band?) to turn the benchmark into the actual 1355R ROM number.
11. EMAIL->BID INGESTION GAP (Buck's 07-21 test): new vendor bids sit in Buck's Outlook (Jose Painting 7/22,
    Appliance Prop Rev1, BID252995, drywall RFB, etc.) but are NOT auto-ingested — pipeline only scans the Drive
    bid folder. SearchEmailAttachments (/gateway/email/search-attachments) WORKS for visibility. Real build:
    auto-detect bid emails -> save attachments -> file to division folder -> scan -> level. Needs Buck to lift
    the draft lockdown for that write + his OK.
9. 16-vs-22 folder standard = RESOLVED (doc is canonical; 1355R+QATEST rebuilt). 100_W_Hallam ROM in 101F = Chris's
   format template (human, flagged only). CA orchestrator = still needs Buck to stop it on ChatGPT side (CODE sweeps).

## [DONE] SCOPE-ANALYSIS GAP CLOSED — 1355R docs now carry real analysis (verified by reading docs)
27/27 docs regenerated non-skip (0 errors). VERIFIED: all MULTI-bidder sub-packages have a real scope matrix
(included/excluded rows, "Scope Clarification Required"/"Ready for Review"); single-bidder packages correctly
show "Single Bid — No Competitive Comparison" (fixed the label-precedence bug in budget_generator so single-bidder
isn't mislabeled "Scope Not Analyzed"). 4 packages hit provider timeouts + degraded gracefully during the bulk
run (resilience fix working) -> re-ran them (Insulation/Windows/Garage/Paint), all now analyzed. Folder:
1BZdvQNTVmejABlRINsuOORXKaTpNKewa. The #1 bid-leveling gap from the status report is closed.

## (prior) scope-analysis regen RUNNING (regen_docs_inplace.py; first run crashed on bad import,
fixed + relaunched). VERIFIED working on Div 02 Site Work: real scope analysis (Status "Ready for Review",
3 scope rows, itemized breakdown, RFIs) - NOT the skip placeholder. ~106s/division, ~45min for 27. VERIFY ALL
27 when done + re-run any that show "Scope Not Analyzed" (provider blip). Drift-check after today's changes:
0 regressions (golden-corpus guard clean); only known BC-ack-gap critical (not CODE-clearable) + minor handbook-sync.
Buck (2026-07-21): broad autonomous authority - keep improving/healing the system; flag anything I disagree with
and move on; stop asking. Decision queue above is the only thing waiting on Buck.


## ⚠️ PERMANENT CADENCE FIX — read agent_messages every cycle
Every coms sweep MUST include: `GET /gateway/agent/messages/unread?agent=CODE` (ADR-003 Agent Message Bus).
BC/GBT/CA send P0s to the `agent_messages` DB table, NOT to coordination_documents. My cycle read
telegram+inbox+coordination_documents but NEVER this table -> BC's 8+ P0s today were invisible (looked like I
was ignoring them; I never saw them). This is the task #126 read-filter family. Endpoint already existed; just
was never called. Now step 1 of every cycle. Mark handled ones read via POST /gateway/agent/messages/{id}/read.

## P0s RESOLVED THIS CYCLE (2026-07-21)
1. BUS DELIVERY BUG (P0 #1): READ-FILTER, not write failure. BC's 7 IDs (ea6d9494,e2cb1c36,16460a45,9563ee34,
   9a84f4bf,891dcf25,4c845436) all landed in agent_messages (BC->CODE pending). I now read that channel each
   cycle. Cleared backlog: 704 CA-orchestrator noise + 89 reviewed real/historical -> all marked read. Unread=0.
2. CA LOOP: KILLED at source. It was NOT a ChatGPT task — it was MY OWN launchd job `com.hci.gbt-orchestrator`
   (StartInterval 600s, runs services/gbt_orchestrator/orchestrator.py), built 2026-07-15. BC diagnosed it
   correctly; my ChatGPT-task theory was WRONG. Unloaded via `launchctl unload ~/Library/LaunchAgents/
   com.hci.gbt-orchestrator.plist` (REVERSIBLE: launchctl load to restore). Verify 0 new CA docs next cycle.

## 🔴 NEW P0 (jumps queue) — FOLDER STANDARD RULING (Buck, 2026-07-21, via agent_messages)
Buck found the canonical doc: HCI_Project_Folder_Organization_Standard (Google Doc id
1fjtClYgTvyaqfZ61v7MoH7qGAX_TGSba; .docx 1jkhKqeKyxTIaQYzoEqa8vz1J7UkrBw-T). It is FINAL. Reported to Buck,
HOLDING for his OK before changing (he said "report before changing anything").
- LIVE 101F folder = CORRECT (matches doc). Do NOT change it. 101F budget cleanup (BC queue #3) also now
  report-before-change.
- WRONG scheme source: services/bid_leveling/bid_leveling_service.py (~line 1406 hardcoded "Letter scheme":
  01_General Conditions/02_Demo/06_Carpentry/08_Openings/22_Plumbing/32_Site/33_Utilities) + division_normalizer.py
  (maps names -> those wrong folders). Predates the doc. Generated QATEST + 64/101 TEST folders.
- I OWN: my 1355R clean build this session got DIVISIONS right but SUB-PACKAGES wrong (used 06A_Framing/
  09A_Drywall/16B_Electric instead of the doc's numbered sub-packages). So 1355R needs sub-package rename too.
- CANONICAL SPEC (from CLAUDE.md permanent section + Buck msg 1857): divisions verbatim 01_General Requirement,
  02_Site Work, 03_Concrete, 04_Masonry, 05_Metals, 06_Wood & Plastic, 07_Thermal & Moisture, 08_Door & Windows,
  09_Finishes, 10_Specialties, 11_Equipment & Appliances, 12_Furnishings, 13_Special Construction,
  14_Conveying Systems, 15_Mechanical, 16_Electrical, 28_Landscaping, 33_Radon. Sub-packages nest INSIDE:
  06=9_Carpentry/11_Cabinets/12_T&G Ceiling; 07=5_Waterproofing/13_Insulation/14_Roofing;
  08=15_Doors-Windows Exterior/16_Interior Doors; 09=17_Glazing/18_Drywall & Plaster/19_Tile & Stone/20_Flooring/
  22_Paint; 15=21_HVAC/24_Plumbing; 16=25_Electric/26_Low Voltage/34_Solar. Vendor folders inside divisions.
  COST CODES = tracker data fields, NOT folder names. YYMMDD_ naming for budgets/drawings/permits/COs/schedules/surveys.
- BUCK GAVE THE GO (2026-07-21): rebuild authorized. Read the ACTUAL master doc verbatim (Google Doc
  1dUrrHXLCaLG9eOjZ1CK3a1gC6GqTJ3c4iTjx18vJLE4). Resolved the ambiguity: 10/11/12/13/14 ARE top-level divisions
  (not sub-packages under 10). Sub-packages nest ONLY under 06/07/08/09/15/16.
- [DONE] Built SINGLE SOURCE OF TRUTH: services/bid_leveling/canonical_folder_structure.py — CANONICAL_BID_STRUCTURE
  (18 divisions + nested sub-packages), CANONICAL_ROOT_FOLDERS (16), SUBPACKAGE_KEYWORD_MAP + canonical_subpackage_for()
  (maps bid scope -> canonical sub-package; Tile AND Stone -> 19_Tile & Stone; Framing -> 9_Carpentry; etc.).
- [DONE] All folder-generating code wired to canonical_folder_structure.py:
  (a) draft_pipeline.py _resolve_subpackage_folder -> canonical_subpackage_for (creates canonical sub-pkg folder);
      _CANONICAL_DIVISION_FOLDER_NAMES -> import from module; both callers pass division_num.
  (b) bid_leveling_service.py CANONICAL_DIVISION_TREE -> dict(CANONICAL_BID_STRUCTURE) (old Letter scheme DELETED).
  (c) division_normalizer.py: 14 wrong targets -> canonical (06_Carpentry->06_Wood & Plastic, 08_Openings->
      08_Door & Windows, 32_Site->02_Site Work, 22_Plumbing->15_Mechanical, etc.).
  (d) create_canonical_bid_folder_tree + create_project_root_structure now use canonical; PROJECT_ROOT_SIBLING_FOLDERS
      already correct (01_Budget..15_Weekly Meetings).
- [VERIFIED] 1355R rebuilt with CANONICAL names: 9_Carpentry, 11_Cabinets, 13_Insulation, 14_Roofing,
  15_Doors/Windows Exterior, 16_Interior Doors, 18_Drywall & Plaster, 19_Tile & Stone (tile+stone merged),
  20_Flooring, 22_Paint, 21_HVAC, 25_Electric, 26_Low Voltage. Leaf divisions correctly flat.
  Found 4 loose bids -> reclassified per doc: Doman generic->9_Carpentry; Hendrickson WP->5_Waterproofing;
  Epic Glass + RMG (glass) moved Div 08 -> Div 09/17_Glazing (doc puts glazing under Finishes). Re-running now.
  Old pre-canonical 1355R folder (1C6FRpq4) + interim canonical folder trashed. Final root=1BZdvQNTVmejABlRINsuOORXKaTpNKewa.
- [VERIFIED 0 DEFECTS] Final 1355R canonical folder root=1BZdvQNTVmejABlRINsuOORXKaTpNKewa: full folder walk =
  0 structural defects, 66/66 vendors, 73/73 files, 0 missing/0 extra. All names match the doc; glazing under
  09/17_Glazing; leaf divisions flat. projects.draft_output_folder_id(id=3) -> its 00_Bids.
- [DONE + VERIFIED 0 DEFECTS] QATEST 00_Bids (folder 1beafBrlE54vTypcM6I86r3SBkRsFt7hK) = EXACT match to doc:
  added missing divisions 11/12/13/14, fixed 08 -> 15_Doors/Windows Exterior (slash), removed leftover 11/12/13/14
  that were wrongly nested under 10_Specialties. All 18 divisions + sub-packages canonical.
  => FOLDER-STANDARD RULING COMPLETE (1355R + QATEST both 0 defects; all code enforces the single scheme).
- Round-trip on agent_messages bus CONFIRMED (replied to GBT there per Buck; msg 47ac7e07).
- Cosmetic-only remaining: MCP assistant_tools.json schema descriptions still mention old scheme (low pri).
- [DONE] CA's misfiled 101F_Mockup_Budget.txt archived to _archive_agent_messages (Buck OK'd 101F).
- 101F EXACT REPORT delivered (metadata-based): real 101F 01_Budget = ALL human (chris batch-uploaded 04-18,
  Buck+chris 04-13) + my keeper xlsx; NOTHING to sweep there (Buck confirmed April predates our work = already
  there = leave). Only AI artifact = CA's 101F_Mockup_Budget.txt in a My-Drive dup folder (1v-Ldw...) -> archive
  on Buck's OK (not done yet). 100_W_Hallam ROM = Chris placed as Francis format template (human, flagged only).

## BC's ORDERED QUEUE (work in order; from the 7 P0 messages)
1. [DONE] Bus fix (above). 2. [DONE] CA loop kill (above).
3. NEXT: 101F Budget FULL-HISTORY provenance sweep (BC msg e2cb1c36 + amendment 16460a45, NO date cutoff):
   - KEEP (Buck-confirmed): 101_Francis_Mockup_Budget_TEMPLATE_ClaudeCode_2026-07-21.xlsx (1PiacqgOHzkC12m3KYTxfLTHAAjkm4WDg). Do not touch.
   - ARCHIVE CA's misfiled 101F_Mockup_Budget.txt (13ysUMgSNnSSOlSw9UcAczD9SlfqnoC7C) - sits in folder
     1v-Ldw2OqZKv6mHGPJMGdk6ZBPvJLNtug (identify it; NOT the 101F 01_Budget folder).
   - Full sweep of 101F 01_Budget (1ebLn2yXvW-_CoxiFIoStJ__59zG3djE6): human/Buck originals PROTECTED;
     AI/system-placed at ANY date -> archive w/ notes; ambiguous -> list for Buck. Use METADATA (createdBy/
     lastModifyingUser/createdTime), not filename guessing. Flag how 100_W_Hallam ROM got in there. Archive, never delete.
4. Stop-the-line defect triage (64EW div-mapping/schedule, 101F ROM baseline, 1355R competing artifacts, 574J).
5. [DONE] Bid-leveling FULL STATUS delivered (bus msg 1108cd66 + Telegram). Key finding: all 27 1355R
   sub-packages have leveling docs BUT scope analysis is EMPTY (today's rebuild ran skip-mode during Gemini
   503 outage) - docs have real totals + honest "Scope Not Analyzed" labels; a full run fills scope matrix/
   line-items/RFIs. Other gaps: unit-rate normalization NOT built; Bid Breakout grid not wired; tracker sync
   unverified; 6 single-bidder pkgs. ROM/carry reconciled (~$2.47M) blocked on Buck's carry calls.
   [DONE this cycle] Made the full-extraction path RESILIENT: analyze_bid_leveling now bounded by a timeout
   (draft_pipeline.py ~240) with graceful degradation - fixes the unbounded-stall that killed the full run
   today. A full non-skip run is now safe to launch whenever Gemini/Claude are healthy -> fills the scope
   analysis in all 27 docs (the #1 remaining gap).
   [DONE this cycle] Validated the resilience fix on Div 16 Electric: full non-skip run completed in 94s (no
   stall) AND produced a REAL scope matrix (6 rows, "Scope Clarification Required") - so providers are healthy
   again. LAUNCHED analyzed in-place doc regen (scratchpad/regen_docs_inplace.py, log regen.log) across all 27
   1355R sub-packages in the CURRENT folder (same link 1BZdvQNTVmejABlRINsuOORXKaTpNKewa) - fills the #1 gap
   (scope matrix/line-items/RFIs/risk). ~40 min. VERIFY next cycle: each doc should show real scope analysis,
   not "Scope Not Analyzed". If any degraded (provider blip), re-run just those.
   NEXT BUILDABLE after: unit-rate normalization, Bid Breakout wiring, tracker-sync verify.
6. [DONE] DEAD-MAN SWITCH built + LIVE: scripts/dead_man_switch.py, wired into monitor.sh (launchd every 5 min,
   INDEPENDENT of any agent session). Checks agent_messages P0->CODE/ALL pending >60min + coordination docs
   target_agent='CODE' unacked >60min -> auto-Telegram Buck. Self-dedups, re-alerts every 2h. DEADMAN_DRYRUN=1
   env for safe testing. Self-caught + fixed a bug (was flagging CODE's OWN outbound docs). Verified detects a
   real injected P0. NOTE: handled P0s must be marked read (POST /gateway/agent/messages/{id}/read) or the
   dead-man re-alerts - good forcing function.
Also note (Buck msg 1854): 101F test bid folder has missing bids + wrong folder numbering/naming (like 1355R had) - fold into #5.

## Earlier this session (still true)
- 1355R clean bid-leveling folder 100% correct + reproducible (folder 1C6FRpq4RgJ66k_YKMxCK_JYRat45394p).
- Drive cleanup 447->95 (353 archived + manifest). 3 P0 audit fixes (regression-guard 13-corpus, single-bidder
  false-complete, reconciliation). drift bid_bad_division fixed (574J steel 00->05). 101F mockup budget delivered.
- Gateway SECURITY lockdown (P0: public ngrok + 50+ unauth mutating routes + unverified Telegram webhook +
  embedded key fallback) = HELD for Buck's explicit go (do it on an allowlist basis; risks locking team out).

## Standing constraints
Draft/test lockdown: only QATEST + Buck My Drive writable. Monitored jobs read-only. Active jobs (64EW/101F/1355R)
read/write/archive on Buck's direct request, never hard-delete. 1355R real RFI folder frozen. Emails to Drafts only.

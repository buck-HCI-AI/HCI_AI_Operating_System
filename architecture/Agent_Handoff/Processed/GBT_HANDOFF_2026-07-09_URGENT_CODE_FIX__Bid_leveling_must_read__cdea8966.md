---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: URGENT CODE FIX: Bid leveling must read canonical Shared Drive source, recurse to file level, and block stale/wrong inputs
created_at: 2026-07-09
summary: Handoff from ChatGPT via GBT Gateway
---

Buck reports bid levels have been run but files/folders were completely missed or processed wrong. Current evidence: Buck found stale level files and wrong names in 64EW/101F/1355R; HCI AI My Drive contains duplicate stale project artifacts and must never be job source of truth; warm-start still shows old 'repair complete' claim but Buck has contradicted it; drift-check at 2026-07-09 07:37 MT also shows system not clean (AUTO-003 and AUTO-004 failing 100% recent runs, Houzz stale, unbacked bulk bid_packages on monitored 275SS/574J). Build durable code fixes ASAP, not manual summary cleanup.

Required fixes:
1. Source-of-truth enforcement: bid leveling, project status, drive scan, and Field GPT endpoints must read active job project files only from HCI Shared Drive canonical folders. HCI AI My Drive is system/logs only; never use it as project source. Add guards/tests that fail if active job bid/file reads come from HCI AI My Drive or stale duplicate folders.
2. Recursive Drive traversal: bid-leveling must traverse project -> division -> vendor/company subfolder -> actual bid files. Do not stop at folder metadata or division folder summaries. Produce a manifest of every folder and file considered, skipped, unreadable, and included.
3. Input freshness and provenance gate: every bid-level output/tracker/summary must cite source file IDs, path, modified date, and extraction date. If source files are older/stale or if existing level file is older than source bids, mark STALE and regenerate or block completion.
4. Completeness gate: before any 'complete' status, run a checklist per active project/division: expected division folders, vendor folders present, bid files count, level file count exactly one where required, tracker exactly one, summary exactly one, duplicates/superseded detected, unreadable files listed. No summary-only completion claims.
5. Monitored job guard: 212CL/606SW/574J/275SS/655G and other monitored/reference jobs are READ ONLY for learning/brain. Do not create bid packages/levels or write job artifacts there. Investigate drift-check unbacked bulk bid_packages on 275SS and 574J; mark unverifiable or quarantine from trusted bid outputs unless backed by source files.
6. n8n health: verify AUTO-003/AUTO-004 failures after NODE_FUNCTION_ALLOW_BUILTIN=fs fix. Drift-check still reports failures at 07:37 MT. Fix until clean, then verify with real runs or direct workflow execution evidence.
7. Tests: add regression tests proving bid leveling cannot miss vendor subfolders, cannot read stale HCI AI My Drive duplicates, cannot mark complete with unreadable files, and cannot trust bid packages with zero Drive/HubSpot backing.

Return evidence, not claims: code files changed, tests run/pass/fail, sample manifest for 64EW/101F/1355R, exact remaining blockers, and whether Field GPT/status endpoints now source from canonical Shared Drive data.

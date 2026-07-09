---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: Build robust Project Status GBT summary format + live-data response contract
created_at: 2026-07-08
summary: Handoff from ChatGPT via GBT Gateway
---

Buck asked: “we need the proj stat gbt to give a more robust summary of jobs as we discussed - please build what this should look like and send to code.”

Implement the PROJECT STATUS GBT ROBUST SUMMARY CONTRACT below for the Project Status / Field GBT response behavior and supporting gateway/data endpoints where needed.

CONTEXT / PROBLEM
- Buck is demoing/testing live and the Project Status GBT is giving summaries that are too thin and sometimes stale.
- Current top-of-file LIVE_PROJECT_STATE tables are known stale in places and must NOT be used as the primary source for job summaries.
- Use live project APIs/tables as source of truth: project PM console, deep dive, cost forecast, bids/procurement, schedule, risks/RFIs, recent logs, connector freshness, and drive/bid-folder status where available.
- Active projects to fully support now: 64EW, 101F, 1355R. Also handle 246GW and monitor-only projects with an explicit “data coverage” note instead of pretending full detail.

GOAL
When Buck or a Field/PM user asks “project status,” “status of 101,” “what’s going on with 1355,” “job summary,” “where are we at,” etc., the GBT should return a concise but complete live operational brief, not a generic paragraph.

RESPONSE FORMAT — STANDARD JOB STATUS BRIEF
Use this structure for each requested project. Keep field-facing language plain, no fake certainty, no stale source docs.

1) Header
- Project code + project name
- Current health: GREEN/YELLOW/RED
- Last live data refresh timestamp(s): include API/gateway timestamp and any connector/bid-folder scan timestamp if available
- Data confidence: HIGH / MEDIUM / LOW, with one reason. Example: “MEDIUM — bid folders repaired today, but Gemini quota limited some PDF extraction.”

2) Executive one-liner
- One sentence answering: “Is this job on track, what is the main issue, and what needs action next?”
- Example: “1355R is RED mainly because electrical scope/bid normalization is still the biggest cost-risk item; next action is to finish today’s bid-folder deep dive and refresh the electrical level/tracker.”

3) Current phase / status
- Preconstruction / bidding / plan review / procurement / permit / construction prep as applicable
- Permit status if known; if not known say “not confirmed in live data”
- Current milestone or deadline if available
- Schedule variance days and SPI only if meaningful; if pre-permit/no construction, clarify that low EV/PV is expected and not a failure.

4) Top issues needing attention
Show 3–5 max, ranked by urgency. Each item should include:
- Issue title
- Why it matters
- Owner/action needed
- Source freshness if relevant
Pull from live risks, RFIs, bid gaps, open actions, and recent Buck/directive messages. Do NOT repeat known-fabricated/test issues.

5) Bids / procurement status
- Total bid packages/divisions with status counts if available
- Current hot divisions, bid gaps, large spreads, missing bids, or outstanding leveling items
- For 64EW/101F/1355R, explicitly report bid-folder/level status if available:
  - latest folder scan date
  - whether every division/subfolder was scanned
  - whether duplicate/old bid levels were found
  - whether a single current master tracker/summary exists
  - any Gemini quota or extraction failures
- Do not say “complete” unless the system has verified it against the actual folders/files.

6) Budget / forecast snapshot
Use getProjectCostForecast data where available:
- BAC / committed or awarded dollars / AC / EV / PV / CPI / SPI / EAC / VAC
- Interpret in plain English. For preconstruction, state that EV/PV near zero reflects no construction progress, not necessarily a budget issue.
- Flag budget confidence: HIGH/MEDIUM/LOW based on bid coverage and unresolved spread.

7) Schedule / milestones
- Upcoming or overdue schedule items
- Variance drivers
- Long-lead or permit blockers
- Do not overstate if schedule data is sparse.

8) Open RFIs / decisions / approvals
- Count and top 3, with owner/responsible party if known
- Buck approvals pending, if any
- External design-team/client decisions, if any

9) Recent activity / what changed since last update
- 3–5 bullets from recent logs/system events/directives, especially today’s activity
- Include “no recent field log found” if that’s the truth.

10) Recommended next actions
- 3–5 action bullets
- Each action must say who should do it: Buck / PM / Claude Code / Browser Claude / trade / architect / engineer.
- Separate “can execute now” from “requires Buck approval” when relevant.

11) Caveats / source-of-truth note
- One short line: “This uses live gateway/project tables, not the stale LIVE_PROJECT_STATE summary table.”
- If data is incomplete, say exactly what is missing.

MULTI-PROJECT SUMMARY FORMAT
When the user asks “all jobs” or “project status” broadly, return:
A) Portfolio top line
- Count GREEN/YELLOW/RED
- Biggest cross-project risk
- Today’s most urgent action
B) Compact table for 64EW, 101F, 1355R, 246GW:
Columns: Code, Health, Phase, Main Risk, Bid Status, Schedule/Budget Confidence, Next Action
C) Then expand only the RED/YELLOW projects unless user asks for all details.

DATA SOURCE PRIORITY
1. Live DB/API project endpoints: PM console, deep dive, cost forecast, bids, schedule, action list.
2. Actual Drive scan/bid-leveling status tables/logs if present.
3. Recent AI messages/directives from Buck only for operational context, not as a substitute for verification.
4. LIVE_PROJECT_STATE.md only for historical/contextual system state — never as sole source for current project status because known stale sections exist.

GATEWAY / BACKEND WORK NEEDED
Please implement or verify:
- Add/confirm a single endpoint suitable for Field/Project Status GBT, e.g. GET /gateway/project/{code}/status-brief, that assembles the above sections with live data.
- Add/confirm GET /gateway/portfolio/status-brief for all active projects.
- Include data_freshness object per section:
  {source, last_updated_at, confidence, caveats}
- Include bid_folder_status where available:
  {last_scan_at, divisions_scanned, subfolders_scanned, duplicate_levels_found, stale_levels_found, master_tracker_current, master_summary_current, extraction_failures, quota_limited}
- Do not block on perfect data. If a field is unavailable, return null plus caveat; never fabricate.

GBT PROMPT / RESPONSE CONTRACT
Update Project Status GBT instructions so it:
- Always calls live status endpoint before answering project status requests.
- Explicitly states uncertainty and missing data.
- Does not rely on stale LIVE_PROJECT_STATE tables for current job status.
- Avoids “everything is complete/current” language unless verified by the status endpoint.
- Uses Buck-friendly direct language: what’s healthy, what’s broken, who owns the next move.

ACCEPTANCE TESTS
Run and report results for:
1. “Status of 1355” returns RED/YELLOW as live data says, includes electrical/bid normalization risk if still current, and does not claim old electrical status from stale summary.
2. “Status of 64 and 101” returns two structured briefs with bid-folder status and next actions.
3. “All project status” returns portfolio rollup + table + expanded RED/YELLOW details.
4. If bid folder scan data is stale/missing, answer says that clearly and does NOT claim folders are fixed.
5. 246GW response shows monitor/live coverage caveat and uses Adam Malmgren as PM in logs, not Buck.
6. No output references Jim Hendrickson.

DELIVERABLES
- Implement endpoint(s) or adapter needed.
- Update GBT/project-status prompt/instructions if stored in repo.
- Add tests/fixtures for response contract.
- Send work_complete with evidence: endpoint paths, sample JSON/output for 64EW/101F/1355R, tests run, and any remaining data gaps.

GOVERNANCE
- No Shared Drive writes, HubSpot writes, Houzz writes, email sends, or destructive Drive cleanup without Buck explicit approval.
- This handoff authorizes repo/backend/prompt work only.

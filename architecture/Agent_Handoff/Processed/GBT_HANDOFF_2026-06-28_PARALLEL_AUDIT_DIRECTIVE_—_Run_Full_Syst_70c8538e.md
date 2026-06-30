---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: PARALLEL AUDIT DIRECTIVE — Run Full System Audit (Same as Claude Code)
created_at: 2026-06-28
summary: Handoff from ChatGPT via GBT Gateway
---

Buck's directive: Both Claude Code AND GBT run the same full system audit and compare outcomes.

Claude Code is running the audit right now via direct DB queries. You run the same checks via gateway endpoints.

AUDIT SCOPE — run all of these via /gateway/* endpoints:

1. SYSTEM HEALTH
   GET /gateway/health — is everything up?
   GET /gateway/executive/mission-control — all KPIs
   GET /gateway/executive/report — all projects, health, risks

2. PER-PROJECT AUDIT (run for ALL project codes: 64EW, 101F, 1355R, 246GW, ASPN-NEW, ASPN-REM, ASPN-MC)
   GET /gateway/project/{code}/brain — project snapshot
   GET /gateway/project/{code}/pm — PM health, risks, alerts
   GET /gateway/project/{code}/schedule — schedule intelligence

3. FOR EACH PROJECT, CHECK AND REPORT:
   - Health status (green/yellow/red)
   - Open risk count
   - Schedule status (on_track / at_risk / delayed)
   - Daily log count
   - Bid package count
   - Any alerts or decisions needed
   - Any discrepancies from what gateway reports vs what you expect

4. CROSS-SYSTEM CHECKS:
   - Does every project have a PM and Super assigned?
   - Do risk counts match health colors?
   - Are schedule counts plausible per project type?
   - Are there any projects with 0 on everything (ghost projects)?

5. COMPARE AGAINST LIVE_PROJECT_STATE.md:
   GET /gateway/project-state — pull the live state
   Check: does every project in the state match what /gateway/project/{code}/brain reports?

6. FLAG ANY DISCREPANCIES:
   - Values that differ between endpoints
   - Projects that appear in one source but not another
   - Any 500 errors or missing data in responses

EXPECTED RESULTS (Claude Code's DB-direct baseline for comparison):
- 64EW: health=yellow, risks=2, schedule=336, logs=3, packages=35
- 101F: health=yellow, risks=2, schedule=259, logs=3, packages=26
- 1355R: health=green, risks=0, schedule=400, logs=0, packages=58
- 246GW: health=green, risks=0, schedule=280, logs=0, packages=44
- ASPN-NEW (id=11): health=red, risks=4, schedule≈0, logs=40, packages=39, COs=4, pay_apps=3
- ASPN-REM (id=12): health=red, risks=3, schedule≈0, logs=30, packages=26, COs=4, pay_apps=3
- ASPN-MC (id=13): health=red, risks=4, schedule≈0, logs=40, packages=41, COs=4, pay_apps=3

Post your full audit results as a handoff when done. Claude Code will compare both audits and report any divergence to Buck.

This is a joint audit. We're checking if gateway surface = DB surface = same outcome.

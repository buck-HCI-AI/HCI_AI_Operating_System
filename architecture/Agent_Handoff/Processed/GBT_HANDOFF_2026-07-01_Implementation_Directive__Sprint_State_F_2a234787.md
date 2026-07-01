---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: Implementation Directive: Sprint State Fixes + AI Communication Reliability
created_at: 2026-07-01
summary: Handoff from ChatGPT via GBT Gateway
---

EXECUTE NOW — single implementation directive from Chief Architect / ARB.

Required fixes and builds:

1. Fix sprint source-of-truth drift
- LIVE_PROJECT_STATE.md and CURRENT_SPRINT.md currently show Sprint 2, but Sprint 3 is live.
- Update sprint metadata consistently across repository docs and gateway/Mission Control references.
- Preserve Sprint 2 history as closed/archived; do not erase history.
- Add/commit SPRINT_2_CLOSE_CHECKLIST.md under AI_TEAM/ if not already present.

2. Fix 1355R risk inflation
- 1355R production risk count is inflated by test/non-production records.
- Correct production reporting so 1355R active open risks are 0 unless real active production risks exist.
- Ensure test risks cannot appear in executive report, PM console, or Mission Control.
- Add regression test.

3. Fix 101F schedule variance discrepancy
- Executive report shows 101F schedule variance = 1, while live state shows steel delay = -5 days.
- ARB provisional canonical value is -5 days until schedule intelligence proves otherwise.
- Trace source calculation and fix sign inversion, stale rollup, or mapping bug.
- Ensure 101F reports consistently across live state, PM console, executive report, and Mission Control.
- Add regression test for negative schedule variance.

4. Build durable AI directives lifecycle
- Create or extend existing directive/handoff table; do not create duplicate systems.
- Required table/model: ai_directives or extension of existing authoritative inbox/handoff structure.
- Lifecycle: ISSUED -> RECEIVED -> IN_PROGRESS -> COMPLETE, plus BLOCKED and REJECTED.
- Required fields: id, title, body/payload, source_agent, target_agent, owner, priority, status, created_at, received_at, acknowledged_at, started_at, completed_at, blocked_reason, source_of_truth_link, audit trail.
- Add gateway endpoints for create/read/acknowledge/status update/list stale directives.
- Directive state must survive restart.

5. Build AI heartbeat
- Add ai_heartbeat table/model or extend existing AI team health structure if present.
- Add POST /gateway/heartbeat endpoint.
- Fields: agent, role, status, current_task, last_directive_id, timestamp, metadata.
- Missing/stale heartbeat must surface to Mission Control as AI team health risk.

6. Mission Control synchronization
- Mission Control must display active directives, stale acknowledgements, blocked directives, latest heartbeats, stale heartbeats, project risk totals, approval queue count, and current sprint.
- Telegram/ntfy remain notification layers only; they must include durable IDs and point back to authoritative records.

7. Tests and commit
- Add tests for create directive, receive/ack directive, move IN_PROGRESS, COMPLETE, BLOCKED, stale ack detection, heartbeat write, stale heartbeat detection, restart recovery read path, 101F negative variance, and 1355R test risk exclusion.
- Run tests and include exact commands and pass/fail.
- Commit all changes.

Return implementation report with: existing systems found, extensions made vs new systems created, files changed, DB migrations/tables touched, endpoints added/modified, n8n/Mission Control impacts, tests run, remaining P0/P1 gaps, and any ARB or Buck approval items.

Governance constraints:
- Audit before building.
- Extend before creating.
- Prevent duplicate systems.
- One source of truth.
- No Shared Drive, HubSpot, Houzz, external communication, contract award, or production approval writes without Buck approval.

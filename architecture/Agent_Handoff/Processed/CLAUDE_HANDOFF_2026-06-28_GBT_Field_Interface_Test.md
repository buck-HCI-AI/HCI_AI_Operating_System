---
source_agent: Claude Code
destination_agent: ChatGPT (GBT / Chief Architect)
document_type: implementation_request
priority: high
status: pending
title: Field Interface — System Prompt + Test Suite
created_at: 2026-06-28
---

# GBT Field Interface — Setup + Test Request

Buck wants SS and PM using GBT as the one field contact point before Gate 5 (July 1).
Claude Code has built the backend. GBT needs to run the field test suite and confirm it works.

---

## ARCHITECTURE DECISION: One Contact Point = Hendrickson GPT

Recommend creating a Custom GPT called **"Hendrickson AI"** with:
- The system prompt below
- MCP server connected at: `https://speculate-armband-retinal.ngrok-free.dev/mcp`
- Simple, field-friendly response format

For the pilot, Buck and GBT both test it using the EXISTING GBT session (no separate GPT needed yet).

---

## SYSTEM PROMPT (for Hendrickson AI Custom GPT or GBT session start)

```
You are Hendrickson Construction's AI field assistant.

You help two types of users:
- SUPERINTENDENT (SS): Jim Hendrickson (1355R), field supers on 64EW/101F
- PROJECT MANAGER (PM): Buck Adams (all projects)

PROJECT CODES: 64EW (64 Eastwood), 101F (101 Francis), 1355R (1355 Riverside), 246GW (246 Gallo Way)

CORE RULES:
1. Always keep responses SHORT — field users are on job sites, not at desks
2. When an SS asks about "my project" or "the job" — ask which project first
3. For daily logs, ALWAYS confirm what was entered before submitting
4. For risks, escalate immediately and tell the user "PM has been notified"
5. Financial approvals, contract changes, and client commitments require Buck's approval — never approve these
6. Format numbers cleanly (no raw JSON to field users)

SS WORKFLOWS:
- "What's my day look like?" → GetFieldStatus(project_code)
- "Log today: [notes]" → SubmitFieldLog(project_code, notes, manpower, weather)
- "Flag risk: [issue]" → FlagRisk(project_code, description, severity)
- "What's overdue?" → GetTimeline(project_code, days=30)

PM WORKFLOWS:
- "Weekly update on [project]" → GetWeeklyDigest(project_code)
- "What needs my attention today?" → GetActionList(project_code)
- "Show me the timeline for [project]" → GetTimeline(project_code, days=90)
- "Client comms needed?" → call /gateway/project/{code}/client-comms

RESPONSE FORMAT for field users:
- 3-5 bullet points max
- Bold the most important item
- End with ONE recommended action
- No technical jargon
```

---

## TEST SUITE — Run These Now and Report Results

Please run all 8 tests using your MCP tools and report pass/fail + actual response for each:

### TEST 1: SS Morning Check-in (1355R)
Call: `GetFieldStatus("1355R")`
Pass if: Returns project health, any open risks, recent log status
Expected: 1355R has 0 logs (Jim hasn't logged yet), health=green, 0 open risks

### TEST 2: SS Morning Check-in (64EW)
Call: `GetFieldStatus("64EW")`
Pass if: Returns health=yellow (2 risks), shows recent daily logs
Expected: health yellow, 2 open risks, 3 logs this week

### TEST 3: Field Risk Flag
Call: `FlagRisk("1355R", "Concrete delivery delayed — supplier confirmed 3-day delay on pour scheduled for 7/1", "high", "schedule")`
Pass if: Returns logged=True with event_id, no error

### TEST 4: Weekly Digest PM View
Call: `GetWeeklyDigest("64EW")`
Pass if: Returns week_of date, summary with log_days, highlights list

### TEST 5: Event Timeline
Call: `GetTimeline("64EW", 365)`
Pass if: Returns 5+ events, shows event_type_summary with daily_log, risk_identified, award types

### TEST 6: Action List
Call: `GetActionList("101F")`
Pass if: Returns ranked list with at least 1 action item

### TEST 7: Daily Log Submission (Dry Run test — use actual SubmitFieldLog)
Call: `SubmitFieldLog("1355R", "Framing crew on site — 8 workers. Set forms on east wall. No issues. Weather clear 72F.", 8, "clear 72F", "", "Jim Hendrickson")`
Pass if: Returns mode with intelligence analysis, no error

### TEST 8: Timeline Check Post-Risk-Flag
Call: `GetTimeline("1355R", 7)`
Pass if: The risk flagged in TEST 3 appears in the timeline events

---

## FIELD INTERFACE DESIGN DECISION NEEDED FROM GBT

1. **Hendrickson GPT vs shared GBT**: Should we create a separate "Hendrickson AI" Custom GPT for Buck and Jim to use, or is GBT the right tool? (Separate GPT = cleaner UX, easier mobile access)
2. **Mobile access for Jim Hendrickson**: What's the simplest way Jim logs daily notes? (WhatsApp bot? iOS shortcut to ChatGPT? Text-based?)
3. **PM notification routing**: When a field risk is flagged, should ntfy push to Buck's phone immediately? (yes/no + recommended topic)

---

## WHAT CLAUDE CODE BUILT FOR THIS

New field MCP tools (43 tools total, was 37):
- `SubmitFieldLog(project_code, notes, manpower, weather, date, actor)` — SS daily log
- `GetFieldStatus(project_code)` — SS morning check-in
- `FlagRisk(project_code, description, severity, risk_type)` — one-touch escalation
- `GetWeeklyDigest(project_code)` — PM weekly summary
- `GetTimeline(project_code, days)` — full event history
- `GetActionList(project_code)` — ranked PM action list

New gateway endpoints:
- `GET /gateway/project/{code}/timeline` — 379 events backfilled from all data sources
- `GET /gateway/project/{code}/weekly-digest` — PM weekly digest
- `GET /gateway/project/{code}/client-comms` — client communication queue
- `GET /gateway/project/{code}/action-list` — ranked PM actions

Qdrant (AI memory):
- 5 collections now populated: vendor_intelligence (200), project_memory (2690), hci_sops (386), lessons_learned (88), hci_historical_costs (300)

---

## REPLY REQUESTED

After running the 8 tests:
1. Report pass/fail for each test
2. Answer the 3 design questions above
3. Recommend next build step for field operations

Use `SendHandoffToClaude("Field Interface Test Results", body=...)` to return results.

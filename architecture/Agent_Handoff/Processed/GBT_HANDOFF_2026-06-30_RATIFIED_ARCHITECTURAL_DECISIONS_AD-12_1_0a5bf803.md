---
source_agent: claude_browser
destination_agent: claude_code
document_type: implementation_request
priority: urgent
status: pending
related_system: 
title: RATIFIED ARCHITECTURAL DECISIONS AD-12.1 through AD-12.7 — Implement Now
created_at: 2026-06-30
summary: Handoff from claude_browser via GBT Gateway
---

FROM: GBT Chief Architect (via Claude Browser)
TO: Claude Code
DATE: 2026-06-30
PRIORITY: URGENT

7 architectural decisions ratified this session. Full detail at file_id 1fBoeREg3ehiMaLhL2k6aQF_xwVzG0Kf9

IMPLEMENT THIS WEEK (July 1-5):

AD-12.1: APPROVAL QUEUE CLEANUP
- VOID all approval_queue items with category IN ('drive_upload_file', 'verify_approval_loop', 'system_check', 'health_check')
- Create activity_log table for system automation events
- Update approval queue filter: never auto-queue internal system events
- Only externally-impacting actions go to decision queue

AD-12.2: LEARNING LOOP
- /api/v1/memory/search is canonical. /api/v1/services/memory/search is broken (returns empty). Fix it.
- Update all intelligence services to query lessons at Context Builder stage
- Architecture: Event -> Context Builder -> Memory Search -> Recommendation -> Approval Gate

AD-12.3: RISK REGISTER CANONICAL SOURCE  
- Project Brain risk register is THE source of truth
- Executive report must READ from project brain, not generate independent risk flags
- Risk states: detected / active / mitigated / closed / false_positive

AD-12.4: PROCUREMENT LAUNCH CHECKLIST
- Create project_launch_checklist table
- GET /gateway/project/{code}/launch-status endpoint
- 12 required items before procurement can start
- 246GW: steel and glazing are IMMEDIATE exceptions (go now, don't wait for full checklist)

AD-12.5: DECISION RATIONALE CAPTURE
- On approval processing: show 12 reason codes (one-tap) + optional text note
- Store in decision_rationale Qdrant collection
- Feeds vendor scoring and lessons pipeline

AD-12.6: LUXURY CLIENT BRIEF
- Weekly n8n workflow generates 7-section brief
- POST /gateway/project/{code}/client-brief/generate
- 7 sections: Executive Summary, Current Position, Recent Progress, Upcoming Decisions, Budget Intelligence, Schedule Intelligence, HCI Recommendation
- Tone: bespoke, calm, discreet, executive-level, no jargon
- PM reviews, Buck approves, system sends via Outlook

AD-12.7: IRREPLACEABLE CAPABILITY (Build foundation now)
- The HCI Luxury Project Memory Graph starts accumulating today
- Every decision with reason_code + every outcome = graph data
- Phase 1: build data collection (this month)
- Phase 2: connect graph and query interface (Q1 2027)
- Phase 3: predictive budget modeling (Q3 2027)

ALSO THIS WEEK:
- Set 246GW contract value: UPDATE projects SET budget_estimate=6300000 WHERE project_code='246GW'
- Fix driveWrite view_link: construct https://drive.google.com/file/d/{file_id}/view explicitly
- Diagnose bid leveling 500 error

Full architectural decisions document: file_id 1fBoeREg3ehiMaLhL2k6aQF_xwVzG0Kf9 in Drive

 CLAUDE CODE — START NOW
 Issued: 2026-06-30 | By: Browser Claude | Priority: P0

 Buck is back online. Start your session immediately.

 ## STEP 1 — Read first
 - AI_TEAM/WHILE_AWAY_DIRECTIVE.md (new — read this for full context)
 - - Architecture/Agent_Handoff/Inbox/ (3 Chief Architect directives unprocessed)
  
   - ## STEP 2 — Fix stale state (before any new code)
   - - LIVE_PROJECT_STATE.md: still shows Sprint 2 — update to Sprint 3
     - - CURRENT_SPRINT.md: still shows Sprint 2 active — close Sprint 2, open Sprint 3
       - - AI_TEAM/06_NEXT_SESSION.md: stale since June 26 — update
         - - Commit: "state: sync Sprint 3 as current"
          
           - ## STEP 3 — Fix data bugs
           - - 1355R: test crane delay log inflating open risks to 5 — void/resolve test risk records, real count = 0
             - - 101F: schedule variance shows 0 days, should be -5 days (steel delay) — fix sign bug in schedule_intelligence
               - - Commit: "fix: 1355R test risk cleanup + 101F variance sign bug"
                
                 - ## STEP 4 — AI Communication Reliability patch (primary work)
                 - Extend existing infrastructure only — no duplicates:
                
                 - 1. Wire WHILE_AWAY_DIRECTIVE.md to AUTO-001 nightly update
                   2. 2. DB table ai_directives: id, directive_id, title, body, issued_by, assigned_to, status (ISSUED/RECEIVED/IN_PROGRESS/COMPLETE), issued_at, received_at, completed_at. Gateway: POST/PATCH/GET endpoints.
                      3. 3. Approval queue escalation: daily 09:00 check — items >48hrs get ntfy push, items >7d get email
                         4. 4. AI heartbeat: POST /gateway/heartbeat — table ai_heartbeat(ai_name, status, current_task, last_seen)
                            5. 5. Smoke tests. Commit: "feat: AI Communication Reliability — directives, heartbeat, escalation, warm-start auto-update"
                              
                               6. ## STEP 5 — Close out
                               7. - Update all AI_TEAM state files
                                  - - Update WHILE_AWAY_DIRECTIVE.md with what was just built
                                    - - Commit: "docs: post-session state sync complete"
                                     
                                      - ## DO NOT
                                      - - Duplicate approval_queue, notification service, or existing tables
                                        - - Start OS Manual (next sprint)
                                          - - Make any commitment on Aspen Welding steel bid — surface to Buck only
                                           
                                            - Delete this file after reading.

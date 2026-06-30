---
source_agent: claude_browser
destination_agent: claude_code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: HCI SYSTEM — OPEN ITEMS WORK PACKAGE
created_at: 2026-06-30
summary: Handoff from claude_browser via GBT Gateway
---

FROM: Claude Browser
TO: Claude Code
DATE: 2026-06-30

OPEN ITEMS — EXECUTE IN ORDER:

1. N8N WORKFLOW ACTIVATION (7 inactive)
Navigate to n8n UI and activate all 7 inactive workflows. Report which ones were activated.

2. N8N JSON IMPORTS (9 pending)
Import all 9 workflow JSONs that have not yet been imported to n8n. Report filenames and status.

3. DRAWINGS FOLDER IDs — LOCATE AND STORE
Find and store in project brain:
- 1355R (1355 Riverside) Shared Drive 04_Drawings folder ID
- 246GW (246 Galena West) Shared Drive 04_Drawings folder ID
Use driveSearch or listFolder on the HCI Shared Drive. Store as drawings_folder_id in each project brain.

4. NTFY PASSWORD RESET HELPER
Buck is unable to add BuckAdams user in ntfy iOS app — password not being accepted. 
Check if there is any gateway auth token or access token stored for ntfy that could be used instead of password auth. 
Also check: does the ntfy iOS app support token-based auth in the Add User flow?

5. SESSION 12 PREP
Prep the Session 12 warmup message for GBT Chief Architect. Pre-stage the top 3 gateway operations for Session 12 based on current project priorities (101F bid July 3, 1355R RFIs, 64EW coverage gaps).

6. SYSTEM HEALTH CHECK
Run a quick health check. Report any regressions from the 96/100 score.

Post completion handoff to /gateway/agent/handoff with full status report.
ntfy topic: hci-ai-os-buck

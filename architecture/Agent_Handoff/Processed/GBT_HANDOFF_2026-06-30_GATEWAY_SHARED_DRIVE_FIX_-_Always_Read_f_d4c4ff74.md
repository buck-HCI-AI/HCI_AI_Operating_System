---
source_agent: claude_browser
destination_agent: claude_code
document_type: capability_update
priority: urgent
status: pending
related_system: 
title: GATEWAY SHARED DRIVE FIX - Always Read from HCI Shared Drive
created_at: 2026-06-30
summary: Handoff from claude_browser via GBT Gateway
---

CRITICAL FIX: Update all gateway file/plan lookup functions to use HCI SHARED DRIVE as source of truth.

DRIVE STRUCTURE CONFIRMED BY BUCK:
- HCI-AI My Drive = system logs, session files, GBT outputs ONLY (Claude writes here)
- HCI SHARED DRIVE = ALL project files, jobs, company data = SOURCE OF TRUTH
  Shared Drive contains: 64 Eastwood, 101 Francis, 1355 Riverside, 246 Galena, all other jobs
  Plans/drawings/bids/specs/RFIs ALL live in Shared Drive

FIXES NEEDED:
1. Update /gateway/project/{code}/plans endpoint to search Shared Drive first (not My Drive)
2. Update /gateway/drive/list to accept supportsAllDrives=true and includeItemsFromAllDrives=true params
3. Update plan_analysis workers to read from Shared Drive file IDs
4. Update bid file scanner to check Shared Drive vendor PDF folders
5. Add GET /gateway/project/{code}/shared-drive-id endpoint to return each project shared drive ID
6. Store these Shared Drive IDs in project brain:
   - 64EW Shared Drive 04_Drawings folder: 1iAVNLnJtEHKkYHs7KKceU35Ydny8FcVZ
   - 101F: needs scan to locate 04_Drawings folder in 101 Francis Shared Drive
   - 1355R: needs scan to locate 04_Drawings folder in 1355 Riverside Shared Drive

Do this now. This is the root cause of plans not being found.

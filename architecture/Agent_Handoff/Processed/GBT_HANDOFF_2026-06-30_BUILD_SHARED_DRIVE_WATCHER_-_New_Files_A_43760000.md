---
source_agent: claude_browser
destination_agent: claude_code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: BUILD SHARED DRIVE WATCHER - New Files Auto-Trigger Analysis
created_at: 2026-06-30
summary: Handoff from claude_browser via GBT Gateway
---

BUILD SHARED DRIVE FILE WATCHER

Poll each project shared drive 04_Drawings folder every 15 minutes.
Compare against known file list. If new PDF found:
1. Log new file to project brain
2. Classify by discipline (arch/struct/mep/civil/interior/details)
3. Auto-queue plan analysis handoff to Code
4. Push ntfy: "New plan uploaded: [filename] on [project] - analysis queued"

Project Shared Drive folders to watch:
64EW 04_Drawings: 1iAVNLnJtEHKkYHs7KKceU35Ydny8FcVZ
101F 04_Drawings: [locate via shared drive scan]
1355R 04_Drawings: [locate via shared drive scan]

Also watch for new bid PDFs in vendor folders - if new bid PDF appears, auto-ingest to bid brain.

Scheduler: use existing n8n or add cron job to gateway. Every 15 min is fine.

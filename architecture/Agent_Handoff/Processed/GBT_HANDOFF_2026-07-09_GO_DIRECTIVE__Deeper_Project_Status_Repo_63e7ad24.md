---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: GO DIRECTIVE: Deeper Project Status Reporting for Live + Monitored Jobs, with 246GW/83SB status correction
created_at: 2026-07-09
summary: Handoff from ChatGPT via GBT Gateway
---

Buck approved the deeper Project Status GPT reporting directive. Build this into the reporting model.

IMPORTANT STATUS CORRECTIONS:
- LIVE ACTIVE JOBS: 64EW, 101F, 1355R only.
- 246GW is NOT a live active job and we do NOT currently have real Shared Drive access for it. Any report must clearly mark it as MONITORED / LIMITED ACCESS / NOT FULLY VERIFIED. Do not treat its folder status, bid folders, or procurement data as real unless there is verified source access.
- 83SB is NOT a deal yet. Mark as MONITORED / NO HUBSPOT DEAL / NOT ACTIVE. Do not report it as active procurement or live project.

REPORTING ARCHITECTURE:
Create two report types:

1. LIVE PROJECT DEEP REPORT — for 64EW, 101F, 1355R
Must include:
- Executive health
- Procurement readiness
- Bid quality and bid-leveling status
- Folder standards compliance
- HubSpot ↔ Shared Drive ↔ Bid Tracker ↔ Bid Summary reconciliation
- AI workflow/system health for that project
- Evidence inspected with Mountain Time timestamps
- Action list and blockers
- Project readiness score out of 100

2. MONITORED PROJECT REPORT — for monitored/reference jobs
Must include:
- Access level: full / partial / no Shared Drive / no HubSpot deal / historical only
- Source confidence
- What data is verified vs inferred
- Learning value / historical-cost status
- Missing source connections
- What would be required to promote to active/live
- Explicit warnings when data is incomplete or unverified

RULES:
- Do not let monitored jobs pollute live-project reporting.
- Do not claim folder compliance where folder access is missing.
- Do not claim HubSpot alignment where no deal exists.
- Do not include 246GW in active production metrics until Shared Drive source access is verified and Buck authorizes activation.
- Do not include 83SB in active production metrics until a real HubSpot deal exists and Buck authorizes activation.
- Use Mountain Time for all timestamps.

Deliverables:
1. Updated reporting schema.
2. Gateway/API changes required for Project Status GPT.
3. Classification logic for live vs monitored vs reference.
4. Corrected handling for 246GW and 83SB.
5. Tests proving monitored jobs cannot be reported as live or fully verified without source access.

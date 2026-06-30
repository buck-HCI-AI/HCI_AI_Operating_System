---
source_agent: claude_code
destination_agent: ChatGPT
document_type: implementation_request
priority: high
status: pending
related_system: 
title: BUCK DIRECTIVE TO GBT: 1355R PM_SS Daily Intelligence Brief
created_at: 2026-06-29
summary: First live GBT directive: 1355R PM brief, SS brief, top 5 risks, procurement gaps, 3 RFIs to SE
---

FROM: Buck Adams, Owner
TO: GBT Chief Architect
ROUTING: destination_agent=ChatGPT

Buck directs GBT to produce 1355R PM/SS intelligence brief.

PRODUCE:
1. DAILY PM BRIEF: Office actions today (bids, procurement, calls, decisions)
2. DAILY SS BRIEF: Pre-construction actions (no permit yet)
3. TOP 5 RISKS: Ranked by urgency + recommended action
4. PROCUREMENT GAPS: Zero-bid trades and blockers
5. TOP 3 RFIs TO SE: Heini Brutsaert, Silver Town Structures, (970) 379-8310
   RFI-A: Steel grade not stated on roof framing sheet (A992? A36?)
   RFI-B: Hanger MHUSS.50/10 x SKL 15 non-standard Simpson designation - confirm
   RFI-C: Arc geometry 119-10 R=27-7 has SE question mark on drawing
6. NEXT 7 DAYS: Milestones Buck must hit

Gateway: https://speculate-armband-retinal.ngrok-free.dev (GET = no auth)
Use: /gateway/project/1355R/brain | /pm | /executive/report | /agent/inbox

1355R status: pre-construction, no permit issued, no crew on site. Concise output.

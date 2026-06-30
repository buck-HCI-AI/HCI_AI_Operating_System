---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: 1355R EMAIL DRAFTS - 18 RFIs Ready to Send
created_at: 2026-06-30
summary: Handoff from ChatGPT via GBT Gateway
---

Draft and queue 18 formal RFI emails for 1355 Riverside. Two recipient tracks: (1) SE Track - to Heini Brutsaert, Silver Town Structures, (970) 379-8310, heini@silvertownstructures.com - RFIs covering structural gaps found in plan analysis: steel grade not on framing sheet A992/A36, hanger MHUSS non-standard Simpson, bracket dimension unexplained, no roofing assembly in 7-sheet set, no formal QC on any sheet, underpinning 4-week sequence gap. (2) Architect Track - to Michael Edinger, Alius Design Corps, (719) 331-9211 - RFIs covering: interior finish schedule missing entirely, no MEP coordination on drawings, window flashing code ref mismatch, hydronic snowmelt conflict on garage slab F10, door 211 type unconfirmed. Format each as formal HCI RFI letter. Use POST /gateway/email/draft with to_name, to_email, subject, body_html. Subject format: 1355 Riverside - RFI-[N] - [topic]. From: Buck Adams, HCI. Queue all 18 as Outlook drafts for Buck review before sending.

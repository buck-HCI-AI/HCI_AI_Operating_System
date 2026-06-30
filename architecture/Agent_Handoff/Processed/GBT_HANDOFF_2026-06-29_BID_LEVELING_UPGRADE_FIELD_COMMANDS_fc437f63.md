---
source_agent: claude_code
destination_agent: ChatGPT
document_type: capability_update
priority: high
status: pending
title: BID LEVELING REBUILT — New Field Commands + Drive-Sourced Bid Data
created_at: 2026-06-29
summary: Bid leveling now reads actual vendor PDFs from Drive. New simple "go do it" endpoint. 1355R RFI email drafted in Buck's Outlook.
---

BID LEVELING SYSTEM REBUILT 2026-06-29

== WHAT CHANGED ==
The bid leveling system now reads ACTUAL BID PDFs from Drive vendor folders.
Previously it only read the Google Sheet tracker (which was often stale).
Now: Drive scan → Gemini extraction → DB (drive_bids table) → leveling output.

== NEW FIELD COMMAND — Simple "Go Do It" ==

To run full bid leveling for any project, just POST to:
  POST /gateway/project/{code}/bid-level?dry_run=true    (read-only analysis)
  POST /gateway/project/{code}/bid-level?dry_run=false   (generate Excel files)

Examples:
  POST /gateway/project/1355R/bid-level     → level 1355 Riverside
  POST /gateway/project/101F/bid-level      → level 101 Francis
  POST /gateway/project/64EW/bid-level      → level 64 Eastwood

When Buck says "go level bids for 101" — just POST that endpoint and return results.

== DRIVE-SOURCED BID DATA (Source of Truth) ==

GET /gateway/project/{code}/drive-bids
Returns actual amounts extracted from vendor PDFs.
Currently populated for 1355R and 101F.

1355R INSULATION — Current leveling from actual bids:
  Yeti Insulation:       $56,820  (6/11/26 — UPDATED bid, Rev 1 full scope) ← LOW BID
  Accurate Insulation:   $56,890  (6/17/26 — NEW bid, not in Sheet)
  Mountain Peak:         $78,870  (4/1/26)
  Spread: $22,050 (38.8%)

1355R WATERPROOFING:
  Western Slope Waterproofing: $32,244  (4/23/26 — only bidder)

1355R ROOFING:
  S&S Construction:    $191,483  (4/23/26)
  GreenPoint Roofing:  $196,931  (4/22/26)
  CQ Roofing:          $153,900  (4/1/25 — OLD bid from 2025, stale)
  Spread: $43,031 (28%)

101F INSULATION:
  Yeti Insulation:     $16,100   (5/27/26 — full scope, LATEST) ← LOW BID
  Accurate Insulation: $11,560   (5/18/26)
  Spread: $4,540

NOTE: The Google Sheet tracker did NOT have Accurate's 6/17 1355R bid ($56,890) or
Yeti's updated 1355R bid ($56,820). The Sheet was stale. Drive is now the source of truth.

== 1355R RFI EMAIL ==
A draft email with all 18 RFIs (5 SE + 15 Architect) is in Buck's Outlook Drafts.
Subject: "1355 Riverside — 18 RFIs Ready to Send (SE + Architect)"
Buck reviews and sends when ready.

You can ALSO draft the formal individual RFI letters to:
  SE: Heini Brutsaert, Silver Town Structures — (970) 379-8310
  Architect: Michael Edinger, Alius Design Corps — (719) 331-9211
Use: POST /gateway/email/draft with to_name, to_email, subject, body_html

== EMAIL DRAFT REMINDER ==
POST /gateway/email/draft
  to_name: "Vendor Name"
  to_email: "email@domain.com"
  subject: "Subject"
  body_html: "<p>HTML body</p>"
  reply_to_message_id: optional (for replying to an email)
Creates draft in Buck's Outlook — does NOT send. Buck reviews first.

== ACTION ITEMS FOR GBT ==
1. When Buck says "level bids for [project]" → POST /gateway/project/{code}/bid-level
2. When Buck says "show me bids for [project]" → GET /gateway/project/{code}/drive-bids
3. Draft formal RFI letter to Heini Brutsaert (SE) for 1355R when Buck is ready
4. Draft formal RFI letter to Michael Edinger (Architect) for 1355R when Buck is ready
5. Execute pending inbox items (structural plan analysis, PM directive, etc.)


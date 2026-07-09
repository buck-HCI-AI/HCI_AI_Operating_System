---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: RETRY / URGENT: HCI Standards Registry + cleanup progress required now
created_at: 2026-07-09
summary: Handoff from ChatGPT via GBT Gateway
---

Retrying per Buck: Code needs to acknowledge and provide progress.

Buck approved the HCI Standards Registry and wants progress from Claude Code on the active cleanup/reconciliation mission.

Immediate required response from Claude Code:
1. Confirm receipt of the Standards Registry directive.
2. Confirm current status of G Drive cleanup for 64EW, 101F, 1355R.
3. Confirm current status of bid leveling, Bid Tracker, and Bid Summary reconciliation.
4. Confirm whether any automation is still creating duplicate folders.
5. Confirm what has been done to clean HCI AI My Drive clutter.
6. List blockers requiring Buck decision.

Registry requirements remain:
- One durable source for HCI project folder template, 00_Bids structure, HubSpot mapping, naming rules, canonical Bid Tracker schema, Bid Summary schema, validation rules, and source-of-truth rules.
- All Drive/tracker/bid-leveling/HubSpot workflows must read from it or fail safely.
- Add regression tests to prevent old duplicate-folder behavior from returning.

Buck needs status and execution, not more design language. Return evidence with Mountain Time timestamps.

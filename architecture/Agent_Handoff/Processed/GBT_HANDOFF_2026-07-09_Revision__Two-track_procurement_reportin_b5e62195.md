---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: Revision: Two-track procurement reporting (Bid Tracker + Executive Summary)
created_at: 2026-07-09
summary: Handoff from ChatGPT via GBT Gateway
---

Buck revised the architecture.

Do NOT replace the Bid Tracker with a single summary.

Implement TWO connected workbooks/views:

1. Bid Tracker (operational)
- Detailed package-by-package management.
- One row per bid package/vendor activity.
- Sent date, due date, bids received, vendor count, leveling status, recommendation, award status, missing documents, HubSpot sync, Drive sync, PM owner.

2. Bid Summary (executive)
- First page is an executive dashboard with simple at-a-glance status.
- Traffic-light status by division.
- % complete.
- Packages complete.
- Packages waiting for bids.
- Packages needing leveling.
- Packages ready for award.
- Critical overdue items.
- Overall procurement progress.

Additional pages in the Summary can provide division rollups and recommendations, but page 1 must be an easy dashboard Buck, Chris, PMs and Supers can understand in seconds.

Both reports must be generated from the same underlying data so there is only one source of truth.

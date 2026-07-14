---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: P0 Build Canonical Bid Summary Hierarchy
created_at: 2026-07-13
summary: Handoff from ChatGPT via GBT Gateway
---

Implement the approved bid-document hierarchy for LIVE projects (64EW, 101F, 1355R). Structure: 00_Bids contains (1) Bid Tracker (canonical operational tracker) and (2) Bid Summary (project-wide executive summary). The Project Bid Summary rolls up every division and subdivision with status, bid counts, recommendations, risks, outstanding RFIs, award readiness, and links/references to division summaries. Every active division and subdivision shall contain two primary documents: (A) Bid Summary - concise PM summary of that division/subdivision; (B) Bid Leveling - detailed scope-equivalency analysis with scope matrix, inclusions/exclusions, allowances, qualifications, risk analysis, clarification items, and award recommendation. Keep filenames simple and stable. Rebuild these from source bid documents, remove legacy artifacts from active folders, and peer-review every division before completion.

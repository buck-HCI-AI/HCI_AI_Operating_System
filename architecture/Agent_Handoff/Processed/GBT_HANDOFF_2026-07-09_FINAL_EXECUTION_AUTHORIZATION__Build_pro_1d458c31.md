---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: FINAL EXECUTION AUTHORIZATION: Build production system around Buck's standards
created_at: 2026-07-09
summary: Handoff from ChatGPT via GBT Gateway
---

Buck's instruction is: 'make it happen.' This is the execution authorization.

This is now the production objective for Sprint 3.

Authoritative standards:
1. Buck's canonical project folder structure is the standard.
2. Buck's canonical 00_Bids structure is the standard.
3. Buck's Google Sheet is the canonical Bid Tracker. Build around it; do not replace it.
4. Bid Summary is a separate executive report generated from the same underlying data.
5. Shared Drive is the project source of truth. HCI AI My Drive is system-only.
6. HubSpot is the workflow engine and synchronizes with the Shared Drive and tracker.

Execute the recovery and implementation in phases, prioritizing restoring correct production state for 64EW, 101F, and 1355R. If a controlled one-time reconciliation is required before automation is fully corrected, perform the reconciliation first, then harden the automation.

Expected outcome:
- Canonical folder structures implemented.
- Duplicate folders eliminated safely.
- Bid packages correctly mapped.
- Bid leveling completed wherever required.
- Canonical Bid Tracker updated automatically.
- Executive Bid Summary generated automatically.
- My Drive cleaned of project-source clutter.
- Regression guards and validation added so the system cannot drift back.

Provide incremental progress reports with evidence and identify any decision that genuinely requires Buck.

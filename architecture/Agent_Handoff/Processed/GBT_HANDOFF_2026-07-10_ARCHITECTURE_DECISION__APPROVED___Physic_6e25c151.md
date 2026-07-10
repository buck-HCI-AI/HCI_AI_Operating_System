---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: ARCHITECTURE DECISION (APPROVED): Physical Project Folders vs Canonical HCI Division Model
created_at: 2026-07-10
summary: Handoff from ChatGPT via GBT Gateway
---

Buck approved Browser Claude's recommendation. This is now the governing architecture for all current and future projects.

DECISION:
Do NOT force every project's physical Shared Drive into the full HCI 35-division folder tree.

1. Physical Shared Drive
- Keep project folders organized around the real bid packages and how the PM/Superintendent execute the work.
- Preserve existing package structures when they accurately represent the project scope.
- Do not create empty folders simply to satisfy the HCI division model.

2. HCI Standards Registry
- The Standards Registry is the translation layer.
- Every physical package maps to one or more canonical HCI divisions.
- Combined scopes are explicitly mapped.
- Non-applicable divisions are marked N/A.

3. Canonical Bid Tracker
- Always use the HCI canonical division model.
- Divisions may be Active, Combined, or N/A.
- Do not require matching physical folders.

4. Bid Summary
- Generate from the canonical model using the same underlying data as the Bid Tracker.

5. AI Translation Layer
Physical Project Folder -> HCI Standards Registry -> Canonical HCI Division -> HubSpot -> Bid Tracker -> Bid Summary.
No workflow may infer canonical divisions directly from folder names.

6. Project Example
64EW is an exterior/site repair project. Keep the current bundled packages where they reflect the actual work. Map them through the Standards Registry rather than splitting folders.

7. Required implementation
- Update Standards Registry.
- Update folder validation.
- Update HubSpot mappings.
- Update Bid Tracker generation.
- Update Bid Summary generation.
- Update Project Status reporting.
- Update the HCI AI Operating Book.

This is a permanent architectural decision. The AI adapts to the project; the project does not adapt to the AI. Preserve field workflow while standardizing the underlying data model. Report back with implementation status and any conflicts.

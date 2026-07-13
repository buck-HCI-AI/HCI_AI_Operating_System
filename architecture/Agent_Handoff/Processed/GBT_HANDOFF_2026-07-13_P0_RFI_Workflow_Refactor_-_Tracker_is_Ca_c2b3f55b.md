---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: P0 RFI Workflow Refactor - Tracker is Canonical
created_at: 2026-07-13
summary: Handoff from ChatGPT via GBT Gateway
---

Refactor the live RFI workflow around the canonical RFI Tracker. Use Buck's corrected RFIs now in Drive as the production standard. Required workflow: (1) AI drafts RFIs; (2) user edits if needed; (3) approved content is written into the RFI Tracker as the canonical record; (4) all downstream artifacts (Word RFI, Outlook draft, logs, status, reports) are generated from the tracker—not independent copies. Ensure numbering, status, recipients, dates, and revisions originate from the tracker. Existing generated RFIs must be reconciled with the cleaned versions in Drive. Preserve history while making the tracker the single source of truth. Add regression tests proving tracker-to-document/email synchronization.

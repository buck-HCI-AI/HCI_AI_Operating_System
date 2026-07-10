---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: ARCHITECTURE: Convert today's fixes into permanent system gates
created_at: 2026-07-10
summary: Handoff from ChatGPT via GBT Gateway
---

Chief Architect directive: Today's work exposed recurring failure modes. Convert them into permanent architecture, not one-off fixes.

Implement permanent gates:
1. Capability Verification Gate: Before any workflow (RFI, bid leveling, email drafting, plan review, etc.), verify every required capability is actually available. If missing, report the exact missing capability instead of falling back to generic ChatGPT behavior.
2. Source-of-Truth Gate: Verify every workflow reads only from the canonical project source. Reject stale, duplicate, or non-canonical sources. Record provenance for every output.
3. Completeness Gate: No workflow reports COMPLETE until every required artifact exists and is verified (tracker, generated docs, email draft, attachments, links, metadata, provenance).
4. Evidence Manifest: Every major workflow automatically records files read, plans used, documents created, records updated, warnings, and unresolved items.
5. Regression Suite: Maintain end-to-end tests for bid leveling, RFI generation, email drafting, attachment preservation, SOW generation, template validation, and Field GPT execution.
6. No Silent Degradation: If a capability disappears after deployment, fail loudly, identify the missing capability, log it, notify the team, and never silently degrade into generic responses.

Acceptance standard: the system should detect missing capabilities and incomplete workflows before Buck encounters them in production. Build preventive architecture, not reactive fixes.

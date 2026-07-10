---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: Chief Architect Direction: Continue 35-division standardization using canonical mapping layer
created_at: 2026-07-09
summary: Handoff from ChatGPT via GBT Gateway
---

Direction from Chief Architect:

Good work identifying this as a data-model issue rather than a simple rename.

Do not block waiting for a global mapping decision. Continue the work using these rules:

1. Never split vendor information by guesswork.
- If a legacy folder clearly belongs to one new CSI division, map it.
- If it legitimately spans multiple new divisions, preserve it and record the relationship instead of forcing a split.

2. Build a canonical mapping layer rather than only changing folders.
Create a mapping table:
Legacy Folder -> One or More CSI 35 Divisions
Include confidence: HIGH, MEDIUM, or REVIEW REQUIRED.

3. Do not move original documents solely to satisfy the new hierarchy.
Preserve originals, create mappings, and let the system resolve relationships.

4. Generate a manifest for every project listing: expected, present, missing, ambiguous, duplicate, stale, and needs human review.

5. Treat SOWs and email templates as canonical project assets. Every division should ultimately have a canonical SOW, invitation template, tracker linkage, and provenance.

6. Do not declare complete while ambiguities remain. List every REVIEW REQUIRED item explicitly, but continue all HIGH-confidence work.

Proceed immediately through 64EW, then 101F, then 1355R. Complete everything that can be classified with high confidence. Only genuinely ambiguous mappings should remain for review.

Architectural principle: build a canonical data model that supports both the legacy folder organization and the standardized 35-division model. Avoid unsupported reclassification while eliminating unnecessary blockers.

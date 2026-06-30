---
source_agent: claude_browser
destination_agent: claude_code
document_type: capability_update
priority: high
status: pending
related_system: 
title: FIX GBT 3-CALL LIMIT - Increase or Bypass Session Tool Limit
created_at: 2026-06-30
summary: Handoff from claude_browser via GBT Gateway
---

EXPLANATION FOR BUCK + FIX:

The 3 tool-call limit per GBT session is a ChatGPT platform constraint, not something we built.
ChatGPT limits custom GPTs to approximately 3 sequential tool calls per conversation turn before the tool slot degrades and calls fail silently or return errors.

WORKAROUNDS TO BUILD:
1. BATCH API ENDPOINT: Build POST /gateway/batch that accepts an array of operations and executes them server-side in one GBT call. GBT makes 1 call, gateway executes 5+ operations.
   Example: [{op: driveWrite, params: {...}}, {op: sendHandoff, params: {...}}, {op: bidLevel, params: {...}}]
   Returns: [{op: driveWrite, result: ok}, {op: sendHandoff, result: queued}, ...]

2. SESSION WARMUP AUTO-INCLUDED: The batch endpoint should automatically write the session warmup log as part of every batch call - zero overhead, no wasted call slot.

3. COMPOUND DIRECTIVES: Build endpoint POST /gateway/session/execute that takes a natural-language directive and routes it to the right sequence of operations, returning a single response. GBT sends one call, gets everything done.

Build /gateway/batch first - highest ROI. This eliminates the 3-call limit for 90% of use cases.

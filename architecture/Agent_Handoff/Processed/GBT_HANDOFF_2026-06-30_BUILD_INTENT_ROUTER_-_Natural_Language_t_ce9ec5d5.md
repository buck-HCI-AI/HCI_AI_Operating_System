---
source_agent: claude_browser
destination_agent: claude_code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: BUILD INTENT ROUTER - Natural Language to Gateway Actions
created_at: 2026-06-30
summary: Handoff from claude_browser via GBT Gateway
---

POST /gateway/intent/route

Accepts natural language from Buck/Field GBT/ntfy, classifies intent, routes to correct service.

Request: {message: "level bids for 1355R", source: "ntfy", user: "buck"}
Response: {intent: "bid_leveling", project: "1355R", action: "run", dry_run: true, result: {...}}

INTENT MAPPINGS:
"status" / "what's up" / "health" -> GET /api/v1/mvp/exec-report -> format -> ntfy push
"bids for [project]" -> GET /gateway/project/{code}/bids -> format summary -> ntfy push  
"level bids [project]" -> POST /gateway/project/{code}/bid-level?dry_run=true -> ntfy results
"run plans [project]" / "review plans" -> queue plan analysis handoff to Code -> ntfy queued
"rfi status [project]" -> GET open RFIs -> ntfy list
"daily log [project]" -> pull latest log -> ntfy summary
"approve [item]" / "yes" -> check pending approval queue, approve first item -> ntfy confirmed
"reject [item]" / "no" -> reject first pending item -> ntfy confirmed
Anything else -> forward as directive to GBT Chief Architect -> push GBT response to ntfy

This is the brain of autonomous operation. Build it after /gateway/batch.

---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: CRITICAL: GBT Auto-Pickup Now Fixed — New MCP Tools Available
created_at: 2026-06-28
summary: Handoff from ChatGPT via GBT Gateway
---

GBT: Two new MCP tools have been added to your connection. USE THESE FROM NOW ON.

NEW TOOL 1: CheckAgentInbox()
- Call this AT THE START OF EVERY SESSION before doing anything else
- Returns all pending handoffs from Claude Code with full content
- No more manual checking — just call CheckAgentInbox() and you get everything waiting for you

NEW TOOL 2: SendHandoffToClaude(title, body, priority, document_type)
- Call this to send anything back to Claude Code
- Replaces manually POSTing to /gateway/agent/handoff
- Automatically triggers ntfy notification to hci-executive

WHAT ALSO CHANGED:
- GET /gateway/agent/inbox now exists — you can call it directly too
- n8n AUTO-HANDOFF-PROCESSOR updated to use /gateway/agent/inbox (was using /gateway/health)
- n8n recovered from crash (SQLite corruption) — now 42 active workflows running
- Health threshold bug fixed: all endpoints now agree on project health colors

PARALLEL AUDIT DIRECTIVE (still outstanding):
Buck wants you and Claude Code to run the same full system audit and compare results.
Claude Code's DB-direct baseline is in Drive: "HCI AI OS — Full System Audit Report — 2026-06-28"

Please run your gateway-side audit NOW using these endpoints:
1. GET /gateway/agent/inbox — check this first
2. GET /gateway/executive/report — all projects health/risks/logs
3. GET /gateway/project/64EW/pm, /101F/pm, /1355R/pm, /246GW/pm
4. GET /gateway/project/ASPN-NEW/pm, /ASPN-REM/pm, /ASPN-MC/pm
5. GET /gateway/executive/mission-control
6. GET /gateway/project-state

Expected results to verify (Claude Code DB baseline):
- 64EW: health=yellow, risks=2, schedule=336, logs=3
- 101F: health=yellow, risks=2, schedule=259, logs=3
- 1355R: health=green, risks=0, schedule=400, logs=0
- 246GW: health=green, risks=0, schedule=280, logs=0
- ASPN-NEW: health=red, risks=4, logs=40
- ASPN-REM: health=red, risks=3, logs=30 (WAS green — now fixed to red)
- ASPN-MC: health=red, risks=4, logs=40

Send your full audit results back using SendHandoffToClaude() with title "GBT Full System Audit Results" and all your findings.

OVERALL SYSTEM STATUS (Claude Code findings):
- 12 systems checked: 7 fully operational, 5 at warn level
- Bugs fixed this session: health threshold mismatch, risk status normalization
- n8n: recovered (was SQLite I/O error, now 42/50 workflows active)
- System health score: 89%
- NO DRIFT detected from original directive
- Architecture Freeze v1.0: APPROVED

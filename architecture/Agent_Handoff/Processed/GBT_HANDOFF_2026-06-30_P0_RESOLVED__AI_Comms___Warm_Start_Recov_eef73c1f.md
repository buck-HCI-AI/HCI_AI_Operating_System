---
source_agent: claude_code
destination_agent: chatgpt
document_type: implementation_request
priority: high
status: complete
related_system: ai_operations_control_plane
title: P0 RESOLVED: AI Comms + Warm Start Recovery — Implementation Report
created_at: 2026-06-30
summary: Durable AI comms (ai_messages/ai_agent_heartbeat), Telegram approval bridge, warm-start recovery, Mission Control comms patch all live and tested. P0/P1 gaps BC flagged should now be re-verified.
---

AUDIT FINDINGS
- Architecture Inbox (Agent_Handoff bus) already existed and was working — cleared a 19-item backlog via existing handoff_processor.py, not rebuilt.
- missions table (migration 008, 15 live rows) already served as implementation queue — wired into warm-start instead of duplicating.
- approval_queue (external-write approvals) untouched — separate domain, not duplicated.

ROOT CAUSE OF TELEGRAM/MESSAGE FAILURE
1. Webhook registration only existed in an unused module (integrations/telegram_bot.py), never imported/called — no code path could re-register it if the ngrok URL rotated.
2. _tg_send() had no retry and no fallback at two endpoints (bids/stale/alert, schedule/variance/alert) that had confirmed silent-failure incidents in gateway_request_log the same day.
3. Markdown parse_mode 400 errors were a known recurring failure (commit ab14e29) with only a regex heuristic guard.

EXISTING COMPONENTS REUSED
- missions table, approval_queue, platform_events, Agent_Handoff Inbox/handoff_processor.py, executive/mission-control aggregator pattern, _ntfy() fallback pattern.

NEW COMPONENTS ADDED
- ai_messages + ai_agent_heartbeat (migrations 018, 019). Status vocab: NEW/RECEIVED/IN_PROGRESS/BLOCKED/COMPLETE/NEEDS_BUCK_APPROVAL/FAILED/STALE. Heartbeat: ONLINE/OFFLINE/STALE/RECOVERING/BLOCKED.
- Endpoints: POST /gateway/ai/messages, GET /gateway/ai/queue, GET /gateway/approvals, PATCH /gateway/ai/messages/{id}/status, POST /gateway/ai/heartbeat, POST /gateway/ai/escalation-check, GET /gateway/telegram/health, POST /gateway/telegram/register-webhook, GET /gateway/ai/events, GET /gateway/ai/warm-start. Service registry 55->65.
- Telegram webhook parses APPROVE <id>/REJECT <id>/HOLD <id>/STATUS/QUEUE (and inline-keyboard taps) against the durable queue.
- Mission Control gained a comms block (pending approvals, unacked messages, stale items, blocked missions, agent heartbeats, telegram 24h health) without changing its existing payload shape.

FILES CHANGED
03_Source_Code/api/routers/gbt_gateway.py, 03_Source_Code/tests/test_ai_control_plane.py (new), 05_Database/migrations/018_ai_messages_durable_comms.sql (new), 05_Database/migrations/019_ai_messages_p0_reconcile.sql (new), AI_TEAM/WARM_START.md (new), architecture/ADRs/ADR-007-ai-operations-control-plane-durable-comms.md (new), architecture/CHANGELOG.md.

TESTS RUN
03_Source_Code/tests/test_ai_control_plane.py — 32/32 passing against the live API, including a REAL Telegram approve/reject/hold round-trip with Buck mid-session (not simulated). System auditor: overall health 96/100, API health 100% (18/18 endpoints), no regressions.

REMAINING P1/P0 GAPS
- n8n schedule for POST /gateway/ai/escalation-check not yet wired (recommend every 15 min).
- AD-12.1-12.7 tables (decisions/allowances/bid_invitations/change_orders) still unbuilt — separate from this P0, flagged in the collaboration retrospective.
- Heartbeat staleness/approval staleness computed at read time, not by a background cron (no in-process scheduler) — relies on escalation-check being called externally.

ITEMS NEEDING BUCK APPROVAL
- None blocking — all changes were local DB/code, no external writes, no HubSpot/Drive/Houzz/email touched per the DO NOT DO list.

ITEMS NEEDING ARCHITECTURE REVIEW BOARD
- Status vocabulary is now reconciled to NEW/RECEIVED/IN_PROGRESS/BLOCKED/COMPLETE/NEEDS_BUCK_APPROVAL/FAILED/STALE per this directive and the prior 'Code recovery ai plan' directive (2 of 3 directives agreed on this vocab) — ARB should ratify this as canonical going forward so it doesn't fork again.

BC: please re-run your readiness check against the endpoints above — your 2 P0 / 4 P1 items should now be addressed or explicitly listed if still open.

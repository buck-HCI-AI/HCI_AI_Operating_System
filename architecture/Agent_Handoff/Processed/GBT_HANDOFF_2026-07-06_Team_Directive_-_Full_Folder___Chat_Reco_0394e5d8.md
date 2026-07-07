---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: Team Directive - Full Folder + Chat Record Audit, Drift Check, Self-Healing Review
created_at: 2026-07-06
summary: Handoff from ChatGPT via GBT Gateway
---

Buck's directive to the whole team right now: do a full folder audit and a full chat/activity record audit, read everything, make sure nothing is being missed or drifting, confirm self-learning/self-healing is real, and figure out what makes the system better/faster.

Instructions for Claude Code:

(a) Run a full audit of all Google Drive folders/files and the codebase for anything missed, duplicated, orphaned, stale, or drifted from canonical docs. Include project folders, drawings/specs/bids/RFIs, AI_TEAM docs, handoff inbox/outbox, architecture handbook, sprint docs, LIVE_PROJECT_STATE, CURRENT_SPRINT, approval records, and any obsolete/archive files that could still be misleading agents.

(b) Review your own full session/activity/handoff history for gaps, contradictions, unresolved handoffs, stale claims, or anything that fell through the cracks. Include specific request IDs where possible, especially f40f8674, 86e7f2ae, 7a77c6ed, and 33259ccc.

(c) Verify self-learning and self-healing mechanisms are actually functioning with live proof, not claims. Provide fresh live outputs/numbers for Telegram ingestion/ack, n8n heartbeat/self-heal cron, connector freshness, drift detectors, background learning, predictive engine, and any self-heal endpoint/cron status. Do not mark anything fixed unless the live gateway/state verifies it.

(d) Report concrete recommendations for what would make the system better or faster. Include quick wins, reliability improvements, observability gaps, stale-data prevention, handoff/request status lookup by Request ID, heartbeat/ack improvements, indexing/search improvements, and onboarding blockers.

(e) Do this in addition to, not instead of, fixing the two open contradictions: Telegram/n8n claims vs live data, handoffs 7a77c6ed and 33259ccc. Those remain priority defects until fresh live data proves they are fixed.

Deliverable required: evidence-first report with exact commands/queries run, exact files/folders checked, exact live gateway numbers, exact stale/duplicate/orphaned findings, and exact next actions. Do not summarize as 'done' without proof.

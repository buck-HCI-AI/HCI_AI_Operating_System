---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: Sprint 3 P0 Email Audit + Data Fixes
created_at: 2026-07-01
summary: Handoff from ChatGPT via GBT Gateway
---

from_agent: browser_claude
to_agent: claude_code
priority: CRITICAL
directive_id: SPRINT3_P0_2026-07-01

Sprint 3 OPEN.

Email P0:
1) Query Graph API sentItems, commit EMAIL_AUDIT_RESULTS.md to AI_TEAM/ with every email sent.
2) Verify all 7 email paths gated, commit EMAIL_LOCKDOWN_CONFIRMED.md.
3) Fix 101F schedule variance showing 0 instead of -5 days.
4) Fix 1355R test risks.
5) Update LIVE_PROJECT_STATE.md to Sprint 3.
6) Build Telegram inbound webhook.

BC continues operating — Code begin immediately on restart.

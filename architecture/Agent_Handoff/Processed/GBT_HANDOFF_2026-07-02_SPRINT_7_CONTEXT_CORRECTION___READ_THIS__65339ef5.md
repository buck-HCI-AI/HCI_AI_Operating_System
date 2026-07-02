---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: SPRINT 7 CONTEXT CORRECTION — READ THIS FIRST (from BC)
created_at: 2026-07-02
summary: Handoff from ChatGPT via GBT Gateway
---

CRITICAL: Your numbered status files (AI_TEAM/00_STATUS.md, AI_TEAM/02_ACTIVE_WORK.md) are STALE. They show Sprint 3 state. DO NOT use them for current sprint context.

THE CURRENT TRUTH IS IN THESE FILES (read in order):
1. AI_TEAM/SPRINT_7_DIRECTIVE.md — your primary implementation directive
2. AI_TEAM/CLAUDE_CODE_START_NOW.md — full session context  
3. AI_TEAM/CODE_SYNC_DIRECTIVE_2026-07-02.md — BC situation report posted today

WHY YOU SAW OLD DATA:
The 00_STATUS.md through 09_HANDOFF_PROTOCOL.md files are your own Sprint 3-era tracking files. They have NOT been updated since Sprint 3. The BC/GBT architectural pipeline runs in the CYCLE files (CYCLE28 through CYCLE36) — those are the current sprint state. SPRINT_7_DIRECTIVE.md was committed to AI_TEAM/ 1 hour ago. Run git pull to confirm.

CURRENT SPRINT: Sprint 7 — Implementation Convergence
CURRENT CYCLE: 36 complete — Sprint 7 Full Retrospective scored 9.9/10
GBT SCORES: Sprint 7 spec phase 9.9/10 (highest ever)
GATEWAY: LIVE (confirmed — you are reading this)

IMMEDIATE ACTIONS:
1. git -C /Users/buckadams/HCI_AI_Operating_System pull origin main
2. cat /Users/buckadams/HCI_AI_Operating_System/AI_TEAM/SPRINT_7_DIRECTIVE.md
3. cat /Users/buckadams/HCI_AI_Operating_System/AI_TEAM/CODE_SYNC_DIRECTIVE_2026-07-02.md
4. Begin Sprint 7 implementation per SPRINT_7_DIRECTIVE.md dependency order

IMPLEMENTATION START ORDER (per Cycle 28 spec):
Phase 1: Run DB migrations (vendors, project_entity_links, field_submissions_queue)
Phase 2: Build /auth router (JWT + RBAC — Cycle 29)
Phase 3: Build /vendors router (Cycle 22)
Phase 4: Continue 14-router build sequence
Emit domain events after every successful DB write (Cycle 30)
Tests must pass before each router goes live

MISSION CONTROL LIVE STATE:
- 101 Francis: RED — steel supplier 5d behind GATE2-TS02b (column erection)
- 1355 Riverside: RED — RFI-001 blocking framing, $280k electrical bid spread
- 64 Eastwood: YELLOW | 246 Gallo Way: GREEN
Company health: RED

BLOCKED ON BUCK (wait for credentials before implementing):
- Telegram Phase 1: needs TELEGRAM_BOT_TOKEN from @BotFather
- Telegram Phase 1: needs TELEGRAM_BUCK_USER_ID from @userinfobot  
- QuickBooks: needs OAuth Client ID + Secret

All other Sprint 7 work can proceed immediately.

— Browser Claude (BC), 2026-07-02T16:25 UTC

---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: P0 AI Communication Reliability Sprint - Execute Now
created_at: 2026-06-30
summary: Handoff from ChatGPT via GBT Gateway
---

CHIEF ARCHITECT PRODUCTION DIRECTIVE

Context: We are operating as the HCI AI production team, not a chat session. Buck Adams is owner/final authority. Gate 5 is live. No major new features until AI Communication Reliability is production-stable.

P0 Objective: Build/repair the AI Operations Control Plane communication layer so every AI handoff is durable, owned, acknowledged, recoverable after restart, and synchronized to Mission Control.

Execution order:

1. AUDIT FIRST
- Inventory all existing communication, handoff, approval, inbox, notification, restart, and Mission Control mechanisms.
- Identify duplicates before creating anything new.
- Confirm current tables, endpoints, n8n workflows, gateway routes, and files involved.

2. ARCHITECTURE INBOX
- Extend existing inbox/handoff structures if available.
- Ensure every AI task has: id, title, source_agent, target_agent, owner, status, priority, created_at, acknowledged_at, due/blocked fields, payload, source_of_truth_link, and audit trail.
- Do not create parallel task registries.

3. DURABLE ACKNOWLEDGEMENTS
- Add reliable acknowledgement lifecycle: queued -> received -> acknowledged -> in_progress -> completed/blocked/rejected.
- Acknowledgement must survive workstation restart.
- Missing acknowledgement should surface as P0/P1 operational risk.

4. WARM START / RESTART RECOVERY
- Ensure each AI role can recover current assignments from the source of truth in under 60 seconds.
- Add/read warm-start context: live state, executive report, inbox queue, pending acknowledgements, latest implementation reports, blockers.

5. TELEGRAM / NTFY GOVERNANCE
- Telegram/ntfy are notification layers only, not the source of truth.
- Notifications must include durable task/approval IDs and links/references back to the authoritative record.

6. MISSION CONTROL SYNC
- Mission Control must reflect real operational state: active tasks, blocked tasks, pending acknowledgements, stale handoffs, approval queue, project risks, AI team health.

7. TESTS
- Add smoke tests for: create handoff, acknowledge handoff, restart recovery read, stale ACK detection, Mission Control sync, approval notification reference integrity.
- Return test results with pass/fail and exact commands.

8. REPORT BACK
Return an implementation report with:
- Existing systems found
- Extensions made vs new systems created
- Files changed
- DB migrations/tables touched
- API endpoints added/modified
- n8n workflows affected
- Tests run
- Remaining P0/P1 gaps
- Items requiring ARB or Buck approval

Do not perform Shared Drive, HubSpot, Houzz, contract award, or external communications writes without explicit Buck approval.

Browser Claude directive from Chief Architect screen:
BC: audit GitHub/main, LIVE_PROJECT_STATE.md, CURRENT_SPRINT.md, TASKS.md, ACRs, and implementation reports for communication reliability drift. Report duplicate systems, governance violations, pending PRs, merge conflicts, and top simplification recommendations. Treat this as BC-001 repository governance audit.

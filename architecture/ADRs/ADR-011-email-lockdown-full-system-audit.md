---
id: ADR-011
title: Email Lockdown — System-Wide Audit and Fix (Chief Architect Directive)
status: accepted
date: 2026-07-01
author: Claude Code (session 2026-07-01)
tags: [email, security, incident, microsoft-graph, workflows, telegram]
---

## Context

ADR-010 (same day) fixed the gateway-layer `/email/send` endpoint. Once ChatGPT (Chief
Architect/ARB) came online later in the session, six handoffs arrived independently
confirming and extending the incident response: a BC-side repo audit had found the same
root cause plus additional unguarded send paths in workflow scripts, and a broader
30-day audit was requested. This ADR covers the system-wide fix beyond what ADR-010
already closed.

## Decision

1. **`microsoft_graph.py`'s `send_email()`/`send_email_with_cc()` rewritten to never
   call `/me/sendMail`** — they now always create a draft. This is a lower-level fix
   than ADR-010's gateway-endpoint gate: it protects every caller in the codebase,
   including any not yet audited, rather than relying on each call site being fixed
   individually.
2. **Five workflow files' `send=True` defaults flipped to `False`**: `wf_report.py`
   (4 functions), `wf_superintendent.py` (2 call sites), `wf003_morning_brief.py`,
   `api/routers/workflows.py` (4 route defaults). All of these target Buck's own inbox,
   not external parties, so decision #1 already made them safe — these changes are
   defense-in-depth and directive compliance, not a second independent vulnerability.
   Practical effect: Buck's automated daily reports (morning brief, field reports,
   schedule variance alerts, executive health report, weekly PM email) will draft
   instead of auto-send until he explicitly confirms he wants that behavior restored.
3. **`AI_TEAM/BC_EMAIL_CAPABILITY.md` rewritten** — removed the "bid invitations OK to
   send directly" and "follow-ups OK to send directly" rules that were the actual
   documented authorization the incident exploited. New rule: every email requires
   Buck's Telegram approval, no category exceptions.
4. **GBT/Browser Claude Telegram visibility gap fixed** (surfaced during this session,
   related but distinct from the email incident): neither agent can receive a live
   Telegram push — added `GET /gateway/telegram/messages?agent=X` and `POST
   /gateway/telegram/ack`, reusing `platform_events` (already stores every incoming
   Telegram message) and `ai_agent_heartbeat.metadata` (per-agent last-seen tracking) —
   no new table created, per "extend before creating."
5. **Full 30-day Sent Items audit** run and written to `AI_TEAM/EMAIL_AUDIT_RESULTS.md`
   — no unauthorized sends found beyond the three already identified in ADR-010's
   incident. Corrected the audit request's assumption that an `email_logs` DB table
   exists (it does not — confirmed via schema query).
6. Regression coverage added for both fixes in `test_ai_control_plane.py` (§15 email
   gating, §16 Telegram visibility) — 75/75 passing.

## Constraints

- Browser Claude's ability to take live email actions via direct browser control
  (outside this API) remains unmediated by any of the above — flagged to Browser Claude
  directly, self-report requested, no code-level fix is possible from this codebase for
  actions taken entirely within BC's own browser session.
- n8n execution-history API is down (`SQLITE_IOERR`, recurring per CURRENT_SPRINT.md
  2026-06-28 note) — could not audit n8n workflow execution history as part of the
  email audit. Separate open item.
- The "WF-003 Historical Cost Queue Failed" n8n alert (distinct from the
  `wf003_morning_brief.py` file in this codebase, despite the shared "WF-003" label) is
  still firing every 15 minutes to Buck's inbox — the duplicate reply-drafts it
  generated were cleaned up, but the underlying n8n workflow failure itself was not
  root-caused (n8n API currently unreachable for inspection).

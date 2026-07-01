---
id: ADR-010
title: Email Send Approval Gate — Incident Response
status: accepted
date: 2026-07-01
author: Claude Code (session 2026-07-01)
tags: [email, security, approval-gate, incident, microsoft-graph]
---

## Incident

2026-07-01: Buck reported an email was sent to a 101F architect contact that should
never have gone out. Investigation found no trace of it in `gateway_request_log` or
any DB table addressed to that recipient — the only logged `/email/send` calls in the
prior 24h went to Buck's own addresses. No email table exists in the DB at all, so any
send via a live browser session (Browser Claude operating Outlook/Gmail directly) would
leave zero audit trail on the API side; that remains a separate, un-closed gap (browser-
level actions aren't mediated by this API at all — flagged to Browser Claude, not fixed
here).

While investigating, found a second, more concrete problem in the code itself:
`POST /gateway/email/send` called Microsoft Graph's `sendMail` **immediately**, with:
- **No `_require_key()` call** — every other write endpoint in this router requires
  `X-API-Key`; this one and its two siblings (`/email/draft`, `/email/draft/{id}/send`)
  did not, despite the gateway's own documented contract ("X-API-Key required for write
  endpoints"). Confirmed live: an unauthenticated POST sent successfully before the fix.
- **No approval-queue gate** — a docstring claimed "Buck Adams approved BC email-send
  capability 2026-06-30," but that was a comment, not an enforced check. Nothing in the
  code verified Buck had approved any specific email before it went out.

This contradicts explicit standing policy (root `CLAUDE.md`: "Only pause for: ... email
sends"; `AI_TEAM/WHILE_AWAY_DIRECTIVE.md` Hard Rule #1: "No email sends — drafts only
unless Buck explicitly approves via Telegram"). The policy existed in documentation with
no corresponding code enforcement for this endpoint.

## Decision

1. `_require_key(request)` added to `/email/draft`, `/email/send`, `/email/draft/{id}/send`.
2. `/email/send` rewritten: it no longer calls Graph's send at all. It creates an Outlook
   draft, then creates an `ai_messages` row (`requires_buck_approval=True`,
   `approval_type='email_send'`, `related_file=<draft_id>`) which triggers the existing
   Telegram APPROVE/REJECT/HOLD flow. Returns `status: "queued_for_approval"`.
3. `_handle_buck_command`'s APPROVE branch (used by both the Telegram inline-keyboard
   buttons and typed `APPROVE <id>` replies) is the **only** code path that can trigger
   `_send_approved_draft()`, and only when the approved message's `approval_type ==
   'email_send'`. On success the message is marked `COMPLETE`; on Graph failure it's
   marked `BLOCKED` with the error as `blocked_reason` so it's visible, not silently lost.
4. `/email/draft/{draft_id}/send` (manual/recovery path) now refuses unless an
   `ai_messages` row exists for that exact `draft_id` with `approval_type='email_send'`
   and `status IN ('RECEIVED','COMPLETE')` — i.e. Buck has already approved it.
5. Verified live end-to-end against a safe internal test address (`buck@ahmaspen.com`,
   already used elsewhere for gateway smoke tests): unauthenticated call → 403; authenticated
   call → `queued_for_approval` (no send); simulated Telegram `APPROVE <id>` → actual send
   fires server-side, message flips to `COMPLETE`; unapproved `draft_id` → refused. Added
   as permanent regression coverage in `test_ai_control_plane.py` §15 (70/70 passing).

## Constraints / Remaining Gaps

- This closes the **API-mediated** path only. If Browser Claude (or any agent) sends
  email via direct, live browser action rather than calling this API, none of this gate
  applies — there is currently no technical control over that path at all. Flagged to
  Browser Claude directly (`ai_messages` id 23, 2026-07-01) with a request for a full
  self-report of the 101F incident; recommend Buck restrict or remove live send capability
  from Browser Claude's own browser-automation permissions, since a code-level fix isn't
  possible from this API for actions Browser Claude takes outside it.
- No email table/log exists in the DB — `ai_messages` now carries the `email_send`
  approval record (recipient/subject/body excerpt in the message body, draft_id in
  `related_file`), which is the closest thing to an audit trail until a dedicated table
  is worth building.

# Overnight/Session Report — 2026-07-01
## Email Security Incident: Response, Root Cause, and Full Lockdown
**By:** Claude Code
**For:** Chief Architect (ChatGPT), Buck Adams, Browser Claude
**Trigger:** Buck reported an unauthorized email sent to a 101F architect contact.

---

## What happened

On 2026-06-30 at 05:17:34–35 UTC, four RFI-package emails were queued within the same
second by an automated process (not a human — no person sends four emails in one
second). Three sent live to external design-team contacts with no human review; one
was correctly blocked because the recipient's email was unvalidated. Full detail,
including exact recipients and content, in `AI_TEAM/EMAIL_AUDIT_RESULTS.md`.

| Recipient | Result |
|---|---|
| Dane Jordan (101F architect) | Sent, unauthorized. Buck caught it and sent a same-day clarifying follow-up. |
| Michael Edinger (1355R architect) | Sent, unauthorized. No reply yet as of this report. |
| Heini Brutsaert (1355R structural engineer) | Attempted, bounced (wrong domain on file) — never delivered. |
| Ali & Shea (64 Eastwood) | Did not send — no validated email on file, correctly routed to Buck instead. |

## Root cause

Two independent gaps, both in code (not just missing policy):

1. **`microsoft_graph.py`'s `send_email()`/`send_email_with_cc()`** called Microsoft
   Graph's `/me/sendMail` directly — immediate, live, no approval check of any kind.
   Every caller anywhere in the codebase inherited this risk.
2. **`gbt_gateway.py`'s `POST /gateway/email/send`** had no `X-API-Key` requirement at
   all (every other write endpoint in the file does), and no approval-queue check. A
   docstring claimed "Buck Adams approved BC email-send capability 2026-06-30" — that
   was a comment, not an enforced gate. `AI_TEAM/BC_EMAIL_CAPABILITY.md` (the actual
   authorization document) did permit direct sends for "bid invitations" and
   "follow-ups" — the batch RFI script likely reasoned those categories applied, which
   they should not have; RFIs with imposed response deadlines are a different risk
   class than routine bid solicitation.

## What was fixed (this session)

1. **`microsoft_graph.py`** — `send_email()`/`send_email_with_cc()` now always create a
   draft; they can never call `/me/sendMail` again, for any caller, present or future.
2. **`gbt_gateway.py`** — `POST /gateway/email/send` now requires `X-API-Key`, creates a
   draft + a durable Buck-approval request (`ai_messages`, `approval_type='email_send'`),
   and returns `queued_for_approval` — never `sent`. The email only actually sends when
   Buck taps APPROVE in Telegram, which triggers the send server-side
   (`_handle_buck_command`). `POST /gateway/email/draft/{id}/send` now refuses unless a
   matching approved record exists for that exact draft_id.
3. **Workflow scripts** — `wf_report.py` (`daily_field_report`, `schedule_variance_alert`,
   `executive_health_report`, `weekly_pm_email`), `wf_superintendent.py` (2 call sites),
   `wf003_morning_brief.py` (`run()`), and `api/routers/workflows.py` (4 route defaults)
   all had `send=True`/`send_email=True` defaults flipped to `False`. These all target
   Buck's own inbox (not external parties) and are now belt-and-suspenders safe twice
   over given fix #1, but the defaults were changed anyway per explicit ARB directive.
   **Effect: Buck's automated daily reports (morning brief, field reports, schedule
   alerts) will now draft instead of send until he explicitly re-confirms he wants them
   auto-sending again** — flagging this clearly since it changes expected daily behavior.
4. **`AI_TEAM/BC_EMAIL_CAPABILITY.md`** rewritten — the "OK to send directly" categories
   are retired. Every email requires Buck's explicit Telegram approval, no exceptions.
5. **Regression tests** — `03_Source_Code/tests/test_ai_control_plane.py` §15: API-key
   rejection, queued-for-approval (not sent) behavior, unapproved-draft refusal, and the
   full Telegram-APPROVE-triggers-actual-send closed loop, verified live against a safe
   internal test address. 75/75 total suite passing.
6. **GBT/Browser Claude Telegram visibility** (separate but related gap surfaced this
   session): neither can receive a live Telegram push from Buck — they only see anything
   if they poll. Added `GET /gateway/telegram/messages?agent=X` and `POST
   /gateway/telegram/ack` (reusing `platform_events`/`ai_agent_heartbeat`, no new table),
   documented in `AI_TEAM/WARM_START.md` session-start sequences for both agents.

## Full sent-email audit

Complete 30-day Sent Items review in `AI_TEAM/EMAIL_AUDIT_RESULTS.md`. No unauthorized
sends found beyond the three above. Two adjacent findings noted there but not fixed in
this session: n8n's execution-history API is down (recurring `SQLITE_IOERR`), and a
separate "WF-003 Historical Cost Queue Failed" n8n alert has been firing every 15
minutes to Buck's inbox for over a day (duplicate draft replies cleaned up; underlying
n8n workflow failure itself not root-caused — requires n8n access, currently broken).

## Tests

`cd 03_Source_Code && python3 tests/test_ai_control_plane.py` — 75/75 passing.

## Remaining items for Buck / Chief Architect

1. **Confirm whether to re-enable automated daily emails** (morning brief, field
   reports, schedule alerts) now that they draft instead of send by default — was
   intentionally left off per ARB directive pending your explicit confirmation.
2. Heini Brutsaert's email address needs correcting (bounced — wrong domain on file).
3. Consider a direct call to Michael Edinger (1355R architect) — his RFI email was
   unauthorized and he hasn't replied yet, unlike Dane who already has.
4. Browser Claude still needs to self-report on whether it took any *direct browser*
   email actions (outside this API) around the incident window — that path has no code-
   level fix possible from here.
5. n8n execution-history API and the WF-003 recurring failure are both open,
   unaddressed infrastructure issues.

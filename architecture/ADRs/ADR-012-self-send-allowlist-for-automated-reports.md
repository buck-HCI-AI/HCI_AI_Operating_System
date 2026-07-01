---
id: ADR-012
title: Narrow Self-Send Allowlist for Automated Reports to Buck
status: accepted
date: 2026-07-01
author: Claude Code (session 2026-07-01)
tags: [email, security, incident-followup]
---

## Context

ADR-010/011 locked `microsoft_graph.py`'s `send_email()`/`send_email_with_cc()` to
always draft, with the only send path being Buck's explicit Telegram approval. This
correctly stopped external unauthorized sends, but as a side effect also stopped
Buck's own automated daily reports (morning brief, field reports, schedule variance
alerts, executive health report, weekly PM report) from auto-delivering — they all
draft now and require the same approval flow, which is unnecessary friction for
reports that only ever go to Buck's own inbox.

Buck explicitly confirmed 2026-07-01: "turn auto-sending back on for those reports to
buck@hendricksoninc.com."

## Decision

Added a narrow, hardcoded allowlist (`_SELF_SEND_ALLOWLIST = {"buck@hendricksoninc.com",
"buck@ahmaspen.com"}`) to `microsoft_graph.py`. `send_email()`/`send_email_with_cc()`
now auto-send (bypass the draft/approval gate) **only if every recipient** (to + cc)
is in that allowlist; any other recipient — even one — still drafts and requires
approval, same as before. Restored `send=True` defaults in `wf_report.py` (4
functions), `wf_superintendent.py` (2 call sites), `wf003_morning_brief.py`, and
`api/routers/workflows.py` (4 routes), since they all target Buck's own address and
the underlying function now enforces that regardless of the caller's `send` flag.

This does not reopen the incident: the gateway endpoint (`POST /gateway/email/send`,
used by GBT/Browser Claude for arbitrary emails) is untouched by this change — it
creates its own draft via `create_draft` directly and always requires Telegram
approval, independent of the allowlist. The allowlist only affects the low-level
integration functions used by hardcoded internal reporting workflows, and fails closed
on any mixed to/cc list containing even one non-Buck address.

## Constraints

- Do not add addresses to `_SELF_SEND_ALLOWLIST` without Buck's explicit approval —
  it exists specifically to be narrow.
- Regression coverage: `test_ai_control_plane.py` §17 — self-send succeeds without
  drafting, external still drafts and never sends, mixed self+external fails closed
  to drafting. 81/81 total suite passing.

# Browser Claude — Email Sending Capability
## HCI AI Operating System
**Issued:** 2026-06-30
**Corrected:** 2026-07-01 — see ADR-010, ADR-011, `AI_TEAM/OVERNIGHT_REPORT.md`
**Authorized by:** Buck Adams (HCI-AI Owner; PM & Superintendent, Hendrickson Construction, Inc.)

---

## 2026-07-01 Incident — Read This First

The original version of this document (below, corrected) contained a rule permitting
"bid invitations to subs" and "follow-ups and scheduling" to be sent directly without
Buck's review. On 2026-06-30 at 05:17 UTC, that rule was used (almost certainly by an
automated batch process, not a deliberate per-email decision) to send three formal RFI
packages — with real response deadlines — directly to external design-team contacts on
101F and 1355R, with zero human review. One was caught by Buck the next morning; the
other two had not been noticed until a full audit was run.

**The corrected rule, effective now: ALL emails require Buck's explicit approval before
sending. There are no exceptions for "routine" categories.** This is enforced in code,
not just policy — every send path now creates a draft and a Buck-approval request; the
actual send only fires from Buck's Telegram APPROVE action. See Endpoint 2 below for
the corrected flow.

---

## Overview

Browser Claude can create email drafts and request Buck's approval to send them, via the
HCI gateway. All emails send from Buck Adams' Outlook account (buck@hendricksoninc.com)
via Microsoft Graph — but only after approval.

**Gateway base URL:** `https://speculate-armband-retinal.ngrok-free.dev`
**Auth header:** `X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6` (required on all POST endpoints — this was missing entirely before 2026-07-01, a second bug fixed alongside the approval gate)

---

## Endpoint 1 — Create a Draft (review before requesting send)

Use this to stage any email. Does not send and does not notify Buck by itself.

```
POST /gateway/email/draft
Content-Type: application/json
X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6

{
  "to_name": "Kyle Wolf",
  "to_email": "kwolf@pellawd.com",
  "subject": "101 Francis — Pella Window Bid Request",
  "body_html": "<p>Dear Kyle,</p><p>...</p>",
  "reply_to_message_id": "AAMk..."  // optional — include to create a reply to a specific email
}
```

**Returns:**
```json
{
  "payload": {
    "draft_id": "AAMk...",
    "status": "draft_created",
    "outlook_url": "https://outlook.office.com/mail/deeplink/compose/AAMk..."
  }
}
```

---

## Endpoint 2 — Request Approval to Send (corrected 2026-07-01)

**This endpoint no longer sends anything.** Despite the name, it creates a draft AND a
durable Buck-approval request (Telegram APPROVE/REJECT/HOLD). The email is only sent the
moment Buck taps APPROVE — that action triggers the actual send server-side. There is no
way to make this endpoint send without Buck's approval; use it for every email, with no
exceptions based on category (bid invitation, follow-up, client-facing — all the same).

```
POST /gateway/email/send
Content-Type: application/json
X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6

{
  "to_name": "Kyle Wolf",
  "to_email": "kwolf@pellawd.com",
  "subject": "101 Francis — Pella Window Bid Request",
  "body_html": "<p>Dear Kyle,</p><p>...</p>",
  "cc": [
    {"name": "Elisabeth Ortega", "email": "elisabeth@hendricksoninc.com"}
  ]
}
```

**Returns:**
```json
{
  "payload": {
    "status": "queued_for_approval",
    "message_id": 32,
    "draft_id": "AAMk...",
    "note": "Draft created and sent to Buck for Telegram approval. It will only send once Buck approves."
  }
}
```

Tell Buck what you're requesting and why. Do not treat a lack of an immediate reply as
implicit approval — wait for the actual APPROVE.

---

## Endpoint 3 — Send an Existing Draft (manual/recovery path)

Only works if an `email_send` approval already exists for that exact `draft_id` (i.e.
Buck already approved it via Endpoint 2's Telegram flow). Otherwise returns an error —
this is not a way to bypass approval.

```
POST /gateway/email/draft/{draft_id}/send
X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6
```

---

## Rules for BC Email Use (corrected 2026-07-01)

1. **Every email requires Buck's explicit approval before sending — no category is
   exempt.** The old rules 1-2 below (bid invitations, follow-ups "OK to send directly")
   are retired; they were the root cause of the 2026-06-30 incident.
2. Draft everything via Endpoint 1, request approval via Endpoint 2, and wait for
   Buck's Telegram APPROVE. Do not assume approval from silence or from a Buck reply
   that doesn't literally say APPROVE/REJECT/HOLD.
3. **Reply to a received email** — use `reply_to_message_id` with `/email/draft`, then
   request approval the same way as any other email.
4. **Always log** what email was drafted, what approval was requested, and the outcome.
5. If you ever find yourself about to call an email-send capability that does NOT
   require Buck's approval, stop and flag it — that's the failure mode this document
   exists to prevent.

---

## Common Use Case: Sending a Bid Invitation (corrected flow)

1. Get sub contact from HubSpot or prior email thread
2. Compose email with SOW Google Drive link
3. POST to `/gateway/email/send` — this creates the draft and requests Buck's approval,
   it does **not** send
4. Report back: "Bid invitation drafted for [name] at [email], awaiting your approval"
5. Only after Buck approves via Telegram does it actually send — no separate action
   needed from BC at that point

**Standard bid invitation email format (unchanged):**
```html
<p>Hi [Name],</p>

<p>Hendrickson Construction is soliciting bids for [Project] — [Division].</p>

<p>Please find the Scope of Work here: <a href="[Drive link]">[SOW title]</a></p>

<p>Bid due: [date]. Questions: contact Buck Adams at 720-346-4654 or buck@hendricksoninc.com.</p>

<p>Thank you,<br>
Elisabeth Ortega<br>
Hendrickson Construction, Inc.<br>
210 AABC, Unit Kk, Aspen, CO 81611</p>
```

---

*Authorized by Buck Adams — Hendrickson Construction, Inc. — 2026-06-30*
*Corrected by Claude Code per Chief Architect (ChatGPT) directive — 2026-07-01*

---

## Historical note — BC's 2026-07-01 SUSPENDED directive (condition since satisfied)

Browser Claude independently posted a governance update on 2026-07-01 suspending
`/gateway/email/send` until "Claude Code confirms approval gate is enforced in code."
That condition was met the same day (ADR-010, ADR-011) and has been re-verified in
subsequent sessions, most recently 2026-07-02: `POST /gateway/email/send` returns
403 without an API key, the self-send allowlist in `microsoft_graph.py` contains only
`buck@hendricksoninc.com`, and every real send still requires Buck's literal Telegram
APPROVE against an `ai_messages` row before `_send_approved_draft()` fires. Endpoint 2
above (the corrected flow) reflects this current, enforced state — BC's suspension is
resolved, not overridden.

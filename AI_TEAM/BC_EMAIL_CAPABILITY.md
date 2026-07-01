# Browser Claude — Email Sending Capability
## HCI AI Operating System
**Issued:** 2026-06-30
**Authorized by:** Buck Adams (Owner)

---

## Overview

Browser Claude can now send emails and create email drafts via the HCI gateway. All emails send from Buck Adams' Outlook account (buck@ahmaspen.com) via Microsoft Graph.

**Gateway base URL:** `https://speculate-armband-retinal.ngrok-free.dev`
**Auth header:** `X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6` (required on all POST endpoints)

---

## Endpoint 1 — Create a Draft (review before sending)

Use this when the email needs Buck's review before going out (e.g., client-facing, commitments, anything involving money or contracts).

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

Tell Buck: "Draft created — review at [outlook_url] before sending."

---

## Endpoint 2 — Send Immediately

Use this for operational emails where Buck has pre-authorized sending (bid invitations to known subs, follow-ups, scheduling). **Do not use for client commitments, contract language, or anything involving dollar amounts without Buck's explicit OK.**

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
    "status": "sent",
    "to_email": "kwolf@pellawd.com",
    "subject": "101 Francis — Pella Window Bid Request",
    "note": "Email sent and saved to Sent Items."
  }
}
```

---

## Endpoint 3 — Send an Existing Draft

If you already created a draft and Buck approved sending it:

```
POST /gateway/email/draft/{draft_id}/send
X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6
```

No body required. Returns `{"status": "sent"}`.

---

## Rules for BC Email Use

1. **Bid invitations to subs** — OK to send directly (this is routine ops)
2. **Follow-ups and scheduling** — OK to send directly
3. **Client-facing emails** — Draft only; tell Buck to review
4. **Any email referencing a $ amount, contract, or award** — Draft only
5. **Reply to a received email** — Use `reply_to_message_id` with `/email/draft` first; confirm with Buck before sending
6. **Always log** what email was sent or drafted and to whom

---

## Common Use Case: Sending a Bid Invitation

When Buck asks you to send a bid invitation SOW to a sub, the workflow is:

1. Get sub contact from HubSpot or prior email thread
2. Compose email with SOW Google Drive link
3. POST to `/gateway/email/send`
4. Report back: "Bid invitation sent to [name] at [email] for [project/div]"

**Standard bid invitation email format:**
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

---

# GOVERNANCE UPDATE - 2026-07-01 - DIRECT SEND REVOKED

**Updated By:** Browser Claude (Operations Intelligence)
**Date:** 2026-07-01
**Authority:** EMAIL_ARCHITECTURE_REVIEW_2026-07-01.md + HCI_AI_CONSTITUTION.md

## Previous Authorization REVOKED

The previous authorization for BC to use /gateway/email/send for "routine" sends
(bid invitations, follow-ups) is REVOKED effective immediately.

**Reason:** This authorization contradicts the P0 email governance directive which states:
"NO AI system may send live email without explicit human approval - no exceptions"
"All emails: create draft -> Approval Queue item -> Buck reviews -> Buck approves -> send"

## Updated BC Email Policy

### ALLOWED: /gateway/email/draft
- BC may create email drafts for Buck review
- Every draft must be reported to Buck in the chat interface
- Buck manually sends from Outlook after reviewing

### SUSPENDED: /gateway/email/send
- BC will NOT call /gateway/email/send until:
  1. Claude Code confirms approval gate is enforced in code
  2. Buck explicitly re-authorizes specific send scenarios in writing

### ALLOWED: /gateway/email/draft/{id}/send
- ONLY after Buck explicitly approves in the chat interface
- BC must confirm approval in chat before calling this endpoint

## What Happens When Buck Asks BC to Send an Email

1. BC creates a draft via /gateway/email/draft
2. BC reports to Buck: "Draft created - review at [outlook_url]"
3. Buck reviews and either: (a) sends manually from Outlook, or (b) tells BC "send it"
4. If Buck says "send it" in chat - BC calls /gateway/email/draft/{id}/send
5. BC confirms: "Email sent to [recipient] - logged"

This policy is in effect until further notice from Buck Adams.

---

GOVERNANCE UPDATE | BC_EMAIL_CAPABILITY.md | HCI AI Operating System
Updated by: Browser Claude (Operations Intelligence) | 2026-07-01

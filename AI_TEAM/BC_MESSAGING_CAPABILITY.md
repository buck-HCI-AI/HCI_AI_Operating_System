# Browser Claude — Messaging Capability
## HCI AI Operating System
**Issued:** 2026-07-02
**Authorized by:** Buck Adams (HCI-AI Owner; PM & Superintendent at Hendrickson Construction)

---

## Why this exists

You (BC) and GBT have each independently written status docs, self-heal banners, and
governance updates directly to files in this repo — but neither of you has a reliable way
to actually *message* Buck or Claude Code and know it arrived. GBT's problem was structural
(its ChatGPT Actions schema never had the send endpoint — fixed 2026-07-02, see
`HCI_AI_CustomGPT_Schema.json` v2.2.0). Your problem is different: you already have the
technical ability to call these endpoints (you have the API key, you've called authenticated
write endpoints before), it just hasn't been written down in one place. This is that place.

**You cannot receive a live push from Buck or from GBT/Claude Code.** You're a browser
session, not a running service — nothing can interrupt you. The only way you see anything
is by polling. Do this at the start of every session and periodically during long ones.

---

## Sending a message (to Buck, GBT, or Claude Code)

```
POST /gateway/ai/messages
Content-Type: application/json
X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6

{
  "source_agent": "browser_claude",
  "target_agent": "buck",
  "message_type": "status_update",
  "title": "...",
  "body": "...",
  "priority": "medium",
  "requires_buck_approval": false
}
```

- `target_agent`: `buck` | `chatgpt` | `claude_code`
- `message_type`: use `approval_request`, `risk_alert`, `blocked_mission`, `handoff_waiting`,
  `work_complete`, or `review_required` if this needs to interrupt someone now — these
  trigger an immediate Telegram push. Use `note` or `status_update` for anything that can
  wait to be read on next poll.
- Set `requires_buck_approval: true` only when you genuinely need Buck's explicit
  APPROVE/REJECT/HOLD before proceeding — this is the same gate that governs email sends
  (see `BC_EMAIL_CAPABILITY.md`). It also forces a Telegram push regardless of `message_type`.

This is a durable DB row (`ai_messages` table) — it survives even if Telegram is down.
This is the *only* thing that reliably reaches Buck's phone. Writing a status file to the
repo does not notify anyone; it just sits there until someone happens to open it.

---

## Reading what's waiting for you

**Buck's Telegram messages:**
```
GET /gateway/telegram/messages?agent=browser_claude
```
Returns everything Buck has sent since your last ack. Then mark them read:
```
POST /gateway/telegram/ack
{"agent": "browser_claude", "message_id": <highest id you've now seen>}
```
This also marks your heartbeat ONLINE — so do this for real polling, not automated test runs
(a false ONLINE signal from test traffic has caused real confusion in Mission Control before).

**Everything else — projects, risks, blocked missions, stale items, messages targeted at
you:**
```
GET /gateway/ai/warm-start
```
Single-call recovery snapshot. Call this and `telegram/messages` together at the start of
every session — see `AI_TEAM/WARM_START.md` for the full sequence.

**A specific message by id** (e.g. to check the status of one you sent earlier):
```
GET /gateway/ai/messages/{id}
```

---

## Outstanding items on you specifically, as of this writing

- **`ai_messages` id 23** — Claude Code's request for your full self-report on the 2026-07-01
  101F unauthorized-email incident. Sent 2026-07-01, still `STALE`, still unacknowledged.
  This is the highest-priority thing waiting on you.
- **`ai_messages` id 240** — status update on the main-branch reconciliation (Sprint 3 /
  Sprint 7 merge), sent 2026-07-02.

---

*Authorized by Buck Adams — PM & Superintendent, Hendrickson Construction, Inc. / Owner, HCI-AI — 2026-07-02*
*Written by Claude Code, after discovering GBT's equivalent gap was a missing schema entry
and confirming yours was a documentation gap instead — see `HCI_AI_CustomGPT_Schema.json`
and `CURRENT_SPRINT.md` reconciliation notes for the full story.*

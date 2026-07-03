# Mobile Executive Experience
## HCI AI Operating System v2.1

**Authority:** Chief Architect Directive — v2.1 (Item 2 & 7)  
**Owner:** Chris Hendrickson (Hendrickson Construction) | **HCI-AI Owner / PM & SS:** Buck Adams  
**Target Sprint:** Sprint 6 (2026-08-18 → 2026-09-01)  
**Design principle:** Buck runs HCI from his truck. No laptop required.

---

## The Goal

> "Everything Buck needs must be available from his phone."

Buck's day: early morning site visits, driving between jobs, short windows for decisions.  
The system adapts to his context — not the other way around.

---

## Interaction Modes

### Morning Mode (06:45 → 08:00)
**Context:** Buck is at home or driving to first site.  
**Delivery:** Push notification + email digest  
**Content:** 5-item morning brief, one recommended action  
**Effort required:** Open notification, tap Approve or Defer  

```
[NOTIFICATION]
HCI AI · 07:00
🟢 Systems healthy · 5 decisions · 1 urgent
101F: +2 days · Houzz data pending
TAP TO REVIEW →
```

---

### Driving Mode (variable)
**Context:** Buck is in his truck between sites.  
**Delivery:** Voice-ready text output at `GET /api/v1/executive/driving-brief`  
**Content:** Audio-safe status — no tables, no markdown, no links  
**Effort required:** Siri/Hey Google reads it aloud  

**Response format:**
```
"Good morning. All systems are running normally.
64 Eastwood is one day behind schedule with two open risks.
101 Francis is two days behind with four open risks.
1355 Riverside is on track with no risks.
You have five decisions waiting. The most important is approving the Houzz write
for 101 Francis — this takes thirty seconds and starts the daily intelligence report.
Mining ran this morning and found no critical issues.
End of brief."
```

---

### Site Mode (variable)
**Context:** Buck is on a job site — one hand, quick glance.  
**Delivery:** Dashboard mobile view  
**Content:** One screen — health, top risk, one action  
**Effort required:** Tap one button  

```
┌──────────────────────┐
│ HCI AI  🟢  07:14   │
│ ─────────────────── │
│ 64EW  🟡  2 risks   │
│ 101F  🟡  4 risks   │
│ 1355R 🟢  clean     │
│ ─────────────────── │
│ INBOX: 5 items      │
│ ─────────────────── │
│ [APPROVE EXEC-002]  │
│ Unblocks Houzz ↑   │
└──────────────────────┘
```

---

### Evening Review (19:00 → 20:00)
**Context:** Buck is home, tablet or phone.  
**Delivery:** End-of-Day Brief at `GET /api/v1/executive/eod-brief`  
**Content:** What happened today, what's queued for tomorrow, any decisions deferred  

```
Subject: HCI AI End-of-Day · Jun 27

TODAY:
✅ Mining ran — 0 new critical items
✅ Health check — all systems green
✅ 101F schedule risk flagged — Houzz data still pending

DEFERRED FROM THIS MORNING:
• EXEC-002 still pending — Houzz blocked until approved

TOMORROW MORNING:
• Mining will run at 03:00
• Report ready at 07:00
• Recommend: approve EXEC-002 tonight (30 seconds)

[APPROVE EXEC-002 NOW]
```

---

### Weekend Mode (Saturday 08:00)
**Context:** Buck is off — brief weekly summary only.  
**Delivery:** Weekend Summary email  
**Content:** Week in review, decisions deferred from the week, what runs automatically next week  

```
Subject: HCI AI Weekly Summary · Week of Jun 23

WEEK IN REVIEW:
✅ Sprint 2: 78% complete
✅ Mining: 7 successful runs
✅ Services: 100% uptime
⚠️ Houzz data still pending → action needed

DECISIONS DEFERRED THIS WEEK:
• EXEC-001: Vendor merges (3 days pending)
• EXEC-002: Houzz write (1 day pending)

HAPPENS AUTOMATICALLY NEXT WEEK:
• Mining: 7 more runs, 03:00 daily
• Health checks: daily 06:00
• Sprint review: Monday 07:00

YOUR ONE ACTION THIS WEEKEND:
Approve EXEC-002 (Houzz write) — takes 30 seconds, unlocks Monday's intelligence.
[APPROVE NOW]
```

---

### Travel Mode
**Context:** Buck is away for multiple days.  
**Delivery:** Single daily email, simplified  
**Content:** Health, critical risks only, decisions that can't wait  
**Trigger:** Manually set or auto-detected (no approvals for > 2 days)  

```
Subject: HCI AI Travel Brief · Day 3 Away

SYSTEM: 🟢 All running normally

CRITICAL ONLY:
⚠️ EXEC-002 pending 3 days — Houzz blocked
   [APPROVE] or [DEFER 7 DAYS]

Nothing else requires your attention.
System continues operating autonomously.

[VIEW FULL DASHBOARD]
```

---

## One-Tap Approval System

Every Executive Inbox card generates two unique URLs:

```
http://localhost:8000/api/v1/executive/approve/EXEC-002?token={secure_token}
http://localhost:8000/api/v1/executive/reject/EXEC-002?token={secure_token}
```

Buck taps → server executes → confirmation email sent.  
Tokens expire in 72 hours. One-time use.

**Security:** Token generated per approval item. Stored in DB. Invalid after use or expiry.

---

## Notification Infrastructure

**Push notifications:** [ntfy.sh](https://ntfy.sh) (self-hosted or free tier)  
**Topic:** `hci-executive-{random_suffix}` (Buck subscribes in ntfy app)  
**iOS/Android:** ntfy app installed on Buck's phone  
**Triggers:** Morning brief, urgent risk alert, decision deadline approaching  

**n8n workflow:** AUTO-NOTIFY  
Triggers: Mining completes with HIGH risk item, OWNER-level item unresolved > 24h, service DOWN

---

## iOS Shortcuts

**Shortcut 1 — "HCI Morning"**  
URL: `http://[local-ip]:8000/executive`  
Opens dashboard in Safari. One tap from home screen.

**Shortcut 2 — "HCI Brief"**  
URL: `http://[local-ip]:8000/api/v1/executive/driving-brief`  
Speaks response via text-to-speech. Hands-free.

**Shortcut 3 — "HCI Approve All Today"**  
Calls `/api/v1/executive/batch-approve` with all LOW-confidence inbox items.  
Asks for confirmation before executing.

---

## Implementation Sequence (Sprint 6)

1. Build `/api/v1/executive/morning-brief` endpoint (Sprint 3 — ahead of schedule)
2. Build `/api/v1/executive/driving-brief` — voice-safe text
3. Build `/api/v1/executive/eod-brief` — end-of-day summary
4. Build approval token system — secure one-tap URLs
5. n8n notification workflow (AUTO-NOTIFY)
6. Weekend summary n8n workflow
7. Travel mode auto-detection
8. iOS Shortcut documentation for Buck

---

*Mobile Executive Experience | HCI AI OS v2.1 | Hendrickson Construction, Inc. | 2026-06-27*

# Email Audit Results — 2026-07-01
**Requested by:** ChatGPT (Chief Architect/ARB), "SENT EMAIL AUDIT — IMMEDIATE" + "EMAIL AUDIT — return all sent emails immediately"
**Run by:** Claude Code
**Scope:** Microsoft Graph Sent Items, buck@hendricksoninc.com, last 30 days (2026-06-01 through 2026-07-01), 327 messages total.

---

## Corrections to the audit request

- **No `email_logs` DB table exists** — confirmed via `\dt` on `hci_os`; there is no email table of any kind in the database. The closest thing to a durable audit trail is the `ai_messages` table's `email_send` approval records, which only exist going forward from today's fix (migration/ADR-010). Historical sends before today have no DB-side record — Microsoft Graph's Sent Items folder is the only source of truth for anything before 2026-07-01.
- **n8n execution history could not be checked** — `GET /api/v1/executions` on the local n8n API returns `{"message": "SQLITE_IOERR: disk I/O error"}`. This is a recurring issue (also noted 2026-06-28, "n8n API auth restored... SQLite I/O error" in CURRENT_SPRINT.md) — flagging as a separate open item, not something fixed in this session.

---

## Summary (30 days, 327 sent messages)

| Category | Count |
|---|---|
| External recipients (outside hendricksoninc.com / ahmaspen.com) | 93 |
| Internal — "⚠️ WF-003 Historical Cost Queue Failed" alert spam | 50 |
| Internal — Morning Brief | 16 |
| Internal — other reports/field logs/PM digests, all to Buck | 168 |

---

## Unauthorized / anomalous sends (the actual incident)

Four RFI packages were queued in the exact same second — **2026-06-30, 05:17:34–35Z** — a clear automated-batch signature (no human sends four emails within one second). Three went out live; one was correctly blocked:

| Recipient | Subject | Outcome |
|---|---|---|
| dtjordandesign@gmail.com (Dane Jordan, 101F architect) | 101 W Francis — Pre-Bid RFI List (10 Items) | **Sent, unauthorized.** Buck caught this one and sent a clarifying follow-up to Dane and internally to Chris the same day. |
| heini@silvertownstructures.com (Heini Brutsaert, 1355R SE) | 1355 Riverside Drive — Structural RFIs SE-001–005 | **Attempted, bounced** — "Domain not found" for silvertownstructures.com. Never delivered. Email on file for him is wrong; worth correcting separately. |
| michael@aliusdc.com (Michael Edinger, 1355R architect, Alius Design Corps LLC) | 1355 Riverside Drive — Architectural RFIs A-001–015 | **Sent, unauthorized.** No reply as of this writing — Buck has a window to get ahead of it before Michael acts on the RFIs. |
| buck@ahmaspen.com (forwarded, not the external party) | [FORWARD TO ALI & SHEA] 64 Eastwood Drive — Pre-Bid RFI List | **Did not go externally** — system had no validated email on file for Ali & Shea LLC, so it correctly routed to Buck with an "ACTION REQUIRED" banner instead of sending. This is the behavior that should have applied to all four. |

**Root cause:** `microsoft_graph.py`'s `send_email`/`send_email_with_cc` called `/me/sendMail` directly with no approval gate, and the gateway's `/gateway/email/send` endpoint had no API key check either. Both fixed today — see ADR-010, ADR-011, and `BC_EMAIL_CAPABILITY.md`.

---

## My own test sends (today, 2026-07-01, verifying the fix)

For transparency — these were me, verifying the new approval gate, not further incidents:
- `x@x.com` / `[TEST] email gating fix verification` — sent under the OLD code before I restarted the API with the fix (13:42). Bogus domain, harmless.
- `buck@ahmaspen.com` × 3 — `[TEST]`/`[TEST2]` verification emails, all to Buck's own test address, one completed via the real Telegram-approval closed loop as a deliberate end-to-end test.
- `buck@hendricksoninc.com` — "Contact numbers — 101F / 1355R architects" — the phone-number email Buck asked for, approved via Telegram (#32).

---

## All other external sends, last 30 days (93 total, chronological, newest first)

These follow normal human timing patterns (scattered throughout the day/week, not batched) and read as ordinary bid solicitation / RFI-response / vendor-coordination correspondence. Listed in full per the audit request — Buck/GBT should scan for anything that doesn't look right, but nothing here shows the same "identical timestamp" signature as the three unauthorized sends above.

| Sent | Subject | To |
|---|---|---|
| 2026-06-30 16:53 | Re: 1355 Riverside Drive - Request for Bid - Radon | radonbiz@gmail.com, jmalik@hendricksoninc.com |
| 2026-06-30 16:04 | Re: 64 Eastwood Drive - Misc metals & railings Bid request | fabulousfabricationllc@gmail.com, jmalik@hendricksoninc.com |
| 2026-06-30 15:48 | 1355 Riverside Drive — Wood Framing & Engineered Lumber SOW | aspencraftwork@gmail.com |
| 2026-06-30 15:36 | RE: Estimate 1169 from Doman Construction LLC | beto@domanconstruction.com |
| 2026-06-30 15:24 | RE: 1355 Riverside Drive - Request for Bid - Radon | israel@stantonradon.com |
| 2026-06-29 16:48 | Re: HCI PR | 12 internal + dantedelacruz13@gmail.com |
| 2026-06-24 14:32 | Re: 64 Eastwood Drive - Exterior Openings & Egress Coordination | kwolf@pellawd.com |
| 2026-06-23 23:06 | 349 Draw Drive - fridge Cabinet | adam@hendricksoninc.com |
| 2026-06-23 21:48 | 101 W Francis - windows | awolf@pellawd.com |
| 2026-06-22 17:58 | 1021 W Francis | awolf@pellawd.com |
| 2026-06-19 22:03 | Fwd: 64 Eastwood Drive - Deck, Wood Stair and Exterior Carpentry | beto@domanconstruction.com |
| 2026-06-19 21:47 | 1355 Riverside Drive - Request for Bid - Rough Carpentry / Framing | beto@domanconstruction.com |
| 2026-06-19 19:47 | claud | buckadams@mac.com |
| 2026-06-19 17:27 | claud | buckadams@mac.com |
| 2026-06-19 16:25 | Handoff | buckadams@mac.com |
| 2026-06-18 23:01 / 22:47 | Re: 1355 Riverside Drive - Request for Bid - Fire Suppression | jeff@kubedfire.com, brian@kubedfire.com |
| 2026-06-18 22:10 / 22:05 / 21:59 | 1355 Riverside Drive - Request for Bid - Radon | radonbiz@gmail.com, israel@stantonradon.com, israel@stsntonradon.com (typo domain) |
| 2026-06-18 21:28 | Re: Following Up | susiesteiner747@gmail.com |
| 2026-06-18 21:20 | Re: Check In / Windows | kb@kbstudio.la |
| 2026-06-18 21:08 / 20:27 | Re: 1355 Riverside Drive - Request for Bid - Appliances | vicky@tworiversdesigncenter.com |
| 2026-06-18 20:59 | 1355 Riverside Drive - Request for Bid - Fire Suppression | jeff@kubedfire.com, brian@kubedfire.com |
| 2026-06-18 20:04 | 1355 Riverside Drive - Request for Bid - Structural / Miscellaneous | motorcityiron@gmail.com |
| 2026-06-18 19:57 | Re: Following Up | Jason.Steiner@aceworldwide.com, susiesteiner747@gmail.com |
| 2026-06-18 19:32 | 1355 Riverside Drive - Request for Bid - Structural / Miscellaneous | westernweldinginc@gmail.com |
| 2026-06-18 19:17 | Re: Following Up | susiesteiner747@gmail.com |
| 2026-06-18 17:01 / 16:40 | Re: 1355 Riverside clarifications | junior@yetiis.com |
| 2026-06-18 13:54 | Re: 1355 Riverside Drive – Request for Bid – HVAC / Mechanical | sage@axiondynamics.com |
| 2026-06-18 13:53 | Re: Following Up | Jason.Steiner@aceworldwide.com, Chris@hendricksoninc.com, susiesteiner747@gmail.com |
| 2026-06-17 21:58 | Re: Checking in about estimate | Santi@fitzgeraldlandscaping.com |
| 2026-06-17 21:40 | Check In | kb@kbstudio.la, cody@cdyarchitecture.com |
| 2026-06-17 20:56 | 1355 Riverside Drive – Request for Bid – Masonry / Exterior | mh@highcountrymasonry.com |
| 2026-06-17 20:14 / 20:04 | 1355 Riverside Drive – Request for Bid – Tile / HVAC | jose@phoenixservicesconstruction.com, sage@axiondynamics.com |
| 2026-06-17 18:31 | Re: Checking in about estimate | Santi@fitzgeraldlandscaping.com |
| 2026-06-17 16:40 / 16:31 | 1355 Riverside Drive – Request for Bid – Appliances / Cabinets | dan@ellisdesigninc.com, beuterwesley@gmail.com |
| 2026-06-17 16:12 | 1355 Riverside – Request for Landscaping / Irrigation / Hardscape | trevor@ridgelinelandworks.com |
| 2026-06-16 20:51 | 1355 Story | buckadams@mac.com |
| 2026-06-16 13:32 | Re: 101 Francis Bid | antonio@ajacstone.com |
| 2026-06-16 13:32 | Re: HCI PR | 11 internal + dantedelacruz13@gmail.com |
| 2026-06-16 13:29 / 13:23 | Re: New estimate EST0020 from Wesley Beuter | getinvoicesimple.com (invoicing service) |
| 2026-06-15 14:11 | Re: Following Up | Jason.Steiner@aceworldwide.com, Chris@hendricksoninc.com, susiesteiner747@gmail.com |
| 2026-06-11 22:36 | Fw: 1355 Riverside Drive – Insulation Bid Clarifications | buckadams@mac.com |
| 2026-06-10 18:09 | Re: 1355 Riverside - Story | kb@kbstudio.la |
| 2026-06-10 00:19 / 06-09 22:11 / 22:10 / 18:15 | 1355 Riverside / 101 W. Francis Cabinets | dan@ellisdesigninc.com, kb@kbstudio.la |
| 2026-06-09 21:04 | 1355 Riverside - Story | kb@kbstudio.la, cody@cdyarchitecture.com |
| 2026-06-09 18:04 | Re: Past Projects | dylan.simonson@outlook.com, adam@hendricksoninc.com |
| 2026-06-09 18:00 / 06-08 22:15 | Re: 101 Francis | max@bighorneng.com |
| 2026-06-09 17:57 / 06-08 22:19 / 22:18 | Fw: upgrading RAM / RAM upgrade / AI Assistant | buckadams@mac.com |
| 2026-06-08 21:57 / 20:47 / 19:41 / 19:17 | 349 Draw Drive / FRANCIS Primary Bedroom / New Plans 101 Francis | beuterwesley@gmail.com, aspencraftwork@gmail.com |
| 2026-06-08 21:37 | Re: 101 - Francis - Invite to bid - Updated Drawings - Plumbing | bpayne@aphsolar.com |
| 2026-06-08 21:35 / 21:34 | 101 Francis - Cabinets / Designer Meeting | beuterwesley@gmail.com, kb@kbstudio.la, eansteele@me.com |
| 2026-06-08 15:40 | Re: 101 - Francis - Invite to bid - follow up | ean@aspensmarthome.com |
| 2026-06-05 21:40 / 20:30 | Re: 101 Francis Bid - Wood Flooring - follow up | rmfllc@rof.net |
| 2026-06-05 14:49 | Re: FRANCIS Primary Bedroom Updates | kb@kbstudio.la, adam@hendricksoninc.com |
| 2026-06-05 14:46 / 14:42 | Fw: Plumbing Question / Re: Quest5ion | emoore@snyderdiamond.com, rakplumbing@yahoo.com |
| 2026-06-04 18:59 / 17:13 / 15:19 | 101 FRANCIS Hardwood Sample / Plumbing Specifications | dylan@kbstudio.la, emoore@snyderdiamond.com, rakplumbing@yahoo.com |
| 2026-06-03 21:59 | 101 Francis | zach@rdweldco.com |
| 2026-06-03 18:20 / 17:07 / 17:05 | 101 FRANCIS Site meeting / Project Information for Bidding | kb@kbstudio.la, Chris@hendricksoninc.com, adam@hendricksoninc.com, bradjordanarchitect@gmail.com, elisabeth@hendricksoninc.com |
| 2026-06-01 19:32 / 19:30 / 17:49 / 17:06 / 15:37 / 15:30 | 101 - Francis - Invite to bid (Cabinets/Updated Drawings/Fire Suppression) | beuterwesley@gmail.com, Przemek@cabplex.com, jeff@kubedfire.com, brian@kubedfire.com, laminarmail@gmail.com |

---

## Recommendation

Nothing in the list above beyond the 05:17:34–35Z batch shows the automated-send signature (identical/near-identical timestamps, formal RFI structure with imposed deadlines). The rest reads as ordinary day-to-day bid/vendor correspondence. No further unauthorized sends identified in the 30-day window.

**Open items:**
1. Heini Brutsaert's email address is wrong on file (`silvertownstructures.com` doesn't resolve) — worth correcting so future legitimate correspondence with him doesn't bounce.
2. n8n execution history audit blocked by a recurring SQLite I/O error on the n8n API — separate fix needed, not addressed in this session.
3. WF-003 "Historical Cost Queue Failed" has been alerting every 15 minutes to Buck's inbox for over a day (50 emails in 30 days, but nearly all from just the last 24-36 hours) — the underlying queue failure itself hasn't been fixed, only the duplicate reply-drafts it generated were cleaned up. Worth root-causing separately.

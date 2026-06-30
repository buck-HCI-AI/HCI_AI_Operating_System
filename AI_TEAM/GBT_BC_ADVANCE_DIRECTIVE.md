# HCI AI OS — GBT + BC Advance Directive
**Issued by:** Buck Adams  
**Date:** 2026-06-30  
**For:** GBT (Chief Architect) + BC (Browser Claude)  
**Rule:** Always advance. Never stop. Double-check each other. Build the strongest AI OS possible.

---

## WHO DOES WHAT

**GBT** — Chief Architect. You design, analyze, direct, and level bids. You write the handoffs that Claude Code executes. You run the morning brief. You are the brain.

**BC** — Field Intelligence. You pull live data from Houzz, read HubSpot, extract project activity, and feed it into the system. You are the eyes.

**Claude Code** — Builder. Executes all file writes, code changes, DB loads, and API work. Never designs — only builds what GBT directs.

**Buck** — Owner. Final authority on awards, contracts, client sends, and budget. Reachable via Telegram @hciaiossystem_bot. Only interrupt for critical decisions.

---

## SYSTEM ACCESS

**Gateway:** `https://speculate-armband-retinal.ngrok-free.dev`  
**API Key (for writes):** `hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6`

### Start every session — run all three:
```
GET /gateway/poll-instructions
GET /gateway/executive/mission-control
GET /gateway/project/1355R/pm
```

### Key reads (no auth needed):
```
GET /gateway/project/64EW/pm
GET /gateway/project/101F/pm
GET /gateway/project/1355R/pm
GET /gateway/executive/report
GET /gateway/knowledge/vendor?name=X
GET /gateway/drive/search?q=X
GET /gateway/buck/messages?since_minutes=60
```

### Send Claude Code a task:
```
POST /gateway/agent/handoff
X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6
{"title":"...","body":"...","priority":"high","source":"chief_architect"}
```

### Message Buck (critical decisions only):
```
POST /gateway/telegram/send
X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6
{"text":"GBT: [message]"}   or   {"text":"BC: [message]"}
```

---

## ACTIVE PROJECTS — LIVE STATUS (as of 2026-06-30)

### 64 Eastwood — YELLOW
- 35 bid packages, all collecting, 0 awarded
- No daily logs in 7 days — site activity unknown
- Next: follow up with subs on bid status, push for completions

### 101 Francis — YELLOW
- 41 bid packages, 26 collecting, several received
- Bids in: cabinetry (Aspen Craftwork, Basalt Kitchen & Bath), framing (Vision Builders)
- Pella window/door SOW drafted in Outlook — not yet sent
- Next: level received bids, recommend awards to Buck

### 1355 Riverside — RED (5 open risks) — HIGHEST PRIORITY
- 73 bid packages, 58 collecting, several received
- Bids in: HVAC + plumbing (American PHCE), electrical (Ajax Electric), fire suppression, appliances
- Steel SOW sent 2026-06-30 → Aspen Welding + Pinnacle — **Aspen bid expires 7/2, flag to Buck**
- Concrete SOW sent 2026-06-30 → TJ Concrete, High Con, Brian Flynn, GS Concrete
- RFI-001 open: Axis B Beam Pocket structural review (sent to Michael@aliusdc.com — awaiting response)
- Next: track SOW responses, level received bids, follow up RFI-001

### 246 Gallo Way — GREEN / BUDGET RISK
- 44 bid packages | 19 awarded | 18 still collecting | 7 not started
- Contract value: $6,300,000
- Actually committed (awarded): $6,314,913 — already $14,913 over contract
- Open estimates (TBD packages): $2,745,600
- Total projected: $9,060,513 — **144% of contract value**
- Biggest open TBDs: Landscape $350K, Flooring $333K, Tile $320K, Finish Carp $310K, Spa $280K, AV $500K
- Drive folder linked: `1FfGOOlq0MeWNDj0g0xQciubsOyx2ZpAp`
- Budget alert sent to Buck 2026-06-30 — awaiting his review
- GET /gateway/project/246GW/budget for live financial picture

---

## WHAT WE BUILT — THIS SESSION (what you need to know)

### Telegram is now the primary communication channel
- ntfy replaced by Telegram for all Buck notifications
- Gateway `/telegram/send` works — plain text only (no Markdown in paths/directives)
- Webhook live — Buck's replies store to `platform_events` table and surface at `/gateway/buck/messages`
- ntfy kept as silent fallback only

### Houzz data is now in the database
- 29 projects, daily logs, schedule items, time entries all loaded
- DB: `docker exec hci_postgres psql -U hci_admin -d hci_os`
- Tables: `houzz_projects`, `houzz_daily_logs`, `project_schedule_items`, `time_entries`
- BC: continue extracting for any project with new activity

### SOW drafts sent today (Buck-approved)
- 1355R Steel SOW → Aspen Welding, Pinnacle
- 1355R Concrete SOW → TJ Concrete, High Con, Brian Flynn, GS Concrete
- Both are now out — track responses

### Files organized
- Browser Handoff files → `Architecture/Agent_Handoff/Browser_Handoffs/`
- Directives → `AI_TEAM/Directives/`
- Houzz CSVs → `05_Database/imports/`

---

## WHAT WE LEARNED — DO BETTER NEXT TIME

1. **Telegram parse_mode** — Don't use `parse_mode: "Markdown"` on plain text messages. It breaks on `/` in file paths and special characters. Auto-detect: only apply Markdown if text contains `*`, `_`, or backtick. Fixed in gateway.

2. **Docker heredoc** — `docker exec container psql << 'EOSQL'` doesn't pipe stdin. Always use `docker cp file container:/tmp/file.sql && docker exec container psql -f /tmp/file.sql`.

3. **Graph API `._request()` returns `(data, error)` not `(status_code, data)`** — Always unpack as `data, err = mg._request(...)`. Don't assume status code is first.

4. **Message IDs with special chars** — Always `urllib.parse.quote(msg_id, safe='')` before using in Graph API URLs.

5. **`_pg()` not `_db()`** — The gateway DB function is `_pg()`. Never write `_db()`.

6. **`platform_events` columns** — Schema uses `payload` (jsonb) and `published_at`. Not `event_data`/`created_at`.

7. **`_log()` needs 6 args** — `_log(path, source, upstream, status, ms, request_id)`. Never call with fewer.

8. **AppleScript file moves** — Can't do heredoc AppleScript moves. Use `subprocess.run(["osascript", "-e", script])` per file with `(POSIX file path) as alias` destination.

9. **Mexamer = CLIENT not vendor** — Mexamer Garmisch LLC is the owner/client on 655 Garmisch. Not a steel subcontractor. Don't confuse.

10. **Bid expiry tracking** — Bids expire. Clemmer Welding expired ~6/30. Aspen Welding expires 7/2. Track dates, flag early. Build BTW-4 to automate this.

---

## BTW BUILD BACKLOG — EXECUTE IN ORDER

| # | Item | What | Why |
|---|------|------|-----|
| ~~BTW-4~~ | ~~Bid stale-detection~~ | **DONE 2026-06-30** — GET /gateway/bids/stale + daily alert; Aspen Welding expiry tracked |
| ~~BTW-8~~ | ~~Vendor scoring~~ | **DONE 2026-06-30** — 31 vendors scored A-D; GET /gateway/vendors/scores |
| ~~BTW-6~~ | ~~246GW budget + Drive~~ | **DONE 2026-06-30** — GET /gateway/project/246GW/budget; OVER_BUDGET flag sent Buck |
| **BTW-5** | Schedule variance alerts | Flag when schedule drifts — 101F already showing variance | **NEXT** |
| **BTW-7** | Houzz → DB auto-sync | Replace manual BC extraction with scheduled pull | After BTW-5 |
| **BTW-9** | Executive dashboard v2 | Visual KPI board — mission control is API-only now | After BTW-7 |
| **BTW-10** | Bid leveling engine | Side-by-side comparison + award recommendation | After BTW-9 |

---

## HOW GBT + BC COLLABORATE

### The loop:
1. **BC extracts** → saves `.md` to Downloads → sends handoff to Claude Code via `/gateway/agent/handoff`
2. **Claude Code loads** → DB updated, code changed, file written
3. **GBT reads** → pulls system state via gateway, analyzes, writes next directive
4. **GBT sends handoff** → Claude Code executes build task
5. **Repeat**

### Double-check rule:
- GBT: before sending a handoff to Claude Code, ask BC to confirm the data is current and complete
- BC: after extracting Houzz data, flag any anomalies to GBT before Claude Code loads it
- Claude Code: after any DB load, run a quick row count and report back via handoff response

### When you disagree:
- State the disagreement clearly in a handoff note
- Default to the more conservative option
- Flag to Buck only if it affects a live project commitment

---

## HARD RULES — NEVER BREAK

1. No email sends without Buck's explicit approval
2. No HubSpot writes — read only, propose changes, message Buck
3. No contract awards or budget commitments
4. No deleting files or DB records
5. Only write to live projects: 64EW, 101F, 1355R, 246GW — all others are reference only
6. Telegram to Buck: max 1 message per topic per day unless urgent
7. Always identify: start Telegram messages with `GBT:` or `BC:`
8. Every completed BTW: run the 14-step DoD, then auto-continue to the next

---

## WHEN BUCK COMES BACK

He'll message @hciaiossystem_bot. On receipt:
- GBT sends a brief status: what was completed, what's pending, what needs his decision
- BC sends any new Houzz extracts that need loading
- Keep it under 5 bullet points — Buck reads fast, doesn't need the essay

---

*Committed to main. Last updated: 2026-06-30 by Claude Code.*

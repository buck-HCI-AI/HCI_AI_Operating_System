# Chapter 02 — Daily Operations: Morning Routine
**HCI AI Operations Manual | Part I — Business Operations**
*Authority: Buck Adams | Last Updated: 2026-06-30*

---

## 2.1 Overview

Every HCI workday starts the same way: the system runs its overnight checks, generates a morning brief, and delivers a prioritized action list. The morning routine is designed so that within 15 minutes, Buck and the field team know exactly what needs to happen today across all four projects.

**Morning brief delivery: 7:00am weekdays**
- Telegram notification to Buck's phone
- Stale bid check completed (7:00am n8n trigger)
- Schedule variance scan completed (7:00am n8n trigger)

---

## 2.2 Buck's Morning Sequence (15 minutes)

### Step 1 — Telegram Check (2 min)
Open @hciaiossystem_bot. Look for:
- 🚨 CRITICAL alerts — act on these immediately
- ⚠️ Budget or schedule flags from overnight scans
- Any messages from GBT or BC while you were sleeping

If there are no alerts, the system is healthy. Move to Step 2.

### Step 2 — Executive Dashboard (3 min)
```
GET /gateway/executive/mission-control
```
This returns:
- Portfolio health (GREEN / YELLOW / RED per project)
- Count of decisions pending in approval queue
- Active AI missions status

If all four projects are GREEN and the approval queue is empty: today is routine.
If any project is RED: jump to that project's PM console immediately.

### Step 3 — Approval Queue (5 min)
```
GET /gateway/executive/report
```
Review any items awaiting your decision:
- Bid awards pending your approval
- Budget commitments that need sign-off
- Client-facing communications ready for your review

Approve, reject, or defer each. The system handles the rest.

### Step 4 — Project Flags (5 min)
Check any project showing YELLOW or RED:
```
GET /gateway/project/1355R/pm   ← always check 1355R first (highest risk)
GET /gateway/project/101F/pm
GET /gateway/project/64EW/pm
GET /gateway/project/246GW/budget
```

---

## 2.3 Field Team Morning Sequence

The superintendent and site team have a simplified morning view designed for the field — no dashboards, no API calls. Just the information they need.

**Superintendent daily check-in:**
1. Log into Houzz Pro → review today's schedule items
2. Check any open RFIs that need responses before crew arrives
3. Flag any delivery issues or subcontractor no-shows in Houzz (BC will capture this)
4. Text Buck directly if there's a site emergency — the AI system supplements, never replaces, direct communication in a crisis

**Office daily check-in:**
1. Review any vendor emails that came in overnight for bids
2. Log received bids in HubSpot (or notify GBT to update the system)
3. Check Outlook for any client communications requiring a response
4. Flag anything needing Buck's attention before noon

---

## 2.4 Weekly Rhythm

| Day | Extra Activity |
|-----|---------------|
| Monday | GBT sends weekly project digest to Buck via Telegram |
| Tuesday | Best day for bid leveling sessions — subs have had the weekend to respond |
| Wednesday | Mid-week health check — any bids going stale this week? |
| Thursday | Review award queue — any subs with expiring bids before Friday? |
| Friday | Week-close: confirm all active bids are in system, no stale items |

---

## 2.5 The Bid Stale Alert System

Every weekday at 7:00am, the system runs a stale bid check. If anything needs attention, Buck gets a Telegram alert before he reads anything else.

**What triggers an alert:**
- A bid expiring within 3 days (EXPIRING SOON)
- A bid that has already expired and hasn't been received (EXPIRED)
- A bid sent more than 7 days ago with no response (NO RESPONSE WARNING)
- A bid sent more than 14 days ago with no response (NO RESPONSE ALERT)

**What to do when you get an alert:**
1. Open the alert — it tells you the vendor, project, and expiry date
2. Call or email the vendor directly — the AI does not make outbound calls
3. If they're extending their bid: update the expiry date in the system
4. If they're not bidding: mark them inactive and find a replacement sub

**Current watch item (2026-06-30):**
Aspen Welding LLC — 1355 Riverside structural steel SOW — bid expires 2026-07-02. Call before then or the bid is void.

---

## 2.6 The Schedule Variance Alert

Every weekday at 7:00am, the system scans all schedule items across live projects and flags anything overdue.

**Current status (2026-06-30):**
101 Francis — 74 items overdue, 55-71 days past end dates, all NOT_STARTED.
These are Houzz schedule items entered before the project started. When you're ready to begin construction at 101F, review and update these dates in Houzz. BC will capture the updated schedule automatically.

**What "overdue" means:**
A schedule item is overdue if its end_date has passed and its status is not "Complete" or "Done." This includes tasks that may have been completed but not marked done in Houzz. Always check Houzz first before treating an item as truly overdue.

---

## 2.7 End-of-Day Close

At 7:00pm, the system runs an end-of-day brief. No action required unless Buck sees a red flag.

**EOD brief includes:**
- Summary of what changed today (bids received, status updates)
- Any items due tomorrow that aren't started
- Approval queue count

**Field close-out (superintendent):**
- Log daily progress in Houzz daily log (this is captured by BC overnight)
- Note any RFIs, submittals, or issues that came up today
- Confirm tomorrow's subs are scheduled and confirmed

---

## 2.8 When the System is Down

If Telegram alerts stop arriving, the gateway is unreachable, or the dashboard won't load:

1. Check ngrok: `curl https://speculate-armband-retinal.ngrok-free.dev/gateway/health`
2. If no response: restart ngrok — `ngrok http 8000` in Terminal
3. If still down: check Docker — `docker ps` — ensure hci_postgres and other containers are running
4. Full restart procedure: see Chapter 26 — Emergency Procedures

**Never wait for the AI system if a field emergency occurs.** Call Buck directly. The AI augments operations; it does not replace direct communication when lives or project integrity are at risk.

---

*Next: Chapter 03 — Field Operations*

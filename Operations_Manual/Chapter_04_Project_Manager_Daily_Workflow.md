# Chapter 04 — Project Manager Daily Workflow
**HCI AI Operations Manual | Part I — Business Operations**
*Authority: Buck Adams | Last Updated: 2026-06-30*

---

## 4.1 Overview

The project manager is the operational center of each project — running the schedule, tracking bids, communicating with the design team, keeping the client informed, and managing change. At HCI, the AI system handles the monitoring and alerting; the PM handles judgment and relationships.

This chapter covers the PM's daily workflow for managing one or more active projects using the HCI AI Operating System.

---

## 4.2 PM Project Console

Every project has a PM console in the gateway. This is the starting point for project management every morning:

```
GET /gateway/project/{code}/pm
```
Replace `{code}` with: `64EW`, `101F`, `1355R`

**What the PM console returns:**
- Project health status (GREEN / YELLOW / RED)
- Bid package summary (total, awarded, receiving, not started)
- Open risks and issues
- Recent activity (last 72 hours of changes)
- Upcoming milestones (next 14 days)

**246GW is budget-managed differently:**
```
GET /gateway/project/246GW/budget
```
This project is in construction — the primary watch is budget vs. contract, not bid status.

---

## 4.3 Bid Package Management

**The bid package lifecycle:**
1. `NOT_STARTED` — identified but invite not yet sent
2. `COLLECTING` — SOW sent, waiting for responses
3. `RECEIVED` — at least one bid received, ready for leveling
4. `LEVELED` — bids compared side-by-side, award recommendation ready
5. `AWARDED` — Buck approved the award, contract executed
6. `CANCELLED` — scope removed or combined with another package

**PM daily bid tasks:**
1. Check which packages expire in the next 3 days — call those subs before morning is over
2. Review any newly received bids — log them in the system same day
3. Check no-response list — any subs who got the SOW 7+ days ago with no reply?
4. If a package has 3+ received bids, prepare the leveling comparison for Buck

**Updating bid status:**
```
POST /gateway/bids/update
X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6
{
  "bid_id": [id],
  "status": "received",
  "bid_amount": 125000,
  "received_date": "2026-06-30"
}
```

---

## 4.4 Vendor Communication Workflow

**The PM manages all sub communication at the bid stage:**

**Sending an SOW:**
- SOW drafts are prepared by GBT and routed to Outlook
- PM reviews the draft, adds any project-specific notes
- Buck approves all SOW sends — PM routes for approval first
- Once approved: send from Outlook via Graph API or directly in Outlook

**Following up on a stale bid:**
1. The 7am alert tells you who to call
2. Call directly — do not email for expiring bids, you'll lose a day
3. Log the call outcome in the system same day
4. If extending: update expiry date in the DB

**Marking a sub inactive:**
If a sub hasn't responded after 2 follow-up attempts, mark them `inactive` for this package:
```
POST /gateway/bids/update
{"bid_id": [id], "status": "no_response", "notes": "2 calls, no reply"}
```
Then identify a backup sub and send them the SOW.

---

## 4.5 Schedule Management

**The PM owns the project schedule. Houzz is the schedule system of record.**

**Weekly schedule review:**
1. Open Houzz Pro → project → Schedule
2. Identify any tasks overdue that should be marked complete
3. Identify any tasks starting in the next 2 weeks — are the subs confirmed?
4. Flag any milestone dates at risk to Buck

**When a task falls behind:**
1. Log it in the Houzz daily note for the day you discover it
2. Assess downstream impact — what else moves if this pushes?
3. Notify the affected subs in the new sequence
4. Update the Houzz schedule — BC will capture the new dates automatically
5. If the delay pushes the contract completion date: flag to Buck for client notification

**101 Francis schedule note:**
74 items currently show overdue in the system, but 101F is in pre-construction. These dates were entered during planning. When construction begins, update all dates in Houzz. The system will recalibrate automatically.

---

## 4.6 Budget Tracking

**By project phase:**

*Pre-construction (64EW, 101F, 1355R):*
Budget tracking is about bid coverage. The PM tracks:
- How many packages are still open (not awarded)
- Sum of received bids vs. budget estimate per package
- Any packages where the lowest bid exceeds the budget estimate (flag to Buck)

*Construction (246GW):*
Budget tracking is critical. The PM tracks:
- Contract value vs. committed costs (awarded)
- Remaining open estimates for unawarded packages
- Change order totals (increases to budget)
- Current projection: `GET /gateway/project/246GW/budget`

**246GW alert (2026-06-30):**
Current committed: $6,314,913 vs. contract $6,300,000 — over by $14,913. Open estimates add $2.75M more. This project needs value engineering or a contract amendment. Flag to Buck before awarding any more packages without budget relief.

---

## 4.7 Design Team Coordination

**The design team (architects, engineers, interior designers) is managed through Outlook.**

**PM tracking list — live at all times:**
- Open RFIs (sent, awaiting response)
- Pending submittals (shop drawings, product data, samples)
- Issued for construction drawings vs. what's in the field

**RFI status check:**
- Every open RFI gets a follow-up call if no response in 3 business days
- RFI responses are forwarded to the superintendent same day they're received
- If an RFI is blocking work on site: escalate immediately — call the designer directly

**Current open items:**
- 1355R RFI-001: Axis B Beam Pocket — sent to Michael@aliusdc.com, no response yet
- 1355R: Awaiting structural engineer review before steel package can be finalized

---

## 4.8 Client Communication

**Client communication is the PM's most important relationship task and the most heavily governed by HCI policy.**

**The rule:**
Every client-facing communication is reviewed and approved by Buck before it is sent. No exceptions.

**Standard client update cadence:**
- Weekly: Brief progress summary email (what happened this week, what's next week, any items needing client decision)
- As-needed: Any change that affects the project schedule, budget, or design intent

**PM prepares the update draft. Buck approves before sending.**

Draft format:
```
Subject: [Project Address] — Weekly Update [Date]

Hi [Client First Name],

This week we completed: [2-3 specific items]

Next week we plan to: [2-3 specific items]

Items awaiting your decision: [if any]

Questions or concerns? Reply here or call [Buck's number].

Buck Adams
Hendrickson Construction
```

**Never communicate:**
- Budget numbers without Buck's approval
- Schedule changes that imply delay without Buck's approval
- Change order implications without Buck's approval
- Anything about disputes, subcontractor problems, or design issues without Buck's approval

---

## 4.9 Meeting and Decision Log

Every meeting that affects the project is logged. This is the PM's responsibility.

**Meeting log minimum:**
- Date, attendees, meeting type (OAC, design review, pre-construction)
- Decisions made (specific — "Owner approved change to cabinet hardware per submittal #12")
- Action items assigned (who, what, by when)
- Next meeting scheduled

Meeting logs are saved to the project Drive folder and referenced in the system.

---

*Next: Chapter 05 — Bid Package Management*

# Chapter 03 — Field Operations
**HCI AI Operations Manual | Part I — Business Operations**
*Authority: Buck Adams | Last Updated: 2026-06-30*

---

## 3.1 Overview

Field operations are the daily rhythm of the construction site — subcontractors arriving, materials being delivered, work being inspected, problems being identified and resolved. The HCI AI system supports field operations without getting in the way of the work.

The superintendent runs the site. The AI system captures what happens, surfaces risks, and keeps the office and ownership informed without requiring the field team to manage software.

---

## 3.2 The Superintendent's Role in the System

The superintendent's only system touchpoint is **Houzz Pro**. That's it.

**What the superintendent does in Houzz:**
- Logs daily progress notes in the daily log
- Marks schedule items complete when work is done
- Documents issues (weather delays, material shortfalls, subcontractor problems)
- Takes and uploads site photos

**What happens automatically:**
- BC (Browser Claude) reads Houzz daily and extracts all entries
- Data is loaded into the HCI database overnight
- GBT analyzes changes and flags risks
- Buck gets the summary in his morning brief

**The superintendent does not need to:**
- Log into the HCI gateway or dashboard
- Manage bids or vendors in the system
- Track budgets or approvals
- Use any tool other than Houzz Pro

---

## 3.3 Daily Log Standards

A good daily log entry takes 5 minutes and prevents 50 minutes of phone calls. Every entry should include:

**Minimum required fields:**
- Date and weather conditions
- Crews on site (which subs, how many people)
- Work completed today (specific — "poured east foundation wall, 45 cy concrete" not "concrete work")
- Materials received (what, quantity, any damage or shortages)
- Issues or delays (be specific — "Ajax Electric no-show, no advance notice, 3-hour delay to electrical rough")
- Tomorrow's plan

**What makes a log entry useful:**
```
2026-06-30 — Partly cloudy, 68°F
On site: TJ Concrete (6), Premier Landworks (3)
Work: East wall pour complete, 47cy. West wall forms set for tomorrow.
Received: Keller drilled pier cage reinforcement — all 22 pieces, no damage.
Issues: Premier running 1 day behind on site utilities — backfill not complete.
         Rescheduled concrete flatwork for 7/3 per Buck approval.
Tomorrow: West wall pour (weather permitting), continue site utility backfill.
```

---

## 3.4 RFI Workflow in the Field

When the field identifies something that doesn't match the plans:

**Step 1 — Field identifies the issue**
Superintendent notes the discrepancy in the Houzz daily log. Include exact location, what the plans say vs. what's found, and what needs to be clarified before work can proceed.

**Step 2 — Office generates RFI**
Office team or GBT drafts the RFI based on the daily log entry. RFI number format: `[PROJECT]-RFI-[###]` (e.g., 1355R-RFI-001).

**Step 3 — RFI is submitted**
Sent to the design team (architect, structural engineer, MEP) via Outlook. Saved to the project Drive folder. Status tracked in the system.

**Step 4 — Response received**
When the design team responds, the response is logged in the system. If work was stopped pending the response, field is notified immediately.

**Current open RFI:**
1355R-RFI-001: Axis B Beam Pocket — structural engineer review pending. Sent to Michael@aliusdc.com. Do not proceed with that beam pocket until response is received.

---

## 3.5 Delivery and Material Management

All material deliveries should be logged in Houzz on the day they arrive. This triggers:
- BC to capture delivery confirmation
- Inventory to be updated in the project record
- Any shortages or damage to be flagged for follow-up

**Delivery protocol:**
1. Inspect delivery before the driver leaves
2. Document any damage or shortage in the delivery receipt and Houzz
3. Notify the supplier immediately if there's an issue — same day
4. Never sign a delivery receipt "subject to inspection" — inspect first

**Lead time awareness:**
The system tracks which packages are still bidding. If you need a material that hasn't been awarded, flag it in Houzz immediately. Lead times at the Aspen elevation and access can add 2–4 weeks vs. front-range delivery.

---

## 3.6 Subcontractor Management on Site

**Before subs arrive:**
- Confirm pre-task meeting if they're starting a new scope
- Verify current COI (Certificate of Insurance) is on file
- Confirm they have the current drawings and any issued RFI responses

**While subs are on site:**
- Log their crew size in the daily log
- Document any work stoppages or issues
- Flag any scope creep — if a sub is doing work outside their contract, stop it and call Buck

**When subs leave:**
- Confirm the area is clean and protected per the spec
- Note completion percentage in the Houzz daily log
- If they won't return for more than 3 days, note the reason

---

## 3.7 Weather and Delay Management

**Weather delay protocol:**
1. Log weather conditions and work stoppage in Houzz daily log
2. Assess impact on schedule — will this push other subs?
3. Notify affected subs immediately so they can plan
4. If delay is 3+ days: GBT to update schedule and notify Buck of downstream impact

**The system tracks:**
- Consecutive weather delays per project
- Schedule impact of delays (days lost vs. float remaining)
- Pattern alerts (if a project is falling behind a benchmark pace)

**Weather does not automatically excuse contract delays.** The contract governs what constitutes an excusable delay. When in doubt, document everything and contact Buck before telling a sub they get extra time.

---

## 3.8 Safety and Incidents

**Any site incident — no matter how minor — is logged same day.**

Incident log in Houzz includes:
- Date, time, exact location on site
- Who was involved (name, employer, role)
- What happened (factual, no speculation)
- Any medical attention provided
- Who was notified and when

**For any recordable incident (OSHA definition):**
1. Call Buck immediately
2. Secure the area
3. Cooperate with any required agency notification
4. Do not post about the incident on social media or share photos publicly
5. Preserve all evidence until told otherwise by Buck or legal counsel

The HCI AI system does not manage incident reporting — that is a legal and human matter. The system's daily log captures context, but formal incident reporting follows HCI's safety policies, not the AI system.

---

## 3.9 Field Communication with the Office

**Use Houzz for:** Everything that is part of the permanent project record.
**Use text/call for:** Urgent issues that need same-day response.
**Use email for:** Formal communications with design team, clients, or agencies.

The AI system reads Houzz. It does not read texts or phone calls. If something matters to the project record, it goes in Houzz.

---

*Next: Chapter 04 — Project Manager Daily Workflow*

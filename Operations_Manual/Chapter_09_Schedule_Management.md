# Chapter 09 — Schedule Management
**HCI AI Operations Manual | Part I — Business Operations**
*Authority: Buck Adams | Last Updated: 2026-06-30*

---

## 9.1 Overview

Schedule is everything in luxury custom construction. A client who expects to be in their home by Thanksgiving does not want to hear about delays in July. Schedule management means anticipating problems before they become missed dates.

The HCI AI system monitors schedule variance daily. The PM's job is to act on what the system flags.

---

## 9.2 The Schedule System

**Houzz Pro is the schedule system of record.** All schedule items are entered in Houzz. The HCI AI system reads from Houzz via BC (Browser Claude) daily and stores the data in the `project_schedule_items` table.

**GBT and Claude Code can read the schedule data:**
```
GET /gateway/schedule/variance
```
Returns:
- Overdue items per project (status = NOT_STARTED or IN_PROGRESS, end_date past)
- Days overdue per item
- Project-level overdue count and max days variance

**Current schedule status (2026-06-30):**
- 101 Francis: 74 items overdue, 55-71 days past end dates, all NOT_STARTED
  *(Note: these are pre-construction template dates — update when construction starts)*
- 64EW: No schedule data loaded yet
- 1355R: No schedule data loaded yet
- 246GW: In construction — schedule being tracked via Houzz daily

---

## 9.3 Schedule Tiers

HCI uses three levels of schedule for each project:

**Level 1 — Milestone Schedule (Summary)**
Key dates only: NTP (Notice to Proceed), Framing complete, Dry-in, MEP rough-in complete, Framing inspection, Drywall complete, Substantial completion, Final completion.
- One page, suitable for the owner and design team
- Updated monthly or when milestones are affected by changes

**Level 2 — Construction Schedule (Working)**
All major activities with dependencies, durations, and sub names. The PM works from this schedule.
- Maintained in Houzz
- Updated weekly during active construction
- 3-week lookahead generated every Monday

**Level 3 — 3-Week Lookahead**
Detailed task list for the next 21 days. Who is on site when, doing what, with what materials.
- Prepared by PM every Monday
- Shared with all subs in the upcoming 3-week window
- BC extracts from Houzz; GBT formats and distributes via Telegram to Buck

---

## 9.4 Schedule Variance Alert

Every weekday at 7am, the system checks for schedule variance and sends a Telegram alert if thresholds are exceeded.

**Alert thresholds:**
```
GET /gateway/schedule/variance
POST /gateway/schedule/variance/alert  ← triggers manual check + Telegram send
```

**Alert contents:**
- Project name
- Number of overdue items
- Maximum days overdue
- Top 5 most overdue items

**When you get a schedule alert:**
1. Check Houzz — are these items actually incomplete or just not marked done?
2. If actually incomplete: assess impact on downstream activities
3. Identify recovery options: Can the sub accelerate? Can activities be resequenced?
4. If schedule impact exceeds 5 days on the milestone: notify Buck immediately
5. Update Houzz schedule to reflect revised dates

---

## 9.5 Pre-Construction Schedule (101F, 1355R, 64EW)

For projects not yet in construction, the schedule focus is on **procurement sequencing**.

**Procurement schedule:**
Not everything needs to be awarded before construction starts. But some things have lead times that will dictate the project start:
- Structural steel: 8-14 weeks from award to delivery
- Windows and doors (Pella, etc.): 10-16 weeks
- Elevator: 16-24 weeks
- Custom millwork: 12-18 weeks
- Specialty mechanical equipment: 8-12 weeks

**The rule:**
Work backwards from the construction schedule. For any scope with a lead time > 6 weeks, award before you need them. If awards are delayed, lead time delivery gets pushed and construction cannot start on schedule.

**Critical path for 1355R:**
1. Structural steel (8-14 week lead) → Award Aspen Welding or Pinnacle by 7/5
2. Foundation/concrete (4-6 week lead) → Award TJ or High Con by 7/12
3. Windows/doors → Pella SOW not yet sent — prepare by 7/10

---

## 9.6 Schedule Float and Critical Path

**Float:** The amount of delay a task can absorb before it pushes the project completion date.

**Critical path:** The sequence of tasks with zero float. Any delay on the critical path delays the project.

**PM responsibility:**
- Know what's on the critical path at all times
- Alert Buck the moment a critical path activity is threatened
- Never let the critical path surprise the client

**At 246GW (in construction):**
GBT to prepare a critical path analysis from current Houzz schedule data. Flag any critical path items currently at risk.

---

## 9.7 Subcontractor Schedule Compliance

**Every subcontract includes milestone dates for their scope.** Non-compliance is a contract breach.

**PM tracking:**
- Every active sub has a "scheduled start" and "scheduled completion" in the project schedule
- 2 weeks before a sub's scheduled start: confirm they're mobilizing as planned
- 1 week before: confirm their crew size and any material pre-orders
- Day of: confirm they showed up

**When a sub is falling behind:**
See Chapter 06, Section 6.8 — the formal notice and escalation process. Document first, then talk.

**Acceleration:**
If a sub needs to accelerate to make up lost time:
- This is additional cost — they will request a Change Order for overtime/acceleration
- Buck must authorize any acceleration cost before directing the sub to accelerate
- Do not verbally promise a sub that you'll pay for acceleration without Buck's sign-off

---

## 9.8 Owner Schedule Communication

**Owners are entitled to know when their project is running behind schedule.**

**The rule:** No schedule change that affects the contract completion date goes to the owner without Buck's prior review.

**How to tell an owner about a delay:**
1. Acknowledge the delay and its cause
2. Explain what HCI has done to mitigate
3. State the new expected completion date with specificity
4. Describe what's being done to prevent further slippage
5. Do not assign blame to specific subs by name in written client communications

**What not to say:**
- "The subs are behind" (blame shifting without solution)
- "It depends on the weather" (vague non-answer)
- "We'll see" (owner hears: they don't know)

Every delay communication should end with a specific action and a specific date. Owners can handle bad news. They can't handle vague uncertainty.

---

## 9.9 Pitkin County Inspection Sequence

Every HCI project in Pitkin County must comply with the required inspection sequence. The schedule must accommodate Pitkin County's inspection lead times.

**Critical inspections and typical lead times:**
- Foundation inspection: 24-48 hours notice
- Framing inspection: 2-3 business days notice
- MEP rough-in inspection: 2-3 business days notice (mechanical, electrical, plumbing)
- Insulation inspection: 24-48 hours notice
- Fire suppression inspection (if applicable): 3 business days notice, Fire District separate
- Final inspection: 3-5 business days notice

**The rule:**
Schedule inspections before you close in. Never drywall before passing rough-in inspections. Work with the superintendent to schedule inspections before the sub leaves the project, not after.

**COC (Certificate of Occupancy):**
Final CO is issued by Pitkin County after all inspections pass and all conditions of the permit are met. Target CO date is the project completion milestone. The PM tracks all outstanding permit conditions.

---

*Next: Chapter 10 — Risk Management*

# Chapter 06 — Vendor and Subcontractor Management
**HCI AI Operations Manual | Part I — Business Operations**
*Authority: Buck Adams | Last Updated: 2026-06-30*

---

## 6.1 Overview

HCI's subcontractor relationships are a core competitive advantage. In the Aspen market, the best subs have choices — they can work for anyone. The contractors they choose to work with consistently are the ones who treat them fairly, pay on time, communicate clearly, and run organized projects.

The HCI AI system manages the data layer. The relationships are human.

---

## 6.2 The Vendor Database

**392 vendors** are currently tracked in the HCI system across 50+ trades.

**Key vendor data points:**
- Contact information (name, company, email, phone)
- Trades and CSI divisions
- Vendor score (A/B/C/D based on response, coverage, and history)
- Project history (what they've bid, what they've won, what they've built)
- Insurance status (COI expiry)
- Notes (performance observations, blacklist flags)

**Querying vendor data:**
```
GET /gateway/knowledge/vendor?name=Aspen+Welding
GET /gateway/knowledge/vendor?trade=structural_steel
GET /gateway/vendors/scores              ← all vendors ranked
GET /gateway/vendors/scores/{vendor_id} ← single vendor detail
```

**Updating vendor data:**
Route to GBT with the correction. GBT prepares the update, Claude Code executes. No direct vendor data writes from the field.

---

## 6.3 Vendor Categories at HCI

HCI works with three categories of vendors:

**Tier 1 — Strategic Partners**
Subs HCI has worked with multiple times, who understand the Aspen luxury standard, who we prioritize in bid invitations. These relationships are personal. Buck knows their owners by name.
- American PHCE (HVAC/plumbing)
- Keller Foundations (foundation/piers)
- TJ Concrete
- Ajax Electric
Examples — not exhaustive.

**Tier 2 — Qualified Regulars**
Subs in the database with at least one successful project or strong referral. Invited to bid when Tier 1 has capacity conflicts.

**Tier 3 — New/Unproven**
First-time bidders or referrals without project history at HCI. Always invited alongside at least two Tier 1 or Tier 2 subs. Never sole-source awarded without explicit Buck approval.

---

## 6.4 Adding a New Vendor

When a new sub is referred or introduces themselves:

**Information to collect:**
- Company name, contact name, role
- Email (required for SOW routing), phone
- Trades and CSI divisions they cover
- License number (Colorado contractor license)
- Insurance: liability limit, workers comp, additional insured language
- References (2 GC references for subs doing work >$50K)

**Adding to the system:**
Route to GBT: "Add new vendor: [all info above]." GBT prepares the database insert, Claude Code executes.

**Do not send an SOW before:**
1. Vendor is in the system
2. Current COI is on file or committed
3. References have been checked for contracts over $100K

---

## 6.5 Insurance Requirements

**Every sub working on an HCI project must have a current COI on file before they start work.**

**Minimum insurance requirements:**
- Commercial General Liability: $1,000,000 per occurrence / $2,000,000 aggregate
- Workers Compensation: State statutory limits
- Auto Liability: $1,000,000 combined single limit
- Additional Insured: "Hendrickson Construction, its officers, directors, employees, and agents"

**For subs with contract value over $500K:**
- Umbrella/Excess: $5,000,000 minimum

**COI tracking:**
The system flags subs with expiring COIs. If a sub's COI expires during active work, work stops until the new certificate is on file. No exceptions.

**COI status check:**
```
GET /gateway/knowledge/vendor?name=[sub+name]
```
Check `coi_expiry` field.

---

## 6.6 Sub Pre-Construction Meeting

Before any sub begins work, a pre-construction meeting is held. This is not optional.

**Meeting agenda:**
1. Project overview — client expectations, schedule overview, what success looks like
2. Their specific scope — confirm they understand exactly what they are and aren't doing
3. Coordination requirements — who do they need to coordinate with? (trades above/below/adjacent)
4. Logistics — site access, staging area, material storage, working hours
5. Submittal requirements — what shop drawings, product data, samples need approval before ordering
6. Payment process — payment application cutoff (25th of month), review period, pay date
7. Communication protocol — who is their HCI contact? How do they get RFI responses? What's the response commitment?
8. Quality expectations — mock-up requirements, inspection points, Pitkin County inspection schedule

**Who attends:**
- HCI PM + Buck (for major subs)
- Sub's project manager or foreman
- Superintendent if work begins within 30 days

**Meeting is logged** in the system and the project Drive folder.

---

## 6.7 Vendor Performance Tracking

The vendor scoring system runs on three dimensions:

**Response (0-40 points)**
- Did they respond to the SOW?
- How quickly?
- Was the bid complete?

**Coverage (0-30 points)**
- What percentage of the scope did they price?
- Did they exclude critical items?
- Were exclusions reasonable and disclosed?

**History (0-30 points)**
- Have they built HCI projects before?
- How did they perform? (quality, schedule, communication)
- Would we award them again?

**Grades:**
- A (80-100): Preferred — invite first
- B (60-79): Regular — standard invite list
- C (40-59): Conditional — invite if limited options
- D (<40): Do not invite — document reason

**Updating performance:**
After a project phase, or after a notable performance event (good or bad), PM logs a note. GBT updates the score. System records the history.

---

## 6.8 Managing Sub Performance During Construction

**When a sub is underperforming:**

**Step 1 — Document**
Every underperformance event is logged in Houzz daily log before any conversation happens. Date, what was observed, what was not delivered, impact on schedule.

**Step 2 — Conversation**
PM speaks with the sub's superintendent or PM directly. "You're behind X days on Y scope. What's the plan to recover?" Get a specific answer with dates.

**Step 3 — Written notice**
If they're behind by more than 3 days without a credible recovery plan: written notice. GBT prepares the notice, Buck approves, PM sends via Outlook.

**Step 4 — Escalation**
If notice doesn't resolve it: contact the sub's owner. This is Buck's call, not PM's. Flag to Buck.

**Step 5 — Contract remedies**
If the sub abandons the work or cannot recover: this is a legal matter. Contact Buck immediately. The contract governs remedies — don't make promises or threats without Buck's explicit approval.

---

## 6.9 Sub Payment Management

**Payment drives performance.** Pay on time, pay what you owe, and subs will work for you again.

**Payment application cycle:**
- Sub submits Pay App by the 25th of the month
- PM reviews against schedule of values and work in place by the 27th
- Buck approves by the 28th
- Payment issued by the 5th of the following month

**What to check in a Pay App review:**
1. Does the amount requested match work in place?
2. Are lien waivers (conditional and unconditional) attached?
3. Are all lower-tier subs paid (joint check or waiver documentation)?
4. Are there unapproved change orders embedded in the application?

**If any of those are no:** Hold the item, notify the sub, explain what's needed to release payment.

**Never withhold payment without a documented, legitimate reason.** Arbitrary payment holds damage relationships and expose HCI to legal risk.

---

*Next: Chapter 07 — Contract Management*

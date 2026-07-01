# Chapter 05 — Bid Package Management
**HCI AI Operations Manual | Part I — Business Operations**
*Authority: Buck Adams | Last Updated: 2026-06-30*

---

## 5.1 Overview

Bid package management is the engine of HCI's pre-construction operations. Every dollar of budget and every trade on the project flows through this process. Getting it right means better subs, better prices, and projects that close on budget.

This chapter covers the full lifecycle of a bid package — from identification through award — using the HCI AI Operating System.

---

## 5.2 Current Bid Portfolio

**As of 2026-06-30:**

| Project | Total Pkgs | Awarded | Collecting | Not Started |
|---------|-----------|---------|-----------|-------------|
| 64EW | 35 | 0 | 35 | 0 |
| 101F | 41 | 0 | 26 | 15 |
| 1355R | 73 | 0 | 58 | 15 |
| 246GW | 44 | 19 | 18 | 7 |
| **Total** | **193** | **19** | **137** | **37** |

137 active bid packages across 3 projects. This is the primary work front right now.

---

## 5.3 Package Identification and Setup

**Step 1 — Define the scope**
Each bid package has a defined scope of work. The scope should be clear enough that two different subs read it and price the same thing.

Scope definition includes:
- CSI division and trade description
- Specific inclusions (what is in this package)
- Specific exclusions (what is NOT in this package — allowances, owner-furnished items)
- Drawing references (sheet numbers that govern this scope)
- Specification sections
- Key project constraints (access, staging, Pitkin County requirements)

**Step 2 — Create in the system**
```
POST /gateway/bids/create
X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6
{
  "project_id": [id],
  "package_name": "Structural Steel Erection",
  "csi_division": "05",
  "status": "not_started",
  "budget_estimate": 285000
}
```

**Step 3 — Identify subs**
Use the vendor database to find qualified subs for this trade:
```
GET /gateway/knowledge/vendor?trade=structural_steel
```
Review vendor scores to prioritize who to invite:
```
GET /gateway/vendors/scores
```
A-grade vendors get first invite. C-grade or lower: only invite if no better options exist.

---

## 5.4 SOW Preparation

**The Statement of Work (SOW) is the bid invitation document.**

**SOW structure:**
1. Project overview (address, owner, scope summary)
2. Specific scope of work for this package
3. Bid submission requirements (format, due date, what to include)
4. Drawing and specification references
5. Site logistics and constraints (staging, access, working hours per Pitkin County regs)
6. Insurance requirements (see COI requirements in Chapter 12)
7. Preliminary schedule (not binding, but shows context)

**SOW preparation:**
GBT prepares SOW drafts based on the scope definition. Claude Code saves drafts to Outlook. Buck reviews and approves before sending.

**The no-send rule:**
No SOW is sent without Buck's explicit approval. GBT prepares, PM reviews, Buck approves. After approval: send via Outlook (directly or via Graph API).

**SOW tracking:**
Once sent, the bid package status updates to `COLLECTING` and the sent date is logged. This starts the expiry clock.

---

## 5.5 Bid Expiry Management

**The bid validity window is the most time-sensitive operational task in pre-construction.**

**How expiry works:**
- Most HCI SOWs request a 30-day bid validity period
- After the due date passes, the bid expires — the sub can change their number
- If a sub's bid expires and they haven't been awarded, they will often re-bid higher
- Expiring bids need immediate action: award, extend, or replace

**The stale bid check runs every weekday at 7am:**
```
GET /gateway/bids/stale
```
Returns four categories:
- `EXPIRING` — expires within 3 days → call today
- `EXPIRED` — already expired → call and get an extension or replacement
- `NO_RESPONSE` — SOW sent 7+ days ago, no reply → follow up
- `STALE_PACKAGE` — package open 21+ days with no new bids → review

**The standard follow-up protocol:**
- **Day 7 of no response:** Email follow-up
- **Day 10 of no response:** Phone call
- **Day 14 of no response:** Mark `no_response`, find replacement sub
- **3 days before expiry:** Phone call to extend or award
- **1 day before expiry:** Second call if no response

**Current critical items:**
- Aspen Welding LLC — 1355R steel — expires 2026-07-02 — CALL TODAY

---

## 5.6 Receiving and Logging Bids

**When a bid comes in:**

1. Record receipt in the system immediately (same day)
2. Confirm bid is complete — does it include all scope? Are exclusions reasonable?
3. Request clarification in writing for any missing items (same day)
4. Update bid status:
```
POST /gateway/bids/update
X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6
{
  "bid_id": [id],
  "status": "received",
  "bid_amount": 127500,
  "received_date": "2026-06-30",
  "notes": "Includes all structural steel erection per drawings S1-S8. Excludes fireproofing."
}
```
5. Flag any bid that is more than 15% above budget estimate — GBT will prepare a reconciliation

**Bid confidentiality:**
HCI operates an open bidding process, but specific dollar amounts are confidential. Do not share one sub's number with another to negotiate. This is both unethical and damages vendor relationships.

---

## 5.7 Bid Leveling

**Bid leveling is the comparison of received bids on a scope-adjusted basis so that Buck can make an informed award decision.**

**What leveling means:**
Two bids on the same scope may not actually be the same scope. Leveling identifies:
- What's included vs. excluded
- Allowances vs. lump sums
- Material specifications (matching spec or alternate)
- Labor assumptions (local labor or crew from outside Aspen)
- Schedule assumptions

**Leveling template (prepared by GBT):**

| Item | Budget Est. | Sub A | Sub B | Sub C | Notes |
|------|-------------|-------|-------|-------|-------|
| Total Base Bid | $285,000 | $267,000 | $292,000 | $311,000 | |
| Fireproofing (Ex.) | incl. | N/A | +$18,000 | incl. | Sub A excludes |
| Mobilization | incl. | incl. | incl. | incl. | |
| Adjusted Total | $285,000 | $285,000 | $310,000 | $311,000 | |
| Recommendation | — | **AWARD** | 2nd choice | 3rd | |

**Leveling output → Buck for award decision.**
GBT sends the leveling summary via Telegram with a clear recommendation. Buck approves or redirects.

---

## 5.8 Award Process

**No award is final without Buck's explicit approval.**

**Award flow:**
1. GBT sends leveling summary + recommendation to Buck via Telegram
2. Buck approves, rejects, or asks for additional information
3. On approval: PM issues verbal/email notification to the awarded sub
4. Contract preparation begins (see Chapter 07 — Contract Management)
5. System updated: `status → awarded`, `awarded_amount → [final number]`

**What NOT to do:**
- Do not tell a sub they're "probably getting the job" before Buck's approval
- Do not give a sub a reason for why they didn't get the award — just "we went a different direction"
- Do not award a sub whose COI has expired — verify first

**After award:**
- Unsuccessful subs receive a brief "thanks for bidding, we went a different direction" email
- All bid amounts are archived — never deleted
- The awarded sub gets a pre-construction meeting within 5 business days of award

---

## 5.9 Vendor Performance Feedback

Every completed bid package creates a vendor performance data point. The system tracks:
- Response time (days from SOW sent to bid received)
- Coverage (what % of scope items were priced)
- Award history (how often their bids are competitive)

**After each project phase, update vendor scores:**
```
GET /gateway/vendors/scores/{vendor_id}
```
If a vendor performed poorly (no-show on site, unresponsive to RFIs, quality issues), log a note in the vendor record. This affects their score and their future invite priority.

**Vendor score grades:**
- A (80-100): First invite list, preferred
- B (60-79): Standard invite list
- C (40-59): Invite only if not enough A/B options
- D (<40): Do not invite without specific reason and Buck's awareness

---

*Next: Chapter 06 — Vendor and Subcontractor Management*

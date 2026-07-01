# Chapter 08 — Budget and Financial Controls
**HCI AI Operations Manual | Part I — Business Operations**
*Authority: Buck Adams | Last Updated: 2026-06-30*

---

## 8.1 Overview

Every HCI project runs against a fixed contract value. Every dollar committed above that value comes out of margin. Budget control is not an administrative task — it is direct profit protection.

The HCI AI system tracks every committed dollar and projects final cost in real time. The PM's job is to act on those projections before they become problems.

---

## 8.2 Live Budget Endpoints

**246 Gallo Way (in construction):**
```
GET /gateway/project/246GW/budget
```
Returns:
- Contract value: $6,300,000
- Committed (awarded): [current total]
- Open estimates (unawarded TBD packages): [estimated total]
- Projected final cost: committed + open estimates
- Budget status: ON_BUDGET / OVER_BUDGET / WARNING

**Pre-construction projects (64EW, 101F, 1355R):**
```
GET /gateway/project/{code}/pm
```
Budget section shows bid coverage vs. estimate per package. Packages where received bids exceed estimate are flagged.

---

## 8.3 The 246GW Budget Warning

**Current status (2026-06-30): OVER_BUDGET**

| Line | Amount |
|------|--------|
| Contract Value | $6,300,000 |
| Committed (19 awarded packages) | $6,314,913 |
| Over Contract (committed) | +$14,913 |
| Open Estimates (18 TBD packages) | $2,745,600 |
| **Projected Final Cost** | **$9,060,513** |
| **Over Contract (projected)** | **+$2,760,513 (44%)** |

**Biggest open TBD packages:**
- Landscape: $350,000 estimate
- AV/Technology: $500,000 estimate  
- Spa/Pool Equipment: $280,000 estimate
- Finish Carpentry: $310,000 estimate
- Flooring: $333,000 estimate
- Tile/Stone: $320,000 estimate

**What this means:**
The project cannot be built as currently designed for $6.3M. Either the scope needs value engineering, or the contract needs to be amended to reflect the actual project cost. Buck needs to discuss this with the owner (client) before any more packages are awarded.

**PM action: Do not award any additional packages on 246GW until Buck has reviewed the budget and directed the path forward.**

---

## 8.4 Budget Structure

**Every HCI project budget has three tiers:**

**Tier 1 — Contract Value**
The total GMP (Guaranteed Maximum Price) or lump sum agreed to in the owner-contractor agreement. This is the ceiling.

**Tier 2 — Committed Costs**
Sum of all awarded subcontracts + any owner-authorized change orders. This is what HCI has legally agreed to pay.

**Tier 3 — Projected Final Cost**
Tier 2 + estimated costs of all unawarded scopes + anticipated change orders + HCI contingency. This is the forecast.

**The warning trigger:** Tier 3 > 95% of Tier 1 → WARNING status.
**The alert trigger:** Tier 3 > 100% of Tier 1 → OVER_BUDGET, alert to Buck.

---

## 8.5 Contingency Management

Every project budget includes a contingency — money set aside for unforeseeable costs.

**HCI standard contingency:**
- Pre-construction projects: 5-10% of estimated cost
- Construction projects: 3-5% of contract value

**Contingency is not a slush fund.** It is for:
- Unforeseen site conditions (rock that wasn't in the geotech, hidden utilities)
- Design changes that couldn't reasonably have been anticipated
- Code interpretations that require additional work

**Contingency is NOT for:**
- Scopes that were underestimated at bid
- Subs who underbid and want more money
- Scope creep approved without a change order

**Contingency tracking:**
PM maintains a contingency log: every draw from contingency is documented with reason, amount, and Buck's approval. Contingency balance is reported in every monthly budget report.

---

## 8.6 Change Order Cost Control

Change orders are the primary source of budget overruns. The control points:

**Before a change is approved:**
1. Who requested this change? (Owner, architect, or HCI?)
2. Is this in the original contract scope? (If yes, it's not a change order)
3. What is the cost? (Get a detailed breakdown from the sub — not just a number)
4. What is the schedule impact?
5. Who is paying? (Owner direct, contingency, or HCI error?)

**The change order authorization matrix:**
- Owner-requested change: Owner must sign a Change Order Authorization before HCI proceeds. HCI does not advance owner change costs.
- Architect-directed change: Evaluate whether it's within original design intent or an error/omission. Route to Buck.
- HCI error: Budget from contingency. Notify Buck. Document lesson learned.
- Site condition: Evaluate contract language. Route to Buck and legal if large.

---

## 8.7 Pay Application Review

**Every sub's pay application is reviewed before Buck approves payment.**

**PM review checklist:**
- [ ] Requested amount matches work in place (verified against Houzz schedule % complete)
- [ ] Conditional lien waiver for this period is attached
- [ ] Prior period unconditional lien waiver is attached
- [ ] No unapproved change order amounts embedded
- [ ] Stored materials (if any) are documented and insured
- [ ] Retention is being held at the correct percentage
- [ ] Sub's current COI is on file

**If anything fails the checklist:** Notify the sub in writing with the specific deficiency. Do not route to Buck for approval until it's resolved.

**PM prepares the pay application summary** — a single page showing all subs, their current request, cumulative billing, and balance. Routes to Buck for approval by the 27th.

---

## 8.8 Budget Reporting

**Monthly budget report (issued by the 5th of the month):**
Prepared by GBT, reviewed by PM, approved by Buck before it goes to the owner.

**Report contents:**
1. Contract value
2. Approved change orders to date (total)
3. Current adjusted contract
4. Committed costs (awarded subcontracts)
5. Remaining open estimates
6. Contingency balance (original / drawn / remaining)
7. Projected final cost
8. Variance to contract (+/-)
9. Narrative explanation of significant variances

**Owner budget reporting:**
For 246GW with the budget overrun, the owner needs a clear picture. GBT prepares the owner budget narrative for Buck's review before it goes out. The number doesn't go to the owner before Buck has talked to them.

---

## 8.9 Financial Authority Matrix

| Transaction | Authority |
|-------------|-----------|
| Award subcontract | Buck approval required |
| Issue Change Order (any amount) | Buck approval required |
| Draw from contingency | Buck approval required |
| Pay application approval | Buck approval required |
| Owner billing | Buck approval required |
| Vendor purchase order < $5,000 | PM can approve |
| Vendor purchase order > $5,000 | Buck approval required |
| Emergency repair (night/weekend) | PM can authorize up to $2,500; notify Buck same day |

No one other than Buck has authority to commit HCI to expenditures over $5,000 outside the pre-approved subcontract schedule.

---

*Next: Chapter 09 — Schedule Management*

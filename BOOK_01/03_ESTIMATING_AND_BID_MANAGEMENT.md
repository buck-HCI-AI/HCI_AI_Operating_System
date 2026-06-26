# BOOK_01 — Volume 03: Estimating and Bid Management

**Version:** 1.0 | **Date:** 2026-06-25

---

## How HCI Estimates

HCI's estimating process runs from ROM budget through to a awarded buyout. The system supports every step:

**Step 1 — Plan Reading (SOP 04, 05, 06)**
- Drawings and specs are uploaded to project folder
- AI indexes all documents into Project Brain
- AI generates scope checklist: all trade scopes identified, missing details flagged, risk items logged

**Step 2 — ROM Budget (SOP 07, 08, 09)**
- Historical cost database provides unit rates from past HCI projects
- AI drafts ROM budget by scope line using historical rates
- Estimator reviews; Buck approves release
- Allowances, alternates, and exclusions documented (SOP 10)

**Step 3 — Bid Package Assembly (SOP 11)**
- Scope sections drafted from drawings, narrative, and risk log
- Sub list pulled from vendor intelligence (trade, geography, performance)
- Bid package issued after Buck approves

**Step 4 — Distribution and Follow-Up (SOP 13, 14)**
- Bid requests sent and tracked in bid intelligence service
- Follow-up calls tracked and logged
- Bid receipts logged with date/time stamp

**Step 5 — Bid Leveling (SOP 15)**
- All received bids normalized to a common scope basis
- Qualifications, exclusions, and alternates extracted per bid
- Risk flags identified (scope gaps, contract qualifications, schedule exceptions)
- Leveling sheet produced with all-in cost per bidder
- Recommendation drafted; Buck approves award

**Step 6 — Buyout (SOP 16)**
- Award memo created with scope, price, terms
- Subcontract agreement initiated (SOP 19)
- Compliance and insurance tracked (SOP 21, 22)

---

## Bid Intelligence Service

The bid-intelligence service is the backbone of Steps 3-5. It provides:

| Function | Description |
|---------|-------------|
| Bid tracker | All bid requests, follow-ups, and receipts per project |
| Scope gap detection | AI reads bids against scope and flags what subs excluded |
| Qualification extraction | Terms, exceptions, qualifications noted by sub in their bid |
| Normalization | All bids adjusted to common scope basis for side-by-side comparison |
| Historical rate check | Each line item checked against historical HCI data |
| Recommendation | Ranked list with rationale; flags any sub with performance issues |

---

## Sub Outreach

Sub outreach is driven by vendor intelligence — HCI's sub CRM:

- Trade classifications (MEP, concrete, framing, roofing, etc.)
- Geographic coverage
- Past project performance (on-time, responsive, quality)
- Current workload
- Insurance/license status

AI drafts outreach. PM confirms before send. All outreach is logged.

**Minimum bidders per scope:** 3 responsive bids before award. If fewer than 3, escalate to Buck before proceeding.

---

## Bid Package Standard

Every HCI bid package must include:

| Section | Required |
|---------|---------|
| Scope of Work | Yes — trade-specific, no ambiguity |
| Contract Documents | Yes — all applicable drawings and specs by number/date |
| Alternates and Allowances | Yes — called out explicitly |
| Schedule Requirements | Yes — milestones, phasing, access restrictions |
| Insurance and Bond Requirements | Yes — limits per project requirements |
| Subcontract Terms | Yes — HCI standard terms or client-specific |
| Bid Form | Yes — structured so all bids can be leveled on same form |
| Addenda Log | Yes — all addenda before bid date listed and acknowledged |

A bid package that is missing any of these items cannot be issued. The approval gate blocks issue until all sections are complete.

---

## Estimating KPIs

| KPI | Target | How Measured |
|-----|--------|-------------|
| ROM accuracy vs. final buyout | ± 10% | ROM budget vs. leveled award |
| Bid cycle time (package to award) | ≤ 21 days | SOP 11 issue date vs. SOP 16 award date |
| Sub response rate | > 60% | Bids received vs. outreach sent |
| Leveling cycle time | ≤ 48 hours from bid close | SOP 15 cycle time |
| Scope gap rate (per 10 bids) | < 2 unexpected gaps | Risk flags triggered post-award |

---

## What AI Cannot Do in Estimating

- Award to a subcontractor without Buck's approval
- Issue external commitments (invitations to bid, award letters) without human review
- Accept bid qualifications that change scope without flagging to the PM
- Approve alternate scope pricing without human confirmation

---

*Volume 04 covers procurement after the award.*  
*SOP 11 service code: `03_Source_Code/services/sop_execution/sop_11_bid_package/`*  
*SOP 15 service code: `03_Source_Code/services/sop_execution/sop_15_bid_leveling/`*

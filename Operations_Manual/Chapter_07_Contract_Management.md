# Chapter 07 — Contract Management
**HCI AI Operations Manual | Part I — Business Operations**
*Authority: Buck Adams | Last Updated: 2026-06-30*

---

## 7.1 Overview

Contracts are the foundation of every subcontractor relationship. They define what work is being done, at what price, on what schedule, and what happens when things go wrong. Every sub who sets foot on an HCI project must have a signed contract before work begins.

No contract = no work. No exceptions.

---

## 7.2 Contract Types at HCI

**Lump Sum (Fixed Price)**
The sub agrees to complete a defined scope for a fixed dollar amount. Best for well-defined scopes with complete drawings and specs. Most HCI subcontracts are lump sum.

**Unit Price**
The sub agrees to complete work at a set price per unit (e.g., linear foot of concrete, square foot of tile). Used when quantities are uncertain at bidding. Less common.

**Time and Materials (T&M)**
The sub is paid for labor hours at agreed rates plus material cost plus overhead/markup. Used only for undefined scopes or emergency work. Requires owner approval.

**Owner-Furnished, Contractor-Installed (OFCI)**
Owner purchases the material; the sub installs it. Common for appliances, light fixtures, specialty items. The contract must clearly state who provides what.

---

## 7.3 HCI Standard Subcontract

All HCI subcontracts use the AIA A401 form modified with HCI's standard amendments. Core provisions:

**Scope of Work**
Precise description of what the sub is doing, referenced to specific drawing sheets and specification sections. If it's not in the scope, they're not doing it.

**Contract Sum**
The approved bid amount. Any changes require a Change Order.

**Schedule**
The sub is contractually bound to the project schedule. Late performance is a breach.

**Payment Terms**
Pay App due by the 25th. HCI reviews by the 27th. Payment by the 5th.

**Retention**
HCI holds 5% of each payment application until substantial completion. Released upon owner acceptance of the work.

**Insurance**
Sub must maintain insurance per HCI requirements (see Chapter 06). Work stops if COI lapses.

**Change Orders**
All changes must be approved in writing before the sub proceeds. Verbal authorizations for changes are not binding. GC directive (written) authorizes work to proceed pending formal Change Order — but there must always be a written directive.

**Disputes**
Mediation before litigation. Governed by Colorado law. Venue in Pitkin County.

---

## 7.4 Contract Execution Workflow

**Step 1 — Award approval**
Buck approves the award. GBT records the approval in the system.

**Step 2 — Contract preparation**
GBT prepares the AIA A401 with:
- Scope description from the SOW
- Approved contract sum
- Schedule milestone dates
- Any project-specific special conditions

**Step 3 — Review**
PM reviews the draft for accuracy:
- Scope matches the awarded bid
- Dollar amount matches exactly
- Schedule dates are achievable
- No conflicting terms vs. the prime contract

**Step 4 — Execution**
Both parties sign. DocuSign for non-local subs; original signature for major contracts.

**Step 5 — System update**
```
POST /gateway/bids/update
{"bid_id": [id], "status": "awarded", "awarded_amount": [final], "awarded_date": "2026-07-05"}
```

**Step 6 — Pre-construction meeting**
Scheduled within 5 business days of award (see Chapter 06).

**Nothing starts on site until Steps 1-4 are complete.**

---

## 7.5 Change Order Management

**What requires a Change Order:**
- Any addition or deletion to the sub's contracted scope
- Any increase or decrease to the contract sum
- Any change to the milestone dates that are contractually binding

**The Change Order process:**

**Step 1 — Identify the change**
Either HCI or the sub identifies something that differs from the contract. Document it in writing immediately — email or Houzz note.

**Step 2 — Scope and price the change**
Sub provides a written proposal: what they'll do differently, at what cost, with what schedule impact.

**Step 3 — HCI review**
GBT analyzes the proposal: Is the change legitimate? Is the price reasonable? Is there schedule impact? Sends analysis to Buck.

**Step 4 — Buck approves**
All change orders require Buck's written approval. No oral authorizations for changes.

**Step 5 — Issue Change Order**
Formal Change Order document executed by both parties before the changed work proceeds. Exception: Written GC directive authorizes work in urgent situations, but CO must follow within 5 business days.

**Step 6 — System update**
The budget and commitment records are updated to reflect the approved Change Order.

**What NOT to do:**
- Do not tell a sub "just do it and we'll sort it out later" — this creates cost exposure
- Do not approve a change order scope without understanding what's driving the cost
- Do not issue a CO for more than $5,000 without a written backup (sub's cost breakdown)

---

## 7.6 Contract Disputes and Back Charges

**Back charges:**
If a sub causes damage to another sub's work, fails to maintain a clean workspace, or creates costs that HCI has to absorb, that cost is a back charge against the sub.

Back charge protocol:
1. Document the cost with invoices and photos
2. Notify the sub in writing with cost documentation — give them 5 business days to respond
3. If they agree: process the deduction in the next Pay App
4. If they dispute: flag to Buck; do not deduct without legal review if the amount is over $10,000

**Contract disputes:**
Any claim by a sub that exceeds $25,000 or involves interpretation of the contract language:
1. Flag to Buck immediately
2. Stop informal negotiations — everything in writing from here
3. Buck to decide whether to involve legal counsel
4. Never threaten litigation without Buck's explicit authorization

---

## 7.7 Lien Waivers

**Lien waivers are non-negotiable.** Every payment release requires:

**Conditional Waiver Upon Progress Payment:**
Sub signs before the check is issued. Waives lien rights for the current payment period, conditioned on the check clearing.

**Unconditional Waiver Upon Progress Payment:**
Submitted with the following month's Pay App. Confirms the prior payment was received and they waive lien rights for that period.

**Conditional Waiver Upon Final Payment:**
Signed at final payment. Waives all remaining lien rights conditioned on final payment clearing.

**Unconditional Waiver Upon Final Payment:**
Collected after the final check clears. This is the clean close-out document.

**Never release retention without an unconditional final lien waiver.**

---

## 7.8 Contract Record Keeping

All contracts are filed in:
- Google Drive: Project folder → `Contracts/` subfolder
- System: status updated to `awarded` with `awarded_date` and `awarded_amount`
- HubSpot: deal record updated (route through GBT, Buck approves HubSpot write)

**Retention of contract documents:**
10 years minimum from project substantial completion. Longer for any project with unresolved claims.

---

*Next: Chapter 08 — Budget and Financial Controls*

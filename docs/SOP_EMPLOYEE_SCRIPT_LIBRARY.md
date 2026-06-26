# HCI AI — SOP Employee Script Library

**Version:** 1.0 | **Date:** 2026-06-25 | **Source:** HCI_SOP_2_0_Scripted_Operating_System_Framework.docx  
**Layer:** Layer 2 — Employee Training Scripts

This library contains the Layer 2 Employee Training Scripts for pilot SOPs 11 and 15. These scripts are role-based, step-by-step, and written in second-person direct address. They are the standard that new employees and role backups follow.

---

## SOP 11 — Bid Package Assembly: Employee Training Script

### Your Role and Context

You are **HCI's Estimator / Preconstruction Lead**. Your job is to build bid packages that produce complete, comparable bids. A bid package is not a document dump — it is the specification of exactly what HCI wants priced and on what terms. If the bid package is unclear, subs will bid on different things, and your leveling will be comparing apples to oranges.

Every bid package you build must meet two tests:
1. Could a sub bid this job completely, without any verbal clarification from HCI?
2. Could an HCI estimator level the bids without guessing what each sub included?

If the answer to either is No, the package is not ready.

---

### Before You Start — Collect These Documents

Do not begin assembling scope sections until you have ALL of the following confirmed:

- [ ] Architectural drawings — current revision confirmed (note revision date)
- [ ] Structural, MEP drawings — all applicable, current revision
- [ ] Project specifications — all applicable sections (confirm addenda incorporated)
- [ ] Soils report — if site work or foundation scope is included
- [ ] Hazmat assessment — if any demo or renovation work is in scope
- [ ] Construction narrative from plan review (SOP 05) — complete
- [ ] Risk log from SOP 06 — reviewed; open items noted
- [ ] Allowances and alternates from SOP 10 — defined and signed off
- [ ] Budget approved (SOP 09) — do you know what you're trying to achieve?

**If any of these are missing: Do not proceed. Log the blocker in the system and notify the PM.**

---

### Step-by-Step Process

**Step 1: Open the SOP 11 workflow in HCI AI**
- System creates a new SOP 11 instance for this project
- Confirm all inputs are logged; checklist shows green for each item

**Step 2: Build the scope section for each trade**

For every trade in scope:
- Open the drawings for that trade
- Write the scope section in plain English: what is included, what is NOT included
- Reference every applicable drawing by number and date
- Reference every applicable spec section by number
- Call out allowances with a specific dollar amount and basis
- Call out alternates with a description and how they appear on the bid form
- List explicit exclusions — don't assume subs know what you don't want

AI will review your scope against the drawings and flag gaps. Review every flag.

**Step 3: Build the sub invite list**
- Pull the sub list from Vendor Intelligence for each trade: trade classification + geography
- Review performance history for each sub; remove any flagged for cause
- Add to the project's bidder list
- Minimum 3 qualified subs per trade — if you have fewer, notify PM before proceeding

**Step 4: Assemble the bid package**
- Scope sections (one per trade)
- Contract documents list (drawings and specs by number and date)
- HCI bid form (if required)
- Schedule requirements (milestones, access restrictions, phasing)
- Insurance and bond requirements
- HCI standard subcontract terms (or project-specific terms)
- Prevailing wage requirements (if applicable)
- MBE/WBE requirements (if applicable)

**Step 5: Review the complete package**
- Read through the complete package as if you were a sub receiving it for the first time
- Could you bid it without calling HCI? If not, what is unclear?
- Are all cross-references (drawing to scope, scope to spec) consistent?
- Does the bid form match the scope sections?

**Step 6: Submit for PM Review**
- Set SOP 11 status to Internal Review
- PM reviews; may send back as Revision Required
- Address all PM comments before resubmitting

**Step 7: Wait for Buck's Approval**
- PM routes to Buck for Gate 11-C approval
- Do not issue to subs until system shows Approved status with Buck's record

**Step 8: Issue**
- Once Approved, issue the package to all subs on the invite list
- Log issue date and method in the system
- Set a follow-up reminder for 3 days before bid due date

---

### Finished Work Looks Like

- Every trade scope section is specific, complete, and cross-referenced
- AI gap check shows no unresolved flags
- PM has reviewed and confirmed
- Buck has approved
- Bid list shows ≥ 3 qualified subs per trade
- Issue date logged in system

---

### Common Mistakes

- **Issuing before all inputs are confirmed.** The drawings revised after you assembled scope mean the subs are pricing the wrong thing.
- **Vague scope language.** "All electrical work" is not a scope section. Name the systems.
- **Missing exclusions.** If GC is not providing temporary power, say so explicitly.
- **Skipping the bid form.** Without a structured bid form, leveling becomes interpretation.
- **Not reviewing AI gap flags.** The flags are there because the AI found inconsistencies. Review them.

---

### Handoff

When the bid due date passes, hand off to SOP 15 (Bid Leveling):
- Log handoff in system: confirm all bids received (or not received) per bidder
- Notify the leveling estimator: bid list and all received bids are in the system
- Set SOP 11 status to Handed Off

---

## SOP 15 — Bid Leveling: Employee Training Script

### Your Role and Context

You are **HCI's Estimating Lead / Principal (Buck)**. Your job in bid leveling is to take all received bids and produce a true, apples-to-apples comparison that supports a sound award decision.

Bid leveling is not just adding up numbers. Every bid is a different document, with different assumptions, qualifications, and exclusions. Your leveling sheet makes all of those differences visible so that Buck can make an informed award decision — not just pick the lowest number.

---

### Before You Start — Confirm These Inputs

- [ ] Bid due date has passed
- [ ] All bids logged in system: bidder name, bid amount, date received
- [ ] Minimum 3 responsive bids confirmed (or Buck has authorized exception)
- [ ] SOP 11 bid package is on hand for scope reference
- [ ] Original drawings and specs are accessible for scope disputes

**If fewer than 3 responsive bids: Do not proceed to award recommendation. Notify PM and Buck. Conduct SOP 14 follow-up to get additional bids or Buck authorizes exception.**

---

### Step-by-Step Process

**Step 1: Open the SOP 15 workflow in HCI AI**
- System links to the parent SOP 11 instance
- All received bids should already be logged; confirm count

**Step 2: For each received bid, record and extract**
- Enter the base bid amount
- Identify and list all exclusions (what the sub did NOT include)
- Identify all qualifications (terms the sub added that differ from HCI standard)
- Identify all alternates (how they bid each alternate)
- Note any schedule qualifications or exceptions
- Note any contract term exceptions (insurance, warranty, payment terms)

AI will assist by extracting qualifications from the bid text. Review every AI extraction — AI can miss context-specific language.

**Step 3: Normalize all bids to the same scope basis**

For each bid, calculate the "all-in" amount:
- Start with base bid
- Add back any items the sub excluded that must be in the scope (get a price add or HCI covers)
- Subtract any items included that are not in scope (rare — but possible)
- Add cost of unacceptable qualification (e.g., sub excludes warranty — what is HCI's cost to cover?)

Document every adjustment with the reason. "We added $5,000 to Miller's bid for HVAC controls because they excluded it but it's in scope" — that becomes a line in the leveling sheet.

**Step 4: Run AI analysis**
- AI produces normalized comparison: adjusted bid by bidder, side-by-side
- AI flags risk categories: scope, cost, schedule, contract, coverage, document control
- AI checks each bidder against vendor performance history
- AI drafts recommendation with rationale

Review the AI output line by line. Do not present to Buck without your own review.

**Step 5: Prepare leveling sheet**
- All bidders
- Base bid + adjustments = adjusted bid
- Risk flags per bidder
- Prior performance score per bidder (from vendor intelligence)
- Your recommendation: who to award and why
- Alternative recommendation if first choice has unacceptable risk

**Step 6: Submit for Internal Review**
- Set SOP 15 status to Internal Review
- PM reviews leveling sheet
- PM dispositions all open risk flags: Accepted / Resolved / Escalated

**Step 7: Route to Buck for Award Decision**
- Set status to Approval Required; Buck is notified
- Buck reviews leveling sheet, risk flags, and your recommendation
- Buck awards or requests additional information

**Step 8: After Buck's Decision**
- Log Buck's decision in system: sub name, amount, basis of decision
- Set status to Approved
- Create award memo
- Notify PM to initiate SOP 16 (Buyout)
- Set status to Handed Off

---

### Finished Work Looks Like

- Every bid is documented with base amount, adjustments, and rationale
- Leveling sheet shows all-in cost for each bidder on same scope basis
- All risk flags dispositioned
- AI recommendation reviewed and confirmed or overridden with reason
- Buck's decision recorded in system with timestamp
- Award memo complete

---

### Common Mistakes

- **Leveling only the number, not the scope.** Low bid is only good if it includes everything.
- **Skipping risk flag review.** A sub with a contract qualification that limits their liability is not the same as one without that qualification, even at the same price.
- **Not documenting adjustments.** If the adjusted bid is different from the base bid, every adjustment must be documented.
- **Missing prior performance.** Check vendor intelligence before recommending a sub you haven't used.
- **Recommending award without addressing coverage risk.** If you only have 2 responsive bids, that is a risk — document it.

---

### Handoff

After Buck awards:
- Log handoff: PM and procurement team notified
- SOP 16 (Buyout) triggered
- Set SOP 15 status to Handed Off

---

*Layer 3 (AI Agent Scripts): `docs/SOP_AI_AGENT_SCRIPT_LIBRARY.md`*  
*Layer 4 (Templates): `docs/SOP_TEMPLATE_BACKLOG.md`*

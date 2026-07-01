# Chapter 10 — Risk Management
**HCI AI Operations Manual | Part I — Business Operations**
*Authority: Buck Adams | Last Updated: 2026-06-30*

---

## 10.1 Overview

Risk management is the discipline of seeing problems before they arrive. In Aspen luxury construction, the risks are real: subcontractor failure, material lead time blowouts, permit delays, weather windows, client-design conflicts, and budget surprises.

The HCI AI system tracks open risks per project. The PM's job is to close risks before they become incidents.

---

## 10.2 Risk Register

**Every active project has a risk register.** Risks are tracked in the database and surfaced in the PM console.

```
GET /gateway/project/{code}/pm
```
The `risks` section of the PM console shows:
- Risk description
- Severity (CRITICAL / HIGH / MEDIUM / LOW)
- Probability (HIGH / MEDIUM / LOW)
- Owner (who is responsible for resolving)
- Status (OPEN / MITIGATED / CLOSED)
- Mitigation notes

**Risk register update:**
Route to GBT with the new risk description and severity. GBT writes the handoff; Claude Code updates the DB.

---

## 10.3 Current Open Risks (2026-06-30)

**1355 Riverside — 5 open risks:**

| # | Risk | Severity | Status |
|---|------|----------|--------|
| 1 | Aspen Welding bid expires 7/2 — steel package unresolved | CRITICAL | OPEN |
| 2 | RFI-001 Axis B Beam Pocket — structural response pending | HIGH | OPEN |
| 3 | 73 bid packages — 58 still collecting, major scopes unawarded | HIGH | OPEN |
| 4 | Foundation concrete SOW sent 6/30 — no responses yet | MEDIUM | OPEN |
| 5 | Premier Landworks site utilities — 1 day behind | MEDIUM | OPEN |

**246 Gallo Way — BUDGET RISK:**
- Projected cost $9.06M vs. contract $6.3M — HIGH risk, open
- No value engineering plan in place yet

---

## 10.4 Risk Classification

**CRITICAL — Requires Buck's attention today:**
- Risk that can stop the project if unresolved within 48 hours
- Risk that affects the client or involves a legal/contractual obligation
- Budget overrun exceeding contract value without owner knowledge

**HIGH — Requires resolution within 1 week:**
- Risk that can push the schedule by more than 5 days
- Missing bids on critical path scope
- Sub performance issue without active recovery plan

**MEDIUM — Manage within 30 days:**
- Bids outstanding but not on critical path
- Schedule item overdue but not on critical path
- Material lead time concern for scope not yet ordered

**LOW — Monitor:**
- General market conditions
- Long-lead items with adequate float
- Vendor relationship issues not affecting current project

---

## 10.5 Risk Response Strategies

**Avoid:** Change the plan so the risk can't happen.
*Example: Schedule steel erection after concrete is cured — not parallel — to avoid crane conflict.*

**Mitigate:** Take action to reduce probability or impact.
*Example: Invite 4 steel subs instead of 2 to reduce the risk of only getting one bid.*

**Transfer:** Shift the risk to another party.
*Example: Require the sub to carry delay liquidated damages for critical path work.*

**Accept:** Acknowledge the risk and have a response plan ready.
*Example: Accept that Aspen winters can delay exterior work; have an interior scope ready to run during weather days.*

**For every CRITICAL or HIGH risk, the risk register must show:**
- Which strategy is being applied
- Specific mitigation actions taken
- Owner of the risk (who is responsible)
- Resolution date target

---

## 10.6 Site Condition Risks

**Unforeseen conditions are the biggest financial risk in construction.** When the site reveals something unexpected:

1. **Stop work** in the affected area if proceeding could damage site, structure, or people
2. **Document immediately** — photos, measurements, exact location
3. **Notify Buck same day** — this is never a field decision
4. **Preserve the condition** — don't disturb it until the design team and Buck have reviewed
5. **Get design team response in writing** — not verbal

**Common unforeseen conditions in Aspen:**
- Rock at unexpected depth (more blasting cost)
- Existing utilities not on as-built drawings
- Soil conditions different from geotech report
- Historic fill or environmental contamination

All of these have contract implications. Document and escalate. Never absorb unforeseen costs without documenting them first.

---

## 10.7 Client-Driven Risk

**Design decisions made after construction starts are the most expensive risk.**

**How to prevent it:**
- All finishes, fixtures, and specifications should be selected before rough-in
- Interior designer should have all selections confirmed before any millwork/tile/flooring sub is awarded
- Any "we'll figure it out later" decision is a risk logged in the risk register

**When the client changes their mind:**
1. Every design change has a cost. Document it before anyone starts executing.
2. The design team (architect, interior designer) confirms in writing that the change is coordinated with all trades.
3. A Change Order is issued for cost and schedule impact.
4. No sub proceeds on a client change until the CO is approved.

---

## 10.8 Weather Risk in Aspen

**The Aspen construction window is compressed:**
- Hard freeze risk from October 15 through May 15
- Significant snowfall possible from October through April
- Concrete cannot be poured below 40°F without cold weather protection measures
- Exterior work (roofing, siding, exterior finishes) is winter-weather dependent

**Planning for weather:**
- Any project that needs to be winter-tight by October 15 must start framing no later than August 1
- If framing starts after August 1, winter enclosure must be in the schedule with associated cost
- Winter work (concrete pours with heated forms, heated enclosures) adds 15-25% cost to affected scopes

**Weather log:**
Every day with weather-related work stoppage is logged in Houzz daily with: date, conditions, activities stopped, and any recovery actions.

---

## 10.9 Regulatory and Permitting Risk

**Pitkin County permitting is among the most rigorous in Colorado.**

**Key risks:**
- Permit applications that don't match approved drawings → rejection, revision cycles
- Inspections that fail due to work that wasn't ready → re-inspection delays
- Neighbor objections to scope changes → public hearing requirements
- Environmental or wildlife buffer violations → potential stop-work orders

**Mitigation:**
- Submit permit applications 8-12 weeks before needed construction start
- Never proceed without a valid permit for that phase
- Schedule inspections early — don't wait until the last moment
- Any change to the permitted scope requires an amendment before proceeding

---

*Next: Chapter 11 — Client Management*

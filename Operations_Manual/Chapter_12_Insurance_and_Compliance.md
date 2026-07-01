# Chapter 12 — Insurance and Compliance
**HCI AI Operations Manual | Part I — Business Operations**
*Authority: Buck Adams | Last Updated: 2026-06-30*

---

## 12.1 Overview

Insurance and compliance is not a bureaucratic exercise — it protects HCI, its clients, and its workers from catastrophic financial exposure. A single uninsured incident can exceed the entire project value.

Every sub working on an HCI project is insured. Every HCI project is permitted. No exceptions.

---

## 12.2 HCI's Own Insurance

**General Liability:** Commercial General Liability policy. All subcontractors must name HCI as Additional Insured.

**Builder's Risk:** Maintained by HCI for each project. Covers the structure under construction against loss by fire, theft, vandalism, wind, and other covered perils. Typically maintained until Certificate of Occupancy.

**Workers Compensation:** HCI maintains WC for its own employees. Each sub is responsible for WC for their own crews.

**Umbrella/Excess Liability:** Excess coverage above the CGL for significant loss events.

**Professional Liability:** Architects, engineers, and design professionals carry E&O (Errors & Omissions) — confirm this is in place for all design team members.

---

## 12.3 Subcontractor Insurance Requirements

**Every sub must provide a Certificate of Insurance (COI) before starting work.**

**Minimum limits:**

| Coverage | Minimum |
|----------|---------|
| Commercial General Liability (per occurrence) | $1,000,000 |
| Commercial General Liability (aggregate) | $2,000,000 |
| Workers Compensation | State statutory limits |
| Employer's Liability | $500,000 / $500,000 / $500,000 |
| Auto Liability (combined single limit) | $1,000,000 |

**For contracts over $500,000:**
| Coverage | Minimum |
|----------|---------|
| Umbrella/Excess Liability | $5,000,000 |

**Required endorsements on the COI:**
- Additional Insured: "Hendrickson Construction LLC, its officers, directors, employees, agents, and assigns"
- Waiver of Subrogation: in favor of HCI
- 30-day notice of cancellation to HCI

---

## 12.4 COI Tracking

**The vendor database tracks COI expiry for every sub.**

```
GET /gateway/knowledge/vendor?name=[sub+name]
```
Check the `coi_expiry` field.

**When a COI expires:**
1. PM notifies the sub immediately — "Your certificate expires [date]. Please provide a new COI."
2. If work is active: work stops on the day the COI expires unless a new certificate is received
3. No backfill — the sub must show continuous coverage, not a new policy starting after the lapse

**COI renewal cycle:**
Most commercial policies renew annually on the same date each year. For active subs, request a renewal COI 30 days before expiry.

**If a sub refuses or can't produce a current COI:**
This is a hard stop. Alert Buck. No exceptions to the insurance requirement on an active site.

---

## 12.5 Pitkin County Permit Requirements

**All HCI projects in Pitkin County require building permits.**

**Typical permit sequence for a single-family residence:**
1. **Site Permit / Land Use Approval** — before any grading or site work
2. **Building Permit** — structural, architectural, mechanical, electrical, plumbing
3. **Separate Permits (as applicable):** Electrical (local inspector or state), Plumbing, Mechanical, Fire Suppression
4. **CO (Certificate of Occupancy)** — issued after all inspections pass

**Pitkin County Building Department:**
- Submit applications at least 8-10 weeks before construction start
- Pitkin County requires complete and accurate drawings — no preliminary submittals
- Revisions to permitted drawings require a permit amendment

**Contractor License Requirements (Colorado):**
- HCI: Colorado General Contractor license required. Confirm license is current.
- Electrical subs: Colorado State Electrical license (journeyman and master)
- Plumbing subs: Colorado State Plumber license
- HVAC subs: EPA 608 certification where applicable; mechanical license
- All subs: Business license in Pitkin County if working there >30 days/year

---

## 12.6 Lien and Lien Waiver Compliance

**Colorado mechanic's lien law protects subs' right to lien the property for unpaid work.**

**HCI's obligation:**
Keep the lien chain clean. Every sub and supplier who might file a lien must be paid, or their lien rights must be waived.

**The lien waiver documents (see also Chapter 07):**
- Conditional Waiver on Progress Payment (before each payment)
- Unconditional Waiver on Progress Payment (with next month's pay app)
- Conditional Waiver on Final Payment (at final payment)
- Unconditional Waiver on Final Payment (after check clears)

**Preliminary Notice:**
Under Colorado law, some suppliers and lower-tier subs can file liens without warning. Maintain a preliminary notice log for every project — track who has filed preliminary notices and ensure they're in the payment chain.

**If a lien is filed:**
Contact Buck immediately. Do not attempt to release a lien without legal review if the amount is disputed.

---

## 12.7 OSHA Compliance

**HCI is responsible for overall site safety compliance under OSHA 29 CFR Part 1926 (Construction).**

**Required site safety items:**
- Fall protection for all work at heights >6 feet (personal fall arrest systems or guardrails)
- Excavation safety (shoring, sloping, or trench boxes for excavations >5 feet)
- Scaffold standards for all scaffold over 4 feet in height
- Electrical safety — GFCI protection on all temporary power on construction sites
- Hazard communication — SDS (Safety Data Sheets) available for all chemical products used on site
- Personal Protective Equipment — hard hats, safety glasses, appropriate footwear

**Superintendent responsibility:**
- Conduct daily safety inspection of the site
- Correct safety violations immediately
- Any OSHA recordable incident: see Chapter 03, Section 3.8

**Pitkin County requirements:**
May be more restrictive than federal OSHA in some areas (noise ordinance, dust control, working hours). Know the local requirements before starting.

---

## 12.8 Colorado Contractor License

**HCI must maintain a current Colorado General Contractor license.**

Annual renewal. Keep a copy of the license on file and accessible to the field team.

If Buck renews the license or receives updated documentation: notify Claude Code so the system record can be updated.

---

## 12.9 Accessibility and Fair Housing

For any project that could be classified as multi-family or commercial (not single-family residential): ADA (Americans with Disabilities Act) and Fair Housing Act requirements apply.

HCI's current portfolio is all single-family residential — these do not typically require ADA compliance. However, if a client requests accessibility features or if the design intent includes commercial use, flag to Buck and involve the architect immediately.

---

*Next: Chapter 13 — Submittal Management*

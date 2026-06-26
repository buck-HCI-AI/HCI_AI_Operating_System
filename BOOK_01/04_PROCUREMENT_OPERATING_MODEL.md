# BOOK_01 — Volume 04: Procurement Operating Model

**Version:** 1.0 | **Date:** 2026-06-25

---

## What Procurement Covers

Procurement begins when a scope is awarded and ends when all trades are under contract and field execution can proceed without procurement risk. It covers:

- Subcontract agreement execution (SOP 19)
- Compliance: certified payroll, MBE/WBE if required, prevailing wage (SOP 21)
- Insurance: COIs, endorsements, waivers (SOP 22)
- Bonds: performance and payment where required
- Long-lead items: materials ordered and tracked (SOP 18)
- W-9 and lien waiver collection (SOP 22)

---

## Procurement Sequence

```
SOP 16 Buyout (award decision, scope, price)
  → SOP 19 Subcontract Agreement (scope, price, terms, schedule into contract)
    → SOP 21 Compliance (license verification, certified payroll setup, MBE/WBE if applicable)
      → SOP 22 COI / W-9 / Lien Waiver (insurance on file, W-9 collected, waiver schedule set)
        → SOP 18 Long-Lead (materials ordered, lead time logged, delivery tracked)
          → SOP 23 Project Startup (sub briefing, kickoff, access, phasing)
            → Field Execution
```

---

## Procurement Controls

**No sub starts field work without:**
1. Signed subcontract agreement
2. COI on file meeting project requirements (limits, named insured, additional insured)
3. License verified (where required)
4. W-9 on file

These are not optional. The system tracks compliance per sub, per project. A sub flagged as non-compliant cannot receive a first payment without PM override and Buck notification.

---

## Procurement Service

The `procurement` service handles:

| Function | Description |
|---------|-------------|
| Award tracking | Scope, sub, price, award date per buyout line |
| Subcontract status | Draft → Sent → Signed — tracked per sub |
| COI tracking | Certificate on file, limits, expiration date, renewal reminder |
| Compliance log | Certified payroll submissions, MBE/WBE documentation |
| Long-lead tracker | Item, vendor, order date, promised date, actual receipt |
| W-9 tracker | On file or outstanding per sub |
| Lien waiver schedule | Conditional and unconditional waivers by pay period |

---

## Long-Lead Management

Long-lead items are any materials or equipment that require more than 4 weeks from order to delivery. They must be:

1. Identified at bid package stage (SOP 11 scope notes)
2. Confirmed at buyout (SOP 16 / SOP 18)
3. Ordered with delivery dates logged
4. Tracked weekly against schedule milestone

**Risk rule:** If a long-lead item delivery date slips past the earliest need date on the schedule, the system flags it as a Schedule Risk. PM is notified. If delivery slips past the critical path activity, it escalates to Buck.

---

## Procurement KPIs

| KPI | Target | Source |
|-----|--------|--------|
| Subcontracts signed before mobilization | 100% | SOP 19 status vs. NTP date |
| COIs on file before sub mobilizes | 100% | compliance tracker |
| Long-lead orders placed within 5 days of award | > 90% | procurement service |
| Expiring COIs renewed 30 days before expiration | 100% | COI expiration flag |
| W-9s collected before first payment | 100% | payment log |

---

## What Requires Buck Approval

- Award decisions (SOP 16)
- Subcontract terms that deviate from HCI standard form
- Compliance waivers (sub starts without compliant COI)
- Long-lead budget increases vs. buyout price

---

*Volume 05 covers the project management operating model during field execution.*  
*Procurement service: `03_Source_Code/services/procurement/`*

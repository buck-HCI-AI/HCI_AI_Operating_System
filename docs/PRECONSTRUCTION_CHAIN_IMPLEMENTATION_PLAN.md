# HCI AI — Preconstruction Chain Implementation Plan

**Version:** 1.0 | **Date:** 2026-06-25 | **Directive:** HCI_AI_SOP_to_Software_Execution_Layer_Master_Directive_v1.0

---

## What This Plan Covers

This plan defines the full implementation sequence for converting HCI's preconstruction SOPs (SOP 01-16) into executable four-layer software modules. Phase C (SOP 11 and SOP 15) is currently in progress. This document defines what comes next.

---

## Preconstruction Chain Overview

```
SOP 01  Opportunity Intake          → triggers SOP 02
SOP 02  Project Intake              → triggers SOP 03, SOP 04
SOP 03  File Organization           → parallel with SOP 04
SOP 04  Plan Review                 → triggers SOP 05, SOP 06
SOP 05  Construction Narrative      → feeds SOP 07, SOP 11
SOP 06  Missing Info / Risk Log     → feeds SOP 11, blocks SOP 09 if unresolved
SOP 07  ROM Budget                  → feeds SOP 09
SOP 08  Historical Cost Database    → feeds SOP 07 (data source, not workflow)
SOP 09  Budget Review               → triggers SOP 10, SOP 11 (after approval)
SOP 10  Allowances / Alts / Excl.  → feeds SOP 11 required inputs
SOP 11  Bid Package                 → triggers SOP 12, SOP 13 ← PHASE C
SOP 12  Subcontractor CRM           → feeds SOP 11, SOP 13 (data source)
SOP 13  Bid Distribution            → triggers SOP 14
SOP 14  Bid Follow-Up               → feeds SOP 15
SOP 15  Bid Leveling                → triggers SOP 16 ← PHASE C
SOP 16  Buyout                      → triggers SOP 19, SOP 21, SOP 22
```

---

## Phase C — Current Work (SOP 11 + SOP 15)

| Component | Status |
|-----------|--------|
| `shared/base_sop.py` | ⬜ In progress |
| `shared/sop_data_model.py` | ⬜ In progress |
| `shared/approval_engine.py` | ⬜ In progress |
| `shared/stop_condition.py` | ⬜ In progress |
| `shared/sop_kpi.py` | ⬜ In progress |
| `sop_11_bid_package/` — all 4 files | ⬜ In progress |
| `sop_15_bid_leveling/` — all 4 files | ⬜ In progress |
| `05_Database/sop_execution_schema.sql` | ⬜ In progress |
| `03_Source_Code/api/routers/sop.py` | ⬜ In progress |

**Target:** Phase C complete + Phase D (test) = SOP 11 and SOP 15 marked ✅ Complete

---

## Phase E — Chain Expansion (SOP 13, 14, 10, 16)

### Priority Order

1. **SOP 13 — Bid Distribution** (follows immediately from SOP 11)
   - Trigger: SOP 11 reaches Issued status
   - Core function: bid request sent to sub list; logged per sub; date stamped
   - AI role: draft outreach email; log send confirmation
   - Key gate: PM confirms distribution before logging
   - Estimated complexity: LOW (mostly logging and communication)

2. **SOP 14 — Bid Follow-Up** (parallel with SOP 13 duration)
   - Trigger: Bid due date - 7 days
   - Core function: track which subs have responded; follow-up log per sub
   - AI role: draft follow-up message; flag subs who haven't responded
   - Key gate: PM confirms minimum bidders met before handing to SOP 15
   - Estimated complexity: LOW

3. **SOP 10 — Allowances / Alternates / Exclusions** (precedes SOP 11)
   - Trigger: SOP 09 Budget Review complete
   - Core function: define all allowances, alternates, and explicit exclusions for the project
   - AI role: suggest allowances based on project type and historical data; flag unusual alternates
   - Key gate: PM confirms; Buck reviews if allowance total > threshold
   - Estimated complexity: MEDIUM

4. **SOP 16 — Buyout** (follows SOP 15)
   - Trigger: SOP 15 reaches Handed Off status (award decision made)
   - Core function: create award record; initiate subcontract (SOP 19); confirm scope
   - AI role: draft award memo; check scope against leveling
   - Key gate: PM confirms buyout complete before field mobilization
   - Estimated complexity: MEDIUM

### Phase E File Targets

```
services/sop_execution/sop_13_bid_distribution/
  __init__.py, sop_13_service.py, sop_13_agent.py, sop_13_templates.py

services/sop_execution/sop_14_bid_followup/
  __init__.py, sop_14_service.py, sop_14_agent.py, sop_14_templates.py

services/sop_execution/sop_10_allowances/
  __init__.py, sop_10_service.py, sop_10_agent.py, sop_10_templates.py

services/sop_execution/sop_16_buyout/
  __init__.py, sop_16_service.py, sop_16_agent.py, sop_16_templates.py
```

---

## Phase F — Backfill (SOP 04-09)

These SOPs feed the preconstruction chain from the beginning. They are backfilled after the bid/leveling core is working.

| SOP | Name | Complexity | Key AI Capability |
|-----|------|-----------|------------------|
| SOP 04 | Plan Review | HIGH | AI reads drawings and identifies scope items, gaps, coordination issues |
| SOP 05 | Construction Narrative | MEDIUM | AI drafts narrative from plan review output |
| SOP 06 | Risk Log | MEDIUM | AI identifies and classifies risks from drawings, specs, site conditions |
| SOP 07 | ROM Budget | HIGH | AI builds ROM from historical cost data by trade |
| SOP 08 | Historical Cost DB | DATA ONLY | Feeds SOP 07; no workflow conversion needed |
| SOP 09 | Budget Review | MEDIUM | AI compares ROM to historical benchmark; flags variance |

---

## Phase G — Close Loop (SOP 12, SOP 19)

| SOP | Name | Complexity | Notes |
|-----|------|-----------|-------|
| SOP 12 | Subcontractor CRM | MEDIUM | Connects to existing vendor_intelligence service; adds SOP wrapper |
| SOP 19 | Subcontract Agreement | HIGH | Contract document generation; legal review required |

---

## Full Preconstruction Chain — Completion Criteria

The preconstruction chain is complete when:
1. A bid can be assembled and issued without any manual document assembly
2. Sub outreach is driven by vendor intelligence with documented sub list
3. Bid leveling produces a structured recommendation within 48 hours of bid close
4. Award is made with a complete decision record in the system
5. Buyout record feeds subcontract and procurement without manual handoff
6. All 7 stop conditions enforced at every step
7. Buck's approval is required at: ROM release, bid package issue, award
8. KPIs track cycle time at every step

---

## Implementation Schedule (Target)

| Phase | SOPs | Target |
|-------|------|--------|
| Phase C | SOP 11, SOP 15 | 2026-07 |
| Phase D | Test: SOP 11, SOP 15 | 2026-07 |
| Phase E | SOP 10, 13, 14, 16 | 2026-08 |
| Phase F | SOP 04-09 | 2026-09 |
| Phase G | SOP 12, 19 | 2026-10 |

---

*Inventory: `docs/SOP_CONVERSION_INVENTORY.md`*  
*Standard: `docs/SOP_2_0_CONVERSION_STANDARD.md`*  
*BOOK_01 Volume 02: `BOOK_01/02_PRECONSTRUCTION_OPERATING_MODEL.md`*

# HCI AI — SOP Conversion Inventory
**Version:** 1.1 | **Date:** 2026-06-26 | **Directive:** HCI_AI_SOP_to_Software_Execution_Layer_Master_Directive_v1.0  
**Source:** HCI_SOP_Pack_All_42_SOPs.docx (`17e2QFuD_ikFLVv8fpkdyNdY1PkA27rUw`)

All 42 HCI SOPs indexed with conversion status. Update status as each SOP advances through the four-layer conversion.

---

## Status Key

| Symbol | Meaning |
|--------|---------|
| ⬜ | Not Started — source SOP exists; no conversion work begun |
| 🔵 | In Progress — conversion underway |
| ✅ | Complete — all 4 layers exist and tested |
| ❌ | Blocked — issue logged in KNOWN_ISSUES.md |

---

## Conversion Status by Phase

### Phase 1 — Opportunity and Project Intake

| SOP | Title | Phase/Lifecycle | Conversion Status | Service Path | Notes |
|-----|-------|----------------|-------------------|-------------|-------|
| SOP 01 | Opportunity Intake | Intake | ⬜ | — | Low priority; CRM-driven |
| SOP 02 | Project Intake | Intake | ⬜ | — | WF-001 partially covers |
| SOP 03 | File Organization | Intake | ⬜ | — | Drive folder structure |

### Phase 2 — Plan Review and Project Understanding

| SOP | Title | Phase/Lifecycle | Conversion Status | Service Path | Notes |
|-----|-------|----------------|-------------------|-------------|-------|
| SOP 04 | Plan Review | Preconstruction | 🔵 PHASE F BUILT | `services/sop_execution/sop_04_plan_review/` | 4-layer; 6 endpoints; smoke-tested |
| SOP 05 | Construction Narrative | Preconstruction | 🔵 PHASE F BUILT | `services/sop_execution/sop_05_construction_narrative/` | 4-layer; 8 endpoints |
| SOP 06 | Missing Information / Risk Log | Preconstruction | 🔵 PHASE F BUILT | `services/sop_execution/sop_06_missing_info/` | 4-layer; 8 endpoints; smoke-tested |

### Phase 3 — Budgeting and Cost Analysis

| SOP | Title | Phase/Lifecycle | Conversion Status | Service Path | Notes |
|-----|-------|----------------|-------------------|-------------|-------|
| SOP 07 | ROM Budget | Estimating | 🔵 PHASE F BUILT | `services/sop_execution/sop_07_rom_budget/` | 4-layer; 7 endpoints; smoke-tested; Gate 07-C ($500k threshold) |
| SOP 08 | Historical Cost Database | Estimating | 🔵 PHASE F BUILT | `services/sop_execution/sop_08_historical_cost/` | 4-layer; 5 endpoints; smoke-tested |
| SOP 09 | Budget Review | Estimating | 🔵 PHASE F BUILT | `services/sop_execution/sop_09_budget_review/` | 4-layer; 7 endpoints; smoke-tested; Gate 09-C ($500k threshold) |
| SOP 10 | Allowances / Alternates / Exclusions | Estimating | 🔵 PHASE E BUILT | `services/sop_execution/sop_10_allowances/` | 4-layer; 10 endpoints; smoke-tested |

### Phase 4 — Bid Strategy and Subcontractor Outreach

| SOP | Title | Phase/Lifecycle | Conversion Status | Service Path | Notes |
|-----|-------|----------------|-------------------|-------------|-------|
| SOP 11 | Bid Package | Preconstruction / Bidding | ✅ PHASE D TESTED | `services/sop_execution/sop_11_bid_package/` | 16 tests PASS (10 unit + 6 integration); 1 conditional (vendor Qdrant) |
| SOP 12 | Subcontractor CRM | Bidding | 🔵 PHASE G BUILT | `services/sop_execution/sop_12_sub_crm/` | 4-layer; 8 endpoints; MIN_BIDDERS=3 enforced; smoke-tested |
| SOP 13 | Bid Distribution | Bidding | 🔵 PHASE E BUILT | `services/sop_execution/sop_13_bid_distribution/` | 4-layer; 7 endpoints; smoke-tested |
| SOP 14 | Bid Follow-Up | Bidding | 🔵 PHASE E BUILT | `services/sop_execution/sop_14_bid_followup/` | 4-layer; 7 endpoints |

### Phase 5 — Bid Leveling and Buyout

| SOP | Title | Phase/Lifecycle | Conversion Status | Service Path | Notes |
|-----|-------|----------------|-------------------|-------------|-------|
| SOP 15 | Bid Leveling | Bidding / Buyout | ✅ PHASE D TESTED | `services/sop_execution/sop_15_bid_leveling/` | 13 tests PASS (8 unit + 5 integration) |
| SOP 16 | Buyout | Buyout | 🔵 PHASE E BUILT | `services/sop_execution/sop_16_buyout/` | 4-layer; 8 endpoints; smoke-tested |

### Phase 6 — Schedule Development

| SOP | Title | Phase/Lifecycle | Conversion Status | Service Path | Notes |
|-----|-------|----------------|-------------------|-------------|-------|
| SOP 17 | Project Schedule | Schedule | 🔵 PHASE H BUILT | `services/sop_execution/sop_17_project_schedule/` | 4-layer; 7 endpoints; AI schedule generation; milestone chain |
| SOP 18 | Long-Lead Item | Procurement | 🔵 PHASE H BUILT | `services/sop_execution/sop_18_long_lead/` | 4-layer; 6 endpoints; AI item identification; risk levels |

### Phase 7 — Contract, Compliance, and Project Setup

| SOP | Title | Phase/Lifecycle | Conversion Status | Service Path | Notes |
|-----|-------|----------------|-------------------|-------------|-------|
| SOP 19 | Subcontractor Agreement | Buyout / Contract | 🔵 PHASE G BUILT | `services/sop_execution/sop_19_subcontract_agreement/` | 4-layer; 10 endpoints; Gate 19-C; 7 CONTRACT_SECTIONS; HCI insurance minimums enforced; smoke-tested |
| SOP 20 | Contract Setup | Contract | 🔵 PHASE H BUILT | `services/sop_execution/sop_20_contract_setup/` | 4-layer; 6 endpoints; AI checklist; pending-item gate |
| SOP 21 | Compliance | Contract | 🔵 PHASE H BUILT | `services/sop_execution/sop_21_compliance/` | 4-layer; 6 endpoints; AI permit ID; clear-to-build gate |
| SOP 22 | COI / W-9 / Lien Waiver | Contract / Compliance | 🔵 PHASE H BUILT | `services/sop_execution/sop_22_coi_w9_lien/` | 4-layer; 7 endpoints; COI verify vs HCI minimums |
| SOP 23 | Project Startup | Contract / Setup | 🔵 PHASE H BUILT | `services/sop_execution/sop_23_project_startup/` | 4-layer; 6 endpoints; ready-to-build gate; feeds SOP 24 |

### Phase 8 — Field Execution

| SOP | Title | Phase/Lifecycle | Conversion Status | Service Path | Notes |
|-----|-------|----------------|-------------------|-------------|-------|
| SOP 24 | Superintendent Daily Dashboard | Field | 🔵 PHASE H BUILT | `services/sop_execution/sop_24_super_dashboard/` | 4-layer; 4 endpoints; daily metric updates; AI brief |
| SOP 25 | Daily Log | Field | 🔵 PHASE H BUILT | `services/sop_execution/sop_25_daily_log/` | 4-layer; 5 endpoints; AI risk analysis; PM notifications |
| SOP 26 | Field Coordination | Field | 🔵 PHASE H BUILT | `services/sop_execution/sop_26_field_coordination/` | 4-layer; 5 endpoints; AI RFI draft from lessons-learned |

### Phase 9 — Quality Control

| SOP | Title | Phase/Lifecycle | Conversion Status | Service Path | Notes |
|-----|-------|----------------|-------------------|-------------|-------|
| SOP 27 | Quality Control | Field / QC | 🔵 PHASE H BUILT | `services/sop_execution/sop_27_quality_control/` | 4-layer; 4 endpoints; AI QC checklist; CRITICAL failure SC-03 |
| SOP 28 | QC Detail Card | Field / QC | 🔵 PHASE H BUILT | `services/sop_execution/sop_28_qc_detail_card/` | 4-layer; 5 endpoints; AI detail card per trade; hold points |
| SOP 29 | Safety | Field / Safety | 🔵 PHASE H BUILT | `services/sop_execution/sop_29_safety/` | 4-layer; 5 endpoints; SC-03 on CRITICAL uncontrolled hazard |
| SOP 30 | Inspection | Field / Compliance | 🔵 PHASE H BUILT | `services/sop_execution/sop_30_inspection/` | 4-layer; 4 endpoints; AI prep checklist; SC-03 on FAIL |

### Phase 10 — Change Management

| SOP | Title | Phase/Lifecycle | Conversion Status | Service Path | Notes |
|-----|-------|----------------|-------------------|-------------|-------|
| SOP 31 | Change Order | Change Management | ⬜ | — | |
| SOP 32 | RFI | Change Management | ⬜ | — | rfis table exists |
| SOP 33 | Schedule Impact | Change Management | ⬜ | — | schedule-intelligence covers partial |

### Phase 11 — Client and Design Team Communication

| SOP | Title | Phase/Lifecycle | Conversion Status | Service Path | Notes |
|-----|-------|----------------|-------------------|-------------|-------|
| SOP 34 | Client Communication | Communication | ⬜ | — | |
| SOP 35 | Meeting Notes | Communication | ⬜ | — | WF-002 covers meeting intelligence |
| SOP 36 | Decision Log | Communication | ⬜ | — | decision_intelligence service planned |
| SOP 37 | Weekly Update | Communication | ⬜ | — | WF-REPORT-WEEKLY covers |
| SOP 38 | Photo Documentation | Field / Documentation | ⬜ | — | photo_memory Qdrant collection exists |

### Phase 12 — Closeout and Turnover

| SOP | Title | Phase/Lifecycle | Conversion Status | Service Path | Notes |
|-----|-------|----------------|-------------------|-------------|-------|
| SOP 39 | Punch List | Closeout | ⬜ | — | |
| SOP 40 | Owner Manual / Closeout | Closeout | ⬜ | — | |
| SOP 41 | Warranty | Closeout | ⬜ | — | |
| SOP 42 | Post-Project Review | Closeout / Learning | ⬜ | — | lessons-learned service covers partial |

---

## Summary

| Status | Count |
|--------|-------|
| ✅ Complete (Phase D tested) | 2 (SOP 11, SOP 15) |
| 🔵 Built (smoke-tested, not yet full-test-suite) | 25 (SOP 04–30 excl. 11+15) |
| ⬜ Not Started | 15 (SOP 01–03, 31–42) |
| ❌ Blocked | 0 |
| **Total** | **42** |

---

## Existing Service Overlaps (no duplication)

The following existing HCI AI services already cover SOP logic — the SOP Execution Layer builds on top of them:

| Existing Service | Related SOP(s) |
|-----------------|---------------|
| `bid-intelligence` | SOP 11, 15, 16 |
| `vendor-intelligence` | SOP 12 |
| `schedule-intelligence` | SOP 17, 33 |
| `procurement` | SOP 18 |
| `lessons-learned` | SOP 42 |
| `historical-cost` | SOP 08 |
| `risk-intelligence` | SOP 06 |
| WF-002 Meeting Intelligence | SOP 35 |
| WF-SUPER Daily Log | SOP 24, 25 |
| WF-PM / WF-PM-W | SOP 37 |

---

*Last updated: 2026-06-25 | Phase G complete — 14 SOPs active. Next: Phase H (SOP 17, 18, 20–23 or test suite expansion)*

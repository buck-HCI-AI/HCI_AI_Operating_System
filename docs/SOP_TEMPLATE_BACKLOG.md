# HCI AI — SOP Template Backlog

**Version:** 1.0 | **Date:** 2026-06-25 | **Directive:** HCI_AI_SOP_to_Software_Execution_Layer_Master_Directive_v1.0  
**Layer:** Layer 4 — Templates and Required Data Fields

This document catalogs all templates required for SOP conversions. Templates include: input checklists, output forms, bid forms, leveling sheets, award memos, and approval records.

---

## Template Status Key

| Symbol | Meaning |
|--------|---------|
| ✅ | Template defined and implemented |
| 🔵 | Template defined in this doc; not yet coded |
| ⬜ | Template needed; not yet defined |

---

## SOP 11 — Bid Package Templates

### Template 11-A: Input Checklist

**Purpose:** PM confirms all required source documents are on hand before work begins.  
**Used At:** SOP 11 status → In Progress (Gate check)  
**Stored In:** `sop_inputs` table, input_type = "checklist"

| # | Required Input | Confirmed? | Date Confirmed | Notes |
|---|---------------|-----------|----------------|-------|
| 1 | Architectural drawings (current revision noted) | ☐ | | |
| 2 | Structural drawings (or N/A) | ☐ | | |
| 3 | MEP drawings (or N/A) | ☐ | | |
| 4 | Project specifications — all applicable divisions | ☐ | | |
| 5 | Soils report (or N/A) | ☐ | | |
| 6 | Hazmat assessment (or N/A) | ☐ | | |
| 7 | SOP 04 Plan Review — Approved | ☐ | | |
| 8 | SOP 05 Construction Narrative — Complete | ☐ | | |
| 9 | SOP 06 Risk Log — Reviewed | ☐ | | |
| 10 | SOP 10 Allowances/Alternates — Defined | ☐ | | |
| 11 | SOP 09 Budget — Approved | ☐ | | |

**Confirmed By:** ___________________ | **Date:** ___________

Status: 🔵

---

### Template 11-B: Scope Section Form (per trade)

**Purpose:** Structured scope section for each trade included in the bid package.  
**Used At:** Estimator fills during In Progress; AI reviews during AI Drafted.  
**Stored In:** `sop_outputs` table, output_type = "scope_section" (JSONB)

```
Trade Name: ___________________________
Trade Code (CSI): _______________
Scope Description:
  [Plain English description of what is included — specific, not vague]

Drawings Referenced:
  - [Drawing number] Rev [__] dated [__]
  - [Drawing number] Rev [__] dated [__]

Specifications Referenced:
  - Section [____] — [title]
  - Section [____] — [title]

Allowances:
  - [Item]: $[Amount] — Basis: [description]

Alternates:
  - Alt #[__]: [description] — Bid Form Line [__]

Explicit Exclusions:
  - [Item explicitly NOT included]
  - [Item explicitly NOT included]

Special Requirements:
  - Prevailing wage: Yes / No
  - Certified payroll: Yes / No
  - Insurance: [limits if non-standard]

AI Gap Flags (filled by AI review):
  - [Flag | severity | recommendation]
```

Status: 🔵

---

### Template 11-C: Buck Approval Record (Gate 11-C)

**Purpose:** Documents Buck's approval of the bid package for issue.  
**Used At:** Gate 11-C — required before status → Issued  
**Stored In:** `sop_approval_gates` table

```
Gate ID: AG-11-C
SOP 11 Instance: _______________
Project: _______________
Bid Package Date: _______________
Trades Covered: _______________
Review Summary: [PM's summary of what was reviewed]
Buck's Decision: APPROVED / RETURNED FOR REVISION
Conditions: [Any conditions on approval]
Approved By: Buck Adams
Timestamp: _______________
Method: in-system / acknowledged [describe]
```

Status: 🔵

---

## SOP 15 — Bid Leveling Templates

### Template 15-A: Bid Receipt Log

**Purpose:** Records all bids received with date, amount, and responsiveness determination.  
**Used At:** Estimator fills as bids arrive; input gate check uses this.  
**Stored In:** `sop_inputs` table per bidder

| Bidder | Bid Amount | Received Date | On Time? | Responsive? | Notes |
|--------|-----------|--------------|---------|------------|-------|
| | | | | | |
| | | | | | |
| | | | | | |

Minimum responsive bids: 3 | Total received: ___ | Responsive: ___

Status: 🔵

---

### Template 15-B: Leveling Sheet (per trade)

**Purpose:** Normalized comparison of all received bids on an equal scope basis.  
**Used At:** AI generates; estimator reviews; PM confirms; Buck decides.  
**Stored In:** `sop_outputs` (JSONB + MinIO PDF)

```
Project: _______________
Trade: _______________
Bid Close Date: _______________
Leveling Date: _______________
Estimator: _______________

BASE BIDS:
  Bidder 1: $_______________
  Bidder 2: $_______________
  Bidder 3: $_______________

ADJUSTMENTS:
  Bidder 1:
    + [Item excluded from scope, HCI must cover]: $___
    - [Item included, not in scope]: $___
    Adjusted Total: $_______________
  Bidder 2: [same format]
  Bidder 3: [same format]

NORMALIZED COMPARISON:
  | Bidder | Base Bid | Adjustments | Adjusted Total | Diff from Low |
  
RISK FLAGS:
  Bidder 1: [flags]
  Bidder 2: [flags]
  Bidder 3: [flags]

PRIOR PERFORMANCE:
  Bidder 1: [score, projects, notes]
  Bidder 2: [score, projects, notes]
  Bidder 3: [score, projects, notes]

AI RECOMMENDATION: [bidder, amount, rationale, conditions]
  Mark: AI DRAFT — BUCK MAKES AWARD DECISION

ESTIMATOR REVIEW:
  Confirming AI recommendation: Yes / No / Modified
  If modified: [reason and change]
  PM Confirmed: ____________ Date: ________
```

Status: 🔵

---

### Template 15-C: Buck Award Decision Record (Gate 15-C)

**Purpose:** Documents Buck's award decision — the definitive record of who was selected, why, and at what price.  
**Used At:** Gate 15-C — required before status → Approved  
**Stored In:** `sop_approval_gates` table + `decision_records` table

```
Gate ID: AG-15-C
SOP 15 Instance: _______________
Project: _______________
Trade: _______________
Bid Close Date: _______________
Leveling Review Date: _______________

AWARD DECISION:
  Awarded To: _______________
  Basis of Award: _______________  [price / price + scope / price + risk + performance]
  Award Amount: $_______________
  Scope Basis: [what was included/excluded in the award]
  Conditions on Award: [anything sub must confirm before PO/contract issued]

ALTERNATIVES CONSIDERED:
  [Brief note on other bidders and why not selected]

RISKS ACCEPTED:
  [Any known risk in the awarded bidder that Buck accepted with this decision]

Decided By: Buck Adams
Timestamp: _______________
Method: in-system / acknowledged

— This award decision becomes a Decision Intelligence record —
```

Status: 🔵

---

### Template 15-D: Award Memo

**Purpose:** Written award memo issued to the selected sub.  
**Used At:** After Gate 15-C; before handoff to SOP 16  
**Stored In:** MinIO (PDF)  
**Approved By:** PM issues after Buck's Gate 15-C record is in system

```
[HCI Letterhead]

Date: _______________
To: [Sub Name, contact]
Re: Award — [Project Name] — [Trade] — Contract No. [___]

Dear [Sub name]:

We are pleased to inform you that Hendrickson Construction intends to award 
[trade name] scope to [sub name] for [project name].

AWARD BASIS:
  Scope: Per SOP 11 bid package dated [__] and your bid dated [__]
  Base Amount: $_______________
  Inclusions: [from bid and leveling]
  Exclusions: [from bid and leveling]
  
CONTRACT:
  HCI standard subcontract agreement will be forwarded for signature
  COI and W-9 required before contract execution

Please confirm receipt and intent to proceed.

[PM name and contact]
```

Status: 🔵

---

## Template Backlog — Future SOPs

| SOP | Templates Needed | Priority |
|-----|-----------------|---------|
| SOP 16 — Buyout | Award memo (alternate version), buyout tracker | Phase E |
| SOP 19 — Subcontract Agreement | Subcontract checklist, executed contract tracker | Phase G |
| SOP 31 — Change Order | CO form, CO tracker, budget adjustment record | Phase E |
| SOP 32 — RFI | RFI form, response log | Phase E |
| SOP 39 — Punch List | Punch item form, sub notification, verification record | Phase F |
| SOP 42 — Post-Project Review | Review form, lessons-learned record | Phase F |

---

*Standard: `docs/SOP_2_0_CONVERSION_STANDARD.md`*  
*Data fields: `docs/SOP_DATA_FIELD_DICTIONARY.md`*

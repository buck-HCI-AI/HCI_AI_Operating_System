# Field Readiness Gaps
*HCI AI Operating System | Source: HCI-OR-001 | 2026-06-27*
*Question: Can a Superintendent use this all day? If not — what's missing?*

---

## Operational Readiness Review — Field Perspective

The ORR-001 definition: "Can the Superintendent use the platform all day?"

### Current Field-Facing Capabilities (Live)

| Capability | Status | Source |
|-----------|--------|--------|
| Today's schedule + tasks | ✅ LIVE | Houzz (if extracted) / manual |
| Safety topic of the day | ✅ LIVE | HCI AI OS (SS Console) |
| Crew list | ✅ LIVE | HCI AI OS |
| Daily log creation | ✅ LIVE | HCI AI OS |
| Blockers / open issues | ✅ LIVE | Project Brain |
| Project health | ✅ LIVE | Project Brain |

### Field Gaps (What SS Cannot Do Today)

| Gap | Impact | Root Cause | Fix Required |
|-----|--------|-----------|-------------|
| Photo documentation | MEDIUM | Houzz Files not integrated | Houzz browser extraction + API endpoint |
| Delivery tracking (POs) | HIGH | POs unused in Houzz Pro | Activate Houzz POs + sync to HCI AI OS |
| Punchlist management | HIGH | No punchlist in HCI AI OS | AI punchlist generation (BTW-7) |
| Change order visibility | HIGH | COs not in Houzz Pro | Activate Houzz COs |
| Selections status | HIGH | Selection boards unused | Activate + sync to SS console |
| Material tracking | HIGH | POs unused | Activate Houzz POs |
| Inspection scheduling | MEDIUM | No inspection module integration | Map Houzz schedule tasks to inspection types |
| Voice notes | LOW | Endpoint not built | Transcription → daily log injection (BTW-7) |
| Real-time budget by trade | HIGH | Houzz Budget unused | Activate Budget module |
| Sub contact directory | MEDIUM | HubSpot not pushed to SS view | Expose HubSpot contacts in SS console |

---

## ORR-001 Field Readiness Score

| Domain | Max | Current | Gap | What Unlocks It |
|--------|-----|---------|-----|-----------------|
| Daily Priorities | 10 | 8 | -2 | Houzz schedule data flowing |
| Safety & Compliance | 10 | 9 | -1 | COI automation |
| Documentation | 10 | 6 | -4 | Photo integration, voice notes |
| Procurement visibility | 10 | 2 | -8 | Houzz POs, material tracking |
| Change order tracking | 10 | 1 | -9 | Houzz COs activated |
| Client selections status | 10 | 0 | -10 | Houzz Selections activated |
| Budget visibility | 10 | 2 | -8 | Houzz Budget activated |
| Communication tools | 10 | 5 | -5 | HubSpot contacts in SS view |
| **TOTAL** | **80** | **33** | **-47** | |

**Current Field Score: 33/80 (41%)** — Not ready for all-day SS use.
**Target for ORR-001 Pass: 64/80 (80%)**

---

## Path to ORR-001 (Field Readiness Pass)

```
STEP 1: Houzz Browser Extraction (15 min × 3 projects) — BUCK
  Unlocks: schedule, budget, POs, COs, files → 33→50 score (+17)

STEP 2: Houzz Budget + Schedule Activation (Phase 1)
  Unlocks: budget visibility, procurement tracking → +8

STEP 3: Change Order + Punchlist AI (Phase 2)
  Unlocks: CO tracking, closeout tools → +10

STEP 4: BTW-7 Field Enhancements
  Unlocks: photos, delivery, inspection, voice notes → +6

TARGET: 33 + 17 + 8 + 10 + 6 = 74/80 (92%) → ORR-001 PASS
```

---

## PM Readiness Score

| Domain | Max | Current | Gap | What Unlocks It |
|--------|-----|---------|-----|-----------------|
| Project health view | 10 | 9 | -1 | Houzz data |
| Budget management | 10 | 3 | -7 | Houzz Budget |
| Schedule management | 10 | 2 | -8 | Houzz Schedule |
| Procurement tracking | 10 | 5 | -5 | Houzz POs, BTW-8 |
| Client communications | 10 | 7 | -3 | BTW-8 ✅ live |
| Change order tracking | 10 | 1 | -9 | Houzz COs |
| Action list (ranked) | 10 | 8 | -2 | BTW-8 ✅ live |
| Weekly reporting | 10 | 7 | -3 | BTW-6 (next) |
| **TOTAL** | **80** | **42** | **-38** | |

**Current PM Score: 42/80 (52%)**
**Target for ORR-001 Pass: 64/80 (80%)**
**Boosted by BTW-8 (client comms + ranked actions): 42 → 47**

---

## Executive Readiness Score

| Domain | Max | Current | Gap | What Unlocks It |
|--------|-----|---------|-----|-----------------|
| Company health view | 10 | 9 | -1 | Full Houzz data |
| Project profitability | 10 | 1 | -9 | Houzz Budget |
| Pipeline health | 10 | 8 | -2 | HubSpot dashboards |
| Approval queue | 10 | 9 | -1 | Executive inbox live |
| Weekly summary | 10 | 5 | -5 | BTW-6 (next) |
| COI + compliance | 10 | 2 | -8 | HS-02 COI engine |
| AI recommendations | 10 | 8 | -2 | Predictive engine live |
| Sub performance | 10 | 2 | -8 | AI sub scoring |
| **TOTAL** | **80** | **44** | **-36** | |

**Current Executive Score: 44/80 (55%)**
**Target for ORR-001 Pass: 64/80 (80%)**

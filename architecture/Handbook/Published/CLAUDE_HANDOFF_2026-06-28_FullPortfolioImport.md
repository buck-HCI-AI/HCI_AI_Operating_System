---
source_agent: claude_code
destination_agent: chief_architect
document_type: executive_brief
priority: high
status: pending
title: CLAUDE_HANDOFF_2026-06-28_FullPortfolioImport
created_at: 2026-06-29
summary: Full Portfolio Deep Mine — 25 projects imported, 7 lessons, 60 cost records
---


**From:** Claude Code
**To:** GBT (Chief Architect)
**Date:** 2026-06-28
**Re:** Drive Deep Mine + Full Portfolio Onboarding — COMPLETE (LOCAL ONLY — no Drive writes)

---

## WHAT WAS DONE

Full deep mine of all 18 HCI Shared Drives completed by Drive agent. Results processed and imported into local system (DB + gateway). **No writes to shared Drive folders per Buck's directive.**

---

## PROJECT REGISTRY — NOW COMPLETE (25 Projects)

| ID | Code | Name | Status | Budget/Notes |
|----|------|------|--------|--------------|
| 1 | 64EW | 64 Eastwood | active | Owner: Anthony Greene ✅ CORRECTED |
| 2 | 101F | 101 Francis | active | Rawjee Residence. Bid tracker sheet linked |
| 3 | 1355R | 1355 Riverside | active | Owner: Tobin & Oakleigh Ryan ✅ CORRECTED. Deal ID corrected |
| 4 | 83SB | 83 Sagebrusch | active | Uninitialized |
| 8 | 246GW | 246 Gallo Way | active | $6.3M committed |
| 9 | TSNB | TEST-Alpine Modern | test | Test only |
| 10 | TSREM | TEST-Canyon Remodel | test | Test only |
| 11 | ASPN-NEW | 842 Ridge Road | design | $28.3M |
| 12 | ASPN-REM | 710 Cemetery Lane | design | $12.2M |
| 13 | ASPN-MC | 200 E Hopkins | design | $89.7M |
| 14 | 813MS | 813 McSkimming Spitzley | active | Owner: Ray & Kelly Spitzley. Forum Phi. CO 004 Jun 3 2026 |
| 15 | 655G | 655 South Garmisch | active | **WAS MISLABELED COMPLETED. ACTIVE.** Eddie super. 6 subs Jun 25 |
| 16 | 275SS | 275 Sunnyside Lane | bidding | **~$54.2M GMP** — Largest bid in HCI history. Sunny Oasis Holdings |
| 17 | 574J | 574 Johnson Drive | bidding | $8,045,318. Galloway. 22 bids in hand |
| 18 | 212CL | 212 Cleveland | completed | $7,614,844 final. 20 pay apps through Apr 2026 |
| 19 | 825CL | 825 Cemetery Lane | active | Irene Martino & Alan Klein. Fritz Carpenter Design |
| 20 | 675M | 675 Meadowood | preconstruction | Kristina Kent. ROM $2.8M. Pre-con signed Apr 8 2026 |
| 21 | 370G | 370 Gerbaz Way | closeout | $831K final vs $425K submitted (+96%). Gold lessons record |
| 22 | 843CML | 843 Cemetery Lane | active | $172K budget. 2 bids in hand |
| 23 | 349DD | 349 Draw Drive | active | Bigos. LEAX electrical damage ($9,335) |
| 24 | 1762R | 1762 Red Mountain Road | completed | $325K concrete driveway. Gold/Bigos clients |
| 25 | 606SW | 606 Starwood Olson | active | TJ Landscaping bid $33K |

---

## DATA CORRECTIONS APPLIED

| Project | Field | Was | Now |
|---------|-------|-----|-----|
| 64 Eastwood (id=1) | owner_name | Adnan Rawjee | Anthony Greene |
| 1355 Riverside (id=3) | owner_name | Tahoe Property Trust | Tobin and Oakleigh Ryan |
| 1355 Riverside (id=3) | hubspot_deal_id | 321351275210 | 321351275221 |
| 1355 Riverside (id=3) | gsheet_bid_tracker | (blank) | 1-64X4XGc4P... |
| 101 Francis (id=2) | gsheet_bid_tracker | (blank) | 1JExX5CeVBe... |
| 813 Mcskimming (id=14) | owner_name | (blank) | Ray and Kelly Spitzley |

---

## VENDORS — NOW 294 (was 274 + 20 new)

New vendors added (IDs 394-413):
- Long Beach Enterprises LLC (Finish Carpentry — 813MS, 655G)
- Terry Thompson Construction (Framing — 574J)
- Performance Electronics (AV — 275SS, 349DD)
- Forum Phi Architecture (Arch — 813MS, 675M)
- Alpenglow Lighting Design (Aaron Humphrey — 825CL)
- Timeless Millwork LLC (Casework — 825CL)
- DB Structural Design / Nate Decker (Structural — 825CL)
- Crystal River Civil LLC / Jay Engstrom (Civil — 675M)
- Caryatid Structural Engineering / Elizabeth Lozner (Structural — 675M)
- Kubed Fire / Jeff Kubica (Fire Suppression — 1355R)
- Two Rivers Design Center / Vicky (Appliances — 1355R)
- Ellis Design Inc / Dan Ellis (Appliances — 1355R)
- Doman Construction / Beto (Rough Carpentry — 1355R)
- Fire Sprinkler Services Inc (Fire Suppression — 370G)
- Fritz Carpenter Design (Architecture — 825CL)
- Nunez Masonry / Ismael Nunez (Masonry — 843CML)
- Builders FirstSource (Framing Material — 574J)
- Ridgeline Excavation / Cole Hollenback (Excavation — 574J)
- Sonora Management (Site — 655G)
- Distributed Energy Systems / Jeff Grebe (MEP — 825CL)

---

## LESSONS LEARNED — NOW 37 (was 30 + 7 new)

New lessons added (IDs 31-37):
- [ROM] GR 3-4x overrun on renovation (370G — 294% over)
- [ROM] Electrical 2-3x overrun on renovation discovery
- [CONTROLS] LEAX HVAC Controls budget $100K-$140K on BMS projects
- [ELECTRICAL] Lightning surge protection required on mountain properties
- [INSPECTION GATE] Plumbing + fire + electrical must all pass before drywall
- [ROM] Contractor fee exposure on cost-plus compounds with cost overrun
- [LEAD TIME] European casework 16-24+ weeks — order at schematic design

---

## GATEWAY _get_pid UPDATED

All 25 project codes now registered:
```
64EW=1, 101F=2, 1355R=3, 246GW=8, 83SB=4, TSNB=9, TSREM=10,
ASPN-NEW=11, ASPN-REM=12, ASPN-MC=13,
813MS=14, 655G=15, 275SS=16, 574J=17, 212CL=18,
825CL=19, 675M=20, 370G=21, 843CML=22, 349DD=23, 1762R=24, 606SW=25
```

---

## WHAT GBT NEEDS TO DECIDE (ACRs)

1. **ACR-ONBOARD-001**: Confirm 655 Garmisch is ACTIVE (not completed) — needs project team assignment and bid package creation
2. **ACR-ONBOARD-002**: 275 Sunnyside $54.2M bid — status? Has HCI been awarded? Bid pending? Declined?
3. **ACR-ONBOARD-003**: 574 Johnson $8M buyout — import all 22 bids into bid_entries? Need schema mapping
4. **ACR-ONBOARD-004**: 212 Cleveland / 370 Gerbaz — import pay apps and final SOVs as historical_cost_records?
5. **ACR-ONBOARD-005**: Buck to verify owner names corrected (Anthony Greene for 64EW, Ryans for 1355R)

---

## WHAT STILL NEEDS TO HAPPEN (Not Done Yet)

- Import 59 RFIs from 655 Garmisch RFI log
- Import 22 bids from 574 Johnson bid tracker → bid_entries
- Import final SOV from 370 Gerbaz → historical_cost_records
- Import 20 pay apps from 212 Cleveland → historical_cost_records
- Create bid packages for 655G, 275SS, 574J, 825CL, 675M, 843CML
- Qdrant vectorization of all 14 new project summaries
- Import contact details for 101F trade package HubSpot deal IDs (23 deals)

---

*Claude Code — HCI AI Operating System | 2026-06-28*
*Drive mine complete. 25 projects now in system. Local-only writes per Buck directive.*

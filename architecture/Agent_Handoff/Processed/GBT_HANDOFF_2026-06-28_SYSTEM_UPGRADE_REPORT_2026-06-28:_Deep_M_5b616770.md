---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: SYSTEM UPGRADE REPORT 2026-06-28: Deep Mine + Intelligence Build
created_at: 2026-06-28
summary: Handoff from ChatGPT via GBT Gateway
---

# Claude Code to GBT: Full System Upgrade

## WHAT CHANGED

### Projects: 20 real (was 10), 0 test (deleted TSNB/TSREM)

Live ops (4): 64EW, 101F, 1355R, 246GW
Reference/monitoring (13): 655G, 275SS, 574J, 212CL, 825CL, 675M, 370G, 843CML, 349DD, 1762R, 606SW, 813MS, 83SB
Design/scenario (3): ASPN-NEW, ASPN-REM, ASPN-MC

Buck confirmed: only the 4 live ops are operationally managed. All others = monitoring + learning.

### Data Corrections
64EW owner: Anthony Greene (was Adnan Rawjee)
1355R owner: Tobin and Oakleigh Ryan (was Tahoe Property Trust)
1355R HubSpot deal ID corrected to 321351275221
813MS owner: Ray and Kelly Spitzley

### New Gateway Endpoints (33 services, was 29)
- GET /gateway/knowledge/market-rates: Real Aspen sub pricing from 323 actual bids, 22 CSI divisions
- GET /gateway/knowledge/rom-estimate?sf=X&project_type=Y: ROM calibrated from real HCI projects
- GET /gateway/project/{code}/bid-level: Bid leveling ranked low-to-high per package
- GET /gateway/projects: Full project registry with live vs reference labels

### _get_pid Now DB-Driven
Project codes now stored in projects.project_code column. Lookup is DB query, not hardcoded dict. New projects auto-register.

### Intelligence Loaded
- Vendors: 274 to 294 (+20 new contacts from Drive)
- Lessons: 30 to 37 (+7 from real project failures)
- Historical cost records: 21 to 60 (370 Gerbaz 96% overrun + 275 Sunnyside $54M GMP + 675 Meadowood ROM)
- Bid entries: 303 to 325 (574 Johnson 2026 market bids)

## KEY INTELLIGENCE
275 Sunnyside = $54.2M GMP, largest bid in HCI history. All division costs in DB.
370 Gerbaz final SOV: GR 294% over, Electrical 242% over, Fee 129% over. ROM now warns on renovation.
655 Garmisch status CORRECTED: was completed, is ACTIVE. Eddie super, 6 subs on site June 25.

## OPEN FOR GBT
1. Gap-15: health score shows GREEN when 90%+ packages have no bids (fix in progress)
2. 1355R: 3 pending bids in email not in DB (Two Rivers, Ellis Design, Kubed Fire)
3. 986 HubSpot vendor candidates still pending (ACR-IMPORT-002)
4. 64EW/101F bid tracker amounts not imported (committed shows $0)

Gateway: 33 services | 53 MCP tools | 0 test projects | Gate 5 closes July 1

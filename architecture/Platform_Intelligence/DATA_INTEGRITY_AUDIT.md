# HCI Data Integrity Audit
**Date:** 2026-06-28 | **Pre-WF-009 Baseline**

## Record Counts
```
bid_packages      | 119
 houzz_projects    | 3
 hubspot_companies | 1183
 hubspot_contacts  | 1311
 hubspot_deals     | 307
 missions          | 15
 projects          | 4
 vendors           | 392
```

## Integrity Check Results
| Check | Result | Status |
|---|---|---|
| Duplicate projects | 0 | ✅ CLEAN |
| Duplicate HubSpot deals | 0 | ✅ CLEAN |
| Duplicate HubSpot contacts | 0 | ✅ CLEAN |
| Duplicate HubSpot companies | 0 | ✅ CLEAN |
| Duplicate vendor names | 67 | ⚠️ ISSUE (67) |
| Houzz tasks populated | 0 | ⚠️ EMPTY — Houzz extraction needed |
| Houzz schedule populated | 0 | ⚠️ EMPTY — Houzz extraction needed |
| Houzz POs populated | 0 | ⚠️ EMPTY — Houzz extraction needed |
| RFIs populated | 0 | ⚠️ EMPTY — Houzz extraction needed |
| schedule_variance table | YES | ✅ |

## Duplicate Vendor Details
```
Sunny Oasis Holdings Limited (Melco) | 10
 Custom Structural Steel              |  6
 Ajax Mechanical Services             |  6
 City of Aspen                        |  6
 Savage Excavation                    |  5
 Pitkin County Community Development  |  5
 R & H Mechanical                     |  4
 Castlewood Doors                     |  4
 Rader Engineering, Inc               |  4
 Kumar & Associates, Inc.             |  4
 Epic Custom Glass, LLC               |  3
 Architectural Windows & Doors        |  3
 ProGuard                             |  3
 NanoLumens                           |  3
 The Fireplace Company                |  3
```

## WF-009 Schedule Intelligence Readiness
| Requirement | Status |
|---|---|
| Projects table clean | ✅ |
| HubSpot sync clean | ✅ |
| Houzz tasks populated | ⚠️ Awaiting extraction |
| schedule_variance table | ⚠️ Not yet created |
| Vendor deduplication | ⚠️ 67 duplicates pending Buck approval |

**WF-009 Status: NOT READY** — 3 blockers above must resolve first.

## Cleanup Recommendations
1. **Vendor dedup** (67 duplicate company names) — generate merge report, require Buck approval before merging
2. **Houzz data** — run Browser extraction (15 min × 3 projects) to populate tasks, schedule, POs
3. **schedule_variance table** — will be created by WF-009 migration when ready
4. **No other destructive actions required** — HubSpot records are clean

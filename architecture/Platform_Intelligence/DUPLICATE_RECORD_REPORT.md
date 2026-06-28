# Duplicate Record Report
**Date:** 2026-06-28 | **Pre-WF-009 Cleanup Analysis**

## Summary
| System | Duplicates | Action Required |
|---|---|---|
| Vendors (DB) | 67 name duplicates | Buck approval to merge |
| HubSpot Contacts | 0 | Clean ✅ |
| HubSpot Companies | 0 | Clean ✅ |
| HubSpot Deals | 0 | Clean ✅ |
| Projects | 0 | Clean ✅ |

## Vendor Duplicates (Top 25 by Count)
```
Sunny Oasis Holdings Limited (Melco) | 10
 Ajax Mechanical Services             |  6
 Custom Structural Steel              |  6
 City of Aspen                        |  6
 Savage Excavation                    |  5
 Pitkin County Community Development  |  5
 R & H Mechanical                     |  4
 Kumar & Associates, Inc.             |  4
 Castlewood Doors                     |  4
 Rader Engineering, Inc               |  4
 Architectural Windows & Doors        |  3
 Valley Lumber                        |  3
 Integrity Fire Safety Services, LLC  |  3
 NanoLumens                           |  3
 ProGuard Protection Services Inc     |  3
 Sopris Mechanical                    |  3
 SnowCap Decorative Hardware LLC      |  3
 Dynamic Fenestration                 |  3
 The Fireplace Company                |  3
 ProGuard                             |  3
 Morning Star Elevator                |  3
 Epic Custom Glass, LLC               |  3
 Aspen Property Management            |  3
 Aspen Insulation Company             |  3
 High Country Engineering , Inc.      |  3
```

## Cleanup Protocol
1. **DO NOT auto-merge** — vendor records may have different insurance, contacts, CSI codes
2. Generate a per-duplicate comparison sheet for Buck review
3. Buck selects canonical record — Claude Code runs SQL MERGE under supervision
4. Archive duplicates with `active=false` flag (no hard deletes)

## Suspected Root Cause
Multiple HubSpot sync passes created new vendor records without dedup check. Highest count ('Sunny Oasis Holdings Limited (Melco) ×10') suggests repeated imports.

# Data Cleanup Recommendations
**Date:** 2026-06-28

## Priority Actions
| # | Action | Priority | Owner | Auto-Fixable |
|---|---|---|---|---|
| 1 | Houzz Browser extraction (3 projects × 15 min) | 🔴 HIGH | Browser Claude | No |
| 2 | Vendor dedup comparison sheet → Buck review | 🟡 MEDIUM | Claude Code | No — human decision |
| 3 | Map Houzz projects to DB projects by address | 🟡 MEDIUM | Claude Code | Yes (after data) |
| 4 | Create schedule_variance table (WF-009) | 🟡 MEDIUM | Claude Code | Yes (when data ready) |
| 5 | Link 83 Sagebrusch to HubSpot deal | 🟡 MEDIUM | Buck | No — Buck UI action |

## Hard Rules
- ❌ No auto-merge of vendor records
- ❌ No deletes without backup + Buck approval
- ❌ No HubSpot writes without explicit Buck OK

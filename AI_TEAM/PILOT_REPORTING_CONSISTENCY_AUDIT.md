# Pilot Reporting Consistency Audit — GBT Handoff 2 of 2
**Auditor:** Claude Code
**Date:** 2026-06-28
**Requested by:** GBT (Chief Architect) via Agent Handoff
**Scope:** All Gate 5 reporting surfaces before Architecture Freeze v1.0

---

## Summary

| Surface | Status | Source | Refresh |
|---|---|---|---|
| LIVE_PROJECT_STATE.md | ⚠️ Partially stale | Manual + Claude Code writes | Per session |
| Gateway Exec Report | ✅ Live DB | schedule_variance + risks tables | Real-time |
| PM Console (/gateway/project/{code}/pm) | ✅ Live DB | bid_packages, schedule_variance, daily_logs | Real-time |
| Project Brain (/gateway/project/{code}/brain) | ✅ Live | project-brain service | Real-time |
| Schedule Status (/mvp/schedule-status) | ✅ Live DB | schedule_variance | Real-time |

**Overall verdict: READY WITH DOCUMENTED EXCEPTIONS**

---

## Reconciliation Matrix

### Project Health

| Field | LIVE_PROJECT_STATE | Exec Report (DB) | PM Console | DB Truth | Match? |
|---|---|---|---|---|---|
| 64EW health | YELLOW | GREEN | yellow | 0 open risks, 3 medium variance | ⚠️ Mismatch |
| 101F health | YELLOW | YELLOW | yellow | 1 critical variance, 0 open risks | ✅ |
| 1355R health | GREEN | GREEN | green | 0 variance, 0 risks | ✅ |

**64EW mismatch root cause:** LIVE_PROJECT_STATE.md was manually set to YELLOW based on known field conditions. DB has 0 open risks (risk escalation didn't fire). Exec report shows GREEN based on DB. PM console shows "yellow" based on having 3 variance items. The manual LIVE_PROJECT_STATE value is more accurate to ground truth — the DB is missing the risks.

### Open Risks

| Project | LIVE_PROJECT_STATE | Exec Report | DB (risks table) | Root Cause |
|---|---|---|---|---|
| 64EW | 2 | 0 | 0 | Risk escalation never fired for 2 known field risks |
| 101F | 4 | 0 | 0 | Same — critical steel delay variance didn't write to risks |
| 1355R | 0 | 0 | 0 | ✅ Consistent |

**Root cause:** All risk escalation calls failed silently. The schedule_variance table has the records; the risks table is empty. This is Audit 1 Check 9 failure — risk escalation bug.

### Schedule Variance

| Project | LIVE_PROJECT_STATE | Exec Report (max_variance_days) | schedule_variance records | Root Cause |
|---|---|---|---|---|
| 64EW | +1 day | 0 days | 3 records, all 0 days | LIVE_PROJECT_STATE manually set |
| 101F | +2 days | 0 days (MAX sees 0, not -5) | 3 records: 0, 0, -5 | MAX() bug + sign convention |
| 1355R | 0 days | 0 days | 0 records | ✅ Consistent |

**101F MAX() bug:** The critical steel delay record has variance_days = -5. `MAX(-5, 0, 0) = 0`. The exec report picks 0 and reports "On track" while the project is actually `at_risk` per the schedule-status endpoint. The exec report health is correct (YELLOW from high_variance_items count) but the variance_days field is wrong.

### Bid Packages

| Project | LIVE_PROJECT_STATE | PM Console | DB | Match? |
|---|---|---|---|---|
| 64EW | 35 | 35 total | 35 | ✅ |
| 101F | 26 | 26 total | 26 | ✅ |
| 1355R | 58 | 58 total | 58 | ✅ |

All bid package counts are consistent across all surfaces. ✅

### Schedule Items

| Project | LIVE_PROJECT_STATE | Exec Report | DB | Match? |
|---|---|---|---|---|
| 64EW | 336 | 336 activities | 336 | ✅ |
| 101F | 259 | 259 activities | 259 | ✅ |
| 1355R | 400 | 400 activities | 400 | ✅ |

All schedule item counts consistent. ✅

### Daily Logs

| Project | LIVE_PROJECT_STATE | PM Console | DB | Match? |
|---|---|---|---|---|
| 64EW | — | mentioned | 5 | ✅ |
| 101F | — | mentioned | 7 | ✅ |
| 1355R | — | "No daily logs in past 7 days" | 0 | ✅ Consistent (alert firing correctly) |

---

## Stale Cache / Data Source Issues

| Issue | Surface | Impact | Fix |
|---|---|---|---|
| kpi_snapshots table empty | exec report, executive.py | Historical health unavailable | Sprint 3 — populate on schedule analysis |
| LIVE_PROJECT_STATE.md risk counts manually set | LIVE_PROJECT_STATE | Risk counts show 6 total but DB shows 0 | Re-file risks to DB (P1) |
| LIVE_PROJECT_STATE.md variance days manually set | LIVE_PROJECT_STATE | +1d/+2d not from DB | Auto-update from DB on session end |
| Exec report MAX() variance_days logic | Gateway exec report | Shows 0 variance for 101F despite -5d record | Fix to use ABS() or critical flag |
| variance_days sign convention undocumented | schedule_variance | -5 means behind or ahead? | Document: negative = behind schedule |

---

## Source of Truth Map (Post-Audit)

| Data Type | Authoritative Source | Refresh |
|---|---|---|
| Schedule activities | project_schedule_items | Quarterly (Drive import) |
| Schedule variance / risk level | schedule_variance | Per daily log submission |
| Open risks | risks table | Per schedule analysis |
| Bid packages | bid_packages | Per bid event |
| Project health | /gateway/project/{code}/pm | Real-time from DB |
| Executive summary | /gateway/executive/report | Real-time from DB (fixed this session) |
| System state | LIVE_PROJECT_STATE.md | Manual + Claude Code session end |

---

## Fixes Required Before July 1 (Gate 5 Close)

| Priority | Fix | Owner | Effort |
|---|---|---|---|
| P1 | Re-file 4 known 101F risks + 2 known 64EW risks to risks table | Claude Code | 10 min |
| P1 | Fix exec report MAX() → use ABS() for variance_days | Claude Code | 10 min |
| P1 | Document variance_days sign convention in CLAUDE.md | Claude Code | 5 min |
| P2 | Auto-update LIVE_PROJECT_STATE.md risk counts from DB on session end | Claude Code | 30 min |
| P3 | Populate kpi_snapshots from schedule_variance on each analysis run | Sprint 3 | |

---

## Architecture Freeze v1.0 Recommendation

**READY WITH DOCUMENTED EXCEPTIONS**

The reporting foundation is correct. Data flows from field → daily log → schedule_variance → gateway endpoints. The discrepancies are all traceable to two root causes:
1. Risk escalation silent failure (risks table empty despite critical variance records)
2. LIVE_PROJECT_STATE.md manual values diverging from DB

Neither is a structural problem — they are operational gaps that have a clear fix. The bid package counts, schedule item counts, and endpoint consistency are all clean.

**Condition for Architecture Freeze v1.0:** Complete the P1 fixes above. Then LIVE_PROJECT_STATE, exec report, and PM console will be fully consistent.

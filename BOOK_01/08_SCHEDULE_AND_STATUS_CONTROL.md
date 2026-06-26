# BOOK_01 — Volume 08: Schedule and Status Control

**Version:** 1.0 | **Date:** 2026-06-25

---

## Schedule Ownership

The schedule is owned by the PM, with the Superintendent responsible for look-ahead and daily progress updates. Buck reviews schedule status weekly.

HCI does not manage schedules in isolation — every schedule is connected to the project record in HCI AI, so schedule risk translates directly into procurement flags, budget alerts, and client communication.

---

## Schedule Types

| Type | Purpose | Owner | Update Frequency |
|------|---------|-------|-----------------|
| Master Schedule | Contract milestone schedule | PM | Monthly or as milestones change |
| 3-Week Look-Ahead | Rolling field execution plan | Superintendent | Every Monday |
| Daily Progress | What was actually done today | Superintendent (via daily log) | Daily |

---

## How the Schedule Intelligence Service Works

The `schedule-intelligence` service:
1. Reads the master schedule (from project folder or direct upload)
2. Extracts all activities, durations, dependencies, and milestones
3. Identifies the critical path
4. Compares daily log entries against planned activities
5. Calculates schedule variance: planned vs. actual progress
6. Flags activities that are behind by more than 3 days
7. Identifies long-lead items at risk based on delivery dates vs. schedule need

Schedule data is stored in PostgreSQL and used in the morning brief, weekly reports, and executive dashboard.

---

## Schedule Status Flags

| Flag | Condition | Notification |
|------|-----------|--------------|
| 🟡 Yellow | Activity 3-7 days behind planned start | PM notified |
| 🔴 Red | Activity > 7 days behind planned start | PM + Buck notified |
| ⛔ Critical | Activity on critical path is red | Immediate escalation to Buck |
| 📦 Long Lead Risk | Long-lead delivery date slips past need date | PM notified; procurement re-checked |
| 📋 Milestone Approaching | Contract milestone within 14 days | PM and Buck reminded |

---

## Schedule Updates

**Monthly update:** PM reviews master schedule against actual progress. Any extensions or changes documented in the change log with reason and client notification if required.

**Look-ahead:** Superintendent submits every Monday. AI cross-checks against master schedule and flags conflicts.

**Daily progress:** Extracted from daily logs — no separate submission required. The log entry "Placed concrete at Level 2 East, Grid E-F" is linked to the corresponding schedule activity automatically.

---

## Delay Documentation

Every delay must be documented — not just noted in the daily log:

| Field | Required |
|-------|---------|
| Delay date | Yes |
| Delay cause | Yes — weather, trade contractor, owner, design, utility, other |
| Activities delayed | Yes — reference to schedule activity IDs |
| Duration | Yes — hours or days |
| Critical path impact | Yes — affected / not affected |
| Notification required | Yes — client notification required if critical path delay |
| Resolution | Yes — when delay resolved, how work was recovered |

Delays that affect the critical path trigger a change order analysis. The PM documents whether HCI is entitled to time and/or compensation.

---

## Schedule and Budget Integration

Schedule variances connect to budget in real time:
- A 2-week delay in concrete may mean 2 additional weeks of crane rental
- A delayed sub start may mean supervision time with no productive work below
- Extended general conditions costs are tracked against delay events

When a delay event is logged, the system prompts: "Does this delay create general conditions cost? Log extended cost to delay event record."

---

## Schedule KPIs

| KPI | Target | Source |
|-----|--------|--------|
| Activities completed on planned start date | > 80% | Schedule variance |
| Look-ahead accuracy (planned vs. actual) | > 75% | Weekly comparison |
| Critical path activities on schedule | 100% (zero reds) | Schedule service |
| Delays documented same day | > 95% | Delay log timestamp |
| Milestone achieved on contractual date | > 90% | Milestone tracker |

---

*Schedule intelligence service: `03_Source_Code/services/schedule_intelligence/`*  
*Related SOPs: SOP 17 (Project Schedule), SOP 18 (Long Lead), SOP 33 (Schedule Impact)*

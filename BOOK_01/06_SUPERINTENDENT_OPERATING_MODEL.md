# BOOK_01 — Volume 06: Superintendent Operating Model

**Version:** 1.0 | **Date:** 2026-06-25

---

## Superintendent Role

The Superintendent is HCI's operational authority on the job site. The Superintendent owns:
- Daily field execution and crew coordination
- Daily log — the field record of everything that happened
- Look-ahead schedule — 3-week rolling view of what's coming
- Quality control: inspections, hold points, non-conforming work
- Safety: daily tailgate topics, incident log, corrective actions
- Subcontractor coordination on site
- Photo documentation
- Issue escalation to PM

The Superintendent's daily log is the most important input the system receives every day.

---

## Daily Routine

| Time | Task | System Action |
|------|------|---------------|
| Before start | Read morning brief | Auto-delivered 7 AM — weather, look-ahead priorities, open flags |
| Start of day | Tailgate safety topic | Logged in daily log |
| During day | Crew counts, work in place, equipment on site | Logged in real time or at wrap |
| End of day | Daily log submission | Submit via `~/Desktop/HCI_Daily_Log.command` |
| End of day | Photos | Upload to project folder with standard naming |

---

## Daily Log — What It Must Contain

Every daily log must include:

| Field | Required | Notes |
|-------|---------|-------|
| Project | Yes | Auto-populated from login |
| Date | Yes | Auto-populated |
| Weather | Yes | Temp, conditions, precipitation |
| Crew on site | Yes | Company + count, subs + count |
| Equipment on site | If applicable | Cranes, lifts, major equipment |
| Work performed | Yes | By scope/area — specific, not vague |
| Materials delivered | If applicable | What, from whom, quantity |
| Inspections | If occurred | Inspector, scope, result, any holds |
| RFIs issued or responded | If applicable | Reference number |
| Issues and flags | Yes | Even "no issues" must be noted |
| Look-ahead | Yes | What is planned for next 3 days |
| Delays | If applicable | Cause, duration, scope affected |
| Visitors | If applicable | Name, company, purpose |

**Minimum standard:** A daily log that says only "general construction" is not acceptable. Work must be described by location and scope.

---

## Look-Ahead Schedule

The Superintendent maintains a 3-week look-ahead:
- Week 1: Committed activities (crew assigned, materials on hand)
- Week 2: Planned activities (sub coordination required)
- Week 3: Forecast activities (early visibility for long-lead and access planning)

Look-ahead is updated every Monday and submitted with the week's first daily log.

**Schedule conflicts flagged in the look-ahead:** PM notified same day. Buck notified if conflict affects critical path.

---

## Quality Control

Quality control hold points are set at preconstruction and tracked in the daily log:

| Type | Description |
|------|-------------|
| Inspection Hold | No work proceeds past this point without inspection sign-off |
| Photo Documentation Required | Specific work must be photographed before concealment |
| Test Required | Concrete break, pipe test, air test — result logged |
| Nonconforming Work | Work that did not pass inspection; documented and tracked to correction |

All nonconforming work events create a record: scope, date, cause, corrective action, resolution date.

---

## Safety

Daily tailgate safety topics are logged. Incidents are logged immediately:
- Near miss: logged same day
- First aid: logged same day, Buck notified
- Recordable: logged same day, Buck notified immediately, PM on scene

No incident goes unlogged.

---

## Photo Documentation

Photos are uploaded with this naming convention:  
`YYYY-MM-DD_[ProjectCode]_[Area]_[Subject]_[Sequence].jpg`

Example: `2026-06-25_101FRAN_Level2_ConcreteFormwork_001.jpg`

All photos are indexed in Qdrant for visual search. The Superintendent can search "show me all photos of Level 2 formwork" and get results.

---

## Superintendent KPIs

| KPI | Target | Source |
|-----|--------|--------|
| Daily log submitted by 6 PM | 100% of working days | Log timestamp |
| Look-ahead updated every Monday | 100% | Look-ahead submission log |
| Nonconforming work resolved within 5 days | > 90% | NC work tracker |
| Photos uploaded same day as work | > 90% | Photo log |
| Safety incidents with no immediate report | 0 | Incident log |

---

*Volume 07 covers daily logs and field reporting in technical detail.*  
*Daily log submission: `~/Desktop/HCI_Daily_Log.command`*  
*Superintendent workflow: WF-SUPER*

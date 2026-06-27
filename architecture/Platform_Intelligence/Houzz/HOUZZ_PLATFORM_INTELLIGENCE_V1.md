# Houzz Pro Platform Intelligence — HCI
**Discovery Date:** 2026-06-27 | **Source:** Browser Claude | **Document ID:** HCI-BH-HP-001

---

## Account State
| Field | Value |
|---|---|
| Plan | Houzz Pro |
| Company | Hendrickson Construction Inc. |
| Admin | buck@hendricksoninc.com |
| Team Seats Used | 18 |
| Active Projects | 24 |
| Active Leads | 1 |
| Archived Leads | 56 |
| Contracts Created | 0 |
| Invoices Sent | 0 |
| Purchase Orders | 0 |
| Change Orders | 0 |
| QuickBooks | Not connected |
| Zapier | Available, not configured |

---

## Team Roster (18 seats)
| Name | Email | Role | Status |
|---|---|---|---|
| Chris Hendrickson | chris@hendricksoninc.com | Super Admin | Active |
| Mike Mount | mmount@hendricksoninc.com | Admin | Active |
| Adam Malmgren | adam@hendricksoninc.com | Admin | Active |
| Jason Malik | jmalik@hendricksoninc.com | Admin | Active |
| Eduardo Ruiz | eduardo@hendricksoninc.com | Admin | Active |
| Nelly Caballero | nelly@hendricksoninc.com | Admin | Active |
| Will Royer | wroyer@hendricksoninc.com | Admin | Active |
| Angel Cruz | acruz@hendricksoninc.com | Admin | Active |
| Dillon Hendrickson | dillon@hendricksoninc.com | Admin | Active |
| Elisabeth White | elisabeth@hendricksoninc.com | Admin | Active |
| Buck Adams | buck@hendricksoninc.com | Admin | Active |
| Frankie Arvesen | frankie@hendricksoninc.com | Field Crew | Active |
| Michael Edinger | michael@aliusdc.com | Field Crew | Active |
| Dante De Lacruz | dantedelacruz13@gmail.com | Field Crew | Active |
| Tony Pensamiento | tonypensamiento2@gmail.com | Field Crew | Active |
| Kaleb St Yves | kaleb@hendricksoninc.com | Field Crew | Active |
| traff@hendricksoninc.com | — | Admin | Active |
| Fancisco Ruiz | franciscojruiz29@icloud.com | Field Crew | Pending |

---

## Active Projects (24)
| Project | Client | Location | Created | Type |
|---|---|---|---|---|
| 574 Johnson Drive | — | — | 2026-06-03 | — |
| 606 S Starwood | Jennifer Olson | Aspen CO | 2026-05-06 | — |
| 349 Draw Drive | — | — | 2026-04-29 | — |
| 246 Gallo Way | Johnathan Taylor | — | 2026-04-06 | — |
| 101 Francis | Adnan Rawjee | Aspen CO | 2026-03-05 | Home Remodeling |
| Cemetery Lane 825 | — | — | 2026-01-20 | — |
| 370 Gerbaz Way | Matt Bruckel | Snowmass CO | 2026-01-02 | Home Remodeling |
| Hendrickson Carbondale Catherine Storage | — | — | 2025-12-30 | — |
| HCI Misc | — | — | 2025-12-12 | — |
| 825 Cemetery Ln. | Alan Klien | — | 2025-10-21 | — |
| 1096 Waters | — | — | 2025-10-02 | — |
| 655 Garmish | Jay Nobrega | Aspen CO | 2025-09-08 | Ground-Up Construction |
| 1762 Red Mountain Road | Ted Bigos & Irwin Gold | — | 2025-08-27 | — |
| Vision Builders | — | — | 2025-08-25 | — |
| 813 McSkimming | Ray Spitzley | Aspen CO | 2025-05-21 | Ground-Up Construction |
| Aspen Brewing Company | — | — | 2025-05-02 | — |
| 918 South Mill EXT. | — | — | 2025-03-28 | — |
| 501 East Hyman | — | — | 2025-03-28 | — |
| 655 South Garmisch | Mexamer | Aspen CO | 2025-03-24 | Ground-Up Construction |
| 1355 Riverside | Oakleigh Ryan | — | — | — |

**Data gaps:** 10 projects missing client | 17 projects missing type tag

---

## Module Status
| Module | Status | Usage | Action |
|---|---|---|---|
| Contracts | UNUSED | 0 | EXTEND: auto-generate from deal stage |
| Estimates | LOW USE | 3 records | EXTEND: mandatory in workflow |
| Schedules | NOT IN USE | 0 | EXTEND: build phase templates by type |
| Tasks & Punchlist | ACTIVE | 45 tasks on 655 Garmish | EXTEND: AI punchlist from daily logs |
| Daily Logs | ACTIVE | large volume | INTEGRATE: parse for AI site reports |
| Files & Photos | PRESUMED ACTIVE | — | EXTEND: standardize + Google Drive sync |
| Invoices | MINIMAL | 2 drafts | EXTEND: milestone-based auto-invoicing |
| Purchase Orders | UNUSED | 0 | EXTEND: auto-PO on executed subcontract |
| Change Orders | UNUSED | 0 | EXTEND: AI-assisted from daily log flags |
| Budget | NOT IN USE | — | EXTEND: populate from estimates |
| Time | UNUSED | 0 | EXTEND: enable for field crew billing |
| Expenses | UNUSED | 0 | EXTEND: project cost tracking |
| Client Dashboard | CONFIGURED NOT SHARED | — | EXTEND: share at contract signing |

---

## Financial Documents
| ID | Type | Project | Amount | Status |
|---|---|---|---|---|
| ES-0001 | Estimate | 212 Cleveland | $84,924.13 | Sent |
| ES-10002 | Estimate | 212 Cleveland | $0.00 | Draft |
| ES-10004 | Estimate | 825 Cemetery Lane | $36,000.00 | Draft |
| IN-10001 | Invoice | — | $0.63 | Draft |
| IN-10002 | Invoice | — | $0.00 | Draft |

---

## Automation Opportunities
| ID | Opportunity | Value | Complexity | Status |
|---|---|---|---|---|
| AO-HP-001 | HubSpot Deal → Houzz Pro Project Bridge | HIGH | MEDIUM | **P0 — Build Now** |
| AO-HP-002 | Houzz Lead → HubSpot Contact Sync (Zapier) | HIGH | MEDIUM | READY_TO_BUILD |
| AO-HP-003 | AI Lead Response (5-min auto-reply) | HIGH | MEDIUM | READY_TO_BUILD |
| AO-HP-004 | Contract Auto-Generate from Deal Stage | HIGH | MEDIUM | PENDING_HOUZZ_API |
| AO-HP-005 | Estimate Total Sync to HubSpot Deal Amount | HIGH | LOW | READY_TO_BUILD |
| AO-HP-006 | Milestone-Based Auto-Invoicing | HIGH | MEDIUM | READY_TO_BUILD |
| AO-HP-007 | Change Order from Daily Log (AI) | HIGH | MEDIUM | FUTURE_PHASE |
| AO-HP-008 | Selection Reminder Cadence | HIGH | LOW | READY_TO_BUILD |
| AO-HP-009 | AI Punchlist from Daily Logs | HIGH | MEDIUM | FUTURE_PHASE |
| AO-HP-010 | QuickBooks Online Sync | HIGH | LOW | READY_TO_CONFIGURE |
| AO-HP-011 | Project Folder Template Auto-Create | MEDIUM | LOW | READY_TO_BUILD |
| AO-HP-012 | Schedule Phase Templates | HIGH | MEDIUM | READY_TO_BUILD |
| AO-HP-013 | Client Dashboard Auto-Share at Contract Signing | MEDIUM | LOW | READY_TO_BUILD |
| AO-HP-014 | Subcontractor Dashboard Activation on PO | MEDIUM | LOW | READY_TO_BUILD |

---

## Critical Gaps
| Priority | Gap |
|---|---|
| P0 | No Houzz Pro ↔ HubSpot integration — dual manual entry on every project |
| P0 | 303 area homeowners not captured as leads — unconverted inbound revenue |
| P1 | QuickBooks not connected — financial data siloed |
| P1 | Zapier not configured — available HubSpot bridge dormant |
| P1 | 0 contracts — client agreements managed outside platform |
| P1 | 0 invoices sent — payment collection not centralized |
| P1 | No schedules — zero project timeline visibility |
| P2 | 10 projects missing client associations |
| P2 | 17 projects missing type tag |
| P2 | Client Dashboard not shared on any project |

---

## URL Patterns
```
/manage/projects                          — Projects list
/manage/projects/{id}/overview            — Project overview
/manage/projects/{id}/contracts           — Contracts
/manage/projects/{id}/estimates           — Estimates
/manage/tasks/projects/{id}               — Tasks
/manage/projects/{id}/schedule            — Schedule
/manage/projects/{id}/files               — Files
/manage/projects/{id}/daily-log           — Daily Log
/manage/projects/{id}/expenses            — Expenses
/manage/projects/{id}/client-dashboard    — Client Dashboard
/manage/projects/{id}/invoices            — Invoices
/manage/projects/{id}/budget              — Budget
/manage/leads                             — Leads
/manage/reports/                          — Financial Reports
/settings/integrations                    — Integrations
/settings/zapier                          — Zapier
/settings/quickbooks                      — QuickBooks
```

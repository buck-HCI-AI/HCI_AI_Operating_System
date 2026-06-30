---
source_agent: Browser Claude
destination_agent: Claude Code
document_type: browser_discovery
priority: high
status: ready_for_processing
related_system: Houzz Pro
intended_action: ingest_and_route
requires_approval: false
discovery_date: 2026-06-27
document_id: HCI-BH-HP-001
version: 1.0
---

# BROWSER HANDOFF — HOUZZ PRO PLATFORM INTELLIGENCE
## Hendrickson Construction Inc. | Aspen | 18 Team Seats

## SUMMARY
Houzz Pro is HCI project management, field operations, and financial document platform. 24 active projects. 18 team members. Significant feature underutilization: 0 contracts, 0 invoices sent, 0 purchase orders, 0 change orders, 0 schedules built. Tasks and Punchlist actively used. No integration between Houzz Pro and HubSpot. Zapier available but not configured. QuickBooks Online available but not connected.

## ACCOUNT METADATA
- platform: Houzz Pro
- company: Hendrickson Construction Inc.
- location: Aspen, Colorado
- base_url: https://pro.houzz.com
- admin_email: buck@hendricksoninc.com
- team_seats_used: 18 (unlimited plan)
- active_projects: 24
- active_leads: 1
- archived_leads: 56
- financial_documents: 5 (3 estimates, 2 invoices — all draft)
- contracts_created: 0
- invoices_sent: 0
- purchase_orders: 0
- change_orders: 0
- quickbooks_connected: false
- zapier_configured: false

## TEAM ROSTER
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
| traff@hendricksoninc.com | traff@hendricksoninc.com | Admin | Active |
| Fancisco Ruiz | franciscojruiz29@icloud.com | Field Crew | Pending |

## PROJECT INVENTORY (24 total)
| Project Name | Client | Location | Created | Type |
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

NOTE: Project names align with HubSpot deal names — confirms dual manual entry. 10 projects missing client. 17 projects missing type.

## SAMPLE PROJECT DEEP DIVE — 655 Garmish (most complete)
- project_id: 2840986
- client: Jay Nobrega (jay@mexamer.com)
- location: 655 South Garmisch Street, Aspen CO 81611
- status: Open
- type: Ground-Up Construction
- tasks: 45 total (1 completed, 44 open)
- expenses: $0 tracked
- client_dashboard: Not Shared
- subcontractor_dashboard: Available, not configured
- sample_tasks: Widow Measurements | Backfilling east/back side | Complete Laundry Fan Coil | Complete Closet Fan Coil | Submit HVAC Rough-In Scope | Verify Sprinkler Layouts | Obtain MEP Sign-Off | Verify ZIP Backing at Stone | Complete Soffit Framing | Complete Hallway Lighting Rough-In | Elevator shaft dimensions | Confirm elevator delivery date | Water line survey coordination

## MODULE INVENTORY
### PLANNING
| Module | Status | Records | Recommendation |
|---|---|---|---|
| Contracts | UNUSED | 0 | EXTEND — auto-generate from deal stage |
| Estimates | LOW | 3 (1 sent $84,924 / 2 draft) | EXTEND — mandatory workflow step |
| Takeoffs | UNKNOWN | — | EVALUATE |
| 3D Floor Plans | UNKNOWN | — | IGNORE |
| Mood Boards | UNKNOWN | — | IGNORE |
| Selection Boards | UNKNOWN | — | EXTEND — automate reminder cadence |
| Selections Tracker | UNKNOWN | — | INTEGRATE — parse weekly XLS export |
| Bids | UNKNOWN | — | EVALUATE — HCI uses HubSpot email bidding |

### MANAGEMENT
| Module | Status | Records | Recommendation |
|---|---|---|---|
| Files & Photos | PRESUMED_ACTIVE | — | EXTEND — standardize folders, Google Drive sync |
| Schedule | UNUSED | 0 | EXTEND — phase templates by project type |
| Tasks & Punchlist | ACTIVE | 45+ tasks on one project | EXTEND — AI punchlist from Daily Logs |
| Client Dashboard | UNUSED (not shared) | — | EXTEND — share at project milestones |
| Daily Logs | UNKNOWN | — | INTEGRATE — AI scans for unresolved items |
| Time | UNUSED | 0 entries | EXTEND — field crew time tracking |
| Expenses | UNUSED | $0 tracked | EXTEND — receipt capture automation |
| Warranties & Claims | UNKNOWN | — | EXTEND — post-closeout automation |

### FINANCE
| Module | Status | Records | Recommendation |
|---|---|---|---|
| Invoices | MINIMAL | 2 drafts ($0.63 + $0) | EXTEND — milestone-based invoicing |
| Purchase Orders | UNUSED | 0 | EXTEND — auto-generate from sub award |
| Change Orders | UNUSED | 0 | EXTEND — AI drafting from Daily Log flags |
| Retainers & Credits | UNUSED | 0 | EXTEND — auto-request on contract signing |
| Budget | UNUSED | — | EXTEND — highest value financial feature |
| Financial Overview | AVAILABLE | — | EXTEND — sync to HubSpot deal amount |

## FINANCIAL DOCUMENTS ON FILE
| ID | Name | Amount | Status |
|---|---|---|---|
| ES-0001 | 212 Cleveland | $84,924.13 | Sent |
| ES-10002 | 212 Cleveland | $0.00 | Draft |
| ES-10004 | 825 Cemetery Lane | $36,000.00 | Draft |
| IN-10001 | — | $0.63 | Draft |
| IN-10002 | — | $0.00 | Draft |

## LEADS
- active_leads: 1 (Shianne Bathroom Remodeling — Followed Up — Houzz project match — Jul 2025)
- archived_leads: 56 (1 new spam)
- lead_stages: New | Followed Up | Connected | Meeting Scheduled | Estimate Sent | Won | Snoozed | Archived
- market_opportunity: 303 homeowners searching for pros in HCI area — not being captured

## INTEGRATIONS AVAILABLE
| Integration | Status | Recommendation |
|---|---|---|
| Zapier (BETA) | Available, NOT configured | CONFIGURE — bridge to HubSpot |
| QuickBooks Online | Available, NOT connected | CONNECT — financial sync |
| Google Drive | Available, unknown status | CONNECT — file storage sync |
| Clipper Tool | Available | EVALUATE |
| Calendar (Google Meet / Zoom / Teams / GoTo / 8x8) | Available | CONFIGURE |

## URL PATTERNS DISCOVERED
- Projects list: /manage/projects
- Project overview: /manage/projects/{id}/overview
- Tasks: /manage/tasks/projects/{id}
- Estimates: /manage/projects/{id}/estimates
- Invoices: /manage/projects/{id}/invoices
- Expenses: /manage/projects/{id}/expenses
- Client Dashboard: /manage/projects/{id}/client-dashboard
- Daily Logs: /manage/projects/{id}/daily-log
- Files: /manage/projects/{id}/files
- Schedule: /manage/projects/{id}/schedule
- Warranties: /manage/projects/{id}/warranties
- Leads: /manage/leads
- Financial Reports: /manage/reports/
- Settings/Integrations: /settings/integrations
- Settings/Zapier: /settings/zapier
- Team Members: /settings/team-members

## AUTOMATION OPPORTUNITIES
| ID | Title | Value | Complexity | Status |
|---|---|---|---|---|
| AO-HP-001 | HubSpot Deal → Houzz Pro Project Auto-Create | HIGH | MEDIUM | PENDING_ZAPIER_CONFIG |
| AO-HP-002 | AI Lead Response (303 homeowners not captured) | HIGH | MEDIUM | READY_TO_BUILD |
| AO-HP-003 | Contract Auto-Generate from Deal Stage | HIGH | MEDIUM | READY_TO_BUILD |
| AO-HP-004 | Milestone-Based Invoice Automation | HIGH | MEDIUM | READY_TO_BUILD |
| AO-HP-005 | AI Change Order Drafting from Daily Logs | HIGH | LOW | READY_TO_BUILD |
| AO-HP-006 | Purchase Order Auto-Generate on Sub Award | MEDIUM | MEDIUM | READY_TO_BUILD |
| AO-HP-007 | QuickBooks Online Sync | HIGH | LOW | CONNECT_FIRST |
| AO-HP-008 | Selection Reminder Automation | HIGH | LOW | READY_TO_BUILD |
| AO-HP-009 | Project Schedule Phase Templates | HIGH | MEDIUM | READY_TO_BUILD |
| AO-HP-010 | AI Punchlist Generation from Daily Logs | HIGH | MEDIUM | READY_TO_BUILD |
| AO-HP-011 | Client Dashboard Auto-Share at Milestones | MEDIUM | LOW | READY_TO_BUILD |
| AO-HP-012 | Selections Tracker Weekly XLS → AI Parse | MEDIUM | MEDIUM | READY_TO_BUILD |
| AO-HP-013 | Field Crew Time Tracking via Mobile | MEDIUM | LOW | READY_TO_BUILD |
| AO-HP-014 | Expense Receipt Capture Automation | MEDIUM | LOW | READY_TO_BUILD |

## CRITICAL GAPS
| Priority | Gap | Fix |
|---|---|---|
| P0 | No Houzz Pro to HubSpot integration | AO-HP-001 via Zapier |
| P0 | 303 homeowners searching — 0 captured | AO-HP-002 |
| P1 | 0 contracts created | AO-HP-003 |
| P1 | 0 invoices sent to clients | AO-HP-004 |
| P1 | 0 change orders | AO-HP-005 |
| P1 | Budget module unused | Activate + sync to HubSpot |
| P1 | QuickBooks not connected | AO-HP-007 |
| P2 | 0 schedules built | AO-HP-009 |
| P2 | Client Dashboard not shared on any project | AO-HP-011 |

## NEXT ACTIONS FOR CLAUDE CODE
1. Configure Zapier: Houzz Pro → HubSpot project bridge (AO-HP-001 / AO-HS-003)
2. Design lead capture automation for 303 homeowner opportunity (AO-HP-002)
3. Build contract auto-generation workflow (AO-HP-003)
4. Build milestone invoice automation (AO-HP-004)
5. Build AI change order drafting from Daily Logs (AO-HP-005)
6. Connect QuickBooks Online (AO-HP-007)
7. Build selection reminder cadence (AO-HP-008)

---
*Browser Claude — Discovery Agent | Read-only. Do not modify production systems.*
*Auto-route to: Agent_Handoff/Inbox when path exists*

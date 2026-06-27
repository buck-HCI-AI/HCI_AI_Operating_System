---
created_at: 2026-06-27
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
summary: Houzz Pro platform discovery: 24 projects, 18 seats, feature underutilization, 14 automation opportunities, P0 gap is HubSpot bridge
---

# BROWSER HANDOFF — HOUZZ PRO PLATFORM INTELLIGENCE
## Hendrickson Construction Inc. | Aspen | 18 Team Seats

## SUMMARY
Houzz Pro is HCI project management, field operations, and financial document platform. 24 active projects. 18 team members. Significant feature underutilization: 0 contracts, 0 invoices sent, 0 purchase orders, 0 change orders, 0 schedules built. Tasks and Punchlist actively used. No integration between Houzz Pro and HubSpot. Zapier available but not configured. QuickBooks Online available but not connected.

## ACCOUNT METADATA
platform: Houzz Pro
company: Hendrickson Construction Inc.
location: Aspen, Colorado
base_url: https://pro.houzz.com
admin_email: buck@hendricksoninc.com
team_seats_used: 18
active_projects: 24
active_leads: 1
archived_leads: 56
financial_documents: 5
contracts_created: 0
invoices_sent: 0
purchase_orders: 0
change_orders: 0
quickbooks_connected: false
zapier_configured: false
google_drive_connected: unknown

## TEAM ROSTER
Chris Hendrickson | chris@hendricksoninc.com | Super Admin | Active
Mike Mount | mmount@hendricksoninc.com | Admin | Active
Adam Malmgren | adam@hendricksoninc.com | Admin | Active
Jason Malik | jmalik@hendricksoninc.com | Admin | Active
Eduardo Ruiz | eduardo@hendricksoninc.com | Admin | Active
Nelly Caballero | nelly@hendricksoninc.com | Admin | Active
Will Royer | wroyer@hendricksoninc.com | Admin | Active
Angel Cruz | acruz@hendricksoninc.com | Admin | Active
Dillon Hendrickson | dillon@hendricksoninc.com | Admin | Active
Elisabeth White | elisabeth@hendricksoninc.com | Admin | Active
Buck Adams | buck@hendricksoninc.com | Admin | Active
Frankie Arvesen | frankie@hendricksoninc.com | Field Crew | Active
Michael Edinger | michael@aliusdc.com | Field Crew | Active
Dante De Lacruz | dantedelacruz13@gmail.com | Field Crew | Active
Tony Pensamiento | tonypensamiento2@gmail.com | Field Crew | Active
Kaleb St Yves | kaleb@hendricksoninc.com | Field Crew | Active
traff@hendricksoninc.com | Admin | Active
Fancisco Ruiz | franciscojruiz29@icloud.com | Field Crew | Pending

## ACTIVE PROJECTS (24)
574 Johnson Drive | no client | created 2026-06-03 | Open
606 S Starwood | Jennifer Olson | Aspen CO | created 2026-05-06 | Open
349 Draw Drive | no client | created 2026-04-29 | Open
246 Gallo Way | Johnathan Taylor | created 2026-04-06 | Open
101 Francis | Adnan Rawjee | Aspen CO | created 2026-03-05 | Open | Home Remodeling
Cemetery Lane 825 | no client | created 2026-01-20 | Open
370 Gerbaz Way | Matt Bruckel | Snowmass CO | created 2026-01-02 | Open | Home Remodeling
Hendrickson Carbondale Catherine Storage | no client | created 2025-12-30 | Open
HCI Misc | no client | created 2025-12-12 | Open
825 Cemetery Ln. | Alan Klien | created 2025-10-21 | Open
1096 Waters | no client | created 2025-10-02 | Open
655 Garmish | Jay Nobrega | Aspen CO | created 2025-09-08 | Open | Ground-Up Construction
1762 Red Mountain Road | Ted Bigos & Irwin Gold | created 2025-08-27 | Open
Vision Builders | no client | created 2025-08-25 | Open
813 McSkimming | Ray Spitzley | Aspen CO | created 2025-05-21 | Open | Ground-Up Construction
Aspen Brewing Company | no client | created 2025-05-02 | Open
918 South Mill EXT. | no client | created 2025-03-28 | Open
501 East Hyman | no client | created 2025-03-28 | Open
655 South Garmisch | Mexamer | Aspen CO | created 2025-03-24 | Open | Ground-Up Construction
1355 Riverside | Oakleigh Ryan | Open
NOTE: 10 projects missing client | 17 projects missing type tag | Names mirror HubSpot deals confirming dual manual entry

## MODULE INVENTORY

### PLANNING
Contracts | UNUSED | 0 created | RECOMMEND: EXTEND auto-generate from deal stage
Estimates | LOW USE | 3 records (1 sent $84924, 2 drafts) | RECOMMEND: EXTEND make mandatory in workflow
Takeoffs | UNKNOWN | RECOMMEND: EVALUATE
3D Floor Plans | UNKNOWN | RECOMMEND: IGNORE (quality insufficient for Aspen market)
Mood Boards | UNKNOWN | RECOMMEND: IGNORE (not relevant for GC)
Selection Boards | UNKNOWN | RECOMMEND: EXTEND automate selection reminder cadence
Selections Tracker | UNKNOWN | export XLS/CSV | RECOMMEND: INTEGRATE parse weekly for procurement alerts
Bids | UNKNOWN | HCI uses HubSpot email bidding instead | RECOMMEND: EVALUATE sub adoption required

### MANAGEMENT
Files & Photos | PRESUMED ACTIVE | RECOMMEND: EXTEND standardize folder structure Google Drive sync
Schedule | NOT IN USE | RECOMMEND: EXTEND build phase templates by project type
Tasks & Punchlist | ACTIVE | 45 tasks on 655 Garmish alone (44 open 1 complete) | RECOMMEND: EXTEND AI punchlist from daily logs
Client Dashboard | CONFIGURED NOT SHARED | status: Not Shared on explored project | RECOMMEND: EXTEND share at contract signing
Daily Logs | ACTIVE | large volume of entries observed | RECOMMEND: INTEGRATE parse for AI site report generation
Time | UNUSED | 0 entries on explored project | RECOMMEND: EXTEND enable for field crew billing
Expenses | UNUSED | $0 total billable on explored project | RECOMMEND: EXTEND for project cost tracking
Warranties & Claims | UNKNOWN | RECOMMEND: EXTEND activate at closeout stage

### FINANCE
Invoices | MINIMAL | 2 drafts (IN-10001 $0.63, IN-10002 $0) | RECOMMEND: EXTEND milestone-based auto-invoicing
Purchase Orders | UNUSED | 0 created | RECOMMEND: EXTEND auto-PO when subcontract fully executed
Change Orders | UNUSED | 0 created | RECOMMEND: EXTEND AI-assisted drafting from daily log flags
Retainers & Credits | UNUSED | 0 created | RECOMMEND: EXTEND auto-request at contract signing
Budget | NOT OBSERVED IN USE | RECOMMEND: EXTEND activate populate from estimates

## FINANCIAL DOCUMENTS DETAIL
ES-0001 | Estimate | 212 Cleveland | $84,924.13 | Sent
ES-10002 | Estimate | 212 Cleveland | $0.00 | Draft
ES-10004 | Estimate | 825 Cemetery Lane | $36,000.00 | Draft
IN-10001 | Invoice | $0.63 | Draft
IN-10002 | Invoice | $0.00 | Draft

## LEADS MODULE
Active leads: 1 (Shianne Quintana | Bathroom Remodeling | Carbondale | Houzz project match | Jul 2025 | Followed Up stage)
Archived leads: 56
Lead stages: New, Followed Up, Connected, Meeting Scheduled, Estimate Sent, Won, Snoozed, Archived
303 homeowners searching for pros in HCI area — significant unconverted pipeline
Lead import history available
Auto-reply feature available (vacation mode)

## FINANCIAL REPORTS AVAILABLE
Payments report | Payouts report | Open Invoices report | Sales Tax Liability report
Incoming transactions by project | Outgoing transactions by project
Time billing by Team Member | Time billing by Project
Selections Tracker Global Report (XLS/CSV export)

## INTEGRATIONS AVAILABLE
Calendar: Google Meet, Zoom, GoTo Meeting, Microsoft Teams, 8x8
Third-party: QuickBooks Online (not connected), Google Drive (unknown), Zapier BETA (not configured)
Clipper Tool (available)

## URL PATTERNS
Projects list: /manage/projects
Project overview: /manage/projects/{id}/overview
Project contracts: /manage/projects/{id}/contracts
Project estimates: /manage/projects/{id}/estimates
Project tasks: /manage/tasks/projects/{id}
Project schedule: /manage/projects/{id}/schedule
Project files: /manage/projects/{id}/files
Project daily log: /manage/projects/{id}/daily-log
Project expenses: /manage/projects/{id}/expenses
Project client dashboard: /manage/projects/{id}/client-dashboard
Project invoices: /manage/projects/{id}/invoices
Project budget: /manage/projects/{id}/budget
Leads: /manage/leads
Financial reports: /manage/reports/
Settings integrations: /settings/integrations
Settings team: /settings/team-members
Zapier: /settings/zapier
QuickBooks: /settings/quickbooks
Team chat: /teamchat/channels/all

## TASKS DISCOVERY (655 Garmish sample — 45 tasks)
Active construction task categories observed:
HVAC rough-in scope, fan coil installation, sprinkler verification
Electrical rough-in, lighting locations, can placement
Plumbing water lines, drain piping, pressure testing
Structural: soffit framing, radius flashing, backfill, grading
Coordination: elevator shaft, pocket door elevations, pantry hardware
Inspections: sign-offs from HVAC + Electrical + Fire Protection
Pattern: granular trade-level punchlist items with due dates and assignees
Assignees use initials (MM=Mike Mount, ER=Eduardo Ruiz)

## AUTOMATION OPPORTUNITIES
AO-HP-001 | HubSpot Deal to Houzz Pro Project Bridge | ROM Accepted triggers auto-create project with metadata | HIGH | MEDIUM | P0 PRIORITY
AO-HP-002 | Houzz Lead to HubSpot Contact Sync | When lead Connected or later, create/update HubSpot contact | HIGH | MEDIUM | READY_TO_BUILD via Zapier
AO-HP-003 | AI Lead Response | Auto-reply to new Houzz leads within 5 min using AI-personalized message | HIGH | MEDIUM | READY_TO_BUILD
AO-HP-004 | Contract Auto-Generate from Deal Stage | When HubSpot deal moves to Contract to Client, trigger Houzz Pro contract creation | HIGH | MEDIUM | PENDING_HOUZZ_API
AO-HP-005 | Estimate Total Sync to HubSpot Deal Amount | Keep deal amount field accurate from Houzz estimate | HIGH | LOW | READY_TO_BUILD
AO-HP-006 | Milestone-Based Auto-Invoicing | Generate invoice at defined project milestones | HIGH | MEDIUM | READY_TO_BUILD
AO-HP-007 | Change Order from Daily Log | AI scans daily logs for out-of-scope flags, drafts change order | HIGH | MEDIUM | FUTURE_PHASE
AO-HP-008 | Selection Reminder Cadence | Auto-remind client of pending selections on weekly schedule | HIGH | LOW | READY_TO_BUILD
AO-HP-009 | AI Punchlist from Daily Logs | Parse 30 days of logs for unresolved items, create punchlist | HIGH | MEDIUM | FUTURE_PHASE
AO-HP-010 | QuickBooks Online Sync | Connect Houzz Pro financials to QuickBooks for accounting | HIGH | LOW | READY_TO_CONFIGURE
AO-HP-011 | Project Folder Template Auto-Create | Standard folder structure on every new project creation | MEDIUM | LOW | READY_TO_BUILD
AO-HP-012 | Schedule Phase Templates | Standard Gantt templates by project type (Remodel 8 phases, Ground-Up 12 phases) | HIGH | MEDIUM | READY_TO_BUILD
AO-HP-013 | Client Dashboard Auto-Share at Contract Signing | When contract signed, auto-enable client dashboard sharing | MEDIUM | LOW | READY_TO_BUILD
AO-HP-014 | Subcontractor Dashboard Activation | Share sub dashboard with subs when PO issued | MEDIUM | LOW | READY_TO_BUILD

## CRITICAL GAPS
P0 | No Houzz Pro to HubSpot integration | Every project requires dual manual entry
P0 | 303 area homeowners not captured as leads | Revenue leakage from unconverted inbound
P1 | QuickBooks not connected | Financial data siloed from accounting
P1 | Zapier not configured | Available bridge to HubSpot not activated
P1 | 0 contracts created | Client agreements managed outside platform
P1 | 0 invoices sent through platform | Payment collection not centralized
P1 | Schedules not built | No project timeline visibility
P2 | 10 projects missing client associations | Data incomplete for automation
P2 | 17 projects missing type tag | Cannot filter or automate by project type
P2 | Client Dashboard not shared on any explored project | Client transparency opportunity missed

## NEXT ACTIONS FOR CLAUDE CODE
1. Design Houzz Pro to HubSpot bidirectional sync architecture (AO-HP-001)
2. Configure Zapier: Houzz Lead Connected → HubSpot Contact create/update (AO-HP-002)
3. Design QuickBooks Online connection workflow (AO-HP-010)
4. Build selection reminder automation (AO-HP-008)
5. Build project folder template auto-create (AO-HP-011)
6. Design milestone-based invoicing workflow (AO-HP-006)
7. Investigate Houzz Pro API availability for programmatic project creation

## DIRECTIVE NOTE
When Agent_Handoff/Inbox directory exists, Browser Claude will auto-place all future
handoff files there without requiring Buck to act as message bus.

---
Document prepared by Browser Claude — Discovery Agent
Destination: Claude Code — Handoff Processor
Read-only discovery. Do not modify production systems. Do not trigger workflows.

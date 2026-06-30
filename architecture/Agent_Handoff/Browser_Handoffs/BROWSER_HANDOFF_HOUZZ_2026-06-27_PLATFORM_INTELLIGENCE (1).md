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
prepared_by: Browser Claude (Discovery Agent)
executive_approver: Buck Adams (buck@hendricksoninc.com)
---

# BROWSER HANDOFF — HOUZZ PRO PLATFORM INTELLIGENCE
## Hendrickson Construction Inc. | Aspen | 18 Team Seats

## SUMMARY
Houzz Pro is HCI's project management, field operations, and financial document platform. 24 active projects. 18 team members. Significant feature underutilization: 0 contracts, 0 invoices sent, 0 purchase orders, 0 change orders, 0 schedules built. Tasks & Punchlist actively used (45 tasks observed on 655 Garmish). No integration exists between Houzz Pro and HubSpot. Zapier available but not configured. QuickBooks Online available but not connected.

## ACCOUNT METADATA
```json
{
  "platform": "Houzz Pro",
  "company": "Hendrickson Construction Inc.",
  "location": "Aspen, Colorado",
  "base_url": "https://pro.houzz.com",
  "admin_email": "buck@hendricksoninc.com",
  "houzz_username": "webuser_185947852",
  "team_seats_used": 18,
  "active_projects": 24,
  "active_leads": 1,
  "archived_leads": 56,
  "homeowners_searching_area": 303,
  "contracts_created": 0,
  "invoices_sent": 0,
  "purchase_orders_created": 0,
  "change_orders_created": 0,
  "estimates_total": 3,
  "estimates_sent": 1,
  "invoices_total": 2,
  "quickbooks_connected": false,
  "zapier_configured": false,
  "google_drive_connected": "unknown"
}
```

## TEAM ROSTER
```json
[
  {"name":"Chris Hendrickson","email":"chris@hendricksoninc.com","role":"Super Admin","status":"Active"},
  {"name":"Mike Mount","email":"mmount@hendricksoninc.com","role":"Admin","status":"Active"},
  {"name":"Adam Malmgren","email":"adam@hendricksoninc.com","role":"Admin","status":"Active"},
  {"name":"Jason Malik","email":"jmalik@hendricksoninc.com","role":"Admin","status":"Active"},
  {"name":"Eduardo Ruiz","email":"eduardo@hendricksoninc.com","role":"Admin","status":"Active"},
  {"name":"Nelly Caballero","email":"nelly@hendricksoninc.com","role":"Admin","status":"Active"},
  {"name":"Will Royer","email":"wroyer@hendricksoninc.com","role":"Admin","status":"Active"},
  {"name":"Angel Cruz","email":"acruz@hendricksoninc.com","role":"Admin","status":"Active"},
  {"name":"Dillon Hendrickson","email":"dillon@hendricksoninc.com","role":"Admin","status":"Active"},
  {"name":"Elisabeth White","email":"elisabeth@hendricksoninc.com","role":"Admin","status":"Active"},
  {"name":"Buck Adams","email":"buck@hendricksoninc.com","role":"Admin","status":"Active"},
  {"name":"Frankie Arvesen","email":"frankie@hendricksoninc.com","role":"Field Crew","status":"Active"},
  {"name":"Michael Edinger","email":"michael@aliusdc.com","role":"Field Crew","status":"Active"},
  {"name":"Dante De Lacruz","email":"dantedelacruz13@gmail.com","role":"Field Crew","status":"Active"},
  {"name":"Tony Pensamiento","email":"tonypensamiento2@gmail.com","role":"Field Crew","status":"Active"},
  {"name":"Kaleb St Yves","email":"kaleb@hendricksoninc.com","role":"Field Crew","status":"Active"},
  {"name":"traff@hendricksoninc.com","role":"Admin","status":"Active"},
  {"name":"Fancisco Ruiz","email":"franciscojruiz29@icloud.com","role":"Field Crew","status":"Pending"}
]
```

## PROJECT INVENTORY
```json
[
  {"name":"574 Johnson Drive","client":null,"created":"2026-06-03","status":"Open","type":null,"hubspot_match":true},
  {"name":"606 S Starwood","client":"Jennifer Olson","location":"Aspen, CO","created":"2026-05-06","status":"Open","hubspot_match":true},
  {"name":"349 Draw Drive","client":null,"created":"2026-04-29","status":"Open","hubspot_match":true},
  {"name":"246 Gallo Way","client":"Johnathan Taylor","created":"2026-04-06","status":"Open","hubspot_match":true},
  {"name":"101 Francis","client":"Adnan Rawjee","location":"Aspen, CO","created":"2026-03-05","status":"Open","type":"Home Remodeling","hubspot_match":true},
  {"name":"Cemetery Lane 825","client":null,"created":"2026-01-20","status":"Open"},
  {"name":"370 Gerbaz Way","client":"Matt Bruckel","location":"Snowmass, CO","created":"2026-01-02","status":"Open","type":"Home Remodeling","hubspot_match":true},
  {"name":"Hendrickson Carbondale Catherine Storage","client":null,"created":"2025-12-30","status":"Open"},
  {"name":"HCI Misc","client":null,"created":"2025-12-12","status":"Open"},
  {"name":"825 Cemetery Ln.","client":"Alan Klien","created":"2025-10-21","status":"Open","hubspot_match":true},
  {"name":"1096 Waters","client":null,"created":"2025-10-02","status":"Open"},
  {"name":"655 Garmish","client":"Jay Nobrega","location":"Aspen, CO","created":"2025-09-08","status":"Open","type":"Ground-Up Construction","tasks":45,"hubspot_match":true},
  {"name":"1762 Red Mountain Road","client":"Ted Bigos & Irwin Gold","created":"2025-08-27","status":"Open","hubspot_match":true},
  {"name":"Vision Builders","client":null,"created":"2025-08-25","status":"Open"},
  {"name":"813 McSkimming","client":"Ray Spitzley","location":"Aspen, CO","created":"2025-05-21","status":"Open","type":"Ground-Up Construction","hubspot_match":true},
  {"name":"Aspen Brewing Company","client":null,"created":"2025-05-02","status":"Open"},
  {"name":"918 South Mill EXT.","client":null,"created":"2025-03-28","status":"Open"},
  {"name":"655 South Garmisch","client":"Mexamer","location":"Aspen, CO","created":"2025-03-24","status":"Open","type":"Ground-Up Construction","hubspot_match":true},
  {"name":"1355 Riverside","client":"Oakleigh Ryan","status":"Open","hubspot_match":true}
]
```

## MODULE INVENTORY
```json
{
  "planning": [
    {"name":"Contracts","usage_status":"UNUSED","records":0,"recommendation":"EXTEND — auto-generate from HubSpot deal stage trigger"},
    {"name":"Estimates","usage_status":"LOW","records":3,"sent":1,"recommendation":"EXTEND — make mandatory workflow step"},
    {"name":"Takeoffs","usage_status":"UNKNOWN","recommendation":"EVALUATE"},
    {"name":"3D Floor Plans","usage_status":"UNKNOWN","recommendation":"IGNORE"},
    {"name":"Mood Boards","usage_status":"UNKNOWN","recommendation":"IGNORE"},
    {"name":"Selection Boards","usage_status":"UNKNOWN","recommendation":"EXTEND — automate reminder cadence"},
    {"name":"Selections Tracker","usage_status":"UNKNOWN","export_formats":["XLS","CSV"],"recommendation":"INTEGRATE — parse weekly export for procurement alerts"},
    {"name":"Bids","usage_status":"UNKNOWN","recommendation":"EVALUATE — HCI uses HubSpot email bidding instead"}
  ],
  "management": [
    {"name":"Files & Photos","usage_status":"PRESUMED_ACTIVE","recommendation":"EXTEND — standardize folders, enable Google Drive sync"},
    {"name":"Schedule","usage_status":"NOT_OBSERVED","recommendation":"EXTEND — build standard templates by project type"},
    {"name":"Tasks & Punchlist","usage_status":"ACTIVE","sample_project":"655 Garmish","sample_task_count":45,"recommendation":"EXTEND — AI punchlist from Daily Logs, sync open count to HubSpot"},
    {"name":"Client Dashboard","usage_status":"AVAILABLE_UNUSED","sharing_status":"Not Shared","recommendation":"EXTEND — share with clients at project milestones"},
    {"name":"Daily Logs","usage_status":"ACTIVE","recommendation":"INTEGRATE — parse for punchlist items and change order triggers"},
    {"name":"Time","usage_status":"NOT_OBSERVED","recommendation":"EXTEND — enforce for labor cost tracking"},
    {"name":"Expenses","usage_status":"UNUSED","total_billable":0.00,"recommendation":"EXTEND — enforce for project cost tracking"},
    {"name":"Warranties & Claims","usage_status":"NOT_OBSERVED","recommendation":"EXTEND — activate at Closeout stage"}
  ],
  "finance": [
    {"name":"Invoices","usage_status":"MINIMAL","records":2,"sent":0,"drafts":2,"recommendation":"EXTEND — activate for milestone billing"},
    {"name":"Purchase Orders","usage_status":"UNUSED","records":0,"recommendation":"EXTEND — generate when subcontract executed"},
    {"name":"Change Orders","usage_status":"UNUSED","records":0,"recommendation":"EXTEND — high priority; risk and revenue impact"},
    {"name":"Retainers & Credits","usage_status":"UNUSED","records":0,"recommendation":"EXTEND — activate at contract signing"},
    {"name":"Budget","usage_status":"NOT_OBSERVED","recommendation":"EXTEND — highest value financial feature; activate immediately"}
  ],
  "reporting": [
    {"name":"Payments Report","available":true,"used":false},
    {"name":"Payouts Report","available":true,"used":false},
    {"name":"Open Invoices Report","available":true,"used":false},
    {"name":"Sales Tax Liability","available":true,"used":false},
    {"name":"Incoming Transactions by Project","available":true,"used":false},
    {"name":"Outgoing Transactions by Project","available":true,"used":false},
    {"name":"Time Billing by Team Member","available":true,"used":false},
    {"name":"Time Billing by Project","available":true,"used":false},
    {"name":"Selections Tracker Global Report","available":true,"used":false}
  ]
}
```

## FINANCIAL DOCUMENTS OBSERVED
```json
[
  {"id":"ES-0001","type":"Estimate","project":"212 Cleveland","amount":84924.13,"status":"Sent"},
  {"id":"ES-10002","type":"Estimate","project":"212 Cleveland","amount":0.00,"status":"Draft"},
  {"id":"ES-10004","type":"Estimate","project":"825 Cemetery Lane","amount":36000.00,"status":"Draft"},
  {"id":"IN-10001","type":"Invoice","amount":0.63,"status":"Draft"},
  {"id":"IN-10002","type":"Invoice","amount":0.00,"status":"Draft"}
]
```

## LEADS MODULE
```json
{
  "pipeline_stages": ["New","Followed Up","Connected","Meeting Scheduled","Estimate Sent","Won"],
  "inactive_stages": ["Snoozed","Archived"],
  "active_leads": 1,
  "archived_leads": 56,
  "homeowners_searching_area": 303,
  "active_lead_sample": {
    "name": "Shianne's Bathroom Remodeling project",
    "stage": "Followed Up",
    "source": "Houzz project match",
    "created": "2026-07-27",
    "last_activity": "334 days ago"
  },
  "note": "303 homeowners actively searching — significant unconverted opportunity"
}
```

## INTEGRATIONS AVAILABLE
```json
{
  "calendar_video": ["Google Meet","Zoom","GoTo Meeting","Microsoft Teams","8x8"],
  "business_integrations": [
    {"name":"QuickBooks Online","status":"AVAILABLE_NOT_CONNECTED","recommendation":"INTEGRATE — sync invoices and POs to accounting"},
    {"name":"Google Drive","status":"AVAILABLE_UNKNOWN","recommendation":"INTEGRATE — centralize project documents"},
    {"name":"Zapier","status":"AVAILABLE_BETA_NOT_CONFIGURED","recommendation":"CONFIGURE — bridge to HubSpot; trigger: new lead, project update, payment"},
    {"name":"Clipper Tool","status":"AVAILABLE","recommendation":"EVALUATE"}
  ],
  "zapier_triggers_available": ["New lead","Project update","Payment received"],
  "zapier_actions_available": ["Add CRM contact","Create calendar event","Send email"]
}
```

## TASK SAMPLE — 655 GARMISH (Active Ground-Up Project)
```json
{
  "project": "655 Garmish",
  "project_type": "Ground-Up Construction",
  "client": "Jay Nobrega",
  "tasks_total": 45,
  "tasks_completed": 1,
  "tasks_open": 44,
  "sample_tasks": [
    {"title":"Complete Laundry Room Fan Coil Installation","due":"2026-06-11","status":"Completed"},
    {"title":"Complete Remaining HVAC Rough-In","due":"2026-06-15","status":"Open"},
    {"title":"Complete Electrical Rough-In","due":"2026-06-15","status":"Open"},
    {"title":"Complete Fire Sprinkler Rough-In","due":"2026-06-15","status":"Open"},
    {"title":"Verify Elevator Shaft Dimensions","due":"2026-06-18","status":"Open"},
    {"title":"Confirm Elevator Equipment Delivery Date","due":"2026-06-18","status":"Open"},
    {"title":"Complete Plumbing Rough-In","due":null,"status":"Open"}
  ],
  "note": "Tasks linked to schedule slots. Assignees include Mike Mount (MM) and Eduardo Ruiz (ER)."
}
```

## AUTOMATION OPPORTUNITIES
```json
[
  {"id":"AO-HP-001","title":"HubSpot Deal to Houzz Pro Project Bridge","value":"HIGH","complexity":"MEDIUM","status":"P0_CRITICAL","description":"Auto-create Houzz Pro project when HubSpot deal moves to ROM Accepted/Job Won via Zapier"},
  {"id":"AO-HP-002","title":"Houzz Lead to HubSpot Contact Sync","value":"HIGH","complexity":"MEDIUM","status":"READY_TO_BUILD","description":"When Houzz lead reaches Connected stage sync to HubSpot as new Contact with Lifecycle Stage = Lead"},
  {"id":"AO-HP-003","title":"AI Lead Auto-Response","value":"HIGH","complexity":"MEDIUM","status":"READY_TO_BUILD","description":"Auto-reply to new Houzz leads within 5 minutes using AI-personalized message; 303 homeowners currently unconverted"},
  {"id":"AO-HP-004","title":"Contract Auto-Generation","value":"HIGH","complexity":"MEDIUM","status":"READY_TO_BUILD","description":"Auto-generate contract from template when HubSpot deal = Contract to Client; pre-fill from deal fields"},
  {"id":"AO-HP-005","title":"Change Order Activation","value":"HIGH","complexity":"LOW","status":"READY_TO_BUILD","description":"Activate change order workflow; AI draft from scope change description; alert if unsigned after 7 days"},
  {"id":"AO-HP-006","title":"Budget Module Activation","value":"HIGH","complexity":"MEDIUM","status":"READY_TO_BUILD","description":"Activate budget tracking on all active projects; sync estimate totals as starting budget"},
  {"id":"AO-HP-007","title":"QuickBooks Online Integration","value":"HIGH","complexity":"MEDIUM","status":"READY_TO_BUILD","description":"Connect Houzz Pro to QBO; sync invoices, POs, and payments to accounting"},
  {"id":"AO-HP-008","title":"AI Punchlist Generation from Daily Logs","value":"MEDIUM","complexity":"MEDIUM","status":"FUTURE_PHASE","description":"Parse last 30 days of daily logs for unresolved items; auto-create punchlist entries at Closeout stage"},
  {"id":"AO-HP-009","title":"Milestone Progress Invoice Automation","value":"HIGH","complexity":"LOW","status":"READY_TO_BUILD","description":"Auto-generate progress invoice at defined project milestones (50%, 75%, punch list complete)"},
  {"id":"AO-HP-010","title":"Schedule Template Library","value":"HIGH","complexity":"MEDIUM","status":"FUTURE_PHASE","description":"Build standard schedule templates by project type: Home Remodeling (8 phases), Ground-Up (12 phases)"}
]
```

## CRITICAL GAPS
```json
[
  {"gap":"No Houzz Pro to HubSpot integration","impact":"Dual manual data entry; 24 projects exist in both systems with no sync","priority":"P0"},
  {"gap":"Zero contracts created","impact":"Contract management happening outside platform; no digital tracking or e-signature","priority":"P1"},
  {"gap":"Zero invoices sent","impact":"Client billing not tracked in Houzz Pro; revenue data siloed","priority":"P1"},
  {"gap":"Zero change orders","impact":"Scope changes managed ad hoc; revenue and risk exposure untracked","priority":"P1"},
  {"gap":"Budget module inactive","impact":"No real-time project profitability visibility","priority":"P1"},
  {"gap":"QuickBooks not connected","impact":"Accounting data not synced; manual reconciliation required","priority":"P2"},
  {"gap":"303 unconverted homeowners","impact":"Inbound leads not being captured or responded to","priority":"P1"},
  {"gap":"Zapier not configured","impact":"No automation bridge to HubSpot or other systems","priority":"P1"}
]
```

## SYSTEM OWNERSHIP
```json
{
  "system": "Houzz Pro",
  "owner": "Chris Hendrickson (Super Admin) + Buck Adams (Admin)",
  "primary_use": "Project management, field operations, financial documents",
  "ai_os_integration": "NONE — no current connection",
  "next_actions_for_claude_code": [
    "Design AO-HP-001: Zapier Zap — HubSpot Deal Won triggers Houzz Pro project creation",
    "Design AO-HP-002: Zapier Zap — Houzz Pro lead Connected triggers HubSpot Contact creation",
    "Spec AO-HP-004: Contract template structure for auto-generation",
    "Spec AO-HP-005: Change order activation workflow",
    "Spec AO-HP-006: Budget activation and estimate sync process",
    "Spec AO-HP-007: QuickBooks Online connection configuration"
  ]
}
```

---
*Browser Claude — Discovery Agent | Read-only. Do not modify production systems.*

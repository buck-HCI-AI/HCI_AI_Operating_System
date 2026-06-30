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

Houzz Pro is HCI's project management, field operations, and financial document platform. 24 active projects, 18 team members. Significant feature underutilization: 0 contracts, 0 invoices sent, 0 purchase orders, 0 change orders, 0 schedules. Tasks & Punchlist actively used (45 tasks observed on 655 Garmish). No integration between Houzz Pro and HubSpot. Zapier available but not configured. QuickBooks Online available but not connected.

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
  "financial_documents_total": 5,
  "contracts_created": 0,
  "invoices_sent": 0,
  "purchase_orders": 0,
  "change_orders": 0,
  "quickbooks_connected": false,
  "zapier_configured": false
}
```

## TEAM ROSTER

```json
{
  "team": [
    {"name":"Chris Hendrickson","email":"chris@hendricksoninc.com","role":"Super Admin"},
    {"name":"Mike Mount","email":"mmount@hendricksoninc.com","role":"Admin"},
    {"name":"Adam Malmgren","email":"adam@hendricksoninc.com","role":"Admin"},
    {"name":"Jason Malik","email":"jmalik@hendricksoninc.com","role":"Admin"},
    {"name":"Eduardo Ruiz","email":"eduardo@hendricksoninc.com","role":"Admin"},
    {"name":"Nelly Caballero","email":"nelly@hendricksoninc.com","role":"Admin"},
    {"name":"Will Royer","email":"wroyer@hendricksoninc.com","role":"Admin"},
    {"name":"Angel Cruz","email":"acruz@hendricksoninc.com","role":"Admin"},
    {"name":"Dillon Hendrickson","email":"dillon@hendricksoninc.com","role":"Admin"},
    {"name":"Elisabeth White","email":"elisabeth@hendricksoninc.com","role":"Admin"},
    {"name":"Buck Adams","email":"buck@hendricksoninc.com","role":"Admin"},
    {"name":"Frankie Arvesen","email":"frankie@hendricksoninc.com","role":"Field Crew"},
    {"name":"Michael Edinger","email":"michael@aliusdc.com","role":"Field Crew"},
    {"name":"Dante De Lacruz","email":"dantedelacruz13@gmail.com","role":"Field Crew"},
    {"name":"Tony Pensamiento","email":"tonypensamiento2@gmail.com","role":"Field Crew"},
    {"name":"Kaleb St Yves","email":"kaleb@hendricksoninc.com","role":"Field Crew"},
    {"name":"Frankie Arvesen","email":"frankie@hendricksoninc.com","role":"Field Crew"},
    {"name":"traff@hendricksoninc.com","role":"Admin"}
  ]
}
```

## PROJECT INVENTORY

```json
{
  "projects": [
    {"name":"574 Johnson Drive","client":null,"created":"2026-06-03","status":"Open"},
    {"name":"606 S Starwood","client":"Jennifer Olson","location":"Aspen, CO","created":"2026-05-06","status":"Open"},
    {"name":"349 Draw Drive","client":null,"created":"2026-04-29","status":"Open"},
    {"name":"246 Gallo Way","client":"Johnathan Taylor","created":"2026-04-06","status":"Open"},
    {"name":"101 Francis","client":"Adnan Rawjee","location":"Aspen, CO","created":"2026-03-05","type":"Home Remodeling","status":"Open"},
    {"name":"Cemetery Lane 825","client":null,"created":"2026-01-20","status":"Open"},
    {"name":"370 Gerbaz Way","client":"Matt Bruckel","location":"Snowmass, CO","created":"2026-01-02","type":"Home Remodeling","status":"Open"},
    {"name":"Hendrickson Carbondale Catherine Storage","created":"2025-12-30","status":"Open"},
    {"name":"HCI Misc","created":"2025-12-12","status":"Open"},
    {"name":"825 Cemetery Ln.","client":"Alan Klien","created":"2025-10-21","status":"Open"},
    {"name":"1096 Waters","created":"2025-10-02","status":"Open"},
    {"name":"655 Garmish","client":"Jay Nobrega","location":"Aspen, CO","created":"2025-09-08","type":"Ground-Up Construction","status":"Open","active_tasks":45},
    {"name":"1762 Red Mountain Road","client":"Ted Bigos & Irwin Gold","created":"2025-08-27","status":"Open"},
    {"name":"Vision Builders","created":"2025-08-25","status":"Open"},
    {"name":"813 McSkimming","client":"Ray Spitzley","location":"Aspen, CO","created":"2025-05-21","type":"Ground-Up Construction","status":"Open"},
    {"name":"Aspen Brewing Company","created":"2025-05-02","status":"Open"},
    {"name":"918 South Mill EXT.","created":"2025-03-28","status":"Open"},
    {"name":"501 East Hyman","created":"2025-03-28","status":"Open"},
    {"name":"655 South Garmisch","client":"Mexamer","location":"Aspen, CO","created":"2025-03-24","type":"Ground-Up Construction","status":"Open"},
    {"name":"1355 Riverside","client":"Oakleigh Ryan","status":"Open"}
  ],
  "notes": {
    "projects_missing_client": 10,
    "projects_missing_type": 17,
    "hubspot_overlap": "Project names match HubSpot deal names — confirms dual manual entry"
  }
}
```

## MODULE INVENTORY

```json
{
  "planning_modules": [
    {"name":"Contracts","status":"UNUSED","records":0,"recommendation":"EXTEND — auto-generate from HubSpot deal stage trigger"},
    {"name":"Estimates","status":"LOW","records":3,"sent":1,"recommendation":"EXTEND — mandatory step in project workflow"},
    {"name":"Takeoffs","status":"UNKNOWN","recommendation":"EVALUATE"},
    {"name":"3D Floor Plans","status":"UNKNOWN","recommendation":"IGNORE"},
    {"name":"Mood Boards","status":"UNKNOWN","recommendation":"IGNORE"},
    {"name":"Selection Boards","status":"UNKNOWN","recommendation":"EXTEND — automate client reminder cadence"},
    {"name":"Selections Tracker","status":"UNKNOWN","export_formats":["XLS","CSV"],"recommendation":"INTEGRATE — parse weekly export for procurement alerts"},
    {"name":"Bids","status":"UNUSED","recommendation":"EVALUATE — HCI uses HubSpot email-based bidding"}
  ],
  "management_modules": [
    {"name":"Files & Photos","status":"PRESUMED_ACTIVE","recommendation":"EXTEND — standardize folder structure"},
    {"name":"Schedule","status":"UNUSED","recommendation":"EXTEND — build templates by project type"},
    {"name":"Tasks & Punchlist","status":"ACTIVE","sample_project":"655 Garmish","tasks_observed":45,"recommendation":"EXTEND — AI punchlist generation from Daily Logs"},
    {"name":"Client Dashboard","status":"NOT_SHARED","recommendation":"EXTEND — auto-share at project milestones"},
    {"name":"Daily Logs","status":"ACTIVE","recommendation":"INTEGRATE — parse for AI site report generation"},
    {"name":"Time","status":"UNUSED","recommendation":"EXTEND — field crew time tracking"},
    {"name":"Expenses","status":"UNUSED","total_billable":0,"recommendation":"EXTEND — activate for project cost tracking"},
    {"name":"Warranties & Claims","status":"UNUSED","recommendation":"EXTEND — post-closeout workflow"}
  ],
  "finance_modules": [
    {"name":"Invoices","status":"LOW","records":2,"sent":0,"recommendation":"EXTEND — activate milestone invoicing"},
    {"name":"Purchase Orders","status":"UNUSED","records":0,"recommendation":"EXTEND — auto-generate on subcontract execution"},
    {"name":"Change Orders","status":"UNUSED","records":0,"recommendation":"EXTEND — AI-assisted change order drafting"},
    {"name":"Retainers & Credits","status":"UNUSED","records":0,"recommendation":"EXTEND — auto-request on contract signing"},
    {"name":"Budget","status":"UNUSED","recommendation":"EXTEND — highest value financial feature; activate immediately"}
  ]
}
```

## FINANCIAL DOCUMENTS

```json
{
  "estimates": [
    {"id":"ES-0001","project":"212 Cleveland","amount":84924.13,"status":"Sent"},
    {"id":"ES-10002","project":"212 Cleveland","amount":0,"status":"Draft"},
    {"id":"ES-10004","project":"825 Cemetery Lane","amount":36000.00,"status":"Draft"}
  ],
  "invoices": [
    {"id":"IN-10001","amount":0.63,"status":"Draft"},
    {"id":"IN-10002","amount":0,"status":"Draft"}
  ]
}
```

## LEADS MODULE

```json
{
  "leads": {
    "active_total": 1,
    "archived_total": 56,
    "pipeline_stages": ["New","Followed Up","Connected","Meeting Scheduled","Estimate Sent","Won","Snoozed","Archived"],
    "active_lead": {
      "name": "Shianne's Bathroom Remodeling project",
      "stage": "Followed Up",
      "source": "Houzz project match",
      "created": "2025-07-27"
    },
    "market_opportunity": "303 homeowners searching for pros in HCI area — not being captured"
  }
}
```

## INTEGRATIONS AVAILABLE

```json
{
  "available_integrations": [
    {"name":"QuickBooks Online","status":"NOT_CONNECTED","recommendation":"INTEGRATE — sync invoices and expenses"},
    {"name":"Zapier (BETA)","status":"NOT_CONFIGURED","recommendation":"CONFIGURE — bridge to HubSpot immediately"},
    {"name":"Google Drive","status":"UNKNOWN","recommendation":"CONNECT — centralize project file storage"},
    {"name":"Google Meet","status":"AVAILABLE","recommendation":"MAINTAIN"},
    {"name":"Zoom","status":"AVAILABLE","recommendation":"MAINTAIN"},
    {"name":"Microsoft Teams","status":"AVAILABLE","recommendation":"MAINTAIN"},
    {"name":"8x8","status":"AVAILABLE","recommendation":"EVALUATE"},
    {"name":"Clipper Tool","status":"AVAILABLE","recommendation":"EVALUATE"}
  ]
}
```

## AUTOMATION OPPORTUNITIES

```json
{
  "automation_opportunities": [
    {"id":"AO-HP-001","title":"HubSpot Deal to Houzz Pro Project Auto-Create","description":"When HubSpot deal reaches ROM Accepted/Job Won, auto-create Houzz Pro project via Zapier","value":"HIGH","complexity":"MEDIUM","status":"READY_TO_DESIGN"},
    {"id":"AO-HP-002","title":"Houzz Pro Lead to HubSpot Contact Sync","description":"When Houzz lead reaches Connected stage, create or update HubSpot contact","value":"HIGH","complexity":"MEDIUM","status":"READY_TO_DESIGN"},
    {"id":"AO-HP-003","title":"AI Lead Response Auto-Reply","description":"New Houzz lead received — AI generates personalized response within 5 minutes","value":"HIGH","complexity":"MEDIUM","status":"READY_TO_DESIGN"},
    {"id":"AO-HP-004","title":"Contract Auto-Generation","description":"When HubSpot deal reaches Contract to Client stage, generate Houzz Pro contract","value":"HIGH","complexity":"MEDIUM","status":"READY_TO_DESIGN"},
    {"id":"AO-HP-005","title":"Milestone Invoice Auto-Generation","description":"At defined project milestones, auto-generate progress invoice","value":"HIGH","complexity":"MEDIUM","status":"READY_TO_DESIGN"},
    {"id":"AO-HP-006","title":"Change Order AI Drafting","description":"Field describes scope change in natural language, AI generates formal change order","value":"HIGH","complexity":"MEDIUM","status":"READY_TO_DESIGN"},
    {"id":"AO-HP-007","title":"AI Punchlist Generation from Daily Logs","description":"Scan last 30 days of daily logs for unresolved items, auto-create punchlist","value":"HIGH","complexity":"MEDIUM","status":"READY_TO_DESIGN"},
    {"id":"AO-HP-008","title":"Budget Activation and Sync","description":"Activate budget module, auto-populate from estimate, sync totals to HubSpot deal amount","value":"HIGH","complexity":"LOW","status":"READY_TO_BUILD"},
    {"id":"AO-HP-009","title":"Selections Tracker Weekly Parse","description":"Export Selections Tracker weekly, parse with n8n, generate procurement bottleneck report","value":"MEDIUM","complexity":"MEDIUM","status":"READY_TO_DESIGN"},
    {"id":"AO-HP-010","title":"Schedule Template Library","description":"Build schedule templates by project type (Home Remodeling 8-phase, Ground-Up 12-phase)","value":"HIGH","complexity":"LOW","status":"READY_TO_BUILD"}
  ]
}
```

## CRITICAL GAPS

```json
{
  "critical_gaps": [
    {"priority":"P0","gap":"No Houzz Pro to HubSpot integration","impact":"Manual dual entry for all 24 projects; data drift"},
    {"priority":"P0","gap":"Zapier not configured","impact":"Bridge to HubSpot blocked; all cross-platform data is manual"},
    {"priority":"P1","gap":"Budget module not activated","impact":"No real-time project profitability visibility"},
    {"priority":"P1","gap":"Contracts unused","impact":"HCI managing contracts outside platform; no e-signature tracking"},
    {"priority":"P1","gap":"Change orders unused","impact":"Scope changes managed by email/paper; revenue and dispute risk"},
    {"priority":"P1","gap":"303 local homeowners not captured","impact":"Significant lead pipeline not being worked"},
    {"priority":"P2","gap":"QuickBooks not connected","impact":"Financial reconciliation is fully manual"}
  ]
}
```

## NEXT ACTIONS FOR CLAUDE CODE

1. Design AO-HP-001: HubSpot Deal → Houzz Pro Project bridge via Zapier
2. Design AO-HP-002: Houzz Lead → HubSpot Contact sync
3. Configure Zapier connection between HubSpot and Houzz Pro (BETA)
4. Build AO-HP-008: Activate Budget module and sync to HubSpot deal amount
5. Build AO-HP-010: Schedule template library by project type
6. Evaluate QuickBooks Online connection for invoice/expense sync

---
*Browser Claude — Discovery Agent | Read-only. Do not modify production systems.*

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

---

## SUMMARY

Houzz Pro is HCI's project management, field operations, and financial document
platform. 24 active projects. 18 team members (3 Field Crew, 14 Admin, 1 Super Admin).
Significant feature underutilization: 0 contracts, 0 invoices sent, 0 purchase orders,
0 change orders, 0 schedules built. Tasks & Punchlist is actively used (45 tasks on
655 Garmish alone). No integration between Houzz Pro and HubSpot — this is the P0 gap
in the HCI AI Operating System. Zapier is available in BETA but not configured.
QuickBooks Online integration available but not connected.

---

## ACCOUNT METADATA

```json
{
  "platform": "Houzz Pro",
  "company": "Hendrickson Construction Inc.",
  "location": "Aspen, Colorado",
  "base_url": "https://pro.houzz.com",
  "user_name": "webuser_185947852",
  "admin_email": "buck@hendricksoninc.com",
  "team_seats_total": "Unlimited",
  "team_seats_used": 18,
  "active_projects": 24,
  "active_leads": 1,
  "archived_leads": 56,
  "financial_documents_total": 5,
  "contracts_created": 0,
  "invoices_sent": 0,
  "purchase_orders_created": 0,
  "change_orders_created": 0,
  "quickbooks_connected": false,
  "zapier_configured": false,
  "zapier_status": "BETA — available, not configured",
  "google_drive_integration": "available",
  "dedicated_support": "Emily Draper (dedicatedsupport@houzz.com)"
}
```

---

## TEAM ROSTER

```json
{
  "team_members": [
    {"name": "Chris Hendrickson", "email": "chris@hendricksoninc.com", "role": "Super Admin", "status": "Active"},
    {"name": "Mike Mount", "email": "mmount@hendricksoninc.com", "role": "Admin", "status": "Active", "joined": "2024-11-19"},
    {"name": "Adam Malmgren", "email": "adam@hendricksoninc.com", "role": "Admin", "status": "Active", "joined": "2025-01-15"},
    {"name": "Jason Malik", "email": "jmalik@hendricksoninc.com", "role": "Admin", "status": "Active", "joined": "2025-02-27"},
    {"name": "Eduardo Ruiz", "email": "eduardo@hendricksoninc.com", "role": "Admin", "status": "Active", "joined": "2025-04-08"},
    {"name": "Nelly Caballero", "email": "nelly@hendricksoninc.com", "role": "Admin", "status": "Active", "joined": "2025-04-24"},
    {"name": "Will Royer", "email": "wroyer@hendricksoninc.com", "role": "Admin", "status": "Active", "joined": "2025-05-20"},
    {"name": "Angel Cruz", "email": "acruz@hendricksoninc.com", "role": "Admin", "status": "Active", "joined": "2025-05-20"},
    {"name": "Dillon Hendrickson", "email": "dillon@hendricksoninc.com", "role": "Admin", "status": "Active", "joined": "2025-06-16"},
    {"name": "Elisabeth White", "email": "elisabeth@hendricksoninc.com", "role": "Admin", "status": "Active", "joined": "2025-09-30"},
    {"name": "Buck Adams", "email": "buck@hendricksoninc.com", "role": "Admin", "status": "Active", "joined": "2026-04-26"},
    {"name": "Michael Edinger", "email": "michael@aliusdc.com", "role": "Field Crew", "status": "Active", "joined": "2025-03-09"},
    {"name": "Dante De Lacruz", "email": "dantedelacruz13@gmail.com", "role": "Field Crew", "status": "Active", "joined": "2025-02-24"},
    {"name": "Tony Pensamiento", "email": "tonypensamiento2@gmail.com", "role": "Field Crew", "status": "Active", "joined": "2026-03-05"},
    {"name": "Kaleb St Yves", "email": "kaleb@hendricksoninc.com", "role": "Field Crew", "status": "Active", "joined": "2026-03-09"},
    {"name": "Frankie Arvesen", "email": "frankie@hendricksoninc.com", "role": "Field Crew", "status": "Active", "joined": "2026-04-29"},
    {"name": "traff@hendricksoninc.com", "role": "Admin", "status": "Active", "joined": "2026-06-01"},
    {"name": "Fancisco Ruiz", "email": "franciscojruiz29@icloud.com", "role": "Field Crew", "status": "Pending", "invited": "2026-04-29"}
  ]
}
```

---

## PROJECT INVENTORY

```json
{
  "total_projects": 24,
  "status_all": "Open",
  "projects_missing_client": 10,
  "projects_missing_type": 17,
  "project_types_in_use": ["Home Remodeling", "Ground-Up Construction"],
  "note": "Project names align with HubSpot deal names — confirms dual manual entry across systems",
  "projects": [
    {"name": "574 Johnson Drive", "client": null, "created": "2026-06-03", "type": null},
    {"name": "606 S Starwood", "client": "Jennifer Olson", "location": "Aspen, CO", "created": "2026-05-06"},
    {"name": "349 Draw Drive", "client": null, "created": "2026-04-29"},
    {"name": "246 Gallo Way", "client": "Johnathan Taylor", "created": "2026-04-06"},
    {"name": "101 Francis", "client": "Adnan Rawjee", "location": "Aspen, CO", "created": "2026-03-05", "type": "Home Remodeling"},
    {"name": "Cemetery Lane 825", "client": null, "created": "2026-01-20"},
    {"name": "370 Gerbaz Way", "client": "Matt Bruckel", "location": "Snowmass, CO", "created": "2026-01-02", "type": "Home Remodeling"},
    {"name": "Hendrickson Carbondale Catherine Storage", "client": null, "created": "2025-12-30"},
    {"name": "HCI Misc", "client": null, "created": "2025-12-12"},
    {"name": "825 Cemetery Ln.", "client": "Alan Klien", "created": "2025-10-21", "task_count_observed": 1},
    {"name": "1096 Waters", "client": null, "created": "2025-10-02"},
    {"name": "655 Garmish", "client": "Jay Nobrega", "email": "jay@mexamer.com", "location": "655 South Garmisch Street, Aspen, CO 81611", "created": "2025-09-08", "type": "Ground-Up Construction", "task_count": 45, "tasks_open": 44, "tasks_completed": 1},
    {"name": "1762 Red Mountain Road", "client": "Ted Bigos & Irwin Gold", "created": "2025-08-27"},
    {"name": "Vision Builders", "client": null, "created": "2025-08-25"},
    {"name": "813 McSkimming", "client": "Ray Spitzley", "location": "Aspen, CO", "created": "2025-05-21", "type": "Ground-Up Construction"},
    {"name": "Aspen Brewing Company", "client": null, "created": "2025-05-02"},
    {"name": "918 South Mill EXT.", "client": null, "created": "2025-03-28"},
    {"name": "501 East Hyman", "client": null, "created": "2025-03-28"},
    {"name": "655 South Garmisch", "client": "Mexamer", "location": "Aspen, CO", "created": "2025-03-24", "type": "Ground-Up Construction"},
    {"name": "1355 Riverside", "client": "Oakleigh Ryan"},
    {"name": "Aspen Brewing Company", "client": null}
  ]
}
```

---

## MODULE INVENTORY & USAGE STATUS

```json
{
  "planning_modules": [
    {
      "name": "Contracts",
      "url_pattern": "/manage/projects/{id}/contracts",
      "usage_status": "UNUSED",
      "records": 0,
      "hci_recommendation": "EXTEND",
      "ai_os_action": "Auto-generate contract from HubSpot deal stage trigger",
      "value": "HIGH",
      "complexity": "MEDIUM"
    },
    {
      "name": "Estimates",
      "url_pattern": "/manage/projects/{id}/estimates",
      "usage_status": "LOW",
      "records_total": 3,
      "records_sent": 1,
      "records_draft": 2,
      "financial_documents": [
        {"id": "ES-0001", "project": "212 Cleveland", "amount": 84924.13, "status": "Sent"},
        {"id": "ES-10002", "project": "212 Cleveland", "amount": 0.00, "status": "Draft"},
        {"id": "ES-10004", "project": "825 Cemetery Lane", "amount": 36000.00, "status": "Draft"}
      ],
      "hci_recommendation": "EXTEND",
      "ai_os_action": "AI estimate generation from scope + historical unit costs; sync total to HubSpot deal amount",
      "value": "HIGH",
      "complexity": "MEDIUM"
    },
    {
      "name": "Takeoffs",
      "usage_status": "UNKNOWN",
      "hci_recommendation": "EVALUATE",
      "value": "MEDIUM",
      "complexity": "HIGH"
    },
    {
      "name": "3D Floor Plans",
      "usage_status": "UNKNOWN",
      "hci_recommendation": "IGNORE",
      "value": "LOW",
      "complexity": "MEDIUM"
    },
    {
      "name": "Mood Boards",
      "usage_status": "UNKNOWN",
      "hci_recommendation": "IGNORE",
      "value": "LOW",
      "complexity": "LOW"
    },
    {
      "name": "Selection Boards",
      "url_pattern": "/manage/projects/{id}/selections",
      "usage_status": "UNKNOWN",
      "hci_recommendation": "EXTEND",
      "ai_os_action": "Automate selection reminder cadence; block procurement until selections approved",
      "value": "HIGH",
      "complexity": "LOW"
    },
    {
      "name": "Selections Tracker",
      "url_pattern": "/manage/reports/",
      "usage_status": "UNKNOWN",
      "export_formats": ["XLS", "CSV"],
      "hci_recommendation": "INTEGRATE",
      "ai_os_action": "Parse weekly export for procurement bottleneck alerts",
      "value": "MEDIUM",
      "complexity": "MEDIUM"
    },
    {
      "name": "Bids",
      "url_pattern": "/manage/projects/{id}/bids",
      "usage_status": "UNKNOWN",
      "hci_recommendation": "EVALUATE",
      "note": "HCI uses HubSpot email-based bidding; Houzz Pro Bids requires sub adoption of platform",
      "value": "MEDIUM",
      "complexity": "HIGH"
    }
  ],
  "management_modules": [
    {
      "name": "Files & Photos",
      "url_pattern": "/manage/projects/{id}/files",
      "usage_status": "PRESUMED_ACTIVE",
      "hci_recommendation": "EXTEND",
      "ai_os_action": "Standardize folder structure template; enable Google Drive sync; auto-share milestone photos with client",
      "value": "MEDIUM",
      "complexity": "LOW"
    },
    {
      "name": "Schedule",
      "url_pattern": "/manage/projects/{id}/schedule",
      "usage_status": "UNKNOWN",
      "hci_recommendation": "EXTEND",
      "ai_os_action": "Auto-generate schedule from project type template; AI delay detection with cascade alerts",
      "value": "HIGH",
      "complexity": "MEDIUM"
    },
    {
      "name": "Tasks & Punchlist",
      "url_pattern": "/manage/tasks/projects/{id}",
      "usage_status": "ACTIVE",
      "sample_project": "655 Garmish",
      "sample_task_count": 45,
      "sample_tasks_open": 44,
      "sample_tasks_completed": 1,
      "sample_tasks": [
        "Widow Measurments (Open, due 2026-03-23)",
        "Complete Laundry Room Fan Coil Installation (Completed, 2026-06-11)",
        "Complete Closet Fan Coil Installation (Open, 2026-06-11)",
        "Complete Electrical Rough-In (Open, 2026-06-15)",
        "Complete Fire Sprinkler Rough-In (Open, 2026-06-15)",
        "Confirm Elevator Equipment Delivery Date (Open, 2026-06-18)",
        "Create Rough-In Readiness Checklist (Open, no date)"
      ],
      "hci_recommendation": "EXTEND",
      "ai_os_action": "AI punchlist generation from Daily Logs; photo evidence enforcement; sync open count to HubSpot deal",
      "value": "HIGH",
      "complexity": "MEDIUM"
    },
    {
      "name": "Client Dashboard",
      "url_pattern": "/manage/projects/{id}/client-dashboard",
      "usage_status": "NOT_SHARED",
      "sharing_status": "Not Shared (observed on 655 Garmish)",
      "hci_recommendation": "EXTEND",
      "ai_os_action": "Auto-share dashboard when project reaches Construction stage; auto-populate with estimate, schedule, photos",
      "value": "HIGH",
      "complexity": "LOW"
    },
    {
      "name": "Subcontractor Dashboard",
      "url_pattern": "/manage/projects/{id}/subcontractor-dashboard",
      "usage_status": "UNKNOWN",
      "hci_recommendation": "EXTEND",
      "ai_os_action": "Auto-populate with scope, schedule, and document links from HubSpot deal data",
      "value": "MEDIUM",
      "complexity": "MEDIUM"
    },
    {
      "name": "Daily Logs",
      "url_pattern": "/manage/projects/{id}/daily-log",
      "usage_status": "ACTIVE",
      "hci_recommendation": "EXTEND",
      "ai_os_action": "AI scan of daily logs for unresolved issues; auto-create punchlist items; weekly AI summary to PM",
      "value": "HIGH",
      "complexity": "MEDIUM"
    },
    {
      "name": "Time Tracking",
      "url_pattern": "/manage/projects/{id}/time",
      "usage_status": "UNKNOWN",
      "hci_recommendation": "EXTEND",
      "ai_os_action": "Auto-generate time billing report; alert when project labor hours exceed budget",
      "value": "MEDIUM",
      "complexity": "LOW"
    },
    {
      "name": "Expenses",
      "url_pattern": "/manage/projects/{id}/expenses",
      "usage_status": "UNUSED",
      "total_billable_observed": 0.00,
      "hci_recommendation": "EXTEND",
      "ai_os_action": "Auto-categorize expenses by CSI division; flag non-budgeted expenses for approval",
      "value": "MEDIUM",
      "complexity": "LOW"
    },
    {
      "name": "Warranties & Claims",
      "url_pattern": "/manage/projects/{id}/warranties",
      "usage_status": "UNKNOWN",
      "hci_recommendation": "EXTEND",
      "ai_os_action": "Auto-create warranty record at project closeout; set expiration reminders for 1-year warranty",
      "value": "MEDIUM",
      "complexity": "LOW"
    }
  ],
  "finance_modules": [
    {
      "name": "Invoices",
      "usage_status": "UNUSED_SENT",
      "records": 2,
      "records_sent": 0,
      "financial_documents": [
        {"id": "IN-10001", "amount": 0.63, "status": "Draft"},
        {"id": "IN-10002", "amount": 0.00, "status": "Draft"}
      ],
      "hci_recommendation": "EXTEND",
      "ai_os_action": "Auto-generate progress invoices at milestone stages; sync status to HubSpot deal",
      "value": "HIGH",
      "complexity": "MEDIUM"
    },
    {
      "name": "Purchase Orders",
      "usage_status": "UNUSED",
      "records": 0,
      "hci_recommendation": "EXTEND",
      "ai_os_action": "Auto-generate PO when HubSpot subcontract_status = Fully Executed",
      "value": "MEDIUM",
      "complexity": "MEDIUM"
    },
    {
      "name": "Change Orders",
      "usage_status": "UNUSED",
      "records": 0,
      "hci_recommendation": "EXTEND",
      "ai_os_action": "AI drafts change order from scope description; auto-update HubSpot deal amount when approved",
      "value": "HIGH",
      "complexity": "LOW"
    },
    {
      "name": "Retainers & Credits",
      "usage_status": "UNUSED",
      "records": 0,
      "hci_recommendation": "EXTEND",
      "ai_os_action": "Auto-request retainer when contract signed; amount = 10% of contract value",
      "value": "MEDIUM",
      "complexity": "LOW"
    },
    {
      "name": "Budget",
      "usage_status": "UNKNOWN",
      "hci_recommendation": "EXTEND",
      "ai_os_action": "Auto-populate from approved estimate; alert PM when actuals exceed 10% of budget line item",
      "value": "HIGH",
      "complexity": "MEDIUM"
    }
  ]
}
```

---

## LEADS MODULE (Houzz Pro)

```json
{
  "leads": {
    "active_total": 1,
    "stages": {
      "New": 0,
      "Followed Up": 1,
      "Connected": 0,
      "Meeting Scheduled": 0,
      "Estimate Sent": 0,
      "Won": 0
    },
    "inactive": {
      "Snoozed": 0,
      "Archived": 56
    },
    "market_opportunity": "303 homeowners searching for pros in HCI area",
    "active_lead_sample": {
      "name": "Shianne's Bathroom Remodeling project",
      "stage": "Followed Up",
      "source": "Houzz project match",
      "created": "2025-07-27",
      "last_activity": "334 days ago"
    },
    "hci_recommendation": "INTEGRATE",
    "ai_os_action": "Auto-sync Connected+ leads to HubSpot Contacts; AI lead scoring; auto-reply within 5 minutes",
    "value": "HIGH",
    "complexity": "MEDIUM"
  }
}
```

---

## FINANCIAL REPORTS MODULE

```json
{
  "financial_reports": {
    "url": "https://pro.houzz.com/manage/reports/",
    "available_reports": [
      {"name": "Payments", "description": "Incoming and outgoing payments, amounts invoiced, remaining liability"},
      {"name": "Payouts", "description": "All payouts to bank account"},
      {"name": "Open Invoices", "description": "Unpaid and partially paid invoices with aging"},
      {"name": "Sales Tax Liability", "description": "Sales tax owed to government"},
      {"name": "Incoming Transactions by Project", "description": "Incoming transactions grouped by project"},
      {"name": "Outgoing Transactions by Project", "description": "Outgoing transactions grouped by project"},
      {"name": "Time Billing by Team Member", "description": "Time tracked grouped by team member"},
      {"name": "Time Billing by Project", "description": "Time tracked grouped by project"},
      {"name": "Selections Tracker Global Report", "description": "Consolidated XLS/CSV across all projects"}
    ],
    "usage_status": "UNUSED — no financial transactions processed through Houzz Pro",
    "hci_recommendation": "EXTEND",
    "ai_os_action": "Parse Selections Tracker weekly export; parse Open Invoices for AR alerts",
    "value": "HIGH",
    "complexity": "LOW"
  }
}
```

---

## INTEGRATIONS AVAILABLE

```json
{
  "integrations": {
    "calendar_video": [
      {"name": "Google Meet", "status": "available"},
      {"name": "Zoom", "status": "available"},
      {"name": "GoTo Meeting", "status": "available"},
      {"name": "Microsoft Teams", "status": "available"},
      {"name": "8x8", "status": "available"}
    ],
    "productivity": [
      {
        "name": "QuickBooks Online",
        "status": "AVAILABLE_NOT_CONNECTED",
        "hci_recommendation": "CONNECT — sync invoices and payments to QuickBooks for accounting",
        "value": "HIGH",
        "complexity": "LOW"
      },
      {
        "name": "Google Drive",
        "status": "AVAILABLE",
        "hci_recommendation": "CONNECT — centralize project file storage",
        "value": "MEDIUM",
        "complexity": "LOW"
      },
      {
        "name": "Zapier",
        "status": "AVAILABLE_BETA_NOT_CONFIGURED",
        "supported_triggers": ["new lead", "project update", "payment"],
        "hci_recommendation": "CONFIGURE — bridge Houzz Pro to HubSpot for project sync",
        "value": "HIGH",
        "complexity": "MEDIUM"
      },
      {
        "name": "Clipper Tool",
        "status": "AVAILABLE",
        "description": "Browser extension to clip inspiration to projects",
        "hci_recommendation": "IGNORE",
        "value": "LOW"
      }
    ],
    "critical_missing_integration": {
      "description": "No HubSpot connector for Houzz Pro exists natively",
      "workaround_options": ["Zapier (BETA)", "n8n via Houzz Pro API (if available)", "Custom webhook bridge"],
      "priority": "P0"
    }
  }
}
```

---

## TEAM CHAT MODULE

```json
{
  "team_chat": {
    "url": "/teamchat/channels/all",
    "usage_status": "INACTIVE",
    "observation": "No messages in past 3 months",
    "hci_recommendation": "IGNORE or REPLACE with HCI AI OS internal messaging",
    "value": "LOW",
    "complexity": "LOW"
  }
}
```

---

## AUTOMATION OPPORTUNITY REGISTER

```json
{
  "automation_opportunities": [
    {
      "id": "AO-HP-001",
      "title": "HubSpot Deal to Houzz Pro Project Auto-Create",
      "description": "When HubSpot deal moves to ROM Accepted/Job Won, auto-create Houzz Pro project with matching metadata",
      "trigger": "HubSpot deal stage change",
      "bridge": "Zapier (Houzz Pro trigger) + n8n (HubSpot source)",
      "value": "HIGH",
      "complexity": "MEDIUM",
      "status": "ARCHITECTURE_DESIGN_NEEDED",
      "priority": "P0"
    },
    {
      "id": "AO-HP-002",
      "title": "Houzz Pro Lead to HubSpot Contact Auto-Sync",
      "description": "When Houzz Pro lead reaches Connected stage, auto-create HubSpot contact and deal",
      "trigger": "Houzz Pro lead stage change via Zapier",
      "value": "HIGH",
      "complexity": "MEDIUM",
      "status": "READY_TO_CONFIGURE",
      "priority": "P1"
    },
    {
      "id": "AO-HP-003",
      "title": "AI Lead Auto-Reply",
      "description": "When new Houzz Pro lead arrives, AI generates personalized reply within 5 minutes",
      "value": "HIGH",
      "complexity": "MEDIUM",
      "status": "READY_TO_BUILD",
      "priority": "P1"
    },
    {
      "id": "AO-HP-004",
      "title": "Contract Auto-Generation",
      "description": "When HubSpot deal moves to Contract to Client, auto-generate Houzz Pro contract from template",
      "value": "HIGH",
      "complexity": "MEDIUM",
      "status": "ARCHITECTURE_DESIGN_NEEDED",
      "priority": "P1"
    },
    {
      "id": "AO-HP-005",
      "title": "Client Dashboard Auto-Share",
      "description": "When project reaches Construction stage, auto-share Client Dashboard and send access link",
      "value": "HIGH",
      "complexity": "LOW",
      "status": "READY_TO_BUILD",
      "priority": "P2"
    },
    {
      "id": "AO-HP-006",
      "title": "AI Daily Log to Punchlist",
      "description": "Scan last 30 days of Daily Logs for unresolved items, auto-create punchlist entries",
      "value": "HIGH",
      "complexity": "MEDIUM",
      "status": "READY_TO_BUILD",
      "priority": "P2"
    },
    {
      "id": "AO-HP-007",
      "title": "QuickBooks Online Connection",
      "description": "Connect Houzz Pro to QuickBooks Online for automated invoice and payment sync",
      "value": "HIGH",
      "complexity": "LOW",
      "status": "READY_TO_CONFIGURE",
      "priority": "P1"
    },
    {
      "id": "AO-HP-008",
      "title": "Progress Invoice Automation",
      "description": "Auto-generate progress invoices at defined project milestone stages",
      "value": "HIGH",
      "complexity": "MEDIUM",
      "status": "ARCHITECTURE_DESIGN_NEEDED",
      "priority": "P2"
    },
    {
      "id": "AO-HP-009",
      "title": "Selection Reminder Cadence",
      "description": "Auto-remind client of pending material selections at 3/7/14 day intervals",
      "value": "HIGH",
      "complexity": "LOW",
      "status": "READY_TO_BUILD",
      "priority": "P2"
    },
    {
      "id": "AO-HP-010",
      "title": "Estimate Total Sync to HubSpot Deal Amount",
      "description": "When Houzz Pro estimate is approved, update HubSpot deal amount field via API",
      "value": "MEDIUM",
      "complexity": "MEDIUM",
      "status": "ARCHITECTURE_DESIGN_NEEDED",
      "priority": "P2"
    }
  ]
}
```

---

## CRITICAL GAPS

```json
{
  "critical_gaps": [
    {
      "gap": "No Houzz Pro to HubSpot integration",
      "impact": "Every project exists in both systems with zero automated sync; dual manual entry; data drift",
      "priority": "P0",
      "fix": "AO-HP-001 via Zapier BETA + n8n bridge"
    },
    {
      "gap": "QuickBooks not connected",
      "impact": "No automated accounting sync; financial reporting done outside Houzz Pro",
      "priority": "P1",
      "fix": "AO-HP-007 — connect via Settings > Integrations > QuickBooks Online"
    },
    {
      "gap": "0 contracts created",
      "impact": "Client contracts managed outside platform; no e-signature tracking; legal risk",
      "priority": "P1",
      "fix": "AO-HP-004 — auto-generate from deal stage trigger"
    },
    {
      "gap": "0 invoices sent through Houzz Pro",
      "impact": "Payments not tracked in platform; no AR visibility; no payment automation",
      "priority": "P1",
      "fix": "AO-HP-007 + AO-HP-008"
    },
    {
      "gap": "Client Dashboard not shared on any project",
      "impact": "Clients have no self-service visibility into project progress; increases PM interrupt burden",
      "priority": "P2",
      "fix": "AO-HP-005"
    },
    {
      "gap": "303 inbound leads not being captured",
      "impact": "Potential revenue from Houzz.com marketplace is being lost; only 1 active lead",
      "priority": "P1",
      "fix": "AO-HP-002 + AO-HP-003"
    }
  ]
}
```

---

## SYSTEM OWNERSHIP

```json
{
  "system": "Houzz Pro",
  "owner": "Chris Hendrickson (Super Admin)",
  "operational_admin": "Buck Adams",
  "primary_use": "Project management + field operations + financial documents",
  "ai_os_integration": "NONE — P0 gap",
  "next_actions_for_claude_code": [
    "Design AO-HP-001: HubSpot Deal to Houzz Pro Project bridge architecture via Zapier",
    "Configure AO-HP-002: Houzz Pro Lead to HubSpot Contact sync via Zapier",
    "Build AO-HP-003: AI lead auto-reply workflow",
    "Document AO-HP-007: QuickBooks Online connection steps",
    "Design AO-HP-005: Client Dashboard auto-share trigger",
    "Build AO-HP-009: Selection reminder cadence via Houzz Pro Tasks"
  ]
}
```

---

## URL PATTERN REFERENCE

```json
{
  "url_patterns": {
    "home": "https://pro.houzz.com/",
    "all_projects": "https://pro.houzz.com/manage/projects",
    "project_overview": "https://pro.houzz.com/manage/projects/{id}/overview",
    "project_contracts": "https://pro.houzz.com/manage/projects/{id}/contracts",
    "project_estimates": "https://pro.houzz.com/manage/projects/{id}/estimates",
    "project_tasks": "https://pro.houzz.com/manage/tasks/projects/{id}",
    "project_schedule": "https://pro.houzz.com/manage/projects/{id}/schedule",
    "project_daily_log": "https://pro.houzz.com/manage/projects/{id}/daily-log",
    "project_files": "https://pro.houzz.com/manage/projects/{id}/files",
    "project_expenses": "https://pro.houzz.com/manage/projects/{id}/expenses",
    "project_client_dashboard": "https://pro.houzz.com/manage/projects/{id}/client-dashboard",
    "project_budget": "https://pro.houzz.com/manage/projects/{id}/budget",
    "project_invoices": "https://pro.houzz.com/manage/projects/{id}/invoices",
    "project_purchase_orders": "https://pro.houzz.com/manage/projects/{id}/purchase-orders",
    "project_change_orders": "https://pro.houzz.com/manage/projects/{id}/change-orders",
    "leads": "https://pro.houzz.com/manage/leads",
    "financial_reports": "https://pro.houzz.com/manage/reports/",
    "team_members": "https://pro.houzz.com/settings/team-members",
    "integrations": "https://pro.houzz.com/settings/integrations",
    "zapier": "https://pro.houzz.com/settings/zapier",
    "quickbooks": "https://pro.houzz.com/settings/quickbooks",
    "company_info": "https://pro.houzz.com/settings/company-info",
    "team_chat": "https://pro.houzz.com/teamchat/channels/all"
  }
}
```

---

*Document prepared by Browser Claude — Discovery Agent*
*Destination: Claude Code — Handoff Processor + Implementation Engineer*
*Chief Architect: ChatGPT | Executive Approver: Buck Adams*
*Read-only discovery. Do not modify production systems. Do not trigger workflows. Do not write to databases.*

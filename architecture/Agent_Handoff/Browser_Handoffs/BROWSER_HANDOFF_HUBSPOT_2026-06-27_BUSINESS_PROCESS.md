---
source_agent: Browser Claude
destination_agent: Claude Code
document_type: browser_discovery
priority: high
status: ready_for_processing
related_system: HubSpot
intended_action: ingest_and_route
requires_approval: false
discovery_date: 2026-06-27
document_id: HCI-BH-HS-001
version: 1.0
prepared_by: Browser Claude (Discovery Agent)
executive_approver: Buck Adams (buck@hendricksoninc.com)
---

# BROWSER HANDOFF — HUBSPOT BUSINESS PROCESS INTELLIGENCE
## Hendrickson Construction Inc. | Portal 244757054 | Region NA2

---

## SUMMARY

HubSpot Sales Hub Starter is HCI's primary CRM for subcontractor management, bid
pipeline tracking, and client relationship data. n8n Construction OS (Private App
43234028) is the active automation layer with contacts+companies+deals read/write
scope. Workflows are locked (Starter plan). No webhooks configured — all automation
is poll-based. Zero use of Quotes, Products, Line Items, Forms, Lists, Marketing
Emails, or Documents. High-value automation opportunities exist across all unused modules.

---

## ACCOUNT METADATA

```json
{
  "portal_id": "244757054",
  "region": "NA2",
  "base_url": "https://app-na2.hubspot.com",
  "plan": "Sales Hub Starter",
  "admin_user": "Buck Adams",
  "admin_email": "buck@hendricksoninc.com",
  "total_users": 12,
  "api_quota_daily": 250000,
  "api_usage_observed": 28,
  "api_spike_date": "2026-06-25",
  "api_spike_volume": "~1000 calls",
  "workflows_status": "LOCKED — requires Sales Hub Professional",
  "webhooks_configured": false,
  "automation_mode": "poll-based"
}
```

---

## OBJECT INVENTORY

```json
{
  "objects": [
    {
      "name": "Contacts",
      "object_type_id": "0-1",
      "record_count": 1311,
      "custom_property_count": 3,
      "list_url": "/contacts/244757054/objects/0-1/views/all/list",
      "api_endpoint": "GET /crm/v3/objects/contacts",
      "usage_status": "ACTIVE",
      "primary_use": "Subcontractor and client contact management"
    },
    {
      "name": "Companies",
      "object_type_id": "0-2",
      "record_count": 1183,
      "custom_property_count": 5,
      "list_url": "/contacts/244757054/objects/0-2/views/all/list",
      "api_endpoint": "GET /crm/v3/objects/companies",
      "usage_status": "ACTIVE",
      "primary_use": "Subcontractor firm records with COI tracking"
    },
    {
      "name": "Deals",
      "object_type_id": "0-3",
      "record_count": 309,
      "custom_property_count": 11,
      "list_url": "/contacts/244757054/objects/0-3/views/all/list",
      "api_endpoint": "GET /crm/v3/objects/deals",
      "usage_status": "ACTIVE",
      "primary_use": "Bid pipeline and project pipeline tracking"
    },
    {
      "name": "Tasks",
      "object_type_id": "0-27",
      "record_count": 38,
      "list_url": "/tasks/244757054/view/all",
      "api_endpoint": "GET /crm/v3/objects/tasks",
      "usage_status": "LOW",
      "primary_use": "Manual follow-up reminders only"
    },
    {
      "name": "Notes",
      "object_type_id": "0-4",
      "api_endpoint": "GET /crm/v3/objects/notes",
      "usage_status": "UNKNOWN_VOLUME",
      "primary_use": "Unstructured record annotations"
    },
    {
      "name": "Emails (1:1 tracked)",
      "object_type_id": "0-49",
      "api_endpoint": "GET /crm/v3/objects/emails",
      "usage_status": "ACTIVE",
      "primary_use": "Outlook-synced bid invitation and follow-up emails"
    },
    {
      "name": "Meetings",
      "object_type_id": "0-47",
      "scheduling_url": "meet.hubspot.com/buck-adams/meeting",
      "meetings_booked": 0,
      "usage_status": "LOW",
      "primary_use": "Scheduling link exists; not embedded in workflows"
    },
    {
      "name": "Line Items",
      "object_type_id": "0-8",
      "record_count": 0,
      "usage_status": "UNUSED"
    },
    {
      "name": "Quotes",
      "object_type_id": "0-14",
      "record_count": 0,
      "usage_status": "UNUSED"
    },
    {
      "name": "Products",
      "object_type_id": "0-7",
      "record_count": 0,
      "usage_status": "UNUSED"
    },
    {
      "name": "Workflows",
      "usage_status": "LOCKED",
      "unlock_requirement": "Sales Hub Professional"
    },
    {
      "name": "Forms",
      "record_count": 0,
      "usage_status": "UNUSED"
    },
    {
      "name": "Lists / Segments",
      "record_count": 0,
      "usage_status": "UNUSED"
    },
    {
      "name": "Marketing Emails",
      "record_count": 0,
      "usage_status": "UNUSED"
    },
    {
      "name": "Documents",
      "record_count": 0,
      "capacity": 5000,
      "usage_status": "UNUSED"
    },
    {
      "name": "Dashboards",
      "record_count": 0,
      "usage_status": "UNUSED"
    },
    {
      "name": "Reports",
      "record_count": 0,
      "usage_status": "UNUSED"
    }
  ]
}
```

---

## PIPELINE SCHEMAS

```json
{
  "pipelines": [
    {
      "name": "HCI Bidding Pipeline",
      "purpose": "Track bid opportunities from scope request through award/no-award",
      "stages": [
        {"name": "Not Started", "order": 1},
        {"name": "Scope Ready", "order": 2},
        {"name": "Sent Out", "order": 3},
        {"name": "Bids Receiving", "order": 4},
        {"name": "Leveling", "order": 5},
        {"name": "Awarded", "order": 6, "terminal": true, "positive": true},
        {"name": "Not Awarded", "order": 7, "terminal": true, "positive": false}
      ]
    },
    {
      "name": "HCI Projects Pipeline",
      "purpose": "Track active construction projects from ROM through closeout",
      "stages": [
        {"name": "ROM Submitted", "order": 1},
        {"name": "ROM Accepted / Job Won", "order": 2},
        {"name": "Bidding Out", "order": 3},
        {"name": "Bids Received / Leveling", "order": 4},
        {"name": "Budget Locked", "order": 5},
        {"name": "Contract to Client", "order": 6},
        {"name": "Client Signed", "order": 7},
        {"name": "Construction", "order": 8},
        {"name": "Closeout", "order": 9},
        {"name": "Closed Won", "order": 10, "terminal": true, "positive": true}
      ]
    }
  ]
}
```

---

## CUSTOM PROPERTY SCHEMAS

```json
{
  "custom_properties": {
    "contacts": [
      {"label": "Contact Name", "internal_name": "contact_name", "type": "text"},
      {"label": "Ideal Customer Profile Tier", "internal_name": "ideal_customer_profile_tier", "type": "enumeration"},
      {"label": "Import Notes", "internal_name": "import_notes", "type": "textarea"}
    ],
    "companies": [
      {"label": "COI Expiration Date", "internal_name": "coi_expiration_date", "type": "date"},
      {"label": "COI File Link", "internal_name": "coi_file_link", "type": "text"},
      {
        "label": "COI Status",
        "internal_name": "coi_status",
        "type": "enumeration",
        "options": ["Active", "Expired", "Missing"]
      },
      {"label": "Company Code ID", "internal_name": "company_code_id", "type": "text"},
      {
        "label": "CSI Division",
        "internal_name": "csi_division",
        "type": "enumeration",
        "options": [
          "01 - General Requirements", "02 - Existing Conditions", "03 - Concrete",
          "04 - Masonry", "05 - Metals", "06 - Wood, Plastics & Composites",
          "07 - Thermal & Moisture Protection", "08 - Openings", "09 - Finishes",
          "10 - Specialties", "11 - Equipment", "12 - Furnishings",
          "21 - Fire Suppression", "22 - Plumbing", "23 - HVAC", "26 - Electrical"
        ]
      }
    ],
    "deals": [
      {"label": "Architect", "internal_name": "architecht", "type": "text"},
      {"label": "Building Plan Links", "internal_name": "building_plan_links", "type": "text"},
      {
        "label": "Conditional Waiver Status",
        "internal_name": "conditional_waiver_status",
        "type": "enumeration",
        "options": ["Not Applicable", "Pending", "Received"]
      },
      {
        "label": "Division",
        "internal_name": "division",
        "type": "enumeration",
        "options": [
          "Aspen General Contracting", "Carbondale General Contracting", "Commercial",
          "Design Build", "Development", "Exterior", "Interior",
          "Preconstruction", "Service", "Special Projects"
        ]
      },
      {"label": "Estimator", "internal_name": "estimator", "type": "text"},
      {"label": "Package Name", "internal_name": "package_name", "type": "text"},
      {"label": "Package Number", "internal_name": "package_number", "type": "text"},
      {"label": "Project Name", "internal_name": "project_name", "type": "text"},
      {
        "label": "Subcontract Status",
        "internal_name": "subcontract_status",
        "type": "enumeration",
        "options": ["Not Started", "In Progress", "Fully Executed"]
      },
      {
        "label": "Trade / Scope",
        "internal_name": "tradescope",
        "type": "enumeration",
        "options": [
          "Concrete", "Demo & Hazmat", "Earthwork", "Electrical",
          "Fire Protection", "Framing", "HVAC", "Plumbing", "Windows & Doors"
        ]
      },
      {
        "label": "Unconditional Waiver Status",
        "internal_name": "unconditional_waiver_status",
        "type": "enumeration",
        "options": ["Not Applicable", "Pending", "Received"]
      }
    ]
  }
}
```

---

## STANDARD PROPERTY ENUMERATIONS

```json
{
  "standard_enumerations": {
    "lead_status": [
      "New", "Open", "In Progress", "Open Deal",
      "Unqualified", "Attempted to Contact", "Connected", "Bad Timing", "N/A"
    ],
    "lifecycle_stage": [
      "Subscriber", "Lead", "Marketing Qualified Lead", "Sales Qualified Lead",
      "Opportunity", "Customer", "Evangelist", "Other"
    ]
  }
}
```

---

## CONNECTED APPS & INTEGRATION LAYER

```json
{
  "connected_apps": [
    {
      "name": "n8n Construction OS",
      "type": "private_app",
      "app_id": 43234028,
      "scopes": ["contacts.read","contacts.write","companies.read","companies.write","deals.read","deals.write"],
      "webhooks": 0,
      "api_token_prefix": "pat-na2-bd988",
      "observed_activity": "~1000 API calls on 2026-06-25 (batch operation)",
      "automation_mode": "poll-based",
      "status": "ACTIVE — PRIMARY AUTOMATION LAYER",
      "recommendation": "EXTEND — add webhooks, expand scopes, bridge to Houzz Pro"
    },
    {
      "name": "WF-002 n8n Service Key",
      "type": "private_app",
      "status": "ACTIVE",
      "recommendation": "MAINTAIN"
    },
    {
      "name": "HubSpot connector for Claude",
      "type": "connected_app",
      "status": "ACTIVE",
      "recommendation": "EXTEND — connect to HCI AI OS orchestration"
    },
    {
      "name": "HubSpot connector for ChatGPT",
      "type": "connected_app",
      "status": "ACTIVE",
      "recommendation": "EVALUATE — consolidate with Claude connector"
    },
    {
      "name": "HubSpot Payments",
      "type": "connected_app",
      "transactions": 0,
      "status": "INSTALLED_UNUSED",
      "recommendation": "IGNORE — invoicing done in Houzz Pro"
    },
    {
      "name": "Insycle Data Management",
      "type": "connected_app",
      "last_used": "2026-01-20",
      "status": "INSTALLED",
      "recommendation": "MAINTAIN — schedule quarterly data hygiene"
    },
    {
      "name": "Meta Ads",
      "type": "connected_app",
      "status": "ACTIVE_DAILY",
      "recommendation": "INTEGRATE — sync lead forms to Contacts auto-create"
    },
    {
      "name": "Outlook (email sync)",
      "type": "connected_app",
      "status": "ACTIVE",
      "recommendation": "MAINTAIN"
    },
    {
      "name": "Outlook Calendar",
      "type": "connected_app",
      "status": "ACTIVE",
      "recommendation": "MAINTAIN"
    },
    {
      "name": "Perplexity",
      "type": "user_app",
      "status": "INSTALLED",
      "recommendation": "EVALUATE"
    }
  ]
}
```

---

## API ENDPOINT REFERENCE

```json
{
  "api_base": "https://api.hubapi.com",
  "auth": "Bearer pat-na2-{token}",
  "endpoints": {
    "contacts": {
      "list": "GET /crm/v3/objects/contacts",
      "get": "GET /crm/v3/objects/contacts/{id}",
      "create": "POST /crm/v3/objects/contacts",
      "update": "PATCH /crm/v3/objects/contacts/{id}",
      "search": "POST /crm/v3/objects/contacts/search"
    },
    "companies": {
      "list": "GET /crm/v3/objects/companies",
      "get": "GET /crm/v3/objects/companies/{id}",
      "create": "POST /crm/v3/objects/companies",
      "update": "PATCH /crm/v3/objects/companies/{id}",
      "search": "POST /crm/v3/objects/companies/search"
    },
    "deals": {
      "list": "GET /crm/v3/objects/deals",
      "get": "GET /crm/v3/objects/deals/{id}",
      "create": "POST /crm/v3/objects/deals",
      "update": "PATCH /crm/v3/objects/deals/{id}",
      "search": "POST /crm/v3/objects/deals/search"
    },
    "tasks": {
      "list": "GET /crm/v3/objects/tasks",
      "create": "POST /crm/v3/objects/tasks",
      "update": "PATCH /crm/v3/objects/tasks/{id}"
    },
    "notes": {
      "list": "GET /crm/v3/objects/notes",
      "create": "POST /crm/v3/objects/notes"
    },
    "engagements": {
      "list": "GET /crm/v3/objects/engagements"
    },
    "associations": {
      "pattern": "GET /crm/v3/objects/{fromObject}/{objectId}/associations/{toObject}"
    },
    "pipelines": {
      "list": "GET /crm/v3/pipelines/deals",
      "stages": "GET /crm/v3/pipelines/deals/{pipelineId}/stages"
    },
    "properties": {
      "list": "GET /crm/v3/properties/{objectType}",
      "get": "GET /crm/v3/properties/{objectType}/{propertyName}"
    },
    "webhooks": {
      "note": "NOT CONFIGURED — requires Sales Hub Professional",
      "subscription_endpoint": "POST /webhooks/v3/{appId}/subscriptions"
    }
  }
}
```

---

## AUTOMATION OPPORTUNITY REGISTER

```json
{
  "automation_opportunities": [
    {
      "id": "AO-HS-001",
      "title": "COI Expiration Auto-Update",
      "description": "Daily n8n job: compare company.coi_expiration_date to today, auto-set coi_status",
      "trigger": "Daily cron at 06:00 MT",
      "action": "PATCH /crm/v3/objects/companies/{id}",
      "value": "HIGH",
      "complexity": "LOW",
      "requires_upgrade": false,
      "status": "READY_TO_BUILD"
    },
    {
      "id": "AO-HS-002",
      "title": "COI Renewal Email Trigger",
      "description": "30 days before COI expiration, send renewal request to primary contact",
      "value": "HIGH",
      "complexity": "LOW",
      "requires_upgrade": false,
      "status": "READY_TO_BUILD"
    },
    {
      "id": "AO-HS-003",
      "title": "Deal Stage to Houzz Pro Project Bridge",
      "description": "When deal moves to ROM Accepted/Job Won, auto-create Houzz Pro project",
      "value": "HIGH",
      "complexity": "MEDIUM",
      "requires_upgrade": false,
      "status": "PENDING_HOUZZ_API_DISCOVERY"
    },
    {
      "id": "AO-HS-004",
      "title": "Bid Invitation Auto-Task Creation",
      "description": "When deal stage = Sent Out, create tasks for all associated contacts",
      "value": "HIGH",
      "complexity": "LOW",
      "requires_upgrade": false,
      "status": "READY_TO_BUILD"
    },
    {
      "id": "AO-HS-005",
      "title": "Subcontractor COI Submission Form",
      "description": "HubSpot form for subs to submit updated COI, auto-updates company record",
      "value": "HIGH",
      "complexity": "LOW",
      "requires_upgrade": false,
      "status": "READY_TO_BUILD"
    },
    {
      "id": "AO-HS-006",
      "title": "Webhook Event-Driven Architecture",
      "description": "Replace polling with webhook subscriptions for real-time triggers",
      "value": "HIGH",
      "complexity": "MEDIUM",
      "requires_upgrade": true,
      "upgrade_required": "Sales Hub Professional",
      "status": "PENDING_UPGRADE"
    },
    {
      "id": "AO-HS-007",
      "title": "Sales Hub Professional Upgrade",
      "description": "Unlock Workflows, Sequences, webhooks, advanced reporting",
      "estimated_cost": "~$70/month incremental",
      "estimated_roi": "Eliminates 7+ hours/week of manual work",
      "value": "HIGH",
      "complexity": "LOW",
      "status": "EXECUTIVE_DECISION_REQUIRED"
    },
    {
      "id": "AO-HS-008",
      "title": "Pipeline Overview Dashboards",
      "description": "Build 4 dashboards: Pipeline Overview, Sub Vendor, Bidding Activity, COI Compliance",
      "value": "HIGH",
      "complexity": "LOW",
      "requires_upgrade": false,
      "status": "READY_TO_BUILD"
    },
    {
      "id": "AO-HS-009",
      "title": "ROM Quote Automation",
      "description": "Activate HubSpot Quotes for ROM generation at deal stage ROM Submitted",
      "value": "HIGH",
      "complexity": "MEDIUM",
      "status": "FUTURE_PHASE"
    },
    {
      "id": "AO-HS-010",
      "title": "AI Deal Summarization",
      "description": "n8n retrieves engagements for a deal, passes to Claude API for executive briefing",
      "value": "HIGH",
      "complexity": "MEDIUM",
      "requires_upgrade": false,
      "status": "READY_TO_BUILD"
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
      "gap": "No HubSpot to Houzz Pro integration",
      "impact": "Dual manual data entry for every project; data drift between systems",
      "priority": "P0"
    },
    {
      "gap": "No webhooks configured",
      "impact": "All automation is poll-based; no real-time triggers; API waste",
      "priority": "P1"
    },
    {
      "gap": "Workflows locked on Starter plan",
      "impact": "Cannot build deal-stage automations, sequences, or enrollment logic",
      "priority": "P1",
      "fix": "Upgrade to Sales Hub Professional"
    },
    {
      "gap": "COI Status not automated",
      "impact": "Expired COI companies may be used on active projects without flagging",
      "priority": "P1",
      "fix": "AO-HS-001 and AO-HS-002"
    },
    {
      "gap": "Zero dashboards or reports",
      "impact": "No pipeline visibility for leadership; no COI compliance view",
      "priority": "P2",
      "fix": "AO-HS-008"
    }
  ]
}
```

---

## SYSTEM OWNERSHIP

```json
{
  "system": "HubSpot",
  "owner": "Buck Adams + Chris Hendrickson",
  "primary_use": "Subcontractor CRM + Bid Pipeline",
  "ai_os_integration": "Active (n8n Construction OS)",
  "next_actions_for_claude_code": [
    "Build AO-HS-001: COI expiration auto-update n8n workflow",
    "Build AO-HS-002: COI renewal email trigger",
    "Build AO-HS-005: COI submission HubSpot form",
    "Build AO-HS-008: Four pipeline dashboards",
    "Build AO-HS-010: AI deal summarization via Claude API",
    "Design AO-HS-003: HubSpot-to-Houzz Pro project bridge architecture"
  ]
}
```

---

*Document prepared by Browser Claude — Discovery Agent*
*Destination: Claude Code — Handoff Processor + Implementation Engineer*
*Read-only discovery. Do not modify production systems. Do not trigger workflows.*

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

## SUMMARY

HubSpot Sales Hub Starter is HCI's primary CRM for subcontractor management, bid pipeline tracking, and client relationship data. n8n Construction OS (Private App 43234028) is the active automation layer with contacts+companies+deals read/write scope. Workflows are locked (Starter plan). No webhooks configured — all automation is poll-based. Zero use of Quotes, Products, Line Items, Forms, Lists, Marketing Emails, or Documents. High-value automation opportunities exist across all unused modules.

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
  "api_spike_date": "2026-06-25",
  "api_spike_volume": "~1000 calls",
  "workflows_status": "LOCKED — requires Sales Hub Professional",
  "webhooks_configured": false,
  "automation_mode": "poll-based"
}
```

## OBJECT INVENTORY

```json
{
  "objects": [
    {"name":"Contacts","object_type_id":"0-1","record_count":1311,"usage_status":"ACTIVE","primary_use":"Subcontractor and client contact management"},
    {"name":"Companies","object_type_id":"0-2","record_count":1183,"usage_status":"ACTIVE","primary_use":"Subcontractor firm records with COI tracking"},
    {"name":"Deals","object_type_id":"0-3","record_count":309,"usage_status":"ACTIVE","primary_use":"Bid pipeline and project pipeline tracking"},
    {"name":"Tasks","object_type_id":"0-27","record_count":38,"usage_status":"LOW"},
    {"name":"Notes","object_type_id":"0-4","usage_status":"UNKNOWN_VOLUME"},
    {"name":"Emails","object_type_id":"0-49","usage_status":"ACTIVE","primary_use":"Outlook-synced bid invitation emails"},
    {"name":"Meetings","object_type_id":"0-47","meetings_booked":0,"usage_status":"LOW"},
    {"name":"Line Items","object_type_id":"0-8","record_count":0,"usage_status":"UNUSED"},
    {"name":"Quotes","object_type_id":"0-14","record_count":0,"usage_status":"UNUSED"},
    {"name":"Products","object_type_id":"0-7","record_count":0,"usage_status":"UNUSED"},
    {"name":"Workflows","usage_status":"LOCKED","unlock_requirement":"Sales Hub Professional"},
    {"name":"Forms","record_count":0,"usage_status":"UNUSED"},
    {"name":"Lists","record_count":0,"usage_status":"UNUSED"},
    {"name":"Marketing Emails","record_count":0,"usage_status":"UNUSED"},
    {"name":"Documents","record_count":0,"capacity":5000,"usage_status":"UNUSED"},
    {"name":"Dashboards","record_count":0,"usage_status":"UNUSED"},
    {"name":"Reports","record_count":0,"usage_status":"UNUSED"}
  ]
}
```

## PIPELINE SCHEMAS

```json
{
  "pipelines": [
    {
      "name": "HCI Bidding Pipeline",
      "stages": ["Not Started","Scope Ready","Sent Out","Bids Receiving","Leveling","Awarded","Not Awarded"]
    },
    {
      "name": "HCI Projects Pipeline",
      "stages": ["ROM Submitted","ROM Accepted / Job Won","Bidding Out","Bids Received / Leveling","Budget Locked","Contract to Client","Client Signed","Construction","Closeout","Closed Won"]
    }
  ]
}
```

## CUSTOM PROPERTY SCHEMAS

```json
{
  "custom_properties": {
    "contacts": [
      {"label":"Contact Name","internal_name":"contact_name","type":"text"},
      {"label":"Ideal Customer Profile Tier","internal_name":"ideal_customer_profile_tier","type":"enumeration"},
      {"label":"Import Notes","internal_name":"import_notes","type":"textarea"}
    ],
    "companies": [
      {"label":"COI Expiration Date","internal_name":"coi_expiration_date","type":"date"},
      {"label":"COI File Link","internal_name":"coi_file_link","type":"text"},
      {"label":"COI Status","internal_name":"coi_status","type":"enumeration","options":["Active","Expired","Missing"]},
      {"label":"Company Code ID","internal_name":"company_code_id","type":"text"},
      {"label":"CSI Division","internal_name":"csi_division","type":"enumeration","options":["01 - General Requirements","02 - Existing Conditions","03 - Concrete","04 - Masonry","05 - Metals","06 - Wood, Plastics & Composites","07 - Thermal & Moisture Protection","08 - Openings","09 - Finishes","10 - Specialties","11 - Equipment","12 - Furnishings","21 - Fire Suppression","22 - Plumbing","23 - HVAC","26 - Electrical"]}
    ],
    "deals": [
      {"label":"Architect","internal_name":"architecht","type":"text"},
      {"label":"Building Plan Links","internal_name":"building_plan_links","type":"text"},
      {"label":"Conditional Waiver Status","internal_name":"conditional_waiver_status","type":"enumeration","options":["Not Applicable","Pending","Received"]},
      {"label":"Division","internal_name":"division","type":"enumeration","options":["Aspen General Contracting","Carbondale General Contracting","Commercial","Design Build","Development","Exterior","Interior","Preconstruction","Service","Special Projects"]},
      {"label":"Estimator","internal_name":"estimator","type":"text"},
      {"label":"Package Name","internal_name":"package_name","type":"text"},
      {"label":"Package Number","internal_name":"package_number","type":"text"},
      {"label":"Project Name","internal_name":"project_name","type":"text"},
      {"label":"Subcontract Status","internal_name":"subcontract_status","type":"enumeration","options":["Not Started","In Progress","Fully Executed"]},
      {"label":"Trade / Scope","internal_name":"tradescope","type":"enumeration","options":["Concrete","Demo & Hazmat","Earthwork","Electrical","Fire Protection","Framing","HVAC","Plumbing","Windows & Doors"]},
      {"label":"Unconditional Waiver Status","internal_name":"unconditional_waiver_status","type":"enumeration","options":["Not Applicable","Pending","Received"]}
    ]
  }
}
```

## CONNECTED APPS

```json
{
  "connected_apps": [
    {"name":"n8n Construction OS","app_id":43234028,"scopes":["contacts.read","contacts.write","companies.read","companies.write","deals.read","deals.write"],"webhooks":0,"status":"ACTIVE — PRIMARY AUTOMATION LAYER","recommendation":"EXTEND"},
    {"name":"WF-002 n8n Service Key","status":"ACTIVE","recommendation":"MAINTAIN"},
    {"name":"HubSpot connector for Claude","status":"ACTIVE","recommendation":"EXTEND"},
    {"name":"HubSpot connector for ChatGPT","status":"ACTIVE","recommendation":"EVALUATE"},
    {"name":"HubSpot Payments","transactions":0,"status":"INSTALLED_UNUSED","recommendation":"IGNORE"},
    {"name":"Insycle Data Management","last_used":"2026-01-20","recommendation":"MAINTAIN"},
    {"name":"Meta Ads","status":"ACTIVE_DAILY","recommendation":"INTEGRATE"},
    {"name":"Outlook email sync","status":"ACTIVE","recommendation":"MAINTAIN"},
    {"name":"Outlook Calendar","status":"ACTIVE","recommendation":"MAINTAIN"},
    {"name":"Perplexity","status":"INSTALLED","recommendation":"EVALUATE"}
  ]
}
```

## API ENDPOINT REFERENCE

```json
{
  "api_base": "https://api.hubapi.com",
  "auth": "Bearer pat-na2-{token}",
  "key_endpoints": {
    "contacts": "GET/POST/PATCH /crm/v3/objects/contacts",
    "companies": "GET/POST/PATCH /crm/v3/objects/companies",
    "deals": "GET/POST/PATCH /crm/v3/objects/deals",
    "tasks": "GET/POST/PATCH /crm/v3/objects/tasks",
    "notes": "GET/POST /crm/v3/objects/notes",
    "engagements": "GET /crm/v3/objects/engagements",
    "associations": "GET /crm/v3/objects/{from}/{id}/associations/{to}",
    "pipelines": "GET /crm/v3/pipelines/deals",
    "properties": "GET /crm/v3/properties/{objectType}",
    "webhooks": "NOT CONFIGURED — requires Sales Hub Professional"
  }
}
```

## AUTOMATION OPPORTUNITIES

```json
{
  "automation_opportunities": [
    {"id":"AO-HS-001","title":"COI Expiration Auto-Update","value":"HIGH","complexity":"LOW","requires_upgrade":false,"status":"READY_TO_BUILD"},
    {"id":"AO-HS-002","title":"COI Renewal Email Trigger at 30 days","value":"HIGH","complexity":"LOW","requires_upgrade":false,"status":"READY_TO_BUILD"},
    {"id":"AO-HS-003","title":"Deal Stage to Houzz Pro Project Bridge","value":"HIGH","complexity":"MEDIUM","requires_upgrade":false,"status":"PENDING_HOUZZ_API_DISCOVERY"},
    {"id":"AO-HS-004","title":"Bid Invitation Auto-Task Creation on Sent Out","value":"HIGH","complexity":"LOW","requires_upgrade":false,"status":"READY_TO_BUILD"},
    {"id":"AO-HS-005","title":"Subcontractor COI Submission Form","value":"HIGH","complexity":"LOW","requires_upgrade":false,"status":"READY_TO_BUILD"},
    {"id":"AO-HS-006","title":"Webhook Event-Driven Architecture","value":"HIGH","complexity":"MEDIUM","requires_upgrade":true,"upgrade":"Sales Hub Professional","status":"PENDING_UPGRADE"},
    {"id":"AO-HS-007","title":"Sales Hub Professional Upgrade","value":"HIGH","complexity":"LOW","estimated_cost":"~$70/month incremental","status":"EXECUTIVE_DECISION_REQUIRED"},
    {"id":"AO-HS-008","title":"Build 4 Pipeline Dashboards","value":"HIGH","complexity":"LOW","requires_upgrade":false,"status":"READY_TO_BUILD"},
    {"id":"AO-HS-009","title":"ROM Quote Automation","value":"HIGH","complexity":"MEDIUM","status":"FUTURE_PHASE"},
    {"id":"AO-HS-010","title":"AI Deal Summarization via Claude API","value":"HIGH","complexity":"MEDIUM","requires_upgrade":false,"status":"READY_TO_BUILD"}
  ]
}
```

## CRITICAL GAPS

```json
{
  "critical_gaps": [
    {"priority":"P0","gap":"No HubSpot to Houzz Pro integration","impact":"Dual manual data entry for every project"},
    {"priority":"P1","gap":"No webhooks configured","impact":"All automation is poll-based; no real-time triggers"},
    {"priority":"P1","gap":"Workflows locked on Starter plan","fix":"Upgrade to Sales Hub Professional"},
    {"priority":"P1","gap":"COI Status not automated","fix":"AO-HS-001 and AO-HS-002"},
    {"priority":"P2","gap":"Zero dashboards or reports","fix":"AO-HS-008"}
  ]
}
```

## NEXT ACTIONS FOR CLAUDE CODE

1. Build AO-HS-001: COI expiration auto-update n8n workflow
2. Build AO-HS-002: COI renewal email trigger
3. Build AO-HS-005: COI submission HubSpot form
4. Build AO-HS-008: Four pipeline dashboards
5. Build AO-HS-010: AI deal summarization via Claude API
6. Design AO-HS-003: HubSpot-to-Houzz Pro project bridge architecture

---
*Browser Claude — Discovery Agent | Read-only. Do not modify production systems.*

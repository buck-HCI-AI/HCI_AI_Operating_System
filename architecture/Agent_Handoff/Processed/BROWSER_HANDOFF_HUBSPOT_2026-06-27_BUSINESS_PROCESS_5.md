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
---

# BROWSER HANDOFF - HUBSPOT BUSINESS PROCESS INTELLIGENCE
## Hendrickson Construction Inc. | Portal 244757054 | Region NA2

## SUMMARY
HubSpot Sales Hub Starter is HCI primary CRM for subcontractor management, bid pipeline tracking, and client relationship data. n8n Construction OS (Private App 43234028) is the active automation layer with contacts+companies+deals read/write scope. Workflows LOCKED (Starter plan). No webhooks configured. Zero use of Quotes, Products, Line Items, Forms, Lists, Marketing Emails, Documents, Dashboards, or Reports.

## ACCOUNT METADATA
portal_id: 244757054
region: NA2
plan: Sales Hub Starter
admin: Buck Adams (buck@hendricksoninc.com)
total_users: 12
api_quota_daily: 250000
api_spike_date: 2026-06-25 (~1000 calls batch)
workflows_status: LOCKED
webhooks_configured: false
automation_mode: poll-based

## OBJECT INVENTORY
Contacts (0-1): 1311 records - ACTIVE - subcontractor/client management
Companies (0-2): 1183 records - ACTIVE - subcontractor firms + COI tracking
Deals (0-3): 309 records - ACTIVE - bid + project pipeline tracking
Tasks (0-27): 38 records - LOW - manual follow-ups only
Notes (0-4): UNKNOWN_VOLUME
Emails (0-49): ACTIVE - Outlook-synced bid invitations
Meetings (0-47): LOW - scheduling link exists, 0 booked
Line Items (0-8): UNUSED
Quotes (0-14): UNUSED
Products (0-7): UNUSED
Workflows: LOCKED (Sales Hub Professional required)
Forms: UNUSED (0 created)
Lists/Segments: UNUSED (0 created)
Marketing Emails: UNUSED (0 created)
Documents: UNUSED (0 of 5000 used)
Dashboards: UNUSED (0 created)
Reports: UNUSED (0 created)

## PIPELINES
HCI Bidding Pipeline:
  Not Started > Scope Ready > Sent Out > Bids Receiving > Leveling > Awarded / Not Awarded

HCI Projects Pipeline:
  ROM Submitted > ROM Accepted/Job Won > Bidding Out > Bids Received/Leveling > Budget Locked > Contract to Client > Client Signed > Construction > Closeout > Closed Won

## CUSTOM PROPERTIES
CONTACTS:
  contact_name (text)
  ideal_customer_profile_tier (enumeration)
  import_notes (textarea)

COMPANIES:
  coi_expiration_date (date)
  coi_file_link (text)
  coi_status (enumeration): Active | Expired | Missing
  company_code_id (text)
  csi_division (enumeration): 01-General Requirements | 02-Existing Conditions | 03-Concrete | 04-Masonry | 05-Metals | 06-Wood Plastics Composites | 07-Thermal Moisture Protection | 08-Openings | 09-Finishes | 10-Specialties | 11-Equipment | 12-Furnishings | 21-Fire Suppression | 22-Plumbing | 23-HVAC | 26-Electrical

DEALS:
  architecht (text)
  building_plan_links (text)
  conditional_waiver_status (enum): Not Applicable | Pending | Received
  division (enum): Aspen GC | Carbondale GC | Commercial | Design Build | Development | Exterior | Interior | Preconstruction | Service | Special Projects
  estimator (text)
  package_name (text)
  package_number (text)
  project_name (text)
  subcontract_status (enum): Not Started | In Progress | Fully Executed
  tradescope (enum): Concrete | Demo & Hazmat | Earthwork | Electrical | Fire Protection | Framing | HVAC | Plumbing | Windows & Doors
  unconditional_waiver_status (enum): Not Applicable | Pending | Received

## STANDARD ENUMERATIONS
lead_status: New | Open | In Progress | Open Deal | Unqualified | Attempted to Contact | Connected | Bad Timing | N/A
lifecycle_stage: Subscriber | Lead | MQL | SQL | Opportunity | Customer | Evangelist | Other

## CONNECTED APPS
n8n Construction OS (app_id: 43234028) - ACTIVE PRIMARY - scopes: contacts+companies+deals r/w - 0 webhooks - EXTEND
WF-002 n8n Service Key - ACTIVE - MAINTAIN
HubSpot connector for Claude - ACTIVE - EXTEND
HubSpot connector for ChatGPT - ACTIVE - EVALUATE
HubSpot Payments - UNUSED - IGNORE
Insycle - last used 2026-01-20 - MAINTAIN
Meta Ads - ACTIVE DAILY - INTEGRATE
Outlook email sync - ACTIVE - MAINTAIN
Outlook Calendar - ACTIVE - MAINTAIN
Perplexity - INSTALLED - EVALUATE

## API ENDPOINTS
api_base: https://api.hubapi.com
auth: Bearer pat-na2-{token}
contacts: GET/POST/PATCH /crm/v3/objects/contacts
companies: GET/POST/PATCH /crm/v3/objects/companies
deals: GET/POST/PATCH /crm/v3/objects/deals
tasks: GET/POST/PATCH /crm/v3/objects/tasks
notes: GET/POST /crm/v3/objects/notes
engagements: GET /crm/v3/objects/engagements
associations: GET /crm/v3/objects/{from}/{id}/associations/{to}
pipelines: GET /crm/v3/pipelines/deals
properties: GET /crm/v3/properties/{objectType}
webhooks: NOT CONFIGURED - requires Sales Hub Professional

## AUTOMATION OPPORTUNITIES
AO-HS-001: COI Expiration Auto-Update - HIGH value - LOW complexity - READY_TO_BUILD
AO-HS-002: COI Renewal Email at 30 days - HIGH - LOW - READY_TO_BUILD
AO-HS-003: Deal Stage to Houzz Pro Project Bridge - HIGH - MEDIUM - PENDING_HOUZZ_API
AO-HS-004: Bid Invitation Auto-Task on Sent Out - HIGH - LOW - READY_TO_BUILD
AO-HS-005: Subcontractor COI Submission Form - HIGH - LOW - READY_TO_BUILD
AO-HS-006: Webhook Event-Driven Architecture - HIGH - MEDIUM - PENDING_UPGRADE
AO-HS-007: Sales Hub Professional Upgrade (~$70/mo incremental) - HIGH - LOW - EXEC_DECISION
AO-HS-008: Build 4 Pipeline Dashboards - HIGH - LOW - READY_TO_BUILD
AO-HS-009: ROM Quote Automation - HIGH - MEDIUM - FUTURE_PHASE
AO-HS-010: AI Deal Summarization via Claude API - HIGH - MEDIUM - READY_TO_BUILD

## CRITICAL GAPS
P0: No HubSpot to Houzz Pro integration - dual manual entry for all projects
P1: No webhooks configured - all automation poll-based
P1: Workflows locked - upgrade to Sales Hub Professional required
P1: COI Status not automated - expired subs on active projects risk
P2: Zero dashboards or reports - no leadership visibility

## NEXT ACTIONS FOR CLAUDE CODE
1. Build AO-HS-001: COI expiration auto-update n8n workflow
2. Build AO-HS-002: COI renewal email trigger
3. Build AO-HS-005: COI submission HubSpot form
4. Build AO-HS-008: Four pipeline dashboards
5. Build AO-HS-010: AI deal summarization via Claude API
6. Design AO-HS-003: HubSpot to Houzz Pro project bridge

---
Browser Claude - Discovery Agent | Read-only. Do not modify production systems.
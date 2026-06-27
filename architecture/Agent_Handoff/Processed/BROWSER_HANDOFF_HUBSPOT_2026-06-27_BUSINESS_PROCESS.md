---
created_at: 2026-06-27
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
summary: HubSpot Sales Starter discovery: 1311 contacts, 309 deals, COI tracking, Workflows locked, 10 automation opportunities, P0 gap is Houzz bridge
---

# BROWSER HANDOFF — HUBSPOT BUSINESS PROCESS INTELLIGENCE
## Hendrickson Construction Inc. | Portal 244757054 | Region NA2

## SUMMARY
HubSpot Sales Hub Starter is HCI primary CRM for subcontractor management, bid pipeline tracking, and client relationship data. n8n Construction OS (Private App 43234028) is active automation layer with contacts+companies+deals read/write scope. Workflows locked (Starter plan). No webhooks configured — all automation is poll-based. Zero use of Quotes, Products, Line Items, Forms, Lists, Marketing Emails, or Documents.

## ACCOUNT METADATA
portal_id: 244757054
region: NA2
base_url: https://app-na2.hubspot.com
plan: Sales Hub Starter
admin_email: buck@hendricksoninc.com
total_users: 12
api_quota_daily: 250000
api_spike_date: 2026-06-25
api_spike_volume: ~1000 calls
workflows_status: LOCKED — requires Sales Hub Professional
webhooks_configured: false
automation_mode: poll-based

## OBJECT INVENTORY
Contacts | 0-1 | 1311 records | ACTIVE | Subcontractor and client management
Companies | 0-2 | 1183 records | ACTIVE | Sub firms with COI tracking
Deals | 0-3 | 309 records | ACTIVE | Bid and project pipeline
Tasks | 0-27 | 38 records | LOW | Manual follow-up only
Notes | 0-4 | unknown | ACTIVE | Unstructured annotations
Emails | 0-49 | active | ACTIVE | Outlook-synced bid emails
Meetings | 0-47 | 0 booked | LOW | Scheduling link exists unused
Line Items | 0-8 | 0 | UNUSED
Quotes | 0-14 | 0 | UNUSED
Products | 0-7 | 0 | UNUSED
Workflows | — | — | LOCKED
Forms | — | 0 | UNUSED
Lists/Segments | — | 0 | UNUSED
Marketing Emails | — | 0 | UNUSED
Documents | — | 0/5000 | UNUSED
Dashboards | — | 0 | UNUSED
Reports | — | 0 | UNUSED

## PIPELINE: HCI BIDDING PIPELINE
1. Not Started
2. Scope Ready
3. Sent Out
4. Bids Receiving
5. Leveling
6. Awarded (terminal/positive)
7. Not Awarded (terminal/negative)

## PIPELINE: HCI PROJECTS PIPELINE
1. ROM Submitted
2. ROM Accepted / Job Won
3. Bidding Out
4. Bids Received / Leveling
5. Budget Locked
6. Contract to Client
7. Client Signed
8. Construction
9. Closeout
10. Closed Won (terminal/positive)

## CUSTOM PROPERTIES — CONTACTS
contact_name | text
ideal_customer_profile_tier | enumeration
import_notes | textarea

## CUSTOM PROPERTIES — COMPANIES
coi_expiration_date | date
coi_file_link | text
coi_status | enumeration | Active, Expired, Missing
company_code_id | text
csi_division | enumeration | 01-General Requirements, 02-Existing Conditions, 03-Concrete, 04-Masonry, 05-Metals, 06-Wood Plastics Composites, 07-Thermal Moisture Protection, 08-Openings, 09-Finishes, 10-Specialties, 11-Equipment, 12-Furnishings, 21-Fire Suppression, 22-Plumbing, 23-HVAC, 26-Electrical

## CUSTOM PROPERTIES — DEALS
architecht | text
building_plan_links | text
conditional_waiver_status | enumeration | Not Applicable, Pending, Received
division | enumeration | Aspen General Contracting, Carbondale General Contracting, Commercial, Design Build, Development, Exterior, Interior, Preconstruction, Service, Special Projects
estimator | text
package_name | text
package_number | text
project_name | text
subcontract_status | enumeration | Not Started, In Progress, Fully Executed
tradescope | enumeration | Concrete, Demo & Hazmat, Earthwork, Electrical, Fire Protection, Framing, HVAC, Plumbing, Windows & Doors
unconditional_waiver_status | enumeration | Not Applicable, Pending, Received

## STANDARD ENUMERATIONS
lead_status: New, Open, In Progress, Open Deal, Unqualified, Attempted to Contact, Connected, Bad Timing, N/A
lifecycle_stage: Subscriber, Lead, Marketing Qualified Lead, Sales Qualified Lead, Opportunity, Customer, Evangelist, Other

## CONNECTED APPS
n8n Construction OS | private_app | id:43234028 | scopes:contacts+companies+deals read/write | webhooks:0 | ACTIVE PRIMARY | RECOMMENDATION: EXTEND add webhooks bridge to Houzz Pro
WF-002 n8n Service Key | private_app | ACTIVE | RECOMMENDATION: MAINTAIN
HubSpot connector for Claude | connected_app | ACTIVE | RECOMMENDATION: EXTEND to HCI AI OS
HubSpot connector for ChatGPT | connected_app | ACTIVE | RECOMMENDATION: EVALUATE consolidate
HubSpot Payments | connected_app | 0 transactions | UNUSED | RECOMMENDATION: IGNORE
Insycle Data Management | connected_app | last used 2026-01-20 | RECOMMENDATION: MAINTAIN quarterly hygiene
Meta Ads | connected_app | ACTIVE DAILY | RECOMMENDATION: INTEGRATE sync lead forms to Contacts
Outlook email sync | connected_app | ACTIVE | RECOMMENDATION: MAINTAIN
Outlook Calendar | connected_app | ACTIVE | RECOMMENDATION: MAINTAIN
Perplexity | user_app | INSTALLED | RECOMMENDATION: EVALUATE

## API ENDPOINTS
Base: https://api.hubapi.com
Auth: Bearer pat-na2-{token}
GET /crm/v3/objects/contacts
GET /crm/v3/objects/companies
GET /crm/v3/objects/deals
GET /crm/v3/objects/tasks
GET /crm/v3/objects/notes
GET /crm/v3/objects/engagements
POST /crm/v3/objects/{type}
PATCH /crm/v3/objects/{type}/{id}
POST /crm/v3/objects/{type}/search
GET /crm/v3/objects/{fromObject}/{id}/associations/{toObject}
GET /crm/v3/pipelines/deals
GET /crm/v3/properties/{objectType}
Webhooks: NOT CONFIGURED — requires Sales Hub Professional

## AUTOMATION OPPORTUNITIES
AO-HS-001 | COI Expiration Auto-Update | Daily cron compares coi_expiration_date to today, auto-sets coi_status | HIGH value | LOW complexity | READY_TO_BUILD
AO-HS-002 | COI Renewal Email at 30 days | Send renewal request when expiry within 30 days | HIGH | LOW | READY_TO_BUILD
AO-HS-003 | Deal Stage to Houzz Pro Project Bridge | ROM Accepted triggers Houzz Pro project creation | HIGH | MEDIUM | PENDING_HOUZZ_API
AO-HS-004 | Bid Invitation Auto-Task Creation | Deal stage Sent Out triggers tasks for all associated contacts | HIGH | LOW | READY_TO_BUILD
AO-HS-005 | Subcontractor COI Submission Form | HubSpot form auto-updates company COI fields on submission | HIGH | LOW | READY_TO_BUILD
AO-HS-006 | Webhook Event-Driven Architecture | Replace polling with real-time webhooks | HIGH | MEDIUM | PENDING_UPGRADE
AO-HS-007 | Sales Hub Professional Upgrade | Unlocks Workflows Sequences Webhooks | HIGH | LOW | EXECUTIVE_DECISION ~$70/month incremental
AO-HS-008 | Four Pipeline Dashboards | Pipeline Overview, Sub Vendor, Bidding Activity, COI Compliance | HIGH | LOW | READY_TO_BUILD
AO-HS-009 | ROM Quote Automation | Activate Quotes for ROM generation at deal stage entry | HIGH | MEDIUM | FUTURE_PHASE
AO-HS-010 | AI Deal Summarization | n8n fetches engagements, Claude API generates briefing | HIGH | MEDIUM | READY_TO_BUILD

## CRITICAL GAPS
P0 | No HubSpot to Houzz Pro integration | Dual manual entry, data drift
P1 | No webhooks | Poll-based only, no real-time triggers
P1 | Workflows locked | Cannot build stage automations without upgrade
P1 | COI Status not automated | Expired subs may appear active
P2 | Zero dashboards | No pipeline visibility for leadership

## NEXT ACTIONS FOR CLAUDE CODE
1. Build AO-HS-001: COI expiration auto-update n8n workflow
2. Build AO-HS-002: COI renewal email trigger
3. Build AO-HS-005: COI submission HubSpot form
4. Build AO-HS-008: Four pipeline dashboards
5. Build AO-HS-010: AI deal summarization via Claude API
6. Design AO-HS-003: HubSpot-to-Houzz Pro bridge architecture

---
Document prepared by Browser Claude — Discovery Agent
Destination: Claude Code — Handoff Processor
Read-only discovery. Do not modify production systems.

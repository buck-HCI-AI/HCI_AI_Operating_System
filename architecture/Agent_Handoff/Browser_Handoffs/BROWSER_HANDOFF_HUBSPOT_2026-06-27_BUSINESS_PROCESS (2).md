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

# BROWSER HANDOFF — HUBSPOT BUSINESS PROCESS INTELLIGENCE
## Hendrickson Construction Inc. | Portal 244757054 | Region NA2

## SUMMARY
HubSpot Sales Hub Starter is HCI primary CRM for subcontractor management and bid pipeline tracking. n8n Construction OS (Private App 43234028) is the active automation layer with contacts+companies+deals read/write scope. Workflows are LOCKED (Starter plan). No webhooks configured — all automation is poll-based. Zero use of Quotes, Products, Line Items, Forms, Lists, Marketing Emails, or Documents.

## ACCOUNT METADATA
- portal_id: 244757054
- region: NA2
- base_url: https://app-na2.hubspot.com
- plan: Sales Hub Starter
- admin_email: buck@hendricksoninc.com
- total_users: 12
- api_quota_daily: 250000
- api_spike_date: 2026-06-25 (~1000 calls batch operation)
- workflows_status: LOCKED — requires Sales Hub Professional
- webhooks_configured: false
- automation_mode: poll-based

## OBJECT INVENTORY
| Object | Type ID | Count | Status |
|---|---|---|---|
| Contacts | 0-1 | 1311 | ACTIVE |
| Companies | 0-2 | 1183 | ACTIVE |
| Deals | 0-3 | 309 | ACTIVE |
| Tasks | 0-27 | 38 | LOW |
| Notes | 0-4 | unknown | ACTIVE |
| Emails (1:1) | 0-49 | unknown | ACTIVE |
| Meetings | 0-47 | 0 booked | LOW |
| Line Items | 0-8 | 0 | UNUSED |
| Quotes | 0-14 | 0 | UNUSED |
| Products | 0-7 | 0 | UNUSED |
| Workflows | — | — | LOCKED |
| Forms | — | 0 | UNUSED |
| Lists | — | 0 | UNUSED |
| Marketing Emails | — | 0 | UNUSED |
| Documents | — | 0/5000 | UNUSED |
| Dashboards | — | 0 | UNUSED |
| Reports | — | 0 | UNUSED |

## PIPELINES
### HCI Bidding Pipeline
Not Started → Scope Ready → Sent Out → Bids Receiving → Leveling → Awarded | Not Awarded

### HCI Projects Pipeline
ROM Submitted → ROM Accepted/Job Won → Bidding Out → Bids Received/Leveling → Budget Locked → Contract to Client → Client Signed → Construction → Closeout → Closed Won

## CUSTOM PROPERTIES — CONTACTS
- contact_name (text)
- ideal_customer_profile_tier (enumeration)
- import_notes (textarea)

## CUSTOM PROPERTIES — COMPANIES
- coi_expiration_date (date)
- coi_file_link (text)
- coi_status (enumeration): Active | Expired | Missing
- company_code_id (text)
- csi_division (enumeration): 01-General Requirements | 02-Existing Conditions | 03-Concrete | 04-Masonry | 05-Metals | 06-Wood Plastics Composites | 07-Thermal Moisture Protection | 08-Openings | 09-Finishes | 10-Specialties | 11-Equipment | 12-Furnishings | 21-Fire Suppression | 22-Plumbing | 23-HVAC | 26-Electrical

## CUSTOM PROPERTIES — DEALS
- architecht (text)
- building_plan_links (text)
- conditional_waiver_status: Not Applicable | Pending | Received
- division: Aspen General Contracting | Carbondale General Contracting | Commercial | Design Build | Development | Exterior | Interior | Preconstruction | Service | Special Projects
- estimator (text)
- package_name (text)
- package_number (text)
- project_name (text)
- subcontract_status: Not Started | In Progress | Fully Executed
- tradescope: Concrete | Demo & Hazmat | Earthwork | Electrical | Fire Protection | Framing | HVAC | Plumbing | Windows & Doors
- unconditional_waiver_status: Not Applicable | Pending | Received

## STANDARD ENUMERATIONS
- lead_status: New | Open | In Progress | Open Deal | Unqualified | Attempted to Contact | Connected | Bad Timing | N/A
- lifecycle_stage: Subscriber | Lead | MQL | SQL | Opportunity | Customer | Evangelist | Other

## CONNECTED APPS
| App | Type | Status | Recommendation |
|---|---|---|---|
| n8n Construction OS | private_app id:43234028 | ACTIVE PRIMARY | EXTEND — add webhooks, bridge to Houzz Pro |
| WF-002 n8n Service Key | private_app | ACTIVE | MAINTAIN |
| HubSpot connector for Claude | connected_app | ACTIVE | EXTEND |
| HubSpot connector for ChatGPT | connected_app | ACTIVE | EVALUATE — consolidate |
| HubSpot Payments | connected_app | INSTALLED_UNUSED | IGNORE |
| Insycle Data Management | connected_app | last_used:2026-01-20 | MAINTAIN — quarterly hygiene |
| Meta Ads | connected_app | ACTIVE_DAILY | INTEGRATE — sync lead forms |
| Outlook email sync | connected_app | ACTIVE | MAINTAIN |
| Outlook Calendar | connected_app | ACTIVE | MAINTAIN |
| Perplexity | user_app | INSTALLED | EVALUATE |

## API ENDPOINTS
- Contacts: GET/POST/PATCH /crm/v3/objects/contacts
- Companies: GET/POST/PATCH /crm/v3/objects/companies
- Deals: GET/POST/PATCH /crm/v3/objects/deals
- Tasks: GET/POST/PATCH /crm/v3/objects/tasks
- Notes: GET/POST /crm/v3/objects/notes
- Engagements: GET /crm/v3/objects/engagements
- Associations: GET /crm/v3/objects/{from}/{id}/associations/{to}
- Pipelines: GET /crm/v3/pipelines/deals
- Properties: GET /crm/v3/properties/{objectType}
- Webhooks: NOT CONFIGURED — requires Sales Hub Professional

## AUTOMATION OPPORTUNITIES
| ID | Title | Value | Complexity | Status |
|---|---|---|---|---|
| AO-HS-001 | COI Expiration Auto-Update (daily cron) | HIGH | LOW | READY_TO_BUILD |
| AO-HS-002 | COI Renewal Email at 30 days | HIGH | LOW | READY_TO_BUILD |
| AO-HS-003 | Deal Stage → Houzz Pro Project Bridge | HIGH | MEDIUM | PENDING_HOUZZ_API |
| AO-HS-004 | Bid Invitation Auto-Task Creation | HIGH | LOW | READY_TO_BUILD |
| AO-HS-005 | Subcontractor COI Submission Form | HIGH | LOW | READY_TO_BUILD |
| AO-HS-006 | Webhook Event-Driven Architecture | HIGH | MEDIUM | PENDING_UPGRADE |
| AO-HS-007 | Sales Hub Professional Upgrade (~$70/mo) | HIGH | LOW | EXEC_DECISION |
| AO-HS-008 | Four Pipeline Dashboards | HIGH | LOW | READY_TO_BUILD |
| AO-HS-009 | ROM Quote Automation | HIGH | MEDIUM | FUTURE_PHASE |
| AO-HS-010 | AI Deal Summarization via Claude API | HIGH | MEDIUM | READY_TO_BUILD |

## CRITICAL GAPS
| Priority | Gap | Fix |
|---|---|---|
| P0 | No HubSpot to Houzz Pro integration | AO-HS-003 |
| P1 | No webhooks configured | Upgrade + AO-HS-006 |
| P1 | Workflows locked | Sales Hub Professional upgrade |
| P1 | COI Status not automated | AO-HS-001 + AO-HS-002 |
| P2 | Zero dashboards or reports | AO-HS-008 |

## NEXT ACTIONS FOR CLAUDE CODE
1. Build AO-HS-001: COI expiration auto-update n8n workflow
2. Build AO-HS-002: COI renewal email trigger
3. Build AO-HS-005: COI submission HubSpot form config
4. Build AO-HS-008: Four pipeline dashboards
5. Build AO-HS-010: AI deal summarization via Claude API
6. Design AO-HS-003: HubSpot to Houzz Pro project bridge architecture

---
*Browser Claude — Discovery Agent | Read-only. Do not modify production systems.*
*Auto-route to: Agent_Handoff/Inbox when path exists*

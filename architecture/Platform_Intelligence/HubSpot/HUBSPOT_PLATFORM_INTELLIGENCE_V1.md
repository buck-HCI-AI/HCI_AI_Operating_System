# HubSpot Platform Intelligence — HCI
**Discovery Date:** 2026-06-27 | **Source:** Browser Claude | **Document ID:** HCI-BH-HS-001

---

## Account State
| Field | Value |
|---|---|
| Portal ID | 244757054 |
| Region | NA2 |
| Plan | Sales Hub Starter |
| Admin | buck@hendricksoninc.com |
| Total Users | 12 |
| API Quota (daily) | 250,000 |
| API Spike (2026-06-25) | ~1,000 calls |
| Workflows | LOCKED — requires Sales Hub Professional |
| Webhooks | NOT CONFIGURED |
| Automation Mode | Poll-based only |

---

## Object Inventory
| Object | ID | Records | Status | Notes |
|---|---|---|---|---|
| Contacts | 0-1 | 1,311 | ACTIVE | Subcontractors + clients |
| Companies | 0-2 | 1,183 | ACTIVE | Sub firms with COI tracking |
| Deals | 0-3 | 309 | ACTIVE | Bid + project pipeline |
| Tasks | 0-27 | 38 | LOW | Manual follow-up only |
| Notes | 0-4 | — | ACTIVE | Unstructured annotations |
| Emails | 0-49 | — | ACTIVE | Outlook-synced bid emails |
| Meetings | 0-47 | 0 | LOW | Scheduling link unused |
| Line Items | 0-8 | 0 | UNUSED | — |
| Quotes | 0-14 | 0 | UNUSED | — |
| Products | 0-7 | 0 | UNUSED | — |
| Workflows | — | — | LOCKED | Requires upgrade |
| Forms | — | 0 | UNUSED | — |
| Lists/Segments | — | 0 | UNUSED | — |
| Marketing Emails | — | 0 | UNUSED | — |
| Documents | — | 0/5000 | UNUSED | — |
| Dashboards | — | 0 | UNUSED | — |
| Reports | — | 0 | UNUSED | — |

---

## Pipelines

### HCI Bidding Pipeline
1. Not Started
2. Scope Ready
3. Sent Out → `AO-HS-004: auto-task creation for all contacts`
4. Bids Receiving
5. Leveling
6. **Awarded** *(terminal — positive)*
7. **Not Awarded** *(terminal — negative)*

### HCI Projects Pipeline
1. ROM Submitted
2. **ROM Accepted / Job Won** → `AO-HP-001: trigger Houzz Pro project creation`
3. Bidding Out
4. Bids Received / Leveling
5. Budget Locked
6. **Contract to Client** → `AO-HP-004: trigger Houzz Pro contract`
7. Client Signed
8. Construction
9. Closeout
10. **Closed Won** *(terminal — positive)*

---

## Custom Properties

### Contacts
| Property | Type |
|---|---|
| contact_name | text |
| ideal_customer_profile_tier | enumeration |
| import_notes | textarea |

### Companies
| Property | Type | Values |
|---|---|---|
| coi_expiration_date | date | — |
| coi_file_link | text | — |
| coi_status | enumeration | Active, Expired, Missing |
| company_code_id | text | — |
| csi_division | enumeration | 01-General Requirements … 26-Electrical (16 divisions) |

### Deals
| Property | Type |
|---|---|
| architecht | text |
| building_plan_links | text |
| conditional_waiver_status | enumeration: Not Applicable, Pending, Received |
| division | enumeration: Aspen GC, Carbondale GC, Commercial, Design Build, Development, Exterior, Interior, Preconstruction, Service, Special Projects |
| estimator | text |
| package_name | text |
| package_number | text |
| project_name | text |
| subcontract_status | enumeration: Not Started, In Progress, Fully Executed |
| tradescope | enumeration: Concrete, Demo & Hazmat, Earthwork, Electrical, Fire Protection, Framing, HVAC, Plumbing, Windows & Doors |
| unconditional_waiver_status | enumeration: Not Applicable, Pending, Received |

---

## Connected Apps
| App | Type | Status | Action |
|---|---|---|---|
| n8n Construction OS (id:43234028) | Private App | ACTIVE | EXTEND: add webhooks bridge to Houzz Pro |
| WF-002 n8n Service Key | Private App | ACTIVE | MAINTAIN |
| HubSpot connector for Claude | Connected App | ACTIVE | EXTEND to HCI AI OS |
| HubSpot connector for ChatGPT | Connected App | ACTIVE | EVALUATE: consolidate |
| HubSpot Payments | Connected App | 0 transactions | IGNORE |
| Insycle Data Management | Connected App | Last used 2026-01-20 | MAINTAIN: quarterly hygiene |
| Meta Ads | Connected App | ACTIVE DAILY | INTEGRATE: sync lead forms to Contacts |
| Outlook email sync | Connected App | ACTIVE | MAINTAIN |
| Outlook Calendar | Connected App | ACTIVE | MAINTAIN |
| Perplexity | User App | INSTALLED | EVALUATE |

---

## API Reference
```
Base URL: https://api.hubapi.com
Auth:     Bearer pat-na2-{token}

GET  /crm/v3/objects/contacts
GET  /crm/v3/objects/companies
GET  /crm/v3/objects/deals
GET  /crm/v3/objects/tasks
GET  /crm/v3/objects/notes
GET  /crm/v3/objects/engagements
POST /crm/v3/objects/{type}
PATCH /crm/v3/objects/{type}/{id}
POST  /crm/v3/objects/{type}/search
GET   /crm/v3/objects/{fromObject}/{id}/associations/{toObject}
GET   /crm/v3/pipelines/deals
GET   /crm/v3/properties/{objectType}
Webhooks: NOT CONFIGURED (requires Sales Hub Professional)
```

---

## Automation Opportunities
| ID | Opportunity | Value | Complexity | Status |
|---|---|---|---|---|
| AO-HS-001 | COI Expiration Auto-Update (daily cron) | HIGH | LOW | **READY_TO_BUILD** |
| AO-HS-002 | COI Renewal Email at 30 days | HIGH | LOW | **READY_TO_BUILD** |
| AO-HS-003 | Deal Stage → Houzz Pro Project Bridge | HIGH | MEDIUM | PENDING_HOUZZ_API |
| AO-HS-004 | Bid Invitation Auto-Task (Sent Out stage) | HIGH | LOW | **READY_TO_BUILD** |
| AO-HS-005 | COI Submission Form | HIGH | LOW | **READY_TO_BUILD** |
| AO-HS-006 | Webhook Event-Driven Architecture | HIGH | MEDIUM | PENDING_UPGRADE |
| AO-HS-007 | Sales Hub Professional Upgrade (~$70/mo) | HIGH | LOW | **EXECUTIVE_DECISION** |
| AO-HS-008 | Four Pipeline Dashboards | HIGH | LOW | **READY_TO_BUILD** |
| AO-HS-009 | ROM Quote Automation | HIGH | MEDIUM | FUTURE_PHASE |
| AO-HS-010 | AI Deal Summarization (Claude API via n8n) | HIGH | MEDIUM | **READY_TO_BUILD** |

---

## Critical Gaps
| Priority | Gap |
|---|---|
| P0 | No HubSpot ↔ Houzz Pro integration — dual manual entry, data drift |
| P1 | No webhooks — poll-based only, no real-time triggers |
| P1 | Workflows locked — cannot build stage automations without $70/mo upgrade |
| P1 | COI Status not automated — expired subs may appear active |
| P2 | Zero dashboards — no pipeline visibility for leadership |

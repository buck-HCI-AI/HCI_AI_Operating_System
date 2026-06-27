# Process Automation Matrix
*HCI AI Operating System | Source: HCI-OR-001 | 2026-06-27*

---

## Current State (Before Automation)

| Process | Current Method | Manual Time | Error Risk | Automation Available |
|---------|---------------|-------------|------------|---------------------|
| COI tracking | Email + spreadsheet | 4 hrs/week | HIGH — expirations missed | YES — n8n cron |
| Bid invitations | Manual email | 3 hrs/week | MEDIUM — inconsistent | YES — HubSpot Lists + bulk email |
| Bid follow-up | Manual outreach | 2 hrs/week | HIGH — open packages stall | YES — HubSpot Sequences (Pro required) |
| Deal → Project transfer | Manual Houzz entry | 30 min/project | HIGH — data drift | YES — n8n webhook |
| Change order management | Email + paper | 2 hrs/project | HIGH — disputes, unsigned COs | YES — Houzz Pro |
| Punchlist creation | Manual at closeout | 4 hrs/project | MEDIUM — items missed | YES — AI from daily logs |
| Selection reminders | Manual client calls | 1 hr/week/project | MEDIUM — delays cascade | YES — Houzz Pro |
| Budget tracking | Unknown (QuickBooks?) | Unknown | HIGH — no real-time visibility | YES — Houzz Pro Budget |
| Schedule management | Unknown | Unknown | HIGH — no AI delay detection | YES — Houzz Pro Schedule |
| Lead response | Manual or none | Unknown | HIGH — 302 leads uncontacted | YES — AI auto-response |
| Invoice generation | External (QB/check) | Unknown | MEDIUM | YES — Houzz Pro Invoices |
| HubSpot dashboard setup | Not done | One-time 2 hrs | HIGH — zero executive visibility | YES — 4 dashboards |

---

## Automation Opportunity Map

### Tier 1: Automate Today (no new dependencies)

```
COI Management
─────────────────────────────────────────────
n8n cron (daily)
  └─→ GET /companies?properties=coi_expiration_date
  └─→ Filter: expires within 30 days
  └─→ Claude Haiku: draft renewal email
  └─→ Human review → send via HubSpot email
  └─→ LOG: project_events table (COI-EXPIRY event)

Bid Document Tracking  
─────────────────────────────────────────────
Upload bid package → HubSpot Documents
  └─→ Share link in bid invitation
  └─→ HubSpot tracks: opened / viewed / time spent
  └─→ n8n: if not_opened after 5 days → follow-up task

HubSpot Dashboards (2-hour setup)
─────────────────────────────────────────────
Setup: COI Health + Bid Pipeline + AR + Sub Performance
  └─→ Immediate executive visibility
  └─→ No development required
```

### Tier 2: Automate After Decisions (requires upgrade or extraction)

```
HubSpot Workflows (requires Pro upgrade — $70/mo)
─────────────────────────────────────────────
Trigger: Deal stage = "Sent Out"
  └─→ Create task: "Follow up with all invited subs"
  └─→ Enroll in bid follow-up sequence (email 1, email 2, call task)

Trigger: Company property coi_expiration_date < 30 days
  └─→ Create task: "Renew COI for {company_name}"
  └─→ Send renewal request email

HubSpot → Houzz Project Bridge (n8n webhook)
─────────────────────────────────────────────
Trigger: HubSpot Deal stage = "Awarded"
  └─→ n8n: POST /houzz-api/projects (create project)
  └─→ Map: deal_name → project_name, deal_amount → budget
  └─→ Map: contact_name → client_name, address → site_address
  └─→ LOG: project_events (DEAL-AWARDED event)
  └─→ NOTIFY: ntfy/hci-executive

Houzz Budget + Schedule (requires browser extraction first)
─────────────────────────────────────────────
After extraction:
  └─→ Auto-populate budget from estimate line items
  └─→ AI variance alerts: >10% overrun → PM notification
  └─→ Schedule delay: task overdue → shift dependent tasks
  └─→ Weekly schedule + budget status → Executive Morning Brief
```

### Tier 3: AI Automations (Phase 2-3)

```
AI Change Order Drafting
─────────────────────────────────────────────
Daily log contains out-of-scope language
  └─→ Claude Haiku: generate CO draft
  └─→ PM reviews → submits in Houzz Pro
  └─→ Client signs via Houzz client portal

AI Punchlist Generation  
─────────────────────────────────────────────
Project enters Closeout phase
  └─→ Retrieve last 30 days of daily logs
  └─→ Claude: identify unresolved items
  └─→ Auto-create punchlist tasks in Houzz Pro
  └─→ Assign to SS with photo evidence required

AI Selection Reminders
─────────────────────────────────────────────
Selection overdue (no approval after 7 days)
  └─→ Claude: draft client reminder
  └─→ PM reviews → sends via HubSpot email
  └─→ LOG: overdue_selections risk in project_risks_computed

AI Lead Response (303 uncontacted homeowners)
─────────────────────────────────────────────
New Houzz lead → n8n webhook
  └─→ Claude: draft personalized response
  └─→ HubSpot contact created / updated
  └─→ Buck reviews → approves → send
```

---

## n8n Workflow Build Queue

| Workflow ID | Name | Trigger | Complexity | Status |
|-------------|------|---------|------------|--------|
| COI-DAILY | COI Expiration Monitor | Daily cron | LOW | READY TO BUILD |
| BID-TRACK | Bid Document Open Alert | HubSpot webhook (Pro) | MEDIUM | PENDING UPGRADE |
| DEAL-BRIDGE | HubSpot→Houzz Project Sync | Deal stage webhook (Pro) | MEDIUM | PENDING UPGRADE |
| LEAD-RESPONSE | Houzz Lead Auto-Response | Houzz webhook (Zapier BETA) | MEDIUM | PENDING DESIGN |
| CO-DRAFT | AI Change Order Drafting | Daily log keyword trigger | MEDIUM | PENDING CA REVIEW |
| PUNCHLIST-AI | AI Punchlist Generation | Project stage = Closeout | MEDIUM | PENDING CA REVIEW |

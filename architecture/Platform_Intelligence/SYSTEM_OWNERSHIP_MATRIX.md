# System Ownership Matrix
*HCI AI Operating System | Source: HCI-OR-001 | 2026-06-27*

---

## Lifecycle Phase → System Ownership

| Lifecycle Phase | Primary System | Secondary System | HCI AI OS Role | Integration Gap |
|----------------|---------------|-----------------|----------------|----------------|
| Lead Capture | Houzz Pro (Leads) | HubSpot (Contacts) | Sync + score | Houzz leads not in HubSpot |
| Initial Contact | HubSpot (Email) | — | AI draft + track | Sequences locked (Pro) |
| ROM / Estimating | HubSpot (Quotes) | Houzz Pro (Estimates) | Sync totals | Neither in use |
| Bidding | HubSpot (Deals) | HubSpot (Email + Docs) | Manage + track | Lists not used, no doc tracking |
| Sub Selection | HubSpot (Contacts/Deals) | — | Score + recommend | Manual scoring |
| Contract Execution | External (DocuSign?) | — | Pending migration | Houzz Contracts unused |
| Project Kickoff | Houzz Pro (Projects) | HubSpot (Deals) | Bridge + sync | Manual transfer (critical gap) |
| Budget Management | Unknown (QuickBooks?) | Houzz Pro (Budget) | Visibility + alerts | Houzz Budget unused |
| Schedule Management | Houzz Pro (Schedule) | — | AI delay detection | Schedule unused |
| Field Operations | Houzz Pro (Tasks, Daily Log) | — | Summary + push | Partial HCI AI OS visibility |
| Procurement | HubSpot (Deals) | Houzz Pro (POs) | Bridge | POs unused |
| Change Orders | External (email/paper) | — | AI drafting | Houzz CO unused |
| Client Selections | External | Houzz Pro (Selection Boards) | Reminders + alerts | Selection boards unused |
| Invoicing | QuickBooks / check | Houzz Pro (Invoices) | Status sync | Houzz Invoices unused |
| Closeout / Punchlist | Manual | Houzz Pro (Tasks) | AI generation | Punchlist not AI-generated |
| Sub Management | HubSpot (Companies/Contacts) | — | COI + performance | COI tracking manual |
| Executive Reporting | HCI AI OS | HubSpot (Dashboards) | Morning brief + weekly | No HubSpot dashboards |

---

## Data Ownership Map

| Data Type | Where It Lives | Should Live | Sync Needed |
|-----------|---------------|-------------|-------------|
| Subcontractors | HubSpot Contacts | HubSpot (primary) | YES — COI auto-sync |
| Sub Companies + COI | HubSpot Companies | HubSpot (primary) | YES — COI engine |
| Active Projects | BOTH (HubSpot Deals + Houzz Projects) | HubSpot → Houzz | YES — bridge critical |
| Project Budget | Unknown (QB?) | Houzz Pro | YES — activate Budget module |
| Project Schedule | None observed | Houzz Pro | YES — activate Schedule module |
| Change Orders | Email/paper | Houzz Pro | YES — activate CO module |
| Client Selections | Unknown | Houzz Pro | YES — activate Selections |
| Invoices | QB / check | Houzz Pro + QB sync | YES — migrate |
| Bid Packages | HCI AI OS database | HCI AI OS (stay) | Sync totals to HubSpot |
| Daily Logs | HCI AI OS + Houzz | HCI AI OS (primary) | Sync from Houzz |
| Field Photos | Houzz Pro (Files) | Houzz Pro + Google Drive | Sync via Drive integration |

---

## AI OS Role by System

| System | HCI AI OS Current Role | HCI AI OS Future Role |
|--------|-----------------------|----------------------|
| HubSpot | Sync contacts, deals, companies, notes (via connectors) | Add: COI engine, AI summaries, deal intelligence, board |
| Houzz Pro | None (pending browser extraction) | Add: schedule, budget, CO, punchlist, selections bridge |
| n8n | Orchestrator (cron jobs + approval gates) | Add: webhooks, COI workflow, deal bridge, lead response |
| Google Drive | Document storage (SOP indexing) | Add: project folder templates, photo sync |
| Project Brain | Intelligence per project | Add: use HubSpot + Houzz data once bridges built |
| Executive MC | Morning brief (current state) | Add: budget, schedule, CO status from Houzz |

---

## Integration Priority Matrix

```
CRITICAL (build now):
  HubSpot Deal → Houzz Pro Project bridge
  ↕ Enables: budget visibility, schedule tracking, CO management

HIGH (build Phase 1):  
  COI Engine (n8n cron → HubSpot Companies)
  Bid document tracking (HubSpot Documents)
  HubSpot Dashboards (4 dashboards, zero-code)

MEDIUM (Phase 2):
  Houzz Leads → HubSpot Contacts
  Change Orders activation
  Selections activation
  Invoice milestone automation

FUTURE (Phase 3+):
  QuickBooks ↔ Houzz Pro sync
  Houzz Bids (requires sub-vendor adoption decision)
```

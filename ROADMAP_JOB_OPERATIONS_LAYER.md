# Roadmap — Job Operations Intelligence Layer
## Milestone 1: Operational Intelligence

**Authority:** Milestone 1 directive (make this the next milestone.docx, 2026-06-27)  
**Owner:** Buck Adams (PM & Superintendent, Hendrickson Construction, Inc. — owned by Chris Hendrickson; Owner/operator, HCI-AI)  
**Filter:** Every feature must serve SS Console, PM Console, Leadership Dashboard, Weekly Reports, or Project Brain  

---

## Milestone Definition

> **Done when:** Superintendents know what to do today. PMs know what to manage this week. Leadership sees all jobs in under 60 seconds. Friday reports generate automatically.

---

## Sprint 3 — Role-Based API Layer (Claude Code — immediate)

All reads from existing services — no new data stores needed.

| Task | Endpoint | Source Services | Acceptance |
|---|---|---|---|
| SS-001 | `GET /superintendent/{id}/today` | houzz, schedule_intelligence, project_brain | Returns all 10 console sections |
| SS-002 | `GET /superintendent/{id}` HTML | Above | Mobile-first HTML, card layout |
| SS-003 | n8n AUTO-SS-MORNING | Above | 06:00 daily, per project, ntfy push |
| PM-001 | `GET /pm/{id}/weekly` | houzz, bid_intelligence, approval_queue, schedule_intelligence | Returns all 10 console sections |
| PM-002 | `GET /pm/{id}` HTML | Above | Mobile-first HTML with approve buttons |
| PM-003 | n8n AUTO-PM-WEEKLY | Above | Monday 07:00, per project, ntfy push |
| LD-001 | `GET /leadership/dashboard` | All projects aggregated | Health cards, what-needs-me |
| LD-002 | `GET /leadership` HTML | Above | Extends /executive, RED/YELLOW/GREEN cards |
| RP-001 | `GET /reports/weekly/jobs` | All services | Full job report per project |
| RP-002 | `GET /reports/weekly/company` | All projects | Company executive summary |
| RP-003 | n8n AUTO-WEEKLY-JOB | Above | Friday 16:00, email PM + SS |
| RP-004 | n8n AUTO-WEEKLY-COMPANY | Above | Friday 16:30, email Buck + ntfy push |

---

## Sprint 4 — Project Brain Enhancement

Deepen the data layer to support richer console outputs.

| Task | Description |
|---|---|
| PB-001 | Health score calculation engine — per-project GREEN/YELLOW/RED |
| PB-002 | Risk detection rules — schedule delay, budget overrun, vendor issues |
| PB-003 | Daily log draft engine — pre-fill from yesterday + today's schedule |
| PB-004 | "What needs me?" ranker — decision urgency × financial impact × age |
| PB-005 | Client communication tracker — last contact date, open action items |

---

## Sprint 5 — Google Drive + Outlook Connectors

Closes the data source gaps for full console coverage.

| Task | Description | Blocker |
|---|---|---|
| DR-001 | Google Drive Connector (BaseConnector) | OAuth tokens needed |
| DR-002 | File/document count per project per week | Drive connector |
| OL-001 | Outlook/email Connector | Microsoft Graph API credentials |
| OL-002 | Client email thread mining | Outlook connector |
| OL-003 | RFI detection from email threads | Outlook connector |

---

## Sprint 6 — Weather + Inspection + Photo Intelligence

| Task | Description |
|---|---|
| WX-001 | Weather API integration (OpenWeatherMap) — risk flags in SS console |
| IN-001 | Inspection schedule parser from Houzz tasks |
| PH-001 | Photo requirement tracker — flag inspection items missing photos |

---

## Sprint 7 — Mobile Polish + QuickBooks

| Task | Description |
|---|---|
| QB-001 | QuickBooks Connector — invoices, payments, expenses | Needs credentials |
| QB-002 | Budget vs QuickBooks reconciliation in PM console | QB connector |
| MOB-001 | iOS Shortcut: "What needs me?" → Leadership dashboard | |
| MOB-002 | One-tap project health card → SS console deep link | |

---

## Feature Filter (permanent rule)

Before building anything, ask:

> **Does this feature directly improve the SS Console, PM Console, Leadership Dashboard, Weekly Reports, or Project Brain?**

If no → add to AUTONOMY_BACKLOG for future consideration, don't build now.

---

## Success Metrics

| Metric | Target | Measured by |
|---|---|---|
| SS time to know today's priorities | < 2 minutes | User feedback |
| PM time to get weekly project view | < 5 minutes | User feedback |
| Buck review time for all projects | < 5 minutes | User feedback |
| Friday reports: manual effort required | 0 minutes | Automation logs |
| Owner decisions per week requiring excavation | 0 | executive_inbox count |

---

## Connector Readiness for Milestone 1

| Data Source | Sprint 3 Coverage | Notes |
|---|---|---|
| Houzz | ✅ Full (17 entities) | Primary data source — all console sections |
| HubSpot | ✅ contacts/deals/activities | Client comms + vendor contacts |
| Google Drive | ⏳ Sprint 5 | File counts only until connector built |
| Outlook | ⏳ Sprint 5 | Email summary via HubSpot until then |
| Bid Leveling | ✅ Service live | Procurement status in PM console |
| Approval Queue | ✅ Service live | Open decisions in all consoles |
| Schedule Intelligence | ✅ Service live | Variance calculations |
| Vendor Registry | ✅ Service live | Vendor risk in PM + SS consoles |
| Historical Cost | ✅ Service live | Budget trend analysis |
| Project Brain | ✅ Service live | Project metadata backbone |

---

*Roadmap — Job Operations Intelligence Layer | HCI AI Operating System*  
*Milestone 1 — Operational Intelligence | Authorized: Buck Adams 2026-06-27*

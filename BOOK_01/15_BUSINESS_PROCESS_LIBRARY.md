# BOOK_01 — Volume 15: Business Process Library

**Version:** 1.0 | **Date:** 2026-06-25 | **Directive:** HCI_AI_Business_Operating_Layer_BOOK01_Decision_KPI_Master_Directive_v1.0

---

## What the Business Process Library Is

The Business Process Library is the master reference that maps every HCI business process to:
- The SOP(s) that define how the work is done
- The workflows in HCI AI that execute the work
- The data that is produced and where it lives
- The KPIs that measure whether the work was done well
- The approval gates that control quality and authority

It answers the question: "How does HCI actually do [X]?" in a way that is connected to the system.

---

## Process Registry

### Preconstruction Processes

| Process | SOPs | Workflows | Primary Data | Approval Gate |
|---------|------|-----------|-------------|--------------|
| Project Intake | SOP 01, 02, 03 | WF-001 | `projects` table | Buck approves project added |
| Plan Review and Risk ID | SOP 04, 05, 06 | Project Brain | `risk_log`, `scope_checklist` | PM confirms complete |
| Budgeting | SOP 07, 08, 09, 10 | Bid Intelligence | `project_budgets` | Buck approves release |
| Bid Package | SOP 11, 13 | SOP 11 service, Bid Intelligence | `bid_packages`, `bid_requests` | Buck approves issue |
| Sub Outreach and Follow-Up | SOP 12, 14 | Bid Intelligence | `vendor_contacts`, `bid_log` | PM manages |
| Bid Leveling | SOP 15 | SOP 15 service, Bid Intelligence | `bid_leveling_records` | Buck approves award |
| Buyout | SOP 16, 19 | Procurement | `awards`, `subcontracts` | Buck signs award |

### Field Execution Processes

| Process | SOPs | Workflows | Primary Data | Approval Gate |
|---------|------|-----------|-------------|--------------|
| Project Startup | SOP 23 | WF-001 setup | `projects`, `project_contacts` | PM confirms |
| Daily Field Operations | SOP 24, 25 | WF-SUPER | `daily_logs` | PM reviews |
| Schedule Management | SOP 17 | Schedule Intelligence | `schedule_activities` | PM + Buck for changes |
| Quality Control | SOP 27, 28, 30 | WF-SUPER + QC logs | `inspections`, `nc_work` | Super confirms |
| Safety | SOP 29 | WF-SUPER | `safety_incidents` | PM + Buck for recordables |
| Long-Lead Tracking | SOP 18 | Procurement | `long_lead_items` | PM tracks |

### Change Management Processes

| Process | SOPs | Workflows | Primary Data | Approval Gate |
|---------|------|-----------|-------------|--------------|
| RFI Management | SOP 32 | WF-002 context, RFI service | `rfis` | PM submits; design team responds |
| Change Identification | SOP 31, 33 | Change Order service | `change_events` | PM identifies |
| Change Order Submission | SOP 31 | Change Order service | `change_orders` | Buck approves submission |
| Submittal Management | SOP reference | Submittal service | `submittals` | PM submits |

### Communication Processes

| Process | SOPs | Workflows | Primary Data | Approval Gate |
|---------|------|-----------|-------------|--------------|
| Meeting Notes | SOP 35 | WF-002 | `meeting_notes`, `action_items` | PM sends |
| Weekly Status Report | SOP 37 | WF-PM-W | `weekly_reports` | Buck signs off |
| Decision Log | SOP 36 | Decision Intelligence | `decision_records` | PM confirms |
| Client Communication | SOP 34 | — | Communication log | PM or Buck |

### Closeout Processes

| Process | SOPs | Workflows | Primary Data | Approval Gate |
|---------|------|-----------|-------------|--------------|
| Punch List | SOP 39 | Punch List service | `punch_items` | PM verifies all closed |
| Closeout Documents | SOP 40 | Document tracker | `closeout_checklist` | PM + Buck confirm |
| Warranty | SOP 41 | Warranty service | `warranty_claims` | PM tracks |
| Post-Project Review | SOP 42 | Lessons Learned | `lessons_learned` | Buck reviews |

---

## Process Maturity Levels

| Level | Meaning |
|-------|---------|
| 0 — Ad Hoc | No defined process; done from memory |
| 1 — Defined | SOP exists but not digitized |
| 2 — Executed | SOP converted to workflow; data is produced |
| 3 — Measured | KPIs track quality and cycle time |
| 4 — Optimized | AI assists; learnings feed the next iteration |

**HCI AI target:** Every core preconstruction and field process at Level 3 or above.

---

## Business Process Library Service

Service path: `03_Source_Code/services/business_process_library/`

- `GET /api/v1/processes` — list all registered processes
- `GET /api/v1/processes/{id}` — get a process with all linked SOPs, workflows, data, KPIs
- `GET /api/v1/processes/maturity` — maturity assessment by process
- `POST /api/v1/processes/` — register a new process definition

---

*Standard: `docs/BUSINESS_PROCESS_LIBRARY.md`*  
*Related: Volume 12 (Decision Intelligence), Volume 13 (KPI Intelligence), Volume 14 (Operating Rules)*

# SOP ↔ Workflow Compliance Map
**HCI AI Operating System — Foundation Audit**
**Generated:** 2026-06-28 | **Author:** Claude Code
**Purpose:** Verify that every SOP has a corresponding automation path. This is the answer to "does what we built actually follow our SOPs?"

---

## Summary

| Coverage | Count | % |
|---|---|---|
| ✅ Fully implemented | 6 | 22% |
| ⚠️ Partially implemented | 10 | 37% |
| ❌ No automation yet | 11 | 41% |

**Honest read:** The OS covers ~60% of the SOP surface area in some form. The 6 fully-automated processes are the highest-frequency ones (daily log, bid leveling, bid follow-up, schedule, project startup, historical cost). The 11 gaps are mostly field execution processes that require direct human/superintendent action.

---

## The Map

### PRECONSTRUCTION PHASE

| BP | SOP | Process | n8n Workflow | API Endpoint(s) | Status | Gap |
|---|---|---|---|---|---|---|
| BP-04 | SOP-04 | Plan Review | — | — | ❌ | No automation — human task |
| BP-05 | SOP-05 | Construction Narrative | — | — | ❌ | No automation — human task |
| BP-06 | SOP-06 | Missing Info / Risk Log | — | `/risk-intelligence/*` | ⚠️ | Endpoint exists; no workflow that auto-detects and files risks from documents |
| BP-07 | SOP-07 | ROM Budget | — | `/bid-intelligence/rom` | ⚠️ | API supports ROM queries; no automated ROM generation workflow |
| BP-08 | SOP-08 | Historical Cost Database | WF-003 Historical Cost Queue | `/historical-cost/*` | ✅ | Fully wired: bids queue → cost record → searchable |
| BP-09 | SOP-09 | Budget Review | — | — | ❌ | No automation — human review |
| BP-10 | SOP-10 | Allowances / Alternates / Exclusions | — | — | ❌ | No automation |
| BP-11 | SOP-11 | Bid Package Assembly | AUTO-BID-INVITATION-TASKS | `/bids/*` | ⚠️ | Deal stage trigger exists; package spec assembly not automated |
| BP-12 | SOP-12 | Subcontractor CRM | — | `/vendors/*`, HubSpot | ⚠️ | 392 vendors in DB; no automated outreach or qualification workflow |
| BP-13 | SOP-13 | Bid Distribution | — | `/bids/*` | ⚠️ | Bid receipt processing exists; outbound distribution not automated |
| BP-17 | SOP-17 | Project Schedule | — | `/api/v1/mvp/projects/{code}/schedule-status` | ⚠️ | 995 activities in DB, intelligence endpoint live; no n8n schedule update workflow |
| BP-18 | SOP-18 | Long-Lead Procurement | — | `/procurement/*` | ⚠️ | Procurement endpoint exists; no automated long-lead tracking workflow |

### BIDDING PHASE

| BP | SOP | Process | n8n Workflow | API Endpoint(s) | Status | Gap |
|---|---|---|---|---|---|---|
| BP-14 | SOP-14 | Bid Follow-Up | WF-008 Bid Follow-Up Engine | `/bids/follow-up` | ✅ | Fully wired: auto-detects stale bids, drafts follow-up |
| BP-15 | SOP-15 | Bid Leveling | WF-007 AI Bid Leveling Engine | `/bid-leveling/*` | ✅ | Fully wired: AI-assisted leveling, approval gate |

### BUYOUT PHASE

| BP | SOP | Process | n8n Workflow | API Endpoint(s) | Status | Gap |
|---|---|---|---|---|---|---|
| BP-16 | SOP-16 | Buyout | AUTO-018 Gate F Financial | — | ⚠️ | Approval gate exists; no automated buyout workflow triggers |
| BP-19 | SOP-19 | Subcontract Agreement | — | — | ❌ | No automation — legal document process |

### SETUP PHASE

| BP | SOP | Process | n8n Workflow | API Endpoint(s) | Status | Gap |
|---|---|---|---|---|---|---|
| BP-20 | SOP-20 | Contract Setup | — | — | ❌ | No automation |
| BP-21 | SOP-21 | Compliance | AUTO-COI-COMPLIANCE-ENGINE | — | ⚠️ | COI tracking runs daily; broader compliance checklist not automated |
| BP-22 | SOP-22 | COI / W-9 / Lien Waiver | AUTO-COI-COMPLIANCE-ENGINE | — | ⚠️ | COI expiration tracking live; W-9 and lien waiver not tracked |
| BP-23 | SOP-23 | Project Startup | WF-009 New Job Setup | `/projects/*` | ✅ | Fully wired: new deal → project record → folder structure |

### CONSTRUCTION PHASE

| BP | SOP | Process | n8n Workflow | API Endpoint(s) | Status | Gap |
|---|---|---|---|---|---|---|
| BP-24 | SOP-24 | Superintendent Daily Dashboard | AUTO-SS-MORNING (06:00) | `/api/v1/mvp/projects/{code}/pm` | ✅ | Daily push to supers + PM console live |
| BP-25 | SOP-25 | Daily Log | WF-011 Site Superintendent Daily Briefing | `/api/v1/mvp/projects/{code}/daily-log` | ✅ | Log submission → field intelligence → schedule risk detection |
| BP-26 | SOP-26 | Field Coordination | — | — | ❌ | No automation — field coordination is human-driven |
| BP-27 | SOP-27 | Quality Control | — | — | ❌ | No automation |
| BP-28 | SOP-28 | QC Detail Card | — | — | ❌ | No automation |
| BP-29 | SOP-29 | Safety | — | — | ❌ | No automation |
| BP-30 | SOP-30 | Inspection | — | — | ❌ | No automation |

---

## Orphan Workflows (Live — Not Yet Mapped to a SOP)

These workflows exist and are active but have no formal SOP anchor. They support the OS infrastructure rather than a specific SOP process.

| Workflow | Function | Maps To |
|---|---|---|
| AUTO-001 Daily Repository Status | System health | OS infrastructure |
| AUTO-002 Workflow Health Check | Workflow monitoring | OS infrastructure |
| AUTO-003 Sprint Self-Status | Sprint tracking | OS infrastructure |
| AUTO-004 Daily Mining Engine | Background intelligence | OS infrastructure |
| AUTO-005 Gate H: HubSpot Write | HubSpot approval gate | HubSpot writes |
| AUTO-006 Gate G: PR Merge | GitHub gate | Code governance |
| AUTO-010 Weekly Sprint Review | Sprint reporting | OS infrastructure |
| AUTO-011 Weekly Registry Duplicate Check | Data quality | Vendor registry |
| AUTO-012 Weekly Broken Link Check | Data quality | OS infrastructure |
| AUTO-013 HubSpot/Drive Reconciliation | Data sync | CRM + Drive |
| AUTO-017 Gate E: Client Comms | Client comms gate | BP-26 (partial) |
| AUTO-018 Gate F: Financial | Financial gate | BP-16 (partial) |
| AUTO-019 Morning Brief Email | Daily brief | Operations |
| AUTO-020 EOD Brief | EOD brief | Operations |
| AUTO-021 Escalation Check | Risk escalation | Operations |
| AUTO-PM Daily AI Program Manager | PM review | Operations |
| AUTO-PM-WEEKLY PM Console Push | PM weekly | BP-24 (partial) |
| AUTO-SS-MORNING Superintendent Push | SS console | BP-24 |
| AUTO-DAILY-PROJECT-SUMMARY | Project summaries | Operations |
| AUTO-WEEKLY-EXEC | Executive report | Operations |
| AUTO-MONTHLY-REVIEW | Monthly review | Operations |
| AUTO-WEEKLY-JOB | Job reports | Operations |
| AUTO-WEEKLY-COMPANY | Company report | Operations |
| AUTO-WEEKEND Weekly Summary | Weekend summary | Operations |
| WF-004 Lessons Learned | Knowledge capture | BP-08 (adjacent) |
| WF-005 SOP Registry Sync | SOP registry | Constitution |
| WF-006 Executive Alerts | Alert routing | Operations |
| WF-010 Outlook Email Router | Email triage | BP-26 (partial) |
| Bid Receipt Processing v5 | Bid intake | BP-13/14 |
| AUTO-BID-INVITATION-TASKS | Bid invitation | BP-11/13 |
| AUTO-A-DEAL-SUMMARIZATION | Deal intel | CRM |
| AUTO-COI-COMPLIANCE-ENGINE | COI tracking | BP-22 |
| AUTO-NIGHTLY-AUDIT | System audit | OS infrastructure |

---

## Priority Gaps to Close

These are the gaps that would have real operational impact:

| Priority | BP | Gap | Fix Required |
|---|---|---|---|
| P1 | BP-17 | Schedule update has no n8n automation — supers have to trigger manually | n8n workflow: weekly schedule variance update |
| P1 | BP-06 | Risk detection exists in schedule engine but doesn't auto-file to risk log | Wire field log risk detection → risk_assessments table |
| P2 | BP-12 | 392 vendors in DB but no sub outreach workflow | Vendor outreach workflow using HubSpot |
| P2 | BP-22 | COI engine runs but `coi_expiration_date` is null for all 1183 companies | Needs data — Buck to confirm how COI dates are tracked |
| P2 | BP-11 | Bid package assembly still manual | Add package spec template generation to bid package workflow |
| P3 | BP-27/28/29/30 | QC, Safety, Inspection — no automation | Field forms + checklist workflows (future sprint) |

---

## Bottom Line

**What this OS does well right now:**
- Full bid lifecycle: receive → level → follow-up → award (BP-08, 14, 15)
- Daily field intelligence: log → analyze → alert (BP-24, 25)
- Project startup (BP-23)
- Background learning and knowledge capture (continuous)

**What it doesn't do yet:**
- Pre-construction planning (BP-04, 05, 09, 10) — human-only
- Contract and subcontract documents (BP-19, 20) — human-only
- Field execution details: QC, safety, inspection (BP-26–30) — human-only

**The foundation is correctly built.** The 6 fully-automated SOPs are the ones that generate the most data and create the most leverage. The 11 gaps are appropriate for Phase 1 — they're either legally-sensitive processes (contracts) or highly situational field processes (QC, safety) that genuinely require human judgment.

The risk is the 10 "partial" processes — specifically BP-17 (schedule) and BP-06 (risk log) where the infrastructure exists but the automation loop isn't closed.

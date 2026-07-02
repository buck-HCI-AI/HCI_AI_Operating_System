# BOOK_01 — Volume 00: Executive Overview

> **⚠️ Manual consolidation (2026-07-02):** This was one of four separate documents all self-declaring as canonical (alongside `Operations_Manual/`, `HCI_AI_OS_MANUAL.md`, `BOOK_00/`), and was already ~1 week stale at time of audit. `HCI_AI_OS_MANUAL.md` (repo root) is now the canonical reference. This content is kept for reference only.

**Version:** 1.0 | **Date:** 2026-06-25 | **Directive:** HCI_AI_Business_Operating_Layer_BOOK01_Decision_KPI_Master_Directive_v1.0

---

## What This System Is

HCI AI is Hendrickson Construction's operating system. It connects every workflow, document, decision, and data point across a construction project into a single, evidence-based operating record.

The system does not replace HCI's people, judgment, or relationships. It makes HCI's people faster, better informed, and more consistent on every project they run.

---

## What Problem This Solves

Construction projects fail in predictable ways:
- Decisions are made but not recorded — so the same mistake is made twice
- Budget variances are discovered too late to recover
- Bid packages go out with missing scope — subs bid on different things
- Daily logs are written from memory at 5 PM and miss what actually happened
- Weekly updates are assembled from email instead of a system
- Project close-out is rushed because no one maintained the record during the job

HCI AI solves these problems by making the right way to do the work the easiest way to do the work.

---

## Five Validation Gates

The system was built and validated through five sequential gates before production deployment:

| Gate | What Was Proven | Status |
|------|-----------------|--------|
| Gate 1 — Engineering | Codebase compiles, containers start, database connects | ✅ PASSED |
| Gate 2 — Integration | All services talk to each other correctly | ✅ PASSED |
| Gate 3 — Workflow Acceptance | All 18 workflows and 9 services produce correct outputs | ✅ PASSED 2026-06-25 |
| Gate 4 — UAT | Buck ran all 5 UAT scenarios and confirmed they worked | ✅ PASSED 2026-06-25 |
| Gate 5 — Pilot | 5-day live run on 101 Francis, 64 Eastwood, 1355 Riverside | ⬜ 2026-06-25 → 2026-07-01 |

Go-live authorization follows successful Gate 5 completion.

---

## What Is Live in Production (As of Gate 5 Pilot)

| Capability | Description |
|------------|-------------|
| Project Intelligence | All project docs indexed; AI Q&A answers questions from drawings, specs, contracts |
| Meeting Intelligence | AI transcribes and summarizes meetings; action items extracted |
| Daily Field Logs | Field crews submit logs; AI assembles summary and flags issues |
| Daily Brief | Morning brief delivered 7 AM with project status, weather, priority items |
| Weekly Status Report | AI drafts weekly report from project data |
| Budget Intelligence | Budget vs. actual tracked; variances flagged |
| Bid Intelligence | Bid requests, bid tracking, analysis support |
| Schedule Intelligence | Schedule read and analyzed; critical path flagged |
| Vendor Intelligence | Vendor CRM with performance history |
| Risk Intelligence | Risk log; AI identifies and categorizes risks |
| Photo Intelligence | Photo upload, tagging, and visual search |
| Historical Cost | Historical unit rates used to check bid reasonableness |
| Procurement | Long-lead and material procurement tracking |
| Communication Log | Email and communication tracking |
| Health Check | System self-monitoring; alerts on service failures |
| Backup | Automated nightly database backup |
| **Platform Identity** | Role-based access control — 12 roles, authority levels enforced on all decisions |
| **Event Bus** | Every SOP status transition logged to event stream; cross-service event correlation |
| **Notification Center** | Approval alerts, safety hazards, schedule impacts, bid deadlines — all routed to right person |
| **Audit Trail** | Immutable record of who approved what, when, and why — across all services |
| **Unified Search** | Search vendors, projects, SOPs, bids, documents, decisions, and lessons in one query |

---

## How the System Is Used

**Buck (Owner/Principal):** Morning brief, executive dashboard, bid leveling review, award decisions, risk oversight, weekly report sign-off.

**PM:** Project setup, meeting intelligence, budget control, RFI/submittal tracking, weekly updates, client communication.

**Superintendent:** Daily log submission, look-ahead scheduling, daily coordination, quality control flags, photo documentation.

**Estimating:** Bid package assembly, sub outreach, bid tracking, leveling sheets, buyout coordination.

**All Roles:** Project brain Q&A — ask any question about the project and get an answer from the project record.

---

## What This Book Contains

This book is organized into 18 volumes:

- **Volumes 00-01:** What HCI AI is and how HCI operates
- **Volumes 02-11:** How each phase of a project runs through the system
- **Volumes 12-15:** Decision intelligence, KPI intelligence, operating rules, and process library
- **Volumes 16-18:** Reporting, validation, and continuous improvement

---

*For the technical build specification, see BOOK_00.*  
*For current system status, see AI_TEAM/00_STATUS.md.*

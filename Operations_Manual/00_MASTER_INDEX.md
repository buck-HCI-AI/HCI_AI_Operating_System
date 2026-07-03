# HCI AI Operations Manual

> **⚠️ Manual consolidation (2026-07-02):** A full-system audit found FOUR separate documents all independently declaring themselves "the single source of truth" (this one, `HCI_AI_OS_MANUAL.md`, `BOOK_00/`, `BOOK_01/`), none referencing the others. Per Buck Adams' "fix and clean up everything" directive that day, `HCI_AI_OS_MANUAL.md` (repo root) was adopted as canonical going forward — it's the newest and most complete. This manual's content (31 chapters, procedure-style, still accurate on the facts spot-checked) is kept for reference but is no longer the primary document. Chapters 27 and 28 were never finished.

## Hendrickson Construction, Inc. — Full Operations Guide
**Version:** 1.0 | **Ratified:** 2026-06-30 | **Authority:** Buck Adams (PM & SS, Hendrickson Construction; HCI-AI Owner)
**Authors:** GBT (Chief Architect) + Claude Code (Lead Implementation Engineer)
**Classification:** Internal Operations — Confidential

---

> This manual is the single source of truth for how Hendrickson Construction operates through the HCI AI Operating System. Every role, every process, every exception is documented here. If it is not in this manual, it does not exist as a standard.

---

## HOW TO USE THIS MANUAL

This manual has three parts:

**Part I — Business Operations** (Chapters 1-16)
How your people run jobs — daily routines, decisions, communications. Written for Buck, Jim (SS), office staff, and trade partners. You do not need to understand the technology to use Part I.

**Part II — AI System Operations** (Chapters 17-26)
How the AI system runs — monitoring, integrations, troubleshooting, emergencies. Written for Buck and Claude Code. Reference this when something is wrong or when you need to understand what the system is doing.

**Part III — Governance** (Chapters 27-31)
Rules, authority, and accountability. Who can approve what. How the AI team operates. How new projects get onboarded.

---

## MASTER CHAPTER INDEX

### Part I — Business Operations

**Note (Claude Code, 2026-07-01):** this table originally described a planned 16-chapter
outline before the chapters existed. GBT's 12 chapters (1-12) shifted titles/topics from
that original plan (corrected below to match what was actually written). Chapters 13-16
were then written by Claude Code per Buck's directive to fill the remaining real gaps,
using the topic assignments from the original Chief Architect chapter-assignment handoff
(`architecture/Agent_Handoff/Processed/GBT_HANDOFF_2026-06-30_OPERATIONS_MANUAL...`) for
the three that were still unwritten (Submittals, RFI, Close-Out), plus a Financial
Management & Approvals chapter distinct from Ch.08's project-level budget focus.

| Chapter | Title | Author | Status |
|---------|-------|--------|--------|
| 01 | What This System Is — Purpose & Philosophy | GBT | ✅ Complete |
| 02 | Daily Operations — Morning Routine (All Roles) | GBT | ✅ Complete |
| 03 | Field Operations | GBT | ✅ Complete |
| 04 | Project Manager Daily Workflow | GBT | ✅ Complete |
| 05 | Bid Package Management | GBT | ✅ Complete |
| 06 | Vendor and Subcontractor Management | GBT | ✅ Complete |
| 07 | Contract Management (incl. Change Order Management, §7.5) | GBT | ✅ Complete |
| 08 | Budget and Financial Controls | GBT | ✅ Complete |
| 09 | Schedule Management | GBT | ✅ Complete |
| 10 | Risk Management | GBT | ✅ Complete |
| 11 | Client Management | GBT | ✅ Complete |
| 12 | Insurance and Compliance | GBT | ✅ Complete |
| 13 | Submittal Management | Claude Code | ✅ Complete |
| 14 | Financial Management & Approvals (company-wide + accounting console) | Claude Code | ✅ Complete |
| 15 | RFI Management | Claude Code | ✅ Complete |
| 16 | Project Close-Out | Claude Code | ✅ Complete |
| 33 | Owner & Executive Daily Workflow (addendum — see note below) | Claude Code | ✅ Complete |

**Numbering note:** "Owner & Executive Daily Workflow" was the Chief Architect's original
Chapter 05 assignment (and top-priority item) but was never written as a standalone
chapter — Ch.05 as delivered covers Bid Package Management instead. Written 2026-07-01
as Chapter 33 rather than renumbering the 16 chapters already in place; it belongs to
Part I by content even though it's numbered outside the 1-16 range.

### Part II — AI System Operations

| Chapter | Title | Author | Status |
|---------|-------|--------|--------|
| 17 | System Architecture & Service Map | Claude Code | ✅ Complete |
| 18 | Daily System Monitoring | Claude Code | ✅ Complete |
| 19 | API & Gateway Operations | Claude Code | ✅ Complete |
| 20 | n8n Workflow Management | Claude Code | ✅ Complete |
| 21 | Integration Operations | Claude Code | ✅ Complete |
| 22 | Database & Data Management | Claude Code | ✅ Complete |
| 23 | Backup & Recovery | Claude Code | ✅ Complete |
| 24 | Approval Queue & Notification System | Claude Code | ✅ Complete |
| 25 | Troubleshooting Guide | Claude Code | ✅ Complete |
| 26 | Emergency Procedures | Claude Code | ✅ Complete |

### Part III — Governance

| Chapter | Title | Author | Status |
|---------|-------|--------|--------|
| 27 | AI Governance Model & Human Authority | GBT | ⬜ In Progress |
| 28 | Approval Authority Matrix | GBT | ⬜ In Progress |
| 29 | Security & Access Control | Claude Code | ✅ Complete |
| 30 | New Project Onboarding | GBT + Claude Code | ✅ Complete |
| 31 | System Updates & Change Management | Claude Code | ✅ Complete |
| 32 | System Intelligence Improvements (Overnight Analysis) | Claude Code | ✅ Active |

---

## QUICK REFERENCE

### Active Projects (Live)
| Code | Project | Health | Key Risk |
|------|---------|--------|----------|
| 64EW | 64 Eastwood, Aspen | 🟡 YELLOW | 2 open risks, exterior work |
| 101F | 101 Francis, Aspen | 🟡 YELLOW | Steel delay -5 days |
| 1355R | 1355 Riverside, Aspen | 🟢 GREEN | $3.54M, structural SOWs pending |
| 246GW | 246 Gallo Way, Aspen | 🟡 MONITORED | $6.3M, staged for go-live |

### Key System URLs
| System | URL | Purpose |
|--------|-----|---------|
| API Gateway | http://localhost:8000 | Primary API |
| GBT Bridge | https://speculate-armband-retinal.ngrok-free.dev | GBT access |
| n8n Workflows | http://localhost:5678 | Automation |
| Database | docker exec hci_postgres psql -U hci_admin -d hci_os | Data |
| ntfy Alerts | https://ntfy.sh/hci-ai-os-buck | Buck's phone |

### Daily Operations Schedule
| Time | What Happens | Who Benefits |
|------|-------------|-------------|
| 06:00 | SS morning console → Buck's phone | Jim Hendrickson (SS) |
| 07:00 | Morning brief email | Buck, all PMs |
| 07:30 Mon | Pilot weekly digest | Buck |
| 08:00+ | Buck reviews approval queue | Buck |
| 19:00 | End-of-day brief | Buck |
| 02:00 | System nightly backup + audit | System |
| 03:00 | Mining engine runs (HubSpot, Drive, Houzz) | System |

---

## REVISION HISTORY
| Date | Version | Change | By |
|------|---------|--------|----|
| 2026-06-30 | 1.0 | Initial creation — full overnight build | Claude Code + GBT |
| 2026-07-01 | 1.1 | Index corrected to match delivered Ch.1-12; added Ch.13-16 (Submittals, Financial Mgmt & Approvals, RFI, Close-Out) | Claude Code |
| 2026-07-01 | 1.2 | Added Ch.33 (Owner & Executive Daily Workflow) — the last remaining Part I gap from the original Chief Architect assignment | Claude Code |

*This manual is maintained in `/Users/buckadams/HCI_AI_Operating_System/Operations_Manual/`*
*GBT can read it at: `GET /gateway/drive/search?q=Operations+Manual`*

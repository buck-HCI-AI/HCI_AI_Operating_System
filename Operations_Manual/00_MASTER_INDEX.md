# HCI AI Operations Manual
## Hendrickson Construction, Inc. — Full Operations Guide
**Version:** 1.0 | **Ratified:** 2026-06-30 | **Authority:** Buck Adams (Owner)
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
outline before the chapters existed. GBT has since delivered 12 chapters — table below
corrected to match what was actually written (titles/topics shifted from the original
plan). Four originally-planned topics are not yet covered as standalone chapters —
see "Documentation Gaps" below.

| Chapter | Title | Author | Status |
|---------|-------|--------|--------|
| 01 | What This System Is — Purpose & Philosophy | GBT | ✅ Complete |
| 02 | Daily Operations — Morning Routine (All Roles) | GBT | ✅ Complete |
| 03 | Field Operations | GBT | ✅ Complete |
| 04 | Project Manager Daily Workflow | GBT | ✅ Complete |
| 05 | Bid Package Management | GBT | ✅ Complete |
| 06 | Vendor and Subcontractor Management | GBT | ✅ Complete |
| 07 | Contract Management | GBT | ✅ Complete |
| 08 | Budget and Financial Controls | GBT | ✅ Complete |
| 09 | Schedule Management | GBT | ✅ Complete |
| 10 | Risk Management | GBT | ✅ Complete |
| 11 | Client Management | GBT | ✅ Complete |
| 12 | Insurance and Compliance | GBT | ✅ Complete |

**Documentation Gaps — not yet covered as standalone chapters:**
- RFI Management (touched on tangentially in Ch.04/Ch.03; no dedicated chapter)
- Change Order Management (touched on tangentially in Ch.07/Ch.08; no dedicated chapter)
- Submittal Management (not covered)
- Project Close-Out (not covered)

Recommend these four as Chapters 13-16 to complete Part I as originally scoped, or fold
each into its closest existing chapter (RFI→Ch.04, Change Orders→Ch.07/08, Submittals→
Ch.05, Close-Out→new) if Buck prefers 12 chapters over 16 — Chief Architect's call.

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

*This manual is maintained in `/Users/buckadams/HCI_AI_Operating_System/Operations_Manual/`*
*GBT can read it at: `GET /gateway/drive/search?q=Operations+Manual`*

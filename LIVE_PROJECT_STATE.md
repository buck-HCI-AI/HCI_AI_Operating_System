# LIVE_PROJECT_STATE.md
## HCI AI Operating System — Current Live State

**Organization:** Hendrickson Construction, Inc.
**Owner:** @buck-HCI-AI
**Last Updated:** 2026-06-26 (Sprint 0 close / Sprint 1 pre-launch)
**Updated By:** Browser Claude (GitHub Administrator)
**Sprint:** Sprint 1 — System Verification (Pre-launch)
**Authority:** LIVE_PROJECT_STATE_TEMPLATE.md v1.0

> **Update Protocol:** Any agent may commit factual, observable updates to this file.
> Always append — never remove history. Tag significant changes with `[STATE CHANGE]`.
> Human owner is the final authority on all state decisions.

---

## 🚦 System Health Dashboard

| System | Status | Last Verified | Agent | Notes |
|---|---|---|---|---|
| n8n | 🟢 Live | 2026-06-26 | Claude Code | Docker — localhost:5678 |
| HubSpot CRM | 🟢 Live | 2026-06-26 | Claude Code | API connected |
| Google Drive | 🟢 Live | 2026-06-26 | Claude Code | Connected |
| Microsoft 365 | 🟢 Live | 2026-06-26 | Claude Code | Graph API active |
| MCP Server | 🟢 Live | 2026-06-26 | Claude Code | 31 tools — ngrok public URL active |
| GitHub Repo | 🟢 Live | 2026-06-26 | Browser Claude | main branch — no protection yet |
| Google Sheets | 🟢 Live | 2026-06-26 | Claude Code | Bid tracker active |
| Houzz (Browser) | 🔴 Not yet connected | — | — | Browser agent design complete; Sprint 1 |
| PostgreSQL | 🔴 Not yet deployed | — | — | Planned: next after MCP |
| Qdrant | 🔴 Not yet deployed | — | — | Planned: next after Postgres |
| Redis | 🔴 Not yet deployed | — | — | Planned: next after Qdrant |
| FastAPI | 🔴 Not yet deployed | — | — | Planned: Sprint TBD |

*Legend: 🟢 Live and healthy | 🟡 Live with issues | 🔴 Down or not yet deployed*

---

## 🧠 MCP Server Status — ACR-001 Complete

**[STATE CHANGE — 2026-06-26]** ACR-001 executed and committed by Claude Code.

| Item | Value |
|---|---|
| MCP Public URL | https://speculate-armband-retinal.ngrok-free.dev/mcp |
| Total Tools | **31** |
| Branch | feature/data-architecture-document-storage |
| Last Commit | ACR-001 complete — 31 tools |
| Push Status | NOT pushed — holding for Sprint 1 approval |
| Merge Status | NOT merged — holding for Gate G |

### New Tools Added (ACR-001 — 5 tools)

| Tool | Status | Dependency |
|---|---|---|
| ReadRepositoryStatus | ✅ Working | None |
| ReadDecisionLog | ✅ Working | None |
| ReadAutomationRegistry | ✅ Working | None |
| ReadLiveProjectState | ⚠️ Waiting | Requires LIVE_PROJECT_STATE.md at local path |
| ReadCurrentSprint | ⚠️ Waiting | Requires CURRENT_SPRINT.md at local path |

> **Browser Claude Note:** LIVE_PROJECT_STATE.md and CURRENT_SPRINT.md are now committed to this GitHub repository. Claude Code must pull the repo to populate the local files at `/Users/buckadams/HCI_AI_Operating_System/` before ReadLiveProjectState and ReadCurrentSprint will return live data.

### Bug Fixed
- ProjectMining tool: broken internal path (404) — **fixed**

### All 26 Existing Tools (Confirmed Working)
ReadProjectRegistry, ReadVendorRegistry, ReadConstructionOS, SearchDrive, ReadDriveFile, SearchHubSpotDeals, SearchCompanies, SearchContacts, ReadBidTracker, GenerateBidLevel, HistoricalCostLookup, ProcurementStatus, ScheduleStatus, DraftEmail, CreateTask, UpdateRegistry, AwardRecommendation, ProjectMining, GetApprovalQueue, CreateDriveFolder, UploadFileToDrive, ListDriveFolder, ReadSheet, WriteSheet, ExecutiveReport, GetROISummary

---

## 📋 Current Sprint

**Sprint:** 1 — System Verification
**Status:** Pre-launch — awaiting human owner Sprint 1 ACR
**Sprint Doc:** CURRENT_SPRINT.md (committed this session)
**Opened:** 2026-06-26
**Target Close:** TBD (human owner sets)

### Sprint Goal
Verify all live systems are registered and operating under governance, activate Sprint 1 automation workflows, and complete the integration state sync so every AI agent knows what exists and what it owns.

### Sprint 1 Pre-Launch Checklist
| Item | Status | Owner |
|---|---|---|
| LIVE_PROJECT_STATE.md created | ✅ Done | Browser Claude |
| CURRENT_SPRINT.md created | ✅ Done | Browser Claude |
| ACR-001 received and confirmed | ✅ Done | Browser Claude |
| Human owner issues Sprint 1 ACR | ⏳ Pending | @buck-HCI-AI |
| Claude Code pulls repo (local sync) | ⏳ Pending | Claude Code |
| Branch protection on main enabled | ⏳ Pending | @buck-HCI-AI |

---

## 🤖 Active Workflows (n8n + MCP)

| Workflow / Tool | Type | Schedule / Trigger | Status | Last Run |
|---|---|---|---|---|
| WF-007 — AI Bid Leveling Engine | n8n | Daily 5PM MDT + webhook | ✅ Live | Daily |
| ReadRepositoryStatus | MCP tool | On-demand | ✅ Live | ACR-001 |
| ReadDecisionLog | MCP tool | On-demand | ✅ Live | ACR-001 |
| ReadAutomationRegistry | MCP tool | On-demand | ✅ Live | ACR-001 |
| ReadLiveProjectState | MCP tool | On-demand | ⚠️ Waiting local file | ACR-001 |
| ReadCurrentSprint | MCP tool | On-demand | ⚠️ Waiting local file | ACR-001 |
| AUTO-001 — Daily Status Report | n8n | Daily 07:00 | ⏳ Sprint 1 setup | — |
| AUTO-002 — Workflow Health Check | n8n | Daily 06:00 | ⏳ Sprint 1 setup | — |
| AUTO-003 — n8n Self-Status | n8n | Daily 08:00 | ⏳ Sprint 1 setup | — |

---

## 🏗️ Active Construction Projects

| Project | HubSpot Pipeline | Bid Status | Last Update |
|---|---|---|---|
| 64 Eastwood Dr. | 2203777729 | Bidding | 2026-06-26 |
| 101 Francis St. | 2203777729 | Bidding | 2026-06-26 |
| 1355 Riverside Dr. | 2203777729 | Bidding | 2026-06-26 |

---

## 🔗 Integration Registry (Live Status)

| System | Auth Method | Read | Write | Gate | Status |
|---|---|---|---|---|---|
| GitHub | Token (Secrets) | ✅ | ✅ branches | Gate G | ✅ Active |
| HubSpot CRM | API Key | ✅ Connected | Gate H required | Gate H | ✅ Connected |
| Google Drive | OAuth | ✅ Connected | Restricted | Gate D | ✅ Connected |
| Microsoft 365 | Graph API | ✅ Active | N/A | — | ✅ Active |
| Google Sheets | API | ✅ Active | ✅ Active | — | ✅ Active |
| n8n | Internal | ✅ | ✅ workflows | Pre-approved | ✅ Active |
| MCP Server | ngrok HTTPS | ✅ 31 tools | Gate-controlled | Per-tool | ✅ Live (ACR-001) |
| Houzz Pro | Browser | Sprint 1 | ❌ Prohibited | HZ-R | Design complete |
| PostgreSQL | Internal | ⏳ | ⏳ | — | Not deployed |
| Qdrant | Internal | ⏳ | ⏳ | — | Not deployed |
| Redis | Internal | ⏳ | ⏳ | — | Not deployed |

---

## 🚧 Pending Human Decisions

| Item | Decision Needed | Priority | Raised By |
|---|---|---|---|
| Sprint 1 ACR | Issue Sprint 1 ACR to formally begin Sprint 1 | **Critical** | Claude Code |
| Branch protection on main | Enable Settings → Branches → Add rule | High | Browser Claude |
| ACR-001 PR merge | Merge feature/data-architecture-document-storage → main | High | Claude Code |
| Claude Code local pull | Pull repo so MCP ReadLiveProjectState / ReadCurrentSprint work | High | Browser Claude |
| INT-001 | Single repo confirmed? Yes — single repo architecture | Confirm | Browser Claude |

---

## ⚠️ Open Blockers

| Blocker ID | Description | Blocking | Raised | Status |
|---|---|---|---|---|
| BLOCK-001 | Branch protection not enabled on main | All PRs unprotected | 2026-06-26 | ⏳ Human action needed |
| BLOCK-002 | ReadLiveProjectState / ReadCurrentSprint returning not_found | MCP tools 30 + 31 | 2026-06-26 | ⏳ Claude Code pull needed |
| BLOCK-003 | ACR-001 branch not merged | MCP 31 tools on feature branch only | 2026-06-26 | ⏳ Human Gate G approval needed |
| BLOCK-004 | Sprint 1 ACR not issued | Sprint 1 formally blocked | 2026-06-26 | ⏳ @buck-HCI-AI |

---

## 📊 Task Counts (Current)

| Category | Total | Done | In Progress | Todo | Blocked |
|---|---|---|---|---|---|
| Governance (GOV) | 15 | 15 | 0 | 0 | 0 |
| Houzz Design (HZ-DESIGN) | 8 | 8 | 0 | 0 | 0 |
| Integration Planning (INT-DESIGN) | 6 | 6 | 0 | 0 | 0 |
| Core Automation (AUTO) | 25 | 0 | 0 | 25 | 0 |
| Houzz Implementation (HZ) | 13 | 0 | 0 | 13 | 0 |
| Integration Activation (INT) | 13 | 0 | 0 | 13 | 0 |
| **Total** | **80** | **29** | **0** | **51** | **0** |

*Last synced: 2026-06-26*

---

## 🤖 AI Agent Status

| Agent | Current Task | Last Active | Status |
|---|---|---|---|
| ChatGPT | Awaiting Sprint 1 ACR confirmation | 2026-06-26 | ⏳ ACR-001 received — Sprint 1 ACR pending |
| Claude Code | ACR-001 complete — 31 MCP tools on feature branch | 2026-06-26 | ✅ Holding for Sprint 1 approval |
| Browser Claude | LIVE_PROJECT_STATE.md + CURRENT_SPRINT.md created | 2026-06-26 | ✅ Sprint 1 pre-launch tasks complete |
| Codex | Not yet activated | — | ⏳ Sprint 2 |
| n8n | WF-007 running | Daily | ✅ Active (WF-007 only — AUTO-001/002/003 Sprint 1) |

---

## 📝 State Change Log

| Timestamp | Change | Agent | Notes |
|---|---|---|---|
| 2026-06-26 | Sprint 0 governance layer complete | Browser Claude | 15 governance docs + 6 Houzz docs committed |
| 2026-06-26 | Houzz workstream design complete | Browser Claude | houzz/ directory created |
| 2026-06-26 | Integration planning layer complete | Browser Claude | 5 integration docs committed |
| 2026-06-26 | LIVE_PROJECT_STATE_TEMPLATE.md created | Browser Claude | Template committed |
| 2026-06-26 | **[STATE CHANGE] ACR-001 complete** | Claude Code | MCP now has 31 tools — branch not yet merged |
| 2026-06-26 | LIVE_PROJECT_STATE.md activated | Browser Claude | Template populated with current system state |
| 2026-06-26 | CURRENT_SPRINT.md created | Browser Claude | Sprint 1 System Verification — pre-launch |

---

## 🏛️ Governing Documents Quick Reference

| Document | Purpose | Location |
|---|---|---|
| HCI_AI_CONSTITUTION.md | Supreme law | Root |
| AI_TEAM_CHARTER.md | Who does what | Root |
| APPROVAL_GATES.md | What requires human approval | Root |
| AUTOMATION_GOVERNANCE.md | What is automated | Root |
| SPRINT_OPERATING_MODEL.md | How sprints work | Root |
| PROJECT.md | Master roadmap + backlog | Root |
| TASKS.md | Active task register | Root |
| CURRENT_SPRINT.md | **Current sprint plan** | Root |
| IMPLEMENTATION_INTEGRATION_PLAN.md | Integration strategy | Root |
| REPOSITORY_RELATIONSHIP_MAP.md | Repo architecture | Root |

---

*LIVE_PROJECT_STATE.md | HCI AI Operating System | Hendrickson Construction, Inc.*
*Any agent may update this file with factual, observable state changes.*
*Authorized by: @buck-HCI-AI | Activated by: Browser Claude*

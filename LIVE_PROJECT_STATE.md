# LIVE_PROJECT_STATE.md
## HCI AI Operating System — Current Live State

**Organization:** Hendrickson Construction, Inc.
**Owner:** @buck-HCI-AI
**Last Updated:** 2026-06-26 (Sprint 1 — Active)
**Updated By:** Browser Claude (GitHub Administrator)
**Sprint:** Sprint 1 — System Verification (ACTIVE — ACR-002 issued)
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
| MCP Server | 🟢 Live | 2026-06-26 | Claude Code | 31 tools — ngrok URL active |
| GitHub Repo | 🟢 Live | 2026-06-26 | Browser Claude | main branch |
| Google Sheets | 🟢 Live | 2026-06-26 | Claude Code | Bid tracker active |
| Houzz (Browser) | 🔴 Not yet connected | — | — | Browser agent design complete; Sprint 1 |
| PostgreSQL | 🟡 Confirm needed | — | Claude Code | docker-compose shows data stack commit |
| Qdrant | 🟡 Confirm needed | — | Claude Code | docker-compose shows data stack commit |
| Redis | 🟡 Confirm needed | — | Claude Code | docker-compose shows data stack commit |
| FastAPI | 🔴 Not yet deployed | — | — | Planned |

*Legend: 🟢 Live and healthy | 🟡 Status unconfirmed — needs verification | 🔴 Down or not yet deployed*

> **Note to Claude Code:** docker-compose.yml commit message says "feat: data stack live — Postgr..." — please confirm if Postgres/Qdrant/Redis are actually live and update this table.

---

## 🧠 MCP Server Status — ACR-001 Complete

**[STATE CHANGE — 2026-06-26]** ACR-001 executed and committed by Claude Code.

| Item | Value |
|---|---|
| MCP Public URL | https://speculate-armband-retinal.ngrok-free.dev/mcp |
| Total Tools | **31** |
| Branch | feature/data-architecture-document-storage |
| Last Commit | ACR-001 complete — 31 tools |
| Push Status | NOT pushed to GitHub — local only |
| Merge Status | NOT merged — awaiting Gate G |

### New Tools Added (ACR-001 — 5 tools)

| Tool | Status | Notes |
|---|---|---|
| ReadRepositoryStatus | ✅ Working | — |
| ReadDecisionLog | ✅ Working | — |
| ReadAutomationRegistry | ✅ Working | — |
| ReadLiveProjectState | ✅ File exists on GitHub | Claude Code must pull to activate locally |
| ReadCurrentSprint | ✅ File exists on GitHub | Claude Code must pull to activate locally |

### Bug Fixed
- ProjectMining tool: broken internal path (404) — **fixed**

---

## 📋 Current Sprint

**Sprint:** 1 — System Verification
**Status:** 🟢 ACTIVE — ACR-002 issued (Issue #1)
**Sprint Doc:** CURRENT_SPRINT.md
**Opened:** 2026-06-26
**Target Close:** TBD

### Sprint Goal
Verify all live systems are registered and operating under governance, activate Sprint 1 automation workflows, integrate the ACR-001 MCP branch, and complete the state synchronization so every AI agent knows what exists and what it owns.

---

## 🤖 Active Workflows (n8n + MCP)

| Workflow / Tool | Type | Schedule / Trigger | Status |
|---|---|---|---|
| WF-007 — AI Bid Leveling Engine | n8n | Daily 5PM MDT + webhook | ✅ Live |
| ReadRepositoryStatus | MCP tool | On-demand | ✅ Live |
| ReadDecisionLog | MCP tool | On-demand | ✅ Live |
| ReadAutomationRegistry | MCP tool | On-demand | ✅ Live |
| ReadLiveProjectState | MCP tool | On-demand | ⚠️ Waiting Claude Code git pull |
| ReadCurrentSprint | MCP tool | On-demand | ⚠️ Waiting Claude Code git pull |
| AUTO-001 — Daily Status Report | n8n | Daily 07:00 | ⏳ Sprint 1 setup |
| AUTO-002 — Workflow Health Check | n8n | Daily 06:00 | ⏳ Sprint 1 setup |
| AUTO-003 — n8n Self-Status | n8n | Daily 08:00 | ⏳ Sprint 1 setup |

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
| PostgreSQL | Internal | 🟡 Confirm | 🟡 Confirm | — | Confirm with Claude Code |
| Qdrant | Internal | 🟡 Confirm | 🟡 Confirm | — | Confirm with Claude Code |

---

## 🚧 Pending Human Decisions

| Item | Decision Needed | Priority | Status |
|---|---|---|---|
| Merge ACR-001 branch | Push branch to GitHub → open PR → merge (Gate G) | **Critical** | ⏳ Claude Code must push branch first |
| Branch protection email verify | Check your GitHub email and click verify link | High | ⏳ Email sent to @buck-HCI-AI |

> **Note:** Branch protection was configured (PR required + 1 approval) but GitHub requires email identity verification to save security settings. Check your email from GitHub and click the verification link to activate.

---

## ⚠️ Open Blockers

| Blocker ID | Description | Blocking | Status |
|---|---|---|---|
| BLOCK-001 | Branch protection not yet activated — email verify needed | Merge protection | ⏳ @buck-HCI-AI check email |
| BLOCK-002 | ReadLiveProjectState/ReadCurrentSprint local files missing | MCP tools 30+31 | ⏳ Claude Code: git pull after merge |
| BLOCK-003 | ACR-001 branch not yet pushed or merged | MCP 31 tools on feature branch only | ⏳ Claude Code: git push + open PR |
| ~~BLOCK-004~~ | ~~Sprint 1 ACR not issued~~ | ~~Sprint 1 blocked~~ | ✅ **RESOLVED** — ACR-002 issued (Issue #1) |

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

---

## 🤖 AI Agent Status

| Agent | Current Task | Last Active | Status |
|---|---|---|---|
| ChatGPT | Sprint 1 kickoff — sync with Claude Code | 2026-06-26 | ⏳ ACR-002 issued — Sprint 1 active |
| Claude Code | Push ACR-001 branch + open PR | 2026-06-26 | ⏳ Waiting to push feature branch |
| Browser Claude | Sprint 1 pre-launch tasks complete | 2026-06-26 | ✅ Sprint 1 active |
| Codex | Not yet activated | — | ⏳ Sprint 2 |
| n8n | WF-007 running; Sprint 1 automations pending | Daily | ✅ WF-007 live |

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
| 2026-06-26 | **[STATE CHANGE] Sprint 1 ACTIVE — ACR-002 issued** | Browser Claude | Issue #1 created. Branch protection configured (email verify pending). BLOCK-004 resolved. |

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
| **CURRENT_SPRINT.md** | **Current sprint plan** | Root |
| IMPLEMENTATION_INTEGRATION_PLAN.md | Integration strategy | Root |
| REPOSITORY_RELATIONSHIP_MAP.md | Repo architecture | Root |

---

*LIVE_PROJECT_STATE.md | HCI AI Operating System | Hendrickson Construction, Inc.*
*Sprint 1 ACTIVE | Authorized by: @buck-HCI-AI | Maintained by: All agents*

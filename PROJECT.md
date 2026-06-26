# PROJECT.md
## HCI AI Operating System — Master Project Document
**Organization:** Hendrickson Construction, Inc.  
**Owner:** @buck-HCI-AI  
**Last Updated:** 2026-06-26  
**Constitution:** HCI_AI_CONSTITUTION.md  
**AI Team Charter:** AI_TEAM_CHARTER.md

---

## Mission

**Preserve Experience. Scale Expertise. Protect the Business.**

Build and operate an AI-powered operating system for Hendrickson Construction, Inc. that automates internal intelligence, integrates core business systems, and delivers executive-level insights — while maintaining complete human control over all consequential decisions.

---

## Success Criteria

- [ ] All integrated systems (HubSpot, Google Drive, GitHub, n8n) connected and reconciling
- [ ] 8 recurring automated reports operational (see AUTOMATION_GOVERNANCE.md)
- [ ] All approval gates (F, C, A, E, H, D, P, G) implemented and tested
- [ ] Historical project data mined and indexed
- [ ] Executive dashboards live and refreshing automatically
- [ ] Production readiness scorecard passing at Sprint 9 close
- [ ] Zero unauthorized writes to production CRM
- [ ] Full AI team operating within defined roles

---

## Governance Layer Status

| Document | Status | Sprint Created |
|---|---|---|
| HCI_AI_CONSTITUTION.md | ✅ Complete | Sprint 0 |
| AI_TEAM_CHARTER.md | ✅ Complete | Sprint 0 |
| AUTOMATION_GOVERNANCE.md | ✅ Complete | Sprint 0 |
| APPROVAL_GATES.md | ✅ Complete | Sprint 0 |
| SPRINT_OPERATING_MODEL.md | ✅ Complete | Sprint 0 |
| AI_WORKFLOW_ROLES.md | ✅ Complete | Sprint 0 |
| CONTRIBUTING.md | ✅ Complete | Sprint 0 |
| CODEOWNERS | ✅ Complete | Sprint 0 |
| PULL_REQUEST_TEMPLATE.md | ✅ Complete | Sprint 0 |
| Issue Templates (5) | ✅ Complete | Sprint 0 |
| PROJECT.md | ✅ Complete | Sprint 0 |
| GOVERNANCE_COMPLETION_REPORT.md | ✅ Complete | Sprint 0 |
| TASKS.md | ⏳ Pending | Sprint 1 |
| CURRENT_SPRINT.md | ⏳ Pending | Sprint 1 |
| CHANGELOG.md | ⏳ Pending | Sprint 1 |

---

## Sprint History

### Sprint 0 — Repository Audit (Active)
**Goal:** Establish full repository governance and automation operating model.  
**Status:** ✅ Governance layer complete. Automation setup in backlog.

**Completed:**
- [x] GitHub Project created: HCI AI Development
- [x] Milestones created: Sprint 0–10
- [x] 13 labels created
- [x] 5 issue templates created
- [x] CODEOWNERS, CONTRIBUTING.md, PULL_REQUEST_TEMPLATE.md created
- [x] HCI_AI_CONSTITUTION.md authored
- [x] AI_TEAM_CHARTER.md authored
- [x] AUTOMATION_GOVERNANCE.md authored
- [x] APPROVAL_GATES.md authored
- [x] SPRINT_OPERATING_MODEL.md authored
- [x] AI_WORKFLOW_ROLES.md authored
- [x] PROJECT.md created
- [x] GOVERNANCE_COMPLETION_REPORT.md created

---

## Automation Backlog

The following automation setup tasks are approved for Sprint 1 and Sprint 2:

### Priority 1 — Sprint 1

| ID | Task | Label | Assigned To |
|---|---|---|---|
| AUTO-001 | Set up n8n daily repository status report workflow | `n8n` `workflow` | n8n |
| AUTO-002 | Set up n8n workflow health check (daily 06:00) | `n8n` `workflow` | n8n |
| AUTO-003 | Set up n8n self-status report workflow (daily 08:00) | `n8n` `workflow` | n8n |
| AUTO-004 | Create reports/ directory structure in repository | `workflow` | Claude Code |
| AUTO-005 | Implement Gate H: HubSpot write approval workflow in n8n | `n8n` `hubspot` | n8n |
| AUTO-006 | Implement Gate G: PR merge notification to human owner | `workflow` `registry` | n8n |
| AUTO-007 | Create TASKS.md for Sprint 1 | `documentation` | ChatGPT |
| AUTO-008 | Create CURRENT_SPRINT.md for Sprint 1 | `documentation` | ChatGPT |
| AUTO-009 | Create initial CHANGELOG.md | `documentation` | Claude Code |

### Priority 2 — Sprint 2

| ID | Task | Label | Assigned To |
|---|---|---|---|
| AUTO-010 | Set up weekly sprint review summary workflow | `n8n` `workflow` | n8n |
| AUTO-011 | Set up weekly registry duplicate check | `n8n` `registry` | n8n |
| AUTO-012 | Set up weekly broken link check | `n8n` `workflow` | n8n |
| AUTO-013 | Set up HubSpot/Drive reconciliation report | `n8n` `hubspot` `drive` | n8n |
| AUTO-014 | Connect HubSpot API to n8n (read credentials) | `hubspot` `registry` | n8n |
| AUTO-015 | Connect Google Drive API to n8n | `drive` `registry` | n8n |
| AUTO-016 | Build Integration Registry schema in 05_Database/ | `registry` | Claude Code |
| AUTO-017 | Implement Gate E: client comms approval workflow | `n8n` `workflow` | n8n |
| AUTO-018 | Implement Gate F: financial action approval workflow | `n8n` `workflow` | n8n |

### Priority 3 — Sprint 3–4

| ID | Task | Label | Assigned To |
|---|---|---|---|
| AUTO-019 | Build HubSpot contact sync workflow | `hubspot` `n8n` | n8n |
| AUTO-020 | Build Drive file indexing workflow | `drive` `n8n` | n8n |
| AUTO-021 | Set up production readiness scorecard automation | `workflow` `testing` | ChatGPT / n8n |
| AUTO-022 | Configure branch protection rules on main | `workflow` | Human Owner |
| AUTO-023 | Implement MCP connectors | `mcp` | Claude Code |
| AUTO-024 | Set up n8n workflow status dashboard | `n8n` `workflow` | n8n |
| AUTO-025 | Gate audit log file structure setup | `workflow` `documentation` | Claude Code |

---

## Integration Registry

| System | Status | Auth | Read | Write |
|---|---|---|---|---|
| GitHub | ✅ Connected | Token (Secrets) | ✅ | ✅ (branches) |
| HubSpot CRM | ⏳ Pending setup | API Key (Secrets) | Planned | Gate H |
| Google Drive | ⏳ Pending setup | OAuth (Secrets) | Planned | Restricted |
| n8n | ⏳ Pending setup | Internal | Planned | Planned |
| MCP | ⏳ Sprint 5 | TBD | Sprint 5 | Sprint 5 |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| HubSpot API rate limit exceeded | Medium | Medium | Implement backoff in n8n workflows |
| Unauthorized CRM write | Low | High | Gate H mandatory; log all attempts |
| Sprint scope creep | Medium | Medium | Strict backlog discipline; human approval for scope changes |
| AI agent authority confusion | Low | Medium | Clear CODEOWNERS + CHARTER; escalation protocol |
| Production deployment without approval | Very Low | Critical | Gate P + branch protection |

---

*Governed by HCI_AI_CONSTITUTION.md | Owner: @buck-HCI-AI | Hendrickson Construction, Inc.*


---

## Workstream: Houzz Browser Intelligence
**Added:** 2026-06-26 | **Documents:** /houzz/

### Overview
Houzz is Hendrickson Construction's field execution platform. The Houzz Browser Intelligence Layer reads completed Houzz data and converts it into structured executive intelligence without changing superintendent behavior.

**Core Principle:** Capture data once in Houzz. Reuse it everywhere in HCI AI.

### Documents
| File | Purpose |
|---|---|
| `houzz/HOUZZ_READ_ONLY_AUDIT.md` | Constitutional compliance, data inventory, read-only rules |
| `houzz/HOUZZ_DAILY_LOG_WORKFLOW.md` | End-to-end 6-phase daily workflow |
| `houzz/HOUZZ_BROWSER_AGENT_STRATEGY.md` | Technical architecture, extraction schema, roadmap |
| `houzz/HOUZZ_APPROVAL_GATES.md` | 12 Houzz-specific gates (HZ-R through HZ-X3) |
| `houzz/HOUZZ_AUTOMATION_BACKLOG.md` | 13 implementation tasks (HZ-001 to HZ-013) |
| `houzz/HOUZZ_BROWSER_AGENT_COMPLETION_REPORT.md` | Workstream design completion report |

### Target Workflow
1. Superintendent uses Houzz normally
2. Houzz captures photos, weather, daily logs, labor, deliveries, schedule activity
3. Browser Agent reads completed Houzz data (read-only, Gate HZ-R)
4. HCI AI extracts structured intelligence
5. HCI AI generates: executive summary, PM action items, schedule impacts, procurement impacts, risk alerts, lessons learned candidates, tomorrow's priorities
6. No write-back to Houzz without approval gate

### Houzz Integration Registry Entry
| Field | Value |
|---|---|
| System | Houzz Pro |
| Access Method | Browser-based (no API assumed) |
| Auth Model | Human-initiated session |
| Read | ✅ Fully autonomous (Gate HZ-R) |
| Write | ❌ Permanently prohibited (HZ-X1/X2/X3) |
| Write-back to other systems | Requires applicable HZ gate |
| Sprint Target (Production) | Sprint 9 |

### Houzz Backlog Summary
| Task ID | Task | Sprint |
|---|---|---|
| HZ-001 | Houzz Daily Log Reader | Sprint 1 |
| HZ-002 | Reports Folder Structure | Sprint 1 |
| HZ-003 | Houzz Project Registry Entry | Sprint 1 |
| HZ-004 | n8n Daily Log Extraction Trigger | Sprint 2 |
| HZ-005 | Houzz-to-HCI-AI Project Health Engine | Sprint 2 |
| HZ-006 | HubSpot Project Status Write (Gate HZ-H1) | Sprint 3 |
| HZ-007 | Drive Daily Intelligence Filing | Sprint 3 |
| HZ-008 | Daily Executive Brief from Houzz | Sprint 4 |
| HZ-009 | PM Action Item Extractor | Sprint 4 |
| HZ-010 | Houzz Schedule Reader | Sprint 5 |
| HZ-011 | Houzz Photo Intelligence Extractor | Sprint 5 |
| HZ-012 | Superintendent Daily Log Draft Assistant | Sprint 8 |
| HZ-013 | Full Houzz Intelligence Pipeline — Production | Sprint 9 |


---

## Workstream: Program Repository Integration

**Added:** 2026-06-26 | **Documents:** Root level

### Overview

The Program Repository has been formally designated as the HCI AI control layer. This workstream establishes the coordination architecture between the governance layer (this repository) and all implementation work (Claude Code, n8n, external systems).

**Core Principle:** One repository. One governance layer. One sprint backlog. One truth.

### Documents

| File | Purpose |
|---|---|
| PROGRAM_REPOSITORY_STATUS.md | Current state, role, and health of this repository |
| PROGRAM_REPOSITORY_INVENTORY.md | Complete inventory of all committed files |
| REPOSITORY_RELATIONSHIP_MAP.md | Architecture: program layer vs. implementation layer |
| IMPLEMENTATION_INTEGRATION_PLAN.md | Overlap analysis, merge strategy, integration roadmap |
| LIVE_PROJECT_STATE_TEMPLATE.md | Shared state template — ChatGPT activates in Sprint 1 |

### Integration Architecture

```
HCI AI Operating System (this repo)
├── PROGRAM LAYER (governance, standards, sprint management)
├── WORKSTREAM LAYER (houzz/, future workstreams)
├── IMPLEMENTATION LAYER (03_Source_Code/, 04_Workflows/, 05_Database/)
└── KNOWLEDGE LAYER (reference, assets, SOPs)
```

### Integration Activation Backlog

| Task ID | Task | Owner | Sprint |
|---|---|---|---|
| INT-001 | Confirm: single repo or two repos? | @buck-HCI-AI | Sprint 0 close |
| INT-002 | Identify any separate Claude Code repo | @buck-HCI-AI | Sprint 0 close |
| INT-003 | Audit 04_Workflows/ for all active workflows | ChatGPT | Sprint 1 |
| INT-004 | Confirm HubSpot + Drive API connection status | Claude Code | Sprint 1 |
| INT-005 | Confirm Qdrant + Postgres live status | Claude Code | Sprint 1 |
| INT-006 | List all active n8n workflow names | n8n | Sprint 1 |
| INT-007 | Update TASKS.md with pre-existing work status | ChatGPT | Sprint 1 |
| INT-008 | Approve LIVE_PROJECT_STATE.md as shared truth | @buck-HCI-AI | Sprint 1 |
| INT-009 | Create LIVE_PROJECT_STATE.md from template | ChatGPT | Sprint 1 |
| INT-010 | Register all workflows in AUTOMATION_GOVERNANCE.md | n8n + ChatGPT | Sprint 1 |
| INT-011 | Register all APIs in Integration Registry | Claude Code | Sprint 1 |
| INT-012 | Create CHANGELOG.md with all historical work | Claude Code | Sprint 1 |
| INT-013 | Enable branch protection on main | @buck-HCI-AI | Sprint 1 |

### Governance Layer Status Update

| Document | Status | Sprint |
|---|---|---|
| PROGRAM_REPOSITORY_STATUS.md | ✅ Complete | Sprint 0 |
| PROGRAM_REPOSITORY_INVENTORY.md | ✅ Complete | Sprint 0 |
| REPOSITORY_RELATIONSHIP_MAP.md | ✅ Complete | Sprint 0 |
| IMPLEMENTATION_INTEGRATION_PLAN.md | ✅ Complete — Awaiting Review | Sprint 0 |
| LIVE_PROJECT_STATE_TEMPLATE.md | ✅ Complete — Template Ready | Sprint 0 |
| LIVE_PROJECT_STATE.md | ⏳ ChatGPT activates in Sprint 1 | Sprint 1 |

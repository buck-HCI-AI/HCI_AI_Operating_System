# TASKS.md
## HCI AI Operating System — Active Task Register
**Organization:** Hendrickson Construction, Inc.  
**Owner:** @buck-HCI-AI  
**Last Updated:** 2026-06-26  
**Authority:** SPRINT_OPERATING_MODEL.md  
**Parent Document:** PROJECT.md

---

## Status Legend
- `[ ]` Todo
- `[~]` In Progress
- `[x]` Done
- `[!]` Blocked

---

## Active Sprint: Sprint 0 — Repository Audit

### Governance Layer (✅ Complete)

| Status | Task ID | Task | Assigned To | Sprint |
|---|---|---|---|---|
| [x] | GOV-001 | GitHub Project created: HCI AI Development | Browser Claude | Sprint 0 |
| [x] | GOV-002 | Milestones created: Sprint 0–10 | Browser Claude | Sprint 0 |
| [x] | GOV-003 | 13 labels created | Browser Claude | Sprint 0 |
| [x] | GOV-004 | 5 issue templates created | Browser Claude | Sprint 0 |
| [x] | GOV-005 | CODEOWNERS created | Browser Claude | Sprint 0 |
| [x] | GOV-006 | CONTRIBUTING.md created | Browser Claude | Sprint 0 |
| [x] | GOV-007 | PULL_REQUEST_TEMPLATE.md created | Browser Claude | Sprint 0 |
| [x] | GOV-008 | HCI_AI_CONSTITUTION.md authored | Browser Claude | Sprint 0 |
| [x] | GOV-009 | AI_TEAM_CHARTER.md authored | Browser Claude | Sprint 0 |
| [x] | GOV-010 | AUTOMATION_GOVERNANCE.md authored | Browser Claude | Sprint 0 |
| [x] | GOV-011 | APPROVAL_GATES.md authored | Browser Claude | Sprint 0 |
| [x] | GOV-012 | SPRINT_OPERATING_MODEL.md authored | Browser Claude | Sprint 0 |
| [x] | GOV-013 | AI_WORKFLOW_ROLES.md authored | Browser Claude | Sprint 0 |
| [x] | GOV-014 | PROJECT.md created | Browser Claude | Sprint 0 |
| [x] | GOV-015 | GOVERNANCE_COMPLETION_REPORT.md created | Browser Claude | Sprint 0 |

### Houzz Browser Intelligence Workstream (✅ Design Complete)

| Status | Task ID | Task | Assigned To | Sprint |
|---|---|---|---|---|
| [x] | HZ-DESIGN-001 | HOUZZ_READ_ONLY_AUDIT.md created | Browser Claude | Sprint 0 |
| [x] | HZ-DESIGN-002 | HOUZZ_DAILY_LOG_WORKFLOW.md created | Browser Claude | Sprint 0 |
| [x] | HZ-DESIGN-003 | HOUZZ_BROWSER_AGENT_STRATEGY.md created | Browser Claude | Sprint 0 |
| [x] | HZ-DESIGN-004 | HOUZZ_APPROVAL_GATES.md created | Browser Claude | Sprint 0 |
| [x] | HZ-DESIGN-005 | HOUZZ_AUTOMATION_BACKLOG.md created | Browser Claude | Sprint 0 |
| [x] | HZ-DESIGN-006 | HOUZZ_BROWSER_AGENT_COMPLETION_REPORT.md created | Browser Claude | Sprint 0 |
| [x] | HZ-DESIGN-007 | TASKS.md created with all Houzz backlog items | Browser Claude | Sprint 0 |
| [x] | HZ-DESIGN-008 | PROJECT.md updated with Houzz workstream | Browser Claude | Sprint 0 |

---

## Backlog: Sprint 1 — System Verification

### Core Automation Setup

| Status | Task ID | Task | Label | Assigned To |
|---|---|---|---|---|
| [ ] | AUTO-001 | Set up n8n daily repository status report workflow | `n8n` `workflow` | n8n |
| [ ] | AUTO-002 | Set up n8n workflow health check (daily 06:00) | `n8n` `workflow` | n8n |
| [ ] | AUTO-003 | Set up n8n self-status report workflow (daily 08:00) | `n8n` `workflow` | n8n |
| [ ] | AUTO-004 | Create reports/ directory structure in repository | `workflow` | Claude Code |
| [ ] | AUTO-005 | Implement Gate H: HubSpot write approval workflow in n8n | `n8n` `hubspot` | n8n |
| [ ] | AUTO-006 | Implement Gate G: PR merge notification to human owner | `workflow` | n8n |
| [ ] | AUTO-007 | Create CURRENT_SPRINT.md for Sprint 1 | `documentation` | ChatGPT |
| [ ] | AUTO-008 | Create initial CHANGELOG.md | `documentation` | Claude Code |

### Houzz Workstream — Sprint 1

| Status | Task ID | Task | Label | Assigned To |
|---|---|---|---|---|
| [ ] | HZ-001 | Houzz Daily Log Reader (Manual extraction test) | `workflow` `n8n` | Browser Claude |
| [ ] | HZ-002 | Create reports/houzz/ folder structure | `workflow` `documentation` | Claude Code |
| [ ] | HZ-003 | Register Houzz in Integration Registry (05_Database/) | `registry` `workflow` | Claude Code |

**Acceptance Criteria — HZ-001:**
- [ ] Browser Claude reads one complete Houzz daily log (all 10 data categories)
- [ ] Output saved to `reports/houzz/daily/YYYY-MM-DD-[project]-log-extraction.md`
- [ ] Extraction log saved
- [ ] Zero write actions taken in Houzz
- [ ] Passes HOUZZ_READ_ONLY_AUDIT.md compliance checklist

---

## Backlog: Sprint 2 — Registry Consolidation

### Core

| Status | Task ID | Task | Label | Assigned To |
|---|---|---|---|---|
| [ ] | AUTO-010 | Set up weekly sprint review summary workflow | `n8n` `workflow` | n8n |
| [ ] | AUTO-011 | Set up weekly registry duplicate check | `n8n` `registry` | n8n |
| [ ] | AUTO-012 | Set up weekly broken link check | `n8n` `workflow` | n8n |
| [ ] | AUTO-013 | Set up HubSpot/Drive reconciliation report | `n8n` `hubspot` `drive` | n8n |
| [ ] | AUTO-014 | Connect HubSpot API to n8n | `hubspot` `registry` | n8n |
| [ ] | AUTO-015 | Connect Google Drive API to n8n | `drive` `registry` | n8n |
| [ ] | AUTO-016 | Build Integration Registry schema in 05_Database/ | `registry` | Claude Code |
| [ ] | AUTO-017 | Implement Gate E: client comms approval workflow | `n8n` `workflow` | n8n |
| [ ] | AUTO-018 | Implement Gate F: financial action approval workflow | `n8n` `workflow` | n8n |

### Houzz Workstream — Sprint 2

| Status | Task ID | Task | Label | Assigned To |
|---|---|---|---|---|
| [ ] | HZ-004 | n8n daily log extraction trigger (5:30 PM, all active projects) | `n8n` `workflow` | n8n |
| [ ] | HZ-005 | Houzz-to-HCI-AI Project Health Engine (7 intelligence artifacts) | `workflow` `registry` | ChatGPT + n8n |

---

## Backlog: Sprint 3 — HubSpot & Drive Integration

### Houzz Workstream — Sprint 3

| Status | Task ID | Task | Label | Assigned To |
|---|---|---|---|---|
| [ ] | HZ-006 | HubSpot Project Status Write — Gate HZ-H1 implementation | `hubspot` `workflow` | n8n |
| [ ] | HZ-007 | Drive Daily Intelligence Filing (auto, AI folder) | `drive` `workflow` | n8n |

---

## Backlog: Sprint 4 — Workflow Certification

### Houzz Workstream — Sprint 4

| Status | Task ID | Task | Label | Assigned To |
|---|---|---|---|---|
| [ ] | HZ-008 | Daily Executive Brief from Houzz (portfolio view, 1-pager) | `workflow` `n8n` | ChatGPT + n8n |
| [ ] | HZ-009 | PM Action Item Extractor (cross-project ranked list) | `workflow` | ChatGPT + n8n |

---

## Backlog: Sprint 5 — MCP Implementation

### Houzz Workstream — Sprint 5

| Status | Task ID | Task | Label | Assigned To |
|---|---|---|---|---|
| [ ] | HZ-010 | Houzz Schedule Reader (activity list, variance analysis) | `workflow` `mcp` | Browser Claude |
| [ ] | HZ-011 | Houzz Photo Intelligence Extractor (metadata + vision AI) | `workflow` `mcp` | Browser Claude + ChatGPT |

---

## Backlog: Sprint 8 — Production Validation

### Houzz Workstream — Sprint 8

| Status | Task ID | Task | Label | Assigned To |
|---|---|---|---|---|
| [ ] | HZ-012 | Superintendent Daily Log Draft Assistant | `workflow` `n8n` | ChatGPT + n8n |

---

## Backlog: Sprint 9 — Go Live

### Houzz Workstream — Sprint 9

| Status | Task ID | Task | Label | Assigned To |
|---|---|---|---|---|
| [ ] | HZ-013 | Full Houzz Intelligence Pipeline — Production (end-to-end) | `production` `workflow` | n8n + all agents |

---

## Backlog: Sprint 3–4 (Core)

| Status | Task ID | Task | Label | Assigned To |
|---|---|---|---|---|
| [ ] | AUTO-019 | Build HubSpot contact sync workflow | `hubspot` `n8n` | n8n |
| [ ] | AUTO-020 | Build Drive file indexing workflow | `drive` `n8n` | n8n |
| [ ] | AUTO-021 | Set up production readiness scorecard automation | `workflow` `testing` | ChatGPT / n8n |
| [ ] | AUTO-022 | Configure branch protection rules on main | `workflow` | Human Owner |
| [ ] | AUTO-023 | Implement MCP connectors | `mcp` | Claude Code |
| [ ] | AUTO-024 | Set up n8n workflow status dashboard | `n8n` `workflow` | n8n |
| [ ] | AUTO-025 | Gate audit log file structure setup | `workflow` `documentation` | Claude Code |

---

## Task Count Summary

| Category | Total | Done | In Progress | Todo | Blocked |
|---|---|---|---|---|---|
| Governance (GOV) | 15 | 15 | 0 | 0 | 0 |
| Houzz Design | 8 | 8 | 0 | 0 | 0 |
| Core Automation (AUTO) | 25 | 0 | 0 | 25 | 0 |
| Houzz Implementation (HZ) | 13 | 0 | 0 | 13 | 0 |
| **Total** | **61** | **23** | **0** | **38** | **0** |

---

*Governed by SPRINT_OPERATING_MODEL.md | Owner: @buck-HCI-AI | Hendrickson Construction, Inc.*  
*TASKS.md is archived at sprint close to `reports/sprint/sprint-N-tasks.md`*

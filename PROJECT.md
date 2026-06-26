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

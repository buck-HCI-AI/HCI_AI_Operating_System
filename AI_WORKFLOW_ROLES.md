# AI Workflow Roles
## HCI AI Operating System — Hendrickson Construction, Inc.
**Version:** 1.0 | **Effective:** 2026-06-26 | **Authority:** AI_TEAM_CHARTER.md

---

## Purpose

This document maps every AI agent to their specific workflow responsibilities across all sprint phases, recurring automations, and integration touchpoints. It is the operational companion to AI_TEAM_CHARTER.md.

---

## Role-to-Workflow Matrix

| Workflow / Task | ChatGPT | Claude Code | Browser Claude | Codex | n8n | Human |
|---|---|---|---|---|---|---|
| Define sprint scope | Author | — | — | — | — | Approve |
| Create CURRENT_SPRINT.md | Author | — | — | — | — | Approve |
| Create TASKS.md | Author | — | — | — | — | Review |
| Create GitHub issues | — | Create | Browser Claude creates | — | — | — |
| Assign milestones/labels | — | — | Execute | — | — | — |
| Implement features | — | Execute | — | — | — | — |
| Commit to feature branch | — | Execute | Execute (governance) | — | — | — |
| Automated code review | — | — | — | Execute | — | — |
| Run test suite | — | — | — | Execute | Trigger | — |
| Update CHANGELOG.md | Draft | Execute commit | — | — | — | Review |
| Merge PR to main | — | — | — | — | — | **Execute (Gate G)** |
| Close sprint milestone | — | — | Execute | — | — | — |
| Archive sprint docs | Author | Execute commit | — | — | — | — |
| Update PROJECT.md | Author | Execute commit | — | — | — | Review |
| Daily repo status | Draft | — | Execute (manual) | — | **Execute (auto)** | Receive |
| Weekly sprint review | Author | — | — | — | Trigger | **Approve** |
| Workflow health check | — | — | — | — | **Execute** | Receive |
| Registry duplicate check | — | — | — | Validate | **Execute** | Review |
| Broken link check | — | — | — | Validate | **Execute** | Receive |
| HubSpot/Drive reconciliation | Draft report | — | — | — | **Execute** | **Approve writes** |
| n8n workflow status | — | — | — | — | **Execute (self)** | Receive |
| Production readiness scorecard | **Author** | — | — | Validate tests | — | **Approve** |
| CRM reads | Execute | — | — | — | Execute | — |
| CRM writes (production) | Draft | — | — | — | Route | **Gate H** |
| External client comms | Draft | — | — | — | Route | **Gate E** |
| Financial actions | Draft | — | — | — | Route | **Gate F** |
| Production deployment | Recommend | — | — | Validate | Route | **Gate P** |

---

## Per-Agent Workflow Detail

### ChatGPT — Chief Architect / QA / Product Manager

**Sprint Planning Workflows:**
1. Review backlog in PROJECT.md
2. Draft sprint scope with human owner
3. Publish CURRENT_SPRINT.md
4. Create TASKS.md with detailed acceptance criteria
5. Define test criteria for each task

**Quality Assurance Workflows:**
1. Review implementations against acceptance criteria
2. Author Production Readiness Scorecard per sprint close
3. Review and approve test results from Codex
4. Flag architectural drift or scope creep

**Recurring:**
- Weekly: Generate Sprint Review Summary → n8n publishes
- Per sprint: Scorecard → Human approval → Sprint close

---

### Claude Code — Lead Implementation Engineer

**Implementation Workflows:**
1. Read TASKS.md for current sprint tasks
2. Create feature branch: `sprint-N/type/description`
3. Implement per acceptance criteria
4. Write or update relevant documentation
5. Draft CHANGELOG.md entry
6. Open PR referencing GitHub issue
7. Respond to Codex review comments
8. Update TASKS.md status after merge

**Governance File Workflows:**
1. Create governance, template, and configuration files on instruction
2. Commit to `main` only via PR and human merge (Gate G)
3. No modification of application source code without approved issue

---

### Browser Claude — GitHub Administrator

**Repository Configuration Workflows:**
1. Create and update GitHub labels, milestones, projects
2. Assign issues to milestones and projects
3. Create governance and template files via web interface
4. Configure branch protection rules (advisory + execution on instruction)
5. Generate repository audit reports

**Monitoring Workflows:**
1. Manual trigger: Daily Repository Status Report
2. Monitor open issues for label compliance
3. Audit sprint board for unassigned or unmilestoned issues

---

### Codex — Review / Test Engineer

**Code Review Workflows:**
1. Triggered automatically on every PR open or update
2. Read all changed files in PR
3. Check against acceptance criteria from TASKS.md
4. Run automated test suite
5. Post structured review comment:
   - Summary of changes
   - Test results (pass/fail count)
   - Issues found (blocking / non-blocking)
   - Recommendation: Approve / Request Changes
6. Re-review on each new commit pushed to PR

**Validation Workflows:**
1. Validate governance files for completeness and cross-references
2. Run registry duplicate detection queries
3. Validate broken links in documentation
4. Run pre-deployment validation checklist (feeds Gate P)

---

### n8n — Automation Orchestrator

**Daily Automated Workflows (run at scheduled times):**

| Time | Workflow | Output |
|---|---|---|
| 06:00 | Workflow Health Check | `reports/daily/YYYY-MM-DD-workflow-health.md` |
| 07:00 | Repository Status Report | `reports/daily/YYYY-MM-DD-repo-status.md` |
| 08:00 | n8n Self Status Report | `reports/daily/YYYY-MM-DD-n8n-status.md` |

**Weekly Automated Workflows:**

| Day | Workflow | Output |
|---|---|---|
| Monday 09:00 | Sprint Review Summary (triggered) | `reports/weekly/YYYY-WNN-sprint-review.md` |
| Tuesday 07:00 | Registry Duplicate Check | `reports/weekly/YYYY-WNN-registry-duplicates.md` |
| Wednesday 07:00 | Broken Link Check | `reports/weekly/YYYY-WNN-broken-links.md` |
| Thursday 07:00 | HubSpot/Drive Reconciliation | `reports/weekly/YYYY-WNN-hubspot-drive-reconciliation.md` |

**Event-Driven Workflows:**
- On Gate timeout: Create GitHub issue + alert human owner
- On workflow failure: Halt, log, create issue labeled `blocked`, alert
- On sprint close trigger: Initiate production readiness check sequence
- On new PR: Trigger Codex review sequence

**Integration Connectors:**
- GitHub API (read/write issues, commits, labels)
- HubSpot API (read all; write staging; route production writes to Gate H)
- Google Drive API (read/index; write to AI folders)
- Internal Registry (read/write)
- Notification channel (Slack / email / GitHub issues)

---

## Handoff Protocol

When one agent hands off work to another:
1. Update the GitHub issue with a comment: `@[next-agent]: Ready for [action]. Context: [brief summary]`
2. Apply appropriate label change (e.g., `in-review`, `blocked`, `testing`)
3. Move issue to correct sprint board column
4. If handoff requires human approval, create approval request via Gate process

---

## Conflict Resolution

If two agents have conflicting instructions:
1. The agent with lower authority yields to the higher authority agent
2. Authority order: Human > HCI_AI_CONSTITUTION.md > AI_TEAM_CHARTER.md > this document
3. Unresolvable conflicts are escalated to human owner via GitHub issue

---

*Governed by HCI_AI_CONSTITUTION.md | Hendrickson Construction, Inc.*

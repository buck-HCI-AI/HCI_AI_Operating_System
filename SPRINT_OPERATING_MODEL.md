# Sprint Operating Model
## HCI AI Operating System — Hendrickson Construction, Inc.
**Version:** 1.0 | **Effective:** 2026-06-26 | **Authority:** HCI_AI_CONSTITUTION.md Article IV

---

## Purpose

This document defines the mandatory operating model for all sprints in the HCI AI Operating System. Every sprint follows this model without exception. Deviations require human owner approval and must be documented.

---

## The Sprint Document Chain

Every sprint follows this exact sequence. No step may be skipped.

```
PROJECT.md
    ↓
TASKS.md
    ↓
CURRENT_SPRINT.md
    ↓
Implementation (feature branch)
    ↓
Tests (automated + manual validation)
    ↓
Code Review (Codex + human)
    ↓
CHANGELOG.md update
    ↓
Commit to main (Gate G — human approval)
    ↓
Sprint Close & Retrospective
```

---

## Document Definitions

### PROJECT.md
**Owner:** ChatGPT  
**Purpose:** Master project vision, goals, and backlog  
**Contents:**
- Project mission and success criteria
- Full backlog of all planned work items
- Sprint history (completed sprints with outcomes)
- Governance layer status
- Integration registry summary
- Known risks and mitigations

**Rules:**
- Updated at the start of each sprint with new backlog items
- Never deleted — append only for history sections
- All AI agents may read; only ChatGPT and human owner may write

---

### TASKS.md
**Owner:** ChatGPT  
**Purpose:** Active sprint task list with acceptance criteria  
**Contents:**
- All tasks for the current sprint (from CURRENT_SPRINT.md)
- Detailed acceptance criteria for each task
- Assigned AI agent per task
- Dependencies between tasks
- Status: [ ] Todo / [~] In Progress / [x] Done / [!] Blocked

**Rules:**
- Created at sprint start from CURRENT_SPRINT.md
- Updated continuously as tasks are completed
- Archived at sprint close to `reports/sprint/sprint-N-tasks.md`

---

### CURRENT_SPRINT.md
**Owner:** ChatGPT / Human Owner  
**Purpose:** Active sprint definition and tracking dashboard  
**Contents:**
- Sprint number and name
- Sprint dates (start, planned end)
- Sprint goal statement
- Issue list (linked to GitHub issues)
- Velocity target (issues planned vs. completed)
- Blocker log
- Human approvals pending

**Rules:**
- One and only one CURRENT_SPRINT.md active at any time
- Updated daily by automated status report
- Replaced (not deleted) at each sprint close

---

### Implementation (Feature Branch)
**Owner:** Claude Code  
**Branch naming:** `sprint-N/type/short-description`  
**Rules:**
- All implementation work happens on feature branches
- No direct commits to `main` by AI agents
- Each commit references a GitHub issue number
- Commits are small, focused, and descriptive

---

### Tests
**Owner:** Codex  
**Rules:**
- Every implementation task requires corresponding test validation
- Tests run automatically via CI/CD on every PR
- Test results summarized in PR comment
- No merge if tests fail (Gate G pre-condition)
- For governance/documentation-only PRs: manual checklist validation replaces automated tests

---

### Code Review
**Owner:** Codex (automated) + Human Owner (final)  
**Rules:**
- Codex reviews all PRs and posts findings within 2 hours
- Human owner reviews Codex summary and any flagged items
- Minimum 1 human approval required before merge
- All review comments must be resolved

---

### CHANGELOG.md
**Owner:** Claude Code (automated draft) + Human Owner (approval)  
**Format:** Keep a Changelog (https://keepachangelog.com)  
**Rules:**
- Updated with every PR before merge
- Sections: Added, Changed, Fixed, Removed, Security
- Each entry links to the corresponding GitHub issue/PR
- CHANGELOG.md lives in repo root

---

## Sprint Lifecycle

### Phase 1 — Sprint Planning (Day 1)
| Step | Action | Owner |
|---|---|---|
| 1.1 | Human owner reviews and approves sprint scope | Human |
| 1.2 | ChatGPT publishes CURRENT_SPRINT.md | ChatGPT |
| 1.3 | ChatGPT creates TASKS.md with acceptance criteria | ChatGPT |
| 1.4 | Claude Code creates GitHub issues for all tasks | Claude Code |
| 1.5 | Browser Claude assigns issues to milestone | Browser Claude |
| 1.6 | n8n activates daily status reporting for sprint | n8n |

### Phase 2 — Active Sprint (Daily)
| Step | Action | Owner |
|---|---|---|
| 2.1 | n8n publishes daily repo status report (07:00) | n8n |
| 2.2 | Claude Code implements tasks from TASKS.md | Claude Code |
| 2.3 | Claude Code commits to feature branch with issue ref | Claude Code |
| 2.4 | Codex reviews PR and posts findings | Codex |
| 2.5 | Claude Code resolves review comments | Claude Code |
| 2.6 | Human owner approves and merges PR (Gate G) | Human |
| 2.7 | Claude Code updates TASKS.md status | Claude Code |
| 2.8 | Blocked items escalated via GitHub issue + n8n alert | Any agent |

### Phase 3 — Sprint Close
| Step | Action | Owner |
|---|---|---|
| 3.1 | ChatGPT generates Production Readiness Scorecard | ChatGPT |
| 3.2 | Codex runs final test suite | Codex |
| 3.3 | Claude Code updates CHANGELOG.md | Claude Code |
| 3.4 | ChatGPT writes Sprint Review Summary | ChatGPT |
| 3.5 | Human owner reviews and approves sprint close | Human |
| 3.6 | Browser Claude closes milestone in GitHub | Browser Claude |
| 3.7 | ChatGPT archives sprint docs to `reports/sprint/` | ChatGPT |
| 3.8 | ChatGPT updates PROJECT.md backlog | ChatGPT |
| 3.9 | CURRENT_SPRINT.md replaced with next sprint | ChatGPT |

---

## Sprint Rules

**Rule 1 — No Orphan Work**
Every task must have a GitHub issue. Every issue must be assigned to a milestone. Work without a traceable issue is not authorized.

**Rule 2 — No Scope Creep**
New work identified during a sprint goes to the backlog in PROJECT.md. It is not added to the active sprint without human approval.

**Rule 3 — Blockers Surface Immediately**
Any blocker is escalated the same day it is identified. A blocker is never silently carried.

**Rule 4 — Tests Before Merge**
No PR merges to `main` without passing tests (or explicit human override logged in the gate record).

**Rule 5 — Changelog is Non-Negotiable**
CHANGELOG.md is updated with every sprint. There are no exceptions.

**Rule 6 — Sprint Retrospective**
Every sprint close includes a brief retrospective: what worked, what didn't, what changes for next sprint. Archived with sprint docs.

---

## Sprint Calendar

| Sprint | Name | Status |
|---|---|---|
| Sprint 0 | Repository Audit | Active |
| Sprint 1 | System Verification | Planned |
| Sprint 2 | Registry Consolidation | Planned |
| Sprint 3 | HubSpot & Drive Integration | Planned |
| Sprint 4 | Workflow Certification | Planned |
| Sprint 5 | MCP Implementation | Planned |
| Sprint 6 | Historical Project Mining | Planned |
| Sprint 7 | Executive Dashboards | Planned |
| Sprint 8 | Production Validation | Planned |
| Sprint 9 | Go Live | Planned |
| Sprint 10 | Continuous Improvement | Ongoing |

---

*Governed by HCI_AI_CONSTITUTION.md | Hendrickson Construction, Inc.*

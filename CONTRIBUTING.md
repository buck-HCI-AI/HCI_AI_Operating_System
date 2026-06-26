# Contributing to HCI AI Operating System

**Hendrickson Construction, Inc.**
Build started: 2026-06-24 | Constitution v1

This document defines how team members and contributors work within this repository. All contributions must follow the sprint-based workflow defined below.

---

## Governance Principles

- Do not modify application source code without a corresponding issue and approved PR.
- Do not delete existing files or branches without explicit approval.
- All changes must be traceable to a milestone (Sprint 0–10).
- Prefer small, focused PRs over large, sweeping changes.

---

## Sprint Workflow

1. **Create an Issue** using the appropriate issue template (Feature, Bug, Documentation, Architecture, or Workflow).
2. **Assign the Issue** to the correct Sprint milestone (Sprint 0–10).
3. **Apply Labels** from the approved label set.
4. **Create a Branch** from `main` using the naming convention:
   ```
   sprint-<N>/<type>/<short-description>
   Example: sprint-3/feature/hubspot-contact-sync
   ```
5. **Open a Pull Request** using the PR template. Link it to the issue.
6. **Request Review** — CODEOWNERS will be automatically assigned.
7. **Merge** only after review approval and all checklist items are complete.

---

## Branch Naming Convention

| Type | Prefix | Example |
|---|---|---|
| Feature | `feature/` | `sprint-2/feature/registry-schema` |
| Bug fix | `fix/` | `sprint-1/fix/startup-crash` |
| Documentation | `docs/` | `sprint-0/docs/readme-update` |
| Architecture | `arch/` | `sprint-5/arch/mcp-design` |
| Workflow | `workflow/` | `sprint-3/workflow/hubspot-sync` |

---

## Labels

Apply one or more of the following labels to every issue and PR:

`architecture` `documentation` `workflow` `registry` `hubspot` `drive` `mcp` `n8n` `testing` `enhancement` `bug` `blocked` `production`

---

## Milestones

All issues and PRs must be assigned to a milestone:

| Milestone | Purpose |
|---|---|
| Sprint 0 | Repository Audit |
| Sprint 1 | System Verification |
| Sprint 2 | Registry Consolidation |
| Sprint 3 | HubSpot & Drive Integration |
| Sprint 4 | Workflow Certification |
| Sprint 5 | MCP Implementation |
| Sprint 6 | Historical Project Mining |
| Sprint 7 | Executive Dashboards |
| Sprint 8 | Production Validation |
| Sprint 9 | Go Live |
| Sprint 10 | Continuous Improvement |

---

## Code Review Standards

- All PRs require at least **1 approving review** before merge.
- Do not merge your own PR without review.
- Resolve all comments before merging.
- Use the PR checklist to confirm all requirements are met.

---

## Questions?

Open an issue using the Documentation template or contact the repository owner @buck-HCI-AI.

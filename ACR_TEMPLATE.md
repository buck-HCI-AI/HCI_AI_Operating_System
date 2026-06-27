# Architecture Change Request (ACR) Template
## HCI AI Operating System

**Authority:** Chief Architect (ChatGPT) | Governed by HCI_AI_CONSTITUTION.md

---

## How to Use

Copy this template, fill in the fields, and save as `ACR-NNN-TITLE.md` in the repo root.  
Submit to ChatGPT for review. Claude Code implements after ACR is approved.

---

```markdown
# ACR-NNN: [Short Title]
**Date:** YYYY-MM-DD  
**Submitted by:** [Claude Code / Browser Claude / Buck Adams]  
**Reviewed by:** ChatGPT (Chief Architect)  
**Status:** DRAFT | UNDER REVIEW | APPROVED | REJECTED | SUPERSEDED

---

## Summary

One paragraph: what changes, why it's needed, what system it affects.

---

## Problem Statement

What is broken, missing, or suboptimal today?

---

## Proposed Solution

Describe the change. Include:
- New tables, APIs, or services
- Changes to existing components
- Integration points
- Backwards compatibility impact

---

## Affected Components

| Component | Change Type | Notes |
|---|---|---|
| PostgreSQL | Schema extension | New table: xyz |
| FastAPI | New endpoint | POST /api/v1/services/xyz |
| n8n | New workflow | Triggered by webhook |
| Mining Engine | New miner | XyzMiner added |

---

## Implementation Plan

Ordered steps Claude Code will execute:

1. Step 1
2. Step 2
3. Step 3

Estimated time: X hours

---

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Data loss | Low | Backup before migration |
| Service downtime | Low | Apply during off-hours |

---

## Validation Criteria

How do we know it worked?

- [ ] Endpoint returns 200
- [ ] Row count in DB matches expected
- [ ] n8n workflow shows active
- [ ] Mining run completes without errors

---

## Rollback Plan

How to undo if needed.

---

## Decision

**ChatGPT Decision:** APPROVED / REJECTED / DEFERRED  
**Decision Date:** YYYY-MM-DD  
**Conditions:** (if any)  
**Implemented by:** Claude Code  
**Implementation Date:** YYYY-MM-DD
```

---

*ACR Template | HCI AI Operating System | Hendrickson Construction, Inc.*

# EMAIL_ARCHITECTURE_REVIEW_2026-07-01.md
## HCI AI OS - Email Architecture Review
## BC Architectural Audit (What BC Can Confirm Without Code Access)

**Date:** 2026-07-01
**Performed By:** Browser Claude (Operations Intelligence)
**Method:** GitHub documentation review + BC_EMAIL_CAPABILITY.md analysis
**Scope:** What BC can confirm architecturally - NOT a code audit (requires Claude Code)

---

## CRITICAL FINDING: /gateway/email/send Is Open

**Source:** AI_TEAM/BC_EMAIL_CAPABILITY.md (committed 2026-06-30)

BC_EMAIL_CAPABILITY.md documents that BC is authorized to call /gateway/email/send DIRECTLY
for bid invitations and follow-ups WITHOUT requiring an approval queue check.

Exact language from the document:
"Bid invitations to subs - OK to send directly (this is routine ops)"
"Follow-ups and scheduling - OK to send directly"

**THIS CONTRADICTS THE EMAIL GOVERNANCE DIRECTIVE.**

The P0 email incident directive (prior session) states:
"NO AI system may send live email without explicit human approval - no exceptions"
"All emails: create draft -> Approval Queue item -> Buck reviews -> Buck approves -> send"

---

## Email Paths Identified from Documentation

### Path 1: /gateway/email/send (BC_EMAIL_CAPABILITY.md)
- Status: DOCUMENTED AS ACTIVE
- Governance gate: NONE for "routine" sends
- Risk: HIGH - BC can send externally without Buck approval
- Required fix: Must require approval_queue approved=True before any send

### Path 2: /gateway/email/draft (BC_EMAIL_CAPABILITY.md)
- Status: DOCUMENTED AS ACTIVE
- Governance gate: Creates draft only - APPROVED pattern
- Risk: LOW - draft requires Buck to manually send from Outlook

### Path 3: /gateway/email/draft/{id}/send (BC_EMAIL_CAPABILITY.md)
- Status: DOCUMENTED AS ACTIVE
- Governance gate: Requires prior draft creation + implied Buck review
- Risk: MEDIUM - BC could call this after creating a draft without Buck seeing it
- Required fix: Must verify approval_queue item approved=True before this endpoint

### Path 4: OutlookMiner (LIVE_PROJECT_STATE.md)
- Status: LIVE - 03:00 daily mining
- Governance gate: "emails queued for approval only - never auto-reply" (documented)
- Risk: LOW if documented behavior is implemented in code
- Verification needed: Claude Code must confirm no auto-reply in code

### Path 5: n8n Workflows (AUTOMATION_GOVERNANCE.md)
- Status: 55 active workflows
- Governance gate: "all workflows have approval gates" (documented)
- Risk: MEDIUM - BC cannot verify which n8n workflows touch email
- Verification needed: Claude Code must enumerate email-touching n8n workflows

### Path 6: MCP DraftEmail Tool (LIVE_PROJECT_STATE.md)
- Status: Active (43 MCP tools including DraftEmail)
- Governance gate: Draft only by name - APPROVED pattern
- Risk: LOW if DraftEmail truly only creates drafts
- Verification needed: Confirm no send capability in MCP tool

### Path 7: Direct Graph API (speculative)
- Status: Unknown - MS Graph API is active per LIVE_PROJECT_STATE.md
- Governance gate: Unknown
- Risk: HIGH if accessible without approval gate
- Verification needed: Claude Code must confirm no direct Graph API send outside gateway

---

## What BC CANNOT Confirm (Requires Claude Code)

| Item | Why BC Cannot Confirm |
|------|----------------------|
| Actual emails sent (sentItems query) | Requires Graph API query - BC has no API access |
| Whether approval gate is in /send endpoint code | Requires reading FastAPI source |
| n8n workflow email actions | Requires n8n API access |
| DraftEmail MCP source code | Requires file access |
| Graph API direct access controls | Requires code review |

---

## BC Recommendations (Immediate)

### 1. DISABLE /gateway/email/send for BC
BC_EMAIL_CAPABILITY.md says BC can send directly for "routine" ops.
This must be REVOKED immediately. All BC sends must go through approval queue.
BC will only use /gateway/email/draft going forward.
BC self-declaration: I will NOT call /gateway/email/send until further notice.

### 2. Update BC_EMAIL_CAPABILITY.md
The document must be updated to remove direct-send authorization.
New rule: BC creates drafts ONLY. Buck sends. No exceptions.

### 3. Claude Code Priority (when online)
Claude Code must:
a) Add approval_queue check to /gateway/email/send - return 403 if not approved
b) Query sentItems - confirm what was sent, when, to whom
c) Audit all n8n workflows for email actions
d) Confirm DraftEmail MCP creates draft only

---

## BC Self-Governance Declaration

Effective immediately and documented here:

Browser Claude will NOT use /gateway/email/send until Claude Code confirms
approval gate is enforced in code AND Buck explicitly re-authorizes direct sends.

BC will only use /gateway/email/draft for all email operations.
Every draft will be reported to Buck in the chat interface before any follow-up.

This declaration is committed to the repository as a governance record.

---

## Summary: Current Email Risk Posture

| Risk | Level | Status |
|------|-------|--------|
| /gateway/email/send open for BC routine sends | HIGH | DECLARED REVOKED by BC |
| Sent email audit not complete | HIGH | Queued for Claude Code |
| n8n email paths unverified | MEDIUM | Queued for Claude Code |
| OutlookMiner auto-reply | LOW | Documented as gated |
| MCP DraftEmail send capability | LOW | Documented as draft-only |

---

## Next Actions

| # | Action | Owner | Priority |
|---|--------|-------|---------|
| 1 | Update BC_EMAIL_CAPABILITY.md - remove direct send authorization | Browser Claude | IMMEDIATE |
| 2 | Claude Code: query sentItems, commit EMAIL_AUDIT_RESULTS.md | Claude Code | P0 |
| 3 | Claude Code: add approval gate to /gateway/email/send | Claude Code | P0 |
| 4 | Claude Code: audit all n8n email workflows | Claude Code | P0 |
| 5 | Buck: confirm email governance policy (Option A/B/C from GATE5_SIGNOFF_PENDING.md) | Buck | PENDING |

---

EMAIL_ARCHITECTURE_REVIEW_2026-07-01.md | HCI AI Operating System | Hendrickson Construction, Inc.
BC Architectural Audit | 2026-07-01 | Authority: HCI_AI_CONSTITUTION.md

# N8N_EMAIL_AUDIT_CHECKLIST.md
## HCI AI OS - n8n Email Path Governance Checklist
## Implementation-Ready Verification Guide for Claude Code

**Date:** 2026-07-01
**Prepared By:** Browser Claude (Operations Intelligence)
**Chief Architect Recommendation:** GBT Cycle 3 Response
**Purpose:** Provide Claude Code a repeatable checklist to verify every n8n workflow
  that touches email has proper governance gates.

---

## Why This Checklist Exists

LIVE_PROJECT_STATE.md states: "all workflows have approval gates".
But BC cannot verify this from documentation alone.
Claude Code must run this checklist and commit results as EMAIL_LOCKDOWN_CONFIRMED.md.

This is a Sprint 3 P0 item. No n8n workflow may send email without:
1. Check: Is there an item in the approval_queue with approved=True?
2. Check: Is the recipient buck@hendricksoninc.com or an explicitly approved address?
3. Check: Is there an audit log entry for this send?

---

## n8n Workflows to Audit

Based on LIVE_PROJECT_STATE.md (55 active workflows), the following categories
are most likely to touch email. Claude Code must verify EACH workflow:

### Category A: Known Email-Adjacent Workflows
| Workflow ID | Name | Email Risk | Verification Required |
|------------|------|-----------|----------------------|
| AUTO-001 | Daily Repository Status Report | LOW - internal | Does it email anyone? Who? |
| AUTO-002 | Workflow Health Check | LOW - internal | Does it email anyone? |
| AUTO-003 | Sprint Self-Status Report | LOW - internal | Does it email anyone? |
| GATE-E | Client comms approval workflow | HIGH - client facing | Confirm approval required |
| GATE-H | HubSpot write approval | MEDIUM | Does it send email notifications? |
| AUTO-PILOT-WEEKLY | Gate5 Digest Monday | MEDIUM | Who does it send to? |

### Category B: Workflows With Email Capability by Design
| Workflow ID | Name | Email Risk | Verification Required |
|------------|------|-----------|----------------------|
| GATE-F | Financial action approval | HIGH | Any email triggers? |
| GATE-G | PR merge notification | MEDIUM | Who gets notified? |
| WF-001 to WF-007 | Core construction workflows | UNKNOWN | Must enumerate |
| AUTO-010 | Weekly sprint review summary | LOW | Internal or external? |
| AUTO-011 | Weekly registry duplicate check | LOW | Does it alert anyone via email? |
| AUTO-013 | HubSpot/Drive reconciliation | MEDIUM | Email alerts? |

---

## Verification Questions for Each Workflow

For EVERY n8n workflow (55 active), Claude Code must answer:

1. Does this workflow have an Email or Send Email node?
   - If YES: document the node, recipient address, and trigger condition
   - If NO: note "No email capability"

2. If the workflow sends email, is there an approval gate before send?
   - Required gate: Check approval_queue where approved=True and item_type=email
   - If NO gate exists: BLOCK - add gate before deploying

3. What is the recipient address?
   - ALLOWED: buck@hendricksoninc.com, buck@ahmaspen.com
   - REQUIRES EXPLICIT BUCK APPROVAL: Any other address
   - NEVER ALLOWED: Automatic sends to external recipients without approval

4. Is there an audit log entry when this workflow sends email?
   - Required: Date, recipient, subject, triggered_by, approved_by
   - If no log: BLOCK - add logging

5. Is there a regression test for this behavior?
   - Desired: At least one test confirming no send without approved=True

---

## Acceptance Criteria for EMAIL_LOCKDOWN_CONFIRMED.md

Claude Code must commit EMAIL_LOCKDOWN_CONFIRMED.md that contains:

### Section 1: Workflow Inventory
Complete list of all 55 n8n workflows with:
- Email capability: YES/NO
- If YES: recipient, gate status, log status

### Section 2: Email-Capable Workflows (Full Detail)
For each workflow that sends email:
- Workflow ID and name
- Node type (Send Email, HTTP Request to Graph API, etc.)
- Recipient address(es)
- Approval gate: EXISTS/MISSING
- Audit log: EXISTS/MISSING
- Status: COMPLIANT / REMEDIATED / BLOCKED

### Section 3: sentItems Audit
From Microsoft Graph API GET /me/mailFolders/sentItems/messages:
- Total emails sent by system
- For each email: date, to, subject, triggered_by workflow
- Confirmation: All sent emails had approval_queue approved=True

### Section 4: Certification
Signed by Claude Code:
"I have audited all n8n email paths. All email sends require approved=True
in the approval queue. No unauthorized email sends detected."

---

## BC Self-Verification Steps (What BC Can Do)

BC cannot read n8n workflow internals. But BC CAN:

1. Read AUTOMATION_GOVERNANCE.md for workflow list
2. Check if any workflows reference /gateway/email/send in documentation
3. Read GATE-E workflow JSON if committed to repo
4. Verify approval_queue schema includes email_approved field

**BC Next Action:** Read AUTOMATION_GOVERNANCE.md and flag any email references.

---

## Priority Queue for Claude Code

When Code returns, in order:

| # | Task | Output File | Time Estimate |
|---|------|------------|---------------|
| 1 | Query Graph sentItems | EMAIL_AUDIT_RESULTS.md | 30 min |
| 2 | Run this n8n checklist | EMAIL_LOCKDOWN_CONFIRMED.md | 2 hours |
| 3 | Fix 101F variance bug | Code fix + test | 1 hour |
| 4 | Fix 1355R test data | Code fix | 30 min |
| 5 | Update LIVE_PROJECT_STATE.md Sprint 3 | File update | 15 min |
| 6 | Build Telegram inbound | New workflow + test | 3 hours |

Total: ~7 hours of work queued.

---

## Version History
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-01 | Browser Claude | Initial checklist created |

---

N8N_EMAIL_AUDIT_CHECKLIST.md | HCI AI Operating System | Hendrickson Construction, Inc.
Prepared by: Browser Claude (Operations Intelligence) | 2026-07-01
Chief Architect recommendation: GBT Cycle 3 | Authority: HCI_AI_CONSTITUTION.md

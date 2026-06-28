---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: Phase 2 — Actionable Mobile Approvals with ntfy
created_at: 2026-06-28
summary: Handoff from ChatGPT via GBT Gateway
---

Queue this behind the current Gate 5 audit work. Claude Code is busy; this is a high-priority backlog handoff, not an immediate production change unless Buck later authorizes go-live.

Objective:
Design and implement Phase 2 of the HCI Mobile Command Center: secure actionable mobile approvals triggered from ntfy notifications while preserving the existing human-in-the-loop governance model.

Required capabilities:
1. Add secure one-time approval tokens for mobile approval actions.
2. Support Approve / Reject / Request Info actions from mobile deep links.
3. Require explicit human confirmation before any approval action is committed.
4. Add optional biometric confirmation support where the mobile client/browser supports passkeys, Face ID, Touch ID, or platform authenticator flows.
5. Ensure mobile actions route through the existing approval queue service and do not bypass governance.
6. Enforce token expiration, single-use semantics, project/item scoping, and audit logging.
7. Store decision metadata: approver, timestamp, item id, project code, action, device/user agent if available, IP if appropriate, and previous/new approval status.
8. Add escalation behavior for unattended high-priority approvals after configurable SLA windows.
9. Add environment configuration for ntfy topics, token TTL, notification priority mapping, quiet hours, and escalation recipients.
10. Add tests for token generation, token expiration, replay prevention, unauthorized access, approval queue state transitions, and audit log creation.
11. Document deployment steps, rollback procedure, security model, and known limitations.

Security constraints:
- No notification may auto-approve or perform production writes on receipt.
- Mobile approval links must never contain long-lived credentials.
- Approval tokens must be scoped to a single approval item and single action session.
- All write actions remain subject to Buck/HCI authorized-user confirmation.
- Default implementation may ship in dry-run or staging mode until Buck explicitly says go live.

Deliverables:
- Backend implementation plan and code changes.
- n8n workflow update plan for ntfy actionable notification links.
- Approval queue API changes, if required.
- Audit table or audit log updates.
- Test coverage and verification checklist.
- Recommendation on whether this belongs inside Architecture Freeze v1.0 or should be marked as post-freeze controlled enhancement.

Priority: HIGH, queued after HANDOFF 1 OF 2 WF-009 Data Integrity Audit and HANDOFF 2 OF 2 Pilot Reporting Consistency Audit.

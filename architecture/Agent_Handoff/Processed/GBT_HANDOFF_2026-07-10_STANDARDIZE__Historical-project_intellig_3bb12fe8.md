---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: STANDARDIZE: Historical-project intelligence as mandatory quality gate across HCI workflows
created_at: 2026-07-10
summary: Handoff from ChatGPT via GBT Gateway
---

Buck confirms this was the original intent of HCI AI: do not build workflows from scratch when HCI already has mature project data. Make historical/monitored-project intelligence a permanent standard across the board.

Apply this to at least:
- RFIs
- Change Orders
- Submittals
- Bid leveling
- SOWs
- Email templates
- Schedule risk reviews
- Procurement/long-lead reviews
- Vendor evaluations
- Meeting agendas/minutes
- Daily logs
- Closeout/lessons learned

Permanent rule:
Before a workflow output is marked ready, the system should compare it against relevant mature/historical HCI examples, recurring standards, and lessons learned, while keeping monitored/historical jobs read-only.

Required architecture:
1. Build a reusable Historical Practice Review layer that can retrieve comparable examples by project type, document type, division, vendor, issue type, and workflow stage.
2. Separate HCI-wide recurring standards from project-specific quirks.
3. Preserve provenance: every learned pattern should reference source projects/documents.
4. Add confidence and applicability scoring.
5. Never blindly copy prior content; use it as evidence and precedent.
6. Feed validated patterns into the Standards Registry and workflow quality gates.
7. Capture contradictions and exceptions for human review.
8. Make this available to all role GPTs according to permission scope.
9. Add regression tests proving outputs are checked against historical practice before being marked ready.

Acceptance standard:
The system should demonstrate that it is learning from HCI's existing body of work, not generating isolated one-off outputs from scratch.

Also keep onboarding work moving in parallel; do not let this block the Buck pilot onboarding flow.

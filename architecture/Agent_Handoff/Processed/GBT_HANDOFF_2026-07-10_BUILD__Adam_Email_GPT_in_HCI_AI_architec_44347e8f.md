---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: BUILD: Adam Email GPT in HCI AI architecture
created_at: 2026-07-10
summary: Handoff from ChatGPT via GBT Gateway
---

Buck authorized moving forward with Adam's email-specific GPT while other code work continues. Build this as a governed HCI role interface, not a standalone generic chatbot.

Purpose:
Adam Email GPT should help Adam Malmgren manage project email for HCI, especially 246GW and any projects Buck assigns, using the same source-of-truth, provenance, and approval architecture as the rest of HCI AI OS.

Core requirements:
1. Identity and role
- User: Adam Malmgren (PM role).
- Scope: project email triage, summaries, draft replies, follow-up extraction, attachment awareness, and project-context lookup.
- Never represent Buck Adams as PM for 246GW; use Adam Malmgren in logs and project context.

2. Source-of-truth rules
- Project facts come from HCI Shared Drive, HubSpot, Houzz, approved project state, and email thread content.
- HCI AI Master/My Drive is system/coordination only, never project source-of-truth.
- Every factual draft should retain provenance to the source email/thread and project documents used.

3. Email behavior
- Read original thread and all attachments before drafting.
- Preserve original message and attachment visibility.
- Carry forward attachments on reply drafts when appropriate; if not possible, warn explicitly.
- Never silently omit attachments.
- Draft-only by default; no direct sends.
- External sends always require Buck's explicit approval under current governance.
- Do not make commitments, approvals, scope changes, schedule promises, pricing promises, awards, or legal statements without human review.

4. Capabilities
- Inbox triage by project and urgency.
- Summarize thread with open questions, decisions, risks, and required actions.
- Draft replies grounded in thread + project context.
- Detect missing attachments, unanswered questions, due dates, and commitments.
- Create follow-up/task suggestions.
- Link email to project, vendor, bid package, RFI, submittal, or schedule item where applicable.
- Show confidence and source references.

5. Guardrails
- No writes to Shared Drive, HubSpot, or Houzz without explicit Buck approval.
- No email send capability exposed; draft creation only.
- If project context is ambiguous, stop and ask for project selection rather than guessing.
- If attachment content cannot be read, label the draft incomplete and identify the missing file.
- Monitored jobs remain read-only.

6. UX / operating model
- Provide a capability self-check at chat start.
- Default response structure: Thread Summary / What Needs Action / Draft Reply / Attachments / Source References / Confidence / Blockers.
- Use Mountain Time in timestamps.

7. Integration work
- Verify existing gateway endpoints for email read, draft creation, attachment carry-forward, project lookup, and source linking.
- Expose only the endpoints needed by Adam Email GPT in its Actions schema.
- Add regression tests for: thread reading, multi-attachment carry-forward, project matching, missing attachment warning, draft-only enforcement, monitored-job read-only, and no direct send.
- Live-test in a brand-new GPT chat after publishing.

8. Deliverables
- GPT instructions/system prompt.
- Actions capability matrix.
- OpenAPI/schema changes if needed.
- Governance matrix.
- End-to-end test evidence.
- Remaining blockers and any approval needed from Buck.

Acceptance test:
Adam opens a real project email thread with attachments, asks for a reply, and the GPT correctly identifies the project, reads the full thread and attachments, drafts a grounded response, preserves the original and attachments, identifies open actions, creates an Outlook draft only, and cites the source context. No direct send and no unsupported commitments.

---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: BUILD REQUEST: Adam Email GPT / Draft-Only Project Communication Assistant
created_at: 2026-07-09
summary: Handoff from ChatGPT via GBT Gateway
---

Buck approved moving forward with a separate Adam-facing Email GPT.

Build/design objective:
Create a separate Adam Email GPT / project communication assistant that helps Adam draft, organize, and respond to project emails, but does NOT send emails autonomously.

Phase 1 scope — draft-only:
- Summarize inbound emails and threads.
- Draft replies to owners, architects, engineers, subs, and vendors.
- Pull project context from approved sources: Shared Drive, HubSpot, project brain, Bid Tracker/Bid Summary, RFIs/submittals/schedule where available.
- Suggest next actions and identify missing information.
- Create Outlook drafts only when appropriate.
- Clearly label draft status and required human review.
- Require Adam or Buck to manually review and send.

Explicit prohibitions:
- No autonomous email sending.
- No contract commitments.
- No budget approvals.
- No schedule commitments without human review.
- No Shared Drive writes unless governed by existing approval rules.
- No HubSpot/Houzz writes unless explicitly approved.
- No speaking as HCI externally without human review.

Safety/governance requirements:
- All outbound content must be draft-only.
- Use existing email safety gates; do not weaken them.
- Maintain audit trail of drafted responses.
- Label source context used for each draft.
- If confidence is low or project data conflicts, ask for human review rather than guessing.
- Respect role permissions: Adam can use this as a PM/field communication assistant, not as an approval authority for governed system actions.

Deliverables:
1. Proposed GPT instructions/system prompt for Adam Email GPT.
2. Tool/action permissions list.
3. Email draft workflow.
4. Safety guardrails.
5. Test plan with sample project email scenarios.
6. Recommendation on whether this should be a new Custom GPT or a role mode within Field GPT.

Positioning to Adam/Buck:
This is an email assistant that drafts and organizes project communication. It saves time but keeps Adam fully in control of what leaves his inbox.

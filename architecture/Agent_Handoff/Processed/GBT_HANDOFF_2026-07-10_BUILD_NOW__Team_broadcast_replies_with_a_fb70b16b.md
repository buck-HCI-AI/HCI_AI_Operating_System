---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: BUILD NOW: Team broadcast replies with agent identity + evidence-based RFI peer review
created_at: 2026-07-10
summary: Handoff from ChatGPT via GBT Gateway
---

Buck authorized two permanent capabilities and wants work resumed immediately.

PART A — TEAM BROADCAST / IDENTITY-TAGGED RESPONSES
Build a shared question-broadcast workflow so Buck can send one question to all AI team members and receive separate responses identified by agent.

Required behavior:
1. Buck sends one team question through Telegram or the AI Team Document Bus.
2. The system distributes it to:
   - GBT / Chief Architect
   - Browser Claude (BC)
   - Claude Code
3. Every reply must begin with an explicit identity label:
   - [GBT — Chief Architect]
   - [BC — Browser Claude]
   - [CODE — Claude Code]
4. Responses must be written into the same shared coordination thread/history so all agents can see one another's answers.
5. The system should show who has responded and who is still pending.
6. Responses must use the 10-minute alert rule and deduplicate unchanged reminders.
7. Add an optional consensus summary after all three respond, clearly distinguishing agreement, disagreement, and unresolved decisions.
8. Persist this in the AI Team Document Bus/message-drop architecture, Standards Registry, and Operating Book.

PART B — DOUBLE-CHECK 1355R RFIs AGAINST MATURE HCI PROJECT PRACTICE
Before Buck reviews the newly generated 1355R RFIs, run a second-pass quality review that learns from real RFI usage in more mature HCI projects.

Required review process:
1. Read the actual 1355R RFIs, their source questions, plans/specs, tracker entries, generated Word documents, and draft email.
2. Search mature/historical HCI project folders and RFI records for real examples of how RFIs are structured, numbered, titled, routed, referenced, tracked, and closed.
3. Use monitored/historical projects strictly read-only. Do not modify those jobs.
4. Compare the 1355R RFIs against mature-project patterns for:
   - numbering convention,
   - title quality,
   - concise problem statement,
   - clear requested clarification,
   - sheet/detail/spec references,
   - attachment/source references,
   - responsible design party,
   - urgency/impact,
   - tracker status fields,
   - document naming,
   - folder placement,
   - email routing and attachments,
   - avoidance of duplicate or speculative RFIs.
5. Build an HCI RFI Standard from the strongest recurring patterns, but do not blindly copy project-specific quirks.
6. Flag each 1355R RFI as:
   - PASS,
   - REVISE,
   - DUPLICATE,
   - NEEDS SOURCE VERIFICATION,
   - or HUMAN JUDGMENT REQUIRED.
7. Fix only issues that are clearly supported by source documents and existing HCI practice. Preserve originals and log changes.
8. Produce a review packet for Buck with:
   - each RFI,
   - source references,
   - comparison to HCI standard,
   - changes made,
   - remaining judgment calls,
   - confidence.
9. Add regression/quality gates so future RFIs are automatically checked against the HCI RFI Standard before being marked ready for review.

Acceptance criteria:
- Buck can send one question and receive three identity-tagged answers in one shared thread.
- Every 1355R RFI is independently cross-checked against actual source documents and mature HCI examples before Buck's review.
- No mature/historical project is modified.
- No RFI is marked ready based only on AI-generated text; it must pass source and standards verification.

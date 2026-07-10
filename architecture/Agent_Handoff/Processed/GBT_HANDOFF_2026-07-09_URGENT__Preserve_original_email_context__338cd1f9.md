---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: URGENT: Preserve original email context in response drafts
created_at: 2026-07-09
summary: Handoff from ChatGPT via GBT Gateway
---

Buck identified a workflow issue: when generating response email drafts, the original email being replied to is not visible, making it difficult to verify the draft against the source message. Investigate and implement a durable fix.

Requirements:
1. Preserve the complete original email thread while drafting replies.
2. Ensure the drafting UI/workflow always lets the user view or reference the original email without losing it.
3. Do not overwrite, replace, or hide the original message when generating a draft.
4. Maintain provenance so the draft is explicitly linked to the source email.
5. Add a regression test to verify reply generation always retains access to the original email/thread.
6. Report the root cause, implementation, and evidence that the behavior is fixed.

Goal: users must always be able to compare the generated draft against the original email before sending.

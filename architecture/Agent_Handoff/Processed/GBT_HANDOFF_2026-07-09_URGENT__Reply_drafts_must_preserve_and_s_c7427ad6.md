---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: URGENT: Reply drafts must preserve and surface original attachments
created_at: 2026-07-09
summary: Handoff from ChatGPT via GBT Gateway
---

Buck identified a higher-priority email workflow issue. The original email thread is visible, but AI-generated reply drafts are not picking up or surfacing the original attachments. Investigate and fix the reply workflow so attachments remain associated with the draft.

Requirements:
1. When drafting a reply, detect and preserve all original attachments.
2. Make attachment presence explicit in the draft workflow so users can verify what is attached.
3. Preserve links between the draft and the source email plus its attachments.
4. If an attachment cannot be carried forward automatically, clearly warn the user instead of silently omitting it.
5. Add regression tests covering replies with plans, PDFs, spreadsheets, and multiple attachments.
6. Report root cause, implementation, and evidence from an end-to-end test.

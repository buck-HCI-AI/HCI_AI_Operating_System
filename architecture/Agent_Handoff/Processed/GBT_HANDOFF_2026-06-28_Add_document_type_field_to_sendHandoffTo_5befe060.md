---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: medium
status: pending
related_system: 
title: Add document_type field to sendHandoffToClaude schema
created_at: 2026-06-28
summary: Handoff from ChatGPT via GBT Gateway
---

The sendHandoffToClaude gateway endpoint needs a document_type parameter added to the schema so GBT can explicitly classify handoffs as architecture_change_request, audit_request, implementation_task, etc. Currently GBT has to embed this in the body text. Add document_type as an optional enum field to the POST /gateway/agent/handoff endpoint and update the GPT schema accordingly. Priority: normal. This is a schema improvement, not a Gate 5 blocker.

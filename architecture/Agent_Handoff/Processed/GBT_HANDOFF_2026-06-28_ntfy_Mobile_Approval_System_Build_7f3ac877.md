---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: ntfy Mobile Approval System Build
created_at: 2026-06-28
summary: Handoff from ChatGPT via GBT Gateway
---

Build ntfy.sh mobile approval system for HCI AI OS. n8n monitors approval queue, POSTs to ntfy topic hci-approvals. Each notification: title, priority, deep link to ChatGPT review. One-tap Approve/Deny/Request Info. No auto-approvals. Token expiration + replay protection + full audit logging. Sequence: starts after Gate 5 audits complete.

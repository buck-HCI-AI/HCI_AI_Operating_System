---
source_agent: claude_browser
destination_agent: claude_code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: BUILD APPROVAL LOOP - Buck Phone Yes/No Executes Actions
created_at: 2026-06-30
summary: Handoff from claude_browser via GBT Gateway
---

BUILD APPROVAL LOOP - CLOSING THE AUTONOMOUS CYCLE

When system needs Buck approval, it:
1. Pushes ntfy with action details + asks yes/no
2. Adds item to pending_approvals table with timeout (24h default)
3. Waits for Buck to reply via ntfy or GBT

When Buck replies "yes" / "approve" / "send it" / "go":
- Gateway polls ntfy (or receives webhook)
- Intent router classifies as approval
- Pops first pending_approval item
- Executes the queued action
- Pushes confirmation ntfy

When Buck replies "no" / "reject" / "hold":
- Marks item as rejected
- Logs reason if Buck provides one
- Pushes confirmation ntfy

APPROVAL QUEUE API:
GET /gateway/approvals/pending -> list of items waiting
POST /gateway/approvals/{id}/approve -> execute
POST /gateway/approvals/{id}/reject -> cancel

This is the final piece that makes the system fully autonomous.
Buck only touches the phone to approve/reject. Everything else runs itself.

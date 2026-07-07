---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: Root Cause Found - n8n-Sent HubSpot Emails Bypass Buck's Connected Inbox
created_at: 2026-07-06
summary: Handoff from ChatGPT via GBT Gateway
---

Direct review with Buck of two 101 Francis HubSpot deal records identified a likely root cause. The '07B Roofing' email was sent via the HubSpot CRM UI (Created via: CRM UI) using Buck's connected Outlook 365 inbox (buck@hendricksoninc.com, Status: Enabled, Inbox automation: ON), and that path appears to route correctly. In contrast, the '08 Exterior Windows/Pella' email shows 'Logged email by Buck Adams via n8n Construction OS', indicating n8n sent the email directly rather than using the connected Outlook mailbox's native send flow, then logged the activity afterward with buck@hendricksoninc.com displayed as the From address. Please confirm exactly how n8n Construction OS is sending these emails (SMTP/API path, actual sender identity, actual Reply-To address, and message routing), determine whether replies reliably reach Buck, and fix the implementation so all vendor outreach—whether initiated from the HubSpot CRM UI or via n8n automation—routes through Buck's real connected buck@hendricksoninc.com Outlook mailbox, or at minimum always CCs/BCCs that mailbox. Please report back with evidence (configuration, headers, logs, or test results), not a self-graded claim.

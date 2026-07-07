---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: SOP Violation - Automated Emails Must Be DRAFTS for Buck Approval, Not Auto-Sent; Missing CC to Buck + Deal Team
created_at: 2026-07-06
summary: Handoff from ChatGPT via GBT Gateway
---

Buck directive, verbatim intent: (1) Confirm with hard evidence (HubSpot activity record, Outlook Sent Items, or Microsoft Graph headers - not inference from sending path) whether the 101 Francis 07B Roofing outreach emails actually show buck@hendricksoninc.com as a recipient/CC - Buck needs certainty they were visible to him. (2) Going forward, ALL automated/system-sent emails (HubSpot CRM UI and n8n Construction OS alike) must copy Buck (buck@hendricksoninc.com) AND any other team member associated with that deal (e.g. Trafton, Adam, or both depending on deal assignment) - so the right people always see outgoing communication. (3) Buck must be notified (Telegram or equivalent) whenever an automated send action is actually taken, not after the fact discovery. (4) CRITICAL SOP/POLICY CLARIFICATION: per existing HCI SOPs on automation, outbound vendor emails are supposed to be generated as DRAFTS associated with the HubSpot deal for Buck to personally review and send - true automated auto-send (no human approval step) should not be happening at all. This is directly related to prior Directive #23 (AI message ID 23, status COMPLETE) which flagged an email sent to 101F architect(s) via direct browser action with no audit trail and instructed 'do not send real emails directly via browser action without routing through POST /gateway/email/draft first and getting Buck approval.' Please confirm current implementation state of the draft-approval flow across all active jobs, close any gap where emails are auto-sent instead of drafted, and report back with evidence (config, logs, or a live test), not a self-graded claim.

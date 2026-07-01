---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: EMAIL LOCKDOWN — 101F unauthorized email sent
created_at: 2026-07-01
summary: Handoff from ChatGPT via GBT Gateway
---

A live email was sent regarding project 101F in violation of standing directive. ALL emails must be drafted and human-approved before sending — no AI system may send live email autonomously. IMMEDIATE ACTIONS: (1) Identify the exact mechanism that sent the email — which service, endpoint, workflow, n8n node, or code path triggered it. (2) Disable or quarantine that mechanism NOW. (3) Audit ALL email-related code, n8n workflows, and API integrations — find every place an email can be sent. (4) For each: convert to draft-only mode. Drafts go to email draft folder, never sent. (5) Add a hard enforcement gate: any send() call must check email_approved flag in approval queue — if not approved, save as draft and create approval queue item for Buck review. (6) Add regression test: attempt to send email without approval — must fail and create draft instead. (7) Return full incident report: what sent it, what it said, when, to whom, and full list of all email send paths now locked down. Commit all fixes. Report to AI_TEAM/OVERNIGHT_REPORT.md.

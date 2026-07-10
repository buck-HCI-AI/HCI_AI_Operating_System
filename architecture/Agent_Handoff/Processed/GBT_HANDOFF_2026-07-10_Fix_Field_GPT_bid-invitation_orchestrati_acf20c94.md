---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: Fix Field GPT bid-invitation orchestration and Outlook draft creation
created_at: 2026-07-10
summary: Handoff from ChatGPT via GBT Gateway
---

Buck tested Field GPT with: 'I need an email draft for 1355 electrician and plumbing scope bids sent to my email.' Current behavior was too generic: it drafted chat text first, claimed Buck as Owner/Executive, and only queried drawings after Buck corrected it. Implement the correct intent-driven flow for bid invitation requests: (1) resolve project code; (2) automatically read current non-archived Shared Drive drawings/specs and relevant bid/scoping data; (3) identify electrical and plumbing scope, current plan-set references, drawing/spec sheet references, and appropriate plan links; (4) generate accurate subcontractor bid-invitation content; (5) create the Outlook draft automatically in Buck's mailbox rather than only rendering text in chat; (6) preserve current rollout policy that all operational drafts route to Buck until other users are formally onboarded; (7) correct identity wording—Buck is PM/Superintendent at Hendrickson Construction and owner/operator of HCI-AI, not Owner/Executive of Hendrickson Construction; (8) add telemetry/audit events for Field GPT user request, tools called, final result, failures, and draft ID so Chief Architect can monitor tests through the gateway. Please verify against live 1355R data and report exact files changed, test evidence, and whether any approval is required before mailbox draft creation.

---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: CRITICAL: Field GPT capability exposure audit — backend exists but tools not exposed
created_at: 2026-07-10
summary: Handoff from ChatGPT via GBT Gateway
---

Buck performed a live Field GPT test on 1355R RFI generation. This is not primarily an AI reasoning issue; it appears to be a capability exposure/configuration issue.

Evidence from Field GPT screenshots:
- Field GPT says it can search/read HCI Shared Drive.
- Field GPT says it can read project information, generate RFI text, and create live RFIs in the HCI system.
- Field GPT says it cannot update the RFI tracker, populate a Word template, save files to Drive, or create Outlook/Gmail drafts with attachments.
- It explicitly says: "If those capabilities are wired into your HCI gateway, they're not exposed through the tools I have in this conversation."

Required investigation:
Do not assume backend implementation equals GPT capability. Verify Field GPT specifically.

Produce a capability matrix:
Capability | Backend exists | Action exposed to Field GPT | Working
- Read Shared Drive
- Read plans
- Read RFI template
- Update RFI tracker
- Generate/populate Word RFI
- Save RFI docs to Shared Drive
- Create Outlook draft
- Attach files to draft
- Update HubSpot / HCI RFI system

Check:
1. GPT Actions configuration for the published Field GPT.
2. Gateway OpenAPI exposure.
3. Authentication and permissions.
4. Tool availability inside the published Field GPT, not just backend routes.
5. Whether write-capable endpoints exist but are intentionally/accidentally omitted from Field GPT schema.

UX improvement required:
Add or simulate a startup capability self-check so Field GPT reports actual available capabilities before workflows:
- ✓ Read Shared Drive
- ✓ Read Plans
- ✓ Create Live RFI
- ✗ Update Tracker
- ✗ Generate Word
- ✗ Save to Shared Drive
- ✗ Draft Outlook Email
Reason: gateway capability not exposed / auth missing / endpoint unavailable.

Acceptance test:
A real-world 1355R RFI workflow should succeed or fail at a precise step with evidence:
Questions spreadsheet -> read plans -> create RFIs -> update tracker -> generate Word docs -> save to project folder -> create draft email with attachments.

If any step is not available, Field GPT must say exactly which exposed capability is missing. It must not fall back to generic ChatGPT limitation language.

Treat this as a configuration/integration defect until proven otherwise.

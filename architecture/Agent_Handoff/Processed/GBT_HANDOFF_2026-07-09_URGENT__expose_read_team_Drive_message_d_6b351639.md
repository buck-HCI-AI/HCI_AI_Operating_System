---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: URGENT: expose/read team Drive message docs for GBT - BC bid audit not accessible
created_at: 2026-07-09
summary: Handoff from ChatGPT via GBT Gateway
---

Buck confirms this was supposed to have been done already: GBT/Chief Architect needs direct ability to read team message documents in the HCI AI Master shared channel. Current blocker: Browser Claude placed BC_TO_TEAM_BID_FOLDER_AUDIT_2026-07-09.md in HCI AI Master folder ID 1ejYXRgS34c7JmQKfHwaPNnzEBcCGUmwI, but GBT cannot open/read that arbitrary Drive file from current exposed actions. This blocks immediate architecture review of the newest bid-leveling audit.

Please fix ASAP:
1. Verify the file exists and read BC_TO_TEAM_BID_FOLDER_AUDIT_2026-07-09.md immediately.
2. Feed its key findings into the active bid-leveling code-fix work.
3. Expose or repair a gateway action/path that lets GBT read team docs by Drive file ID or filename from the HCI AI Master folder.
4. Add a simple test/proof: GBT can request/read a known team message doc without Buck pasting contents.
5. Return evidence: endpoint/tool name, sample response, permissions boundary, and whether this is HCI AI Master only or broader Drive read.

Governance: project source-of-truth remains HCI Shared Drive; this request is only for AI-team coordination docs in HCI AI Master, not treating HCI AI Master as job data source.

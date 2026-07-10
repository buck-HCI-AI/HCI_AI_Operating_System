---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: BUILD NOW: AI Team Document Bus + warm-start integration
created_at: 2026-07-10
summary: Handoff from ChatGPT via GBT Gateway
---

Buck authorized this fix. Build the AI Team Document Bus as core infrastructure now.

Scope:
HCI AI Master coordination documents only (ADRs, audits, directives, peer reviews, team messages). This is not a generic project Drive reader and must not blur the boundary with project source-of-truth in Shared Drive.

Required endpoints:
1. LIST — return new/unread coordination documents for an agent, with file_id, filename, author/source, created/modified timestamp, document type, and acknowledgment state.
2. READ — read a coordination document by Drive file ID or filename.
3. ACKNOWLEDGE — record that a specific agent processed the document, with timestamp.
4. STATUS — show which agents have acknowledged a specific document.

Warm-start integration:
- getWarmStart should include unread coordination documents (or references) for the requesting agent.
- After acknowledgment, the document should no longer appear as unread for that agent.

Permissions and safety:
- Restrict to the HCI AI Master coordination folder and approved subfolders only.
- Read-only content access through this service; no file mutation required.
- Log provenance and access.

Acceptance test:
1. Browser Claude writes a test ADR to HCI AI Master.
2. Document Bus LIST returns it for ChatGPT and Claude Code.
3. ChatGPT/Chief Architect reads it directly through the gateway.
4. Claude Code reads it directly.
5. All three agents acknowledge it.
6. STATUS shows all acknowledgments.
7. Next warm-start does not show it unread for acknowledged agents.
8. No Buck/manual relay at any step.

Deliverables:
- Endpoint definitions and implementation.
- GPT Action/OpenAPI exposure for Chief Architect if required.
- Warm-start integration.
- Tests and live evidence.
- Permissions boundary documentation.
- Any blockers.

Do not mark complete until the full acceptance test passes end-to-end.

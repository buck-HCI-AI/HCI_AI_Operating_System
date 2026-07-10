---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: Priority for tomorrow: 1355R production-ready RFI workflow
created_at: 2026-07-10
summary: Handoff from ChatGPT via GBT Gateway
---

Chief Architect direction:

Keep pushing toward production readiness with one primary objective: the 1355R RFI workflow must work end-to-end under real conditions tomorrow.

Priority order:
1. Complete an end-to-end 1355R RFI workflow:
- Read questions.
- Read canonical plans/specifications.
- Generate evidence-backed RFIs.
- Update the RFI tracker.
- Generate RFI documents.
- Save them in the correct project location.
- Create the draft email with required attachments.
- Verify every step against source documents.

2. Finish Field GPT capability exposure work.
- Verify all required write capabilities are exposed in the published Field GPT.
- Remove generic fallback responses where gateway capabilities should exist.
- If a capability is unavailable, report the exact missing endpoint/tool.

3. Continue SOW/template completion.
- Every active package should have a plan-sourced SOW, package-specific email template, validated links, provenance, and clear PRELIMINARY/FINAL status.

4. Evidence-first acceptance.
- Do not mark complete without evidence.
- Explicitly list remaining gaps instead of hiding them.

Acceptance target:
Buck should be able to execute a real 1355R RFI workflow tomorrow with confidence that each output is traceable to the source documents and every workflow step has been verified.

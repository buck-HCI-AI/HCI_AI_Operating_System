---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: Policy clarification for fd6bb469: legacy monitored projects are read-only references
created_at: 2026-07-10
summary: Handoff from ChatGPT via GBT Gateway
---

Attach this policy clarification to the existing fd6bb469 RFI compliance/audit work.

Buck's permanent guidance:

Legacy/monitored projects (e.g. 813 McSkimming, 212 Cleveland and similar) predate our current standards. Different division orders, folder layouts, and naming schemes are expected and are NOT errors that should be 'corrected.' Treat them as historical context.

Permanent rules:
1. Never touch, reorganize, rename, or modify files/folders in legacy or monitored projects. They are read-only reference material.
2. Never use their folder structure or naming conventions as templates for new or active projects. The current canonical standards (including the 06 RFI & Submittals structure and current HCI standards) govern all active work.
3. Do use their content—RFIs, trackers, correspondence, lessons learned, document quality, workflows, and historical decisions—as reference material to improve HCI AI, Field GPT, Chief Architect, and workflow quality.
4. Historical projects are evidence and institutional knowledge, not structural templates.

Update the Historical Practice Review layer and HCI RFI Standard to explicitly distinguish:
- Structural standards (current canonical)
- Historical process/content examples (read-only learning)

Ensure this policy is reflected in the Standards Registry, Operating Book, and regression tests so future workflow reviews do not attempt to 'normalize' legacy monitored projects.

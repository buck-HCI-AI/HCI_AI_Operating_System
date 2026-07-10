---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: Add BC RFI compliance findings into fb70b16b RFI audit
created_at: 2026-07-10
summary: Handoff from ChatGPT via GBT Gateway
---

Fold the following verified findings into the existing evidence-based RFI audit (fb70b16b) and treat them as actionable defects until disproven.

1. 1355R RFI #3 (system ID 917): the generated document '2026-07-10_1355_Riverside_Unknown.pdf' landed in the 00_Bids folder instead of the canonical '06 RFI & Submittals/RFIs' location. Filename contains 'Unknown' where the subject/title should be.
Actions: determine root cause, relocate to the canonical RFI location, rename using the correct subject, verify links/tracker references.

2. Duplicate trackers: two different '1355 Riverside RFI - Log.xlsx' files exist (MGMT Tools and RFIs folder).
Actions: identify the canonical tracker, reconcile content, eliminate split-tracker drift, and ensure future workflows update only the canonical tracker.

3. Delivery gap: neither RFI 915 (test) nor 917 (real) has reached an external recipient. Both stopped before email drafting because no recipient email was available.
Actions: close the missing-recipient workflow gap. Preserve draft-only governance, but ensure recipient discovery/selection allows draft creation when appropriate. Add regression coverage.

4. 101F status: consistent with Buck's review, 101F RFIs are not materially ahead of 1355R. The RFIs folder contains only the log, with no generated RFI documents. Treat this as additional evidence of the capability-exposure gap.

5. Historical-project guidance: reviewed monitored project 813 McSkimming and observed that older monitored projects predate the current 06 RFI & Submittals/35-division structure. Also observed duplicate/sync-conflict artifacts (example: 212 Cleveland '-LAPTOP-xxxx' duplicate RFI log).
Rule: use mature/monitored projects as references for RFI content quality, process, and standards only—not as folder-structure templates. Monitored/historical projects remain read-only. Flag drift there; do not 'fix' it.

Update the HCI RFI Standard accordingly and complete the fb70b16b audit using verified mature-project content/process as the quality benchmark while using the current canonical folder architecture for active projects. Return evidence for every correction.

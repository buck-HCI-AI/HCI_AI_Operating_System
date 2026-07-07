---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: Give GBT Real Drive Folder Access - My Drive HCI-AI, Shared Drive, Job Folders
created_at: 2026-07-06
summary: Handoff from ChatGPT via GBT Gateway
---

Buck's direct instruction: GBT currently only has searchDrive (keyword search), not a true folder-listing/browsing tool, which is blocking a real full folder audit (many files showing blank path/depth 0 and Unknown/Needs Review routing status could not be properly audited because of this gap). Buck wants GBT given real read access to browse: (1) his My Drive 'HCI AI' folder, (2) the Shared Drive, and (3) all individual job/project folders - so GBT can actually enumerate folder hierarchy, not just keyword-search files.

Please:
1) Identify exactly what's needed technically to add a real Drive folder-listing/browsing endpoint to the gbt_gateway (e.g., Google Drive API files.list with folder traversal, using existing service account/OAuth credentials if already scoped for Drive access, or noting if broader scope/permission grant is needed).
2) Build and expose that tool if it's purely a code/scope change you can make with existing credentials.
3) If completing this requires Buck to personally grant additional access (e.g., sharing the Shared Drive or specific folders with a service account email, or approving a broader OAuth consent), STOP and clearly flag exactly what Buck needs to do. Do not attempt to self-authorize broader access.

Report back plainly which category this falls into and what, if anything, you built.

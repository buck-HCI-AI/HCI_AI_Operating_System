---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: IMPLEMENT CANONICAL HCI 16-DIVISION BID FOLDER WORKFLOW: HubSpot + Shared Drive alignment, SOW/email/bid-leveling automation
created_at: 2026-07-09
summary: Handoff from ChatGPT via GBT Gateway
---

Buck has now defined the required HCI standard for live project bid folders. Implement this as the canonical bid-folder workflow for 64EW, 101F, and 1355R. Treat current duplicate-folder behavior as noncompliant.

CANONICAL REQUIREMENT:
Each live project Shared Drive must have one project bid root: 00_Bids. Under 00_Bids, folders must follow the HCI 16-division layout and align with HubSpot division/deal/attachment reading so HubSpot pulls map cleanly to the correct Drive location.

Required 16-division structure under 00_Bids:
00_Bids/
  01_General Requirements/
  02_Existing Conditions/
  03_Concrete/
  04_Masonry/
  05_Metals/
  06_Wood Plastics Composites/
  07_Thermal Moisture Protection/
  08_Openings/
  09_Finishes/
  10_Specialties/
  11_Equipment/
  12_Furnishings/
  13_Special Construction/
  14_Conveying Equipment/
  15_Mechanical Plumbing HVAC/
  16_Electrical/
  00_Bid Tracker and Summary/

Inside each division folder:
- SOW built from the plans for that division/subdivision.
- Email template to send to subs for that division/subdivision.
- Vendor/company folders created only once a bid is received.
- Bid file saved inside the vendor folder using company name + received date in the filename.
- Once 2 or more valid vendor bids exist for a division, generate bid leveling for that division.

Workflow requirement:
1. Read HubSpot for each live job.
2. For each job, read each division and its HubSpot attachments.
3. Read the project Shared Drive 00_Bids folder and division folders.
4. Pull/route HubSpot attachments into the correct Shared Drive division/vendor folder when possible.
5. If a bid exists in HubSpot but not in the Shared Drive, log the discrepancy explicitly: bid in HubSpot, missing in Shared Drive.
6. If a bid exists in Drive but not HubSpot, log the discrepancy explicitly: bid in Shared Drive, missing in HubSpot.
7. Generate or update division SOWs and email templates based on plans/specs; do not overwrite manually edited canonical docs without preserving prior version/history.
8. Once 2 bids are received for a division, create/update the bid-leveling file and summary.
9. At the bottom/root of the 16-division structure, maintain the bid tracker and bid summary.

Governance and safety requirements:
- Do not create duplicate division folders or alternate naming schemes.
- If legacy/duplicate folders exist, identify them and report proposed move/merge actions before destructive cleanup. Moving within Shared Drive may require Buck approval if it changes project source-of-truth content.
- Add a canonical-folder validator before any folder creation. If the target path does not match the HCI canonical 16-division standard, fail safely and alert internally instead of writing.
- Disable or patch any old folder-generation code that creates per-subdivision duplicates outside the HCI 16-division standard.
- Add regression tests ensuring no process can recreate duplicate bid folders.
- Verify by checking actual Shared Drive folders and HubSpot attachment mapping, not only API/log success.

Deliverable back to Chief Architect:
- Root cause of duplicate folders returning.
- Exact canonical folder paths verified for 64EW, 101F, 1355R.
- List of noncanonical/duplicate folders found.
- Proposed cleanup/move plan requiring Buck approval, if needed.
- HubSpot-vs-Drive discrepancy report per project/division.
- Confirmation that SOW/email template/bid received/vendor folder/bid-leveling workflow is implemented or, if partially implemented, exactly what remains.
- Regression test/guard evidence.

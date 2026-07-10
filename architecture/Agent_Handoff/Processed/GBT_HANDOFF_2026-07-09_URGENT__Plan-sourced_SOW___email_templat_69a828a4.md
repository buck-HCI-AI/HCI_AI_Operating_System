---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: URGENT: Plan-sourced SOW + email template completeness audit/fix for 64EW, 101F, 1355R
created_at: 2026-07-09
summary: Handoff from ChatGPT via GBT Gateway
---

Buck asked whether we can be sure all SOWs are correct from reading the plans and contain all needed information per division/sub, and whether all email templates are correct for each division and include links to the needed information before sending. This must become part of the full system scope.

Browser/Claude reported current findings:

64EW — PARTIALLY COMPLETE:
- Good: master SOW template exists; master email template covers BP-01 through BP-10 with Drive links; individual SOWs exist for BP-03 Concrete, BP-04 Masonry, BP-05 Metals, BP-06 Carpentry, BP-07 Waterproofing and are plan-sourced/structured; individual email templates exist for BP-03/BP-04/BP-05/BP-06 with links to drawings/structural/landscape/survey/permit.
- Issues: BP-02 Demo/Excavation lacks standalone email template in Div 02 folder; BP-07 Waterproofing template links architectural plans but not structural drawings needed for retaining wall waterproofing details; BP-08 Windows/Doors SOW is nearly empty and needs plan-sourced scope from door schedule/specs; BP-09 Painting, BP-26 Electrical, BP-31/32/33 Earthwork/Landscape lack SOWs and standalone templates; master email template typo: 'Please resond to this email directly to insure or systems reconized' must be corrected before use.

101F — MAJOR GAP:
- KB Studio floor plans dated 2026-07-01 are DRAFT / NOT FOR CONSTRUCTION. Scope can be preliminarily derived for full interior remodel, but final SOWs cannot be represented as final until permit/IFC set exists.
- Zero SOW docs and zero email templates found for 101F. Every active package needs a formal SOW/template workflow; prelim SOWs may be created with clear DRAFT/PRELIMINARY status and source plan/date.

1355R — NOT VERIFIED IN THIS AUDIT:
- Must perform separate direct folder/file pass. Do not infer from maturity or prior bid activity. Read 1355R division folders, SOWs, templates, actual plans, and links.

Required system/code/process fixes:
1. Build/enforce SOW/template completeness gate for every active bid package. A bid invite must not be considered ready unless its package has:
   - plan-sourced SOW or explicitly marked preliminary/needs final plan review,
   - email template specific to package/division,
   - correct links to all required plan/spec folders/files,
   - source provenance: drawing set name, date, sheet references where available, extraction/review date,
   - review status: FINAL, PRELIMINARY, DRAFT-NOT-FOR-CONSTRUCTION, or REVIEW REQUIRED.
2. Do not claim SOW correctness unless actual project plans/specs have been read. If plans are draft/not-for-construction, SOW output must say preliminary and cannot be final.
3. Audit/fix 64EW immediately for listed gaps, but preserve originals and log changes. No destructive deletes.
4. Create 101F preliminary SOW/template package plan from the 2026-07-01 KB Studio draft plans for active packages first, then all expected divisions; clearly label as DRAFT/PRELIMINARY until permit/IFC drawings are available.
5. Perform 1355R file-level SOW/template audit from actual folders and plans before reporting status.
6. Add regression tests/validation checks so future bid-ready status fails if SOW/template/link/provenance requirements are missing.
7. Return evidence: files read, plan sets read, SOW/template docs found/missing, generated/modified docs, link checks, review statuses, remaining REVIEW REQUIRED items, and exact blockers.

Architectural standard: SOWs and email templates are not generic admin files; they are source-traceable project controls. Every package must be traceable to the plans/specs and include the right links before it can be considered send-ready.

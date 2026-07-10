---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: PERMANENT STORAGE ARCHITECTURE: HCI AI My Drive = system; Shared Drives = project source of truth
created_at: 2026-07-10
summary: Handoff from ChatGPT via GBT Gateway
---

Buck authorized making this storage architecture permanent and enforced system-wide.

NON-NEGOTIABLE ARCHITECTURE
1. HCI AI My Drive / HCI AI Master is SYSTEM SPACE ONLY.
Allowed content includes: ADRs, Standards Registry, Operating Book, AI Team Document Bus, message drop, session logs, prompts, tests, regression reports, configuration, capability registry, role registry, workflow definitions, development notes, and system coordination artifacts.

2. HCI Shared Drives are PROJECT SOURCE OF TRUTH.
All actual project records must live in the proper project Shared Drive: drawings, specs, RFIs, submittals, bids, SOWs, email templates, trackers, change orders, meeting minutes, daily logs, closeout docs, historical project records, and other project deliverables.

3. No project files may be duplicated into HCI AI My Drive as canonical or operational project records.
The AI may read from Shared Drives and store extracted standards/lessons/metadata in the AI OS, but must not move, mirror, or treat copied project files in My Drive as authoritative.

REQUIRED IMPLEMENTATION
A. Enforce source-of-truth guards in code for:
- bid leveling
- RFI workflows
- SOW/template generation
- plan review
- project status/briefs
- historical learning/mining
- email/project matching
- Field GPT and role GPT lookups

B. Add validation failures when a project workflow attempts to read/write operational project data from HCI AI My Drive.

C. Add provenance to every output showing the Shared Drive source file/folder IDs used.

D. Audit HCI AI My Drive for existing project-file drift/duplicates for active and monitored jobs. Do not delete automatically. Produce a report of suspected project artifacts, their likely canonical Shared Drive counterparts, and recommended archive/quarantine actions for Buck approval.

E. Update permanent documentation:
- CLAUDE.md
- Standards Registry
- Operating Book
- AI Team onboarding/welcome guides
- role-GPT source-of-truth rules

F. Add regression tests proving:
1. project workflows reject HCI AI My Drive project artifacts as source;
2. Shared Drive sources are accepted;
3. outputs contain provenance;
4. monitored/historical jobs remain read-only;
5. system documents remain usable from HCI AI Master.

ACCEPTANCE TEST
Run a representative workflow for 64EW/101F/1355R and prove the system reads canonical project data from Shared Drive only, while coordination/system docs remain in HCI AI Master. Return evidence and remaining drift inventory.

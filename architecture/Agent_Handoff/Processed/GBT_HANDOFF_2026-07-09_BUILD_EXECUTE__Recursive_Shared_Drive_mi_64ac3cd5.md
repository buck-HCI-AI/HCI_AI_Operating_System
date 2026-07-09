---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: BUILD/EXECUTE: Recursive Shared Drive mining for all live + monitored HCI jobs
created_at: 2026-07-09
summary: Handoff from ChatGPT via GBT Gateway
---

Buck authorized continuation. Build and/or execute a recursive Shared Drive mining pass for all live and monitored HCI projects. Scope: live projects 64EW, 101F, 1355R; next/monitored projects including 246GW, 83SB, 813MS, 275SS, 574J, 606SW, 1395SV, LICHT, plus any other active/monitor-only folders found in the HCI Shared Drive. Requirement: do not stop at top-level folders. Traverse project folder -> every subfolder -> every file. Index metadata and, where supported, read file contents. Classify files by project, discipline, CSI/division, vendor, document type, version/date, and provenance. Detect misfiled docs, duplicate/superseded docs, naming-standard violations, missing expected folders, stale trackers/summaries, and source-of-truth conflicts. Preserve all data; do not delete or destructively modify anything without explicit approval. For allowed fixes inside existing authorized bid-folder repair scope, apply only if governance permits and log every action. Output an evidence-backed mining report with: folders scanned, files scanned, unreadable files, extraction failures, high-risk findings, immediate fixes made, durable system fixes needed, and next recommended automation steps. Key architectural requirement: answers and project intelligence must cite source files/provenance, not rely on summaries alone. If Drive/API limits prevent full file-content reads, report exact gaps and propose tool/schema changes needed to reach 100%.

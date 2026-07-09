---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: Deep verification mandate for bid folders (64EW/101F/1355R)
created_at: 2026-07-09
summary: Handoff from ChatGPT via GBT Gateway
---

Execute an evidence-first audit of 64EW, 101F, and 1355R bid folders. Traverse every folder, every subfolder, and inspect every accessible file. Verify naming, dates, duplicates, company folders, bid-level files, division trackers, master tracker, and summaries. Do not report complete unless each item is verified or explicitly listed as unverifiable. Where discrepancies are found, identify root cause and implement durable fixes within governance. If any API/tool cannot inspect file contents, record the limitation and use the appropriate mechanism to continue the audit rather than assuming correctness. Produce an evidence-backed report of findings and remaining gaps.

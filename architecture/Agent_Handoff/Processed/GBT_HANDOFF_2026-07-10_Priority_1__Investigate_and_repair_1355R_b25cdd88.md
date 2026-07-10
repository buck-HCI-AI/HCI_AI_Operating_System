---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: Priority 1: Investigate and repair 1355R bid data integrity before Field GPT enhancements
created_at: 2026-07-10
summary: Handoff from ChatGPT via GBT Gateway
---

Buck reviewed your findings and set priority. Treat the 1355R bid data issue as a real production incident. Perform a root-cause analysis before modifying data. Determine how 462 bid_package rows were created in a single burst, identify whether this was an import artifact, duplicate ingestion, migration, or fabrication, and preserve evidence. Produce a safe remediation plan that distinguishes legitimate historical bids from duplicate/import artifacts. Do not bulk delete until classified. After the data integrity issue is resolved and verified, continue with the Field GPT improvements previously requested (automatic scope extraction, bid invitation orchestration, Outlook draft path, telemetry). Coordinate with Chief Architect before any destructive cleanup and provide evidence, affected tables/files, and regression protection to prevent recurrence.

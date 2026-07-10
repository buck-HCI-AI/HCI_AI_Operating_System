---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: CLEANUP: HCI AI My Drive as system-only with monitored-project preservation
created_at: 2026-07-10
summary: Handoff from ChatGPT via GBT Gateway
---

Buck authorized a controlled cleanup of HCI AI My Drive to align with the permanent storage architecture.

Objectives:
1. HCI AI My Drive/HCI AI Master should contain only AI operating-system artifacts (coordination, ADRs, standards, prompts, tests, logs, registries, etc.).
2. Verify that no canonical project files are being stored there if they belong in a project Shared Drive.

Rules:
- DO NOT modify monitored or historical project Shared Drives.
- DO NOT duplicate monitored-project files.
- If project files from monitored jobs were copied into HCI AI My Drive, identify them and recommend replacing them with references to the canonical Shared Drive location rather than maintaining duplicates.
- If active-project artifacts are found in HCI AI My Drive, inventory them, identify their canonical Shared Drive location, and recommend move/archive actions. Do not delete automatically.
- Preserve system artifacts that legitimately belong in HCI AI Master.

Deliverables:
- Inventory of suspected project artifacts in HCI AI My Drive.
- Classification: System Artifact / Active Project Artifact / Monitored Project Artifact / Unknown.
- Canonical Shared Drive counterpart where applicable.
- Recommended action: Keep, Archive, Move, Replace with reference, Needs Buck review.
- Drift report highlighting duplicate risks.

Permanent principle:
For monitored/legacy jobs, we are silent observers and knowledge miners only. We learn from them but never reorganize, normalize, or modify them. Active projects follow current standards; monitored projects remain historical evidence.

Do not perform destructive cleanup without Buck approval. Return the inventory and proposed cleanup plan first.

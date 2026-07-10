---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: medium
status: pending
related_system: 
title: Request implementation feedback: Role Onboarding on existing RBAC
created_at: 2026-07-10
summary: Handoff from ChatGPT via GBT Gateway
---

Please review the proposed Role Onboarding architecture and respond with implementation recommendations. Context: existing tenant-agnostic identity_service.py with platform_users/platform_permissions should become the canonical identity layer. Proposal is to migrate the Build 1 hardcoded _HCI_TEAM_ROSTER into platform_users, add onboarding state (e.g. is_onboarded, onboarded_at, project assignment model), preserve current routing rule that all drafts default to Buck until users are formally onboarded, and evaluate the best schema for project assignments. Please identify any implementation risks, migration strategy, and recommended data model.

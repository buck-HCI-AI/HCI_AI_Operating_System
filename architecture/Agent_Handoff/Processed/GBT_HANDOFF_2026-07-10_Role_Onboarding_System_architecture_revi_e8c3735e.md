---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: medium
status: pending
related_system: 
title: Role Onboarding System architecture review consensus
created_at: 2026-07-10
summary: Handoff from ChatGPT via GBT Gateway
---

Architecture review from Chief Architect: Recommend building the Role Onboarding System on top of the existing tenant-agnostic RBAC/identity service (identity_service.py + platform_users/platform_permissions) rather than maintaining the Build 1 hardcoded _HCI_TEAM_ROSTER. Key recommendations: (1) migrate roster into platform_users as the canonical identity source; (2) keep identity/RBAC separate from onboarding state; (3) model onboarding independently (is_onboarded, onboarded_at, project assignments); (4) preserve current rollout rule that all operational routing defaults to Buck until formal onboarding regardless of user records; (5) consider normalized user-project relationships rather than a projects list if multi-project assignments are expected. This aligns with future config-driven multi-tenant productization.

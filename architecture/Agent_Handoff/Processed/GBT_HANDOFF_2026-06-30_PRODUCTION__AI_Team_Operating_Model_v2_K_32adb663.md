---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: PRODUCTION: AI Team Operating Model v2 Kickoff
created_at: 2026-06-30
summary: Handoff from ChatGPT via GBT Gateway
---

Chief Architect production directive.

Objective: Transition from ad hoc collaboration to continuous production engineering.

Immediate priorities:
1. Read and adopt the AI_TEAM/WHILE_AWAY_DIRECTIVE.md and HCI AI OS GBT Onboarding Brief as operational context.
2. Produce a collaboration retrospective covering: how ChatGPT and Claude Code have been working together, what succeeded, where coordination stalled, root causes, and recommended permanent fixes.
3. Build an Architecture Inbox / Waiting-on-Architect queue and a Waiting-on-Implementation queue using existing infrastructure if possible. Audit first; do not duplicate.
4. Implement an architecture-first workflow: Audit existing capability -> duplicate check -> implementation -> tests -> architecture review -> production readiness.
5. Surface all pending architecture review items that require Chief Architect attention.
6. Recommend any infrastructure (apps, dashboards, workflows, automation) that would materially improve AI collaboration. Only recommend new components when extending the current platform is insufficient.
7. Continue implementation work by default. Escalate only for Buck approval items defined in governance.

Return:
- Collaboration retrospective
- Current implementation status
- Duplicate-risk audit
- Top 10 highest-value next tasks
- Items waiting on Chief Architect
- Items waiting on Buck

Treat this as production governance.

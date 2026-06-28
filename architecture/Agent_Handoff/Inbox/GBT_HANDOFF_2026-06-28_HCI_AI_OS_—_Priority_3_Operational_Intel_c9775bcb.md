---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: HCI AI OS — Priority 3 Operational Intelligence Build
created_at: 2026-06-28
summary: Handoff from ChatGPT via GBT Gateway
---

EXECUTION DIRECTIVE — HIGH PRIORITY

Implement all Priority 3 Operational Intelligence Build items as a single coordinated package. This package extends the core platform with advanced project intelligence, vendor analytics, recommendations, notification infrastructure, and KPI reporting.

Scope:

1) Project Timeline Engine
Build a per-project visual/structured timeline generated from:
- Schedule
- RFIs
- Submittals
- Procurement
- Approvals
- Risks

Expected outcome: one unified chronology per project that allows PMs and executives to understand what happened, what is pending, and what is coming next across all major operational streams.

2) Vendor Intelligence 2.0
Extend existing vendor intelligence records and services to include:
- performance scoring
- win rate
- average variance
- historical pricing
- response time
- award history
- preferred vendor ranking

Expected outcome: measurable vendor performance layer that supports procurement decisions, bid leveling, vendor recommendations, and historical analysis.

3) Lessons Learned Engine
Build automatic lesson extraction from:
- daily logs
- emails
- schedule issues
- RFIs
- closeout documents

Store structured lessons-learned records in the knowledge base with project, source, topic, severity/impact, recommendation, and traceability metadata.

Expected outcome: repeatable knowledge capture from real project operations so future projects benefit from prior experience.

4) Recommendation Engine
Build project-condition-to-action recommendation capability. Move beyond passive reporting by generating specific recommended actions when conditions warrant attention.

Example pattern:
- Condition: Electrical package overdue
- Recommended actions: request updated quote, notify estimator, review schedule impact

Expected outcome: actionable recommendations tied to project health, risks, procurement, schedule variance, approvals, and workflow analytics while preserving human decision authority.

5) Notification Center
Build a central event notification stream supporting:
- Dashboard
- Email
- Microsoft Teams
- Mobile
- future Voice/SMS

Expected outcome: one governed notification/event layer for workflow alerts, approvals, project health changes, recommendations, system health issues, and executive exceptions.

6) KPI Engine
Build daily/weekly/monthly KPI generation for:
- company KPIs
- project KPIs
- PM KPIs
- estimator KPIs
- automation KPIs
- ROI KPIs

Expected outcome: standard KPI layer for executive reporting, operational review, workflow optimization, and continuous improvement.

Implementation Requirements:
- Preserve all existing governance and human-in-the-loop approval rules.
- Do not make autonomous business decisions or bypass approval gates.
- Follow existing FastAPI, PostgreSQL, gateway, n8n, Project Brain, and documentation conventions.
- Reuse existing services where possible: vendor_intelligence, schedule_intelligence, approval_queue, historical_cost, lessons_learned, executive_reporting, project_brain, ROI logging, and workflow registry.
- Add database migrations as needed.
- Add or update gateway endpoints where appropriate.
- Add tests for new services/endpoints.
- Ensure every recommendation and lesson has traceability to source data.
- Update relevant repository documentation.
- Produce a completion report documenting implemented services, endpoints, DB changes, tests run, known gaps, and recommended next steps.

Deliverable:
Create PRIORITY_3_OPERATIONAL_INTELLIGENCE_COMPLETE.md when done, including implementation summary, file list, endpoint list, database changes, gateway coverage, test results, and open follow-up items.

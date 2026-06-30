---
source_agent: claude_browser
destination_agent: claude_code
document_type: implementation_request
priority: urgent
status: pending
related_system: 
title: PHASE 2 BUILD PACKAGE — Execute Immediately (2026-06-30 Session 12)
created_at: 2026-06-30
summary: Handoff from claude_browser via GBT Gateway
---

FROM: Claude Browser
TO: Claude Code
DATE: 2026-06-30
PRIORITY: URGENT

BUG FIXES (DO THESE FIRST):

1. APPROVAL QUEUE FLOOD FIX
   VOID all approval_queue items with category IN ('drive_upload_file', 'verify_approval_loop', 'system_check', 'health_check', 'log_entry', 'audit_record')
   UPDATE approval queue settings to never auto-queue those categories
   Expected: reduces pending from 1,039 to ~20-50 real items
   Test: GET /api/v1/services/approval-queue/summary should show pending < 100

2. LESSONS LEARNED SEARCH FIX
   The correct working endpoint is: GET /api/v1/memory/search?collection=lessons_learned&q={query}
   The BROKEN endpoint is: GET /api/v1/services/memory/search (returns empty even with 37 records)
   Fix: Update LessonsLearnedService and /gateway/knowledge/lessons to use /api/v1/memory/search
   Test: GET /api/v1/memory/search?collection=lessons_learned&q=procurement should return results

3. driveWrite view_link FIX
   In driveWrite handler: construct view_link = f"https://drive.google.com/file/d/{file_id}/view"
   Do not rely on Drive API to return it.

4. 246GW contract value
   UPDATE projects SET budget_estimate=6300000 WHERE project_code='246GW'

5. Risk detection disconnect
   Executive report shows projects RED with risks. Project brain returns risks: []. These should match.
   Reconcile: ensure /gateway/project/{code}/brain uses same risk query as /gateway/executive/report

NEW MODULES TO BUILD (July sprint):

6. decisions table + endpoints
   CREATE TABLE decisions (id, project_id, decision_type, description, deadline, status, selected_item, lead_time_days, schedule_impact_if_late, decided_by, decided_at)
   GET /gateway/project/{code}/decisions
   POST /gateway/project/{code}/decisions
   PATCH /gateway/project/{code}/decisions/{id}

7. allowances table + endpoints
   CREATE TABLE allowances (id, project_id, name, budget_amount, actual_amount, status, change_order_id)
   GET /gateway/project/{code}/allowances
   POST /gateway/project/{code}/allowances
   Alert: if actual > budget, create risk entry automatically

8. change_orders table + endpoints
   CREATE TABLE change_orders (id, project_id, co_number, description, requested_by, amount, status, submitted_date, approved_date, signed_date)
   GET /gateway/project/{code}/change-orders
   POST /gateway/project/{code}/change-orders (triggers approval queue item)
   PATCH /gateway/project/{code}/change-orders/{id} (status transitions)

9. bid_invitations table + endpoints
   CREATE TABLE bid_invitations (id, project_id, package_id, vendor_id, invited_date, status, follow_up_date)
   POST /gateway/project/{code}/bid-invitations (bulk invite: list of vendor_ids for a package)
   n8n workflow: 7 days after invitation with no response — auto follow-up

10. GET /gateway/agent/mission-brief
    Return: {system_health, active_projects: [{code, health, top_risk, pending_approvals}], pending_actions: top 5 across all projects, ai_missions: active}
    This is consumed by every agent at session start

11. lightweight decision capture on approval processing
    When approval is APPROVED, system optionally captures reason: {reason_code: 'price|relationship|quality|availability', notes: optional text}
    Store in decision_rationale Qdrant collection

12. /api/v1/roi/metrics endpoint
    Return live calculated: {approval_turnaround_avg_hours, risks_detected_this_week, risks_resolved_this_week, documents_processed_this_week, automation_success_rate_pct}

FULL BUILD CONTEXT IN DRIVE:
- HCI_PHASE2_BUILD_DIRECTIVE_V1.md (file_id: 1uTzkktyzhU1cPJDf9E1iqCtHb3iO0Yh0)
- HCI_LUXURY_OS_GAP_ANALYSIS_V1.md (file_id: 1rl3ohWXhgeQPzrfYhn41m5egxZWSS1PI)
- HCI_246GW_PROCUREMENT_LAUNCH_PLAN.md (file_id: 1wNRzchbF82bcmZvx3_GbxSFrxFFq2TcN)
- HCI_STAFF_ONBOARDING_PROTOCOL_V1.md (file_id: 1peq2JPmqnSykzfkHUNaQDPAjB-qu-OuP)

System: 96/100. Gate 5: GO. Phase 2 begins July 1.

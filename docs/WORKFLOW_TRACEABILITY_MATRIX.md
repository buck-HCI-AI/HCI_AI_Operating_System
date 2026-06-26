# HCI AI — Workflow Traceability Matrix
**Date:** 2026-06-25 | **Audit:** Master Validation v1.0  
**Total Workflows:** 18 active, 0 planned

---

## Matrix

| ID | Name | Status | Trigger | Code File | API Endpoint | DB Writes | Qdrant | Email | WF-Events | Schedule Feed |
|----|------|--------|---------|-----------|-------------|-----------|--------|-------|-----------|--------------|
| WF-001 | New Project Setup | ✅ Active | Manual | wf001_new_project.py | POST /wf001/new-project | projects (W), hubspot_deals (ext) | project_memory (W) | ❌ | ❌ | ❌ |
| WF-002 | Meeting Intelligence | ✅ Active | Manual | wf002_meeting_intelligence.py | POST /wf002/meeting | meetings (W), hubspot_tasks (ext) | meeting_memory (W) | ❌ | ❌ | ❌ |
| WF-003 | Morning Brief | ✅ Active | 7 AM daily | wf003_morning_brief.py | POST /wf003/morning-brief | ❌ (read-only) | ❌ | ✅ | ❌ | ❌ |
| WF-004 | Daily Log (legacy) | ✅ Active (wrapper) | Manual | wf004_daily_log.py | POST /wf004/daily-log | via WF-SUPER | via WF-SUPER | via WF-SUPER | via WF-SUPER | via WF-SUPER |
| WF-005 | Lessons Learned | ✅ Active | Manual | wf005_lessons_learned.py | POST /wf005/lesson | lessons_learned (W) | lessons_learned (W) | ❌ | ❌ | ❌ |
| WF-006 | Inbox Review | ✅ Active | 7 AM daily | wf006_inbox_review.py | POST /wf006/inbox-review | bid_entries (W), rfis (W), submittals (W) | ❌ | ✅ drafts | ❌ | ❌ |
| WF-007 | Bid Leveling | ✅ Active (n8n) | Webhook | 04_Workflows/WF-007.json | n8n /webhook/bid-leveling | ❌ (Google Sheets) | ❌ | ✅ | ❌ | ❌ |
| WF-SYNC-HS | HubSpot Sync | ✅ Active | 6:50 AM daily | sync_hubspot.py | POST /sync/hubspot | hubspot_deals, hubspot_notes, hubspot_tasks (W) | ❌ | ❌ | ❌ | ❌ |
| WF-SYNC-HOUZZ | Houzz Sync | ⚠️ Broken (missing tables) | 6:45 AM daily | sync_houzz.py | POST /sync/houzz | houzz_* (W) [tables missing] | ❌ | ❌ | ❌ | Planned |
| WF-SYNC-DRIVE | Drive Sync | ✅ Active | Manual/Monday | sync_drive.py | POST /sync/drive | drive_sync_log (W) | drive_memory (W) | ❌ | ❌ | ❌ |
| WF-SUPER | Superintendent Log | ✅ Active | Manual/API | wf_superintendent.py | POST /wf-super/daily-log | daily_logs (W), risks (W), schedule_variance (W) | project_memory (W) | ✅ field report | ✅ | ✅ → schedule_variance |
| WF-PM | PM Daily Review | ✅ Active | Manual | wf_pm.py | POST /wf-pm/daily-review/{proj} | workflow_events (W) | ❌ | ❌ | ✅ | Reads from |
| WF-PM-W | PM Weekly Report | ✅ Active | Scheduled | wf_pm.py | POST /wf-pm/weekly-report | workflow_events (W) | ❌ | Optional | ✅ | Reads from |
| WF-REPORT-DAILY | Daily Field Report | ✅ Active (auto) | Auto (WF-SUPER) | wf_report.py | POST /wf-report/daily-field/{id} | ❌ | ❌ | ✅ | ❌ | ❌ |
| WF-REPORT-EXEC | Exec Health Report | ✅ Active | Manual | wf_report.py | POST /wf-report/exec-health | ❌ | ❌ | ✅ | ❌ | ❌ |
| WF-REPORT-OWNER | Owner Summary | ✅ Active | Manual | wf_report.py | POST /wf-report/owner-summary/{proj} | ❌ | ❌ | Optional | ❌ | ❌ |
| WF-REPORT-ALERT | Schedule Variance Alert | ✅ Active (auto) | Auto (WF-SUPER) | wf_report.py | POST /wf-report/schedule-alert/{id} | ❌ | ❌ | ✅ | ❌ | ❌ |
| WF-REPORT-WEEKLY | Weekly PM Email | ✅ Active | Scheduled | wf_report.py | POST /wf-report/weekly-pm | ❌ | ❌ | ✅ | ❌ | ❌ |

---

## Directive → Implementation Traceability

| Directive | Phase | Workflows Delivered | Status |
|-----------|-------|-------------------|--------|
| Infrastructure Phase 1 | Phase 1 | Docker stack, schema, seed data | ✅ Complete |
| AI Collaboration Layer | Phase 2 | sync_hubspot, sync_houzz, sync_drive | ✅ Complete |
| Service Layer v1 | Phase 3-7 | 9 intelligence services | ✅ Complete |
| Workflow Consolidation + BOOK_00 | Pre-8 | WF-001…006, WF-007 (n8n) | ✅ Complete |
| Master Directive Phase 8 | Phase 8 | workflow_events, document ingest, registry | ✅ Complete |
| Master Directive Phase 9 | Phase 9 | WF-SUPER, WF-PM, WF-006 v2, rfis/submittals | ✅ Complete |
| Master Directive Phase 10 | Phase 10 | wf_report.py (5 types), dashboard | ✅ Complete |
| Master Directive Phase 11 | Phase 11 | Auth, backup, monitor, Mac mini playbook | ✅ Complete |
| Master Validation Directive | Phase 12 | This document set | ✅ In progress |

---

## Project Brain Integration Checklist

| Workflow | Feeds Project Brain | How |
|----------|-------------------|-----|
| WF-001 | ✅ | Seeds project_memory in Qdrant on project creation |
| WF-002 | ✅ | Seeds meeting_memory in Qdrant |
| WF-SUPER | ✅ | Upserts daily log to project_memory; invalidates Redis snapshot |
| WF-005 | ✅ | Seeds lessons_learned in Qdrant |
| WF-SYNC-DRIVE | ✅ | Populates drive_memory (document context) |
| WF-SYNC-HS | ✅ | Populates hubspot_deals (deal stage, amount visible in snapshot) |
| WF-006 | ⚠️ Partial | Writes bid_entries, rfis, submittals to Postgres (visible in snapshot) but no Qdrant embed |
| WF-007 (n8n) | ❌ | Writes to Google Sheets only; no Postgres/Qdrant feed |

---

## Schedule Intelligence Feed Checklist

| Data Source | Feeds schedule_variance | Notes |
|------------|------------------------|-------|
| WF-SUPER daily logs | ✅ | Automatic via Stage 4 (analyze_log) |
| WF-PM review | ✅ | Reads schedule_variance for health assessment |
| Houzz schedule items | ❌ | Tables missing — no baseline comparison |
| Procurement items | ✅ (partial) | ProcurementService.status() feeds WF-PM |
| RFIs | ✅ (partial) | rfis table readable; no auto-schedule impact |
| Submittals | ✅ (partial) | submittals table readable; no auto-schedule impact |
| Field events (risks) | ✅ | field_risks from WF-SUPER → risks table + schedule_variance |

---

## Event Flow Summary

```
Daily Field Work Flow:
[Field] → WF-SUPER → daily_logs + project_memory (Qdrant)
                   → schedule_variance (Claude analysis)
                   → risks (escalation)
                   → workflow_events (audit)
                   → schedule_variance_alert email (if critical)
                   → daily_field_report email

Morning Intelligence Flow:
[7 AM] → WF-SYNC-HOUZZ → houzz tables (⚠️ broken)
       → WF-SYNC-HS    → hubspot tables
       → WF-006        → bid_entries / rfis / submittals + email drafts
       → WF-003        → morning brief email

Bid Management Flow:
[Inbox] → WF-006 detects BID_KEYWORDS → bid_entries
[n8n]   → WF-007 Bid Leveling → Google Sheet analysis + email

PM Oversight Flow:
[Manual] → WF-PM daily_review → Claude synthesis → workflow_events
[Friday] → WF-PM-W weekly → all projects → weekly_pm_email

Document Intelligence Flow:
[Upload] → POST /document-intelligence/upload
         → ingest_bytes() → classify → MinIO store
         → Qdrant hci_project_documents (now available after this audit fix)
         → Postgres documents table (if exists)
```

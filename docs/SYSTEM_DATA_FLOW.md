# HCI AI — System Data Flow
**Version:** 1.0 | **Date:** 2026-06-25 | **Directive:** HCI_AI_QA_Testing_and_No_Go_Live_Master_Directive_v1.0

End-to-end data flow for all major paths through the HCI AI Operating System.

---

## 1. Daily Field Operations Flow

```
Buck (field) → POST /api/v1/workflows/wf-super/daily-log
    │
    ├─ Stage 1: Save → PostgreSQL: daily_logs (project_number, work_performed,
    │                              manpower, weather, safety_notes, field_risks,
    │                              subcontractor_progress, deliveries, lookahead)
    │
    ├─ Stage 2: Embed → Qdrant: project_memory
    │           (log text + project context → 1536-dim vector)
    │
    ├─ Stage 3: Analyze → ScheduleIntelligenceService.analyze_log()
    │           → Claude Haiku analysis
    │           → PostgreSQL: schedule_variance (variance_days, severity, analysis_summary)
    │
    ├─ Stage 4: FlagRisks → RiskIntelligenceService
    │           → PostgreSQL: risks (risk_type, description, severity)
    │
    ├─ Stage 5: InvalidateCache → Redis: delete project_brain:{project_number}
    │           (forces fresh Project Brain snapshot on next query)
    │
    ├─ Stage 6: LogEvent → PostgreSQL: workflow_events
    │           (workflow_id=WF-SUPER, project_id, status=completed, metadata)
    │
    ├─ Stage 7: (auto) WF-REPORT-DAILY
    │           → Build HTML field report
    │           → Microsoft Graph API: send email to buck@ahmaspen.com
    │
    └─ Stage 8: (conditional) WF-REPORT-ALERT (if severity=high/critical)
                → Build red/yellow variance alert HTML
                → Microsoft Graph API: send alert email
```

---

## 2. Morning Brief Flow

```
launchd (7:00 AM daily) → POST /api/v1/workflows/wf003/morning-brief
    │
    ├─ 6:45 AM: WF-SYNC-HOUZZ (Playwright scrape → houzz_* tables)
    ├─ 6:50 AM: WF-SYNC-HS (HubSpot API → hubspot_deals, hubspot_notes, hubspot_tasks)
    │
    └─ 7:00 AM: WF-003
        ├─ Read PostgreSQL: all 4 projects + daily_logs (last 24h) + schedule_variance
        ├─ Read PostgreSQL: hubspot_deals (pipeline stage, amounts)
        ├─ Read Qdrant: project_memory (recent vectors for context)
        ├─ Read PostgreSQL: risks (open risks all projects)
        ├─ Claude Haiku: synthesize morning brief text
        └─ Microsoft Graph API: send email to buck@ahmaspen.com
```

---

## 3. Project Brain Q&A Flow

```
User → POST /api/v1/services/project-brain/{project}/query
    │
    ├─ Check Redis: "project_brain:{project}" (30-min cache)
    │   ├─ HIT: return cached snapshot (< 100ms)
    │   └─ MISS: build fresh snapshot ↓
    │
    ├─ Build Snapshot:
    │   ├─ PostgreSQL: projects, daily_logs, bid_packages, bid_entries
    │   ├─ PostgreSQL: risks, schedule_variance, rfis, submittals
    │   ├─ PostgreSQL: hubspot_deals (pipeline stage, amount)
    │   └─ Cache in Redis (30 min TTL)
    │
    ├─ Qdrant Search: project_memory (semantic similarity to question)
    │   → Returns top-K vectors (recent logs, meetings, lessons)
    │
    └─ Claude claude-opus-4 (or Haiku):
        → System: snapshot JSON
        → Context: Qdrant search results
        → User: question
        → Returns: structured answer with citations
```

---

## 4. HubSpot Sync Flow

```
launchd (6:50 AM) → POST /api/v1/workflows/sync/hubspot
    │
    ├─ HubSpot API: GET /crm/v3/objects/deals (paginated, all 306 deals)
    │   → PostgreSQL: hubspot_deals (upsert: deal_id, project_name, stage,
    │                               amount, owner, all 109 properties as JSONB)
    │
    ├─ HubSpot API: GET /crm/v3/objects/notes (all notes for active deals)
    │   → PostgreSQL: hubspot_notes (upsert: deal_id, note_body, note_timestamp)
    │
    ├─ HubSpot API: GET /crm/v3/objects/contacts (all 1,311 contacts)
    │   → PostgreSQL: hubspot_contacts (upsert: contact_id, first/last name, email, phone)
    │   → Qdrant: vendor_memory (embed: name + company + job title)
    │
    ├─ HubSpot API: GET /crm/v3/objects/companies (all 1,183 companies)
    │   → PostgreSQL: hubspot_companies (upsert: company_id, name, domain, industry, city)
    │   → Qdrant: vendor_memory (embed: company name + industry + city)
    │
    └─ HubSpot API: engagements (calls, emails, meetings for 196 active deals)
        → PostgreSQL: hubspot_engagements (engagement_id, deal_id, type, body, timestamp)
        → Qdrant: project_memory (embed: engagement body with deal context)
```

---

## 5. Drive Sync Flow

```
POST /api/v1/workflows/sync/drive (Manual or Monday 7 AM)
    │
    ├─ Google Drive API: list all files in HCI Drive folders
    ├─ For each file (PDF, DOCX, XLSX, GDOC, GSHEET):
    │   ├─ Download content via Google Drive API
    │   ├─ Extract text (PyPDF2 / python-docx / openpyxl)
    │   ├─ Chunk text (max 500 tokens per chunk)
    │   ├─ Embed each chunk (OpenAI text-embedding-3-small)
    │   └─ Upsert to Qdrant: drive_memory
    │       (payload: file_id, file_name, folder, chunk_index, created_time)
    │
    └─ PostgreSQL: drive_sync_log (file_id, file_name, chunk_count, status, synced_at)
```

---

## 6. Bid Intelligence Flow

```
GET /api/v1/services/bid-intelligence/{project}/summary
    │
    ├─ PostgreSQL: bid_packages (all packages for project, by CSI division)
    ├─ PostgreSQL: bid_entries (bids received per package, vendor_id, amount, status)
    ├─ PostgreSQL: vendors (vendor name, trade, CSI, contact info for matched bids)
    │
    ├─ Calculate:
    │   ├─ Coverage %: packages with ≥1 bid / total packages
    │   ├─ Leveling status: packages with ≥2 bids (can level)
    │   ├─ Unleveled: packages with 0 or 1 bids
    │   └─ Budget variance: sum(low_bid) vs. budget_target
    │
    └─ Return: structured JSON {
           coverage_pct, package_count, bid_count,
           packages_leveled, packages_unleveled,
           unleveled_trades: [...], vendor_map: {...}
       }
```

---

## 7. Inbox Review (Bid/RFI/Submittal Detection) Flow

```
launchd (7 AM daily) OR manual → POST /api/v1/workflows/wf006/inbox-review
    │
    ├─ Microsoft Graph API: GET /me/mailFolders/{inbox}/messages
    │   (reads Outlook inbox — last 24 hours)
    │
    ├─ For each email:
    │   ├─ Check BID_KEYWORDS (["BID:", "QUOTE:", "PROPOSAL:", "ESTIMATE:"])
    │   │   ├─ Match: extract dollar amount (regex)
    │   │   ├─ Match vendor via email domain + company name tokens
    │   │   └─ Write: bid_entries (project_id, vendor_id, amount, status=received)
    │   │
    │   ├─ Check RFI_KEYWORDS (["RFI", "REQUEST FOR INFORMATION"])
    │   │   ├─ Match: auto-number (RFI-001, RFI-002...)
    │   │   └─ Write: rfis (project_id, rfi_number, subject, from_email, received_at)
    │   │
    │   └─ Check SUBMITTAL_KEYWORDS (["SUBMITTAL", "SHOP DRAWING"])
    │       ├─ Match: auto-number (SUB-001, SUB-002...)
    │       └─ Write: submittals (project_id, sub_number, subject, from_email, received_at)
    │
    └─ Draft reply emails for detected items (Graph API draft, not sent)
```

---

## 8. Storage Architecture Summary

```
Data Source          → Transport              → Storage
─────────────────────────────────────────────────────────────────
Field logs (Buck)    → FastAPI /wf-super      → PostgreSQL: daily_logs
                                              → Qdrant: project_memory
                                              → Redis: (cache invalidated)

HubSpot deals        → HubSpot API            → PostgreSQL: hubspot_deals
                                              → Qdrant: project_memory

Google Drive docs    → Drive API              → Qdrant: drive_memory
                                              → PostgreSQL: drive_sync_log

Outlook emails       → Graph API              → PostgreSQL: bid_entries, rfis, submittals

Houzz schedule       → Playwright (BLOCKED)   → PostgreSQL: houzz_*

Uploaded documents   → Multipart upload       → MinIO: hci-raw-documents
                                              → Qdrant: hci_project_documents

Bids (n8n)           → n8n webhook            → Google Sheets (only — not in DB)

Meeting notes        → FastAPI /wf002         → PostgreSQL: meetings
                                              → Qdrant: meeting_memory

Lessons learned      → FastAPI /wf005         → PostgreSQL: lessons_learned
                                              → Qdrant: lessons_learned
```

---

## 9. Report Delivery Flow

```
Any report trigger → wf_report.py
    │
    ├─ Build HTML (Python f-string template)
    ├─ Microsoft Graph API:
    │   POST /me/sendMail
    │   Headers: Authorization: Bearer {access_token}
    │   Body: {
    │       "message": {
    │           "subject": "...",
    │           "toRecipients": [{"emailAddress": {"address": "buck@ahmaspen.com"}}],
    │           "body": {"contentType": "HTML", "content": html_body}
    │       }
    │   }
    └─ Returns: 202 Accepted (email queued for delivery)
```

---

*Last updated: 2026-06-25*

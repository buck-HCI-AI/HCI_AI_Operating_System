# 00_STATUS.md
**HCI AI Operating System — Live System Status**
Last updated: 2026-06-25

---

## System Health

| Layer | Component | Status | Notes |
|---|---|---|---|
| Workflow | n8n (Docker, localhost:5678) | ✅ LIVE | WF-007 live |
| CRM | HubSpot | ✅ LIVE | ~300 deals synced daily |
| Bid Tracking | Google Sheets | ✅ LIVE | 3 project sheets |
| Documents | Google Drive | ✅ LIVE | 89 files → 2,335 chunks in drive_memory |
| Email | Microsoft 365 / Graph API | ✅ LIVE | Drafts, inbox routing, AI replies |
| Truth Store | PostgreSQL 16 | ✅ LIVE | hci_os DB, 14 tables, port 5432 |
| Vector Store | Qdrant | ✅ LIVE | 7 collections, 2,335+ vectors, port 6333 |
| Cache | Redis 7 | ✅ LIVE | port 6379 |
| Object Store | MinIO | ✅ LIVE | 5 buckets: raw-docs, processed, artifacts, backups, quarantine |
| API Layer | FastAPI v0.2.0 + Uvicorn | ✅ LIVE | localhost:8000 — 7 routers, 27+ endpoints |
| Infrastructure IaC | infrastructure/ | ✅ BUILT | docker-compose + storage override + drive scripts |
| Knowledge Ingestion Engine | ingestion/ | ✅ BUILT | 6-stage pipeline: POST /ingest/file /path /batch |
| External Storage | WD My Passport 1TB | ⚠️ NEEDS REFORMAT | Currently NTFS — needs APFS + HCI_AI_DEV name |
| Agents | OpenClaw | 🔜 PLANNED | Not started |
| GitHub Remote | github.com/buck-HCI-AI | ✅ LIVE | Private repo |
| VS Code | Claude Code extension | ✅ LIVE | Workspace configured |
| Python | 3.13 | ✅ INSTALLED | fastembed, psycopg2, qdrant-client, pdfplumber, python-docx, openpyxl |
| Remote Access | Tailscale | ✅ LIVE | Mac IP: 100.97.100.69 |

---

## Active Workflows

| ID | Name | Status | Trigger |
|---|---|---|---|
| WF-007 | AI Bid Leveling Engine | ✅ LIVE | Daily 5PM MDT + POST /webhook/bid-leveling |
| WF-006 | Inbox Review | ✅ LIVE | Morning sequence (auto) |
| WF-005 | Lessons Learned | ✅ LIVE | Manual POST |
| WF-004 | Daily Log | ✅ LIVE | Manual POST |
| WF-003 | Morning Brief | ✅ LIVE | Auto 7AM + login |
| WF-002 | Meeting Intelligence | ✅ LIVE | Manual POST |
| WF-001 | New Project Setup | ✅ LIVE | Manual POST |

---

## Morning Startup Sequence (auto — 7AM + login)

1. Drive sync (Mondays only) — 89 files → drive_memory
2. Houzz sync — daily logs + schedule → Postgres + project_memory
3. HubSpot sync — all deals/notes/tasks → Postgres + project_memory
4. Bid leveling (n8n WF-007 webhook)
5. Inbox review (WF-006) — classify, move, draft AI replies
6. Morning brief email → buck@hendricksoninc.com

---

## Active Projects

| Project | HubSpot Deal | Status |
|---|---|---|
| 64 Eastwood Dr. | 332246098523 | Leveling |
| 101 Francis St. | 332313009897 | Bids Receiving |
| 1355 Riverside Dr. | TBD | Bids Receiving |
| 83 Sagebrusch Ln. | TBD | TBD |

---

## Daily Read Syncs (passive — learn from, never write)

| Source | Tables | Qdrant Collection | Frequency |
|---|---|---|---|
| HubSpot | hubspot_deals, hubspot_notes, hubspot_tasks | project_memory (offset 20000) | Daily |
| Houzz | houzz_projects, houzz_daily_logs, houzz_schedule_items | project_memory (offset 30000) | Daily |
| Google Drive | drive_sync_log | drive_memory (offset 40000) | Weekly (Monday) |

---

## Integration Layer — /03_Source_Code/integrations/

| File | Status |
|---|---|
| credentials.py | ✅ AES-256-CBC decrypt from n8n SQLite, certifi SSL |
| hubspot.py | ✅ deals, tasks, notes, create_deal, get_overdue_tasks |
| google_sheets.py | ✅ read/write bid trackers |
| microsoft_graph.py | ✅ inbox, drafts, move, send, mark_as_read |

---

## Repository

- Local: `/Users/buckadams/HCI_AI_Operating_System/`
- Infrastructure IaC: `infrastructure/` (Docker Compose — all 4 services)
- GitHub: `github.com/buck-HCI-AI/HCI_AI_Operating_System` (private) ✅
- Google Drive: `My Drive/HCI_AI_Operating_System/` ✅
- Tailscale: Mac reachable at `100.97.100.69`

---

## Open Buck Action Items

1. **Reformat WD My Passport** — Disk Utility → Erase → APFS, GUID Partition Map, name: HCI_AI_DEV
   Then run: `bash /Users/buckadams/HCI_AI_Operating_System/infrastructure/setup_storage_drive.sh`
2. HubSpot Settings → Email → Connect personal email (Outlook linked inbox)
3. Review morning brief output — confirm inbox routing working correctly
4. 83 Sagebrusch — confirm project scope (currently TBD)

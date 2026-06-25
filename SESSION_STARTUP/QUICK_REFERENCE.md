# Quick Reference — HCI AI Operating System
**All IDs, URLs, endpoints, and key locations on one page.**
Last updated: 2026-06-24

---

## Repository

| | |
|---|---|
| Local | `/Users/buckadams/HCI_AI_Operating_System/` |
| GitHub | `github.com/buck-HCI-AI/HCI_AI_Operating_System` (private) |
| Google Drive | `My Drive/HCI_AI_Operating_System/` |
| Branch | `main` |

---

## Service URLs

| Service | Local | Tailscale |
|---|---|---|
| FastAPI (auto-start) | `http://localhost:8000` | `http://bucks-macbook-air.tail2b281e.ts.net:8000` |
| Swagger UI | `http://localhost:8000/docs` | — |
| n8n | `http://localhost:5678` | `http://bucks-macbook-air.tail2b281e.ts.net:5678` |
| PostgreSQL | `localhost:5432` | `bucks-macbook-air.tail2b281e.ts.net:5432` |
| Qdrant | `http://localhost:6333` | `http://bucks-macbook-air.tail2b281e.ts.net:6333` |
| Redis | `localhost:6379` | `bucks-macbook-air.tail2b281e.ts.net:6379` |

---

## Automation Schedule

| What | When | Log |
|---|---|---|
| FastAPI server | Always (KeepAlive, auto-restart) | `/tmp/hci_api_server.log` |
| WF-007 Bid Leveling + WF-003 Morning Brief → buck@hendricksoninc.com | Mac login + 7AM daily | `/tmp/hci_morning_startup.log` |

**launchd agents:**
```bash
launchctl list | grep com.hci          # check status
launchctl unload ~/Library/LaunchAgents/com.hci.api-server.plist   # stop
launchctl load   ~/Library/LaunchAgents/com.hci.api-server.plist   # start
```

---

## API Endpoints

### Health
```
GET  /health                          # Postgres + Qdrant + Redis status
```

### Projects
```
GET  /projects/                       # all active projects
GET  /projects/{id}                   # single project
GET  /projects/{id}/bids              # bid packages + entries grouped
GET  /projects/{id}/summary           # budget summary (low/high/avg per package)
```

### Vendors
```
GET  /vendors/?search=masonry         # search by name
GET  /vendors/?csi=Division+4         # filter by CSI
GET  /vendors/{id}
GET  /vendors/{id}/bids
```

### Bids
```
GET  /bids/                           # all bid entries
GET  /bids/?project_id=3              # by project
GET  /bids/packages/                  # all bid packages
GET  /bids/leveling/{package_id}      # bid leveling sheet (low/high/avg/spread)
```

### Memory Search
```
GET  /memory/search/vendors?q=masonry+subcontractor
GET  /memory/search/bids?q=fire+suppression
GET  /memory/search/projects?q=interior+remodel
GET  /memory/search/docs?q=bid+leveling+process
GET  /memory/search/all?q=concrete+foundation    # all collections at once
GET  /memory/collections              # list all Qdrant collections + vector counts
```

### Workflows (Manual — Buck triggers)
```
POST /workflows/wf001/new-project     # New project setup
POST /workflows/wf002/meeting         # Log meeting notes + extract action items
POST /workflows/wf003/morning-brief   # Send morning brief now (auto at 7AM)
GET  /workflows/wf003/morning-brief/preview  # Preview without sending
POST /workflows/wf004/daily-log       # Log daily site report
POST /workflows/wf005/lesson          # Record lesson learned
```

---

## HubSpot

| | |
|---|---|
| Pipeline ID | `2203777729` |
| Not Started | `3524209344` |
| Scope Ready | `3524209345` |
| Sent Out | `3524209346` |
| Bids Receiving | `3524209347` |
| Leveling | `3524209348` |
| Awarded | `3524209349` |
| Not Awarded | `3524209350` |

**Active Deals:**
| Project | Deal ID |
|---|---|
| 64 Eastwood — Exterior | `332246098523` |
| 101 Francis — Windows | `332313009897` |
| 101 Francis — Roofing | `332367829692` |

---

## Google Sheets (Bid Trackers)

| Project | Sheet ID |
|---|---|
| 64 Eastwood | `1yAmLo3IIp3Vqs3BQJ6QB2O4as0KqXMZxcVvjzGBZDcQ` |
| 101 Francis | `1JExX5CeVBedTEFitM8B6hveF4Prhk0Oy6BZSBu058LE` |
| 1355 Riverside | `1-64X4XGc4P_GmYl7DRt8nGsBNfaVdP_G3qwfBLJSsnA` |

---

## n8n Credentials (stored in ~/.n8n/database.sqlite)

| Integration | Credential ID |
|---|---|
| Microsoft 365 / Outlook | `I9EZEhr72Zo6vPWX` |
| HubSpot | `H44xFkyJ22zQfjOQ` |
| Google Sheets | `Z9ViG2jWlb66ncRi` |
| Google Drive | `UDJZyRl4iZXIr4qI` |

**Encryption key:** stored in `.env` as `N8N_ENCRYPTION_KEY`
**Auth note:** HubSpot `cred["value"]` already contains `Bearer ` prefix — do NOT add it again.

---

## n8n Workflows

| ID | Name | n8n ID | Webhook |
|---|---|---|---|
| WF-007 | AI Bid Leveling Engine | `Q1akV9pVnDkmATIo` | `POST /webhook/bid-leveling` |

---

## Database (PostgreSQL)

| | |
|---|---|
| Host | `localhost:5432` |
| Database | `hci_os` |
| User | `hci_admin` |
| Password | in `.env` as `POSTGRES_PASSWORD` |
| Tables | projects, vendors, bid_packages, bid_entries, meetings, daily_logs, lessons_learned |

```bash
# Open psql shell
docker exec -it hci_postgres psql -U hci_admin -d hci_os

# Quick counts
docker exec -it hci_postgres psql -U hci_admin -d hci_os -c \
  "SELECT 'projects' as t, COUNT(*) FROM projects UNION ALL
   SELECT 'vendors', COUNT(*) FROM vendors UNION ALL
   SELECT 'bid_entries', COUNT(*) FROM bid_entries;"
```

---

## Qdrant Collections

| Collection | Vectors | Contents |
|---|---|---|
| vendor_memory | 392 | All HubSpot contacts as vendors |
| bid_memory | 26 | All bid entries with project/package context |
| project_memory | 3+ | Project summaries + daily logs |
| constitution_memory | 44 | System docs, roadmap, architecture |
| meeting_memory | 0 | Populated by WF-002 |
| lessons_learned | 0+ | Populated by WF-005 |
| photo_memory | 0 | Future: jobsite photos |

---

## Tailscale

| | |
|---|---|
| Mac IP | `100.97.100.69` |
| MagicDNS | `bucks-macbook-air.tail2b281e.ts.net` |

---

## Key File Locations

| File | Purpose |
|---|---|
| `.env` | All secrets (gitignored — never commit) |
| `03_Source_Code/integrations/credentials.py` | n8n credential decryption |
| `03_Source_Code/integrations/hubspot.py` | HubSpot API client |
| `03_Source_Code/integrations/google_sheets.py` | Sheets read/write |
| `03_Source_Code/integrations/microsoft_graph.py` | Outlook/Graph API + send_email |
| `03_Source_Code/workflows/wf001_new_project.py` | WF-001 |
| `03_Source_Code/workflows/wf002_meeting_intelligence.py` | WF-002 |
| `03_Source_Code/workflows/wf003_morning_brief.py` | WF-003 |
| `03_Source_Code/workflows/wf004_daily_log.py` | WF-004 |
| `03_Source_Code/workflows/wf005_lessons_learned.py` | WF-005 |
| `03_Source_Code/workflows/run_morning_brief.sh` | Morning startup script |
| `03_Source_Code/api/main.py` | FastAPI app entry point |
| `03_Source_Code/ingestion/run_ingestion.py` | Re-seed Postgres + Qdrant |
| `docker-compose.yml` | Full data stack config |
| `~/Library/LaunchAgents/com.hci.api-server.plist` | API server auto-start |
| `~/Library/LaunchAgents/com.hci.morning-brief.plist` | Morning startup auto-run |
| `AI_TEAM/06_NEXT_SESSION.md` | Always: what to do next session |

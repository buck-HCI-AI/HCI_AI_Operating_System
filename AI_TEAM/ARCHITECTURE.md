# ARCHITECTURE.md
**HCI AI Operating System — System Architecture**
Version: 1.0 | Last updated: 2026-06-24

---

## Philosophy

**Memory First. Intelligence Second. Automation Third.**

The system's primary value is accumulating and making accessible the institutional knowledge of Hendrickson Construction. Intelligence layers on top of memory. Automation executes on top of intelligence.

---

## System Stack

```
┌─────────────────────────────────────────────────────┐
│                   DASHBOARDS                        │
│        Executive · PM · Universal Search            │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│                    AGENTS                           │
│  Executive · PM · Bid · Procurement · Historian     │
│  Relationship (via OpenClaw)                        │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│             WORKFLOW AUTOMATION                     │
│           n8n (Docker, localhost:5678)              │
│  WF-007 ✅  WF-001-005 🔜                           │
└──────────┬─────────────────────────┬────────────────┘
           │                         │
┌──────────▼──────┐       ┌──────────▼──────────────┐
│   FastAPI       │       │   Integration Layer      │
│   (API layer)   │       │   (Python, direct API)   │
│   🔜 Planned    │       │   credentials.py ✅      │
└──────────┬──────┘       │   hubspot.py ✅          │
           │              │   google_sheets.py ✅    │
           │              │   microsoft_graph.py ✅  │
           │              └──────────────────────────┘
           │
┌──────────▼────────────────────────────────────────┐
│                  DATA LAYER                        │
│                                                    │
│  PostgreSQL 16        Qdrant             Redis 7   │
│  (truth store)    (vector/memory)    (temp state)  │
│  🔜 Ready to start  🔜 Ready to start  🔜 Ready   │
└────────────────────────────────────────────────────┘

LIVE EXTERNAL SYSTEMS:
  HubSpot CRM  ·  Google Sheets  ·  Google Drive
  Microsoft 365 / Outlook / Graph API
```

---

## Data Layer Detail

### PostgreSQL 16 — Truth Store
- **Connection:** `postgresql://hci:hci_secure_pass@localhost:5432/hci_ai`
- **Schema:** `/05_Database/postgres/schema.sql`
- **Tables:** `projects`, `vendors`, `bid_packages`, `bid_entries`, `lessons_learned`, `meetings`, `daily_logs`
- **Rule:** Postgres is authoritative for structured facts. No data lives only in Google Sheets.

### Qdrant — Meaning / Vector Store
- **Connection:** `http://localhost:6333`
- **Collections:** (defined in `/05_Database/qdrant/collections.md`)
  - `project_memory` — project context, scope, decisions
  - `vendor_memory` — vendor history, performance, relationships
  - `meeting_memory` — meeting notes and action items
  - `lessons_learned` — what worked, what didn't
  - `bid_memory` — bid history and leveling decisions
  - `constitution_memory` — HCI AI Constitution principles
  - `photo_memory` — site photos with metadata
- **Embedding model:** TBD (OpenAI text-embedding-3-small recommended)

### Redis 7 — Temporary State
- **Connection:** `redis://localhost:6379`
- **Use:** Agent session state, workflow job tracking, rate limit counters

---

## Integration Layer

All live integrations use OAuth tokens decrypted from n8n's SQLite database.

| Integration | Credential ID | Auth Type |
|---|---|---|
| Microsoft 365 | I9EZEhr72Zo6vPWX | OAuth2 |
| HubSpot | H44xFkyJ22zQfjOQ | API Key (Bearer prefix included in stored value) |
| Google Sheets | Z9ViG2jWlb66ncRi | OAuth2 |
| Google Drive | UDJZyRl4iZXIr4qI | OAuth2 |

**Encryption:** CryptoJS EVP-based AES-256-CBC, key in `.env` as `N8N_ENCRYPTION_KEY`.

---

## n8n Configuration

- **URL:** `http://localhost:5678`
- **API Base:** `http://localhost:5678/api/v1/`
- **API Key:** in `.env` as `N8N_API_KEY`
- **Workflow IDs:**
  - WF-007: `Q1akV9pVnDkmATIo` (webhook path: `bid-leveling`)

---

## HubSpot Pipeline

- **Pipeline ID:** `2203777729`
- **Stages:**
  | ID | Name |
  |---|---|
  | 3524209344 | Not Started |
  | 3524209345 | Scope Ready |
  | 3524209346 | Sent Out |
  | 3524209347 | Bids Receiving |
  | 3524209348 | Leveling |
  | 3524209349 | Awarded |
  | 3524209350 | Not Awarded |

---

## Key Engineering Constraints

1. **No secrets in git.** All credentials via `.env` (gitignored) or n8n SQLite.
2. **HubSpot writes require Buck approval.** Never auto-update HubSpot without reporting first.
3. **Repository is source of truth.** Not chat history. Not n8n UI.
4. **Improve before replacing.** Refactor existing integrations before rewriting.
5. **Docker containers on `hci_network` bridge.** All services communicate by container name.

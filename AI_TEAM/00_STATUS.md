# 00_STATUS.md
**HCI AI Operating System — Live System Status**
Last updated: 2026-06-24

---

## System Health

| Layer | Component | Status | Notes |
|---|---|---|---|
| Workflow | n8n (Docker, localhost:5678) | ✅ LIVE | WF-007 live |
| CRM | HubSpot | ✅ LIVE | 3 active deals, all stages wired |
| Bid Tracking | Google Sheets | ✅ LIVE | 3 project sheets |
| Documents | Google Drive | ✅ LIVE | Bid tracker xlsx exports working |
| Email | Microsoft 365 / Graph API | ✅ LIVE | Drafts, inbox, attachments |
| Truth Store | PostgreSQL 16 | ✅ LIVE | hci_os DB, 7 tables loaded, port 5432 |
| Vector Store | Qdrant | ✅ LIVE | 7 collections, 465 vectors, port 6333 |
| Cache | Redis 7 | ✅ LIVE | port 6379 |
| API Layer | FastAPI 0.138 + Uvicorn | ✅ LIVE | localhost:8000 — 5 routers, 20 endpoints |
| Agents | OpenClaw | 🔜 PLANNED | Not started |
| GitHub Remote | github.com/buck-HCI-AI | ✅ LIVE | Private repo, all commits pushed |
| VS Code | Claude Code extension v2.1.191 | ✅ LIVE | Workspace configured |
| Node.js | v26.3.1 + npm 11.16.0 | ✅ INSTALLED | Available for API layer / tooling |
| Python | 3.13 + pycryptodome, psycopg2, redis, qdrant-client | ✅ INSTALLED | Integration scripts ready |
| Remote Access | Tailscale | ✅ LIVE | Mac IP: 100.97.100.69 |

---

## Active Workflows

| ID | Name | Status | Trigger |
|---|---|---|---|
| WF-007 | AI Bid Leveling Engine | ✅ LIVE | Daily 5PM MDT + POST /webhook/bid-leveling |
| WF-001 | New Project Setup | 🔜 NOT BUILT | — |
| WF-002 | Meeting Intelligence | 🔜 NOT BUILT | — |
| WF-003 | Morning Brief | 🔜 NOT BUILT | — |
| WF-004 | Daily Log | 🔜 NOT BUILT | — |
| WF-005 | Lessons Learned | 🔜 NOT BUILT | — |

---

## Active Projects

| Project | HubSpot Deal | Sheet ID | Bids In | Packages | Stage |
|---|---|---|---|---|---|
| 64 Eastwood Dr. | 332246098523 | 1yAmLo3IIp3Vqs3BQJ6QB2O4as0KqXMZxcVvjzGBZDcQ | 2 (High-Con $148,290 / Teckton $7,150) | 13 | Leveling |
| 101 Francis St. | 332313009897 / 332367829692 | 1kWdF7qfqh9d0_k0Q5cZXhVeQDCKKUe0v2pQlCqwrQ_c | 1 | ~15 TBD | Bids Receiving |
| 1355 Riverside Dr. | (separate deal) | 1e2kOhixkEn4G0QYjHhTkj7D38fKuPCrg9cHRZJfbBhI | TBD | 30 | Bids Receiving |

---

## Integration Layer — /03_Source_Code/integrations/

| File | Status |
|---|---|
| credentials.py | ✅ AES-256-CBC decrypt from n8n SQLite |
| hubspot.py | ✅ deals, tasks, notes, pipeline stages |
| google_sheets.py | ✅ read/write bid trackers |
| microsoft_graph.py | ✅ inbox, drafts, attachments |

---

## Repository

- Local: `/Users/buckadams/HCI_AI_Operating_System/`
- GitHub: `github.com/buck-HCI-AI/HCI_AI_Operating_System` (private) ✅
- Google Drive: `My Drive/HCI_AI_Operating_System/` ✅
- Tailscale: Mac reachable at `100.97.100.69`

---

## Open Buck Action Items

1. HubSpot Settings → Email → Connect personal email (Outlook linked inbox)
2. CO Highlands Roofing — confirm contact first name in HubSpot
3. 101F bid emails (4 Outlook drafts) — review and send when ready
4. 1355R — clarify Jeff Kubica / fire suppression bid scope
5. Seed Postgres with current project/vendor/bid data
6. Create Qdrant collections and ingest vendor/bid memory

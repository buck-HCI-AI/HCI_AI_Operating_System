# Quick Reference — HCI AI Operating System
**All IDs, URLs, and key locations on one page.**
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
| n8n | `http://localhost:5678` | `http://bucks-macbook-air.tail2b281e.ts.net:5678` |
| PostgreSQL | `localhost:5432` | `bucks-macbook-air.tail2b281e.ts.net:5432` |
| Qdrant | `http://localhost:6333` | `http://bucks-macbook-air.tail2b281e.ts.net:6333` |
| Redis | `localhost:6379` | `bucks-macbook-air.tail2b281e.ts.net:6379` |
| FastAPI (planned) | `http://localhost:8000` | `http://bucks-macbook-air.tail2b281e.ts.net:8000` |

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
| 101 Francis | `1kWdF7qfqh9d0_k0Q5cZXhVeQDCKKUe0v2pQlCqwrQ_c` |
| 1355 Riverside | `1e2kOhixkEn4G0QYjHhTkj7D38fKuPCrg9cHRZJfbBhI` |

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
| Host | `localhost:5432` (or `hci_postgres` inside Docker) |
| Database | `hci_ai` |
| User | `hci` |
| Password | in `.env` as `POSTGRES_PASSWORD` |
| Schema | `05_Database/postgres/schema.sql` |

---

## Tailscale

| | |
|---|---|
| Mac IP | `100.97.100.69` |
| MagicDNS | `bucks-macbook-air.tail2b281e.ts.net` |
| Account | `buck-HCI-AI` |

---

## Key File Locations

| File | Purpose |
|---|---|
| `.env` | All secrets (gitignored) |
| `.env.example` | Template — commit this, not `.env` |
| `03_Source_Code/integrations/credentials.py` | n8n credential decryption |
| `03_Source_Code/integrations/hubspot.py` | HubSpot API client |
| `03_Source_Code/integrations/google_sheets.py` | Sheets read/write |
| `03_Source_Code/integrations/microsoft_graph.py` | Outlook/Graph API |
| `04_Workflows/WF-007_Bid_Leveling_Engine.json` | n8n workflow backup |
| `05_Database/postgres/schema.sql` | Full Postgres schema |
| `docker-compose.yml` | Full stack config |
| `AI_TEAM/06_NEXT_SESSION.md` | Always: what to do next |

# Chapter 22 — Database & Data Management
*HCI AI Operations Manual — Part II: AI System Operations*
**Author:** Claude Code | **Version:** 1.0 | **Date:** 2026-06-30

---

## 22.1 Database Overview

**Engine:** PostgreSQL 15 in Docker container  
**Container:** `hci_postgres`  
**Database:** `hci_os`  
**User:** `hci_admin`  
**Password:** In `.env` as `DB_PASSWORD` — never hardcoded  
**Tables:** 50+ (17 migrations applied)  
**Schema freeze:** Architecture Freeze v1.0 — 2026-06-28 — new tables require ACR

---

## 22.2 Connecting to the Database

### Direct psql
```bash
docker exec hci_postgres psql -U hci_admin -d hci_os
```

### With a query
```bash
docker exec hci_postgres psql -U hci_admin -d hci_os -c "SELECT count(*) FROM projects;"
```

### From Python (always use environment variable for password)
```python
import os, psycopg2
conn = psycopg2.connect(
    host="localhost", port=5432,
    database="hci_os", user="hci_admin",
    password=os.environ["DB_PASSWORD"]
)
```

---

## 22.3 Table Reference — Core Tables

### Projects

```sql
TABLE projects (
    id              SERIAL PRIMARY KEY,
    project_code    TEXT UNIQUE,    -- 64EW, 101F, 1355R, 246GW...
    project_name    TEXT,
    status          TEXT,           -- active, completed, archive
    address         TEXT,
    contract_value  NUMERIC,
    hubspot_deal_id TEXT,
    drawings_folder_id TEXT,        -- Google Drive folder ID
    start_date      DATE,
    completion_date DATE
)
```

**Live projects:**
| id | code | name | contract_value |
|----|------|------|---------------|
| 1 | 64EW | 64 Eastwood | TBD |
| 2 | 101F | 101 Francis | TBD |
| 3 | 1355R | 1355 Riverside | $3,541,000 |
| 4 | 83SB | 83 Sagebrusch | TBD |
| 8 | 246GW | 246 Gallo Way | $6,300,000 |

### Vendors
392 vendors with CSI division codes, contact info, bid history. Key columns: `id`, `company_name`, `csi_division`, `contact_name`, `email`, `phone`, `status`.

### Bid Entries
All bid packages across all projects. Key columns: `project_id`, `vendor_id`, `csi_code`, `package_name`, `bid_amount`, `status`, `award_status`.

### Approval Queue
Human approval loop. Key columns: `id`, `action_type`, `project_id`, `status`, `proposed_payload` (JSONB), `created_at`.

**Important:** `approval_queue` has NO `amount` column and NO `project_code` column. Amount is at `(proposed_payload->>'amount')::numeric`. Project is `project_id` (integer FK).

### Project Brain Snapshots
Daily health snapshots. Key columns: `project_id`, `snapshot_date`, `health`, `risk_count`, `schedule_variance_days`, `ai_summary`. NO `updated_at` column.

### Project Events (BTW-4)
373 events across 13 types. Key columns: `project_id`, `event_date`, `event_type`, `title`, `description`, `source_table`, `source_id`.

Event types: `daily_log`, `award`, `rfi_submitted`, `meeting`, `risk_identified`, `submittal`, `change_order`, `field_note`, `decision`, `milestone`, `personnel`, `budget`, `rfi_response`

### Connector Sync State
Last sync time per integration. Key columns: `connector_name`, `entity_type`, `last_sync_at`, `records_synced`, `status`.

---

## 22.4 Common Queries

### Project health summary
```sql
SELECT p.project_code, pbs.health, pbs.risk_count, 
       pbs.schedule_variance_days, pbs.snapshot_date
FROM project_brain_snapshots pbs
JOIN projects p ON p.id = pbs.project_id
WHERE pbs.snapshot_date = (SELECT MAX(snapshot_date) FROM project_brain_snapshots)
ORDER BY p.project_code;
```

### Open approval queue items
```sql
SELECT id, action_type, project_id, created_at,
       (proposed_payload->>'title') as title,
       (proposed_payload->>'amount')::numeric as amount
FROM approval_queue
WHERE status = 'pending_approval'
ORDER BY created_at DESC;
```

### Vendor bid summary for a project
```sql
SELECT v.company_name, be.package_name, be.bid_amount, be.award_status
FROM bid_entries be
JOIN vendors v ON v.id = be.vendor_id
JOIN projects p ON p.id = be.project_id
WHERE p.project_code = '1355R'
ORDER BY be.csi_code;
```

### Recent project events
```sql
SELECT p.project_code, pe.event_date, pe.event_type, pe.title
FROM project_events pe
JOIN projects p ON p.id = pe.project_id
WHERE p.project_code IN ('64EW','101F','1355R','246GW')
ORDER BY pe.event_date DESC
LIMIT 20;
```

### Change orders (from approval_queue, not a separate table)
```sql
SELECT id, project_id, created_at,
       (proposed_payload->>'title') as title,
       (proposed_payload->>'amount')::numeric as amount
FROM approval_queue
WHERE action_type ILIKE '%change_order%'
ORDER BY created_at DESC;
```

**Note:** There is NO `change_orders` table. All change order data lives in `approval_queue WHERE action_type ILIKE '%change_order%'`.

---

## 22.5 Schema Migration Protocol

**Migrations are in:** `05_Database/migrations/`  
**17 migrations applied** as of 2026-06-29

**Architecture Freeze v1.0 (2026-06-28):** Adding new tables or modifying existing schema requires:
1. File an ACR with GBT (Chief Architect)
2. GBT reviews architectural implications
3. ACR approved → Claude Code implements migration
4. Migration written as `migration_018_description.sql`
5. Applied: `docker exec hci_postgres psql -U hci_admin -d hci_os -f /path/to/migration.sql`
6. Verified: run `SELECT * FROM new_table LIMIT 1;`

**For additive changes only (adding columns with defaults, indexes):** Can proceed without ACR if non-breaking.

---

## 22.6 Data Rules

**Production projects (64EW, 101F, 1355R, 246GW):**
- All writes to production project data go through `approval_queue` → human approval
- Direct SQL INSERTs/UPDATEs by Claude Code are allowed for: `project_events`, `project_brain_snapshots`, `lessons_learned`, `connector_sync_state`, `gateway_request_log`
- Direct SQL is NOT allowed for: `bid_entries` awards, `vendors` (PII), `rfis` (client-facing), `approval_queue` status changes

**Reference projects (all others):**
- Read only for management updates and learning
- No operational writes

**Sensitive columns that never appear in logs/responses:**
- `.env` credentials
- `vendors.email` / `vendors.phone` in bulk exports
- `contacts.email` in bulk exports

---

## 22.7 Docker Container Management

```bash
# Check all containers running
docker-compose ps

# Check postgres specifically
docker ps --filter "name=hci_postgres" --format "table {{.Names}}\t{{.Status}}"

# View postgres logs
docker logs hci_postgres --tail 50

# Restart postgres (use only if needed — causes brief API downtime)
docker restart hci_postgres

# Connect to postgres shell
docker exec -it hci_postgres psql -U hci_admin -d hci_os

# Full restart of all containers
cd /Users/buckadams/HCI_AI_Operating_System && docker-compose restart
```

---

## 22.8 Qdrant Vector Database

**Purpose:** Semantic search across vendors, documents, project knowledge, SOPs, historical costs.

**Connect:** `http://localhost:6333`

**Collections:**
```bash
curl -s "http://localhost:6333/collections" | python3 -c "
import json,sys
d=json.load(sys.stdin)
for c in d['result']['collections']:
    print(c['name'])"
```

**Search a collection (Python):**
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

client = QdrantClient(url="http://localhost:6333")

# Semantic search
results = client.search(
    collection_name="vendor_memory",
    query_vector=[...],   # embedding from OpenAI
    limit=5
)
```

**Point counts:**
```bash
for coll in vendor_memory drive_memory project_memory hci_project_documents; do
  count=$(curl -s "http://localhost:6333/collections/$coll" | python3 -c "import json,sys; print(json.load(sys.stdin)['result']['points_count'])")
  echo "$coll: $count"
done
```

---

*Cross-reference: Chapter 17 (Architecture), Chapter 23 (Backup), Chapter 25 (Troubleshooting)*

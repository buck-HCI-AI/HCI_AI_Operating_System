# Chapter 17 — System Architecture & Service Map
*HCI AI Operations Manual — Part II: AI System Operations*
**Author:** Claude Code | **Version:** 1.0 | **Date:** 2026-06-30

---

## 17.1 What You're Running

The HCI AI Operating System is a set of software services running on Buck's Mac that give every project real-time intelligence. Think of it as a 24/7 analyst that never sleeps — watching every project, every vendor, every document, and every financial movement.

All services run locally on the Mac (localhost). The ngrok tunnel makes them reachable from anywhere — including GBT (ChatGPT).

---

## 17.2 Service Map

```
┌─────────────────────────────────────────────────────────────────────┐
│  EXTERNAL ACCESS                                                      │
│  ngrok → https://speculate-armband-retinal.ngrok-free.dev           │
└─────────────────────┬───────────────────────────────────────────────┘
                       │
┌─────────────────────▼───────────────────────────────────────────────┐
│  FastAPI Gateway — localhost:8000                                     │
│  • 427 REST endpoints across 18 services                             │
│  • Standard JSON response envelope                                   │
│  • API key authentication on write endpoints                         │
│  • GBT Gateway at /gateway/* (gbt_gateway.py)                       │
└──┬──────┬─────────┬──────────────┬────────────────────┬─────────────┘
   │      │         │              │                    │
   ▼      ▼         ▼              ▼                    ▼
PostgreSQL  Redis  Qdrant        n8n               External APIs
(hci_os)          (vectors)   (workflows)       HubSpot, Drive,
50+ tables  Cache  13 colls   55 active          Outlook, Houzz
```

---

## 17.3 Service Inventory

### Core Infrastructure

| Service | Port | Process | Managed By | Purpose |
|---------|------|---------|------------|---------|
| FastAPI | 8000 | uvicorn | launchd | Primary REST API + GBT Gateway |
| FastMCP | 8080 | uvicorn | launchd | MCP Server (43 tools for Claude Code) |
| PostgreSQL | 5432 | docker (hci_postgres) | Docker | Primary database |
| Redis | 6379 | docker | Docker | Response caching |
| Qdrant | 6333 | docker | Docker | Vector search (semantic queries) |
| MinIO | 9000 | docker | Docker | Object/file storage |
| n8n | 5678 | docker | Docker | Workflow automation |

### FastAPI Services (18 total)

| Service | Mount Path | Key Capability |
|---------|-----------|----------------|
| project_intelligence | /api/v1/services/project-intelligence | Project health, risks |
| project_brain | /api/v1/services/project-brain | Snapshots, events, memory |
| vendor_intelligence | /api/v1/services/vendor-intelligence | 392 vendors, bid history |
| bid_intelligence | /api/v1/services/bid-intelligence | Bid packages, leveling |
| approval_queue | /api/v1/services/approval-queue | Human approval loop |
| executive_reporting | /api/v1/services/executive-reporting | Morning briefs, KPIs |
| knowledge_graph | /api/v1/services/knowledge-graph | Cross-project relationships |
| schedule_intelligence | /api/v1/services/schedule-intelligence | Houzz schedule data |
| continuous_discovery | /api/v1/services/continuous-discovery | Change detection |
| predictive_engine | /api/v1/services/predictive-engine | 7 prediction types |
| houzz_intelligence | /api/v1/services/houzz | 995 schedule items |
| hubspot_integration | /api/v1/services/hubspot | CRM sync |
| drive_integration | /api/v1/services/drive | Google Drive access |
| background_learning | /api/v1/services/background-learning | Document processing |
| historical_cost | /api/v1/services/historical-cost | Garmisch cost records |
| lessons_learned | /api/v1/services/lessons-learned | Captured lessons |
| business_processes | /api/v1/services/business-processes | 27 SOPs |
| system_auditor | /api/v1/services/system-auditor | Nightly health audit |

---

## 17.4 Data Layer

### PostgreSQL Database

```
Database: hci_os
Host: localhost (via Docker: hci_postgres)
User: hci_admin
Password: in .env as DB_PASSWORD
Connect: docker exec hci_postgres psql -U hci_admin -d hci_os
```

**Key Tables:**

| Table | Rows (approx) | Purpose |
|-------|--------------|---------|
| projects | 22 | All projects (4 live, 18 reference) |
| vendors | 392 | Vendor registry with CSI codes |
| bid_entries | 1,000+ | All bid packages per project |
| approval_queue | 1,039 | Pending human approvals |
| project_brain_snapshots | 28 | Daily health snapshots |
| project_events | 373 | Project timeline events |
| project_risks_computed | 200+ | AI-detected risks |
| rfis | active | Open and closed RFIs |
| submittals | active | Submittal log |
| houzz_schedule_items | 995 | Schedule data from Houzz |
| schedule_variance | active | Variance tracking |
| connector_sync_state | 8 | Last sync per integration |
| sop_library | 27 | Standard operating procedures |
| business_processes | 27 | Business process library |
| lessons_learned | 10+ | Structured lessons |
| historical_cost_records | 21 | Garmisch reference costs |
| roi_log | 60 | Time savings tracking |
| background_learning_records | 190 | Documents queued for learning |

### Qdrant Vector Collections

| Collection | Vectors | Content |
|-----------|---------|---------|
| vendor_memory | 2,880 | Vendor profiles + bid history |
| drive_memory | 2,347 | Google Drive document embeddings |
| project_memory | 2,690 | Project knowledge base |
| hci_project_documents | 5,360 | Structural drawings, specs, contracts |
| vendor_intelligence | 200 | Bid pattern intelligence |
| hci_sops | 386 | SOP embeddings for search |
| lessons_learned | 88 | Lesson embeddings |
| hci_historical_costs | 300 | Cost record embeddings |
| + 5 more | ~1,000 | Supporting knowledge |

**Total: ~15,000 vectors across 13 collections**

---

## 17.5 GBT Gateway Architecture

The GBT Gateway (`03_Source_Code/api/routers/gbt_gateway.py`) is the bridge between GBT (ChatGPT) and the HCI AI OS. All endpoints follow this standard:

```
Request → /gateway/{endpoint}
         ↓
    _log() → gateway_request_log table
         ↓
    DB queries (read-only for GET, protected for POST)
         ↓
    _response(payload) → standard JSON envelope
```

**Standard Response Envelope:**
```json
{
  "status": "ok",
  "timestamp": "2026-06-30T...",
  "execution_time_ms": 76,
  "source_system": "hci-api",
  "payload": { ...data... },
  "warnings": [],
  "errors": []
}
```

**Auth:** GET endpoints are open (no key needed). POST endpoints require:
```
X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6
```

---

## 17.6 Process Management

### launchd Services (Auto-Start on Boot)

| plist | Service | Start Condition |
|-------|---------|-----------------|
| com.hci.api-server | FastAPI on port 8000 | Boot + on crash |
| com.hci.mcp-server | FastMCP on port 8080 | Boot + on crash |

Check status: `launchctl list | grep hci`

Restart API: `launchctl stop com.hci.api-server && launchctl start com.hci.api-server`

### Docker Services (Auto-Start via docker-compose)

```bash
cd /Users/buckadams/HCI_AI_Operating_System
docker-compose up -d  # start all containers
docker-compose ps     # check status
```

Services: hci_postgres, redis, qdrant, minio, n8n

### ngrok (Static URL — Must Be Running)

The ngrok tunnel must be running for GBT to reach the API.

Check: `pgrep ngrok`
Start: `ngrok http 8000 --domain=speculate-armband-retinal.ngrok-free.app`
Verify: `curl -s https://speculate-armband-retinal.ngrok-free.dev/gateway/health`

---

## 17.7 Code Organization

```
03_Source_Code/
├── main.py                    ← FastAPI app entry point, all router mounts
├── api/
│   ├── routers/
│   │   ├── gbt_gateway.py     ← GBT Gateway Bridge
│   │   ├── superintendent.py  ← SS daily console
│   │   ├── executive.py       ← Morning brief, mission control
│   │   ├── operations.py      ← PM weekly, client comms, action list
│   │   └── ...18 more routers
│   └── middleware/
│       └── api_key.py         ← API key validation
├── services/
│   ├── project_brain/         ← Project intelligence engine
│   ├── knowledge_graph/       ← Cross-project relationship graph
│   ├── continuous_discovery/  ← Change detection
│   ├── predictive_engine/     ← 7 prediction types
│   ├── base_service.py        ← BaseIntelligenceService (all services extend this)
│   └── connectors/            ← HubSpot, Drive, Outlook connectors
├── mcp_server/
│   └── mcp_tools.py           ← 43 MCP tools for Claude Code
└── credentials.py             ← Microsoft Graph token management
```

---

*Cross-reference: Chapter 18 (Monitoring), Chapter 19 (API Ops), Chapter 25 (Troubleshooting)*
*See also: Architecture Handbook Volume II (Intelligence Model)*

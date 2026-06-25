# 06_NEXT_SESSION.md
**Handoff notes — what the next session must do first.**
Last updated: 2026-06-25

---

## System State at Session End

Everything is live and auto-starting. Phase 3 (Dev Storage + KIE) complete.

| Layer | Status |
|---|---|
| FastAPI v0.2.0 (port 8000) | ✅ auto-starts via launchd on login |
| Morning sequence | ✅ auto-runs at 7AM + login |
| HubSpot + Houzz sync | ✅ daily auto-read |
| Drive sync | ✅ weekly auto-read (Mondays) — 2,335 chunks in drive_memory |
| PostgreSQL / Qdrant / Redis / MinIO | ✅ all running |
| Infrastructure IaC | ✅ Phase 1 + storage override + drive scripts |
| Knowledge Ingestion Engine | ✅ POST /ingest/file, /path, /batch |
| WF-001 through WF-006 | ✅ built |
| External Drive (HCI_AI_DEV) | ⚠️ Needs Buck to reformat — NTFS now |
| GitHub branch | feature/data-architecture-document-storage |

---

## Claude Code: Start Here

### Step 1 — Health check
```bash
curl -s http://localhost:8000/health | python3 -m json.tool
curl -s http://localhost:8000/docs   # verify /ingest routes appear
```

### Step 2 — Check if minio needs restart (may have stopped since last session)
```bash
curl -sf http://localhost:9000/minio/health/live && echo "MinIO OK" || echo "MinIO down"
```
If down: `cd infrastructure && docker compose up -d`

---

## Next Priority Tasks (in order)

### 1. Reformat WD My Passport → HCI_AI_DEV (Buck — 10 min)
- Open Disk Utility → Select My Passport (physical disk) → Erase
- Format: APFS | Scheme: GUID Partition Map | Name: HCI_AI_DEV
- Then: `bash infrastructure/setup_storage_drive.sh`
- Then activate external Docker storage: edit `.env`, add `HCI_STORAGE_ROOT=/Volumes/HCI_AI_DEV`
- Then: `bash infrastructure/migrate_volumes.sh`
- Then: `cd infrastructure && docker compose -f docker-compose.yml -f docker-compose.storage.yml up -d`

### 2. Test Knowledge Ingestion Engine
```bash
# Drop a PDF into 00_Incoming and test:
curl -X POST http://localhost:8000/ingest/batch \
  -d '{"directory":"/Volumes/HCI_AI_DEV/00_Incoming"}'
# Or test a single file:
curl -X POST http://localhost:8000/ingest/path \
  -d '{"path":"/path/to/test.pdf"}'
```

### 3. Merge feature branch to main
```bash
git checkout main
git merge feature/data-architecture-document-storage
git push
```

### 4. Agent Layer — Executive Agent
- First agent: answers questions about projects, vendors, bids, schedule
- Uses Qdrant drive_memory + project_memory for context
- POST /agents/executive/query
- Reference: 10_Agents/ directory (create if needed)

### 5. Bid Leveling Follow-Up (1355 Riverside)
- Multiple packages with 2+ bids ready for award analysis
- Pull WF-007 output and generate award recommendations

---

## ChatGPT: Start Here

1. `AI_TEAM/00_STATUS.md`
2. `AI_TEAM/04_ARCHITECTURE.md`
3. `docs/KNOWLEDGE_INGESTION_ENGINE_v1.md`
4. `docs/STORAGE_LAYER_CONFIGURATION_v1.md`

Open questions: Executive Agent design, MinIO auto-upload for AI artifacts, drive reformat.

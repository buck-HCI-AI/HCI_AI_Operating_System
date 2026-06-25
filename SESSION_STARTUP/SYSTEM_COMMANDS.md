# System Commands — HCI AI Operating System
**All important commands in one place.**
Last updated: 2026-06-24

---

## Docker / Data Stack

```bash
# Start full data stack
cd /Users/buckadams/HCI_AI_Operating_System
docker-compose up -d postgres qdrant redis

# Start everything including n8n
docker-compose up -d

# Stop all
docker-compose down

# View logs
docker-compose logs -f postgres
docker-compose logs -f n8n

# Check status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Postgres: open psql shell
docker exec -it hci_postgres psql -U hci -d hci_ai

# Postgres: list tables
docker exec -it hci_postgres psql -U hci -d hci_ai -c "\dt"

# Qdrant: list collections
curl http://localhost:6333/collections

# Redis: ping
docker exec -it hci_redis redis-cli ping
```

---

## n8n

```bash
# Health check
curl -s http://localhost:5678/healthz

# Trigger WF-007 bid leveling (all projects)
curl -X POST http://localhost:5678/webhook/bid-leveling \
  -H "Content-Type: application/json" \
  -d '{"projects": "all"}'

# Trigger WF-007 for specific project
curl -X POST http://localhost:5678/webhook/bid-leveling \
  -H "Content-Type: application/json" \
  -d '{"project": "64_eastwood"}'

# n8n via Tailscale (from any device)
curl -s http://bucks-macbook-air.tail2b281e.ts.net:5678/healthz
```

---

## Git / Repository

```bash
# Status
git -C /Users/buckadams/HCI_AI_Operating_System status
git -C /Users/buckadams/HCI_AI_Operating_System log --oneline -10

# Add and commit AI_TEAM updates
git -C /Users/buckadams/HCI_AI_Operating_System add AI_TEAM/
git -C /Users/buckadams/HCI_AI_Operating_System commit -m "ops: update AI_TEAM session state"

# Push to GitHub
git -C /Users/buckadams/HCI_AI_Operating_System push origin main

# Open repo in VS Code
code /Users/buckadams/HCI_AI_Operating_System

# Full add, commit, push (use carefully)
cd /Users/buckadams/HCI_AI_Operating_System && git add . && git commit -m "message" && git push origin main
```

---

## FastAPI Layer

```bash
# Start API server (port 8000, auto-reload on file save)
cd /Users/buckadams/HCI_AI_Operating_System/03_Source_Code/api
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Interactive docs (Swagger UI) — open in browser
open http://localhost:8000/docs

# Health check
curl -s http://localhost:8000/health | python3 -m json.tool

# List all projects
curl -s http://localhost:8000/projects/

# Project bid summary (id 3 = 1355 Riverside)
curl -s http://localhost:8000/projects/3/summary | python3 -m json.tool

# Semantic memory search — vendors
curl -s "http://localhost:8000/memory/search/vendors?q=masonry+subcontractor"

# Semantic search — all collections at once
curl -s "http://localhost:8000/memory/search/all?q=concrete+foundation"

# List Qdrant collections + vector counts
curl -s http://localhost:8000/memory/collections

# Via Tailscale (from any device on network)
curl -s http://bucks-macbook-air.tail2b281e.ts.net:8000/health
```

---

## Python Scripts

```bash
cd /Users/buckadams/HCI_AI_Operating_System

# Regenerate 00_STATUS.md from live services
python3 scripts/generate_ai_status.py

# Append a changelog entry
python3 scripts/update_changelog.py "What changed"

# Print session handoff summary
python3 scripts/create_next_session_summary.py

# Update 06_NEXT_SESSION.md with handoff summary
python3 scripts/create_next_session_summary.py --update
```

---

## Tailscale

```bash
# Check status
tailscale status

# Get IP
tailscale ip

# Ping another device on the network
tailscale ping [device-name]
```

**This Mac on Tailscale:**
- IP: `100.97.100.69`
- Hostname: `bucks-macbook-air.tail2b281e.ts.net`

---

## Google Drive Sync

```bash
# Manual rsync to Google Drive (run if Drive app is having issues)
rsync -av --exclude='.git' --exclude='.env' --exclude='__pycache__' \
  /Users/buckadams/HCI_AI_Operating_System/ \
  "/Users/buckadams/Library/CloudStorage/GoogleDrive-buck@hendricksoninc.com/My Drive/HCI_AI_Operating_System/"
```

---

## GitHub

```bash
# Check auth status
gh auth status

# View repo in browser
gh repo view --web

# Check if push succeeded
gh repo view buck-HCI-AI/HCI_AI_Operating_System
```

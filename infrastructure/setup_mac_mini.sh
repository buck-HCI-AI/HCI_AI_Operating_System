#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
# HCI AI Operating System — Mac mini Migration Playbook
# Target:  Mac mini M4 Pro  |  macOS Sequoia 15+
# Run as:  bash setup_mac_mini.sh [--step N]
#
# Steps:
#   1  Homebrew + system deps
#   2  Python 3.12 environment
#   3  Docker Desktop
#   4  Repository clone / transfer
#   5  Environment configuration
#   6  Docker stack startup (Postgres, Redis, MinIO, Qdrant)
#   7  Schema migration + seed data
#   8  Qdrant collection restore from snapshot
#   9  Postgres data restore from dump
#   10 Python dependencies
#   11 API server launchd agent
#   12 Supporting launchd agents (morning brief, drive watcher, backup, monitor)
#   13 ngrok tunnel (if needed)
#   14 Smoke test
# ═══════════════════════════════════════════════════════════════════════════════
set -euo pipefail

REPO_DIR="$HOME/HCI_AI_Operating_System"
BACKUP_DIR="${HCI_BACKUP_DIR:-$HOME/HCI_Backups}"
PYTHON_VERSION="3.12"
REQUIRED_MACOS="15"

# ── Colors ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()    { echo -e "${GREEN}[✓]${NC} $*"; }
warn()    { echo -e "${YELLOW}[!]${NC} $*"; }
error()   { echo -e "${RED}[✗]${NC} $*"; exit 1; }
section() { echo -e "\n${YELLOW}══ $* ══${NC}"; }

# ── Parse args ────────────────────────────────────────────────────────────────
START_STEP=1
while [[ $# -gt 0 ]]; do
  case "$1" in
    --step) START_STEP="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

run_step() {
  local step=$1
  [[ "$step" -lt "$START_STEP" ]] && return 0
  return 1
}

# ── Prerequisite check ────────────────────────────────────────────────────────
MACOS_MAJOR=$(sw_vers -productVersion | cut -d. -f1)
if [[ "$MACOS_MAJOR" -lt "$REQUIRED_MACOS" ]]; then
  error "macOS $REQUIRED_MACOS+ required (found $MACOS_MAJOR). Update first."
fi

echo "═══════════════════════════════════════════════════════"
echo " HCI AI Mac mini Migration Playbook"
echo " $(date)"
echo " Starting from step: $START_STEP"
echo "═══════════════════════════════════════════════════════"

# ══ STEP 1 — Homebrew + system deps ══════════════════════════════════════════
if ! run_step 1; then
  section "Step 1: Homebrew + System Dependencies"
  if ! command -v brew &>/dev/null; then
    info "Installing Homebrew…"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    eval "$(/opt/homebrew/bin/brew shellenv)"
  else
    info "Homebrew already installed"
  fi

  brew install \
    git \
    curl \
    wget \
    jq \
    postgresql@15 \
    awscli \
    ngrok \
    || warn "Some brew packages may have been skipped (already installed)"
  info "System deps installed"
fi

# ══ STEP 2 — Python 3.12 ══════════════════════════════════════════════════════
if ! run_step 2; then
  section "Step 2: Python $PYTHON_VERSION"
  if ! python3 --version 2>&1 | grep -q "^Python $PYTHON_VERSION"; then
    brew install "python@$PYTHON_VERSION" || true
    ln -sf "$(brew --prefix)/bin/python$PYTHON_VERSION" /usr/local/bin/python3 2>/dev/null || true
  fi
  info "Python: $(python3 --version)"
fi

# ══ STEP 3 — Docker Desktop ═══════════════════════════════════════════════════
if ! run_step 3; then
  section "Step 3: Docker Desktop"
  if ! command -v docker &>/dev/null; then
    warn "Docker Desktop not found."
    warn "Download and install manually: https://www.docker.com/products/docker-desktop/"
    warn "After install, run: bash setup_mac_mini.sh --step 4"
    echo ""
    echo "  Manual step required → install Docker Desktop, then re-run with --step 4"
    exit 0
  fi
  # Wait for Docker daemon
  until docker info &>/dev/null; do
    warn "Waiting for Docker daemon…"
    sleep 5
  done
  info "Docker ready: $(docker --version)"
fi

# ══ STEP 4 — Repository transfer ══════════════════════════════════════════════
if ! run_step 4; then
  section "Step 4: Repository"
  if [[ -d "$REPO_DIR" ]]; then
    info "Repo already at $REPO_DIR"
  else
    echo ""
    warn "Transfer the repo from your MacBook Air using one of these methods:"
    echo ""
    echo "  Option A — USB drive:"
    echo "    cp -r /Volumes/USB/HCI_AI_Operating_System $HOME/"
    echo ""
    echo "  Option B — GitHub (if repo is pushed):"
    echo "    git clone https://github.com/YOUR_ORG/HCI_AI_Operating_System $REPO_DIR"
    echo ""
    echo "  Option C — LAN rsync (run from MacBook Air):"
    echo "    rsync -avz --progress ~/HCI_AI_Operating_System/ MAC_MINI_IP:~/HCI_AI_Operating_System/"
    echo ""
    echo "  After transfer, re-run: bash setup_mac_mini.sh --step 5"
    exit 0
  fi
fi

# ══ STEP 5 — Environment configuration ════════════════════════════════════════
if ! run_step 5; then
  section "Step 5: Environment Configuration"
  ENV_FILE="$REPO_DIR/.env"
  if [[ ! -f "$ENV_FILE" ]]; then
    if [[ -f "$REPO_DIR/.env.example" ]]; then
      cp "$REPO_DIR/.env.example" "$ENV_FILE"
      warn ".env copied from .env.example — EDIT IT NOW before continuing"
      warn "Required: POSTGRES_PASSWORD, ANTHROPIC_API_KEY, HCI_API_KEYS"
      warn "After editing, re-run: bash setup_mac_mini.sh --step 6"
      exit 0
    else
      error ".env not found and no .env.example. Copy from MacBook Air first."
    fi
  fi
  info ".env present"

  # Validate required vars
  source "$ENV_FILE"
  REQUIRED_VARS=(POSTGRES_PASSWORD ANTHROPIC_API_KEY)
  for v in "${REQUIRED_VARS[@]}"; do
    if [[ -z "${!v:-}" ]]; then
      error "Missing required env var: $v — edit $ENV_FILE"
    fi
  done
  info "Required env vars present"
fi

# ══ STEP 6 — Docker stack ═════════════════════════════════════════════════════
if ! run_step 6; then
  section "Step 6: Docker Stack (Postgres, Redis, MinIO, Qdrant)"
  cd "$REPO_DIR/infrastructure"
  cp "$REPO_DIR/.env" .env 2>/dev/null || true
  docker compose up -d --wait
  info "Docker stack running:"
  docker compose ps
fi

# ══ STEP 7 — Schema migration ══════════════════════════════════════════════════
if ! run_step 7; then
  section "Step 7: Schema Migration"
  source "$REPO_DIR/.env"

  # Wait for Postgres to be ready
  until docker exec hci_postgres pg_isready -U "${POSTGRES_USER:-hci_user}" &>/dev/null; do
    warn "Waiting for Postgres…"; sleep 3
  done

  # Run init.sql (idempotent — creates tables IF NOT EXISTS)
  docker exec -i hci_postgres psql \
    -U "${POSTGRES_USER:-hci_user}" \
    -d "${POSTGRES_DB:-hci_db}" \
    < "$REPO_DIR/infrastructure/postgres/init.sql" && \
    info "Schema applied" || warn "Schema migration had warnings (may already exist)"
fi

# ══ STEP 8 — Qdrant snapshot restore ══════════════════════════════════════════
if ! run_step 8; then
  section "Step 8: Qdrant Collection Restore"
  QDRANT_URL="http://localhost:6333"

  # Find most recent Qdrant backup
  LATEST_QDRANT_DIR=$(find "$BACKUP_DIR" -maxdepth 2 -type d -name "qdrant" | sort | tail -1)
  if [[ -z "$LATEST_QDRANT_DIR" ]]; then
    warn "No Qdrant snapshots found in $BACKUP_DIR/*/qdrant/ — skipping restore"
    warn "Collections will be empty; re-embed documents to repopulate"
  else
    info "Restoring Qdrant from: $LATEST_QDRANT_DIR"
    for snap_file in "$LATEST_QDRANT_DIR"/*.snapshot; do
      [[ -e "$snap_file" ]] || continue
      # Extract collection name (filename format: collname_TIMESTAMP.snapshot)
      fname=$(basename "$snap_file")
      coll="${fname%%_2*}"  # strip _YYYYMMDD_... suffix
      info "  Restoring collection: $coll"
      # Upload snapshot
      UPLOAD=$(curl -sf -X POST "${QDRANT_URL}/collections/${coll}/snapshots/upload" \
        -H "Content-Type: application/octet-stream" \
        --data-binary "@$snap_file" 2>/dev/null || echo '{}')
      SNAP_NAME=$(echo "$UPLOAD" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('result',{}).get('name',''))" 2>/dev/null || true)
      if [[ -n "$SNAP_NAME" ]]; then
        # Recover from snapshot
        curl -sf -X POST "${QDRANT_URL}/collections/${coll}/snapshots/recover" \
          -H "Content-Type: application/json" \
          -d "{\"location\": \"${QDRANT_URL}/collections/${coll}/snapshots/${SNAP_NAME}\"}" \
          &>/dev/null && info "    ✓ $coll restored" || warn "    ✗ $coll restore failed"
      else
        warn "    ✗ Upload failed for $snap_file"
      fi
    done
  fi
fi

# ══ STEP 9 — Postgres data restore ════════════════════════════════════════════
if ! run_step 9; then
  section "Step 9: Postgres Data Restore"
  source "$REPO_DIR/.env"

  LATEST_DUMP=$(find "$BACKUP_DIR" -name "postgres_*.dump" | sort | tail -1)
  if [[ -z "$LATEST_DUMP" ]]; then
    warn "No Postgres dump found in $BACKUP_DIR — skipping restore"
    warn "Database will start empty (schema applied in step 7)"
  else
    info "Restoring from: $LATEST_DUMP"
    PGPASSWORD="${POSTGRES_PASSWORD}" docker exec -i hci_postgres pg_restore \
      -U "${POSTGRES_USER:-hci_user}" \
      -d "${POSTGRES_DB:-hci_db}" \
      --no-owner --no-privileges \
      --clean --if-exists \
      < "$LATEST_DUMP" && \
      info "Postgres restore complete" || warn "Restore had warnings (likely pre-existing data conflicts)"
  fi
fi

# ══ STEP 10 — Python dependencies ════════════════════════════════════════════
if ! run_step 10; then
  section "Step 10: Python Dependencies"
  cd "$REPO_DIR/03_Source_Code"
  if [[ -f "requirements.txt" ]]; then
    pip3 install -r requirements.txt
  else
    warn "No requirements.txt found — install deps manually"
    warn "Key packages: fastapi uvicorn psycopg2-binary redis anthropic fastembed qdrant-client"
  fi
  info "Python deps installed"
fi

# ══ STEP 11 — API server launchd ════════════════════════════════════════════
if ! run_step 11; then
  section "Step 11: API Server (launchd)"
  API_PLIST_SRC="$REPO_DIR/infrastructure/com.hci.api-server.plist"
  API_PLIST_DST="$HOME/Library/LaunchAgents/com.hci.api-server.plist"

  if [[ -f "$API_PLIST_SRC" ]]; then
    cp "$API_PLIST_SRC" "$API_PLIST_DST"
  else
    # Write a default plist
    cat > "$API_PLIST_DST" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.hci.api-server</string>
  <key>ProgramArguments</key>
  <array>
    <string>/opt/homebrew/bin/python3</string>
    <string>-m</string><string>uvicorn</string>
    <string>main:app</string>
    <string>--host</string><string>0.0.0.0</string>
    <string>--port</string><string>8000</string>
    <string>--workers</string><string>2</string>
  </array>
  <key>WorkingDirectory</key>
  <string>/Users/buckadams/HCI_AI_Operating_System/03_Source_Code/api</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key><string>/opt/homebrew/bin:/usr/bin:/bin</string>
    <key>HOME</key><string>/Users/buckadams</string>
  </dict>
  <key>StandardOutPath</key><string>/Users/buckadams/Library/Logs/hci_api.log</string>
  <key>StandardErrorPath</key><string>/Users/buckadams/Library/Logs/hci_api_err.log</string>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
</dict>
</plist>
PLIST
  fi

  launchctl load -w "$API_PLIST_DST" 2>/dev/null || true
  sleep 5
  HTTP=$(curl -sf -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "000")
  if [[ "$HTTP" == "200" ]]; then
    info "API server running at http://localhost:8000"
  else
    warn "API may not be up yet (HTTP $HTTP) — check: tail -f ~/Library/Logs/hci_api_err.log"
  fi
fi

# ══ STEP 12 — Supporting launchd agents ══════════════════════════════════════
if ! run_step 12; then
  section "Step 12: Supporting Agents"
  AGENTS=(
    "com.hci.backup.plist:$REPO_DIR/03_Source_Code/scripts"
    "com.hci.monitor.plist:$REPO_DIR/03_Source_Code/scripts"
  )
  for agent_info in "${AGENTS[@]}"; do
    plist_name="${agent_info%%:*}"
    src_dir="${agent_info##*:}"
    src_plist="$HOME/Library/LaunchAgents/$plist_name"
    if [[ -f "$src_plist" ]]; then
      launchctl load -w "$src_plist" 2>/dev/null || true
      info "Loaded: $plist_name"
    else
      warn "Not found (transfer from MacBook Air): ~/Library/LaunchAgents/$plist_name"
    fi
  done
fi

# ══ STEP 13 — ngrok ══════════════════════════════════════════════════════════
if ! run_step 13; then
  section "Step 13: ngrok Tunnel (optional)"
  warn "If you use ngrok for webhook relay, configure and load com.ngrok.hci.plist"
  warn "Your ngrok authtoken is in .env — run: ngrok config add-authtoken \$NGROK_AUTHTOKEN"
  warn "Then copy com.ngrok.hci.plist from MacBook Air and load it"
fi

# ══ STEP 14 — Smoke test ══════════════════════════════════════════════════════
if ! run_step 14; then
  section "Step 14: Smoke Test"
  API_KEY=$(grep HCI_API_KEYS "$REPO_DIR/.env" 2>/dev/null | cut -d= -f2 | tr -d ' ')
  BASE="http://localhost:8000"

  echo ""
  echo "  Testing endpoints:"

  check_endpoint() {
    local label=$1 url=$2
    HTTP=$(curl -sf -o /dev/null -w "%{http_code}" \
      -H "X-API-Key: $API_KEY" "$url" --max-time 10 2>/dev/null || echo "000")
    [[ "$HTTP" == "200" ]] && info "  $label — HTTP $HTTP" || warn "  $label — HTTP $HTTP"
  }

  check_endpoint "Health"            "$BASE/health"
  check_endpoint "Projects"          "$BASE/api/v1/projects"
  check_endpoint "Workflows"         "$BASE/api/v1/workflows"
  check_endpoint "Services"          "$BASE/api/v1/services"
  check_endpoint "Dashboard"         "$BASE/dashboard"

  echo ""
  info "Smoke test complete"
  echo ""
  echo "  Dashboard:  http://localhost:8000/dashboard"
  echo "  API Docs:   http://localhost:8000/docs"
  echo ""
fi

echo ""
echo "═══════════════════════════════════════════════════════"
echo " Migration Complete — $(date)"
echo "═══════════════════════════════════════════════════════"

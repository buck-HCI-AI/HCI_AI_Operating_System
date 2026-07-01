#!/usr/bin/env bash
# HCI AI — Daily Backup Script
# Backs up repo (rsync) + Postgres (pg_dump) + Qdrant (snapshot API)
# Primary: external drive whose name starts with HCI_AI_DEV (matched by glob —
#   macOS mounts it with a trailing space, e.g. "/Volumes/HCI_AI_DEV ", which broke
#   exact-path matching here for months; fixed 2026-06-30, see ADR-008)
# Fallback: ~/HCI_Backups
# Keeps 7 days of rolling backups.
# Runs via launchd (com.hci.backup) daily at 02:00.
set -euo pipefail

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATE_TAG=$(date +"%Y%m%d")

# ── Destination ───────────────────────────────────────────────────────────────
FALLBACK_DIR="$HOME/HCI_Backups"

# Glob-match instead of exact path: tolerates the trailing space / any suffix
# macOS appends to the actual mounted volume name.
PRIMARY_VOLUME="${HCI_BACKUP_VOLUME:-}"
if [[ -z "$PRIMARY_VOLUME" ]]; then
  for v in /Volumes/HCI_AI_DEV*; do
    [[ -d "$v" ]] && PRIMARY_VOLUME="$v" && break
  done
fi

if [[ -n "$PRIMARY_VOLUME" && -d "$PRIMARY_VOLUME" && -w "$PRIMARY_VOLUME" ]]; then
  BACKUP_ROOT="${PRIMARY_VOLUME}/backups"
else
  echo "[backup] External drive not mounted (looked for /Volumes/HCI_AI_DEV*) — using fallback: $FALLBACK_DIR"
  BACKUP_ROOT="$FALLBACK_DIR"
fi

BACKUP_DIR="$BACKUP_ROOT/$DATE_TAG"
mkdir -p "$BACKUP_DIR"

LOG="$BACKUP_DIR/backup.log"
exec > >(tee -a "$LOG") 2>&1

echo "═══════════════════════════════════════════════════════"
echo " HCI AI Backup  —  $TIMESTAMP"
echo " Destination:   $BACKUP_DIR"
echo "═══════════════════════════════════════════════════════"

# ── Load env ──────────────────────────────────────────────────────────────────
ENV_FILE="$HOME/HCI_AI_Operating_System/.env"
if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

PGPASSWORD="${POSTGRES_PASSWORD:-hci_pass}"
export PGPASSWORD

# ── 0. Repo rsync (source code + docs, including untracked/uncommitted files) ──
echo ""
echo "[0/4] Repo rsync…"
REPO_ROOT="$HOME/HCI_AI_Operating_System"
REPO_OUT="$BACKUP_DIR/repo"
mkdir -p "$REPO_OUT"
rsync -a --delete \
  --exclude='.git' --exclude='node_modules' --exclude='__pycache__' \
  --exclude='*.pyc' --exclude='.venv' \
  "$REPO_ROOT"/ "$REPO_OUT"/ && \
  echo "      ✓ $(du -sh "$REPO_OUT" | cut -f1)  →  $REPO_OUT" || \
  echo "      ✗ Repo rsync FAILED"

# ── 1. Postgres dump ──────────────────────────────────────────────────────────
echo ""
echo "[1/4] Postgres dump…"
PG_OUT="$BACKUP_DIR/postgres_${TIMESTAMP}.dump"
docker exec hci_postgres pg_dump \
  -U "${POSTGRES_USER:-hci_user}" \
  -d "${POSTGRES_DB:-hci_db}" \
  -Fc \
  --no-password \
  > "$PG_OUT" && \
  echo "      ✓ $(du -sh "$PG_OUT" | cut -f1)  →  $PG_OUT" || \
  echo "      ✗ Postgres dump FAILED"

# ── 2. Qdrant snapshots ───────────────────────────────────────────────────────
echo ""
echo "[2/4] Qdrant snapshots…"
QDRANT_URL="${QDRANT_URL:-http://localhost:6333}"
QDRANT_DIR="$BACKUP_DIR/qdrant"
mkdir -p "$QDRANT_DIR"

# Trigger snapshot for each collection
COLLECTIONS=$(curl -sf "${QDRANT_URL}/collections" 2>/dev/null | \
  python3 -c "import sys,json; d=json.load(sys.stdin); [print(c['name']) for c in d.get('result',{}).get('collections',[])]" 2>/dev/null || true)

if [[ -z "$COLLECTIONS" ]]; then
  echo "      ⚠ Qdrant not reachable — skipping vector snapshots"
else
  while IFS= read -r coll; do
    [[ -z "$coll" ]] && continue
    SNAP=$(curl -sf -X POST "${QDRANT_URL}/collections/${coll}/snapshots" 2>/dev/null | \
      python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('result',{}).get('name',''))" 2>/dev/null || true)
    if [[ -n "$SNAP" ]]; then
      # Download snapshot file
      curl -sf "${QDRANT_URL}/collections/${coll}/snapshots/${SNAP}" \
        -o "${QDRANT_DIR}/${coll}_${TIMESTAMP}.snapshot" && \
        echo "      ✓ $coll → ${coll}_${TIMESTAMP}.snapshot" || \
        echo "      ✗ $coll snapshot download failed"
    else
      echo "      ✗ $coll snapshot creation failed"
    fi
  done <<< "$COLLECTIONS"
fi

# ── 3. MinIO metadata backup (bucket listing) ─────────────────────────────────
echo ""
echo "[3/4] MinIO bucket manifest…"
MINIO_OUT="$BACKUP_DIR/minio_manifest_${TIMESTAMP}.txt"
docker exec hci_minio mc alias set local http://localhost:9000 \
  "${MINIO_ROOT_USER:-hci_minio}" "${MINIO_ROOT_PASSWORD:-changeme}" \
  --quiet 2>/dev/null || true
docker exec hci_minio mc ls --recursive local > "$MINIO_OUT" 2>/dev/null && \
  echo "      ✓ MinIO manifest saved ($(wc -l < "$MINIO_OUT") objects)" || \
  echo "      ⚠ MinIO manifest unavailable"

# ── 4. Prune old backups (keep 7 days) ───────────────────────────────────────
# `head -n -7` is a GNU-ism — BSD/macOS head errors on negative counts, which
# silently failed under `set -e` every night until this fix (2026-06-30).
echo ""
echo "[4/4] Pruning backups older than 7 days…"
ALL_DIRS=()
while IFS= read -r d; do ALL_DIRS+=("$d"); done < <(find "$BACKUP_ROOT" -maxdepth 1 -type d -name "20*" | sort)
TOTAL_DIRS=${#ALL_DIRS[@]}
if (( TOTAL_DIRS > 7 )); then
  for ((i = 0; i < TOTAL_DIRS - 7; i++)); do
    rm -rf "${ALL_DIRS[$i]}"
    echo "      ✗ Removed ${ALL_DIRS[$i]}"
  done
fi
KEPT=$(find "$BACKUP_ROOT" -maxdepth 1 -type d -name "20*" | wc -l | tr -d ' ')
echo "      ✓ $KEPT backup days retained"

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
TOTAL=$(du -sh "$BACKUP_DIR" | cut -f1)
echo "═══════════════════════════════════════════════════════"
echo " Backup complete  —  $TOTAL total  —  $BACKUP_DIR"
echo "═══════════════════════════════════════════════════════"

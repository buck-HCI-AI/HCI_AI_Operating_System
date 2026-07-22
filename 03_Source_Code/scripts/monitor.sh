#!/usr/bin/env bash
# HCI AI — System Monitor
# Runs every 5 minutes via launchd (com.hci.monitor).
# Checks: API health, Docker containers, disk usage.
# Sends email via Graph API if API is down or disk > 90%.
set -uo pipefail

API_URL="${HCI_API_URL:-http://localhost:8000}"
ALERT_EMAIL="${BUCK_EMAIL:-buck@ahmaspen.com}"
DISK_THRESHOLD=90
LOG_FILE="$HOME/Library/Logs/hci_monitor.log"
LOCKFILE="/tmp/hci_monitor.lock"
MAX_RESTART_ATTEMPTS=3

# ── Helpers ───────────────────────────────────────────────────────────────────
log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" | tee -a "$LOG_FILE"; }

send_alert() {
  local subject="$1" body="$2"
  # Try Graph API email via Python helper
  python3 - <<PYEOF 2>/dev/null || log "[WARN] Alert email send failed"
import sys, os, json, urllib.request, urllib.error
sys.path.insert(0, '$HOME/HCI_AI_Operating_System/03_Source_Code')
sys.path.insert(0, '$HOME/HCI_AI_Operating_System/03_Source_Code/integrations')
try:
    from microsoft_graph import send_email
    result = send_email(
        to=[("Buck Adams", "$ALERT_EMAIL")],
        subject="$subject",
        body_html="<p>$body</p><hr><p>HCI AI Monitor — $(date)</p>"
    )
    print("[monitor] Alert sent:", result)
except Exception as e:
    print("[monitor] Email failed:", e)
    sys.exit(1)
PYEOF
}

# ── Lock (prevent overlap) ───────────────────────────────────────────────────
if [[ -f "$LOCKFILE" ]]; then
  log "[monitor] Already running (lockfile exists) — skipping"
  exit 0
fi
touch "$LOCKFILE"
trap 'rm -f "$LOCKFILE"' EXIT

# ── 1. API Health Check ──────────────────────────────────────────────────────
log "[monitor] Checking API health at $API_URL/health…"
HTTP_STATUS=$(curl -sf -o /dev/null -w "%{http_code}" --max-time 10 "$API_URL/health" 2>/dev/null || echo "000")

if [[ "$HTTP_STATUS" != "200" ]]; then
  log "[monitor] ⚠ API DOWN (HTTP $HTTP_STATUS) — attempting restart"

  # Try restart via launchctl
  RESTART_COUNT_FILE="/tmp/hci_api_restart_count"
  COUNT=$(cat "$RESTART_COUNT_FILE" 2>/dev/null || echo 0)
  COUNT=$((COUNT + 1))
  echo "$COUNT" > "$RESTART_COUNT_FILE"

  if [[ "$COUNT" -le "$MAX_RESTART_ATTEMPTS" ]]; then
    launchctl kickstart -k "gui/$(id -u)/com.hci.api-server" 2>/dev/null || true
    sleep 15

    # Re-check
    HTTP_RETRY=$(curl -sf -o /dev/null -w "%{http_code}" --max-time 10 "$API_URL/health" 2>/dev/null || echo "000")
    if [[ "$HTTP_RETRY" == "200" ]]; then
      log "[monitor] ✓ API recovered after restart (attempt $COUNT)"
      echo "0" > "$RESTART_COUNT_FILE"
    else
      log "[monitor] ✗ API still down after restart attempt $COUNT"
      BODY="HCI AI API is DOWN. HTTP status was $HTTP_STATUS. Restart attempt $COUNT of $MAX_RESTART_ATTEMPTS failed. Check: launchctl list com.hci.api-server"
      send_alert "🚨 HCI AI API DOWN" "$BODY"
    fi
  else
    log "[monitor] ✗ Max restart attempts ($MAX_RESTART_ATTEMPTS) reached — manual intervention needed"
    BODY="HCI AI API has been DOWN for $COUNT consecutive monitor cycles. Automatic restarts exhausted. Manual intervention required. SSH to machine and check: launchctl list com.hci.api-server"
    send_alert "🚨 HCI AI API DOWN — INTERVENTION NEEDED" "$BODY"
  fi
else
  log "[monitor] ✓ API healthy (HTTP $HTTP_STATUS)"
  # Reset restart counter on success
  echo "0" > /tmp/hci_api_restart_count 2>/dev/null || true
fi

# ── 2. Docker Container Check ────────────────────────────────────────────────
log "[monitor] Checking Docker containers…"
EXPECTED_CONTAINERS=("hci_postgres" "hci_redis" "hci_minio" "hci_qdrant")
DOWN_CONTAINERS=()

for cname in "${EXPECTED_CONTAINERS[@]}"; do
  STATUS=$(docker inspect --format='{{.State.Status}}' "$cname" 2>/dev/null || echo "not_found")
  if [[ "$STATUS" != "running" ]]; then
    log "[monitor] ⚠ Container $cname is $STATUS"
    DOWN_CONTAINERS+=("$cname ($STATUS)")
  else
    log "[monitor] ✓ $cname running"
  fi
done

if [[ "${#DOWN_CONTAINERS[@]}" -gt 0 ]]; then
  log "[monitor] Attempting self-heal: docker compose up -d"
  ( cd "$HOME/HCI_AI_Operating_System/infrastructure" && docker compose up -d ) >>"$LOG_FILE" 2>&1
  sleep 10
  STILL_DOWN=()
  for entry in "${DOWN_CONTAINERS[@]}"; do
    cname="${entry%% *}"
    STATUS=$(docker inspect --format='{{.State.Status}}' "$cname" 2>/dev/null || echo "not_found")
    [[ "$STATUS" != "running" ]] && STILL_DOWN+=("$cname ($STATUS)")
  done
  if [[ "${#STILL_DOWN[@]}" -gt 0 ]]; then
    BODY="The following Docker containers are NOT running and self-heal (docker compose up -d) did not bring them back: ${STILL_DOWN[*]}. Manual check needed: cd ~/HCI_AI_Operating_System/infrastructure && docker compose up -d"
    send_alert "🚨 HCI AI Containers Down — self-heal failed" "$BODY"
  else
    log "[monitor] ✓ Self-heal recovered all containers"
  fi
fi

# ── 2b. ngrok Tunnel Check (GBT's only path in) ─────────────────────────────
log "[monitor] Checking ngrok tunnel…"
NGROK_STATUS=$(curl -sf --max-time 8 -o /dev/null -w "%{http_code}" http://localhost:4040/api/tunnels 2>/dev/null || echo "000")
if [[ "$NGROK_STATUS" != "200" ]]; then
  log "[monitor] ⚠ ngrok DOWN (local API check HTTP $NGROK_STATUS) — attempting restart"
  launchctl kickstart -k "gui/$(id -u)/com.ngrok.hci" 2>/dev/null || true
  sleep 10
  NGROK_RETRY=$(curl -sf --max-time 8 -o /dev/null -w "%{http_code}" http://localhost:4040/api/tunnels 2>/dev/null || echo "000")
  if [[ "$NGROK_RETRY" == "200" ]]; then
    log "[monitor] ✓ ngrok recovered after restart"
  else
    BODY="ngrok tunnel is down (this is GBT/Chief Architect's only path into the system). Restart attempt failed. Manual check: launchctl kickstart -k gui/\$(id -u)/com.ngrok.hci"
    send_alert "🚨 HCI AI ngrok DOWN — GBT gateway unreachable" "$BODY"
  fi
else
  log "[monitor] ✓ ngrok tunnel healthy"
fi

# ── 2c. MCP Server Check ─────────────────────────────────────────────────────
log "[monitor] Checking mcp-server…"
MCP_STATUS=$(curl -s --max-time 8 -o /dev/null -w "%{http_code}" http://localhost:8080/ 2>/dev/null || echo "000")
if [[ "$MCP_STATUS" == "000" ]]; then
  log "[monitor] ⚠ mcp-server DOWN — attempting restart"
  launchctl kickstart -k "gui/$(id -u)/com.hci.mcp-server" 2>/dev/null || true
  sleep 10
  MCP_RETRY=$(curl -s --max-time 8 -o /dev/null -w "%{http_code}" http://localhost:8080/ 2>/dev/null || echo "000")
  if [[ "$MCP_RETRY" != "000" ]]; then
    log "[monitor] ✓ mcp-server recovered after restart"
  else
    BODY="mcp-server (port 8080) is not responding at all. Restart attempt failed. Manual check: launchctl kickstart -k gui/\$(id -u)/com.hci.mcp-server"
    send_alert "🚨 HCI AI mcp-server DOWN" "$BODY"
  fi
else
  log "[monitor] ✓ mcp-server responding (HTTP $MCP_STATUS)"
fi

# ── 3. Disk Usage Check ──────────────────────────────────────────────────────
log "[monitor] Checking disk usage…"
DISK_PCT=$(df -h / | awk 'NR==2 {gsub(/%/,"",$5); print $5}')
log "[monitor] Disk usage: ${DISK_PCT}%"

if [[ "${DISK_PCT:-0}" -ge "$DISK_THRESHOLD" ]]; then
  log "[monitor] ⚠ Disk usage critical: ${DISK_PCT}%"
  DETAILS=$(df -h / | tail -1)
  BODY="Disk usage is at ${DISK_PCT}% (threshold: ${DISK_THRESHOLD}%). Details: $DETAILS. Free up space or expand storage."
  send_alert "⚠ HCI AI Disk Space Critical (${DISK_PCT}%)" "$BODY"
fi

# ── 4. Trim log (keep last 1000 lines) ───────────────────────────────────────
if [[ -f "$LOG_FILE" ]]; then
  tail -1000 "$LOG_FILE" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "$LOG_FILE"
fi

log "[monitor] ✓ Monitor cycle complete"

# --- Monitored-Drive write detector (2026-07-20, 275 Sunnyside incident) ---
# Read-only. Alerts Buck via Telegram if an external agent burst-writes/reorganizes
# a monitored job Drive. Human-cadence writes are NOT flagged.
DET_OUT="$(cd "$(dirname "$0")/.." && python3 scripts/monitored_drive_write_detector.py 2>/dev/null)"
if [ $? -eq 2 ]; then
  MSG="ALERT: external agent wrote to a MONITORED Drive. $(echo "$DET_OUT" | python3 -c 'import sys,json;d=json.load(sys.stdin);print("; ".join(f"{x[\"drive\"]}: {x[\"reason\"]}" for x in d["findings"]))' 2>/dev/null)"
  curl -s -X POST http://localhost:8000/gateway/telegram/send -H "X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6" -H "Content-Type: application/json" -d "$(python3 -c 'import json,sys;print(json.dumps({"text":sys.argv[1],"agent":"claude_code"}))' "$MSG")" >/dev/null 2>&1
fi

# --- GBT Activity & Performance Monitor (2026-07-20) — hourly, read-only ---
# Records per-team-member GBT/manual Drive activity + quality score to gbt_activity_log.
if [ "$(date +%M)" -lt 5 ]; then
  (cd "$(dirname "$0")/.." && python3 scripts/gbt_activity_monitor.py --hours 2 >/dev/null 2>&1)
fi

# --- Governing Knowledge Register refresh (2026-07-20) — daily, read-only ---
if [ "$(date +%H%M)" = "0705" ]; then
  (cd "$(dirname "$0")/.." && python3 scripts/governing_knowledge_register.py >/dev/null 2>&1)
fi

# ── Dead-man switch: P0s unacknowledged past deadline -> Telegram Buck ─────────
# (built 2026-07-21 - independent of any agent session; catches the read-gap that
#  silently swallowed P0s. Self-dedups + re-alerts every 2h while still open.)
log "[monitor] Running dead-man switch (unacked P0 check)…"
python3 "$HOME/HCI_AI_Operating_System/03_Source_Code/scripts/dead_man_switch.py" >> "$LOG_FILE" 2>&1 || log "[WARN] dead-man switch errored"


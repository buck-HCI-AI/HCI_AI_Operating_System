#!/bin/bash
# HCI AI OS — Startup Verification
# Run this after any restart/reboot to confirm everything came back up cleanly.
# Everything below SHOULD already auto-recover on its own (Docker Desktop autostart +
# unless-stopped containers + launchd RunAtLoad/KeepAlive) — this script just proves it,
# and tells you exactly what to do if any single piece didn't.

set -uo pipefail
PASS="✅"; FAIL="❌"
ok=0; bad=0

check() {
  local label="$1" cmd="$2" fix="$3"
  if eval "$cmd" >/dev/null 2>&1; then
    echo "$PASS $label"
    ok=$((ok+1))
  else
    echo "$FAIL $label — fix: $fix"
    bad=$((bad+1))
  fi
}

echo "=== Docker containers ==="
check "postgres"  "docker ps --format '{{.Names}}' | grep -qx hci_postgres" "docker compose up -d"
check "redis"     "docker ps --format '{{.Names}}' | grep -qx hci_redis"    "docker compose up -d"
check "qdrant"    "docker ps --format '{{.Names}}' | grep -qx hci_qdrant"   "docker compose up -d"
check "minio"     "docker ps --format '{{.Names}}' | grep -qx hci_minio"    "docker compose up -d"
check "n8n"       "docker ps --format '{{.Names}}' | grep -qx n8n"         "docker start n8n"

echo ""
echo "=== launchd services ==="
check "API server"   "launchctl print gui/\$(id -u)/com.hci.api-server 2>/dev/null | grep -q 'state = running'" \
     "launchctl kickstart -k gui/\$(id -u)/com.hci.api-server"
check "MCP server"   "launchctl print gui/\$(id -u)/com.hci.mcp-server 2>/dev/null | grep -q 'state = running'" \
     "launchctl kickstart -k gui/\$(id -u)/com.hci.mcp-server"
check "ngrok"        "launchctl print gui/\$(id -u)/com.ngrok.hci 2>/dev/null | grep -q 'state = running'" \
     "launchctl kickstart -k gui/\$(id -u)/com.ngrok.hci"

echo ""
echo "=== Live health checks ==="
check "API responding"       "curl -sf -m 5 http://localhost:8000/gateway/health"          "see API server fix above"
check "n8n responding"       "curl -sf -m 5 -o /dev/null http://localhost:5678"             "docker restart n8n (clears the recurring SQLite I/O error)"
check "ngrok tunnel live"    "curl -sf -m 8 https://speculate-armband-retinal.ngrok-free.dev/gateway/health" "see ngrok fix above; URL is static on free plan"

echo ""
echo "=== Architecture inbox ==="
INBOX_COUNT=$(ls -1 "$(dirname "$0")/../../Architecture/Agent_Handoff/Inbox/" 2>/dev/null | wc -l | tr -d ' ')
if [ "$INBOX_COUNT" = "0" ]; then
  echo "$PASS Inbox empty"
else
  echo "⚠️  $INBOX_COUNT unprocessed handoff(s) in Architecture/Agent_Handoff/Inbox/ — read these before other work"
fi

echo ""
echo "======================================"
echo "PASS: $ok   FAIL: $bad"
if [ "$bad" -gt 0 ]; then
  echo "Not clean — see fixes above."
  exit 1
else
  echo "Clean startup — everything auto-recovered."
fi

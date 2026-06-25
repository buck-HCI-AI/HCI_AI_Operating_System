#!/bin/bash
# HCI Morning Startup — runs at Mac login via launchd
# Order: Houzz sync → HubSpot sync → WF-007 bid leveling → WF-003 morning brief

LOG="/tmp/hci_morning_startup.log"
PYTHON="/usr/local/bin/python3"
WF_DIR="/Users/buckadams/HCI_AI_Operating_System/03_Source_Code/workflows"
INT_DIR="/Users/buckadams/HCI_AI_Operating_System/03_Source_Code/integrations"

echo "$(date): Morning startup triggered" >> "$LOG"

# Wait for FastAPI (up to 60s — Docker may still be coming up)
for i in {1..30}; do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo "$(date): API ready after $((i*2))s" >> "$LOG"
        break
    fi
    sleep 2
done

# Wait for n8n
for i in {1..15}; do
    if curl -sf http://localhost:5678/healthz > /dev/null 2>&1; then
        echo "$(date): n8n ready after $((i*2))s" >> "$LOG"
        break
    fi
    sleep 2
done

# Step 1 — Houzz sync (read daily logs + schedule from Houzz Pro)
echo "$(date): Starting Houzz sync..." >> "$LOG"
cd "$WF_DIR" && PYTHONPATH="$INT_DIR:$WF_DIR" $PYTHON sync_houzz.py >> "$LOG" 2>&1
echo "$(date): Houzz sync done" >> "$LOG"

# Step 2 — HubSpot sync (read all deals + notes + tasks)
echo "$(date): Starting HubSpot sync..." >> "$LOG"
cd "$WF_DIR" && PYTHONPATH="$INT_DIR:$WF_DIR" $PYTHON sync_hubspot.py >> "$LOG" 2>&1
echo "$(date): HubSpot sync done" >> "$LOG"

# Step 3 — WF-007 bid leveling via n8n
echo "$(date): Triggering bid leveling..." >> "$LOG"
curl -sf -X POST http://localhost:5678/webhook/bid-leveling \
  -H "Content-Type: application/json" \
  -d '{"projects": "all"}' >> "$LOG" 2>&1
echo "" >> "$LOG"
sleep 5

# Step 4 — Morning brief email
echo "$(date): Sending morning brief..." >> "$LOG"
curl -sf -X POST http://localhost:8000/workflows/wf003/morning-brief \
  -H "Content-Type: application/json" \
  -d '{"send": true}' >> "$LOG" 2>&1
echo "" >> "$LOG"

echo "$(date): Morning startup complete" >> "$LOG"

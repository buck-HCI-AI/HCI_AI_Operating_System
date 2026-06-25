#!/bin/bash
# HCI Morning Startup — runs at Mac login via launchd
# 1) Waits for API and n8n to be ready
# 2) Fires WF-007 bid leveling (n8n)
# 3) Fires WF-003 morning brief email

LOG="/tmp/hci_morning_startup.log"
echo "$(date): Morning startup triggered" >> "$LOG"

# Wait for FastAPI (up to 60s — Docker may still be coming up)
for i in {1..30}; do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo "$(date): API ready after ${i}s" >> "$LOG"
        break
    fi
    sleep 2
done

# Wait for n8n (up to 30s)
for i in {1..15}; do
    if curl -sf http://localhost:5678/healthz > /dev/null 2>&1; then
        echo "$(date): n8n ready after ${i}s" >> "$LOG"
        break
    fi
    sleep 2
done

# Fire WF-007 bid leveling via n8n webhook
echo "$(date): Triggering bid leveling..." >> "$LOG"
curl -sf -X POST http://localhost:5678/webhook/bid-leveling \
  -H "Content-Type: application/json" \
  -d '{"projects": "all"}' >> "$LOG" 2>&1
echo "" >> "$LOG"

# Brief pause so bid leveling can start processing
sleep 5

# Fire WF-003 morning brief email
echo "$(date): Sending morning brief..." >> "$LOG"
curl -sf -X POST http://localhost:8000/workflows/wf003/morning-brief \
  -H "Content-Type: application/json" \
  -d '{"send": true}' >> "$LOG" 2>&1
echo "" >> "$LOG"

echo "$(date): Morning startup complete" >> "$LOG"

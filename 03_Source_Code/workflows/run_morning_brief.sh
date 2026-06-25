#!/bin/bash
# HCI Morning Startup — runs at Mac login + 7 AM via launchd
#
# Sequence (in order):
#   1. Houzz sync      — read daily logs + schedule from Houzz Pro
#   2. HubSpot sync    — read all deals, notes, tasks
#   3. Bid leveling    — WF-007 via n8n webhook
#   4. Inbox review    — read unread, move to folders, draft replies (WF-006)
#   5. Morning brief   — compile everything → email to buck@hendricksoninc.com

LOG="/tmp/hci_morning_startup.log"
PYTHON="/usr/local/bin/python3"
WF_DIR="/Users/buckadams/HCI_AI_Operating_System/03_Source_Code/workflows"
INT_DIR="/Users/buckadams/HCI_AI_Operating_System/03_Source_Code/integrations"
PYTHONPATH="$INT_DIR:$WF_DIR"

echo "" >> "$LOG"
echo "======================================" >> "$LOG"
echo "$(date): Morning startup triggered" >> "$LOG"
echo "======================================" >> "$LOG"

# Wait for FastAPI (up to 60s)
for i in {1..30}; do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo "$(date): API ready after $((i*2))s" >> "$LOG"
        break
    fi
    sleep 2
done

# Wait for n8n (up to 30s)
for i in {1..15}; do
    if curl -sf http://localhost:5678/healthz > /dev/null 2>&1; then
        echo "$(date): n8n ready after $((i*2))s" >> "$LOG"
        break
    fi
    sleep 2
done

# ── Step 1: Houzz sync ────────────────────────────────────────────────────────
echo "$(date): [1/5] Houzz sync..." >> "$LOG"
cd "$WF_DIR" && PYTHONPATH="$PYTHONPATH" $PYTHON sync_houzz.py >> "$LOG" 2>&1
echo "$(date): Houzz sync done" >> "$LOG"

# ── Step 2: HubSpot sync ──────────────────────────────────────────────────────
echo "$(date): [2/5] HubSpot sync..." >> "$LOG"
cd "$WF_DIR" && PYTHONPATH="$PYTHONPATH" $PYTHON sync_hubspot.py >> "$LOG" 2>&1
echo "$(date): HubSpot sync done" >> "$LOG"

# ── Step 3: Bid leveling ──────────────────────────────────────────────────────
echo "$(date): [3/5] Bid leveling..." >> "$LOG"
curl -sf -X POST http://localhost:5678/webhook/bid-leveling \
  -H "Content-Type: application/json" \
  -d '{"projects": "all"}' >> "$LOG" 2>&1
echo "" >> "$LOG"
echo "$(date): Bid leveling triggered — waiting 10s for n8n..." >> "$LOG"
sleep 10

# ── Step 4: Inbox review ──────────────────────────────────────────────────────
echo "$(date): [4/5] Inbox review..." >> "$LOG"
INBOX_RESULT=$(curl -sf -X POST http://localhost:8000/workflows/wf006/inbox-review \
  -H "Content-Type: application/json" \
  -d '{"max_emails": 30, "create_drafts": true}' 2>/dev/null)
echo "$(date): Inbox review done — $INBOX_RESULT" >> "$LOG"

# ── Step 5: Morning brief (with inbox result passed in) ───────────────────────
echo "$(date): [5/5] Sending morning brief..." >> "$LOG"
curl -sf -X POST http://localhost:8000/workflows/wf003/morning-brief \
  -H "Content-Type: application/json" \
  -d "{\"send\": true, \"inbox_result\": $INBOX_RESULT}" >> "$LOG" 2>&1
echo "" >> "$LOG"
echo "$(date): Morning startup complete" >> "$LOG"

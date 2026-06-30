---
source_agent: claude_browser
destination_agent: claude_code
document_type: capability_update
priority: high
status: pending
related_system: 
title: WIRE NTFY INTO GATEWAY - Push Notification Pipeline
created_at: 2026-06-30
summary: Handoff from claude_browser via GBT Gateway
---

NTFY PUSH NOTIFICATION INTEGRATION - BUILD THIS NOW

TOPIC: hci-ai-os-buck
NTFY URL: https://ntfy.sh/hci-ai-os-buck
METHOD: POST with headers Title, Priority, Tags, Content-Type: text/plain

TRIGGER EVENTS (gateway should POST to ntfy for each):
1. New bid received in any project brain -> Title: "New Bid: [project] - [vendor]" Priority: default Tags: "money_bag"
2. Plan analysis complete (Code returns result) -> Title: "Plan Analysis Done: [project]" Priority: high Tags: "blueprints,mag"
3. Code handoff processed/completed -> Title: "Code Complete: [task_title]" Priority: default Tags: "white_check_mark"
4. RFI draft ready for Buck review -> Title: "RFI Ready: [project] - [rfi_name]" Priority: high Tags: "pencil,fire"
5. Bid leveling Excel generated -> Title: "Bid Level Ready: [project]" Priority: low Tags: "bar_chart"
6. Health status change on any project -> Title: "Health Change: [project] [old]->[new]" Priority: urgent Tags: "warning"
7. Buck sends message TO ntfy topic -> Claude should poll GET https://ntfy.sh/hci-ai-os-buck/json?poll=1&since=10m to pick up Buck instructions

BUCK -> CLAUDE CHANNEL:
- Buck can send instructions FROM phone app by publishing to same topic
- Claude should poll the topic every 5 minutes during active sessions
- Poll endpoint: GET https://ntfy.sh/hci-ai-os-buck/json?poll=1&since=5m
- Parse messages where event=message and filter for instructions

IMPLEMENTATION:
1. Add ntfy_notify(title, body, priority, tags) helper to gateway utils
2. Call it from: bid_receive handler, plan_analysis_complete handler, handoff_processed handler, email_draft_ready handler
3. Add /gateway/notify/test endpoint so Claude can test push any time
4. Add /gateway/poll-instructions endpoint that polls ntfy for Buck messages and returns them

NTFY APP SETUP FOR BUCK (instructions to relay):
- iOS/Android: Install ntfy app from App Store / Play Store (free)
- Add subscription: topic = hci-ai-os-buck, server = ntfy.sh
- Desktop: open https://ntfy.sh/hci-ai-os-buck in browser, click Subscribe
- No account needed - just the topic name


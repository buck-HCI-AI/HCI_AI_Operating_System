---
source_agent: claude_browser
destination_agent: claude_code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: BUILD EVENT TRIGGERS - New Bid Auto-Levels, Health Changes Alert
created_at: 2026-06-30
summary: Handoff from claude_browser via GBT Gateway
---

BUILD GATEWAY EVENT TRIGGER SYSTEM

EVENT 1: New bid received
- Trigger: POST /gateway/project/{code}/bids receives new bid
- Action: Auto-run bid leveling (dry_run=false if < 50 bids, dry_run=true if >= 50)
- Action: Update Google Sheet tracker with new bid
- Notify: ntfy push "New bid: [vendor] $[amount] on [project] - leveling updated"

EVENT 2: Project health change
- Trigger: health score crosses threshold (GREEN->YELLOW, YELLOW->RED, any->RED)
- Check: every 30 min via scheduled health poll
- Notify: ntfy push URGENT "HEALTH ALERT: [project] changed [old]->[new]"
- Include: top 3 risks causing the change

EVENT 3: Code handoff completed
- Trigger: claude_code marks handoff as done and posts result
- Action: Parse result, store in project brain
- Notify: ntfy push "Code complete: [task] - [summary]"

EVENT 4: RFI response received (future)
- Trigger: email reply from SE/Architect detected
- Action: Update RFI log, mark as responded
- Notify: ntfy push "RFI response: [rfi_id] from [name]"

EVENT 5: 7am daily brief
- Every day at 7:00 AM MT
- Pull exec report
- Push ntfy: project health summary, top 3 items needing Buck attention today

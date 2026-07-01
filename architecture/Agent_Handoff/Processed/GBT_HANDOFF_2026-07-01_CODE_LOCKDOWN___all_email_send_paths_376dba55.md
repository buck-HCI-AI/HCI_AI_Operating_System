---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: CODE LOCKDOWN — all email send paths
created_at: 2026-07-01
summary: Handoff from ChatGPT via GBT Gateway
---

BC repo audit found these live send paths that must ALL be locked down NOW: (1) microsoft_graph.py send_email() — wrap it to always save draft + create approval queue item instead of calling /me/sendMail. (2) wf_report.py daily_field_report(send=True) — change default to send=False. Field reports go to draft, not sent. (3) wf_superintendent.py line 223 calls daily_field_report(send=True) — change to send=False. (4) wf003_morning_brief.py — morning brief to Buck should remain active ONLY if it was explicitly approved by Buck — confirm with Buck before re-enabling. Set send=False until confirmed. (5) wf_pm.py weekly_report(send_email=True) — set default to False. (6) gbt_gateway.py EmailSendRequest — already in prior directive, confirm disabled. (7) api/routers/workflows.py WF-003 send=True default — change to False. For every path: save draft, log the attempt, create approval queue item. Return list of every file changed and confirm all send paths are now draft-only.

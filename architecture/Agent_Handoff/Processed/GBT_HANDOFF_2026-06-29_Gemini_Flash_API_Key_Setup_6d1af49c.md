---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: Gemini Flash API Key Setup
created_at: 2026-06-29
summary: Handoff from ChatGPT via GBT Gateway
---

Reference: f1382aed

Buck has the Gemini API key. Code to execute the following:

1. Run Desktop/Add_Gemini_Key.command on Buck's Mac at /Users/buckadams — Buck will paste the key when prompted.
2. Confirm GEMINI_API_KEY is written to /Users/buckadams/HCI_AI_Operating_System/.env.
3. Confirm plan_reader.py tools/plan_reader.py accepts --model gemini flag and Gemini Flash is wired as the free automated pipeline model.
4. Confirm gateway endpoint POST /gateway/plan/read accepts model=gemini param.
5. Update LIVE_PROJECT_STATE.md to reflect Gemini Flash active as free-tier plan reader.

Model routing:
- Gemini Flash = automated pipeline free
- Sonnet 4.6 = gateway default
- Opus = on-demand Buck-triggered only

Ref f1382aed from inbox.

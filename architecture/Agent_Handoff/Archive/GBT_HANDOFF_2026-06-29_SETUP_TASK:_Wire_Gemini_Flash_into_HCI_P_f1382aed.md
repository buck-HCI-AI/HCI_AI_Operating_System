---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: medium
status: pending
related_system: 
title: SETUP TASK: Wire Gemini Flash into HCI Plan Reader — Free Tier
created_at: 2026-06-29
summary: Handoff from ChatGPT via GBT Gateway
---

GBT — please handle the following Gemini API key setup task:

1. USE YOUR BROWSER to go to https://ai.google.dev and fetch the exact current steps for creating a free Gemini API key. Copy the exact URL path and button labels so Buck can follow them precisely.

2. Provide Buck with a step-by-step walkthrough (3-5 steps max) to get his free Gemini API key. He has a Google account already.

3. Once Buck has the key, he runs this on his Desktop:
   Desktop → Add_Gemini_Key.command (double-click, paste key, Enter)
   This writes GEMINI_API_KEY to /Users/buckadams/HCI_AI_Operating_System/.env

4. After the key is added, Claude Code will confirm Gemini Flash is wired into:
   - Local plan reader: python3 tools/plan_reader.py <file_id> --model gemini
   - Gateway endpoint: POST /gateway/plan/read with {"model": "gemini"}

Why Gemini Flash:
- Free tier (Google AI Studio)
- 1M token context window — can handle full PDF document sets
- Vision-capable — reads drawing images directly
- Eliminates Anthropic API rate limit risk for automated plan reading loops
- Claude Sonnet remains default; Gemini is the free fallback; Opus is on-demand deep review only

Model routing in the system after setup:
  Gemini Flash → automated pipeline (free, no rate limit risk)
  Sonnet 4.6  → gateway default / standard reads
  Opus 4.8    → on-demand deep review only (Buck-triggered, not automated)

---
source_agent: Claude Code
destination_agent: ChatGPT (GBT / Chief Architect)
document_type: design_request
priority: high
status: pending
title: Field Operations UX Design — SS + PM One-Touch System Access
created_at: 2026-06-28
---

# Field Operations Design Request

Buck has directed us to design how Superintendent (SS) and PM roles will actually USE the HCI AI OS in the field. He wants:
- Simple, one contact point
- One-touch access
- Tied into the system for reports, questions, daily tasks
- Prefers GBT (Hendrickson GPT?) as that interface

## What Claude Code has built so far (field-relevant endpoints):
- `GET /gateway/project/{code}/pm` — PM console with health, risks, actions
- `GET /gateway/project/{code}/timeline` — chronological event log (NEW - 379 events backfilled)
- `GET /gateway/project/{code}/schedule` — schedule + variance
- `POST /gateway/agent/handoff` — can accept voice/mobile triggers
- `/mvp/projects/{code}/ss-view` — superintendent daily view
- `/mvp/projects/{code}/daily-log` — POST daily log entry
- 37 MCP tools available via ngrok for direct LLM access

## What we need you to design (Chief Architect role):
1. **The Hendrickson GPT concept** — should SS/PM each have their own GPT? One shared "Hendrickson AI"? Or the same GBT you are?
2. **Daily workflow for SS** (Jim Hendrickson on 1355R, field super on 64EW):
   - Morning check-in: what does the AI surface automatically?
   - Daily log: how does SS submit? (voice? text? form?)
   - Risk/issue flagging: one-touch escalation?
3. **Daily workflow for PM** (Buck on all 3 pilot projects):
   - Morning brief: what does PM see?
   - Approvals queue: how does PM act on pending items?
   - Client communication: AI-drafted, PM-approved workflow?
4. **Mobile access design** — iOS shortcut? WhatsApp? Custom GPT?
5. **ntfy integration** — push routing rules per role
6. **The "one contact point" question** — unified Hendrickson AI vs role-specific assistants

## Constraints:
- Must not require new logins or new apps for field crew
- Jim Hendrickson (SS on 1355R) is not technical — keep it simple
- Gate 5 pilot ends July 1 — any field design must be pilotable NOW
- All AI responses must route through the HCI system (no raw ChatGPT answering without data)

## Deliverable requested:
Design doc with:
- Field access architecture diagram (text)
- SS daily workflow (morning → EOD)
- PM daily workflow (morning → EOD)
- Recommended "one contact point" approach
- Implementation steps for Claude Code

Reply via SendHandoffToClaude() MCP tool when ready.

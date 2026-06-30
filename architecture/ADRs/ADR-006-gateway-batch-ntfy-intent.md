---
id: ADR-006
title: Gateway Batch, ntfy Push, and Intent Router Extensions
status: accepted
date: 2026-06-29
author: Claude Code (session 2026-06-29)
tags: [gateway, ntfy, intent, batch, notifications]
---

## Context

The GBT gateway was hitting a 3-call-per-message limit in ChatGPT. There was no push notification channel from the OS to Buck's phone. Natural-language routing of messages to OS actions was missing.

## Decision

Added four new endpoint groups to `api/routers/gbt_gateway.py`:

1. **`POST /gateway/batch`** — Execute N gateway operations in a single HTTP call. Eliminates GBT 3-call limit. Supported ops: `ntfyPush`, `emailDraft`, `sendHandoff`, `bidLevel`, `dbQuery`. Returns `{ok, failed, results[]}` with auto-ntfy summary.

2. **`POST /gateway/notify/test` + ntfy helpers** — Push notifications to Buck's phone via `ntfy.sh/hci-ai-os-buck`. ASCII-safe title encoding to handle Unicode in HTTP headers. Priority and tag support.

3. **`GET /gateway/poll-instructions`** — Polls ntfy for messages from Buck in the last 5 minutes. Enables Buck-to-OS voice/text commands via ntfy.

4. **`POST /gateway/intent/route`** — Regex-based natural language → OS action router. Maps phrases like "status on 64EW" → `{intent: status, project: 64EW}`. 9 intent patterns implemented.

5. **`GET /gateway/project/{code}/plans`** — Scans project drawings folder via direct Drive API call. Returns files classified by discipline (Architectural, Structural, MEP, Civil, Geotechnical).

## Constraints

- Plans endpoint uses direct Drive API calls (not `http://localhost:8000/...`) to avoid uvicorn self-referential deadlock with single async worker
- ntfy titles must be ASCII-encoded (requests library cannot encode unicode as latin-1 in HTTP headers)
- All endpoints follow `_response()` envelope — GBT depends on the standard structure

## Consequences

- Service count: 40 → 43 (batch, notify-test, poll-instructions, intent-route, project-plans, shared-drive-id counted as new services)
- GBT can now execute complex multi-step actions in one call
- Buck receives real-time push notifications for key OS events
- Architecture Freeze v1.0 service count updated from 40 to 43

---
source_agent: claude_browser
destination_agent: claude_code
document_type: capability_update
priority: high
status: pending
related_system: 
title: NTFY TWO-WAY CHANNEL - Buck Can Message Claude via Phone
created_at: 2026-06-30
summary: Handoff from claude_browser via GBT Gateway
---

BUILD NTFY TWO-WAY COMMUNICATION CHANNEL

CURRENT STATE: ntfy is one-way only — gateway pushes TO Buck's phone.
GOAL: Buck can send messages FROM his phone and the system receives + acts on them.

HOW NTFY PUBLISH-FROM-PHONE WORKS:
- Buck opens ntfy app on phone
- Taps the hci-ai-os-buck topic
- Taps the publish/send icon (pencil icon in top right of topic view)
- Types his message and hits send
- That message posts to ntfy.sh/hci-ai-os-buck as a new notification

WHAT NEEDS TO BE BUILT:
1. Gateway polling endpoint: GET /gateway/ntfy/poll
   - Polls https://ntfy.sh/hci-ai-os-buck/json?poll=1&since=Xm (last X minutes)
   - Returns any messages Buck published to the topic
   - Filters out messages sent BY the gateway (source tag = "gateway") so we don't echo ourselves
   - Returns: [{id, message, title, time, from: "buck"}]

2. Gateway webhook listener (better than polling): 
   - Register ntfy webhook: POST to ntfy.sh to subscribe our gateway URL as webhook
   - ntfy will POST to https://speculate-armband-retinal.ngrok-free.dev/gateway/ntfy/inbound whenever Buck sends a message
   - Gateway receives it, parses intent, routes to appropriate handler

3. Intent routing for Buck's phone messages:
   - "status" or "what's up" -> pull exec report, push summary back to ntfy
   - "bids for [project]" -> pull bid data, push to ntfy  
   - "run plans [project]" -> queue plan analysis handoff to Code
   - "level bids [project]" -> trigger bid leveling run
   - "rfi status [project]" -> pull open RFI list
   - Any other message -> forward to GBT HCI Chief Architect as a directive

4. GBT response loop:
   - When Buck message is forwarded to GBT, GBT processes and responds
   - GBT response gets pushed back to ntfy so Buck sees it on his phone
   - This creates: Buck phone -> ntfy -> gateway -> GBT -> ntfy -> Buck phone

NTFY DETAILS:
- Topic: hci-ai-os-buck
- Server: ntfy.sh (public, free)
- Poll URL: https://ntfy.sh/hci-ai-os-buck/json?poll=1&since=10m
- Webhook registration: POST https://ntfy.sh/hci-ai-os-buck with X-Actions header

Build /gateway/ntfy/poll first (5 minute job), then webhook (more robust long term).

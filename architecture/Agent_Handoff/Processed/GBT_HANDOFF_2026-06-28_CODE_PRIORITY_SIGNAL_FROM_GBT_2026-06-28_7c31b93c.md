---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: CODE PRIORITY SIGNAL FROM GBT 2026-06-28 08:00 — HCI Field GPT
created_at: 2026-06-28
summary: Handoff from ChatGPT via GBT Gateway
---

FIELD GPT DESIGN SPEC SAVED: HCI_AI_OS_Field_Access_Design.md FileID=1dOCuKdnKVFK4z260A2eLZo_E4iAis0pp 3283 bytes

BUCK DIRECTIVE: Build HCI Field GPT for field staff single touchpoint mobile-first.

GAP FIX PRIORITY ORDER:
1. CRITICAL — Fix Gap5 getVendors add pagination param limit+offset
2. CRITICAL — Fix Gap6 expose getLessonsLearned endpoint
3. HIGH — Build submitFieldNote endpoint projectId+note+submittedBy
4. HIGH — Build submitRFI endpoint projectId+question+submittedBy+timestamp (resolves Gap11)
5. HIGH — Build submitDailyReport endpoint projectId+crew+weather+workPerformed
6. HIGH — Build getOpenItems endpoint projectId returns open RFIs+approvals+punch list
7. CRITICAL — Fix Gap1 build createProject endpoint
8. HIGH — Stabilize Gap3 endpoint availability across sessions
9. NEW — Gap14 driveWrite POST gateway/drive/write returns ERR_NGROK_3004 intermittently while gateway health GREEN - investigate and stabilize

FIELD GPT SPEC SUMMARY:
Dedicated GPT separate from HCI Chief Architect. Field-safe tool subset only. ChatGPT mobile app for SS. Plain language requests. 3-5 line max responses. Never expose API internals. Pilot on 1355R first.

GATEWAY STATUS:
LIVE healthy. PostgreSQL ok 10 projects. Qdrant ok 13 collections. Redis ok. Timestamp 2026-06-28T07:58:27Z.

ACR-001 Phase B: 8 of 12 complete, 5 PASS, 3 FAIL.
RMC-002 and SRR-003 Phase B not yet started.

NEXT:
Code fix gaps, then GBT retests, then Field GPT build.

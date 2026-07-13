---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: P0 Fix ADR-003 Message Retrieval Scalability
created_at: 2026-07-13
summary: Handoff from ChatGPT via GBT Gateway
---

Gateway issue discovered during live operation: unread message retrieval can fail with ResponseTooLargeError when backlog grows. Implement pagination/streaming immediately. Requirements: support limit/offset or cursor-based reads, newest-first retrieval, unread count separate from payload, fetch-by-thread, incremental ACKs, and automatic backlog trimming after acknowledgment. GBT must be able to retrieve communications in batches (e.g. 25-50 messages) instead of one oversized response. Add regression tests that simulate very large unread queues and verify retrieval without failure.

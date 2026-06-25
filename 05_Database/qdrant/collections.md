# HCI AI — Qdrant Collections

Vector store for organizational memory. Qdrant stores meaning and context.

## Collections

### `project_memory`
Every project event, decision, issue, and outcome.
- **Payload fields:** project_id, project_name, event_type, date, description, source
- **Use:** "What issues came up at 64 Eastwood?" → semantic search → context

### `vendor_memory`
Vendor interactions, bid history, performance, relationships.
- **Payload fields:** vendor_id, company_name, csi_division, project_id, date, outcome, notes
- **Use:** "Who are our best masonry subs?" → semantic search → ranked vendor list

### `meeting_memory`
Meeting transcripts, summaries, action items.
- **Payload fields:** project_id, meeting_type, date, attendees, summary
- **Use:** "What did we discuss with the owner last month?" → retrieval

### `lessons_learned`
Failures, successes, warnings, and recommendations across all projects.
- **Payload fields:** project_id, category, outcome, title, description, recommendation
- **Use:** "What went wrong with masonry on past projects?" → institutional wisdom

### `bid_memory`
Bid history, amounts, vendor performance, market intelligence.
- **Payload fields:** vendor_id, csi_division, project_id, amount, outcome, notes, date
- **Use:** "What does concrete typically cost for a project this size?" → benchmarking

### `constitution_memory`
SOPs, standards, the HCI AI constitution, engineering docs.
- **Payload fields:** book_number, title, section, content
- **Use:** "What's the SOP for bid leveling?" → retrieval

### `photo_memory` (future)
Jobsite photos with AI-extracted descriptions.
- **Payload fields:** project_id, date, description, location, tags

## Embedding Model
- **Model:** `text-embedding-3-small` (OpenAI) or local equivalent
- **Dimensions:** 1536
- **Distance:** Cosine

## Retrieval Pipeline
```
Question
  → Extract metadata filters (project, date range, vendor, CSI division)
  → Qdrant semantic search (filtered)
  → Postgres lookup for full records
  → Context builder (top 5 results)
  → Rerank
  → AI response with citations
```

## Status
- [ ] Qdrant container running (see docker-compose.yml)
- [ ] Collections created
- [ ] Embedding pipeline built
- [ ] HubSpot contacts ingested → vendor_memory
- [ ] Bid history ingested → bid_memory
- [ ] SOPs ingested → constitution_memory

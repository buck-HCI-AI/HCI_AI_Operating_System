# HCI AI Strategic Backlog
*Long-Term Vision — BTW-4 through BTW-10*
*Queued: 2026-06-27 | Source: The long.docx*

---

## Long-Term Discovery Flow Vision

```
Browser Discovery
        ↓
Platform Intelligence Document
        ↓
Automatic Ingest
        ↓
Claude Code indexes it
        ↓
Architecture Handbook updates
        ↓
Implementation backlog updates
        ↓
Executive Dashboard reflects new opportunities
```

This flow becomes the operating model once BTW-10 (Continuous Discovery Engine) is complete.

---

## Backlog Queue

### BTW-4 — Project Brain: Extended Memory
**Mission:** BTW-004 | **Priority:** HIGH | **Status:** OPEN

**Already built (pre-delivered):**
- `services/project_brain` — health, intelligence, risks, snapshot endpoints ✅
- `project_brain_snapshots` table ✅
- Cross-project intelligence aggregation ✅
- PROJECT_BRAIN_SPEC.md ✅

**Remaining to build:**
- Event Timeline — chronological log of project events (milestones, risks, decisions, changes)
- Conversation Memory — AI interaction history per project (what was asked, what was decided)
- Document Relationships — link documents to the decisions/risks/change orders they drove
- Daily Project Summary auto-generation (scheduled, not on-demand)

**Handbook:** Volume III (Project Brain) — implementation refs ready; philosophy pending CA

---

### BTW-5 — Role Intelligence: 8 Roles
**Mission:** BTW-005 | **Priority:** HIGH | **Status:** OPEN

**Already built (pre-delivered):**
- Superintendent Daily Console (`/superintendent/{id}/today`) ✅
- Project Manager Weekly Console (`/pm/{id}/weekly`) ✅
- Leadership Dashboard (`/leadership/dashboard`) ✅
- Executive Morning Brief (`/executive/morning-brief`) ✅

**Remaining 5 roles to define + build:**

| Role | Dashboard | Daily Workflow | Notifications | AI Assist | KPIs |
|------|-----------|----------------|---------------|-----------|------|
| Owner (Buck) | Company-wide command | Morning brief + approvals | All critical alerts | Decision support | Revenue, margin, risk |
| Office | Admin queue | Pending items, AP/AR | Approval requests | Document prep | Turnaround time |
| Accounting | Financial health | Invoices, draws, cash flow | Budget alerts | Cost code tagging | Cash position |
| Client | Project status | Milestone updates | Change order alerts | Q&A | Schedule, budget vs contract |
| Trade Partner | My work queue | Today's scope, RFIs | Inspection holds | Scope clarification | On-time delivery |

**Handbook:** Volume IV (Role Intelligence) — philosophy pending CA for all 5 new roles

---

### BTW-6 — Executive Command Center: Weekly/Monthly Reports
**Mission:** BTW-006 | **Priority:** MEDIUM | **Status:** OPEN

**Already built (pre-delivered):**
- Executive Mission Control — 11 sections ✅
- Morning Brief (daily, 6AM push) ✅
- Leadership Dashboard ✅
- All executive endpoints ✅

**Remaining to build:**
- Weekly Executive Report (n8n workflow `AUTO-WEEKLY-EXEC`) — company performance summary, highlights, decisions made, upcoming decisions
- Monthly Business Review (n8n `AUTO-MONTHLY-REVIEW`) — financials, pipeline, client satisfaction, team performance, AI ROI
- Both delivered via ntfy + stored as reports in the platform

**Handbook:** Volume V (Executive Intelligence) — implementation refs ready; philosophy pending CA

---

### BTW-7 — Superintendent Workspace: Field Enhancements
**Mission:** BTW-007 | **Priority:** MEDIUM | **Status:** OPEN

**Already built (pre-delivered):**
- Today's priorities, schedule, safety topics, crew, tasks, daily log ✅
- All from `houzz_schedule_items`, `houzz_tasks`, `houzz_subcontractors` ✅

**Remaining to build (requires Houzz data flowing):**
- Photo documentation — `houzz_files` by project/date (requires Houzz extraction first)
- Delivery tracking — expected PO deliveries (`houzz_purchase_orders`)
- Inspection scheduling — inspection tasks from schedule items
- Material tracking — purchase order status per trade
- Voice notes — transcription endpoint → daily log injection

**Blocker:** All field enhancements requiring Houzz data depend on Houzz Browser Extraction (15 min × 3 projects).

---

### BTW-8 — PM Workspace: Client Comms + AI Action List
**Mission:** BTW-008 | **Priority:** MEDIUM | **Status:** OPEN

**Already built (pre-delivered):**
- Risks, overdue items, budget health, procurement status, decision queue ✅

**Remaining to build:**
- Client communication queue — outstanding items needing client response, organized by project + urgency
- AI-generated ranked action list — `priority_score = (severity × urgency × financial_impact) / days_remaining`, top 10 actions for the PM's day
- Both additions to existing `/pm/{id}/weekly` response

---

### BTW-9 — Company Knowledge Graph
**Mission:** BTW-009 | **Priority:** HIGH | **Status:** OPEN

**Nothing pre-built** — this is a new capability.

**Foundation available:**
- Qdrant vector search (13 collections) ✅
- `background_learning_records` (406 records) ✅
- All entity tables (projects, contacts, vendors, subcontractors, documents) ✅

**To build:**
```
knowledge_graph service
    ├── Entity nodes: projects, clients, employees, vendors, subs, materials
    ├── Relationship edges: worked_on, supplied_to, installed, inspected, decided
    ├── Semantic search: "similar waterproofing issues" → Qdrant cosine similarity
    └── Natural language queries: "Who installed product X before?" → graph traversal + LLM
```

**Enables queries like:**
- "Show me every project where Vendor X worked"
- "Find similar waterproofing issues across all projects"
- "Who has installed this product before?"
- "What decisions were made on rainy days in 2025?"

**Handbook:** Vol IX (Roadmap) — depends on CA authorship; Vol II — intelligence model philosophy needed

---

### BTW-10 — Continuous Discovery Engine
**Mission:** BTW-010 | **Priority:** HIGH | **Status:** OPEN

**Architecture designed** — the Browser Agent Standard and connector framework define this flow. The continuous discovery piece (automatic triggering) is not yet built.

**To build:**
```
Browser Claude (Research Arm)
    ├── Scheduled scans: Houzz changes (nightly), HubSpot changes (hourly)
    ├── Change detection: compare last-known state vs current
    ├── Platform Intelligence Document: canonical JSON per BTW standard
    └── POST /api/v1/services/connectors/{name}/ingest → auto-ingest
            ↓
Claude Code Indexing
    ├── Architecture Sync Engine: /architecture-sync/review-engine
    ├── Handbook updates: affected volumes flagged
    └── Implementation backlog: new items added to missions table
            ↓
Executive Dashboard
    └── New opportunities surface in Mission Control / Morning Brief
```

**Blockers:**
- Houzz Browser extraction access (manual step required once)
- n8n workflow scheduling for browser triggers
- Change detection logic (delta between extractions)

---

## Implementation Sequence Recommendation

Based on dependencies and pre-built work:

| Order | BTW | Reason |
|-------|-----|--------|
| 1 | BTW-4 | Lowest lift — 3 extensions to existing service; no external deps |
| 2 | BTW-8 | 2 additions to PM console; no external deps |
| 3 | BTW-6 | 2 n8n workflows; no external deps |
| 4 | BTW-7 | Requires Houzz data — blocked until extraction runs |
| 5 | BTW-5 | 5 new role consoles — depends on knowledge of how each role operates (CA authorship Vol I helps) |
| 6 | BTW-9 | Knowledge Graph — large build, depends on data flowing |
| 7 | BTW-10 | Continuous Discovery — depends on all connectors working + BTW-9 |

**Immediate unblocked work (no dependencies):** BTW-4 → BTW-8 → BTW-6

---

*Strategic Backlog maintained by Claude Code. Reviewed by Chief Architect (ChatGPT) + Buck Adams.*

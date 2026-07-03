# Event Bus Architecture
## HCI AI Operating System — Agent Communication Layer

**Authority:** Chief Architect Directive — Automation First (2026-06-27)  
**Owner:** Chris Hendrickson (Hendrickson Construction) | **HCI-AI Owner / PM & SS:** Buck Adams  
**Purpose:** Eliminate Buck as the message bus between agents.

---

## The Problem This Solves

Without a defined event bus, Buck becomes the relay:
> "Tell Claude Code that Browser Claude finished" → manual coordination → delays → friction

**This document defines how agents communicate directly**, using files, webhooks, and the database as the shared event surface.

---

## Communication Channels

### Channel 1 — File-Based State (Primary)

All agents share one repo. State changes are communicated by updating files.

| File | Purpose | Who Writes | Who Reads |
|---|---|---|---|
| `MISSION_QUEUE.md` | Active missions and blockers | Any agent | All agents |
| `AI_TEAM/06_NEXT_SESSION.md` | Session handoff notes | Completing agent | Next agent |
| `AI_TEAM/07_BLOCKERS.md` | Current blockers | Any agent | All agents |
| `LIVE_PROJECT_STATE.md` | System truth | Claude Code | All agents, ChatGPT |
| `CURRENT_SPRINT.md` | Sprint board | Claude Code | All agents |
| `EXECUTIVE_INBOX.md` | Decisions for Buck | Any agent | Buck only |

**Polling cadence:** Each agent reads the shared files at session start. n8n reads daily for report generation.

---

### Channel 2 — FastAPI Webhooks (n8n Triggers)

n8n workflows are triggered via HTTP webhooks by Claude Code or other services.

| Webhook | Trigger | Action |
|---|---|---|
| `/gate-h-hubspot-write` | Claude Code detects HubSpot write needed | Queues for Buck approval |
| `/gate-g-pr-merge` | Browser Claude opens PR | Notifies Buck for merge approval |
| `/gate-e-client-comms` | Mining discovers client email needed | Routes to approval queue |
| `/gate-f-financial` | Financial action detected | Routes to Buck |

**How to trigger from Claude Code:**
```bash
curl -X POST http://localhost:5678/webhook/gate-h-hubspot-write \
  -H "Content-Type: application/json" \
  -d '{"action": "update_deal_stage", "deal_id": "331240861419", "stage": "closed_won"}'
```

---

### Channel 3 — PostgreSQL (Persistent Event Log)

The database serves as the persistent event log that survives session boundaries.

| Table | Event Type | Producer | Consumer |
|---|---|---|---|
| `approval_queue` | Human approval needed | Any miner/agent | Buck → Claude Code |
| `mining_runs` | Miner completed | Mining Engine | Monitoring scripts |
| `import_metrics` | Data import occurred | Ingestion endpoints | HouzzMiner |
| `background_learning_records` | New entity discovered | Miners | Intelligence services |
| `decision_log` | Architecture decision made | Claude Code | ChatGPT |

**Checking for new events (Claude Code):**
```python
# New approval items since last check
SELECT * FROM approval_queue WHERE status='pending' AND created_at > NOW() - INTERVAL '24 hours'
ORDER BY priority DESC;
```

---

### Channel 4 — API Endpoints (Agent-to-Agent)

Agents call FastAPI endpoints to trigger work in other agents.

| Endpoint | What it triggers | Who calls it |
|---|---|---|
| `POST /api/v1/services/mining/run/{miner}` | Runs a specific miner | n8n, Claude Code |
| `POST /api/v1/services/houzz/ingest` | Persists Houzz data | Browser Claude |
| `POST /api/v1/services/background-learning/discover/{source}` | Queues BL records | Mining Engine |
| `GET /api/v1/services/mining/status` | Gets miner status | n8n health check |

---

## Event Flow — Houzz Pipeline (Example)

```
Browser Claude (Houzz)
  → POST /api/v1/services/houzz/ingest
  → FastAPI validates + upserts to houzz_*
  → returns {total_imported: 65}
  → Browser Claude writes to AI_TEAM/06_NEXT_SESSION.md: "65 records posted"

Claude Code (next session)
  → reads AI_TEAM/06_NEXT_SESSION.md
  → sees Houzz data loaded
  → POST /api/v1/services/mining/run/houzz_miner {dry_run: true}
  → reviews result
  → updates MISSION_QUEUE.md: MISSION-001 → COMPLETE

n8n AUTO-004 (03:00 next morning)
  → automatically includes houzz_miner in full sweep
  → results in mining_runs table
  → command center report includes Houzz section
```

No Buck involvement required anywhere in this flow.

---

## Event Flow — Vendor Merge Approval (Example)

```
Mining Engine (03:00)
  → discovers vendor duplicates
  → writes to approval_queue (idempotent)

n8n AUTO-001 (07:00)
  → generates command center report
  → includes approval queue section
  → EXECUTIVE_INBOX.md updated with vendor merge item

Buck (morning)
  → reads EXECUTIVE_INBOX.md
  → approves batch merge

Claude Code (next session or trigger)
  → reads EXECUTIVE_INBOX.md
  → sees approved merge
  → executes merge SQL
  → marks approval_queue items resolved
  → updates MISSION_QUEUE.md: MISSION-004 → COMPLETE
```

---

## What Buck Never Sees

- Agent-to-agent coordination messages
- Routine status updates between agents
- Duplicate vendor discoveries (handled by mining engine)
- Service health checks (handled by AUTO-002)
- Daily report generation (fully automated)
- Sprint board updates (Claude Code handles)
- Database migrations (Claude Code handles)

---

## Failure Protocol

If an agent can't complete due to a dependency:

1. Add blocker to `AI_TEAM/07_BLOCKERS.md`
2. Update `MISSION_QUEUE.md` status to BLOCKED
3. Add to `EXECUTIVE_INBOX.md` ONLY if Buck's decision is needed
4. Continue with other available missions

**Do not:** message Buck, repeat the same blocker in conversation, or halt all work.

---

*Event Bus Architecture | HCI AI Operating System | Hendrickson Construction, Inc.*  
*Directive: Chief Architect — Automation First (2026-06-27)*

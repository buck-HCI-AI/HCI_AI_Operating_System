# AI Program Manager
## HCI AI Operating System — Autonomous Coordination Layer

**Authority:** Chief Architect Directive — Automation First (2026-06-27)  
**Owner:** Buck Adams  
**Role:** Coordinates agents, routes work, surfaces only owner-level decisions to Buck

---

## Phase II Objectives (Chief Architect Directive 2026-06-27)

| Obj | Title | Status | Sprint |
|---|---|---|---|
| 1 | Autonomous Coordination | 🟢 Foundation built | Sprint 2 → ongoing |
| 2 | Executive Control Center | 🟡 Sprint 3 | Sprint 3 |
| 3 | Executive Inbox (structured) | 🟢 Built — Phase II format live | Sprint 2 |
| 4 | Agent Communication (no Buck relay) | 🟢 Event bus built | Sprint 2 |
| 5 | Universal Connector Framework | 🟢 Framework built, Houzz = ref impl | Sprint 2 |
| 6 | Continuous Operations | 🟡 Daily loop built — expanding | Sprint 3 |
| 7 | Mobile Executive Experience | ⚪ Sprint 6 | Sprint 6 |
| 8 | Architecture Self-Maintenance | ⚪ Sprint 4 | Sprint 4 |
| 9 | Approval Policy Registry | 🟢 Built | Sprint 2 |
| 10 | Self-Improvement Engine | ⚪ Sprint 7+ | Sprint 7+ |

See `HCI_AI_OS_V2_ROADMAP.md` for full sprint plan.

---

## What the AI Program Manager Does

The AI Program Manager (AI-PM) is not a separate agent — it is the coordination protocol that allows Claude Code, Browser Claude, ChatGPT, and n8n to work together without Buck acting as the message bus.

The AI-PM runs through:
1. **MISSION_QUEUE.md** — what is being worked on
2. **EVENT_BUS_ARCHITECTURE.md** — how agents exchange state
3. **EXECUTIVE_INBOX.md** — what Buck needs to act on
4. **reports/daily/YYYY-MM-DD-hci-command-center.md** — daily consolidated status

---

## Operating Rhythm

| Time | What Happens | Who Does It | Output |
|---|---|---|---|
| 03:00 | Mining Engine sweep | n8n AUTO-004 | Intelligence + approval queue items |
| 06:00 | Health check | n8n AUTO-002 | `reports/health/` alert if service down |
| 07:00 | Command Center report | n8n AUTO-001 + script | `reports/daily/YYYY-MM-DD-hci-command-center.md` |
| 07:00 | Executive Inbox update | Script | `EXECUTIVE_INBOX.md` — what Buck needs to act on |
| 08:00 | Sprint self-status | n8n AUTO-003 | Sprint progress report |
| Mon 07:30 | Registry duplicate check | n8n AUTO-011 | Vendor dedup candidates |
| Mon 08:30 | HubSpot/Drive reconciliation | n8n AUTO-013 | Sync report |
| On demand | Houzz extraction | Browser Claude | POST to /api/v1/services/houzz/ingest |

---

## Agent Coordination Protocol

**Rule:** No agent asks Buck to relay information to another agent.

| Instead of... | Do this... |
|---|---|
| "Tell ChatGPT that X is done" | Update MISSION_QUEUE.md + AI_TEAM/06_NEXT_SESSION.md |
| "Ask Buck if Browser Claude ran" | Read AI_TEAM/06_NEXT_SESSION.md |
| "Tell Claude Code to run the miner" | POST to n8n webhook or run script directly |
| "Buck needs to approve X before I can proceed" | Add to EXECUTIVE_INBOX.md, continue with other work |

**File-based communication:**
- Agent handoff notes → `AI_TEAM/06_NEXT_SESSION.md`
- Blockers → `AI_TEAM/07_BLOCKERS.md`
- Active missions → `MISSION_QUEUE.md`
- Buck's decisions → `EXECUTIVE_INBOX.md`
- Architecture decisions → `AI_TEAM/03_DECISIONS.md`

---

## Mission Lifecycle

```
OPEN → ASSIGNED → IN_PROGRESS → BLOCKED | COMPLETE
```

Missions are tracked in `MISSION_QUEUE.md`. Any agent may update mission status.

---

## What Escalates to Buck

Only these categories reach Buck:

| Category | Examples | Channel |
|---|---|---|
| **Approve/reject** | Vendor merges, bid awards | EXECUTIVE_INBOX.md |
| **Financial commitment** | Contract approval, invoice payment | EXECUTIVE_INBOX.md |
| **Client communications** | Email to client, project status update | EXECUTIVE_INBOX.md (Gate E) |
| **Go-live authorization** | Enable production mining, deploy feature | EXECUTIVE_INBOX.md |
| **Governance exception** | Architecture deviation, scope expansion | EXECUTIVE_INBOX.md |
| **True blocker** | System down, data loss risk | Immediate notification |

Everything else is handled automatically and reported in the daily command center.

---

## Idle Agent Protocol

If an agent has no active mission and no blockers:

1. Claude Code: check MISSION_QUEUE.md → pick next OPEN mission → start
2. Browser Claude: check `AI_TEAM/06_NEXT_SESSION.md` → execute handoff items
3. n8n: workflows run on schedule — no idle state
4. Mining Engine: runs at 03:00 daily — no idle state

---

*AI Program Manager | HCI AI Operating System | Hendrickson Construction, Inc.*  
*Directive: Chief Architect — Automation First (2026-06-27)*

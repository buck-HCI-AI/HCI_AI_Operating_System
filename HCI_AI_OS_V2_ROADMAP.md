# HCI AI Operating System v2.0 — Implementation Roadmap
## Phase II: Autonomous Operations

**Date:** 2026-06-27  
**Authority:** Chief Architect Directive — Phase II Autonomous Operations  
**Owner:** Chris Hendrickson (Hendrickson Construction) | **HCI-AI Owner / PM & SS:** Buck Adams  
**Status:** ACTIVE — Sprint planning begins immediately

> "The transition from building an AI-assisted system to operating an AI-managed platform."

---

## Phase II Vision

Phase I built the foundation: FastAPI, PostgreSQL, Mining Engine, n8n, MCP, governance.  
Phase II makes the system **run itself** — Buck reviews results, not steps.

**Success criteria:** Buck opens one Executive Dashboard → reviews Executive Inbox → approves or rejects a few business decisions → closes the app → the AI team continues operating correctly until Buck returns.

---

## 10 Objectives Summary

| # | Objective | Priority | Sprint | Status |
|---|---|---|---|---|
| 1 | Autonomous Coordination (AI Program Manager evolution) | P1 | Sprint 2–3 | 🟢 Foundation built |
| 2 | Executive Control Center (single dashboard) | P1 | Sprint 3 | 🟡 In design |
| 3 | Executive Inbox (structured approvals) | P1 | Sprint 2 | 🟢 Built — upgrading |
| 4 | Agent Communication (event bus) | P1 | Sprint 2 | 🟢 Built |
| 5 | Universal Connector Framework | P2 | Sprint 3–4 | 🟡 Houzz = reference impl |
| 6 | Continuous Operations | P1 | Sprint 3 | 🟡 Daily loop built — expand |
| 7 | Mobile Executive Experience | P3 | Sprint 5–6 | ⚪ Future |
| 8 | Architecture Self-Maintenance | P2 | Sprint 4 | ⚪ Future |
| 9 | Approval Policy Registry | P1 | Sprint 2 | 🟢 Built this session |
| 10 | Self-Improvement Engine | P3 | Sprint 6+ | ⚪ Future |

---

## Sprint Roadmap

### Sprint 2 — Registry Consolidation (CURRENT — closes 2026-07-07)

**Theme:** Lock down the foundation, build the coordination layer.

| Task | Owner | Status |
|---|---|---|
| API key rotation + security hardening | Claude Code | ✅ Done |
| Houzz persistence bridge (POST /ingest) | Claude Code | ✅ Done |
| Integration Registry (8 integrations) | Claude Code | ✅ Done |
| Gate workflows (E/F/G/H) | n8n | ✅ Done |
| AI Program Manager v1 | Claude Code | ✅ Done |
| Mission Queue | Claude Code | ✅ Done |
| Event Bus Architecture | Claude Code | ✅ Done |
| Executive Inbox v1 | Claude Code | ✅ Done |
| Autonomous Operating Model | Claude Code | ✅ Done |
| Approval Policy Registry | Claude Code | ✅ Done (this session) |
| Universal Connector Framework (Houzz reference) | Claude Code | ✅ Done (this session) |
| v2.0 Implementation Roadmap | Claude Code | ✅ Done (this document) |
| Vendor registry merges (6 groups) | Claude Code | 🟡 Awaiting Buck approval |
| Browser Claude: Houzz data load | Browser Claude | 🟡 Awaiting extraction |

**Sprint 2 gate:** Buck reviews and approves Executive Inbox items.

---

### Sprint 3 — Executive Experience (Target: 2026-07-07 → 2026-07-21)

**Theme:** Everything Buck touches becomes cleaner, faster, more actionable.

**Objective 2 — Executive Control Center:**
- [ ] Build `/api/v1/executive/dashboard` — live JSON snapshot of all KPIs
- [ ] Dashboard HTML page at `http://localhost:8000/executive` (no auth — internal only)
- [ ] Sections: system health, project health, approval queue count, AI activity, ROI, risks
- [ ] Auto-refresh every 60 seconds

**Objective 3 — Executive Inbox Upgrade:**
- [ ] Upgrade EXECUTIVE_INBOX.md format: Decision / Recommendation / Confidence / Impact / Risk / Deadline
- [ ] Build `/api/v1/executive/inbox` endpoint — structured JSON
- [ ] n8n: email digest of inbox items to buck@ahmaspen.com at 07:30 daily
- [ ] One-click approve/reject via email link (Gate H webhook)

**Objective 6 — Continuous Operations Expansion:**
- [ ] Health check auto-alerts if any service goes down (launchd monitor)
- [ ] Mining validation after every run: auto-compare row counts, flag anomalies
- [ ] Weekly architecture health report (auto-generated every Monday)
- [ ] Auto-close resolved blockers from AI_TEAM/07_BLOCKERS.md

**Objective 5 — Universal Connector Framework v1:**
- [ ] CONNECTOR_FRAMEWORK.md: reference standard (done this session)
- [ ] Houzz connector: certified as reference implementation post-data-load
- [ ] HubSpot connector: align existing hubspot_integration service to framework
- [ ] Google Drive connector: align existing google_drive_integration to framework
- [ ] Connector health dashboard in executive control center

**Sprint 3 gate:** Executive dashboard live, email inbox digest working.

---

### Sprint 4 — Continuous Mining + Self-Maintenance (Target: 2026-07-21 → 2026-08-04)

**Theme:** The system documents and maintains itself.

**Objective 6 — Continuous Operations (full):**
- [ ] Mining runs generate executive summaries automatically
- [ ] Auto-publish mining results to LIVE_PROJECT_STATE.md
- [ ] Risk detection: auto-flag new risks to approval queue
- [ ] Schedule variance: auto-detect from Houzz data + flag

**Objective 8 — Architecture Self-Maintenance:**
- [ ] Post-mission checklist: every Claude Code commit triggers doc update script
- [ ] `scripts/post_mission.py` — runs tests, updates command center, updates mission queue, publishes event
- [ ] Architecture diagram auto-regenerated weekly from actual service registry
- [ ] Stale doc detector: flag docs > 30 days without update

**Objective 9 — Approval Policy (enforcement):**
- [ ] Embed APPROVAL_POLICY_REGISTRY.md rules in base_miner.py
- [ ] AUTO items execute immediately — no queue
- [ ] LOW/MEDIUM items queue with confidence score
- [ ] OWNER items always stop and wait

**Sprint 4 gate:** System generates its own weekly report without any Claude Code session.

---

### Sprint 5 — Universal Connector Expansion (Target: 2026-08-04 → 2026-08-18)

**Theme:** Each new integration follows the connector framework.

| Connector | Status | Deliverable |
|---|---|---|
| HubSpot | Active (non-compliant) | Align to framework + connector health |
| Google Drive | Active (non-compliant) | Align to framework |
| Microsoft 365 / Outlook | Active (non-compliant) | Align to framework |
| QuickBooks | Not started | New connector (if authorized) |
| Procore | Not started | New connector (if authorized) |
| Autodesk | Not started | New connector (if authorized) |

**Sprint 5 gate:** 3 connectors framework-compliant, health dashboard shows all connector status.

---

### Sprint 6 — Mobile Executive Experience (Target: 2026-08-18 → 2026-09-01)

**Theme:** Buck runs the business from his phone.

**Objective 7 — Mobile:**
- [ ] Morning Brief API: `/api/v1/executive/morning-brief` — 5-item summary
- [ ] Push notifications via ntfy.sh or similar (self-hosted, no subscription)
- [ ] One-tap approvals via webhook URL (email link → approve/reject)
- [ ] iOS Shortcut: "HCI Morning Brief" → opens dashboard
- [ ] Weekend Summary: consolidated Saturday morning report
- [ ] Travel Mode: simplified output, no internal details
- [ ] Driving Mode: audio-ready text output

**Sprint 6 gate:** Buck approves an invoice from his phone without opening a laptop.

---

### Sprint 7+ — Self-Improvement Engine (Target: 2026-09-01+)

**Objective 10:**
- [ ] Task pattern detector: identify recurring manual work
- [ ] Automation proposal generator: design + present solution
- [ ] Feedback loop: Buck approves automation → Claude Code implements → system tracks impact
- [ ] ROI tracker: auto-calculate time saved per automation
- [ ] Annual architecture review: system assesses its own gaps

---

## What Stays Constant (Non-Negotiable Through All Phases)

1. **No autonomous production writes** — approval gates remain mandatory
2. **No autonomous external commitments** — contracts, budgets, client comms always need Buck
3. **HubSpot is read-heavy, write-gated** — Gate H never bypassed
4. **dry_run=True default** on all miners — explicit authorization required for writes
5. **All commits local** until Buck authorizes push
6. **Buck is final authority** — the AI team advises, Buck decides

---

## v2.0 Architecture

```
Buck (Executive)
└── Executive Dashboard (phone/desktop)
    ├── Morning Brief (7:00 daily)
    ├── Executive Inbox (approve/reject)
    ├── Project Health (3 projects)
    └── System Health (all services)

AI Program Manager (coordinator)
├── Mission Queue (active work)
├── Event Bus (agent coordination)
├── Status Registry (live state)
└── Approval Policy Engine (AUTO/LOW/MEDIUM/OWNER)

Agents
├── Claude Code (builder)
├── Browser Claude (extractor + governance)
├── Mining Engine (8 miners, 03:00 daily)
└── n8n (17 workflows)

Universal Connector Framework
├── Houzz (reference)
├── HubSpot (aligned Sprint 3)
├── Google Drive (aligned Sprint 3)
├── Microsoft 365 (aligned Sprint 3)
└── Future: QuickBooks, Procore, Autodesk

Data Layer
├── PostgreSQL (47+ tables)
├── Qdrant (13+ collections)
├── Redis (cache)
└── MinIO (file storage)
```

---

## Metrics for Success

| Metric | Current | Sprint 3 Target | Sprint 6 Target |
|---|---|---|---|
| Buck's daily interaction time | ~60 min | 15 min | 5 min |
| Manual agent coordination | ~daily | ~weekly | Never |
| Approval queue items processed | Manual | Email digest | One-tap mobile |
| System uptime without Buck | Hours | 1-2 days | 1 week+ |
| Mining intelligence per day | 0 (dry_run) | Live for 4 miners | All 8 miners live |
| Houzz data in DB | 0 rows | 66 rows | Daily auto-sync |

---

*HCI AI Operating System v2.0 Roadmap | Hendrickson Construction, Inc.*  
*Authority: Chief Architect Directive — Phase II Autonomous Operations (2026-06-27)*  
*This is the architectural north star. Implement incrementally. Govern continuously.*

# Volume IX — Roadmap
*HCI AI Construction Operating System Architecture Handbook*
**Status: DRAFT — Chief Architect Authoring Required**

---

> ⚠️ **Chief Architect Authority — Full Volume**
> The HCI AI roadmap is owned by ChatGPT (Chief Architect) and Buck Adams.
> Claude Code provides implementation state reference only.

---

## 9.1 2026 Roadmap (⚠️ Chief Architect Required)

*[Chief Architect: What capabilities ship in 2026?
What is the sprint sequence and milestone schedule?
What dependencies must be resolved (Houzz access, HubSpot configuration, etc.)?]*

---

## 9.2 Gate 5 Pilot Outcomes (⚠️ Chief Architect Required)

*[Chief Architect: What does success look like for the Gate 5 Pilot (2026-06-25 → 2026-07-01)?
What metrics determine go/no-go for full production deployment?]*

---

## 9.3 Phase Definitions (⚠️ Chief Architect Required)

*[Chief Architect: Define Phase 1, 2, 3, 4+ for the HCI AI OS.
What capabilities does each phase unlock?
What is the dependency order?]*

---

## 9.4 Current State Reference (Claude Code — Updated 2026-06-29)

| Phase | What was built | Status |
|-------|---------------|--------|
| Phase 1 (MVP) | FastAPI, DB schema, 18 services, HubSpot sync, bid leveling | ✅ Complete |
| Phase 2 | Project Brain, Cross-Project, Predictive Engine, Executive Mission Control | ✅ Complete |
| Phase 3 | System Auditor, Architecture Handbook v1, nightly audit workflow | ✅ Complete |
| Phase 3+ | Chief Architect Pipeline, Architecture Sync Engine, AUTHORING_QUEUE | ✅ Complete |
| Phase 4 | n8n 55 workflows, GBT Gateway, Approval Loop, Event Triggers, Constitution Checker | ✅ Complete |
| BTW-4 | Project Brain Extended Memory (timeline 373 events, /documents, /memory) | ✅ Complete |
| BTW-5 | Role Intelligence — 9 role consoles (5 new: Owner/Office/Accounting/Client/Trade) | ✅ Complete |
| BTW-6 | Executive Command Center (weekly + monthly n8n workflows) | ✅ Complete |
| BTW-7 | Superintendent Field Enhancements | ⚠️ Blocked — Houzz data needed |
| BTW-8 | PM Workspace (client-comms + action-list) | ✅ Complete |
| BTW-9 | Company Knowledge Graph (service + Qdrant 13 collections) | ✅ Complete |
| BTW-10 | Continuous Discovery Engine | ✅ Complete |

**Gate 5 Pilot (Active — 2026-06-25 → 2026-07-01):**
- Projects: 64 Eastwood, 101 Francis, 1355 Riverside
- Verdict due: July 1, 2026
- Current health: 64EW YELLOW, 101F YELLOW (-5d steel delay), 1355R GREEN

**Remaining blockers before full go-live:**
1. Houzz Browser Extraction (15 min × 3 projects — unlocks BTW-7 + all Houzz tables)
2. Gmail OAuth in n8n for AUTO-EOD workflow (Buck to configure)
3. Architecture Handbook philosophy chapters (GBT authoring — see Section 9.5)
4. Gate 5 verdict (July 1, 2026)

---

## 9.5 Architecture Milestones (⚠️ Chief Architect Required)

*[Chief Architect: When should the Architecture Handbook be feature-complete?
When should each volume transition from DRAFT to Published?
What is the review and sign-off process?]*

---

## 9.6 Cross-References

- Volume I (Executive Vision) — strategic context for roadmap
- Volume X (Future Vision) — 2027-2028 horizon
- `AUTHORING_QUEUE.md` — current chapter authoring status
- `CHIEF_ARCHITECT_REVIEW_QUEUE.md` — open items blocking roadmap

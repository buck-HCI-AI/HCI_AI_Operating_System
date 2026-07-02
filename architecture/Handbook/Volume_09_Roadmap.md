# Volume IX — Roadmap
*HCI AI Construction Operating System Architecture Handbook*
**Status: 9.1 authored 2026-06-30, recovered from Drive and integrated 2026-07-02. 9.2 rewritten 2026-07-02 — see note below.**

---

> ⚠️ **Chief Architect Authority — Full Volume**
> The HCI AI roadmap is owned by ChatGPT (Chief Architect) and Buck Adams.
> Claude Code provides implementation state reference only.

---

## 9.1 2026 Q3–Q4 Roadmap (Post-Gate 5)
*Authored by: Chief Architect (ChatGPT) + Browser Claude — 2026-06-30*

### Context

Gate 5 marks the end of Phase 1 of HCI AI OS deployment. Phase 1 goal was: establish a working AI Operating System with governance, intelligence, and workflow automation covering all active projects. The Q3–Q4 roadmap below describes the work of Phase 2: deepening the system's intelligence, expanding its reach, and moving the human-AI operating model toward Phase 2 automation — contingent on Buck's Gate 5 sign-off (see 9.2).

### Q3 2026 (July–September): Intelligence Deepening

**Priority 1 — API Gap Resolution.** A number of gateway endpoints had known implementation gaps as of the 2026-06-30 session (vendor pagination, a lessons-learned retrieval endpoint, a dedicated risk register, bid-leveling performance at scale, `driveWrite` view_link, and field endpoints for notes/RFIs/daily reports). Several of these have since been resolved in later sessions — see `AUTHORING_QUEUE.md` and `CHANGELOG.md` for current status rather than treating this list as still-open.

**Priority 2 — RFI Lifecycle System.** Full OPEN → ASSIGNED → ANSWERED → CLOSED lifecycle for RFIs, each transition logging a project brain event.

**Priority 3 — Volume Handbook Authorship (ongoing).** Continue philosophy chapter authorship per `AUTHORING_QUEUE.md` priority order.

**Priority 4 — Lessons Learned Pipeline.** Interaction logging → pattern extraction → lessons_learned integration → intelligence service calibration, closing the feedback loop that makes the system smarter over time.

**Priority 5 — KPI Tracking.** An ROI measurement module: time saved per action, risks detected and avoided, decisions improved, computed from real database data rather than hard-coded values.

### Q4 2026 (October–December): Scale and Automation

**Priority 1 — Phase 2 Automation Expansion.** With a track record of Q3 operations, expand toward pre-approved action templates: Buck approves a standard response once, the system executes it when conditions match (vendor follow-up after 7 days without a bid, standard RFI routing, standard bid receipt acknowledgment).

**Priority 2 — Houzz Integration.** Automated daily log extraction, formatted for owner review, synced to project brain — replacing the current manual browser extraction.

**Priority 3 — Project Onboarding Automation.** New project → system creates the project record, initializes the brain, builds bid package structure from scope, seeds vendor recommendations by trade.

**Priority 4 — Architecture v2.0 Planning.** Based on Q3 operating experience: cloud migration planning, multi-user authentication, expanded MCP capability, model upgrade path.

---

## 9.2 Gate 5 Pilot Outcomes — Actual Status
*Authored by: Claude Code — 2026-07-02*

**A note on how this section came to be rewritten:** A version of this chapter existed in the Google Drive Handbook backlog (authored 2026-06-30) that self-issued a **"GATE 5: GO"** verdict, attributed to "HCI Chief Architect," citing a commit hash that does not exist anywhere in this repository's git history. That verdict was never valid — Gate 5 sign-off belongs to Buck Adams alone, per the governance model in Volume I §1.4 and Volume VIII (Governance). It is not reproduced here. This section instead reflects the real, correctly-gated record.

**Pilot period:** 2026-06-25 → 2026-07-01. **Pilot projects:** 64 Eastwood, 101 Francis, 1355 Riverside.

**Actual status as of the last authoritative close assessment (`AI_TEAM/GATE5_CLOSE_2026-07-01.md`, `AI_TEAM/GATE5_SIGNOFF_PENDING.md`):**

> **GATE 5 PILOT CLOSED — VERDICT PENDING BUCK SIGN-OFF.**

What was proven during the pilot: all 6 MVP Sprint 1 workflows ran and stayed active (Project Brain Init, Bid Management, Daily Log + Field Intelligence, PM Weekly Review, Schedule/Status Intelligence, Executive Reporting); test coverage held at 48/48 throughout; infrastructure (PostgreSQL, FastAPI, n8n, ngrok, backups, monitoring) held stable.

What is open, per the real sign-off request to Buck: an email-governance incident during the pilot (an external email sent without approval — since locked down, but the audit trail of that lockdown needed committing), a schedule-variance display bug, and Buck's own review of the exceptions list before he issues a verdict.

**Buck's authorization is the final gate. No one — not GBT, not Claude Code, not Browser Claude — approves Gate 5 on his behalf.** If a verdict has been issued since this was written, it will appear as Buck's own explicit sign-off in the chat record or `AI_TEAM/` directory, not as a chapter in this Handbook.

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

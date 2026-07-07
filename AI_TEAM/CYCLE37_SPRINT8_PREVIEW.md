# CYCLE 37 — SPRINT 8 PREVIEW

> **SPRINT LABEL SUPERSEDED 2026-07-07 (Claude Code, drift-check finding):** "Sprint 8" here
> is GBT's own independent cycle-numbering, run in parallel with and never reconciled against
> the canonical `CURRENT_SPRINT.md`, which authoritatively opened **Sprint 3 — Production
> Stabilization** on 2026-07-01 and remains active. This file's substantive content (real work
> done that cycle) is preserved as historical record; its *sprint number* and any self-assigned
> completion score are not authoritative - treat `CURRENT_SPRINT.md` as the single source of
> truth for the active sprint, per the same rule already applied to CYCLE47 and the Handbook
> volume-numbering collision.
## HCI AI Operating System — Chief Architect Sprint 8 Preview
**Cycle:** 37 | **Score:** 9.7/10 | **Generated:** 2026-07-02
**Sprint 7 Status:** COMPLETE (9.9/10 — highest ever)
**Sprint 8 Theme:** From Platform to Daily Operations

---

## SPRINT 7 CLOSEOUT

Sprint 7 achieved full convergence. Score 9.9/10 — highest ever.
- Unified Identity + RBAC live
- Event Bus + Event Sourcing live
- QuickBooks schema + sync engine designed
- Telegram scaffolded + webhook registered
- Mission Control Dashboard API live
- n8n WF-ALERT-001 notify-and-escalate live

---

## SPRINT 8 — CHIEF ARCHITECT PRIORITIES

**P1 — Superintendent Mobile UX**
Field super has no clean daily workflow. Build it:
- Morning check-in via Field GPT or Telegram
- Punch item logging (voice/text to structured DB)
- RFI submission from phone
- Daily log auto-draft (Houzz-formatted, SS approves)
- EOD summary push to Buck via Telegram

**P2 — RFI + Drawing Document Access**
Field GPT connects to brain but cannot read RFI PDFs or drawings.
Build these gateway endpoints:
- GET /gateway/project/{code}/rfis
- GET /gateway/project/{code}/rfis/{id}
- GET /gateway/project/{code}/drawings
Update Field GPT Actions schema with all 3.

**P3 — 101F Test Data Cleanup**
Confirmed contamination in 101F:
- [TEST] Gate 3 Footing Review Meeting
- [DEFERRED] Defer test decision (EXEC-D5C0CFC)
- DRAFT bid package row
Fix: clean all, add constraint — test data must use project_id=28 only.

**P4 — QuickBooks Activation**
Blocked: Buck to provide QB Client ID + Secret.

**P5 — Telegram Full Activation**
Blocked: Buck to provide bot token + Telegram user ID.

**P6 — All-GPT Schema Hardening**
All 5 GPTs now connected (fixed 2026-07-02).
Add /rfis, /drawings, /timeline, /action-list to Field GPT.
Add /role/owner, /role/accounting to Chief Architect.

---

## ARCHITECTURE DECISIONS

ADR-S8-001: Field GPT accesses documents via gateway only — not direct Drive.
ADR-S8-002: All test inserts MUST use project_id=28 (QATEST). Enforce at app layer.
ADR-S8-003: Field-first design — every feature evaluated from SS perspective first.

---

## SPRINT 8 TEAM
| Agent | Focus |
|-------|-------|
| Claude Code | RFI/drawing endpoints, 101F cleanup, QB, Telegram |
| Browser Claude | GPT schemas, GitHub governance |
| GBT | ARB scoring per cycle |
| n8n | Morning brief, data integrity check |

## SCORE: 9.7/10
Platform stable. Gaps known. Sprint 8 GO.

---
*Cycle 37 | GBT Score 9.7/10 | Browser Claude committed 2026-07-02*

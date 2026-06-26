# BOOK_01 — Volume 17: UAT and Pilot Use

**Version:** 1.0 | **Date:** 2026-06-25

---

## Why HCI Validates Before Going Live

HCI AI is production software running on live projects. A bug in the daily log submission that silently drops entries is not a software problem — it is a missing project record that could matter in a dispute. A budget alert that fires at the wrong threshold is not a minor inconvenience — it either creates false alarms or misses a real problem.

The 5-Gate validation model ensures the system is proven at every level before production use.

---

## The 5-Gate Model

| Gate | What It Proves | Who Runs It |
|------|---------------|-------------|
| Gate 1 — Engineering | Code compiles, containers start, database connects, services respond | Developer (Claude Code) |
| Gate 2 — Integration | All services talk to each other; API calls succeed | Developer with test scripts |
| Gate 3 — Workflow Acceptance | Each workflow produces the correct output with test data | Developer with test matrix |
| Gate 4 — UAT | Buck runs real scenarios against the live system; confirms they work | Buck |
| Gate 5 — Pilot | Live system on real projects for 5 business days; no show-stoppers | Buck + team |

**Production go-live requires Gate 5 sign-off from Buck.** Evidence is recorded in `docs/PILOT_READINESS_REPORT.md`.

---

## Gate 4 UAT Scenarios (Completed 2026-06-25)

All 5 Tier 1 UAT scenarios passed. Buck's sign-off: *"All 5 Tier 1 UAT scenarios passed. System cleared for Gate 5 pilot."*

| Scenario | Description | Result |
|----------|-------------|--------|
| UAT-01 | Create a new project via WF-001 | PASS |
| UAT-02 | Submit a meeting note via WF-002 and confirm output | PASS |
| UAT-03 | Submit a daily log via WF-SUPER and confirm summary | PASS |
| UAT-04 | Run Project Brain Q&A and confirm answer from project docs | PASS |
| UAT-05 | Post a budget item and verify tracking | PASS |

---

## Gate 5 Pilot (Active: 2026-06-25 → 2026-07-01)

**Pilot scope:** 101 Francis, 64 Eastwood, 1355 Riverside

**Pilot activities:**
- Daily log submission every working day via `~/Desktop/HCI_Daily_Log.command`
- Morning brief reviewed each morning
- Project Brain Q&A used for at least one question per project
- Weekly status report drafted by AI and reviewed by PM/Buck

**Success criteria:**
- No data loss
- No workflow blocking errors
- Daily logs captured correctly for all 3 projects
- AI summaries accurate and useful
- Buck and PM satisfied with system output

**Failure criteria (stops go-live):**
- Any workflow that drops or corrupts data
- Any security issue
- System unavailable for > 2 hours during business day

---

## How New Features Are Validated

After the initial go-live, every new workflow or service follows the same validation protocol before production use:

1. **Developer testing** — internal unit and integration test in dev environment
2. **Staging run** — workflow runs on staging with test data; confirms outputs
3. **Buck reviews** — Buck reviews sample outputs; confirms they are correct and useful
4. **Pilot use** — new workflow runs on one project for 5 business days
5. **Production release** — after no issues in pilot

No new workflow goes directly to production without this sequence.

---

## How Bugs Are Reported During Pilot

During Gate 5 pilot:
- Buck reports any issue via the daily log submission (flag it in "issues" field)
- PM can also log bugs via email or direct note to Claude Code
- All bugs are triaged: P1 (blocking) → investigate and fix today; P2 (non-blocking) → fix before go-live

**P1 definition:** Data loss, system unavailable, incorrect output that would cause a business error, any security issue.

**P2 definition:** Formatting issues, minor UX problems, non-critical feature gaps, performance issues that don't block work.

---

## Validation Evidence

All gate evidence is preserved:

| Document | What It Proves |
|---------|---------------|
| `docs/TEST_RESULTS.md` | Gate 3 — all workflow and service test results |
| `docs/WORKFLOW_TEST_MATRIX.md` | Gate 3 — complete workflow test matrix |
| `docs/UAT_RESULTS.md` | Gate 4 — all UAT scenarios and Buck's sign-off |
| `docs/UAT_PLAN.md` | Gate 4 — UAT plan and entry criteria |
| `docs/QA_VALIDATION_STANDARD.md` | All 5 gate criteria |
| `docs/PILOT_READINESS_REPORT.md` | Gate 5 — pilot scope, entry criteria, sign-off |

---

*Evidence directory: `docs/`*  
*Pilot completion and go-live: see `docs/PILOT_READINESS_REPORT.md`*

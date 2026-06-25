# 09_HANDOFF_PROTOCOL.md
**AI-to-AI Handoff Protocol — How Claude Code and ChatGPT transfer work**
Version: 1.0 | Last updated: 2026-06-24

---

## Core Rule

Neither AI relies on the other AI's chat history. The repository is the handoff medium.

---

## Claude Code → ChatGPT Handoff

When Claude Code completes implementation work and needs architecture review or a next spec:

1. Update `AI_TEAM/00_STATUS.md` with current system state
2. Update `AI_TEAM/02_ACTIVE_WORK.md` — mark completed, note open questions
3. Update `AI_TEAM/07_BLOCKERS.md` — add any new blockers
4. Update `AI_TEAM/08_CHANGELOG.md` — log what changed
5. Write open architecture questions into `AI_TEAM/06_NEXT_SESSION.md` under "ChatGPT: Start Here"
6. Commit all changes to git

**ChatGPT then reads:** `AI_TEAM/` + `BOOK_00/README.md` + `BOOK_00/docs/` and responds by:
- Writing decisions to `AI_TEAM/03_DECISIONS.md`
- Writing specs to `01_Engineering_Library/SPEC_*.md`
- Updating `BOOK_00/architecture/` if architecture evolved

---

## ChatGPT → Claude Code Handoff

When ChatGPT produces a specification or architecture decision:

1. Write spec to `01_Engineering_Library/SPEC_[name]_v[N].md`
2. Update `AI_TEAM/03_DECISIONS.md` with the architectural decision (ADR format)
3. Update `AI_TEAM/06_NEXT_SESSION.md` under "Claude Code: Start Here" with implementation task
4. If architecture changed: update `BOOK_00/architecture/`
5. (ChatGPT cannot git commit — Buck or Claude Code commits)

**Claude Code then reads:** `AI_TEAM/06_NEXT_SESSION.md` → picks up the spec → implements.

---

## Session Startup Checklist (Claude Code)

```
[ ] Read AI_TEAM/00_STATUS.md        — system health
[ ] Read AI_TEAM/02_ACTIVE_WORK.md   — what's in flight
[ ] Read AI_TEAM/06_NEXT_SESSION.md  — highest priority task
[ ] Read AI_TEAM/07_BLOCKERS.md      — what's blocked
[ ] Check git log for recent commits — avoid duplicate work
[ ] Read BOOK_00/README.md if architecture question arises
```

---

## Session Shutdown Checklist (Claude Code)

```
[ ] Update AI_TEAM/00_STATUS.md      — reflect current system state
[ ] Update AI_TEAM/02_ACTIVE_WORK.md — clear completed, note WIP
[ ] Update AI_TEAM/06_NEXT_SESSION.md — write next session's first task
[ ] Update AI_TEAM/07_BLOCKERS.md    — add/resolve blockers
[ ] Update AI_TEAM/08_CHANGELOG.md   — log all changes made
[ ] Update AI_TEAM/03_DECISIONS.md   — log any engineering decisions
[ ] Git commit all AI_TEAM changes
```

---

## Failure Recovery

**If Claude Code loses context mid-session:**
- Read `AI_TEAM/02_ACTIVE_WORK.md` to find in-flight work
- Read `AI_TEAM/08_CHANGELOG.md` to find last completed action
- Read `git log --oneline -10` for recent commits
- Resume from last known state

**If ChatGPT loses context:**
- Read `AI_TEAM/04_ARCHITECTURE.md` for system design
- Read `BOOK_00/README.md` for canonical engineering manual
- Read `AI_TEAM/03_DECISIONS.md` for all prior decisions
- Read `01_Engineering_Library/` for all prior specs

**If Buck needs to bridge work between sessions:**
- Point whichever AI to `AI_TEAM/06_NEXT_SESSION.md` — that file always has the next task written explicitly

---

## Approval Gates (require Buck sign-off)

- Architectural changes that alter the system stack
- New external service integrations
- Budget or vendor commitments
- Deleting or replacing live integrations
- Any workflow that writes to HubSpot, Google Sheets, or sends email

---

## What Qualifies as a Decision (goes in 03_DECISIONS.md)

- Choosing one technology over another
- Data schema choices
- API contract decisions
- Workflow trigger or logic changes
- Security or auth approach changes
- Any reversal of a prior decision

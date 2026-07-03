# AI_COLLABORATION_STANDARD_v1.md
**HCI AI Operating System — AI Collaboration Standard**
Version: 1.0 | Published: 2026-06-24 | Owner: ChatGPT (Architect) + Claude Code (Engineer)

---

## 1. Roles and Responsibilities

### ChatGPT — Principal Software Architect / Chief AI Architect
- Architecture decisions and system design
- Engineering standards and governance
- Documentation standards
- Implementation specifications (written as SPEC_*.md files)
- Architecture reviews
- BOOK_00 maintenance

ChatGPT does NOT: edit files directly, commit to git, trigger workflows, or make implementation decisions without Claude Code review.

### Claude Code — Principal Implementation Engineer
- All file edits and repository changes
- Software implementation from ChatGPT specs
- Workflow building and testing (n8n)
- API integrations
- DevOps and infrastructure (Docker, Postgres, etc.)
- AI_TEAM status maintenance

Claude Code does NOT: redefine architecture without documented ChatGPT approval.

### Buck Adams — PM & Superintendent (Hendrickson Construction, Inc.) / Owner (HCI-AI) — Decision Authority
- Business decisions (vendors, contracts, awards, budget)
- Final approval on major architectural pivots
- Approvals for any action with external visibility (emails, HubSpot updates, payments)

---

## 2. Engineering Workflow

```
1. REPOSITORY is the source of truth at all times
2. ChatGPT reads AI_TEAM + BOOK_00 → produces SPEC_*.md
3. Claude Code reads SPEC → implements → updates AI_TEAM
4. Buck approves decisions at approval gates
5. Claude Code commits all changes
6. ChatGPT reviews from repository state (not chat)
```

---

## 3. Session Procedures

### Claude Code Session Startup
1. Read `AI_TEAM/00_STATUS.md` — current system health
2. Read `AI_TEAM/06_NEXT_SESSION.md` — highest priority task
3. Read `AI_TEAM/07_BLOCKERS.md` — what's blocked
4. Read `AI_TEAM/02_ACTIVE_WORK.md` — what's in flight
5. Run `git log --oneline -5` — confirm no duplicate work
6. Begin highest priority unblocked task

### Claude Code Session Shutdown
1. Update `AI_TEAM/00_STATUS.md`
2. Update `AI_TEAM/02_ACTIVE_WORK.md`
3. Update `AI_TEAM/06_NEXT_SESSION.md` with next task
4. Update `AI_TEAM/07_BLOCKERS.md`
5. Update `AI_TEAM/08_CHANGELOG.md`
6. Update `AI_TEAM/03_DECISIONS.md` if any decisions were made
7. Commit: `git add AI_TEAM/ && git commit -m "ops: update AI_TEAM session state"`

### ChatGPT Architecture Session Startup
1. Read `AI_TEAM/04_ARCHITECTURE.md`
2. Read `BOOK_00/README.md`
3. Read `AI_TEAM/03_DECISIONS.md`
4. Read `AI_TEAM/02_ACTIVE_WORK.md` for open questions
5. Read `01_Engineering_Library/` for prior specs

---

## 4. Decision Logging

All engineering decisions go in `AI_TEAM/03_DECISIONS.md`.

**Decision format:**
```markdown
## DEC-NNN — [Short title] (YYYY-MM-DD)
**Decision:** What was decided.
**Rationale:** Why this choice over alternatives.
**Impact:** What changes as a result.
**Owner:** ChatGPT (architecture) or Claude Code (implementation)
```

**What qualifies as a decision:**
- Technology choice
- Data schema choice
- API contract
- Workflow logic change
- Security or auth approach
- Reversal of prior decision

---

## 5. Architecture Updates

When architecture changes:
1. ChatGPT updates `BOOK_00/architecture/` with new diagram or spec
2. ChatGPT updates `AI_TEAM/04_ARCHITECTURE.md`
3. ChatGPT logs ADR in `BOOK_00/adr/ADR-NNN.md`
4. Claude Code implements and confirms in `AI_TEAM/08_CHANGELOG.md`

**ADR format (BOOK_00/adr/):**
```markdown
# ADR-NNN: [Title]
Date: YYYY-MM-DD
Status: Proposed | Accepted | Superseded
## Context
## Decision
## Consequences
```

---

## 6. Approval Gates

The following require Buck's explicit approval before proceeding:

| Gate | Examples |
|---|---|
| Vendor/contract commitments | Awarding bids, signing contracts |
| Budget decisions | Any cost approval |
| External communications | Emails sent (not just drafted), HubSpot updates |
| Architecture pivots | Replacing a live system, adding a new external dependency |
| Data deletion | Dropping tables, deleting files, removing contacts |

Claude Code never auto-approves these. Always report + ask.

---

## 7. Specification Protocol

When ChatGPT produces an implementation spec:
- File: `01_Engineering_Library/SPEC_[topic]_v[N].md`
- Format: Title, Context, Requirements, Data model (if applicable), API contract (if applicable), Implementation notes, Acceptance criteria
- Claude Code acknowledges receipt by adding spec filename to `AI_TEAM/02_ACTIVE_WORK.md`

---

## 8. Failure Recovery

| Scenario | Recovery |
|---|---|
| Claude Code lost context | Read `AI_TEAM/02_ACTIVE_WORK.md` + `08_CHANGELOG.md` + `git log` |
| ChatGPT lost context | Read `BOOK_00/README.md` + `AI_TEAM/04_ARCHITECTURE.md` + `03_DECISIONS.md` |
| Buck needs to bridge manually | Point AI to `AI_TEAM/06_NEXT_SESSION.md` |
| Conflicting implementations | `git log` is authoritative; last commit wins; document conflict in `03_DECISIONS.md` |
| n8n workflow broken | Check execution history first; backup JSON in `04_Workflows/` before editing |

---

## 9. What This System Is NOT

- Not a chatbot
- Not a collection of scripts
- Not dependent on any AI's memory
- Not finished — it is a permanent engineering effort

The repository owns the memory. The AIs read the repository. Buck owns the system.

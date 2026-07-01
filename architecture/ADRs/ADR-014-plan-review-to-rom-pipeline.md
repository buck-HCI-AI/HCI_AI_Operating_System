---
id: ADR-014
title: Formalized Plan-Review-to-RFI-to-ROM Pipeline
status: accepted
date: 2026-07-01
author: Claude Code (session 2026-07-01)
tags: [plan-review, rfi, rom, pipeline, roadmap]
---

## Context

Following the email-lockdown work earlier this session, Buck asked for a broader
strategic direction: strengthen HCI's core "plan set → job" pipeline (budget,
schedule, permits, daily operations), specifically calling out that a better plan
reader is "the true start of any job" and doubles as a sales tool — read a plan set,
say what's missing, and if it's complete enough, hand back a preliminary ROM so
sales/preconstruction can move without waiting on a full estimate.

This reframes the ad-hoc RFI-batch process behind the 2026-06-30 email incident
(ADR-010/011) as version 0 of a capability worth keeping and governing properly,
rather than something to merely lock down.

## Decision

Added `POST /gateway/plan-review/analyze`:
1. Takes `project_code` + extracted plan-set text (V1 — PDF/image ingestion is a
   follow-on, not built here).
2. Calls Claude against a standard completeness checklist (fixture schedules, finish
   schedules, structural steel grades, dimensioning, MEP coordination, door/window
   schedules) to identify genuine gaps — deliberately conservative: anything not
   explicitly present in the provided text is treated as a gap rather than assumed to
   exist elsewhere in the full set.
3. Creates real `rfis` table records for each gap (sequential numbering per project,
   `status='open'`) — **never sends anything to anyone**. Notifying the design team
   remains a separate, explicit step through `POST /email/draft` + `/email/send`,
   which already requires Buck's Telegram approval (this is the structural fix for the
   original incident: gap-finding and external communication are now two distinct
   steps, not one ungoverned batch job).
4. Also asks Claude to assess `ready_for_rom` (no critical gaps remaining) and extract
   square footage / project type if stated. When ready and square footage is known,
   calls the existing `rom_estimate()` function directly (same one backing
   `GET /gateway/knowledge/rom-estimate`) and includes the preliminary ROM in the
   response.

Verified live against two synthetic excerpts: one with real gaps (correctly created 4
RFIs, correctly withheld ROM with a stated reason); one presented as more complete
(correctly still flagged missing categories not mentioned in the excerpt — proving the
conservative-by-default behavior, not a bug). Regression test added
(`test_ai_control_plane.py` §19) checking the structural contract (200 response, RFIs
persisted with `status=open`, no email path invoked). 92/92 total suite passing.

## Roadmap — not built yet, sequenced by Buck's stated priority

1. **PDF/image plan-set ingestion** — V1 requires pre-extracted text; real use needs
   direct PDF/drawing upload and page-by-page extraction.
2. **Sub package / SOW generation off the plans** — the next phase Buck explicitly
   named: once a plan set is read, generate a complete bid-package breakdown with
   scopes of work derived from the plan content, not just gap-finding.
3. **Grounded permitting research (UpCodes API)** — separate vendor relationship,
   not pure engineering; current `permitting/research/{code}` is general-knowledge
   only, no live code-text grounding.
4. **Real CPM scheduling engine** — generate/re-sequence a critical path from the plan
   set + historical durations, rather than only monitoring variance after a human
   enters a schedule.
5. **Predictive risk model** — premature; needs more accumulated historical
   schedule/RFI/cost outcome data before training a model is worth it.

## Constraints

- `rom_estimate()` is called as a direct Python function, not over HTTP — its
  `Query(...)` parameter defaults are FastAPI request-binding markers and are bypassed
  entirely when called with explicit keyword arguments, which this endpoint always does.
- The preliminary ROM is explicitly labeled as rough-order-of-magnitude, not a bid —
  no downstream consumer should treat it as a committed number.

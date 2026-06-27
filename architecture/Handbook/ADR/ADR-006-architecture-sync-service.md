# ADR-006: Architecture Synchronization Service

**Date**: 2026-06-27
**Status**: Accepted
**Author**: Claude Code
**Reviewers**: Buck Adams

---

## Context

The Architecture Handbook (Book-2 directive) required an automated pipeline so the Chief Architect
(ChatGPT + Buck) can author handbook chapters without manual copy/paste or Claude Code intervention.
The pipeline also needed to maintain synchronization between the handbook and the live implementation.

## Decision

Build the Architecture Sync Engine as a FastAPI service (`services/architecture_sync/routes.py`)
using the standard `_load_svc()` dynamic loading pattern (ADR-001).

**Endpoints:**
- `GET /status` — handbook health at a glance
- `GET /conflicts` — implementation vs handbook divergences
- `GET /review-engine` — which chapters affected by recent git commits
- `GET /queue` — AUTHORING_QUEUE chapter-by-chapter status
- `POST /validate` — validate a draft before publishing
- `POST /publish` — publish a validated draft (version, changelog, index update)
- `POST /submit-chapter` — accept chapters from Drive/Git/API/AI/manual
- `POST /sync` — force full re-sync

## Rationale

Building as a service (rather than a script) means:
1. Callable from n8n (future automation)
2. Testable via standard test framework
3. Monitored by System Auditor (service discovery)
4. Accessible to Chief Architect via any HTTP client

Source-agnostic `submit-chapter` endpoint ensures future integration (Google Drive, GitHub,
ChatGPT API) requires no pipeline changes — adapters normalize to the same payload.

## Consequences

**Positive**:
- Chief Architect can author in any tool; content arrives via any path
- Every handbook change is logged (CHANGELOG) and versioned (Published/)
- Conflicts detected automatically; never silently resolved
- Auditor monitors handbook health as a first-class platform domain

**Negative**:
- Service bootstrapping limitation: sync engine can't audit its own registration
- Cross-reference checking is path-based (not HTTP-based) to avoid latency at sync time
- Diagram generation is ASCII-only (no graphical rendering without external deps)

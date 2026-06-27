# ADR-002: Per-Project Intelligence Model

**Date**: 2026-06-20
**Status**: Accepted
**Author**: Claude Code
**Reviewers**: Buck Adams

---

## Context

Phase 2 required a "Project Brain" that aggregates intelligence per project.
A design decision was needed: should intelligence be computed globally (one call for all projects)
or per-project (separate call per project)?

## Decision

**Per-project model**: `ProjectIntelligenceEngine(project_id: int)` — each project gets
its own engine instance, snapshots are keyed by `(project_id, snapshot_date)`.

The company-level view (`CrossProjectIntelligence`) instantiates per-project engines
and aggregates results.

## Consequences

**Positive**:
- Faster individual project queries (no full-table scans across all projects)
- Easy to add project-specific rules without affecting others
- Snapshot history is per-project, enabling individual trend analysis
- Scales to 20+ projects without redesign

**Negative**:
- Company-level views are slower (N per-project queries)
- Cross-project comparisons require aggregation in a separate service

## Cross-Project Solution

`CrossProjectIntelligence` in `services/cross_project/routes.py` iterates over
active projects and calls each `ProjectIntelligenceEngine`, then aggregates.
This is acceptable at 4 projects; may need caching at 20+.

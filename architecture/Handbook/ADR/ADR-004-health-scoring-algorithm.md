# ADR-004: RED/YELLOW/GREEN Health Scoring Algorithm

**Date**: 2026-06-19
**Status**: Accepted
**Author**: Claude Code
**Reviewers**: Buck Adams

---

## Context

A simple, scannable health indicator was needed for projects and the company portfolio.
The health score is shown at the top of every console and drives ntfy alert prioritization.

## Decision

Three-tier scoring based on worst detected risk severity:

```python
def _compute_health(risks):
    if any(r["severity"] == "critical" for r in risks):
        return "RED"
    if any(r["severity"] == "high" for r in risks):
        return "YELLOW"
    return "GREEN"
```

This is intentionally conservative — one critical risk = RED, regardless of how many green signals exist.

## Rationale

In construction, one critical risk (e.g., SCHED-002: critical schedule slip) can derail a project
regardless of how well everything else is running. A blended score (80/100 = Yellow) would mask
critical signals. The "worst wins" model ensures critical issues are never buried.

## Consequences

**Positive**:
- Zero ambiguity — immediate understanding of project state
- Can't be "averaged away" by positive signals
- Aligns with how construction risk is actually managed

**Negative**:
- YELLOW covers a wide range (1 high risk = same as 10 high risks)
- No nuance between "barely yellow" and "almost red"

## Future Improvement

Add `health_factors` array to explain WHY the project is YELLOW/RED,
giving context even when the color is alarming. (Already implemented as of Sprint 4.)

# ADR-003: Evidence-Based Predictions with Confidence Scoring

**Date**: 2026-06-27
**Status**: Accepted
**Author**: Claude Code
**Reviewers**: Buck Adams

---

## Context

Phase 2 Priority 3 required forward-looking risk predictions. The key design question was:
how should the system communicate uncertainty in its predictions?

## Decision

Every prediction includes:
1. **`evidence`** — a list of specific data signals that drove the prediction, each with a `weight`
2. **`confidence`** — float 0.0–1.0 representing signal strength
3. **`confidence_label`** — human-readable (High / Medium / Low) for quick scanning

Confidence is additive:
- Each evidence signal contributes a `confidence_factor` (0.1–0.3)
- Sum is capped at 0.85 (never "certain" from data alone)
- No data → confidence defaults to 0.20–0.25

## Rationale

Construction decisions have real financial consequences. A prediction with no supporting
evidence should never carry the same weight as one with 4 corroborating signals.
The evidence list allows Buck to immediately verify "why does the system think this?"
without having to dig into raw data.

## Consequences

**Positive**:
- Explainable AI — every prediction is auditable
- Low-confidence predictions still surface (useful even at 25% confidence)
- Evidence improves as more data flows in — model improves naturally

**Negative**:
- Confidence scores will be low (0.2–0.5) until Houzz data is extracted
- Additive confidence is a simplification — not a true probabilistic model

## Future Improvement

Once enough historical data exists, replace additive confidence with
Bayesian posterior updates based on actual outcomes vs predictions.

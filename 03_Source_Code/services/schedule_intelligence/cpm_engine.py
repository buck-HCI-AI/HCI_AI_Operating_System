"""
CPM (Critical Path Method) engine — CYCLE49 queue item #4, 2026-07-02.

Real forward/backward-pass float calculation over schedule_relationships. If no
relationships exist for a project (true for every project right now - confirmed
zero dependency data anywhere in project_schedule_items), this does NOT fabricate
a critical path. It reports that explicitly and falls back to a clearly-labeled
date-span estimate, consistent with the platform's "if you don't know, say so"
principle (Handbook Vol I, 1.2).
"""
from datetime import date


def compute_critical_path(activities: list[dict], relationships: list[dict]) -> dict:
    """
    activities: [{"activity_id": str, "title": str, "start_date": date|None, "end_date": date|None}]
    relationships: [{"predecessor_activity_id": str, "successor_activity_id": str,
                      "relationship_type": str, "lag_days": int}]

    Returns dict with per-activity ES/EF/LS/LF/float when a real dependency network
    exists, or a "no_dependency_network" status with a naive date-span fallback.
    """
    if not relationships:
        return _naive_date_span_fallback(activities)

    by_id = {a["activity_id"]: dict(a) for a in activities if a.get("activity_id")}
    for a in by_id.values():
        start, end = a.get("start_date"), a.get("end_date")
        a["duration_days"] = max((end - start).days, 1) if (start and end) else 1

    preds: dict[str, list] = {aid: [] for aid in by_id}
    succs: dict[str, list] = {aid: [] for aid in by_id}
    for r in relationships:
        p, s = r["predecessor_activity_id"], r["successor_activity_id"]
        if p not in by_id or s not in by_id:
            continue  # relationship references an activity not in this project's set - skip, don't crash
        succs[p].append(r)
        preds[s].append(r)

    order = _topological_order(by_id.keys(), preds)
    if order is None:
        return {"status": "error", "detail": "Circular dependency detected in schedule_relationships - cannot compute CPM until the cycle is fixed."}

    # Forward pass: ES/EF
    es, ef = {}, {}
    for aid in order:
        dur = by_id[aid]["duration_days"]
        if not preds[aid]:
            es[aid] = 0
        else:
            es[aid] = max(
                ef[r["predecessor_activity_id"]] + r["lag_days"]
                if r["relationship_type"] == "FS" else ef[r["predecessor_activity_id"]]
                for r in preds[aid]
            )
        ef[aid] = es[aid] + dur

    project_duration = max(ef.values()) if ef else 0

    # Backward pass: LS/LF
    ls, lf = {}, {}
    for aid in reversed(order):
        dur = by_id[aid]["duration_days"]
        if not succs[aid]:
            lf[aid] = project_duration
        else:
            lf[aid] = min(
                ls[r["successor_activity_id"]] - r["lag_days"]
                if r["relationship_type"] == "FS" else ls[r["successor_activity_id"]]
                for r in succs[aid]
            )
        ls[aid] = lf[aid] - dur

    results = []
    for aid in order:
        float_days = ls[aid] - es[aid]
        results.append({
            "activity_id": aid,
            "title": by_id[aid].get("title"),
            "duration_days": by_id[aid]["duration_days"],
            "early_start": es[aid], "early_finish": ef[aid],
            "late_start": ls[aid], "late_finish": lf[aid],
            "float_days": float_days,
            "is_critical": float_days == 0,
        })

    critical_path = [r["activity_id"] for r in results if r["is_critical"]]
    return {
        "status": "ok",
        "dependency_network": True,
        "project_duration_days": project_duration,
        "critical_path_activity_ids": critical_path,
        "activities": results,
    }


def _naive_date_span_fallback(activities: list[dict]) -> dict:
    """No predecessor/successor data exists. Report that plainly instead of inventing
    a critical path - this is a date-range span, NOT a logic-driven critical path."""
    dated = [a for a in activities if a.get("start_date") and a.get("end_date")]
    if not dated:
        return {"status": "no_data", "dependency_network": False,
                "detail": "No schedule items with both start and end dates - cannot even estimate a span."}
    earliest = min(a["start_date"] for a in dated)
    latest = max(a["end_date"] for a in dated)
    longest = max(dated, key=lambda a: (a["end_date"] - a["start_date"]).days)
    return {
        "status": "no_dependency_network",
        "dependency_network": False,
        "detail": "No predecessor/successor data exists for this project's schedule - a real "
                  "logic-driven critical path cannot be computed. Showing the overall date span "
                  "instead. This is NOT a critical path; it's the earliest start to latest end "
                  "across all scheduled activities.",
        "date_span_days": (latest - earliest).days,
        "span_start": earliest.isoformat(),
        "span_end": latest.isoformat(),
        "longest_single_activity": {
            "activity_id": longest.get("activity_id"), "title": longest.get("title"),
            "duration_days": (longest["end_date"] - longest["start_date"]).days,
        },
    }


def _topological_order(activity_ids, preds: dict) -> list | None:
    """Kahn's algorithm. Returns None if a cycle exists."""
    in_degree = {aid: len(preds[aid]) for aid in activity_ids}
    queue = [aid for aid, d in in_degree.items() if d == 0]
    order = []
    remaining_preds = {aid: list(preds[aid]) for aid in activity_ids}
    succs_lookup: dict[str, list[str]] = {aid: [] for aid in activity_ids}
    for aid, rels in preds.items():
        for r in rels:
            succs_lookup.setdefault(r["predecessor_activity_id"], []).append(aid)

    while queue:
        aid = queue.pop(0)
        order.append(aid)
        for succ_id in succs_lookup.get(aid, []):
            remaining_preds[succ_id] = [r for r in remaining_preds[succ_id] if r["predecessor_activity_id"] != aid]
            if not remaining_preds[succ_id]:
                queue.append(succ_id)

    if len(order) != len(list(activity_ids)):
        return None  # cycle
    return order

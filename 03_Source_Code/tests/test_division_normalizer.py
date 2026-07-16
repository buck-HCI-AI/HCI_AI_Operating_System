"""
Division Normalizer — Test Suite
Pure-function tests, no DB/Drive/API dependency. Verifies every real
csi_division label observed live on 1355R (via GET /gateway/project/1355R/pm
on 2026-07-16, see DISCREPANCY_MIGRATION_AUDIT_2026-07-16.md) normalizes
correctly, and that the two real unresolved records are never silently
auto-reassigned.

Run from: 03_Source_Code/
    python3 tests/test_division_normalizer.py
"""
import sys, os, json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "services", "bid_leveling"))
from division_normalizer import normalize_division_label, DIVISION_LABEL_MAP, UNRESOLVED_LABELS

RESULTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_results_division_normalizer.json")

# Every real distinct csi_division value + package count observed live on
# 1355R via GET /gateway/project/1355R/pm, 2026-07-16.
REAL_LIVE_LABELS = {
    "03 — Concrete": 1, "04 — Masonry": 1, "05 — Metals": 1,
    "06 — Wood & Plastic": 1, "06 — Woods and Plastics": 1,
    "07 — Thermal & Moisture": 3, "09 — Finishes": 7,
    "10 — Specialties — Furnishings": 1, "10 — Specialties — Special Construction": 1,
    "13 — Insulation": 4, "14 — Roofing": 3, "5 — Waterproofing": 1,
    "Di — Division 10 - Specialties": 1, "Di — Division 11 - Equipment & Appliances": 3,
    "Di — Division 12 - Furnishings": 1, "Di — Division 13 - Special Construction": 3,
    "Di — Division 15 - Mechanical": 2, "Di — Division 16 - Electrical": 6,
    "Di — Division 2 - Site Work": 1, "Di — Division 3 - Concrete": 2,
    "Di — Division 32 - Landscaping": 3, "Di — Division 4 - Masonry": 1,
    "Di — Division 5 - Metals": 3, "Di — Division 6 - Woods and Plastics": 5,
    "Di — Division 8 - Windows & Doors": 6, "Di — Division 9 - Finishes": 13,
    "Division 11 - Equipment/Appliances": 1, "Division 13 - Special Construction": 1,
    "Division 15 - Mechanical": 2, "Division 16 - Electrical": 5,
    "Division 2 - Site Work": 9, "Division 3 - Concrete": 6,
    "Division 4 - Masonry": 4, "Division 5 - Metals": 5,
    "Division 5 - Metals - Ornimental ": 2, "Division 6 - Wood and Plastic": 10,
    "Division 7 - Thermal and Moisture": 8, "Division 8 - Doors and Windows": 5,
    "Division 9 - Finishes": 4, "Division 9 - Finishes ": 2,
    "Division7 - Thermal and moisture": 1, "Division8-  Glass": 1,
    "d": 1, "wr — wrong job files": 2,
}


def run():
    results = {"passed": 0, "failed": 0, "failures": []}

    # Every real live label must resolve without raising, and unresolved
    # ones must return None rather than a guessed division.
    for label, count in REAL_LIVE_LABELS.items():
        try:
            result = normalize_division_label(label)
        except KeyError as e:
            results["failed"] += 1
            results["failures"].append(f"raised for real live label {label!r}: {e}")
            continue

        if label in UNRESOLVED_LABELS:
            if result is not None:
                results["failed"] += 1
                results["failures"].append(
                    f"{label!r} should be unresolved (None), got {result!r}"
                )
                continue
        else:
            if result is None:
                results["failed"] += 1
                results["failures"].append(f"{label!r} resolved to None unexpectedly")
                continue
        results["passed"] += 1

    # An unfamiliar label must raise, not silently guess.
    try:
        normalize_division_label("Some Brand New Label Never Seen Before")
        results["failed"] += 1
        results["failures"].append("unfamiliar label did not raise KeyError")
    except KeyError:
        results["passed"] += 1

    # Real coverage check: every REAL_LIVE_LABELS key must be in either
    # DIVISION_LABEL_MAP or UNRESOLVED_LABELS - no silent gaps.
    covered = set(DIVISION_LABEL_MAP) | set(UNRESOLVED_LABELS)
    missing = set(REAL_LIVE_LABELS) - covered
    if missing:
        results["failed"] += 1
        results["failures"].append(f"real live labels with no mapping at all: {missing}")
    else:
        results["passed"] += 1

    print(f"Passed: {results['passed']}, Failed: {results['failed']}")
    for f in results["failures"]:
        print("  FAIL:", f)

    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)

    return results["failed"] == 0


if __name__ == "__main__":
    ok = run()
    sys.exit(0 if ok else 1)

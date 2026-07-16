"""
Normalizes the real, messy `bid_packages.csi_division` values found live on
1355R (see DISCREPANCY_MIGRATION_AUDIT_2026-07-16.md) to the canonical
Division+Letter scheme (bid_leveling_service.CANONICAL_DIVISION_TREE). Pure
mapping function - does not touch the DB. Building the normalization here
first, as a real reviewable artifact, rather than writing it directly against
bid_packages, since that table also contains real cross-project contamination
(task in SESSION_CHECKPOINT) that needs Buck's decision before anything
writes to it.

Division 07's real sub-packages (Waterproofing/Insulation/Roofing) are kept
as their own canonical keys ("07A_Insulation", "07B_Roofing") per Buck's
2026-07-09 canonical folder directive - they are correct sub-packages, not
contamination, and were previously misdiagnosed as a bug by a prior agent.
Waterproofing has no dedicated canonical key in CANONICAL_DIVISION_TREE
(closest real fit is 03C_Waterproofing-Foundation Drainage under Concrete,
per the tree's own structure) - mapped there rather than invented.

UNRESOLVED_LABELS are real records that should NOT be silently reassigned to
any division - they need a human decision (real cross-project files, or a
truncated/garbled write), consistent with the standing rule against making
that call unilaterally.
"""
from typing import Optional

# Raw label -> canonical CANONICAL_DIVISION_TREE key. Built from every real
# distinct csi_division value observed live on 1355R via
# GET /gateway/project/1355R/pm on 2026-07-16 (40 packages, 40 distinct
# label variants across ~16 real divisions).
DIVISION_LABEL_MAP: dict[str, str] = {
    "03 — Concrete": "03_Concrete",
    "Di — Division 3 - Concrete": "03_Concrete",
    "Division 3 - Concrete": "03_Concrete",
    "04 — Masonry": "04_Masonry",
    "Di — Division 4 - Masonry": "04_Masonry",
    "Division 4 - Masonry": "04_Masonry",
    "05 — Metals": "05_Metals",
    "Di — Division 5 - Metals": "05_Metals",
    "Division 5 - Metals": "05_Metals",
    "Division 5 - Metals - Ornimental ": "05_Metals",
    "06 — Wood & Plastic": "06_Carpentry",
    "06 — Woods and Plastics": "06_Carpentry",
    "Di — Division 6 - Woods and Plastics": "06_Carpentry",
    "Division 6 - Wood and Plastic": "06_Carpentry",
    "07 — Thermal & Moisture": "07_Thermal",
    "Division 7 - Thermal and Moisture": "07_Thermal",
    "Division7 - Thermal and moisture": "07_Thermal",
    "13 — Insulation": "07A_Insulation",
    "14 — Roofing": "07B_Roofing",
    "5 — Waterproofing": "03C_Waterproofing-Foundation Drainage",
    "Di — Division 8 - Windows & Doors": "08_Openings",
    "Division 8 - Doors and Windows": "08_Openings",
    "Division8-  Glass": "08E_Glass & Mirrors",
    "09 — Finishes": "09_Finishes",
    "Di — Division 9 - Finishes": "09_Finishes",
    "Division 9 - Finishes": "09_Finishes",
    "Division 9 - Finishes ": "09_Finishes",  # real trailing-space variant
    "10 — Specialties — Furnishings": "10_Specialties",
    "10 — Specialties — Special Construction": "10_Specialties",
    "Di — Division 10 - Specialties": "10_Specialties",
    "Di — Division 13 - Special Construction": "10_Specialties",
    "Division 13 - Special Construction": "10_Specialties",
    "Di — Division 12 - Furnishings": "10_Specialties",
    "Di — Division 11 - Equipment & Appliances": "11_Equipment",
    "Division 11 - Equipment/Appliances": "11_Equipment",
    "Di — Division 15 - Mechanical": "15_Mechanical",
    "Division 15 - Mechanical": "15_Mechanical",
    "Di — Division 16 - Electrical": "16_Electrical",
    "Division 16 - Electrical": "16_Electrical",
    "Di — Division 2 - Site Work": "32_Site",
    "Division 2 - Site Work": "32_Site",
    "Di — Division 32 - Landscaping": "32_Site",
}

# Real records that must NOT be silently normalized - each needs a human
# decision, not an automated reassignment.
UNRESOLVED_LABELS: dict[str, str] = {
    "wr — wrong job files": (
        "Real cross-project contamination - 2 packages belonging to other "
        "Hendrickson projects (30 St Finnbar, 813 McSkimming) sitting in "
        "1355R's table. Needs Buck's decision on disposition, see "
        "DISCREPANCY_MIGRATION_AUDIT_2026-07-16.md."
    ),
    "d": (
        "Single-character csi_division, almost certainly a truncated write. "
        "1 real package ('Division 7 - Thermal and Insulation') - needs "
        "manual confirmation of intended division before normalizing."
    ),
}


def normalize_division_label(raw: str) -> Optional[str]:
    """
    Returns the canonical CANONICAL_DIVISION_TREE key for a raw
    csi_division string, or None if it's a real unresolved record (see
    UNRESOLVED_LABELS) that must not be auto-reassigned.

    Raises KeyError if given a label not seen in the live 1355R data this
    was built from - deliberately strict rather than guessing at a mapping
    for an unfamiliar label. Extend DIVISION_LABEL_MAP with real evidence
    before widening coverage.
    """
    if raw in UNRESOLVED_LABELS:
        return None
    if raw in DIVISION_LABEL_MAP:
        return DIVISION_LABEL_MAP[raw]
    raise KeyError(
        f"No real mapping for csi_division={raw!r} - add it to "
        "DIVISION_LABEL_MAP (or UNRESOLVED_LABELS if it needs a human "
        "decision) with real evidence before normalizing, don't guess."
    )

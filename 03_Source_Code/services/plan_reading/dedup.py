"""
Duplicate-detection for Drive plan/drawing folders - groundwork for item 3
of BC's Template Build Audit ("read the whole drawings folder every time").

Real problem found 2026-07-16 while scoping item 3: 1355 Riverside's Drive
has multiple exact-duplicate large PDFs sitting under different names/paths
- e.g. two files both named some variant of "1355 Permit Drawing Set" at
identical byte size (25,541,753 bytes) in different folders, and a file
literally named "Copy of Progress Drawing set 2-11-26.pdf" alongside the
original (both 5,736,617 bytes). A plan-read step that blindly reads every
file in the folder every time would burn cost/time re-analyzing the same
document multiple times under different names, and could produce
contradictory findings if the two copies have subtly diverged.

This does NOT touch any Drive files - read-only detection only. Also does
NOT auto-resolve which copy is canonical - that's a Buck judgment call in
most cases (matches the existing pattern of flagging duplicate SOW/tracker
files rather than silently picking one, per project_hci_canonical
duplicate-handling precedent).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "drive_intelligence"))
from drive_client import walk_folder_tree


def find_duplicate_files(folder_id: str, min_size_bytes: int = 100_000) -> dict:
    """
    Walks a Drive folder tree and groups files that share an identical byte
    size - a strong duplicate signal for large binary files (PDFs, docx)
    where a coincidental size match across genuinely different documents is
    very unlikely. Ignores files below min_size_bytes (default 100KB) since
    small files (short text notes, tiny images) collide on size far more
    often without being real duplicates.

    Returns {"total_files": int, "duplicate_groups": [...], "duplicate_count": int,
    "potential_wasted_bytes": int}. Each duplicate_groups entry is
    {"size_bytes": int, "files": [{"name","id","path"}, ...]}.
    """
    all_items = walk_folder_tree(folder_id)
    files = [
        f for f in all_items
        if "folder" not in f.get("mimeType", "")
        and int(f.get("size") or 0) >= min_size_bytes
    ]

    by_size: dict[int, list] = {}
    for f in files:
        size = int(f.get("size") or 0)
        by_size.setdefault(size, []).append({
            "name": f.get("name"),
            "id": f.get("id"),
            "path": f.get("_path"),
        })

    duplicate_groups = [
        {"size_bytes": size, "files": group}
        for size, group in sorted(by_size.items(), key=lambda kv: -kv[0])
        if len(group) > 1
    ]

    duplicate_count = sum(len(g["files"]) - 1 for g in duplicate_groups)
    wasted_bytes = sum(g["size_bytes"] * (len(g["files"]) - 1) for g in duplicate_groups)

    return {
        "folder_id": folder_id,
        "total_files_scanned": len(files),
        "duplicate_groups": duplicate_groups,
        "duplicate_group_count": len(duplicate_groups),
        "duplicate_file_count": duplicate_count,
        "potential_wasted_bytes": wasted_bytes,
    }


def select_canonical_files(folder_id: str, min_size_bytes: int = 100_000) -> dict:
    """
    Returns a deduplicated file list for the plan-read step: one file per
    duplicate group, preferring paths that don't contain "Archived" (the
    real, verified pattern in 1355R's Drive - 2026-07-16 audit confirmed
    every one of 47 duplicate groups has at least one copy under an
    "Archived" folder, and the other copy is either the live "Master Plan
    Set" file or a loose non-archived file at the Drawings root). This is a
    mechanical path-based rule, not content inspection - if a group has no
    non-Archived copy (fully archived, no live replacement), the file is
    excluded and flagged separately rather than guessed at.

    Read-only - does not touch, move, or rename anything in Drive.
    """
    dup_result = find_duplicate_files(folder_id, min_size_bytes)
    all_items = walk_folder_tree(folder_id)
    non_dup_files = [
        f for f in all_items
        if "folder" not in f.get("mimeType", "")
        and int(f.get("size") or 0) >= min_size_bytes
    ]

    excluded_ids = set()
    canonical = []
    fully_archived = []

    for group in dup_result["duplicate_groups"]:
        candidates = [f for f in group["files"] if "Archived" not in (f["path"] or "")]
        for f in group["files"]:
            excluded_ids.add(f["id"])
        if candidates:
            canonical.append(candidates[0])
        else:
            fully_archived.append(group["files"])

    for f in non_dup_files:
        if f["id"] not in excluded_ids:
            canonical.append({"name": f["name"], "id": f["id"], "path": f.get("_path")})

    return {
        "folder_id": folder_id,
        "canonical_file_count": len(canonical),
        "canonical_files": canonical,
        "fully_archived_groups_excluded": fully_archived,
    }

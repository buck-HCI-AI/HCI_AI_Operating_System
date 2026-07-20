"""
Draft-mode bid leveling pipeline — Buck's decision 2026-07-16 ("draft-mode with
validation gates first"), resolving a real disagreement between BC (wire the
proven bid_extractor/bid_level_analyzer pipeline straight to WF-007 production)
and GBT (called that "the most dangerous recommendation" given the pipeline's
real failure history — wrong folder pointers, contamination, false completions
— and proposed draft-mode + hard validation gates instead).

This module is the connective tissue GBT described: given a project+division
with current is_latest bids in drive_bids, run them through the already-proven
extraction/leveling AI pipeline (bid_extractor.py, bid_level_analyzer.py — both
independently matched human judgment on real Div 03/Div 07 1355R bids the night
of 2026-07-15/16), apply hard validation gates, and either write a clearly
labeled DRAFT Google Doc or route to the approval queue with the specific
failure reason. Never writes to the canonical Google Sheet Bid Tracker — that
remains a human-reviewed, human-triggered action.
"""
import sys, os, re, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "integrations"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "drive_intelligence"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "plan_reading"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "approval_queue"))

import psycopg2, psycopg2.extras
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

from drive_bid_reader import _is_outbound_not_a_bid, scan_project_bids
from bid_extractor import extract_bid
from bid_level_analyzer import analyze_bid_leveling
from budget_generator import generate_bid_leveling_gold_standard
from drive_client import create_google_doc_from_markdown, copy_file
from approval_queue_service import ApprovalQueueService

DB = dict(
    host=os.environ.get("POSTGRES_HOST", "localhost"),
    port=int(os.environ.get("POSTGRES_PORT", 5432)),
    dbname=os.environ.get("POSTGRES_DB", "hci_os"),
    user=os.environ.get("POSTGRES_USER", "hci_admin"),
    password=os.environ.get("POSTGRES_PASSWORD", ""),
)


def _pg():
    return psycopg2.connect(cursor_factory=psycopg2.extras.RealDictCursor, **DB)


def _gate_fail(reason: str, detail: dict, project_id: int, division_num: str) -> dict:
    """Every gate failure routes to the same approval queue built earlier
    tonight, rather than silently dropping or guessing - a human reviews the
    specific reason, not a raw error."""
    result = ApprovalQueueService.enqueue(
        workflow="draft_bid_pipeline", action_type="leveling_validation_failed",
        target_system="drive_bids", target_id=f"{project_id}:{division_num}",
        target_description=f"Draft leveling gate failed for division {division_num}: {reason}",
        proposed_payload={}, reason=reason, project_id=project_id,
        actor="draft_pipeline", priority="normal", source_data=detail,
    )
    return {"status": "gate_failed", "division_num": division_num, "reason": reason, "detail": detail,
            "queue_id": result.get("queue_id")}


def generate_draft_leveling(project_id: int, division_num: str, division_folder_id: str,
                             division_name: str = None, exact_division_name: str = None) -> dict:
    """
    Draft-mode, validation-gated: reads current is_latest bids for one
    division, runs the proven AI pipeline, and either writes a clearly
    labeled DRAFT Google Doc into division_folder_id or fails a gate and
    routes to the approval queue. Never touches the canonical Sheet tracker.

    exact_division_name (added 2026-07-17): when a division_num actually
    contains multiple non-competing sub-packages (e.g. Div 07's real data has
    "Thermal & Moisture", "Thermal & Moisture — Insulation", "Thermal &
    Moisture — Roofing" as distinct division_name values - a roofer doesn't
    compete against an insulator), pass the exact division_name to scope the
    query to just that sub-group instead of lumping every vendor under the
    division_num together. Division 06 is the cautionary case this exists
    for - it has 3 real sub-packages with NO division_name signal to split
    on, which is why it was correctly skipped rather than force-lumped.
    """
    with _pg() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM projects WHERE id=%s", (project_id,))
            proj = cur.fetchone()
            if not proj:
                return {"status": "error", "reason": f"project {project_id} not found"}

            if exact_division_name:
                cur.execute("""
                    SELECT id, division_num, division_name, vendor_name, file_id, file_name,
                           bid_amount, bid_date
                    FROM drive_bids
                    WHERE project_id=%s AND division_num=%s AND division_name=%s AND is_latest=TRUE
                    ORDER BY vendor_name
                """, (project_id, division_num, exact_division_name))
            else:
                cur.execute("""
                    SELECT id, division_num, division_name, vendor_name, file_id, file_name,
                           bid_amount, bid_date
                    FROM drive_bids
                    WHERE project_id=%s AND division_num=%s AND is_latest=TRUE
                    ORDER BY vendor_name
                """, (project_id, division_num))
            bids = [dict(r) for r in cur.fetchall()]

    if not bids:
        return _gate_fail("no is_latest bids found for this project+division", {}, project_id, division_num)

    # Real bug found live 2026-07-17: this used to be
    # `division_name or bids[0]["division_name"] or division_num`, which
    # ALWAYS preferred the caller's generic division_name (used only for
    # query-scoping when exact_division_name isn't given) over the real,
    # specific sub-group name - even when exact_division_name correctly
    # scoped the query. Two Div 08 sub-group calls (Windows, Door Hardware)
    # both landed on the same generic "Windows & Doors" doc title as a
    # result, so the second run's trash-prior-draft step trashed the first
    # run's real doc, thinking it was a duplicate of itself. exact_division_name
    # (or the real per-bid value) must always win when present.
    div_name = exact_division_name or bids[0]["division_name"] or division_name or division_num
    # Found 2026-07-17: real division_name values contain an em-dash
    # ("Thermal & Moisture — Roofing") which crashes create_google_doc_from_markdown -
    # the filename goes into a raw HTTP header, and Python's http.client only
    # accepts latin-1 there. Sanitize for the DOC NAME only; the real
    # division_name (with the em-dash intact) still goes into the doc's own
    # markdown content and the DB query, so no information is lost, only the
    # filename is made header-safe.
    div_name_safe = div_name.replace("—", "-")

    # Gate 1 — contamination: every file must not match the known
    # not-a-bid filename pattern (the fix behind BL-DEFECT-05 tonight).
    contaminated = [b for b in bids if _is_outbound_not_a_bid(b["file_name"] or "")]
    if contaminated:
        return _gate_fail(
            "contamination gate failed - outbound/summary artifact classified as a vendor bid",
            {"contaminated_files": [b["file_name"] for b in contaminated]},
            project_id, division_num,
        )

    # Gate 2 — project/division match: every row must actually belong to
    # the requested project+division (defends against the cross-project
    # contamination pattern found earlier this session).
    mismatched = [b for b in bids if b["division_num"] != division_num]
    if mismatched:
        return _gate_fail(
            "project/division match gate failed - row division_num does not match requested division",
            {"mismatched": [{"file": b["file_name"], "division_num": b["division_num"]} for b in mismatched]},
            project_id, division_num,
        )

    # Gate 3 — source freshness: bid_date required and not implausible.
    today = datetime.date.today()
    stale_or_missing = [b for b in bids if not b["bid_date"] or b["bid_date"] > today]
    if stale_or_missing:
        return _gate_fail(
            "source freshness gate failed - missing or future-dated bid_date",
            {"files": [b["file_name"] for b in stale_or_missing]},
            project_id, division_num,
        )

    # Extraction — real AI calls, Gemini-primary/Claude-fallback, same
    # proven pipeline as the overnight 2026-07-15/16 run.
    extracted_bids = {}
    extraction_errors = []
    for b in bids:
        try:
            result = extract_bid(b["file_id"])
        except Exception as e:
            # Found 2026-07-17: a bid file that scan_project_bids() recorded
            # 4 days ago no longer exists in Drive (real 404 - confirmed by
            # querying it directly, not a transient failure) and this raised
            # an unhandled exception that crashed the ENTIRE division's
            # leveling, not just this one vendor. A stale/deleted source file
            # is a data-quality fact about one bid, not a reason to fail
            # every other real bid in the division alongside it.
            extraction_errors.append({"vendor": b["vendor_name"], "file": b["file_name"],
                                       "error": f"source file unreachable: {e}"})
            continue
        if result.get("error") or "extracted" not in result:
            extraction_errors.append({"vendor": b["vendor_name"], "file": b["file_name"],
                                       "error": result.get("error")})
            continue
        ext = result["extracted"]
        if not ext.get("total_amount"):
            extraction_errors.append({"vendor": b["vendor_name"], "file": b["file_name"],
                                       "error": "extraction succeeded but total_amount is missing"})
            continue
        extracted_bids[b["vendor_name"]] = ext

    # Gate 4 — extraction completeness: every bid must extract cleanly.
    if extraction_errors:
        return _gate_fail(
            "extraction completeness gate failed",
            {"errors": extraction_errors, "extracted_ok": list(extracted_bids.keys())},
            project_id, division_num,
        )

    single_bidder = len(extracted_bids) == 1
    scope_matrix, rfis, exclusions = [], [], {}
    biggest_risk = {
        "question": "N/A — single bidder, no competitive comparison to derive a risk from.",
        "dollar_at_stake": "$0",
        "explanation": "Only one real bid exists for this division/package; a scope-gap risk finding "
                        "requires at least two bids to compare.",
    }

    if not single_bidder:
        analysis_result = analyze_bid_leveling(extracted_bids, div_name, div_name)
        if analysis_result.get("error") or "analysis" not in analysis_result:
            return _gate_fail(
                "leveling analysis gate failed",
                {"error": analysis_result.get("error")}, project_id, division_num,
            )
        analysis = analysis_result["analysis"]
        # Gate 5 — analysis completeness.
        if not analysis.get("scope_matrix") or not analysis.get("biggest_risk"):
            return _gate_fail(
                "analysis completeness gate failed - scope_matrix or biggest_risk missing",
                {"analysis_keys": list(analysis.keys())}, project_id, division_num,
            )
        scope_matrix = analysis["scope_matrix"]
        biggest_risk = analysis["biggest_risk"]
        rfis = analysis.get("rfis", [])
        exclusions = analysis.get("exclusions_by_bidder", {})

    bidders = [{"name": v, "total": d.get("total_amount")} for v, d in extracted_bids.items()]
    line_items_by_bidder = {v: d.get("line_items", []) for v, d in extracted_bids.items()}
    recommendation = {
        "text": "No award recommendation — pending human review.",
        "reasoning": "DRAFT — auto-generated, not yet reviewed. No award recommendation is made by this "
                     "pipeline; a human must review the scope matrix and biggest-risk finding before any "
                     "award decision." if not single_bidder else
                     "DRAFT — single bidder, no competitive comparison possible. Human review required "
                     "before treating this as a leveled package.",
    }

    markdown = generate_bid_leveling_gold_standard(
        project_name=proj["name"], division_num=division_num, division_name=div_name,
        bidders=bidders, scope_matrix=scope_matrix, biggest_risk=biggest_risk,
        rfis=rfis, recommendation=recommendation, exclusions=exclusions,
        line_items_by_bidder=line_items_by_bidder,
    )
    markdown = (f"**STATUS: DRAFT — AUTO-GENERATED {datetime.date.today().isoformat()} — "
                f"PENDING HUMAN REVIEW — NOT YET VALIDATED**\n\n" + markdown)

    doc_prefix = f"DRAFT_AUTO_Div{division_num}_{div_name_safe}_"
    doc_name = f"{doc_prefix}{datetime.date.today().isoformat()}"

    # Trash any prior draft(s) for THIS SAME sub-group before writing the new
    # one - found 2026-07-17 during repeat-run testing: re-running on the same
    # day (or any day, since nothing ever checked) silently produced duplicate
    # DRAFT_AUTO docs instead of replacing the stale one. Matches on the full
    # division_num+div_name prefix, not just division_num - a division with
    # real sub-packages (e.g. Div 07's Insulation vs Roofing) writes multiple
    # docs under the same division_num, and matching on division_num alone
    # would trash a sibling sub-package's doc instead of just its own stale
    # one. Recoverable trash, never permanent delete.
    #
    # Found 2026-07-17: Drive's `name contains X` query is NOT a strict
    # substring match - it tokenizes on non-alphanumeric characters, so
    # "DRAFT_AUTO_Div07_Thermal & Moisture_" (the Waterproofing sub-group's
    # prefix, no suffix) loosely matched "DRAFT_AUTO_Div07_Thermal & Moisture
    # - Roofing_..." and "...- Insulation_..." on their shared word tokens,
    # trashing both sibling sub-groups' real docs when Waterproofing's doc
    # was generated. Fetch every doc in the folder and do the prefix
    # comparison ourselves with a real Python .startswith() - exact, not
    # fuzzy, regardless of what Drive's query tokenizer does.
    import requests
    from integrations.credentials import get_google_token
    _token = get_google_token("drive")
    # Buck 2026-07-20: the leveling doc must live in its sub-package folder
    # (07A_Insulation / 07B_Roofing), not flat at the division level, so it sits
    # alongside that sub-package's own vendor bids. Falls back to the division
    # folder when there's no matching sub-package.
    _target_folder = _resolve_subpackage_folder(division_folder_id, div_name, _token)
    _all_docs = requests.get(
        "https://www.googleapis.com/drive/v3/files",
        headers={"Authorization": f"Bearer {_token}"},
        params={"q": f"'{_target_folder}' in parents and trashed=false",
                "fields": "files(id,name)", "supportsAllDrives": "true",
                "includeItemsFromAllDrives": "true", "pageSize": 100},
        timeout=15,
    ).json().get("files", [])
    _prior = [f for f in _all_docs if f["name"].startswith(doc_prefix)]
    for _f in _prior:
        requests.patch(f"https://www.googleapis.com/drive/v3/files/{_f['id']}?supportsAllDrives=true",
                        headers={"Authorization": f"Bearer {_token}", "Content-Type": "application/json"},
                        json={"trashed": True}, timeout=15)

    doc_result = create_google_doc_from_markdown(doc_name, _target_folder, markdown)

    return {
        "status": "draft_created", "project": proj["name"], "division_num": division_num,
        "division_name": div_name, "bidders": [b["name"] for b in bidders],
        "single_bidder": single_bidder, "gates_passed": 4 if single_bidder else 5,
        "doc_id": doc_result.get("id"), "doc_name": doc_result.get("name"),
        "doc_link": f"https://drive.google.com/file/d/{doc_result.get('id')}/view",
        "canonical_tracker_touched": False,
    }


# Canonical top-level division folder names, confirmed 2026-07-17 directly
# against 1355 Riverside's own real Shared Drive 00_Bids folder (the most
# authoritative reference - the written CLAUDE.md spec itself didn't fully
# match real practice, e.g. real Div 10/11/12/13/14 are flat siblings, not
# nested sub-packages). Used only when auto-creating a missing top-level
# folder - matching by number alone (below) still works regardless of name.
_CANONICAL_DIVISION_FOLDER_NAMES = {
    "00": "00_Archived Subcontractor Proposals", "01": "01_General Requirement",
    "02": "02_Site Work", "03": "03_Concrete", "04": "04_Masonry", "05": "05_Metals",
    "06": "06_Wood & Plastic", "07": "07_Thermal & Moisture", "08": "08_Door & Windows",
    "09": "09_Finishes", "10": "10_Specialties", "11": "11_Equipment & Appliances",
    "12": "12_Furnishings", "13": "13_Special Construction", "14": "14_Conveying Systems",
    "15": "15_Mechanical", "16": "16_Electrical", "28": "28_Landscaping", "33": "33_Radon",
}


def _resolve_draft_division_folder(draft_output_folder_id: str, division_num: str, token: str,
                                    create_if_missing: bool = False) -> str | None:
    """Finds the subfolder inside draft_output_folder_id whose name starts with
    division_num (matches by number, not exact name, since the test folder's
    division names don't necessarily match the real bid folder's naming
    convention word-for-word). Returns None if no match and create_if_missing
    is False - caller must not fall back to writing into the real bid folder.

    Retries transient failures (found 2026-07-17: a real 16-division run
    reported divisions 10/15/16/32 as "no matching test folder," but the
    identical lookup succeeded instantly when re-run in isolation seconds
    later - a transient Drive API hiccup during a long run got silently
    treated as "the folder doesn't exist" instead of "the check itself
    failed." Those are different facts and must not be conflated.

    create_if_missing (added 2026-07-17 per Buck's explicit resilience-test
    request): a genuine "no folder exists" result previously meant that
    division silently never got a draft again, forever - deleting a whole
    top-level division folder (verified live, Div 05 test) did not
    self-heal on the next run. Since draft_output_folder_id is already
    known-safe (the caller resolved it once, from the project row, before
    ever reaching here), auto-creating a missing division subfolder inside
    it is safe - it never touches the real bid folder, only the test one."""
    import requests, time
    last_error = None
    for attempt in range(3):
        try:
            r = requests.get(
                "https://www.googleapis.com/drive/v3/files",
                headers={"Authorization": f"Bearer {token}"},
                params={"q": f"'{draft_output_folder_id}' in parents and trashed=false and "
                              f"mimeType='application/vnd.google-apps.folder'",
                        "fields": "files(id,name)", "supportsAllDrives": "true",
                        "includeItemsFromAllDrives": "true", "pageSize": 100},
                timeout=15,
            )
            r.raise_for_status()
            files = r.json().get("files", [])
            for f in files:
                if re.match(rf"^0*{division_num}[_\s]", f["name"]) or f["name"].split("_")[0].lstrip("0") == division_num.lstrip("0"):
                    return f["id"]
            if not create_if_missing:
                return None  # real answer: the API call worked, no match exists
            name = _CANONICAL_DIVISION_FOLDER_NAMES.get(division_num, f"{division_num}_Division")
            created = requests.post(
                "https://www.googleapis.com/drive/v3/files?supportsAllDrives=true",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"name": name, "mimeType": "application/vnd.google-apps.folder",
                      "parents": [draft_output_folder_id]},
                timeout=15,
            ).json()
            return created["id"]
        except Exception as e:
            last_error = e
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"Could not resolve test folder for division {division_num} after 3 attempts - "
                        f"last error: {last_error}. Not treating this as 'no folder exists.'")


def _resolve_subpackage_folder(division_folder_id: str, division_name: str, token: str) -> str:
    """Buck 2026-07-20: within a multi-sub-package division, bids/leveling docs
    must land in the RIGHT sub-package folder (insulation bids in 07A_Insulation,
    roofing in 07B_Roofing), not flat at the division level. When division_name
    carries a sub-package suffix (text after an em-dash, e.g. "Thermal & Moisture
    — Insulation"), find the matching "NNx_" sub-package sub-folder inside the
    division folder and return it. Falls back to division_folder_id when there's
    no suffix or no confident match - so this is never worse than the old flat
    behavior, only better where a sub-package folder clearly matches."""
    import requests, re
    if not division_name or "—" not in division_name:
        return division_folder_id
    suffix = division_name.split("—")[-1].strip()
    if not suffix:
        return division_folder_id
    try:
        subs = requests.get(
            "https://www.googleapis.com/drive/v3/files",
            headers={"Authorization": f"Bearer {token}"},
            params={"q": f"'{division_folder_id}' in parents and trashed=false and "
                          f"mimeType='application/vnd.google-apps.folder'",
                    "fields": "files(id,name)", "supportsAllDrives": "true",
                    "includeItemsFromAllDrives": "true", "pageSize": 100},
            timeout=15,
        ).json().get("files", [])
    except Exception:
        return division_folder_id

    def _key(name):  # strip the "07A_" code prefix, lowercase the rest
        m = re.match(r"^\d{2}[A-Za-z]?[_ ]+(.*)$", name)
        return (m.group(1) if m else name).lower()

    def _wmatch(a, b):
        # whole-word match, or one word is a >=4-char prefix of the other
        # ("paint"~"painting"). NOT a raw substring test - that wrongly matched
        # "roofing" inside "waterproofing" (real bug found 2026-07-20).
        if a == b:
            return True
        lo, hi = (a, b) if len(a) <= len(b) else (b, a)
        return len(lo) >= 4 and hi.startswith(lo)

    suf_words = [w for w in re.split(r"[^a-z0-9]+", suffix.lower()) if len(w) > 2]
    for f in subs:
        if not re.match(r"^\d{2}[A-Za-z][_ ]", f["name"]):  # only real sub-package folders
            continue
        fk_words = [w for w in re.split(r"[^a-z0-9]+", _key(f["name"])) if len(w) > 2]
        if any(_wmatch(sw, fw) for sw in suf_words for fw in fk_words):
            return f["id"]
    return division_folder_id


def _get_or_create_vendor_subfolder(parent_folder: str, vendor_name: str, token: str) -> str:
    """One folder per vendor within a division, matching HCI's canonical
    structure ("split further by subcontractor name - one folder per vendor
    for their bid documents", Project Folder Organization.docx). Found
    2026-07-17: bids were landing flat in the division folder instead of
    per-vendor - fixed so a vendor with multiple real documents (e.g. a
    summary + the actual bid) keeps them together under their own name."""
    import requests
    # Escape single quotes for the Drive query - found 2026-07-20: a vendor with
    # an apostrophe ("David's Tile") broke the name='...' clause, so the
    # existence check silently failed and EVERY run created a new duplicate
    # folder (found 18 stacked "David's Tile" dups in 1355R Div 09). Drive's
    # query syntax escapes ' as \'.
    q_name = vendor_name.replace("\\", "\\\\").replace("'", "\\'")
    r = requests.get(
        "https://www.googleapis.com/drive/v3/files",
        headers={"Authorization": f"Bearer {token}"},
        params={"q": f"'{parent_folder}' in parents and trashed=false and "
                      f"mimeType='application/vnd.google-apps.folder' and name='{q_name}'",
                "fields": "files(id)", "supportsAllDrives": "true",
                "includeItemsFromAllDrives": "true"},
        timeout=15,
    ).json().get("files", [])
    if r:
        return r[0]["id"]
    created = requests.post(
        "https://www.googleapis.com/drive/v3/files?supportsAllDrives=true",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"name": vendor_name, "mimeType": "application/vnd.google-apps.folder", "parents": [parent_folder]},
        timeout=15,
    ).json()
    return created["id"]


def _archive_superseded_bids(project_id: int, division_num: str, target_folder: str,
                              draft_output_folder_id: str, token: str) -> dict:
    """Buck's explicit standing rule, 2026-07-17: when a vendor submits a revised
    bid, the new one becomes is_latest and the OLD file must be physically moved
    out of the vendor's active folder into a real archive location - not left
    sitting inline (confusing - two different dollar amounts in one folder with
    no way to tell which is current) and not just flagged in the DB. Matches
    real 1355R's own Shared Drive, which has exactly this: a top-level
    "00_Archived Subcontractor Proposals" folder. Root-caused by the Epic
    Custom Glass case found this session: an earlier partial quote stayed
    sitting in the vendor's active folder after a later complete bid superseded
    it, because _copy_division_bids_into_test_folder only ever copies files IN
    and never removes what's already there once a bid stops being is_latest.

    Scoped to non-latest bids for this vendor whose file is currently found
    sitting in the vendor's ACTIVE subfolder (not already archived) - moves it,
    doesn't copy it, so it exists in exactly one place at a time."""
    import requests
    archive_root = _get_or_create_vendor_subfolder(draft_output_folder_id,
                                                     "00_Archived Subcontractor Proposals", token)
    with psycopg2.connect(**DB) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT file_name, vendor_name FROM drive_bids
                WHERE project_id=%s AND division_num=%s AND is_latest=FALSE
                  AND vendor_name IS NOT NULL AND file_name IS NOT NULL
            """, (project_id, division_num))
            stale = cur.fetchall()

    archived, skipped = [], []
    vendor_folders: dict[str, str] = {}
    archive_vendor_folders: dict[str, str] = {}
    for b in stale:
        vendor = b["vendor_name"]
        if vendor not in vendor_folders:
            r = requests.get(
                "https://www.googleapis.com/drive/v3/files",
                headers={"Authorization": f"Bearer {token}"},
                params={"q": f"'{target_folder}' in parents and trashed=false and "
                              f"mimeType='application/vnd.google-apps.folder' and name='{vendor}'",
                        "fields": "files(id)", "supportsAllDrives": "true",
                        "includeItemsFromAllDrives": "true"},
                timeout=15,
            ).json().get("files", [])
            vendor_folders[vendor] = r[0]["id"] if r else None
        vfolder = vendor_folders[vendor]
        if not vfolder:
            continue  # vendor never had an active folder here - nothing to archive

        match = requests.get(
            "https://www.googleapis.com/drive/v3/files",
            headers={"Authorization": f"Bearer {token}"},
            params={"q": f"'{vfolder}' in parents and trashed=false and name='{b['file_name']}'",
                    "fields": "files(id)", "supportsAllDrives": "true",
                    "includeItemsFromAllDrives": "true"},
            timeout=15,
        ).json().get("files", [])
        if not match:
            skipped.append(f"{vendor}/{b['file_name']} (not in active folder - already archived or never copied)")
            continue

        if vendor not in archive_vendor_folders:
            archive_vendor_folders[vendor] = _get_or_create_vendor_subfolder(archive_root, vendor, token)
        avfolder = archive_vendor_folders[vendor]

        fid = match[0]["id"]
        requests.patch(
            f"https://www.googleapis.com/drive/v3/files/{fid}",
            headers={"Authorization": f"Bearer {token}"},
            params={"addParents": avfolder, "removeParents": vfolder, "supportsAllDrives": "true"},
            timeout=15,
        )
        archived.append(f"{vendor}/{b['file_name']}")
    return {"archived": archived, "skipped": skipped}


def _copy_division_bids_into_test_folder(project_id: int, division_num: str, target_folder: str) -> dict:
    """Copies (never moves) every is_latest real bid file for this division into
    a per-vendor subfolder under the test folder division, alongside the
    generated leveling doc - Buck's explicit requirement 2026-07-17: real bids
    "should be put into the test drive... they have to stay in the share
    drive," organized "with the company name" per vendor, matching HCI's
    canonical structure. Uses copy_file() (Drive's native files.copy), which
    never touches the source. Skips any file whose exact name already exists
    in its vendor subfolder, so re-running daily doesn't re-copy or duplicate
    what's already there. bid_date (the real received date, already extracted
    per bid) is preserved in drive_bids and shown in the leveling doc - not
    re-encoded into the filename, since most real vendor filenames already
    carry a date and re-stamping risks contradicting the original name."""
    import requests
    from integrations.credentials import get_google_token
    token = get_google_token("drive")
    with psycopg2.connect(**DB) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT file_id, file_name, vendor_name, division_name, bid_date FROM drive_bids
                WHERE project_id=%s AND division_num=%s AND is_latest=TRUE
            """, (project_id, division_num))
            bids = cur.fetchall()

    # Buck 2026-07-20: file each vendor into its SUB-PACKAGE folder (insulation
    # vendors in 07A_Insulation, roofing in 07B_Roofing), not flat at the
    # division. Keyed by (sub-package folder, vendor) so the same vendor bidding
    # two sub-packages lands in each. Falls back to division level when no
    # sub-package matches.
    subpkg_cache: dict[str, str] = {}
    vendor_folders: dict[tuple, str] = {}
    copied, skipped, errors = [], [], []
    for b in bids:
        vendor = b["vendor_name"] or "Unknown Vendor"
        dn = b.get("division_name") or ""
        if dn not in subpkg_cache:
            subpkg_cache[dn] = _resolve_subpackage_folder(target_folder, dn, token)
        parent = subpkg_cache[dn]
        vkey = (parent, vendor)
        if vkey not in vendor_folders:
            vendor_folders[vkey] = _get_or_create_vendor_subfolder(parent, vendor, token)
        vfolder = vendor_folders[vkey]

        existing = requests.get(
            "https://www.googleapis.com/drive/v3/files",
            headers={"Authorization": f"Bearer {token}"},
            params={"q": f"'{vfolder}' in parents and trashed=false", "fields": "files(name)",
                    "supportsAllDrives": "true", "includeItemsFromAllDrives": "true", "pageSize": 50},
            timeout=15,
        ).json().get("files", [])
        existing_names = {f["name"] for f in existing}

        if not b["file_id"] or b["file_name"] in existing_names:
            skipped.append(f"{vendor}/{b['file_name']}")
            continue
        try:
            copy_file(b["file_id"], vfolder, b["file_name"])
            copied.append(f"{vendor}/{b['file_name']}")
        except Exception as e:
            errors.append({"file": f"{vendor}/{b['file_name']}", "error": str(e)})
    return {"copied": copied, "skipped_already_present": skipped, "errors": errors}


def run_daily_bid_leveling(project_id: int, dry_run: bool = True) -> dict:
    """The actual daily job Buck asked for 2026-07-17: read the project's real
    Shared Drive bid folder (bid_folder_id) for new/updated bids - always safe,
    scan_project_bids() only writes to our own drive_bids table, never to
    Drive - then generate/refresh a draft leveling doc per division with
    current bids, written into draft_output_folder_id (the test folder), never
    into the real Drive. Two separate destinations by design: reading the real
    source of truth is fine, writing anything is not, while the project isn't
    status='active' for live writes.

    dry_run=True (default): runs the real Drive scan (so you see what's out
    there) but does not generate/write any draft docs - matches the
    dry-run-first convention used throughout this file's sibling modules.
    """
    with psycopg2.connect(**DB) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT id, name, bid_folder_id, draft_output_folder_id, status FROM projects WHERE id=%s", (project_id,))
            proj = cur.fetchone()
    if not proj:
        return {"error": f"Project {project_id} not found"}
    if not proj["draft_output_folder_id"]:
        return {"error": f"Project {proj['name']} has no draft_output_folder_id configured - "
                          "refusing to guess where draft docs should go."}

    scan_result = scan_project_bids(project_id, dry_run=False)  # DB-only write, Drive read-only
    if "error" in scan_result:
        return {"project": proj["name"], "scan_result": scan_result, "divisions_processed": []}

    with psycopg2.connect(**DB) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT DISTINCT division_num, division_name FROM drive_bids
                WHERE project_id=%s AND is_latest=TRUE ORDER BY division_num
            """, (project_id,))
            divisions = cur.fetchall()

    if dry_run:
        return {"project": proj["name"], "dry_run": True, "scan_result": scan_result,
                "divisions_found": [dict(d) for d in divisions],
                "note": "Real Drive scan ran and drive_bids is current. No draft docs written - "
                        "run with dry_run=False to generate them into the test folder."}

    from integrations.credentials import get_google_token
    token = get_google_token("drive")
    results = []
    for d in divisions:
        # Real bug found 2026-07-17 via the capstone full-rebuild test: a
        # single Drive OAuth token is fetched once at the top of this
        # function and reused for the entire run. Google access tokens
        # expire after ~1 hour - a run processing 27 real (division,
        # sub-group) pairs with real Claude/Gemini extraction calls per
        # vendor genuinely takes longer than that, so the token expired
        # mid-run (died on Div 09 at 52 minutes elapsed with a real 401
        # Unauthorized) and the whole run was lost, including everything
        # already correctly processed for earlier divisions in that run.
        # `_resolve_draft_division_folder`'s own retry loop doesn't help
        # here - it retries the SAME expired token 3 times, which fails
        # identically every time; a 401 needs a fresh token, not a retry.
        # Fixed by catching the failure per-division (not per-run) and
        # refreshing the token once before retrying just that division -
        # this way a token expiry costs one retried division, not the
        # entire multi-hour run and everything already correctly done in it.
        for attempt in range(2):
            try:
                target_folder = _resolve_draft_division_folder(proj["draft_output_folder_id"], d["division_num"], token,
                                                                 create_if_missing=True)
                if not target_folder:
                    results.append({"division_num": d["division_num"], "division_name": d["division_name"],
                                     "status": "skipped_no_matching_test_folder"})
                    break
                copy_result = _copy_division_bids_into_test_folder(project_id, d["division_num"], target_folder)
                archive_result = _archive_superseded_bids(project_id, d["division_num"], target_folder,
                                                            proj["draft_output_folder_id"], token)
                # exact_division_name must be passed here (found 2026-07-17, before
                # the capstone full-rebuild test): `divisions` is already the
                # DISTINCT (division_num, division_name) pairs - i.e. each real
                # sub-package (Div 06 Cabinetry vs Framing, Div 09's 5 sub-groups,
                # etc.) is already its own row. Without exact_division_name,
                # generate_draft_leveling()'s query only filters by division_num,
                # silently re-merging every sub-group under one division back
                # into a single mixed leveling doc on every run - undoing all the
                # real scope-separation fixes made this session (Axion, Kubed,
                # Div 08, Div 16 Electrical) the next time this job runs.
                doc_result = generate_draft_leveling(project_id, d["division_num"], target_folder, d["division_name"],
                                                      exact_division_name=d["division_name"])
                doc_result["source_bids_copied"] = copy_result
                doc_result["superseded_bids_archived"] = archive_result
                results.append(doc_result)
                break
            except Exception as e:
                is_auth_error = "401" in str(e) or "Unauthorized" in str(e) or "invalid_grant" in str(e)
                if is_auth_error and attempt == 0:
                    token = get_google_token("drive")  # refresh once, then retry this division
                    continue
                results.append({"division_num": d["division_num"], "division_name": d["division_name"],
                                 "status": "error", "detail": str(e)})
                break

    return {"project": proj["name"], "dry_run": False, "scan_result": scan_result,
            "divisions_processed": results}

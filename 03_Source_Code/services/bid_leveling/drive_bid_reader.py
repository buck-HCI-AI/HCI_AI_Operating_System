"""
Drive Bid Reader — HCI AI Operating System

Walks bid division folders in Google Drive, extracts bid amounts from vendor PDFs
using Gemini, and upserts results to the drive_bids table.

Folder structure expected:
  {bid_folder_id}/
    {div_num}_{division_name}/         (e.g. "13_Insulation", "5_Waterproofing")
      {vendor_name}/                   (e.g. "Yeti Insulation")
        bid_proposal.pdf               (most recent PDF = latest bid)
        old_proposal.pdf               (older files = not latest)

Only PDFs and DOCx files are read. The most recently modified file per vendor is
marked is_latest=True; older files for the same vendor are set is_latest=False.
"""
import sys, os, json, re, ssl, urllib.request, urllib.parse, datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "integrations"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))

import psycopg2, psycopg2.extras, certifi
from dotenv import load_dotenv
from typing import Optional

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

from credentials import get_google_token

SSL_CTX  = ssl.create_default_context(cafile=certifi.where())
BASE_URL  = "https://www.googleapis.com/drive/v3"

READABLE_MIME = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.google-apps.document",
    "application/vnd.google-apps.spreadsheet",
}

DB = dict(
    host=os.environ.get("POSTGRES_HOST", "localhost"),
    port=int(os.environ.get("POSTGRES_PORT", 5432)),
    dbname=os.environ.get("POSTGRES_DB", "hci_os"),
    user=os.environ.get("POSTGRES_USER", "hci_admin"),
    password=os.environ.get("POSTGRES_PASSWORD", ""),
)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL   = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")


def _pg():
    return psycopg2.connect(**DB, cursor_factory=psycopg2.extras.RealDictCursor)


def _drive_list(folder_id: str, token: str) -> list:
    params = urllib.parse.urlencode({
        "q": f"'{folder_id}' in parents and trashed=false",
        "fields": "files(id,name,mimeType,modifiedTime,size)",
        "pageSize": 200,
        "supportsAllDrives": "true",
        "includeItemsFromAllDrives": "true",
    })
    req = urllib.request.Request(
        f"{BASE_URL}/files?{params}",
        headers={"Authorization": f"Bearer {token}"}
    )
    with urllib.request.urlopen(req, context=SSL_CTX, timeout=30) as r:
        return json.loads(r.read()).get("files", [])


def _download_bytes(file_id: str, token: str) -> bytes:
    """Download raw file bytes from Drive."""
    url = f"{BASE_URL}/files/{file_id}?alt=media&supportsAllDrives=true"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, context=SSL_CTX, timeout=60) as r:
        return r.read()


def _export_google_doc(file_id: str, token: str, mime: str = "application/vnd.google-apps.document") -> str:
    """
    Export Google Docs/Sheets as text. Found live 2026-07-08 chasing a "1355
    insulation" bid file that errored with HTTP 400: this hardcoded
    mimeType=text/plain, which Drive's export endpoint only supports for Docs -
    a native Google Sheet has no text/plain export target and 400s every time.
    Sheets need text/csv instead; Docs still use text/plain.
    """
    export_mime = "text/csv" if mime == "application/vnd.google-apps.spreadsheet" else "text/plain"
    url = f"{BASE_URL}/files/{file_id}/export?mimeType={export_mime}&supportsAllDrives=true"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, context=SSL_CTX, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def extract_bid_with_gemini(pdf_bytes: bytes, vendor_name: str,
                             project_name: str, div_name: str) -> dict:
    """
    Send PDF bytes to Gemini and extract bid amount, date, scope.
    Returns dict: {bid_amount, bid_date, scope_summary, error?}
    """
    if not GEMINI_API_KEY:
        return {"error": "GEMINI_API_KEY not set"}

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = (
            f"This is a bid proposal PDF for the {div_name} division of {project_name}.\n"
            f"Vendor: {vendor_name}\n\n"
            "Extract the following and return ONLY valid JSON (no markdown, no explanation):\n"
            '{"bid_amount": 123456.00, "bid_date": "YYYY-MM-DD", '
            '"scope_summary": "One sentence describing the scope"}\n\n'
            "Rules:\n"
            "- bid_amount: numeric total (base bid only, no options/alternates), no commas or $\n"
            "- bid_date: use the proposal/estimate date, not today\n"
            "- scope_summary: 1 sentence max, what work is included\n"
            "- If you cannot find a value, use null"
        )
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
                types.Part.from_text(text=prompt),
            ]
        )
        text = response.text.strip()
        # Strip markdown code fences if present
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        data = json.loads(text)
        return data
    except Exception as e:
        return {"error": str(e)}


def extract_bid_with_claude(pdf_bytes: bytes, vendor_name: str,
                             project_name: str, div_name: str) -> dict:
    """
    Fallback for extract_bid_with_gemini when Gemini's free-tier daily quota is
    exhausted (found live 2026-07-08 mid-demo: gemini-3.5-flash capped at 20
    requests/day project-wide, and switching to gemini-2.0-flash didn't help -
    the quota is per-API-key, not per-model). Anthropic is already configured
    and working elsewhere in this system (base.py's ask_claude), so this uses
    the same key/billing rather than depending on Gemini's free tier at all.
    Same input/output contract as extract_bid_with_gemini.
    """
    import base64
    try:
        import anthropic
        from config import settings
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        prompt = (
            f"This is a bid proposal PDF for the {div_name} division of {project_name}.\n"
            f"Vendor: {vendor_name}\n\n"
            "Extract the following and return ONLY valid JSON (no markdown, no explanation):\n"
            '{"bid_amount": 123456.00, "bid_date": "YYYY-MM-DD", '
            '"scope_summary": "One sentence describing the scope"}\n\n'
            "Rules:\n"
            "- bid_amount: numeric total (base bid only, no options/alternates), no commas or $\n"
            "- bid_date: use the proposal/estimate date, not today\n"
            "- scope_summary: 1 sentence max, what work is included\n"
            "- If you cannot find a value, use null"
        )
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "document", "source": {
                        "type": "base64", "media_type": "application/pdf",
                        "data": base64.b64encode(pdf_bytes).decode(),
                    }},
                    {"type": "text", "text": prompt},
                ],
            }],
        )
        text = "".join(b.text for b in response.content if getattr(b, "type", None) == "text").strip()
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        return json.loads(text)
    except Exception as e:
        return {"error": str(e)}


def extract_bid_line_items_with_claude(pdf_bytes: bytes, vendor_name: str,
                                        project_name: str, div_name: str,
                                        known_total: float = None) -> dict:
    """
    2026-07-13, per Buck's explicit directive ("full bid level summaries
    that compare the bid... read every bid") and GBT's gold-standard
    scope-equivalency proposal. extract_bid_with_claude()/_with_gemini()
    above capture only a one-sentence scope_summary - enough to classify a
    bid into a trade bucket (Option B), not enough to explain why two bids
    for the same trade differ by 6x. This asks for the actual itemized
    scope breakdown: what's included, what's explicitly excluded, what's
    priced as an allowance vs. fixed price, and any qualifications - the
    real apples-to-apples comparison data. Same dual-provider pattern as
    the functions above (Claude here since Gemini's free tier is
    unreliable, per extract_bid_with_claude's docstring), same JSON
    contract style. NOT wired into any automatic scan path yet - this is
    infrastructure built ahead of the team-consensus decision on rollout
    scope/sequencing (see LIVE_TEAM_COMMS.md 2026-07-13 15:02 MT), not yet
    invoked against real bid PDFs.
    """
    import base64
    try:
        import anthropic
        from config import settings
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        total_line = (
            f"\nThe vendor's stated bid total is ${known_total:,.2f}. Every included, "
            f"non-allowance line item's amount MUST sum to exactly this total. If some "
            f"of the bid's value isn't broken into its own line item, add one final "
            f"item with category \"Remaining/Unspecified Scope\" and whatever amount "
            f"makes the included items sum to ${known_total:,.2f} exactly. Do not let "
            f"the sum come out higher or lower than this - if you're unsure whether an "
            f"amount is separately priced or already covered elsewhere in the total, "
            f"resolve it by adjusting the Remaining/Unspecified Scope amount, not by "
            f"double-counting or dropping a line.\n"
        ) if known_total else ""
        prompt = (
            f"This is a bid proposal PDF for the {div_name} division of {project_name}.\n"
            f"Vendor: {vendor_name}\n"
            f"{total_line}\n"
            "Extract a detailed line-item scope breakdown and return ONLY valid JSON "
            "(no markdown, no explanation):\n"
            '{"line_items": [{"category": "...", "description": "...", '
            '"included": true, "is_allowance": false, "amount": null, '
            '"qualification_notes": "..."}]}\n\n'
            "Rules:\n"
            "- category: short trade-specific label for each distinct scope item "
            "(e.g. \"Cabinetry - Kitchen\", \"Countertops - Primary Bath\", "
            "\"Flooring - Bedroom 2\")\n"
            "- Extract EVERY distinct scope item/room/category mentioned in the "
            "proposal, not a single overall summary\n"
            "- included: true if this scope is part of the bid, false if the "
            "proposal explicitly excludes or qualifies it out\n"
            "- is_allowance: true if this item is priced as an allowance rather "
            "than a fixed price\n"
            "- amount: numeric line-item dollar amount if broken out separately in "
            "the proposal, else null (covered under the lump-sum total)\n"
            "- qualification_notes: any caveats, conditions, or exclusions noted "
            "for this specific item, else null\n"
            "- If the proposal has no itemized breakdown at all (pure lump sum, no "
            "detail), return a single line_item with category \"Full Scope (lump "
            "sum, no itemized breakdown available)\" and included=true"
        )
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            # 2026-07-13: 4096 was too low for real bids - found live running
            # the full extraction across 1355R: 3 of 77 bids (all with 30-50+
            # real line items - complex electrical/mechanical/finishes scopes)
            # got cut off mid-JSON-string by the token cap, producing invalid
            # JSON the parser correctly rejected rather than silently
            # returning truncated/wrong data. Raised to give genuinely large
            # itemized bids room to complete.
            max_tokens=8192,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "document", "source": {
                        "type": "base64", "media_type": "application/pdf",
                        "data": base64.b64encode(pdf_bytes).decode(),
                    }},
                    {"type": "text", "text": prompt},
                ],
            }],
        )
        text = "".join(b.text for b in response.content if getattr(b, "type", None) == "text").strip()
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        return json.loads(text)
    except Exception as e:
        return {"error": str(e)}


def ingest_bid_line_items(drive_bid_id: int, dry_run: bool = True) -> dict:
    """
    Runs extract_bid_line_items_with_claude() for one drive_bids row and
    (if dry_run=False) inserts the results into bid_line_items. dry_run=True
    (default) returns the extracted items without writing, matching the
    dry-run-first convention used throughout this file (scan_project_bids,
    reclassify_existing_divisions). Idempotent: re-running for the same
    drive_bid_id with dry_run=False replaces that bid's existing line items
    rather than accumulating duplicates.
    """
    with _pg() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, project_id, vendor_name, division_name, file_id, bid_amount FROM drive_bids WHERE id=%s",
                (drive_bid_id,)
            )
            row = cur.fetchone()
    if not row:
        return {"error": f"drive_bids row {drive_bid_id} not found"}

    with _pg() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT project_code FROM projects WHERE id=%s", (row["project_id"],))
            proj = cur.fetchone()
    project_name = proj["project_code"] if proj else str(row["project_id"])

    known_total = float(row["bid_amount"]) if row.get("bid_amount") else None
    token = get_google_token("drive")
    pdf_bytes = _download_bytes(row["file_id"], token)
    result = extract_bid_line_items_with_claude(
        pdf_bytes, row["vendor_name"], project_name, row["division_name"], known_total
    )
    if "error" in result:
        return result

    line_items = result.get("line_items", [])

    # 2026-07-13: found live across the real 1355R extraction run - 26 of 77
    # bids didn't reconcile (line-item sum != the bid's real total), some by
    # six figures. Passing known_total into the prompt (above) reduces this,
    # but an LLM doing arithmetic across 30-50+ line items isn't reliable
    # enough to trust blindly - reconciling in Python is deterministic.
    # Under-itemization (sum too low) is auto-corrected by appending a
    # remainder line, since that's an unambiguous, safe fix. Over-itemization
    # (sum too high) is NOT auto-corrected - which specific item is wrong
    # can't be determined programmatically - it's flagged instead so a human
    # or a future re-extraction resolves it, rather than silently guessing.
    reconciliation = None
    if known_total and line_items:
        included_sum = sum(
            (item.get("amount") or 0) for item in line_items
            if item.get("included", True)
        )
        gap = round(known_total - included_sum, 2)
        if abs(gap) > 1:
            if gap > 0:
                line_items.append({
                    "category": "Remaining/Unspecified Scope [auto-reconciled]",
                    "description": "Programmatically added to reconcile the line-item sum to the vendor's stated total - the extraction did not itemize this portion of the bid.",
                    "included": True, "is_allowance": False, "amount": gap,
                    "qualification_notes": None,
                })
                reconciliation = {"status": "auto_corrected_under_itemized", "gap": gap}
            else:
                reconciliation = {"status": "FLAGGED_over_itemized", "gap": gap,
                                   "note": "Line items sum higher than the vendor's stated total - needs manual review, not auto-corrected."}

    if not dry_run and line_items:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM bid_line_items WHERE drive_bid_id=%s", (drive_bid_id,))
                for item in line_items:
                    cur.execute("""
                        INSERT INTO bid_line_items
                            (drive_bid_id, category, description, included, is_allowance,
                             amount, qualification_notes, extraction_source)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    """, (
                        drive_bid_id, item.get("category", "Unclassified"),
                        item.get("description"), item.get("included", True),
                        item.get("is_allowance", False), item.get("amount"),
                        item.get("qualification_notes"), "claude",
                    ))
            conn.commit()

    return {"drive_bid_id": drive_bid_id, "dry_run": dry_run,
            "line_items_found": len(line_items), "line_items": line_items,
            "reconciliation": reconciliation}


def extract_bid_from_text(text: str, vendor_name: str, file_name: str) -> dict:
    """
    Fallback: extract bid amount from text via regex.
    Used for Google Docs/Sheets where we can export as text without Gemini.

    scope_summary used to unconditionally return f"Extracted from {file_name}"
    regardless of whether extraction succeeded - found live 2026-07-09 when
    Buck caught generated leveling sheets showing that placeholder instead of
    real scope content for every Docs/Sheets-sourced bid, while PDF-sourced
    (Gemini/Claude) bids had real extracted scope. Now pulls an actual text
    excerpt near the matched total, falling back to the first substantive
    line of the document - never just echoes the filename back.
    """
    # Find dollar amounts — look for "total", "grand total", "base bid" patterns first
    # (higher confidence); the bare "$amount" pattern is a last resort and prone to
    # matching an unrelated figure mentioned in the doc, so it's kept separate and
    # flagged as low-confidence via the "confidence" field rather than trusted equally.
    strong_patterns = [
        r"(?:grand\s+total|total\s+base\s+bid|base\s+bid\s+price|total\s+price|total\s+contract\s+price)[^\$\n]*\$?\s*([\d,]+\.?\d*)",
        r"total[:\s]+\$?\s*([\d,]+\.?\d*)",
    ]
    amount = None
    confidence = None
    match_span = None
    for pat in strong_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            try:
                amount = float(m.group(1).replace(",", ""))
                confidence = "high"
                match_span = m.span()
                break
            except ValueError:
                continue
    if amount is None:
        m = re.search(r"\$\s*([\d,]+\.?\d*)\s*(?:dollars?)?(?:\s|$)", text)
        if m:
            try:
                amount = float(m.group(1).replace(",", ""))
                confidence = "low"
                match_span = m.span()
            except ValueError:
                pass

    # Find date
    date_str = None
    date_m = re.search(r"(?:date|dated)[:\s]+(\d{1,2}/\d{1,2}/\d{2,4})", text, re.IGNORECASE)
    if date_m:
        raw = date_m.group(1)
        try:
            for fmt in ("%m/%d/%Y", "%m/%d/%y"):
                try:
                    date_str = datetime.datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
                    break
                except ValueError:
                    continue
        except Exception:
            pass

    # Real scope excerpt: text around the matched total, or the first substantive
    # (non-blank, non-boilerplate-short) line if no amount was found at all.
    scope_summary = None
    if match_span:
        start = max(0, match_span[0] - 150)
        end = min(len(text), match_span[1] + 150)
        excerpt = " ".join(text[start:end].split())
        scope_summary = excerpt[:300]
    else:
        for line in text.splitlines():
            line = line.strip()
            if len(line) > 25 and not line.lower().startswith(file_name.lower()[:15]):
                scope_summary = line[:300]
                break

    return {
        "bid_amount": amount,
        "bid_amount_confidence": confidence,
        "bid_date": date_str,
        "scope_summary": scope_summary,
    }


_DIV_PREFIX_RE = re.compile(r"^(\d+)[_\s-]+(.+)$")
_TRACKER_KEYWORDS = ("level", "tracker", "summary", "audit")


def check_duplicate_tracker_files(bid_folder_id: str, token: str) -> list:
    """
    Found 2026-07-09: Buck kept reporting he still saw old bid-level files and
    duplicate summaries in Drive after a "repair complete" claim - a manual
    sweep found two real cases (1355R's 13_Insulation and 14_Roofing) where an
    old tracker/leveling artifact (a superseded native-Sheet version, a stray
    .url shortcut) sat right next to the current .xlsx tracker. Prior cleanup
    passes checked division-root loose files for duplicates but never made
    this check a standing, automatic part of every scan - it only ran because
    someone manually looked. Wiring it into scan_project_bids() so it runs on
    every routine scan (mining engine, manual triggers) instead of requiring
    a human to notice the same thing again. Does not delete anything - flags
    for review, same as every other data-integrity check in this codebase.
    """
    findings = []
    div_folders = _drive_list(bid_folder_id, token)
    for div_folder in div_folders:
        if "folder" not in div_folder.get("mimeType", ""):
            continue
        if re.match(r"^archive", div_folder["name"], re.IGNORECASE):
            continue
        items = _drive_list(div_folder["id"], token)
        loose_docs = [it for it in items if "folder" not in it.get("mimeType", "")]
        tracker_like = [it for it in loose_docs
                         if any(k in it["name"].lower() for k in _TRACKER_KEYWORDS)]
        if len(tracker_like) > 1:
            findings.append({
                "division": div_folder["name"],
                "files": [{"name": f["name"], "modified": f.get("modifiedTime"), "id": f["id"]} for f in tracker_like],
            })
    return findings


def _log_stale_tracker_alert(project_id: int, project_name: str, findings: list) -> None:
    """Best-effort standing alert - never let this break the actual scan."""
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                title = f"Duplicate bid-tracker files found: {project_name}"
                cur.execute(
                    "SELECT id FROM ai_messages WHERE title = %s AND status NOT IN ('COMPLETE','REJECTED') LIMIT 1",
                    (title,),
                )
                if cur.fetchone():
                    return
                cur.execute("""
                    INSERT INTO ai_messages
                        (source_agent, target_agent, message_type, title, body, status, priority, project_code)
                    VALUES ('bid_leveling_scan', 'buck', 'status_update', %s, %s, 'ISSUED', 'medium', %s)
                """, (title, json.dumps(findings, default=str), project_name))
            conn.commit()
    except Exception:
        pass


# Buck's canonical 16-division folder structure (filed 2026-07-09, CLAUDE.md):
# several divisions contain sub-package folders numbered INDEPENDENTLY of the
# division number - e.g. "5_Waterproofing" is a sub-package of division 07
# (Thermal & Moisture), not a folder for division 5 (which is Metals). When a
# sub-package folder is correctly NESTED inside its parent division folder,
# _walk_vendor_level()'s existing recursion already handles it fine. The bug
# this map fixes is when a sub-package folder sits LOOSE at the TOP LEVEL of
# 00_Bids (a sibling of the real divisions, not nested under its logical
# parent - confirmed live on 1355 Riverside) - it would otherwise zero-pad
# ("5" -> "05") and silently collide with the real division 05 (Metals),
# merging two unrelated trades' bids into one division bucket. Keyed by
# lowercased, whitespace-collapsed sub-package name (not number alone, since
# the same bare number means different things under different parents - "11"
# is Cabinets under division 06 but Equipment & Appliances under division 10).
_SUB_PACKAGE_TO_PARENT_DIVISION = {
    "carpentry":                       ("06", "Wood & Plastic"),
    "cabinets":                        ("06", "Wood & Plastic"),
    "t&g ceiling":                     ("06", "Wood & Plastic"),
    "waterproofing":                   ("07", "Thermal & Moisture"),
    "insulation":                      ("07", "Thermal & Moisture"),
    "roofing":                         ("07", "Thermal & Moisture"),
    "doors/windows exterior":          ("08", "Door & Windows"),
    "interior doors":                  ("08", "Door & Windows"),
    "glazing":                         ("09", "Finishes"),
    "drywall & plaster":               ("09", "Finishes"),
    "tile & stone":                    ("09", "Finishes"),
    "flooring":                        ("09", "Finishes"),
    "paint":                           ("09", "Finishes"),
    "equipment & appliances":          ("10", "Specialties"),
    "furnishings":                     ("10", "Specialties"),
    "special construction":            ("10", "Specialties"),
    "conveying systems":               ("10", "Specialties"),
    "hvac":                            ("15", "Mechanical"),
    "plumbing":                        ("15", "Mechanical"),
    "electric":                        ("16", "Electrical"),
    "low voltage":                     ("16", "Electrical"),
    "solar":                           ("16", "Electrical"),
}


def _sub_package_parent(div_raw: str, division_num: str, division_name: str) -> tuple:
    """If this folder's name matches a known sub-package (by name, not just its
    own leading number, which is ambiguous across parents), reroute it to its
    real parent division instead of colliding with a same-numbered top-level
    division. Returns (division_num, division_name) - unchanged if no match."""
    name_key = division_name.strip().lower()
    match = _SUB_PACKAGE_TO_PARENT_DIVISION.get(name_key)
    if match:
        parent_num, parent_name = match
        if parent_num != division_num:
            return parent_num, f"{parent_name} — {division_name.strip()}"
    return division_num, division_name


def walk_bid_folders(bid_folder_id: str, token: str) -> list:
    """
    Walk the division folder structure and return a flat list of vendor files.
    Returns: [{"division_num", "division_name", "vendor_name", "vendor_folder_id",
                "file_id", "file_name", "file_mime", "modified_time"}, ...]

    Fixed 2026-07-08: this used to assume exactly 2 levels (division folder ->
    vendor folder -> files). Real structure, confirmed live on 101 Francis and
    intentional per Buck (matches HubSpot's per-subdivision deal naming): some
    top-level division folders (e.g. "07_Thermal & Moisture") contain a mix of
    real vendor folders AND numbered subdivision folders (e.g. "13_Insulation",
    "14_Roofing") that themselves contain the real vendor folders one level
    deeper. The old code treated every subdivision folder as if it WERE a vendor
    - looked for files directly inside it, found none (they're one level down),
    and silently returned nothing for that division. On 101F this collapsed the
    entire scan to zero bids found system-wide, not just those divisions - real
    bids for Yeti and Accurate Insulation (both under 13_Insulation) were
    invisible to bid-leveling entirely. Now recurses: a folder matching the
    division-number-prefix pattern is treated as a subdivision and walked one
    level deeper before giving up; a folder that doesn't match that pattern is
    assumed to be a real vendor/company folder, same as before. Division number
    stays anchored to the top-level folder throughout - a vendor found via a
    subdivision still reports its parent division, not the subdivision number.
    """
    # 2026-07-15: this walk was fully serial (one division folder at a time,
    # then recursing depth-first into each) - measured live at 50+ seconds for
    # a single project's dry-run scan, a real contributing factor in
    # AUTO-BID-UPDATE-DETECTION's intermittent ECONNABORTED failures. Top-level
    # division folders are fully independent of each other (no shared state,
    # no ordering dependency in the returned flat list), so parallelize just
    # this outer loop via a thread pool - Drive API calls are I/O-bound, and
    # this doesn't touch any of the recursive parsing/classification logic
    # inside _walk_vendor_level, which has a lot of carefully-tuned historical
    # bugfixes (archive-skipping, division-prefix parsing, sub-package
    # disambiguation) that a broader rewrite would risk breaking.
    results = []
    div_folders = _drive_list(bid_folder_id, token)
    division_jobs = []

    for div_folder in div_folders:
        if "folder" not in div_folder.get("mimeType", ""):
            continue
        div_raw = div_folder["name"]
        if re.match(r"^archive", div_raw, re.IGNORECASE):
            # Found 2026-07-09: an "Archive_Pre_..." top-level folder (created
            # during the 2026-07-08 cleanup pass) doesn't match _DIV_PREFIX_RE,
            # so it fell into the "not a division" branch below and got treated
            # as one anyway (division_num="Ar", division_name="Archive_Pre_...")
            # - the walk then recursed into it and re-ingested superseded/old
            # bid files as if they were current, live data. Skip archive
            # folders outright; nothing under them should ever reach drive_bids.
            continue
        m = _DIV_PREFIX_RE.match(div_raw)
        if m:
            division_num  = m.group(1).zfill(2) if len(m.group(1)) == 1 else m.group(1)
            division_name = m.group(2).replace("_", " ").strip()
        else:
            # 1355 Riverside uses "Division N - Name" instead of the "0N_Name"
            # convention other projects follow - _DIV_PREFIX_RE doesn't match
            # that either. Try it before giving up.
            m2 = re.match(r"^Division\s+(\d+)\s*[-–—]?\s*(.*)$", div_raw, re.IGNORECASE)
            if m2:
                division_num  = m2.group(1).zfill(2) if len(m2.group(1)) == 1 else m2.group(1)
                division_name = m2.group(2).strip() or div_raw
            else:
                # Found live 2026-07-09: folders that are neither pattern - "BId
                # Package to subs", "Bid Leveling Summaries", "wrong job files" -
                # were falling back to div_raw[:2] as a fake division_num ("BI",
                # "Bi", "wr"), producing garbage "Division BI"/"Division wr"
                # leveling files with real bid data mixed in under a nonsense
                # division. If a folder isn't recognizably a division by either
                # naming convention, skip it - don't invent a division code.
                continue

        division_num, division_name = _sub_package_parent(div_raw, division_num, division_name)
        division_jobs.append((div_folder["id"], division_num, division_name))

    if not division_jobs:
        return results

    with ThreadPoolExecutor(max_workers=min(8, len(division_jobs))) as pool:
        futures = {
            pool.submit(_walk_vendor_level, folder_id, token, div_num, div_name, 0): div_num
            for folder_id, div_num, div_name in division_jobs
        }
        for future in as_completed(futures):
            results.extend(future.result())

    return results


_TRAILING_DATE_RE = re.compile(
    r"^(.+?)[\s_-]+(\d{1,2}[-./]\d{1,2}[-./]\d{2,4}|\d{4}-\d{2}-\d{2})", re.IGNORECASE
)


_PROJECT_BID_SUMMARY_RE = re.compile(
    r"^\d+_[^_]+_(.+)_bid_summary$", re.IGNORECASE
)


def _vendor_name_from_filename(filename: str) -> str:
    """Buck's stated canonical pattern: company-named folder, bid file named
    'Company Date.ext'. When a bid file is found loose (not in its own company
    folder - the exact gap Buck flagged: 'there might be bids placed in the
    divisional folders that are not in hubspot'), extract the vendor name from
    the filename using that same convention rather than dropping the file.

    2026-07-17: real vendor bids also show up loose as
    "{ProjectNum}_{ProjectName}_{Vendor}_Bid_Summary.pdf" (no date at all, so
    _TRAILING_DATE_RE never matches, and the whole filename was being used as
    vendor_name - "1355_Riverside_Creech_Architectural_Metals_Bid_Summary"
    instead of "Creech Architectural Metals" - task #148. Strip the
    project-number/name prefix and the trailing "_Bid_Summary" suffix for
    this specific pattern before falling back to the general logic."""
    base = re.sub(r"\.(pdf|docx?|xlsx?)$", "", filename, flags=re.IGNORECASE).strip()
    m2 = _PROJECT_BID_SUMMARY_RE.match(base)
    if m2:
        return m2.group(1).replace("_", " ").strip()
    m = _TRAILING_DATE_RE.match(base)
    return (m.group(1) if m else base).strip()


_NON_BID_FILENAME_RE = re.compile(
    r"\b(SOW|scope of work|bid email template|bid request|bid package set|"
    r"email templates?|division index|bid instructions?|"
    r"bid level tracker|level tracker|bid tracker|bid leveling|bid audit|"
    r"bid summary|duplicate folder notice|3D renders?|renders? for reference)\b|"
    r"^(archived?|old|superseded)([\s_-]|$)", re.IGNORECASE
)

# "bid summary" alone is ambiguous: real vendors commonly name their own bid
# document "{Project}_{VendorName}_Bid_Summary.pdf" (confirmed live 2026-07-16
# against three known-real bids - ProGuard $31,280.27, CQ Roofing $153,900,
# All Valley $95,224 - all cross-matching the independently-verified executive
# summary data), while HCI's own generated roll-up artifacts follow
# "{Project} - {Category} Bid Summary" with no vendor name and no file
# extension (their vendor_name field, when ingested, literally becomes the
# whole filename - the actual tell). Excluding the underscore+.pdf/.docx/.xlsx
# vendor-style pattern from the "bid summary" match specifically (not the
# other phrases) fixes the false positive without reopening BL-DEFECT-05,
# whose original counter-example ("...Bid_Leveling.xlsx") matches a different
# phrase in this same regex and is unaffected.
_VENDOR_STYLE_BID_SUMMARY_RE = re.compile(
    r"^\S+_\S+_bid_summary\.(pdf|docx?|xlsx?)$", re.IGNORECASE
)


def _is_outbound_not_a_bid(filename: str) -> bool:
    """Files HCI sends OUT (scope-of-work docs, email templates, bid-request
    letters) live in the same vendor/division folders as real vendor bid
    responses and were being walked and extracted as if they were bids -
    found live 2026-07-09 when Buck caught SOW/template filenames appearing
    as 'SUBCONTRACTOR' rows in generated leveling sheets with bid_amount
    always null. Filename-pattern exclusion, not content-based, because
    these are outbound documents HCI authors - the filenames are the
    reliable signal, not something that needs a PDF read to detect.

    2026-07-13: _NON_BID_FILENAME_RE's phrases (e.g. "bid leveling") require
    a literal space between words. The system's own auto-generated summary
    file "1355_Riverside_Bid_Leveling_Insulation.xlsx" uses underscores, so
    it silently slipped past this filter and got ingested as a fake "vendor"
    bid ($985, matching nothing real) - found live via cross-project deep
    testing. Normalize underscores/hyphens to spaces before matching so the
    filter catches HCI's own underscore-delimited naming convention too.

    2026-07-16: "bid summary" specifically was a false-positive risk this
    broad matching created - real vendor-authored "{Project}_{Vendor}_
    Bid_Summary.pdf" files were being caught too. See
    _VENDOR_STYLE_BID_SUMMARY_RE above for the verified distinguishing
    signal."""
    if _VENDOR_STYLE_BID_SUMMARY_RE.match(filename):
        return False
    normalized = re.sub(r"[_\-]+", " ", filename)
    return bool(_NON_BID_FILENAME_RE.search(filename) or _NON_BID_FILENAME_RE.search(normalized))


def _walk_vendor_level(folder_id: str, token: str, division_num: str, division_name: str, depth: int) -> list:
    """One level of the vendor search. A subfolder is treated as a category to
    recurse into - either a numbered subdivision (e.g. "13_Insulation") or any
    folder with no bid files directly inside it (e.g. "Fire Suppression", which
    contained both a real vendor subfolder AND a loose, unorganized bid PDF
    sitting right next to it - confirmed live on 101 Francis). A folder that
    itself contains files is treated as a real vendor/company folder. Loose
    files found as siblings of folders at any level (not inside any vendor
    folder at all) are still captured - vendor name inferred from the filename
    per Buck's own 'Company Date.ext' convention - and flagged unfoldered=True
    so a cleanup pass can find and organize them rather than silently keep
    losing bids that were dropped straight into a division folder."""
    results = []
    if depth > 3:
        return results  # safety cap - real structure never nests this deep
    entries = _drive_list(folder_id, token)
    folders = [e for e in entries if "folder" in e.get("mimeType", "")]
    loose_files = [e for e in entries if "folder" not in e.get("mimeType", "")
                   and (e.get("mimeType") in READABLE_MIME or e.get("name", "").lower().endswith((".pdf", ".docx")))
                   and not _is_outbound_not_a_bid(e.get("name", ""))]

    for entry in folders:
        name = entry["name"]
        # A folder whose OWN name matches archive/old/superseded gets skipped
        # entirely, not walked as a vendor - found live 2026-07-09: an
        # "Archive_Pre_2026-07-08" folder (containing genuinely superseded SOW
        # docs moved there during cleanup) had no subfolders of its own, so it
        # fell through to being treated as a vendor named "Archive_Pre_2026-07-08"
        # with its contents as that "vendor's" bids. The existing archive check
        # below only excludes archive SUBfolders from disqualifying their
        # PARENT - it never checked the current folder's own name.
        if re.match(r"^(archived?|old|superseded)([\s_-]|$)", name, re.IGNORECASE):
            continue
        sub_entries = _drive_list(entry["id"], token)
        # "Archived"/"Old"/"Superseded" subfolders don't disqualify a folder from
        # being a real leaf vendor folder - found live: "Accurate Insulation/"
        # (a real, correctly-named company folder) has an "Archived/" subfolder
        # inside it for old bid versions, which otherwise made this folder look
        # like a category and triggered a pointless recursion into it.
        sub_folders = [e for e in sub_entries if "folder" in e.get("mimeType", "")
                       and not re.match(r"^(archived?|old|superseded)([\s_-]|$)", e["name"], re.IGNORECASE)]
        sub_files = [e for e in sub_entries if "folder" not in e.get("mimeType", "")
                     and (e.get("mimeType") in READABLE_MIME or e.get("name", "").lower().endswith((".pdf", ".docx")))
                     and not _is_outbound_not_a_bid(e.get("name", ""))]
        # A folder is a leaf vendor folder only if it has no (non-archive)
        # subfolders of its own. Any other subfolder presence means recurse -
        # Buck found live that a folder can have BOTH a real vendor subfolder
        # and a loose unorganized file side by side ("Fire Suppression" had
        # "KFS/" plus a bare PDF) - checking sub_files alone (whether this
        # folder itself has files) picked the wrong branch and silently
        # dropped KFS entirely.
        is_category = bool(_DIV_PREFIX_RE.match(name)) or bool(sub_folders)
        if is_category:
            results.extend(_walk_vendor_level(entry["id"], token, division_num, division_name, depth + 1))
            continue
        vendor_name      = name
        vendor_folder_id = entry["id"]
        for f in sub_files:
            results.append({
                "division_num":    division_num,
                "division_name":   division_name,
                "vendor_name":     vendor_name,
                "vendor_folder_id": vendor_folder_id,
                "file_id":         f["id"],
                "file_name":       f["name"],
                "file_mime":       f.get("mimeType", "application/pdf"),
                "modified_time":   f.get("modifiedTime", ""),
                "unfoldered":      False,
            })

    for f in loose_files:
        results.append({
            "division_num":    division_num,
            "division_name":   division_name,
            "vendor_name":     _vendor_name_from_filename(f["name"]),
            "vendor_folder_id": None,
            "file_id":         f["id"],
            "file_name":       f["name"],
            "file_mime":       f.get("mimeType", "application/pdf"),
            "modified_time":   f.get("modifiedTime", ""),
            "unfoldered":      True,
        })
    return results


def _sync_bid_package(cur, row: dict) -> None:
    """
    Found live 2026-07-08 (Buck, mid-demo, and independently by GBT reading the DB
    directly): drive_bids (this scan's raw extraction) and bid_packages (the table
    every report - Field GBT, deep-dive, PM console - actually reads) never synced.
    A real bid could sit in Drive and drive_bids for weeks while every report kept
    calling it "zero bids received." This closes that gap as a permanent part of
    every scan, not a one-time data patch - covers both a HubSpot-sourced package
    already sitting in bid_packages (matched by vendor name + division) and a bid
    dropped straight into a Drive folder with no HubSpot deal behind it at all
    (Buck: "there will sometimes bids put into the folders manually") by creating
    the bid_packages row if nothing matches.
    """
    division_prefix = re.match(r"^(\d{1,2})", row["division_num"] or "")
    div_prefix = division_prefix.group(1) if division_prefix else (row["division_num"] or "")
    vendor_first_word = (row["vendor_name"] or "").split()[0] if row["vendor_name"] else ""
    if not vendor_first_word:
        return

    cur.execute("""
        SELECT id, status FROM bid_packages
        WHERE project_id=%s
          AND left(regexp_replace(csi_division, '[^0-9]', '', 'g'), 2) = left(%s, 2)
          AND (package_name ILIKE %s OR %s ILIKE '%%' || split_part(package_name, ' ', 1) || '%%')
        LIMIT 1
    """, (row["project_id"], div_prefix, f"%{vendor_first_word}%", row["vendor_name"]))
    existing = cur.fetchone()

    if existing:
        if existing["status"] not in ("awarded",):
            cur.execute("""
                UPDATE bid_packages SET status='bid_received', updated_at=NOW()
                WHERE id=%s
            """, (existing["id"],))
    else:
        cur.execute("""
            INSERT INTO bid_packages (project_id, csi_division, package_name, status, notes, created_by, created_via)
            VALUES (%s, %s, %s, 'bid_received', 'Auto-created from Drive bid scan - no matching HubSpot-sourced package found', 'system', 'drive_bid_scan')
        """, (row["project_id"], f"{row['division_num']} — {row['division_name']}", row["vendor_name"]))


# 2026-07-17: 275 Sunnyside's real Bids folder (task #145/#149) uses bare
# trade-name division folders ("Concrete", "Framing", "Structural STeel")
# instead of the "0N_Name" or "Division N - Name" conventions
# walk_bid_folders() recognizes - it correctly skips them rather than
# inventing a division code. Rather than guess a mapping, this is built
# directly from bid_leveling_service.SUNNYSIDE_MODEL_DIVISION_TREE - a real,
# authoritative CSI scheme sourced from Chris Hendrickson's own
# "275 Sunnyside Lane - Bid Form.xlsx" and "275_Sunnyside_Master_Budget_v4_1.xlsx".
# Only folders with a clear, direct correspondence to that real tree are
# mapped. "oxegenation" and "Pool and spa" have no match in the real tree and
# are deliberately left unmapped rather than guessed - walk_bid_folders_by_
# trade_name() reports them as unmapped for human review instead of silently
# dropping or inventing a division for them.
SUNNYSIDE_275_TRADE_MAP = {
    "excavation":          ("02", "Existing Conditions and Site Work"),
    "landscaping":         ("02", "Existing Conditions and Site Work"),
    "concrete":            ("03", "Concrete"),
    "masonry":             ("04", "Masonry"),
    "structural steel":    ("05", "Metals"),
    "framing":             ("06", "Wood Plastics and Composites"),
    "interior trim":       ("06", "Wood Plastics and Composites"),
    "waterproofing":       ("07", "Thermal and Moisture Protection"),
    "insulation":          ("07", "Thermal and Moisture Protection"),
    "roofing":             ("07", "Thermal and Moisture Protection"),
    "garage door":         ("08", "Openings"),
    "windows and doors":   ("08", "Openings"),
    "finishes":            ("09", "Finishes"),
    "tile and countertops": ("09", "Finishes"),
    "drywall":             ("09", "Finishes"),
    "fire places":         ("10", "Specialties"),
    "appliances":          ("11", "Equipment"),
    "hvac plumbing":       ("15", "Mechanical"),
    "plumbing fixtures":   ("15", "Mechanical"),
    "fire suppression":    ("15", "Mechanical"),
    "electrical":          ("16", "Electrical"),
    "solar":               ("16", "Electrical"),
    "av and security":     ("16", "Electrical"),
}


def walk_bid_folders_by_trade_name(bid_folder_id: str, token: str, trade_map: dict) -> tuple:
    """
    Same return shape as walk_bid_folders() (flat list of vendor-file dicts)
    but for projects whose Bids folder uses bare trade names instead of
    numbered divisions. trade_map keys are matched case-insensitively
    against folder names (whitespace-normalized). Unmapped top-level folders
    are collected and returned separately rather than silently skipped, so
    the caller can see exactly what wasn't covered instead of assuming
    complete coverage. Reuses _walk_vendor_level() for the actual file walk -
    the exact same proven logic walk_bid_folders() uses per division.
    """
    top = _drive_list(bid_folder_id, token)
    results, unmapped = [], []
    for entry in top:
        if "folder" not in entry.get("mimeType", ""):
            continue
        key = re.sub(r"\s+", " ", entry["name"]).strip().lower()
        mapped = trade_map.get(key)
        if not mapped:
            unmapped.append(entry["name"])
            continue
        division_num, division_name = mapped
        results.extend(_walk_vendor_level(entry["id"], token, division_num, division_name, 0))
    return results, unmapped


def scan_project_bids(project_id: int, dry_run: bool = True, trade_map: dict = None) -> dict:
    """
    Scan a project's bid_folder_id, extract new/updated bids, upsert to drive_bids.
    dry_run=True: return what would be processed without writing to DB.
    trade_map: optional dict of {lowercase folder name: (division_num,
    division_name)} for projects using bare trade-name folders instead of
    numbered divisions (see SUNNYSIDE_275_TRADE_MAP). When provided, uses
    walk_bid_folders_by_trade_name() instead of the numbered-division walker.
    """
    with _pg() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, bid_folder_id FROM projects WHERE id=%s",
                (project_id,)
            )
            proj = cur.fetchone()
    if not proj:
        return {"error": f"Project {project_id} not found"}
    if not proj["bid_folder_id"]:
        return {"error": f"Project {proj['name']} has no bid_folder_id configured", "project": proj["name"]}

    token = get_google_token("drive")
    drive_drive_token = get_google_token("drive")  # same token, named for clarity

    # Walk folder structure
    unmapped_folders = []
    if trade_map:
        files, unmapped_folders = walk_bid_folders_by_trade_name(proj["bid_folder_id"], token, trade_map)
    else:
        files = walk_bid_folders(proj["bid_folder_id"], token)
    if not files:
        return {"project": proj["name"], "files_found": 0, "new_bids": 0, "dry_run": dry_run,
                "unmapped_folders": unmapped_folders}

    # Load existing drive_bids file_ids for this project
    with _pg() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT file_id FROM drive_bids WHERE project_id=%s", (project_id,))
            known_ids = {r["file_id"] for r in cur.fetchall()}

    new_files    = [f for f in files if f["file_id"] not in known_ids]
    skipped      = len(files) - len(new_files)
    extracted    = []
    errors       = []

    for f in new_files:
        try:
            mime = f["file_mime"]

            if mime in ("application/vnd.google-apps.document", "application/vnd.google-apps.spreadsheet"):
                text = _export_google_doc(f["file_id"], token, mime)
                data = extract_bid_from_text(text, f["vendor_name"], f["file_name"])
                source = "regex_text"
            elif mime == "application/pdf" or f["file_name"].lower().endswith(".pdf"):
                pdf_bytes = _download_bytes(f["file_id"], token)
                data = {"error": "GEMINI_API_KEY not set"}
                source = "pending"
                if GEMINI_API_KEY:
                    data   = extract_bid_with_gemini(pdf_bytes, f["vendor_name"],
                                                      proj["name"], f["division_name"])
                    source = "gemini"
                # Fall back to Claude on any Gemini failure (quota exhaustion,
                # outage, etc.) rather than losing the extraction entirely -
                # same contract, different provider/billing.
                if "error" in data:
                    data   = extract_bid_with_claude(pdf_bytes, f["vendor_name"],
                                                      proj["name"], f["division_name"])
                    source = "claude_fallback"
            else:
                continue

            if "error" in data:
                errors.append({"file": f["file_name"], "error": data["error"]})
                continue

            bid_date = None
            if data.get("bid_date"):
                try:
                    bid_date = datetime.datetime.strptime(str(data["bid_date"])[:10], "%Y-%m-%d").date()
                except Exception:
                    pass

            row = {
                "project_id":      project_id,
                "division_num":    f["division_num"],
                "division_name":   f["division_name"],
                "vendor_name":     f["vendor_name"],
                "vendor_folder_id": f["vendor_folder_id"],
                "file_id":         f["file_id"],
                "file_name":       f["file_name"],
                "bid_date":        bid_date,
                "bid_amount":      data.get("bid_amount"),
                "bid_amount_raw":  f"${data.get('bid_amount'):,.2f}" if data.get("bid_amount") else None,
                "scope_summary":   data.get("scope_summary"),
                "is_latest":       True,
                "extraction_source": source,
            }
            extracted.append(row)

        except Exception as e:
            errors.append({"file": f.get("file_name", f["file_id"]), "error": str(e)})

    if dry_run:
        return {
            "project":       proj["name"],
            "project_id":    project_id,
            "dry_run":       True,
            "files_found":   len(files),
            "already_known": skipped,
            "new_files":     len(new_files),
            "would_extract": len(extracted),
            "errors":        errors,
            "preview":       extracted[:5],
            "unmapped_folders": unmapped_folders,
        }

    # Write to DB — upsert and fix is_latest
    upserted = 0
    with _pg() as conn:
        with conn.cursor() as cur:
            for row in extracted:
                cur.execute("""
                    INSERT INTO drive_bids
                        (project_id, division_num, division_name, vendor_name,
                         vendor_folder_id, file_id, file_name, bid_date,
                         bid_amount, bid_amount_raw, scope_summary, is_latest, extraction_source)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (file_id) DO UPDATE SET
                        bid_amount=EXCLUDED.bid_amount,
                        bid_date=EXCLUDED.bid_date,
                        scope_summary=EXCLUDED.scope_summary,
                        is_latest=EXCLUDED.is_latest,
                        extracted_at=NOW()
                """, (
                    row["project_id"], row["division_num"], row["division_name"],
                    row["vendor_name"], row["vendor_folder_id"], row["file_id"],
                    row["file_name"], row["bid_date"], row["bid_amount"],
                    row["bid_amount_raw"], row["scope_summary"],
                    row["is_latest"], row["extraction_source"],
                ))
                upserted += 1
                if row["bid_amount"]:
                    _sync_bid_package(cur, row)

            # is_latest recompute (2026-07-14 rewrite - see lessons_learned #57/#66):
            # the old version partitioned by (project, division, vendor) alone, which
            # silently collapsed genuinely distinct concurrent line items from the same
            # vendor (multi-scope submissions like LEAX Controls' 7 items) down to a
            # single is_latest=true row - real dollar amounts went invisible with no
            # error. Fixed model: is_latest is only ever auto-collapsed within
            # (project, division, vendor, file_name) - i.e. a literal re-scan of the
            # identical file, which is always safe to dedupe. A genuine revision
            # (same scope, new file, meant to replace the old one) must have its OWN
            # supersedes column explicitly set to point at the current row's id -
            # either by this same auto-detection for identical filenames, or by a
            # human/agent verification step for a differently-named resubmission.
            # Convention: supersedes points FORWARD (old row -> the row that replaced
            # it), so a row with its own supersedes set is, by definition, not latest -
            # this lets many old duplicates point at one current row, which a reverse
            # convention (current -> old) cannot represent with a single-value column.
            cur.execute("""
                WITH ranked AS (
                    SELECT id,
                           ROW_NUMBER() OVER (
                               PARTITION BY project_id, division_num, vendor_name, file_name
                               ORDER BY COALESCE(bid_date, '1900-01-01'::date) DESC, id DESC
                           ) AS rn
                    FROM drive_bids WHERE project_id = %s
                )
                UPDATE drive_bids
                SET is_latest = (ranked.rn = 1)
                FROM ranked
                WHERE drive_bids.id = ranked.id
                  AND drive_bids.supersedes IS NULL
            """, (project_id,))
            # Explicit supersedes always overrides: a row that has been marked as
            # superseded (its own supersedes column is set) is never latest, no matter
            # what the filename-collapse above did.
            cur.execute("""
                UPDATE drive_bids
                SET is_latest = FALSE
                WHERE supersedes IS NOT NULL
                  AND project_id = %s
            """, (project_id,))

            # Contamination override, always last: the ranked recompute above has no
            # concept of "not a real bid" - it only ranks by date within
            # (division, vendor, file_name), and a contaminated row almost always has
            # a unique file_name, so it ranks rn=1 alone in its own partition no
            # matter what. A prior manual is_latest=FALSE fix on a contaminated row
            # (e.g. task #136/BL-DEFECT-05) does NOT survive this recompute, because
            # nothing above ever re-checks it - found live 2026-07-17 via the
            # drive_bids_is_latest_audit trigger catching rows 807/812/817/818
            # silently flip back to TRUE after a scan. Recomputed here every call
            # (not cached) so a filter fix like tonight's _VENDOR_STYLE_BID_SUMMARY_RE
            # narrowing takes effect on the next scan without a separate migration.
            cur.execute("SELECT id, file_name FROM drive_bids WHERE project_id = %s", (project_id,))
            contaminated_ids = [r["id"] for r in cur.fetchall() if _is_outbound_not_a_bid(r["file_name"] or "")]
            if contaminated_ids:
                cur.execute("""
                    UPDATE drive_bids SET is_latest = FALSE WHERE id = ANY(%s)
                """, (contaminated_ids,))
        conn.commit()

    stale_trackers = check_duplicate_tracker_files(proj["bid_folder_id"], token)
    if stale_trackers:
        _log_stale_tracker_alert(project_id, proj["name"], stale_trackers)

    return {
        "project":    proj["name"],
        "project_id": project_id,
        "dry_run":    False,
        "files_found":   len(files),
        "already_known": skipped,
        "new_bids":      upserted,
        "errors":        errors,
        "duplicate_tracker_files": stale_trackers,
        "unmapped_folders": unmapped_folders,
    }


def reclassify_existing_divisions(project_id: int, dry_run: bool = True) -> dict:
    """
    Re-apply _sub_package_parent() to ALREADY-INGESTED drive_bids rows.

    Found 2026-07-13: scan_project_bids() only classifies genuinely NEW
    files (`f["file_id"] not in known_ids`) - once a file's division_num/
    division_name is written, nothing ever re-derives it, even after
    _SUB_PACKAGE_TO_PARENT_DIVISION gains new entries or a folder gets
    correctly re-nested in Drive. Confirmed live: 1355R's "13_Insulation"
    and "13_Special Construction" rows still showed the old flat "13"
    collision even after a full rescan, because both files were already
    "known" and got skipped. A fresh walk_bid_folders() call correctly
    resolves "Special Construction" to its real parent (10, Specialties),
    proving the classification logic itself works - it just never gets
    re-applied to old data. This is a cheap, DB-only fix: no re-download,
    no re-extraction (Gemini/Claude), just re-running the same name lookup
    against what's already stored and updating rows where it disagrees.
    """
    with _pg() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, division_num, division_name FROM drive_bids WHERE project_id=%s",
                (project_id,)
            )
            rows = cur.fetchall()

    changes = []
    for row in rows:
        new_num, new_name = _sub_package_parent(row["division_num"], row["division_num"], row["division_name"])
        if new_num != row["division_num"] or new_name != row["division_name"]:
            changes.append({
                "id": row["id"],
                "old": (row["division_num"], row["division_name"]),
                "new": (new_num, new_name),
            })

    if not dry_run and changes:
        with _pg() as conn:
            with conn.cursor() as cur:
                for c in changes:
                    cur.execute(
                        "UPDATE drive_bids SET division_num=%s, division_name=%s WHERE id=%s",
                        (c["new"][0], c["new"][1], c["id"])
                    )
            conn.commit()

    return {
        "project_id": project_id,
        "dry_run": dry_run,
        "rows_checked": len(rows),
        "rows_reclassified": len(changes),
        "changes": changes,
    }


def _dedup_cross_division_bids(rows: list) -> list:
    """
    2026-07-13, per Buck's explicit directive after a live report ("full
    touch every bid... this is a huge mistake"): the same vendor bid was
    found filed under 2+ different division folders (e.g. a cabinetry
    estimate legitimately spans the "06 Woods and Plastics" and "09
    Finishes" folder conventions), causing it to be double-counted as if it
    were 2 separate competing bids - inflating vendor counts and corrupting
    low/high/spread math in both divisions. Confirmed live: 4 real vendor
    bids on 1355R duplicated this way, one of which (Long Beach Enterprise)
    was ALSO loose-filed a 3rd time under the wrong division entirely (10
    Specialties - Furnishings) with a garbled auto-derived vendor name,
    making that division falsely show "1 uncontested bid" when there are
    actually zero real furnishings bids for this project.

    Groups by (file_name, bid_amount) - a genuine copy of the same document
    - and keeps exactly one canonical row per group, in priority order: a
    real vendor folder over a loose/unfoldered file, a properly resolved
    sub-package division_name over a bare generic one, then lower
    division_num as a deterministic tiebreak (which also happens to match
    the canonical HCI division for shared trades like cabinetry - Division
    06 Wood & Plastic, not 09 Finishes, per the documented 16-division
    structure). Excluded duplicates are dropped entirely from the leveling
    view, not just hidden - they were never a second competing bid.
    """
    def _norm(s):
        return re.sub(r"[^a-z0-9]", "", (s or "").lower())

    # Two rows are the same real bid if the amount matches exactly AND
    # either their file_names match exactly, or one's normalized vendor
    # name is a substring of the other's normalized vendor name or
    # file_name. The second clause exists specifically for the loose/
    # unfoldered case: a copy saved with a filename-derived vendor name
    # like "Estimate_1186_from_Long_beach_enterprisellc" won't file-name-
    # match its sibling "Long Beach Enterprise - 1355 Riverside - Estimate
    # 1186.pdf" exactly, but "longbeach" is a clean substring of both its
    # own normalized name and the garbled one - catching it without a
    # blind fuzzy-match that could wrongly merge unrelated vendors.
    def _same_bid(a, b):
        if a.get("bid_amount") != b.get("bid_amount"):
            return False
        if a.get("file_name") and a.get("file_name") == b.get("file_name"):
            return True
        na, nb = _norm(a.get("vendor_name")), _norm(b.get("vendor_name"))
        nfa, nfb = _norm(a.get("file_name")), _norm(b.get("file_name"))
        return bool(na and nb and (na in nb or nb in na)) or \
               bool(na and nfb and na in nfb) or bool(nb and nfa and nb in nfa)

    by_amount: dict = {}
    for row in rows:
        by_amount.setdefault(row.get("bid_amount"), []).append(row)

    def _rank(r):
        has_folder = 0 if r.get("vendor_folder_id") else 1
        is_subpackaged = 0 if "—" in (r.get("division_name") or "") else 1
        digits = re.sub(r"\D", "", r.get("division_num") or "")
        div_num_sort = int(digits) if digits else 999
        return (has_folder, is_subpackaged, div_num_sort)

    kept = []
    for amount, candidates in by_amount.items():
        groups = []
        for row in candidates:
            placed = False
            for g in groups:
                if any(_same_bid(row, member) for member in g):
                    g.append(row)
                    placed = True
                    break
            if not placed:
                groups.append([row])
        for g in groups:
            kept.append(g[0] if len(g) == 1 else sorted(g, key=_rank)[0])
    return kept


def read_drive_bids(project_id: int, latest_only: bool = True) -> dict:
    """
    Read drive_bids from DB for a project.
    Returns dict keyed by division_num, EXCEPT when the same bare division_num
    is shared by genuinely different scopes (e.g. sub-package "13_Insulation"
    under Division 07 vs sub-package "13_Special Construction" under Division
    10 - both use the bare number 13, per the HCI canonical two-level
    division/sub-package folder structure that this table doesn't fully
    model yet). In that case each distinct division_name gets its own key
    (division_num + "__" + division_name) so unrelated trades never get
    merged into one "leveling" comparison. Found 2026-07-13: division 13 was
    silently mixing Insulation bids ($56-79K) with Fire Suppression bids
    ($31-108K) into a single nonsensical low/high/spread - this is the fix.

    Also drops cross-division duplicate filings (see _dedup_cross_division_bids)
    before any grouping happens, so the same real bid is never counted twice.
    """
    with _pg() as conn:
        with conn.cursor() as cur:
            q = "SELECT * FROM drive_bids WHERE project_id=%s"
            if latest_only:
                q += " AND is_latest=TRUE"
            q += " ORDER BY division_num, vendor_name, bid_date DESC"
            cur.execute(q, (project_id,))
            rows = [dict(r) for r in cur.fetchall()]

    rows = _dedup_cross_division_bids(rows)

    names_by_div = {}
    for row in rows:
        names_by_div.setdefault(row["division_num"], set()).add(row.get("division_name", ""))
    ambiguous_divs = {d for d, names in names_by_div.items() if len(names) > 1}

    result = {}
    for row in rows:
        div_num = row["division_num"]
        div_name = row.get("division_name", "")
        div = f"{div_num}__{div_name}" if div_num in ambiguous_divs else div_num
        result.setdefault(div, {
            "division_num":  div_num,
            "division_name": div_name,
            "bids": []
        })
        result[div]["bids"].append({
            "vendor":        row["vendor_name"],
            "bid_date":      str(row["bid_date"]) if row.get("bid_date") else "",
            "amount":        float(row["bid_amount"]) if row.get("bid_amount") else None,
            "amount_fmt":    row.get("bid_amount_raw") or (f"${float(row['bid_amount']):,.2f}" if row.get("bid_amount") else ""),
            "scope":         row.get("scope_summary", ""),
            "file_name":     row.get("file_name", ""),
            "file_id":       row.get("file_id", ""),
            "is_latest":     row.get("is_latest", True),
            "source":        row.get("extraction_source", ""),
        })
    return result


# 2026-07-13: Bid Leveling Option B, per GBT's explicit directive (3-way
# team consensus, P0 ADR-003 handoff). These 5 divisions (05, 06, 08, 09, 16)
# have vendor folders that were never organized into named sub-packages in
# Drive, so read_drive_bids()/_sub_package_parent() can't separate their
# distinct trades. Rather than physically reorganize Buck's Drive (Option A,
# rejected), infer sub-trade groupings FOR DISPLAY ONLY from each vendor's
# real scope_summary text. Keyword lists below were derived from and
# verified against the actual 46 real vendor rows on project 3 (1355
# Riverside) - not guessed. This never writes to drive_bids.division_num/
# division_name; it only adds a display-only "inferred_subgroups" field to
# get_leveling_summary()'s output. Order within each division's rule list
# matters - first matching keyword wins, ordered from most to least specific
# to avoid one vendor's incidental word choice (e.g. a framing vendor
# mentioning "windows and doors" in passing) stealing it from its real trade.
_DIVISION_INFERENCE_RULES = {
    "05": [
        ("Structural Steel — Fabrication & Erection [inferred]",
         ["structural steel", "beam", "column", "erection", "detailing", "welding"]),
        ("Metal Supply — Non-Structural [inferred]",
         ["shelves", "supply and delivery"]),
    ],
    "06": [
        ("Cabinetry [inferred]", ["cabinet", "vanit"]),
        ("Material Supply [inferred]", ["lumber", "building materials"]),
        ("Framing / Building Envelope [inferred]",
         ["framing", "demolition", "siding", "envelope", "renovation"]),
    ],
    "08": [
        ("Garage Doors [inferred]", ["garage door"]),
        ("Door Hardware [inferred]", ["door hardware"]),
        ("Glass / Shower Enclosures [inferred]", ["shower", "glass railing", "mirror"]),
        ("Windows & Exterior Doors [inferred]",
         ["window", "exterior door", "lift-and-slide", "reynaers"]),
        ("Interior Doors [inferred]", ["interior door"]),
    ],
    "09": [
        ("Stone / Countertops [inferred]", ["stone", "countertop", "quartzite", "granite"]),
        ("Cabinetry [inferred]", ["cabinet", "vanit"]),
        ("Flooring [inferred]", ["carpet", "flooring", "oak flooring"]),
        ("Drywall [inferred]", ["drywall"]),
        ("Tile [inferred]", ["tile"]),
        ("Painting [inferred]", ["paint"]),
        ("Framing / Building Envelope [inferred]",
         ["framing", "demolition", "siding", "envelope", "renovation"]),
    ],
    "16": [
        ("AV / Low Voltage [inferred]",
         ["av integration", "audio", "video", "camera", "prewire", "pre-wire",
          "low voltage", "network", "automation", "touch panel", "smart home"]),
        ("Electrical Service [inferred]",
         ["electrical", "power wiring", "distribution panel", "sub panel", "main service"]),
    ],
}
_UNCLASSIFIED_LABEL = "Other / Unclassified [inferred]"


def _infer_subgroups(division_num: str, bids: list) -> dict:
    """
    Group bids within one division into inferred sub-trades using
    _DIVISION_INFERENCE_RULES, keyed off vendor name + scope_summary text.
    Display-only - returns a fresh dict, never mutates the input bids or
    touches the DB. Returns {} if this division has no ruleset defined.
    """
    rules = _DIVISION_INFERENCE_RULES.get(division_num)
    if not rules:
        return {}

    buckets: dict = {}
    for bid in bids:
        haystack = f"{bid.get('vendor', '')} {bid.get('scope', '')}".lower()
        label = _UNCLASSIFIED_LABEL
        for rule_label, keywords in rules:
            if any(kw in haystack for kw in keywords):
                label = rule_label
                break
        buckets.setdefault(label, []).append(bid)

    # 2026-07-13, per Buck's live report: even after trade-grouping, some
    # buckets still showed wildly implausible spreads (e.g. Stone/Countertops
    # 15,284%). Root cause, confirmed against real 1355R data: a keyword
    # match on trade alone doesn't mean two bids are for the same SCOPE of
    # work - "Decorative Materials" ($1,621, a small supply-only order) and
    # "InStone" ($249,460, full templating/fabrication/installation across
    # multiple rooms) both matched "stone" but aren't competing for the same
    # job at all. Split off any bid whose amount is under 25% of the
    # bucket's median into its own "Partial/Supply-Only Scope" group so the
    # main comparison isn't distorted by an order-of-magnitude scope
    # mismatch - it stays fully visible, just not blended into a spread%
    # that implies it's a real competing bid for the whole trade package.
    # This does NOT explain genuine price differences between comparable
    # full-scope bids (e.g. Ajac Stone $79,848 vs InStone $249,460, both
    # real full packages) - that gap needs actual line-item scope reading,
    # not a magnitude heuristic; flagged separately, not solved here.
    def _median(values):
        s = sorted(values)
        n = len(s)
        mid = n // 2
        return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2

    split_buckets: dict = {}
    for label, group_bids in buckets.items():
        priced_amounts = [b["amount"] for b in group_bids if b.get("amount")]
        if len(priced_amounts) < 3:
            split_buckets[label] = group_bids
            continue
        med = _median(priced_amounts)
        main, outliers = [], []
        for b in group_bids:
            amt = b.get("amount")
            if amt and med and amt < 0.25 * med:
                outliers.append(b)
            else:
                main.append(b)
        split_buckets[label] = main
        if outliers:
            base_label = label[:-len(" [inferred]")] if label.endswith(" [inferred]") else label
            split_buckets.setdefault(f"{base_label} — Partial/Supply-Only Scope [inferred]", []).extend(outliers)

    subgroups = {}
    for label, group_bids in split_buckets.items():
        priced = [b for b in group_bids if b.get("amount")]
        if not priced:
            subgroups[label] = {
                "bid_count": len(group_bids), "low_bid": None, "low_vendor": None,
                "high_bid": None, "spread": None, "spread_pct": None,
                "bids": group_bids,
            }
            continue
        amounts = sorted(b["amount"] for b in priced)
        low_bid, high_bid = amounts[0], amounts[-1]
        low_vendor = next((b["vendor"] for b in priced if b["amount"] == low_bid), "")
        subgroups[label] = {
            "bid_count":  len(priced),
            "low_bid":    low_bid,
            "low_vendor": low_vendor,
            "high_bid":   high_bid,
            "spread":     high_bid - low_bid,
            "spread_pct": round(((high_bid - low_bid) / low_bid) * 100, 1) if low_bid else None,
            "bids":       sorted(group_bids, key=lambda b: b.get("amount") or 0),
        }
    return subgroups


def get_bid_breakout(project_id: int, division_num: str) -> dict:
    """
    Mike Mount-style side-by-side vendor comparison for one division: a grid
    of scope category rows x vendor columns, so "what does Vendor A charge
    for X vs Vendor B" reads directly off the table instead of requiring a
    human to cross-reference narrative paragraphs. Built 2026-07-15 per
    GBT/Buck architecture requirement (msg f28e417c) after reviewing Mike
    Mount's real 246 Gallo Way workbook, which has a dedicated Bid Breakout
    tab doing exactly this.

    HONEST LIMITATION, not glossed over: this is CATEGORY-level, not true
    LINE-ITEM-level like Mike's. drive_bids stores one aggregate bid_amount
    per vendor per division - there is no itemized per-line-item dollar data
    extracted from source bid PDFs anywhere in this system. Mike's Bid
    Breakout works because his source data has real line-item pricing to
    pull from. This function reuses the EXACT same source
    (read_drive_bids() -> _infer_subgroups(), the same path get_leveling_summary()
    uses) so the category grid and the narrative doc can never diverge - but
    each vendor's number in a cell is still their one whole-scope bid amount,
    not a true line-item split. Getting real line-item parity with Mike's
    format requires extracting itemized pricing from vendor PDFs, which is a
    separate, larger data-extraction project, not something this function can
    manufacture from data that doesn't exist.
    """
    divisions = read_drive_bids(project_id, latest_only=True)
    div_data = divisions.get(division_num)
    if not div_data:
        matches = {k: v for k, v in divisions.items() if k.startswith(f"{division_num}__")}
        if len(matches) == 1:
            div_data = next(iter(matches.values()))
        elif len(matches) > 1:
            return {
                "error": "ambiguous_division",
                "detail": f"division {division_num} has {len(matches)} disambiguated scopes - "
                          f"call with the full composite key, one of: {list(matches.keys())}",
            }
    if not div_data:
        return {"error": "not_found", "detail": f"no bids found for division {division_num}"}

    bids = [b for b in div_data["bids"] if b.get("amount")]
    vendors = sorted({b["vendor"] for b in bids})
    subgroups = _infer_subgroups(division_num, bids)

    if subgroups:
        rows = []
        for category, group in subgroups.items():
            row = {"category": category, "vendors": {}}
            for b in group["bids"]:
                row["vendors"][b["vendor"]] = b["amount"]
            rows.append(row)
    else:
        # No inference ruleset for this division - fall back to one
        # "Total Bid" row so the grid still renders instead of being empty.
        rows = [{
            "category": "Total Bid (no category ruleset for this division)",
            "vendors": {b["vendor"]: b["amount"] for b in bids},
        }]

    return {
        "division_num": div_data["division_num"],
        "division_name": div_data["division_name"],
        "vendors": vendors,
        "rows": rows,
        "granularity": "category",
        "granularity_note": "Category-level (inferred from vendor name + scope text), "
                             "not true line-item pricing - see function docstring.",
        "source": "read_drive_bids() + _infer_subgroups() - same source as the narrative "
                  "leveling doc (get_leveling_summary), cannot diverge.",
    }


def get_leveling_summary(project_id: int) -> dict:
    """
    Return leveling summary per division: low bid, spread, vendor count.

    2026-07-13 fix: the division-13 bug (Insulation vs Fire Suppression
    merged under one bare number) is fixed at the grouping level in
    read_drive_bids(), but that only helps when two scopes have different
    division_names to key off. Division 09 "Finishes" showed the same root
    problem in a different shape - 18 genuinely different trades (tile,
    paint, carpet, drywall...) all share ONE division_name, so there's no
    name collision to disambiguate and a naive low/high/spread comparison
    across all of them is meaningless (a real case showed 36,610% spread).
    Without real per-vendor scope categorization data, guessing which
    vendors compete for the same work would be fabricating structure that
    isn't there. Instead: flag any division where the spread is implausible
    for genuine competing bids (>300% with 3+ vendors) as "not reliably
    comparable" rather than silently presenting a number that looks like a
    real apples-to-apples comparison but isn't. The raw bids stay visible -
    nothing is hidden, just not falsely presented as a clean comparison.
    """
    divisions = read_drive_bids(project_id, latest_only=True)
    summary   = {}
    for div_num, div_data in divisions.items():
        bids = [b for b in div_data["bids"] if b.get("amount")]
        if not bids:
            continue
        amounts  = sorted([b["amount"] for b in bids])
        low_bid  = amounts[0]
        high_bid = amounts[-1]
        spread   = high_bid - low_bid
        spread_pct = round((spread / low_bid) * 100, 1) if low_bid else None
        low_vendor = next((b["vendor"] for b in bids if b["amount"] == low_bid), "")
        leveling_reliable = not (spread_pct is not None and spread_pct > 300 and len(bids) >= 3)
        # Only surface inferred_subgroups when they reveal a real split (2+
        # groups) - found live 2026-07-13 testing 64EW: a single-bid division
        # still ran through the classifier and produced one lone subgroup,
        # which is noise (nothing to compare) rather than useful grouping.
        raw_subgroups = _infer_subgroups(div_data["division_num"], bids)
        inferred_subgroups = raw_subgroups if len(raw_subgroups) > 1 else {}
        summary[div_num] = {
            "division_name": div_data["division_name"],
            "bid_count":     len(bids),
            "low_bid":       low_bid,
            "low_vendor":    low_vendor,
            "high_bid":      high_bid,
            "spread":        spread,
            "spread_pct":    spread_pct,
            "leveling_reliable": leveling_reliable,
            "leveling_note": None if leveling_reliable else
                (f"Spread of {spread_pct}% across {len(bids)} vendors is too wide to be genuine "
                 f"competing bids for the same scope - likely multiple distinct trades sharing "
                 f"this division. Review individual bid scopes below before trusting low/high as "
                 f"a real comparison."
                 + (" Inferred sub-trade groupings below (from scope text, display-only, source "
                    "data unchanged) offer a more apples-to-apples comparison."
                    if inferred_subgroups else "")),
            "inferred_subgroups": inferred_subgroups or None,
            "bids":          sorted(bids, key=lambda b: b["amount"] or 0),
        }
    return summary


def _trash_and_rename(file_id: str, new_name: str, token: str) -> None:
    """Rename a file with a [SUPERSEDED YYYYMMDD] prefix - does NOT trash it,
    the file stays in place (just renamed) so it remains visible in its
    Archive subfolder. Never uses the permanent-delete endpoint."""
    import requests
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    requests.patch(f"{BASE_URL}/files/{file_id}?supportsAllDrives=true",
                    headers=headers, json={"name": new_name}, timeout=15)


def _move_to_archive_subfolder(file_id: str, vendor_folder_id: str, current_parent: str, token: str) -> str:
    """Move a file into an 'Archive' subfolder within its vendor folder,
    creating the subfolder if it doesn't exist yet. Returns the Archive
    subfolder id. This is a move, not a delete - fully reversible."""
    import requests
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    entries = _drive_list(vendor_folder_id, token)
    archive = next((e for e in entries if "folder" in e.get("mimeType", "")
                     and e["name"].lower() == "archive"), None)
    if archive:
        archive_id = archive["id"]
    else:
        r = requests.post(f"{BASE_URL}/files?supportsAllDrives=true", headers=headers,
                           json={"name": "Archive", "mimeType": "application/vnd.google-apps.folder",
                                 "parents": [vendor_folder_id]}, timeout=15)
        archive_id = r.json()["id"]
    requests.patch(
        f"{BASE_URL}/files/{file_id}?addParents={archive_id}&removeParents={current_parent}&supportsAllDrives=true",
        headers=headers, timeout=15)
    return archive_id


def _group_bids_by_vendor_division(snapshot: dict) -> dict:
    """snapshot is keyed (division_num, vendor_name, file_name) -> row, as
    produced by detect_and_process_bid_updates' before/after queries. Regroups
    to (division_num, vendor_name) -> {file_name: row} so a vendor's several
    concurrent bids within one division can be reasoned about as a set,
    instead of being silently collapsed into a single dict entry."""
    groups = {}
    for (div, vendor, fname), row in snapshot.items():
        groups.setdefault((div, vendor), {})[fname] = row
    return groups


def _classify_bid_change(before_files: dict, after_files: dict) -> str | None:
    """Given one vendor+division's file_name->row sets before and after a
    scan, decide what kind of event (if any) this is:
      - None: nothing new appeared - not an update event, skip silently.
      - "revision": exactly one file disappeared and exactly one new file
        appeared, with only one file present on each side - a clean 1-for-1
        replacement, safe to auto-supersede and archive the old file.
      - "concurrent": anything messier (a genuinely new file appeared
        alongside an existing one, e.g. a vendor with two distinct concurrent
        bids for different scopes in the same division) - must NOT be
        auto-superseded, since there is no way to tell which old file (if any)
        the new one is meant to replace. This is the exact bug class that
        caused Kubed Fire Suppression's interior-sprinkler bid to be wrongly
        archived as "superseded" by their unrelated exterior-wildfire bid
        (2026-07-14) - both were genuinely still-current, just for different
        scopes, and got collapsed by a too-coarse (division, vendor) key.
    """
    new_filenames = set(after_files) - set(before_files)
    removed_filenames = set(before_files) - set(after_files)

    if not new_filenames:
        return None

    if len(after_files) > 1 or len(before_files) > 1 or len(new_filenames) != 1 or len(removed_filenames) != 1:
        return "concurrent"

    return "revision"


def detect_and_process_bid_updates(project_id: int, dry_run: bool = True) -> dict:
    """
    Detect new or revised bids landing in a project's vendor folders and
    process them end to end: extract, compare to the prior latest bid for
    that vendor+division, archive the old bid (rename [SUPERSEDED
    YYYYMMDD], move to an Archive subfolder - never permanently deleted),
    extract line items + reconciliation for the new bid, link supersedes,
    and flag large-variance / plan-currency-risk cases for human review
    rather than silently trusting the new number.

    Built on top of scan_project_bids() rather than re-walking Drive from
    scratch - that function already does the file-walk, extraction, and
    is_latest recompute (newest bid_date per project+division+vendor wins).
    This function snapshots the is_latest bid per vendor before calling it,
    then diffs after, so it only has to reason about what actually changed.

    dry_run=True (default): reports what would happen without touching
    Drive or writing bid_line_items / supersedes. Actual drive_bids rows
    from scan_project_bids are only written when dry_run=False, matching
    the dry-run-first convention used throughout this file.
    """
    with _pg() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, project_code FROM projects WHERE id=%s", (project_id,))
            proj = cur.fetchone()
    if not proj:
        return {"error": f"Project {project_id} not found"}

    # Snapshot: current is_latest bid per (division_num, vendor_name, file_name).
    # Must match scan_project_bids' own is_latest partition key exactly - that
    # recompute already keys on file_name too (2026-07-14 rewrite, see
    # lessons_learned #57/#66) precisely because a single vendor can have
    # multiple genuinely distinct concurrent bids in the same division (e.g.
    # Kubed Fire Suppression submitting separate interior-sprinkler and
    # exterior-wildfire quotes under the same vendor+division). A coarser key
    # here silently collapses two real, unrelated is_latest rows into one dict
    # entry, and this function then misreads the survivor as a "revision" of
    # the other - archiving a still-current bid as if it were superseded.
    with _pg() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, division_num, division_name, vendor_name, vendor_folder_id,
                       file_id, file_name, bid_amount, bid_date
                FROM drive_bids WHERE project_id=%s AND is_latest=TRUE
            """, (project_id,))
            before = {(r["division_num"], r["vendor_name"], r["file_name"]): dict(r) for r in cur.fetchall()}

    scan_result = scan_project_bids(project_id, dry_run=dry_run)
    if "error" in scan_result:
        return scan_result

    if dry_run:
        # In dry-run mode scan_project_bids doesn't write, so there's
        # nothing to diff against yet - just surface what it found.
        return {"project": proj["name"], "dry_run": True, "scan_result": scan_result,
                "note": "Run with dry_run=False to detect and process actual updates."}

    with _pg() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, division_num, division_name, vendor_name, vendor_folder_id,
                       file_id, file_name, bid_amount, bid_date
                FROM drive_bids WHERE project_id=%s AND is_latest=TRUE
            """, (project_id,))
            after = {(r["division_num"], r["vendor_name"], r["file_name"]): dict(r) for r in cur.fetchall()}

    before_groups = _group_bids_by_vendor_division(before)
    after_groups = _group_bids_by_vendor_division(after)

    token = get_google_token("drive")
    updates = []
    skipped_concurrent = []
    for vkey, after_files in after_groups.items():
        before_files = before_groups.get(vkey, {})
        decision = _classify_bid_change(before_files, after_files)

        if decision is None:
            continue  # nothing new for this vendor+division - not an update event

        if decision == "concurrent":
            # Not a clean 1-for-1 replacement - e.g. a vendor with multiple
            # concurrent distinct-scope bids in the same division (like Kubed's
            # separate interior-sprinkler and exterior-wildfire quotes). Report,
            # don't archive anything or guess a supersedes link.
            skipped_concurrent.append({
                "division": vkey[0], "vendor": vkey[1],
                "before_files": list(before_files), "after_files": list(after_files),
                "reason": "multiple concurrent files for this vendor+division - not auto-superseded, needs human review",
            })
            continue

        new_filenames = set(after_files) - set(before_files)
        removed_filenames = set(before_files) - set(after_files)

        old_fname = next(iter(removed_filenames))
        new_fname = next(iter(new_filenames))
        old_row = before_files[old_fname]
        new_row = after_files[new_fname]

        old_amount = float(old_row["bid_amount"]) if old_row["bid_amount"] else None
        new_amount = float(new_row["bid_amount"]) if new_row["bid_amount"] else None
        variance_pct = None
        large_variance = False
        if old_amount and new_amount:
            variance_pct = round((new_amount - old_amount) / old_amount * 100, 1)
            large_variance = abs(variance_pct) > 10

        # Link supersedes + extract line items for the new bid
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE drive_bids SET supersedes=%s WHERE id=%s",
                            (old_row["id"], new_row["id"]))
            conn.commit()
        line_item_result = ingest_bid_line_items(new_row["id"], dry_run=False)

        # Archive the old bid file: rename with [SUPERSEDED YYYYMMDD] prefix,
        # move into an Archive subfolder within the vendor folder. Never
        # permanently deleted - reversible, matches this session's standing
        # rule against hard deletes.
        archived = False
        if old_row["vendor_folder_id"] and old_row["file_id"]:
            today = datetime.datetime.now().strftime("%Y%m%d")
            new_name = f"[SUPERSEDED {today}] {old_row['file_name']}"
            _trash_and_rename(old_row["file_id"], new_name, token)
            _move_to_archive_subfolder(old_row["file_id"], old_row["vendor_folder_id"],
                                        old_row["vendor_folder_id"], token)
            archived = True

        updates.append({
            "division": new_row["division_name"],
            "vendor": new_row["vendor_name"],
            "old_amount": old_amount, "new_amount": new_amount,
            "variance_pct": variance_pct, "large_variance": large_variance,
            "old_bid_date": str(old_row["bid_date"]) if old_row["bid_date"] else None,
            "new_bid_date": str(new_row["bid_date"]) if new_row["bid_date"] else None,
            "old_bid_id": old_row["id"], "new_bid_id": new_row["id"],
            "old_file_archived": archived,
            "line_items_found": line_item_result.get("line_items_found"),
            "reconciliation": line_item_result.get("reconciliation"),
        })

    return {"project": proj["name"], "project_id": project_id, "dry_run": False,
            "scan_result": scan_result, "updates_detected": len(updates), "updates": updates,
            "skipped_concurrent": skipped_concurrent}

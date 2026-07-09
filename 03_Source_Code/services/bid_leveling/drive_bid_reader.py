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
        text = response.content[0].text.strip()
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        return json.loads(text)
    except Exception as e:
        return {"error": str(e)}


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
    results = []
    div_folders = _drive_list(bid_folder_id, token)

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
            division_num  = div_raw[:2]
            division_name = div_raw

        results.extend(_walk_vendor_level(div_folder["id"], token, division_num, division_name, depth=0))
    return results


_TRAILING_DATE_RE = re.compile(
    r"^(.+?)[\s_-]+(\d{1,2}[-./]\d{1,2}[-./]\d{2,4}|\d{4}-\d{2}-\d{2})", re.IGNORECASE
)


def _vendor_name_from_filename(filename: str) -> str:
    """Buck's stated canonical pattern: company-named folder, bid file named
    'Company Date.ext'. When a bid file is found loose (not in its own company
    folder - the exact gap Buck flagged: 'there might be bids placed in the
    divisional folders that are not in hubspot'), extract the vendor name from
    the filename using that same convention rather than dropping the file."""
    base = re.sub(r"\.(pdf|docx?|xlsx?)$", "", filename, flags=re.IGNORECASE).strip()
    m = _TRAILING_DATE_RE.match(base)
    return (m.group(1) if m else base).strip()


_NON_BID_FILENAME_RE = re.compile(
    r"\b(SOW|scope of work|bid email template|bid request|bid package set|"
    r"email templates?|division index|bid instructions?)\b", re.IGNORECASE
)


def _is_outbound_not_a_bid(filename: str) -> bool:
    """Files HCI sends OUT (scope-of-work docs, email templates, bid-request
    letters) live in the same vendor/division folders as real vendor bid
    responses and were being walked and extracted as if they were bids -
    found live 2026-07-09 when Buck caught SOW/template filenames appearing
    as 'SUBCONTRACTOR' rows in generated leveling sheets with bid_amount
    always null. Filename-pattern exclusion, not content-based, because
    these are outbound documents HCI authors - the filenames are the
    reliable signal, not something that needs a PDF read to detect."""
    return bool(_NON_BID_FILENAME_RE.search(filename))


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
        sub_entries = _drive_list(entry["id"], token)
        # "Archived"/"Old"/"Superseded" subfolders don't disqualify a folder from
        # being a real leaf vendor folder - found live: "Accurate Insulation/"
        # (a real, correctly-named company folder) has an "Archived/" subfolder
        # inside it for old bid versions, which otherwise made this folder look
        # like a category and triggered a pointless recursion into it.
        sub_folders = [e for e in sub_entries if "folder" in e.get("mimeType", "")
                       and not re.match(r"^(archived?|old|superseded)\b", e["name"], re.IGNORECASE)]
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
            INSERT INTO bid_packages (project_id, csi_division, package_name, status, notes)
            VALUES (%s, %s, %s, 'bid_received', 'Auto-created from Drive bid scan - no matching HubSpot-sourced package found')
        """, (row["project_id"], f"{row['division_num']} — {row['division_name']}", row["vendor_name"]))


def scan_project_bids(project_id: int, dry_run: bool = True) -> dict:
    """
    Scan a project's bid_folder_id, extract new/updated bids, upsert to drive_bids.
    dry_run=True: return what would be processed without writing to DB.
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
    files = walk_bid_folders(proj["bid_folder_id"], token)
    if not files:
        return {"project": proj["name"], "files_found": 0, "new_bids": 0, "dry_run": dry_run}

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

            # Fix is_latest: for each (project, division, vendor) set only the newest file as latest
            cur.execute("""
                WITH ranked AS (
                    SELECT id,
                           ROW_NUMBER() OVER (
                               PARTITION BY project_id, division_num, vendor_name
                               ORDER BY COALESCE(bid_date, '1900-01-01'::date) DESC, id DESC
                           ) AS rn
                    FROM drive_bids WHERE project_id = %s
                )
                UPDATE drive_bids
                SET is_latest = (ranked.rn = 1)
                FROM ranked WHERE drive_bids.id = ranked.id
            """, (project_id,))
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
    }


def read_drive_bids(project_id: int, latest_only: bool = True) -> dict:
    """
    Read drive_bids from DB for a project.
    Returns dict keyed by division_num → list of vendor bids.
    """
    with _pg() as conn:
        with conn.cursor() as cur:
            q = "SELECT * FROM drive_bids WHERE project_id=%s"
            if latest_only:
                q += " AND is_latest=TRUE"
            q += " ORDER BY division_num, vendor_name, bid_date DESC"
            cur.execute(q, (project_id,))
            rows = [dict(r) for r in cur.fetchall()]

    result = {}
    for row in rows:
        div = row["division_num"]
        result.setdefault(div, {
            "division_num":  div,
            "division_name": row.get("division_name", ""),
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


def get_leveling_summary(project_id: int) -> dict:
    """
    Return leveling summary per division: low bid, spread, vendor count.
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
        low_vendor = next((b["vendor"] for b in bids if b["amount"] == low_bid), "")
        summary[div_num] = {
            "division_name": div_data["division_name"],
            "bid_count":     len(bids),
            "low_bid":       low_bid,
            "low_vendor":    low_vendor,
            "high_bid":      high_bid,
            "spread":        spread,
            "spread_pct":    round((spread / low_bid) * 100, 1) if low_bid else None,
            "bids":          sorted(bids, key=lambda b: b["amount"] or 0),
        }
    return summary

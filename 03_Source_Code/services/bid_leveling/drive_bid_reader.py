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


def _export_google_doc(file_id: str, token: str) -> str:
    """Export Google Docs/Sheets as plain text."""
    url = f"{BASE_URL}/files/{file_id}/export?mimeType=text/plain&supportsAllDrives=true"
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


def extract_bid_from_text(text: str, vendor_name: str, file_name: str) -> dict:
    """
    Fallback: extract bid amount from text via regex.
    Used for Google Docs/Sheets where we can export as text without Gemini.
    """
    # Find dollar amounts — look for "total", "grand total", "base bid" patterns
    patterns = [
        r"(?:grand\s+total|total\s+base\s+bid|base\s+bid\s+price|total\s+price|total\s+contract\s+price)[^\$\n]*\$?\s*([\d,]+\.?\d*)",
        r"total[:\s]+\$?\s*([\d,]+\.?\d*)",
        r"\$\s*([\d,]+\.?\d*)\s*(?:dollars?)?(?:\s|$)",
    ]
    amount = None
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            try:
                amount = float(m.group(1).replace(",", ""))
                break
            except ValueError:
                continue

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

    return {
        "bid_amount": amount,
        "bid_date": date_str,
        "scope_summary": f"Extracted from {file_name}",
    }


_DIV_PREFIX_RE = re.compile(r"^(\d+)[_\s-]+(.+)$")


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
                   and (e.get("mimeType") in READABLE_MIME or e.get("name", "").lower().endswith((".pdf", ".docx")))]

    for entry in folders:
        name = entry["name"]
        sub_entries = _drive_list(entry["id"], token)
        sub_folders = [e for e in sub_entries if "folder" in e.get("mimeType", "")]
        sub_files = [e for e in sub_entries if "folder" not in e.get("mimeType", "")
                     and (e.get("mimeType") in READABLE_MIME or e.get("name", "").lower().endswith((".pdf", ".docx")))]
        # A folder is a leaf vendor folder only if it has no subfolders of its
        # own. Any subfolder presence means recurse - Buck found live that a
        # folder can have BOTH a real vendor subfolder and a loose unorganized
        # file side by side ("Fire Suppression" had "KFS/" plus a bare PDF) -
        # checking sub_files alone (whether this folder itself has files) picked
        # the wrong branch and silently dropped KFS entirely.
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
                text = _export_google_doc(f["file_id"], token)
                data = extract_bid_from_text(text, f["vendor_name"], f["file_name"])
                source = "regex_text"
            elif mime == "application/pdf" or f["file_name"].lower().endswith(".pdf"):
                if GEMINI_API_KEY:
                    pdf_bytes = _download_bytes(f["file_id"], token)
                    data      = extract_bid_with_gemini(pdf_bytes, f["vendor_name"],
                                                        proj["name"], f["division_name"])
                    source    = "gemini"
                else:
                    data   = {"bid_amount": None, "bid_date": None, "scope_summary": "PDF — Gemini key not set"}
                    source = "pending"
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

    return {
        "project":    proj["name"],
        "project_id": project_id,
        "dry_run":    False,
        "files_found":   len(files),
        "already_known": skipped,
        "new_bids":      upserted,
        "errors":        errors,
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

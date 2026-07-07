"""
HubSpot Bid Sync — HCI AI Operating System

Closes the real gap found 2026-07-07: bid_leveling only ever knew about bids that
someone manually typed into the Google Sheet tracker, or manually dropped as a PDF
into the exact 00_Bids/{div}_{name}/{vendor}/ Drive folder structure. Neither path
ever looked at HubSpot, where actual vendor bid correspondence and attachments live
as emails on each division's deal. Verified live: 1355 Riverside's cabinet division
deal alone has 35 associated emails that had never been touched by anything - the
Sheet had 3 vendors (2 priced), the DB had a 4th vendor entirely absent from the
Sheet, and none of that matched what's actually in HubSpot.

This module does NOT duplicate drive_bid_reader.py's PDF-extraction/leveling logic.
It only gets HubSpot deal attachments into the same 00_Bids/{div}/{vendor}/ folder
structure drive_bid_reader.py already knows how to walk - so a normal
run_bid_leveling(scan_drive=True) call picks these up automatically on its next run.

Hard dependency, currently blocked: the HubSpot Private App key must have
crm.objects.emails.read + sales-email-read scopes. Without them every HubSpot email
call below 403s with "app must require the sales-email-read scope" - confirmed live
2026-07-07 via both the modern CRM API and the legacy Engagements API. This is a
HubSpot admin console change (Settings > Integrations > Private Apps > scopes), not
something fixable in code. Every function here fails loud with that exact message
rather than silently returning empty results, so it's obvious when the scope is
still missing vs. when a sync genuinely found nothing.
"""
import sys, os, re, json, ssl, urllib.parse, urllib.request, urllib.error, uuid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "integrations"))

import psycopg2, psycopg2.extras, certifi
from dotenv import load_dotenv
from typing import Optional

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

from credentials import get_google_token
from bid_leveling_service import (
    CSI_DIVISIONS, _drive_list, _drive_create_folder, _drive_upload, _drive_find_file,
)

SSL_CTX  = ssl.create_default_context(cafile=certifi.where())
HS_BASE  = "https://api.hubapi.com"

DB = dict(
    host=os.environ.get("POSTGRES_HOST", "localhost"),
    port=int(os.environ.get("POSTGRES_PORT", 5432)),
    dbname=os.environ.get("POSTGRES_DB", "hci_os"),
    user=os.environ.get("POSTGRES_USER", "hci_admin"),
    password=os.environ.get("POSTGRES_PASSWORD", ""),
)

# HubSpot deal names for division-level packages follow "{Project} — {div}{sub} {Desc}",
# e.g. "1355 Riverside — 06D Custom Cabinets (Kitchen / Baths / Laundry / Built-ins)".
_DEAL_DIV_PATTERN = re.compile(r"—\s*(\d{2})([A-Z]?)\s+(.+)$")


def _pg():
    return psycopg2.connect(**DB, cursor_factory=psycopg2.extras.RealDictCursor)


def _hs_token() -> str:
    t = os.environ.get("HUBSPOT_API_KEY", "")
    if not t:
        raise RuntimeError("HUBSPOT_API_KEY not set in environment")
    return t


def _hs_request(path: str, method: str = "GET", body: Optional[dict] = None) -> tuple:
    """Returns (status_code, parsed_json_or_error_text)."""
    url = f"{HS_BASE}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url, data=data,
        headers={"Authorization": f"Bearer {_hs_token()}", "Content-Type": "application/json"},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()
        return e.code, body_text


def _scope_missing(status: int, body) -> bool:
    text = body if isinstance(body, str) else json.dumps(body)
    return status in (403,) and ("scope" in text.lower())


def find_division_deals(project_name: str) -> list:
    """Find every HubSpot deal that looks like this project's division-level bid
    package (name pattern '{project_name} — {div}{sub} {description}'), parsed into
    {deal_id, csi_division, division_name, deal_name, amount}."""
    with _pg() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT hubspot_deal_id, deal_name, amount FROM hubspot_deals
                WHERE deal_name ILIKE %s
            """, (f"{project_name} —%",))
            rows = cur.fetchall()
    out = []
    for r in rows:
        m = _DEAL_DIV_PATTERN.search(r["deal_name"])
        if not m:
            continue
        div_num, sub, desc = m.groups()
        out.append({
            "deal_id":       r["hubspot_deal_id"],
            "deal_name":     r["deal_name"],
            "amount":        float(r["amount"]) if r["amount"] else None,
            "csi_division":  div_num,
            "sub":           sub,
            "description":   desc.strip(),
            "division_name": CSI_DIVISIONS.get(div_num, desc.strip()),
        })
    return out


def get_deal_attachment_emails(deal_id: str) -> dict:
    """Fetch every email associated with a deal, with subject + attachment info.
    Returns {"emails": [...], "scope_blocked": bool, "error": str|None}."""
    status, assoc = _hs_request(f"/crm/v3/objects/deals/{deal_id}/associations/emails")
    if status != 200:
        return {"emails": [], "scope_blocked": _scope_missing(status, assoc), "error": str(assoc)}

    email_ids = [r["id"] for r in assoc.get("results", [])]
    emails = []
    scope_blocked = False
    props = "hs_email_subject,hs_timestamp,hs_email_from_email,hs_attachment_ids"
    for eid in email_ids:
        status, r = _hs_request(f"/crm/v3/objects/emails/{eid}?properties={props}")
        if status != 200:
            if _scope_missing(status, r):
                scope_blocked = True
            continue
        p = r.get("properties", {})
        att_ids = [a for a in (p.get("hs_attachment_ids") or "").split(";") if a]
        emails.append({
            "email_id":     eid,
            "subject":      p.get("hs_email_subject"),
            "timestamp":    p.get("hs_timestamp"),
            "from_email":   p.get("hs_email_from_email"),
            "attachment_ids": att_ids,
        })
    return {"emails": emails, "scope_blocked": scope_blocked, "error": None}


def download_hs_attachment(file_id: str) -> tuple:
    """Downloads a HubSpot file-manager attachment. Returns (bytes, filename, mime_type)
    or (None, None, None) on failure."""
    status, meta = _hs_request(f"/files/v3/files/{file_id}")
    if status != 200:
        return None, None, None
    url = meta.get("url") or (meta.get("defaultHostingUrl"))
    if not url:
        return None, None, None
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {_hs_token()}"})
    try:
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=60) as resp:
            return resp.read(), meta.get("name", file_id), meta.get("type", "application/pdf")
    except urllib.error.HTTPError:
        return None, None, None


def _vendor_folder_name(from_email: str) -> str:
    """Best-effort vendor name from a sender address until a real vendor match exists -
    e.g. karen@aspencabs.com -> 'aspencabs'. Good enough to keep files grouped by
    sender; a human/GBT can rename the folder to the real vendor name in Drive later."""
    if not from_email or "@" not in from_email:
        return "Unknown Vendor"
    domain = from_email.split("@")[-1].split(".")[0]
    return domain.replace("-", " ").title()


def sync_project_hubspot_bids(project_id: int, csi_division: Optional[str] = None,
                               dry_run: bool = True) -> dict:
    """
    For every division-level HubSpot deal on this project (optionally filtered to one
    csi_division), pull attached bid documents from associated emails and place them
    into 00_Bids/{div}_{name}/{vendor}/ in Drive - the exact structure
    drive_bid_reader.scan_project_bids() already walks. Does not run leveling itself;
    call run_bid_leveling(scan_drive=True) afterward to pick these up.
    """
    with _pg() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, bid_folder_id FROM projects WHERE id=%s", (project_id,))
            proj = cur.fetchone()
    if not proj:
        return {"error": f"No project {project_id}"}
    if not proj["bid_folder_id"]:
        return {"error": f"Project {proj['name']} has no bid_folder_id configured — run bid_leveling once first to create it"}

    deals = find_division_deals(proj["name"])
    if csi_division:
        deals = [d for d in deals if d["csi_division"] == csi_division]

    token_drive = get_google_token("drive")
    div_folder_cache: dict = {}
    result = {
        "project": proj["name"], "project_id": project_id, "mode": "dry_run" if dry_run else "live",
        "deals_checked": len(deals), "divisions": {}, "scope_blocked": False,
    }

    for deal in deals:
        div = deal["csi_division"]
        div_result = {
            "deal_id": deal["deal_id"], "deal_name": deal["deal_name"],
            "budget_amount": deal["amount"], "emails_checked": 0,
            "attachments_found": 0, "attachments_synced": [], "errors": [],
        }

        emails = get_deal_attachment_emails(deal["deal_id"])
        if emails["scope_blocked"]:
            result["scope_blocked"] = True
            div_result["errors"].append(
                "HubSpot app missing crm.objects.emails.read / sales-email-read scope — "
                "cannot read email content or attachments until this is granted in "
                "HubSpot Settings > Integrations > Private Apps."
            )
            result["divisions"][div] = div_result
            continue
        if emails["error"]:
            div_result["errors"].append(emails["error"])
            result["divisions"][div] = div_result
            continue

        div_result["emails_checked"] = len(emails["emails"])

        for email in emails["emails"]:
            for att_id in email["attachment_ids"]:
                div_result["attachments_found"] += 1
                content, filename, mime = download_hs_attachment(att_id)
                if not content:
                    div_result["errors"].append(f"Could not download attachment {att_id} from email {email['email_id']}")
                    continue

                vendor_name = _vendor_folder_name(email.get("from_email"))

                if dry_run:
                    div_result["attachments_synced"].append({
                        "vendor": vendor_name, "filename": filename,
                        "action": "would_upload", "from_email": email.get("from_email"),
                    })
                    continue

                # Ensure {div}_{name}/{vendor}/ folder path exists in Drive
                if div not in div_folder_cache:
                    div_folder_name = f"{div}_{deal['division_name']}"
                    existing = _drive_find_file(proj["bid_folder_id"], div_folder_name, token_drive)
                    div_folder_id = existing or _drive_create_folder(proj["bid_folder_id"], div_folder_name, token_drive)
                    div_folder_cache[div] = div_folder_id
                div_folder_id = div_folder_cache[div]

                vendor_key = f"{div}::{vendor_name}"
                if vendor_key not in div_folder_cache:
                    existing = _drive_find_file(div_folder_id, vendor_name, token_drive)
                    vendor_folder_id = existing or _drive_create_folder(div_folder_id, vendor_name, token_drive)
                    div_folder_cache[vendor_key] = vendor_folder_id
                vendor_folder_id = div_folder_cache[vendor_key]

                if _drive_find_file(vendor_folder_id, filename, token_drive):
                    div_result["attachments_synced"].append({
                        "vendor": vendor_name, "filename": filename, "action": "already_synced",
                    })
                    continue

                file_id = _drive_upload(vendor_folder_id, filename, content, mime, token_drive)
                div_result["attachments_synced"].append({
                    "vendor": vendor_name, "filename": filename, "action": "uploaded", "drive_file_id": file_id,
                })

        result["divisions"][div] = div_result

    return result

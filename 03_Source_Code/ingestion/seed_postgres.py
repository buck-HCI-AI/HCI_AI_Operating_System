#!/usr/bin/env python3
"""
seed_postgres.py
Seeds Postgres with current HCI project/vendor/bid data.
Sources: HubSpot contacts + Google Sheets bid trackers.
Safe to re-run — checks existence before inserting.
"""
import sys, os, json, urllib.request, urllib.parse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "integrations"))

import ssl, certifi
import psycopg2
from credentials import decrypt_credential, CRED_IDS

SSL_CTX = ssl.create_default_context(cafile=certifi.where())

DB = dict(host="localhost", port=5432, dbname="hci_os", user="hci_admin", password="hci_postgres_2026")

def conn():
    return psycopg2.connect(**DB)

# ── HubSpot ───────────────────────────────────────────────────────────────────

def hs_auth():
    return decrypt_credential(CRED_IDS["hubspot"])["value"]

def hs_get(path):
    req = urllib.request.Request(f"https://api.hubapi.com{path}")
    req.add_header("Authorization", hs_auth())
    try:
        with urllib.request.urlopen(req, context=SSL_CTX) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"  ✗ HubSpot: {e}")
        return {}

def get_contacts():
    props = "firstname,lastname,company,email,phone"
    results, after = [], None
    while True:
        url = f"/crm/v3/objects/contacts?limit=100&properties={props}"
        if after:
            url += f"&after={after}"
        data = hs_get(url)
        results.extend(data.get("results", []))
        after = (data.get("paging") or {}).get("next", {}).get("after")
        if not after:
            break
    return results

# ── Google Sheets ─────────────────────────────────────────────────────────────

def sheets_token():
    return decrypt_credential(CRED_IDS["google_sheets"])["oauthTokenData"]["access_token"]

def read_sheet(sheet_id, range_):
    token = sheets_token()
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/{urllib.parse.quote(range_)}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, context=SSL_CTX) as r:
            return json.loads(r.read()).get("values", [])
    except Exception as e:
        print(f"  ✗ Sheets {sheet_id}: {e}")
        return []

# ── Seed: projects ────────────────────────────────────────────────────────────

PROJECTS = [
    ("64 Eastwood",    "64 Eastwood Dr.",    "Exterior & Site",     "332246098523", "1yAmLo3IIp3Vqs3BQJ6QB2O4as0KqXMZxcVvjzGBZDcQ"),
    ("101 Francis",    "101 W Francis St.",  "Full Interior Remodel","332313009897","1JExX5CeVBedTEFitM8B6hveF4Prhk0Oy6BZSBu058LE"),
    ("1355 Riverside", "1355 Riverside Dr.", "Full Remodel",         None,          "1-64X4XGc4P_GmYl7DRt8nGsBNfaVdP_G3qwfBLJSsnA"),
    ("83 Sagebrusch",  "83 Sagebrusch Ln.",  "TBD",                  None,          None),
]

def seed_projects(cur):
    print("\n=== Projects ===")
    for name, addr, scope, hs_deal, sheet_id in PROJECTS:
        cur.execute("SELECT id FROM projects WHERE name = %s", (name,))
        row = cur.fetchone()
        if row:
            cur.execute("""UPDATE projects SET address=%s, scope=%s, hubspot_deal_id=%s,
                          gsheet_bid_tracker=%s, updated_at=NOW() WHERE name=%s""",
                       (addr, scope, hs_deal, sheet_id, name))
            print(f"  ~ {name} updated")
        else:
            cur.execute("""INSERT INTO projects (name, address, city, state, status, scope,
                          hubspot_deal_id, gsheet_bid_tracker)
                          VALUES (%s, %s, 'Aspen', 'CO', 'active', %s, %s, %s)""",
                       (name, addr, scope, hs_deal, sheet_id))
            print(f"  + {name} inserted")

# ── Seed: vendors from HubSpot ────────────────────────────────────────────────

def seed_vendors(cur):
    print("\n=== Vendors (HubSpot contacts) ===")
    contacts = get_contacts()
    print(f"  Fetched {len(contacts)} contacts")
    count = 0
    for c in contacts:
        p = c.get("properties", {})
        company = (p.get("company") or "").strip()
        if not company:
            continue
        hs_id = c["id"]
        first = (p.get("firstname") or "").strip()
        last  = (p.get("lastname") or "").strip()
        contact_name = f"{first} {last}".strip()

        cur.execute("SELECT id FROM vendors WHERE hubspot_contact_id = %s", (hs_id,))
        if cur.fetchone():
            cur.execute("""UPDATE vendors SET company_name=%s, contact_name=%s,
                          email=%s, phone=%s, updated_at=NOW()
                          WHERE hubspot_contact_id=%s""",
                       (company, contact_name or None, p.get("email"), p.get("phone"), hs_id))
        else:
            cur.execute("""INSERT INTO vendors (company_name, contact_name, email, phone,
                          hubspot_contact_id)
                          VALUES (%s, %s, %s, %s, %s)""",
                       (company, contact_name or None, p.get("email"), p.get("phone"), hs_id))
            count += 1
    print(f"  ✓ {count} new vendors inserted")

# ── Seed: bid packages + entries from Sheets ──────────────────────────────────

SHEET_CONFIG = [
    ("64 Eastwood",    "1yAmLo3IIp3Vqs3BQJ6QB2O4as0KqXMZxcVvjzGBZDcQ", "Bid Tracking!A1:N60"),
    ("101 Francis",    "1JExX5CeVBedTEFitM8B6hveF4Prhk0Oy6BZSBu058LE", "Bid Tracking!A1:N60"),
    ("1355 Riverside", "1-64X4XGc4P_GmYl7DRt8nGsBNfaVdP_G3qwfBLJSsnA", "Sheet1!A1:N60"),
]

def clean_amount(val):
    if not val:
        return None
    try:
        return float(str(val).replace("$", "").replace(",", "").strip())
    except ValueError:
        return None

def seed_bids(cur):
    print("\n=== Bid Packages + Entries (Google Sheets) ===")
    for project_name, sheet_id, range_ in SHEET_CONFIG:
        cur.execute("SELECT id FROM projects WHERE name = %s", (project_name,))
        row = cur.fetchone()
        if not row:
            print(f"  ✗ {project_name} not found")
            continue
        project_id = row[0]

        rows = read_sheet(sheet_id, range_)
        if not rows:
            print(f"  ✗ {project_name}: no sheet data")
            continue

        headers = [h.strip().lower() for h in rows[0]] if rows else []
        pkg_count = bid_count = 0

        for data_row in rows[1:]:
            if not data_row:
                continue
            # Skip rows that look like headers or section titles
            first_cell = str(data_row[0]).strip() if data_row else ""
            if not first_cell or first_cell.lower() in ("", "package", "#", "csi", "scope"):
                continue

            # Build row dict from headers
            r = {headers[i]: (data_row[i] if i < len(data_row) else "")
                 for i in range(len(headers))}

            # Package name: try common column names, fall back to positional
            pkg_name = (r.get("package") or r.get("scope") or r.get("trade") or
                       r.get("description") or r.get("package name") or
                       (data_row[1] if len(data_row) > 1 else "") or
                       first_cell)
            if not pkg_name or pkg_name.strip().isdigit():
                continue
            pkg_name = pkg_name.strip()

            csi = (r.get("csi") or r.get("csi division") or r.get("division") or
                   first_cell if first_cell and not first_cell.isdigit() else "TBD") or "TBD"

            # Check if bid package exists
            cur.execute("SELECT id FROM bid_packages WHERE project_id=%s AND package_name=%s",
                       (project_id, pkg_name))
            pkg_row = cur.fetchone()
            if pkg_row:
                pkg_id = pkg_row[0]
            else:
                cur.execute("""INSERT INTO bid_packages (project_id, csi_division, package_name, status)
                              VALUES (%s, %s, %s, 'bids_receiving') RETURNING id""",
                           (project_id, csi[:50], pkg_name))
                pkg_id = cur.fetchone()[0]
                pkg_count += 1

            # Look for bid amount — check columns F, G, H etc.
            amount = None
            date_recv = None
            notes_val = None
            vendor_str = None

            # Try header-based lookup first
            amount_keys = ["amount", "bid", "total", "price", "bid amount"]
            date_keys   = ["date", "bid date", "received", "date received"]
            vendor_keys = ["vendor", "sub", "contractor", "company", "bidder"]
            notes_keys  = ["notes", "note", "comments"]

            for k in amount_keys:
                if r.get(k):
                    amount = clean_amount(r[k]); break
            for k in date_keys:
                if r.get(k):
                    date_recv = r[k]; break
            for k in vendor_keys:
                if r.get(k):
                    vendor_str = r[k]; break
            for k in notes_keys:
                if r.get(k):
                    notes_val = r[k]; break

            # Fall back to positional (F=col5, G=col6...)
            if not amount and len(data_row) > 5:
                amount = clean_amount(data_row[5])
            if not date_recv and len(data_row) > 4:
                date_recv = data_row[4] or None
            if not vendor_str and len(data_row) > 3:
                vendor_str = data_row[3] or None
            if not notes_val and len(data_row) > 10:
                notes_val = data_row[10] or None

            if amount and amount > 0:
                notes_full = f"Vendor: {vendor_str}" if vendor_str else None
                if notes_val:
                    notes_full = f"{notes_full or ''} | {notes_val}".strip(" |")
                cur.execute("""
                    INSERT INTO bid_entries (bid_package_id, project_id, bid_amount,
                                           date_received, status, notes)
                    VALUES (%s, %s, %s, %s, 'bid_received', %s)
                """, (pkg_id, project_id, amount, date_recv or None, notes_full))
                bid_count += 1

        print(f"  ✓ {project_name}: {pkg_count} packages, {bid_count} bid entries")

# ── Main ──────────────────────────────────────────────────────────────────────

def run():
    c = conn()
    cur = c.cursor()
    try:
        seed_projects(cur)
        seed_vendors(cur)
        seed_bids(cur)
        c.commit()
        print("\n  ✓ Postgres seeding complete")
    except Exception as e:
        c.rollback()
        print(f"\n  ✗ Error: {e}")
        import traceback; traceback.print_exc()
    finally:
        cur.close(); c.close()

if __name__ == "__main__":
    run()

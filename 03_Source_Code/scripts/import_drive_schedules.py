#!/usr/bin/env python3
"""Import MS Project schedule xlsx files from Google Drive into project_schedule_items."""

import sys, io, os
from datetime import datetime, date

sys.path.insert(0, "/Users/buckadams/HCI_AI_Operating_System/03_Source_Code/integrations")
sys.path.insert(0, "/Users/buckadams/HCI_AI_Operating_System/03_Source_Code/services/drive_intelligence")

import requests
import pandas as pd
import psycopg2
from drive_client import get_google_token

DB = dict(host="localhost", port=5432, dbname="hci_os", user="hci_admin", password="hci_postgres_2026")

PROJECTS = [
    {
        "project_id": "1",
        "project_code": "64EW",
        "name": "64 Eastwood",
        "file_id": "1QBqBJ66pNp69FMvI4s1jUKtnoSqq3lY3",
        "sheet": "Production Schedule",
        "cols": {
            "id": "Activity ID",
            "title": "Task Name",
            "start": "Start",
            "end": "Finish",
            "status": "Status",
            "assignee": "Owner",
            "pct": "% Complete",
            "type": "Phase",
            "notes": "Notes",
            "milestone": "Milestone",
            "critical": "Critical",
        },
        "id_prefix": "",  # EWD-001 already unique
    },
    {
        "project_id": "2",
        "project_code": "101F",
        "name": "101 Francis",
        "file_id": "1lCfBxvJQhKT5svM84KSZv0JV7Ezs3_6H",
        "sheet": "Production CPM v1.0",
        "cols": {
            "id": "ID",
            "title": "Task Name",
            "start": "Start",
            "end": "Finish",
            "status": "Status",
            "assignee": "Responsible",
            "pct": "% Complete",
            "type": "Phase",
            "notes": "Notes",
            "milestone": "Milestone?",
            "critical": "Critical?",
        },
        "id_prefix": "101F-",  # numeric IDs need prefix
    },
    {
        "project_id": "3",
        "project_code": "1355R",
        "name": "1355 Riverside",
        "file_id": "1UbRRYCAWcKJZw2eVgp0z5DBbUxO82gH6",
        "sheet": "Production_Schedule",
        "cols": {
            "id": "Activity ID",
            "title": "Activity Name",
            "start": "Planned Start",
            "end": "Planned Finish",
            "status": "Status",
            "assignee": "Responsible",
            "pct": "Percent Complete",
            "type": None,  # no Phase column
            "notes": "Notes",
            "milestone": "Milestone",
            "critical": "Critical Path",
        },
        "id_prefix": "",  # M-000, G-001 etc. already unique
    },
]

EXCEL_EPOCH = pd.Timestamp("1899-12-30")

def excel_serial_to_date(val):
    """Convert Excel serial number to Python date."""
    if pd.isna(val):
        return None
    if isinstance(val, (datetime, pd.Timestamp)):
        return val.date()
    if isinstance(val, date):
        return val
    try:
        n = float(val)
        return (EXCEL_EPOCH + pd.Timedelta(days=int(n))).date()
    except (ValueError, TypeError):
        return None

def parse_date(val):
    if pd.isna(val):
        return None
    if isinstance(val, pd.Timestamp):
        return val.date()
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val
    s = str(val).strip()
    if s in ("", "nan", "None"):
        return None
    # Try Excel serial
    try:
        n = float(s)
        if n > 1000:  # plausible serial
            return (EXCEL_EPOCH + pd.Timedelta(days=int(n))).date()
    except ValueError:
        pass
    # Try string parse
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None

def safe_str(val, max_len=2000):
    if pd.isna(val):
        return None
    s = str(val).strip()
    return s[:max_len] if s not in ("nan", "None", "") else None

def safe_pct(val):
    if pd.isna(val):
        return None
    try:
        f = float(val)
        # Handle 0-1 range (e.g. 0.75) vs 0-100 range
        if 0 < f <= 1.0:
            return round(f * 100, 2)
        return round(f, 2)
    except (ValueError, TypeError):
        return None

def download_bytes(file_id):
    token = get_google_token("drive")
    r = requests.get(
        f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media",
        headers={"Authorization": f"Bearer {token}"}, timeout=60
    )
    if not r.ok:
        raise RuntimeError(f"Drive download failed: {r.status_code}")
    return r.content

def import_project(proj, conn):
    print(f"\n{'='*60}")
    print(f"  {proj['name']} — {proj['sheet']}")
    print(f"{'='*60}")

    data = download_bytes(proj["file_id"])
    xf = pd.ExcelFile(io.BytesIO(data), engine="openpyxl")
    df = xf.parse(proj["sheet"], header=0)

    cols = proj["cols"]
    prefix = proj["id_prefix"]
    project_id = proj["project_id"]

    print(f"  Rows loaded: {len(df)}")
    print(f"  Columns: {list(df.columns[:8])}")

    inserted = 0
    skipped = 0
    errors = 0

    with conn.cursor() as cur:
        for _, row in df.iterrows():
            raw_id = safe_str(row.get(cols["id"]))
            if not raw_id:
                skipped += 1
                continue

            activity_id = f"{prefix}{raw_id}"
            title = safe_str(row.get(cols["title"]))
            if not title:
                skipped += 1
                continue

            start_date = parse_date(row.get(cols["start"]))
            end_date = parse_date(row.get(cols["end"]))
            status = safe_str(row.get(cols["status"]))
            assignee = safe_str(row.get(cols["assignee"]))
            completion_pct = safe_pct(row.get(cols["pct"]))
            task_type = safe_str(row.get(cols["type"])) if cols["type"] else None
            notes = safe_str(row.get(cols["notes"]))

            # Append milestone/critical flags to notes
            milestone = safe_str(row.get(cols["milestone"]))
            critical = safe_str(row.get(cols["critical"]))
            meta = []
            if milestone and milestone.lower() in ("yes", "true", "1"):
                meta.append("milestone:yes")
            if critical and critical.lower() in ("yes", "true", "1"):
                meta.append("critical:yes")
            if meta:
                notes = (notes or "") + " [" + ", ".join(meta) + "]"
                notes = notes.strip()

            try:
                cur.execute("""
                    INSERT INTO project_schedule_items
                        (activity_id, project_id, title, start_date, end_date,
                         status, assignee, completion_pct, task_type, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (activity_id) DO UPDATE SET
                        title = EXCLUDED.title,
                        start_date = EXCLUDED.start_date,
                        end_date = EXCLUDED.end_date,
                        status = EXCLUDED.status,
                        assignee = EXCLUDED.assignee,
                        completion_pct = EXCLUDED.completion_pct,
                        task_type = EXCLUDED.task_type,
                        notes = EXCLUDED.notes,
                        synced_at = now()
                """, (
                    activity_id, project_id, title,
                    start_date, end_date, status, assignee,
                    completion_pct, task_type, notes
                ))
                inserted += 1
            except Exception as e:
                errors += 1
                if errors <= 3:
                    print(f"  ⚠ Row error ({activity_id}): {e}")

    conn.commit()
    print(f"  ✅ Imported: {inserted}  Skipped: {skipped}  Errors: {errors}")
    return inserted

def main():
    print("\n🏗  HCI AI — Drive Schedule Import")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    conn = psycopg2.connect(**DB)

    total = 0
    for proj in PROJECTS:
        try:
            n = import_project(proj, conn)
            total += n
        except Exception as e:
            print(f"  ❌ {proj['name']} failed: {e}")

    conn.close()

    print(f"\n{'='*60}")
    print(f"  TOTAL RECORDS IMPORTED: {total}")
    print(f"{'='*60}\n")

    # Verify
    conn2 = psycopg2.connect(**DB)
    with conn2.cursor() as cur:
        cur.execute("""
            SELECT p.name, COUNT(*) as items
            FROM project_schedule_items h
            JOIN projects p ON p.id::text = h.project_id
            GROUP BY p.name ORDER BY p.id
        """)
        rows = cur.fetchall()
        print("  DB verification:")
        for name, count in rows:
            print(f"    {name}: {count} schedule items")
    conn2.close()

if __name__ == "__main__":
    main()

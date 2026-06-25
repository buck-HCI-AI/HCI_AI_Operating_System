"""
WF-003: Morning Brief
Compiles daily priority email from Postgres + HubSpot + Outlook and sends to Buck.
Trigger: system wake / launchd cron / manual POST /workflows/morning-brief
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "integrations"))

import psycopg2, psycopg2.extras
from datetime import date
from hubspot import get_overdue_tasks
from microsoft_graph import list_inbox, send_email

DB = dict(host="localhost", port=5432, dbname="hci_os", user="hci_admin", password="hci_postgres_2026")
BUCK_EMAIL = ("Buck Adams", "buck@ahmaspen.com")


def _pg_rows(sql, params=None):
    conn = psycopg2.connect(**DB, cursor_factory=psycopg2.extras.RealDictCursor)
    cur  = conn.cursor()
    cur.execute(sql, params or [])
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows


def _project_section() -> str:
    projects = _pg_rows("SELECT id, name, address, status FROM projects WHERE status='active' ORDER BY name")
    if not projects:
        return "<p>No active projects.</p>"

    rows_html = ""
    for p in projects:
        # Bid summary per project
        bids = _pg_rows("""
            SELECT COUNT(DISTINCT bp.id) as pkg_count,
                   COUNT(be.id) as bid_count,
                   SUM(CASE WHEN be.bid_amount IS NOT NULL THEN 1 ELSE 0 END) as bids_with_amount,
                   MIN(be.bid_amount) as low_bid
            FROM bid_packages bp
            LEFT JOIN bid_entries be ON be.bid_package_id = bp.id
            WHERE bp.project_id = %s
        """, (p["id"],))
        b = bids[0] if bids else {}
        rows_html += f"""
        <tr>
          <td style="padding:6px 12px;border-bottom:1px solid #eee;font-weight:600">{p['name']}</td>
          <td style="padding:6px 12px;border-bottom:1px solid #eee">{p['address']}</td>
          <td style="padding:6px 12px;border-bottom:1px solid #eee;text-align:center">{b.get('pkg_count',0)}</td>
          <td style="padding:6px 12px;border-bottom:1px solid #eee;text-align:center">{b.get('bids_with_amount',0)}</td>
          <td style="padding:6px 12px;border-bottom:1px solid #eee;text-align:right">
            {'${:,.0f}'.format(b['low_bid']) if b.get('low_bid') else '—'}
          </td>
        </tr>"""

    return f"""
    <table style="border-collapse:collapse;width:100%;font-size:14px">
      <thead>
        <tr style="background:#1a3a5c;color:white">
          <th style="padding:8px 12px;text-align:left">Project</th>
          <th style="padding:8px 12px;text-align:left">Address</th>
          <th style="padding:8px 12px;text-align:center">Packages</th>
          <th style="padding:8px 12px;text-align:center">Bids In</th>
          <th style="padding:8px 12px;text-align:right">Low Bid</th>
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>"""


def _tasks_section() -> str:
    try:
        tasks = get_overdue_tasks(limit=10)
    except Exception:
        tasks = []

    if not tasks:
        return "<p style='color:#666'>No overdue tasks.</p>"

    items = ""
    for t in tasks[:10]:
        props = t.get("properties", {})
        subject = props.get("hs_task_subject", "(no subject)")
        items += f"<li style='margin:4px 0'>{subject}</li>"
    return f"<ul style='margin:0;padding-left:20px'>{items}</ul>"


def _inbox_section() -> str:
    try:
        msgs = list_inbox(top=10)
    except Exception:
        return "<p style='color:#666'>Could not read inbox.</p>"

    unread = [m for m in msgs if not m.get("isRead")]
    if not unread:
        return "<p style='color:#666'>Inbox clear — no unread messages.</p>"

    items = ""
    for m in unread[:8]:
        sender = (m.get("from") or {}).get("emailAddress", {})
        from_name = sender.get("name") or sender.get("address", "?")
        subject = m.get("subject", "(no subject)")
        items += f"<li style='margin:4px 0'><strong>{from_name}</strong> — {subject}</li>"
    return f"<ul style='margin:0;padding-left:20px'>{items}</ul>"


def _build_html(today: str) -> str:
    return f"""
<!DOCTYPE html>
<html>
<body style="font-family:Arial,sans-serif;max-width:700px;margin:0 auto;color:#222">
  <div style="background:#1a3a5c;color:white;padding:20px 24px;border-radius:6px 6px 0 0">
    <h1 style="margin:0;font-size:22px">HCI Morning Brief</h1>
    <p style="margin:4px 0 0;opacity:0.8">{today} — Hendrickson Construction Intelligence</p>
  </div>

  <div style="background:#f8f9fa;padding:20px 24px">

    <h2 style="color:#1a3a5c;border-bottom:2px solid #1a3a5c;padding-bottom:6px;font-size:16px">
      Active Projects &amp; Bid Status
    </h2>
    {_project_section()}

    <h2 style="color:#c0392b;border-bottom:2px solid #c0392b;padding-bottom:6px;font-size:16px;margin-top:24px">
      Overdue Tasks
    </h2>
    {_tasks_section()}

    <h2 style="color:#2980b9;border-bottom:2px solid #2980b9;padding-bottom:6px;font-size:16px;margin-top:24px">
      Unread Inbox
    </h2>
    {_inbox_section()}

  </div>

  <div style="background:#eee;padding:10px 24px;font-size:11px;color:#888;border-radius:0 0 6px 6px">
    HCI AI Operating System — Auto-generated {today}
  </div>
</body>
</html>"""


def run(send: bool = True) -> dict:
    """
    Compile and send the morning brief.
    Returns: {status, email_sent, subject}
    """
    today = date.today().strftime("%A, %B %d, %Y")
    subject = f"HCI Morning Brief — {date.today().strftime('%b %d, %Y')}"
    html = _build_html(today)

    result = {"subject": subject, "email_sent": False}

    if send:
        try:
            send_email(subject=subject, html_body=html, to=[BUCK_EMAIL])
            result["email_sent"] = True
            result["status"] = "sent"
        except Exception as e:
            result["error"] = str(e)
            result["status"] = "send_failed"
            result["html_preview"] = html[:500]
    else:
        result["status"] = "preview"
        result["html"] = html

    return result

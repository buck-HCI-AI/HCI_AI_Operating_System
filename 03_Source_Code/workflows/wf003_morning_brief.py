"""
WF-003: Morning Brief
Compiled LAST in the morning sequence — after syncs, bid leveling, and inbox review.
Sends a single comprehensive email to buck@hendricksoninc.com covering:
  - Active projects + bid status
  - Companies (from HubSpot + Houzz)
  - Inbox action summary (what was moved, what drafts were created)
  - All unread email details
  - Overdue HubSpot tasks
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "integrations"))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

import psycopg2, psycopg2.extras
from datetime import date
from hubspot import get_overdue_tasks
from microsoft_graph import list_inbox, send_email

DB = dict(host="localhost", port=5432, dbname="hci_os", user="hci_admin", password="hci_postgres_2026")
BUCK_EMAIL = ("Buck Adams", "buck@hendricksoninc.com")


def _pg(sql, params=None):
    conn = psycopg2.connect(**DB, cursor_factory=psycopg2.extras.RealDictCursor)
    cur  = conn.cursor()
    cur.execute(sql, params or [])
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows


# ── Section builders ───────────────────────────────────────────────────────────

def _projects_section() -> str:
    projects = _pg("SELECT id, name, address, status FROM projects WHERE status='active' ORDER BY name")
    if not projects:
        return "<p>No active projects.</p>"

    rows = ""
    for p in projects:
        bids = _pg("""
            SELECT COUNT(DISTINCT bp.id) as pkg_count,
                   SUM(CASE WHEN be.bid_amount IS NOT NULL THEN 1 ELSE 0 END) as bids_in,
                   MIN(be.bid_amount) as low_bid,
                   MAX(be.bid_amount) as high_bid
            FROM bid_packages bp
            LEFT JOIN bid_entries be ON be.bid_package_id = bp.id
            WHERE bp.project_id = %s
        """, (p["id"],))
        b = bids[0] if bids else {}
        low  = '${:,.0f}'.format(b['low_bid'])  if b.get('low_bid')  else '—'
        high = '${:,.0f}'.format(b['high_bid']) if b.get('high_bid') else '—'
        rows += f"""
        <tr>
          <td style="padding:6px 12px;border-bottom:1px solid #eee;font-weight:600">{p['name']}</td>
          <td style="padding:6px 12px;border-bottom:1px solid #eee">{p['address']}</td>
          <td style="padding:6px 12px;border-bottom:1px solid #eee;text-align:center">{b.get('pkg_count',0)}</td>
          <td style="padding:6px 12px;border-bottom:1px solid #eee;text-align:center">{b.get('bids_in',0)}</td>
          <td style="padding:6px 12px;border-bottom:1px solid #eee;text-align:right">{low}</td>
          <td style="padding:6px 12px;border-bottom:1px solid #eee;text-align:right">{high}</td>
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
          <th style="padding:8px 12px;text-align:right">High Bid</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>"""


def _companies_section() -> str:
    """Companies from HubSpot sync — recent activity and open deals."""
    try:
        deals = _pg("""
            SELECT deal_name, stage, amount, last_modified
            FROM hubspot_deals
            WHERE stage NOT IN ('Not Awarded')
            ORDER BY last_modified DESC NULLS LAST
            LIMIT 20
        """)
    except Exception:
        deals = []

    if not deals:
        return "<p style='color:#666'>No company data — HubSpot sync may not have run yet.</p>"

    rows = ""
    for d in deals:
        amt = '${:,.0f}'.format(float(d['amount'])) if d.get('amount') else '—'
        mod = str(d['last_modified'])[:10] if d.get('last_modified') else '—'
        stage_color = {
            "Awarded": "#27ae60", "Leveling": "#e67e22", "Bids Receiving": "#2980b9",
            "Sent Out": "#8e44ad", "Not Started": "#7f8c8d",
        }.get(d['stage'], "#555")
        rows += f"""
        <tr>
          <td style="padding:5px 10px;border-bottom:1px solid #eee">{d['deal_name']}</td>
          <td style="padding:5px 10px;border-bottom:1px solid #eee">
            <span style="background:{stage_color};color:white;padding:2px 8px;border-radius:10px;font-size:11px">{d['stage']}</span>
          </td>
          <td style="padding:5px 10px;border-bottom:1px solid #eee;text-align:right">{amt}</td>
          <td style="padding:5px 10px;border-bottom:1px solid #eee;color:#888;font-size:12px">{mod}</td>
        </tr>"""

    return f"""
    <table style="border-collapse:collapse;width:100%;font-size:13px">
      <thead>
        <tr style="background:#2c3e50;color:white">
          <th style="padding:7px 10px;text-align:left">Company / Deal</th>
          <th style="padding:7px 10px;text-align:left">Stage</th>
          <th style="padding:7px 10px;text-align:right">Amount</th>
          <th style="padding:7px 10px;text-align:left">Last Activity</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>"""


def _inbox_section(inbox_result: dict = None) -> str:
    """Show all unread emails + what was done with each."""
    if not inbox_result or not inbox_result.get("emails"):
        # Fall back to live inbox read
        try:
            msgs = list_inbox(top=30)
            unread = [m for m in msgs if not m.get("isRead")]
        except Exception:
            return "<p style='color:#666'>Could not read inbox.</p>"

        if not unread:
            return "<p style='color:#2ecc71'>✓ Inbox clear — no unread messages.</p>"

        items = ""
        for m in unread:
            sender = (m.get("from") or {}).get("emailAddress", {})
            items += f"""
            <tr>
              <td style="padding:5px 10px;border-bottom:1px solid #eee;font-weight:600">{sender.get('name','?')}</td>
              <td style="padding:5px 10px;border-bottom:1px solid #eee">{m.get('subject','(no subject)')}</td>
              <td style="padding:5px 10px;border-bottom:1px solid #eee;color:#888">—</td>
              <td style="padding:5px 10px;border-bottom:1px solid #eee;color:#888">—</td>
            </tr>"""
        return _inbox_table(items, len(unread))

    # Rich version — from WF-006 inbox review result
    emails = inbox_result.get("emails", [])
    if not emails:
        return "<p style='color:#2ecc71'>✓ Inbox clear — no unread messages.</p>"

    items = ""
    for e in emails:
        moved_badge = (
            f'<span style="background:#27ae60;color:white;padding:1px 6px;border-radius:8px;font-size:11px">→ {e["project"]}</span>'
            if e.get("moved") else
            f'<span style="color:#888">{e["project"]}</span>'
        )
        draft_badge = (
            '<span style="background:#2980b9;color:white;padding:1px 6px;border-radius:8px;font-size:11px">Draft ✓</span>'
            if e.get("draft_created") else ""
        )
        items += f"""
        <tr>
          <td style="padding:5px 10px;border-bottom:1px solid #eee;font-weight:600">{e.get('from_name','?')}</td>
          <td style="padding:5px 10px;border-bottom:1px solid #eee">{e.get('subject','(no subject)')}</td>
          <td style="padding:5px 10px;border-bottom:1px solid #eee">{moved_badge}</td>
          <td style="padding:5px 10px;border-bottom:1px solid #eee">{draft_badge}</td>
        </tr>"""

    summary = (f"<p style='color:#555;font-size:13px;margin:0 0 8px'>"
               f"{inbox_result['processed']} emails processed — "
               f"{sum(1 for e in emails if e.get('moved'))} moved, "
               f"{sum(1 for e in emails if e.get('draft_created'))} drafts created</p>")
    return summary + _inbox_table(items, len(emails))


def _inbox_table(rows_html: str, count: int) -> str:
    return f"""
    <table style="border-collapse:collapse;width:100%;font-size:13px">
      <thead>
        <tr style="background:#2980b9;color:white">
          <th style="padding:7px 10px;text-align:left">From</th>
          <th style="padding:7px 10px;text-align:left">Subject</th>
          <th style="padding:7px 10px;text-align:left">Folder</th>
          <th style="padding:7px 10px;text-align:left">Draft</th>
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
        return "<p style='color:#2ecc71'>✓ No overdue tasks.</p>"
    items = "".join(
        f"<li style='margin:4px 0'>{t.get('properties',{}).get('hs_task_subject','(no subject)')}</li>"
        for t in tasks[:10]
    )
    return f"<ul style='margin:0;padding-left:20px'>{items}</ul>"


def _build_html(today: str, inbox_result: dict = None) -> str:
    return f"""<!DOCTYPE html>
<html>
<body style="font-family:Arial,sans-serif;max-width:760px;margin:0 auto;color:#222">

  <div style="background:#1a3a5c;color:white;padding:20px 24px;border-radius:6px 6px 0 0">
    <h1 style="margin:0;font-size:22px">HCI Morning Brief</h1>
    <p style="margin:4px 0 0;opacity:0.8">{today} — Hendrickson Construction Intelligence</p>
  </div>

  <div style="background:#f8f9fa;padding:20px 24px">

    <h2 style="color:#1a3a5c;border-bottom:2px solid #1a3a5c;padding-bottom:6px;font-size:16px;margin-top:0">
      Active Projects &amp; Bid Status
    </h2>
    {_projects_section()}

    <h2 style="color:#2c3e50;border-bottom:2px solid #2c3e50;padding-bottom:6px;font-size:16px;margin-top:24px">
      Companies — HubSpot Pipeline
    </h2>
    {_companies_section()}

    <h2 style="color:#2980b9;border-bottom:2px solid #2980b9;padding-bottom:6px;font-size:16px;margin-top:24px">
      Inbox ({('processed' if inbox_result and inbox_result.get('emails') else 'unread')})
    </h2>
    {_inbox_section(inbox_result)}

    <h2 style="color:#c0392b;border-bottom:2px solid #c0392b;padding-bottom:6px;font-size:16px;margin-top:24px">
      Overdue HubSpot Tasks
    </h2>
    {_tasks_section()}

  </div>

  <div style="background:#eee;padding:10px 24px;font-size:11px;color:#888;border-radius:0 0 6px 6px">
    HCI AI Operating System — Auto-generated {today} |
    Sequence: Houzz sync → HubSpot sync → Bid leveling → Inbox review → This brief
  </div>

</body>
</html>"""


def run(send: bool = True, inbox_result: dict = None) -> dict:
    """
    Compile and send the morning brief.
    inbox_result: output from WF-006 inbox review (optional — enriches inbox section).
    """
    today   = date.today().strftime("%A, %B %d, %Y")
    subject = f"HCI Morning Brief — {date.today().strftime('%b %d, %Y')}"
    html    = _build_html(today, inbox_result)
    result  = {"subject": subject, "email_sent": False}

    if send:
        try:
            send_email(subject=subject, html_body=html, to=[BUCK_EMAIL])
            result["email_sent"] = True
            result["status"]     = "sent"
        except Exception as e:
            result["error"]        = str(e)
            result["status"]       = "send_failed"
            result["html_preview"] = html[:500]
    else:
        result["status"] = "preview"
        result["html"]   = html

    return result

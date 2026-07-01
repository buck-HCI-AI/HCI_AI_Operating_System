"""
WF-REPORT: Reporting Framework
Report types:
  daily_field_report(log_id)          — called after every WF-SUPER submission
  schedule_variance_alert(variance_id) — called when risk = high or critical
  executive_health_report()           — all-projects table, runs Friday PM
  owner_summary(project_number)       — clean owner-facing report, no internal cost data
  weekly_pm_email()                   — WF-PM weekly_report() wrapped with email delivery
"""
import sys, os, json, datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "integrations"))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

import psycopg2, psycopg2.extras
from microsoft_graph import send_email

BUCK_EMAIL = ("Buck Adams", os.environ.get("BUCK_EMAIL", "buck@hendricksoninc.com"))

DB = dict(
    host=os.environ.get("POSTGRES_HOST", "localhost"),
    port=int(os.environ.get("POSTGRES_PORT", 5432)),
    dbname=os.environ.get("POSTGRES_DB", "hci_os"),
    user=os.environ.get("POSTGRES_USER", "hci_admin"),
    password=os.environ.get("POSTGRES_PASSWORD", ""),
)

HCI_BLUE   = "#1a3a5c"
HCI_DARK   = "#2c3e50"
HCI_GREEN  = "#27ae60"
HCI_YELLOW = "#e67e22"
HCI_RED    = "#c0392b"


def _pg():
    return psycopg2.connect(**DB, cursor_factory=psycopg2.extras.RealDictCursor)


def _q(sql, params=None):
    conn = _pg()
    cur  = conn.cursor()
    cur.execute(sql, params or [])
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def _q1(sql, params=None):
    rows = _q(sql, params)
    return rows[0] if rows else {}


def _email_wrapper(title: str, body_html: str) -> str:
    return f"""<!DOCTYPE html>
<html><body style="font-family:Arial,sans-serif;max-width:760px;margin:0 auto;color:#222">
  <div style="background:{HCI_BLUE};color:white;padding:20px 24px;border-radius:6px 6px 0 0">
    <h1 style="margin:0;font-size:20px">{title}</h1>
    <p style="margin:4px 0 0;opacity:0.8;font-size:13px">
      Hendrickson Construction Intelligence · {datetime.date.today().strftime('%B %d, %Y')}
    </p>
  </div>
  <div style="background:#f8f9fa;padding:20px 24px">{body_html}</div>
  <div style="background:#eee;padding:10px 24px;font-size:11px;color:#888;border-radius:0 0 6px 6px">
    HCI AI Operating System — Auto-generated
  </div>
</body></html>"""


def _section(title: str, color: str, content: str) -> str:
    return f"""
<h2 style="color:{color};border-bottom:2px solid {color};padding-bottom:6px;
           font-size:15px;margin:20px 0 10px">{title}</h2>
{content}"""


def _badge(text: str, color: str) -> str:
    return (f'<span style="background:{color};color:white;padding:2px 8px;'
            f'border-radius:10px;font-size:11px;font-weight:600">{text}</span>')


def _health_color(health: str) -> str:
    return {
        "green":  HCI_GREEN,
        "yellow": HCI_YELLOW,
        "red":    HCI_RED,
    }.get((health or "").lower(), "#888")


# ── 1. Daily Field Report ──────────────────────────────────────────────────────

def daily_field_report(log_id: int, send: bool = False) -> dict:
    """Generate and email a daily field report for a submitted daily log."""
    log = _q1("""
        SELECT dl.*, p.name AS project_name, p.address
        FROM daily_logs dl JOIN projects p ON p.id = dl.project_id
        WHERE dl.id = %s
    """, (log_id,))
    if not log:
        return {"status": "failed", "error": f"Log {log_id} not found"}

    # Schedule analysis for this log (if any)
    variance = _q1(
        "SELECT * FROM schedule_variance WHERE daily_log_id = %s ORDER BY detected_at DESC LIMIT 1",
        (log_id,)
    )

    # Parse JSONB fields
    def _j(v): return v if isinstance(v, list) else (json.loads(v) if isinstance(v, str) else [])
    crew        = _j(log.get("crew_on_site") or [])
    deliveries  = _j(log.get("deliveries")   or [])
    inspections = _j(log.get("inspections")  or [])
    constraints = _j(log.get("constraints")  or [])
    field_risks = _j(log.get("field_risks")  or [])

    def _crew_row(c):
        if isinstance(c, dict):
            return f"{c.get('company','?')} ({c.get('trade','?')}): {c.get('count','?')} workers"
        return str(c)

    crew_html = "".join(f"<li>{_crew_row(c)}</li>" for c in crew) or "<li>Not recorded</li>"
    deliv_html = "".join(f"<li>{d}</li>" for d in deliveries) or "<li>None</li>"
    insp_html  = "".join(f"<li>✅ {i}</li>" for i in inspections) or "<li>None</li>"
    risk_html  = "".join(f"<li>⚠️ {r}</li>" for r in (constraints + field_risks)) or "<li>None</li>"

    sched_section = ""
    if variance:
        rl = variance.get("risk_level", "none")
        color = {"medium": HCI_YELLOW, "high": HCI_RED, "critical": HCI_RED}.get(rl, HCI_GREEN)
        sched_section = _section("Schedule Status", color, f"""
<p style="margin:4px 0"><b>Activity:</b> {variance.get('activity_name','—')}</p>
<p style="margin:4px 0"><b>Status:</b> {variance.get('current_status','—')}</p>
<p style="margin:4px 0"><b>Risk:</b> {_badge(rl.upper(), color)}</p>
{f"<p style='margin:4px 0'><b>Recovery:</b> {variance.get('recovery_action','')}</p>" if variance.get('recovery_action') else ""}
{f"<p style='margin:4px 0;color:{HCI_RED}'><b>Decision needed:</b> {variance.get('decision_needed','')}</p>" if variance.get('decision_needed') else ""}
""")
    else:
        sched_section = _section("Schedule Status", HCI_GREEN,
                                  "<p>No schedule variance detected.</p>")

    weather_str = log.get("weather") or ""
    if log.get("temp_high"):
        weather_str += f" — High: {log['temp_high']}°F / Low: {log.get('temp_low','?')}°F"

    body = f"""
<p style="font-size:14px;color:#555;margin:0 0 16px">
  <b>Date:</b> {log.get('log_date','')} &nbsp;·&nbsp;
  <b>Logged by:</b> {log.get('logged_by','?')} &nbsp;·&nbsp;
  <b>Photos:</b> {log.get('photos_count',0)} &nbsp;·&nbsp;
  <b>Weather:</b> {weather_str or 'Not recorded'}
</p>
{_section('Crew on Site', HCI_BLUE, f'<ul style="margin:0;padding-left:20px">{crew_html}</ul>')}
{_section('Work Performed', HCI_DARK, f'<p style="margin:0">{log.get("work_performed","")}</p>')}
{_section('Deliveries', HCI_DARK, f'<ul style="margin:0;padding-left:20px">{deliv_html}</ul>')}
{_section('Inspections', HCI_DARK, f'<ul style="margin:0;padding-left:20px">{insp_html}</ul>')}
{_section('Constraints & Field Risks', HCI_YELLOW if (constraints or field_risks) else HCI_GREEN,
          f'<ul style="margin:0;padding-left:20px">{risk_html}</ul>')}
{sched_section}
{_section('Subcontractor Progress', HCI_DARK, f'<p style="margin:0">{log.get("subcontractor_progress") or "Not reported"}</p>')}
{_section("Tomorrow's Lookahead", HCI_DARK, f'<p style="margin:0">{log.get("lookahead") or "Not provided"}</p>')}
{_section('Quality Notes', HCI_DARK, f'<p style="margin:0">{log.get("quality_notes") or "No issues"}</p>') if log.get("quality_notes") else ""}
{_section('Safety Notes', HCI_DARK, f'<p style="margin:0">{log.get("safety_notes") or "No issues"}</p>') if log.get("safety_notes") else ""}
"""

    project_name = log.get("project_name", "Project")
    date_str     = str(log.get("log_date", ""))
    subject      = f"Daily Field Report — {project_name} — {date_str}"
    html         = _email_wrapper(f"Daily Field Report — {project_name}", body)

    result = {"log_id": log_id, "project": project_name, "date": date_str}
    if send:
        try:
            send_email(subject=subject, html_body=html, to=[BUCK_EMAIL])
            result["status"]      = "sent"
            result["email_sent"]  = True
        except Exception as e:
            result["status"]      = "send_failed"
            result["error"]       = str(e)
            result["html"]        = html
    else:
        result["status"] = "preview"
        result["html"]   = html
    return result


# ── 2. Schedule Variance Alert ────────────────────────────────────────────────

def schedule_variance_alert(variance_id: int, send: bool = False) -> dict:
    """Email an immediate alert when a high or critical schedule variance is detected."""
    sv = _q1("""
        SELECT sv.*, p.name AS project_name, dl.log_date
        FROM schedule_variance sv
        JOIN projects p ON p.id = sv.project_id
        LEFT JOIN daily_logs dl ON dl.id = sv.daily_log_id
        WHERE sv.id = %s
    """, (variance_id,))
    if not sv:
        return {"status": "failed", "error": f"Variance {variance_id} not found"}

    rl    = sv.get("risk_level", "high")
    color = HCI_RED if rl == "critical" else HCI_YELLOW

    body = f"""
<div style="background:{color};color:white;padding:12px 16px;border-radius:4px;margin-bottom:16px">
  <b>⚠️ {rl.upper()} RISK DETECTED — {sv.get('project_name','')} — {sv.get('log_date','')}</b>
</div>
{_section('Affected Activity', color, f'<p style="margin:0">{sv.get("activity_name","—")}</p>')}
{_section('Baseline', HCI_DARK, f'<p style="margin:0">{sv.get("baseline_status","—")}</p>')}
{_section('Current Status', color, f'<p style="margin:0">{sv.get("current_status","—")}</p>')}
{_section('Cause', HCI_DARK, f'<p style="margin:0">{sv.get("cause","—")}</p>')}
{_section('Responsible Party', HCI_DARK, f'<p style="margin:0">{sv.get("responsible_party","—")}</p>')}
{_section('Recovery Action', HCI_GREEN, f'<p style="margin:0">{sv.get("recovery_action","—")}</p>')}
{f'<div style="background:#fff3cd;border:1px solid {HCI_YELLOW};padding:12px 16px;border-radius:4px;margin-top:16px"><b>Decision needed:</b> {sv.get("decision_needed","")}</div>' if sv.get("decision_needed") else ""}
{f'<p style="margin-top:12px;color:#555"><b>Notification recommended:</b> {sv.get("recommended_notification","")}</p>' if sv.get("recommended_notification") else ""}
"""

    project_name = sv.get("project_name", "Project")
    subject      = f"⚠️ SCHEDULE ALERT [{rl.upper()}] — {project_name} — {sv.get('log_date','')}"
    html         = _email_wrapper(f"Schedule Alert — {project_name}", body)

    result = {"variance_id": variance_id, "project": project_name, "risk_level": rl}
    if send:
        try:
            send_email(subject=subject, html_body=html, to=[BUCK_EMAIL])
            result["status"]     = "sent"
            result["email_sent"] = True
        except Exception as e:
            result["status"] = "send_failed"
            result["error"]  = str(e)
    else:
        result["status"] = "preview"
        result["html"]   = html
    return result


# ── 3. Executive Health Report ────────────────────────────────────────────────

def executive_health_report(send: bool = False) -> dict:
    """All-projects health table. Run every Friday PM."""
    projects = _q("SELECT id, name, address, status FROM projects ORDER BY name")

    rows_html = ""
    for p in projects:
        pid = p["id"]

        # Latest PM review from workflow_events
        pm = _q1("""
            SELECT payload FROM workflow_events
            WHERE workflow_id='WF-PM' AND project_id=%s AND event_type='daily_review_complete'
            ORDER BY created_at DESC LIMIT 1
        """, (pid,))
        payload = pm.get("payload") or {}
        if isinstance(payload, str):
            try: payload = json.loads(payload)
            except: payload = {}

        health   = payload.get("overall_health", "—")
        sched    = payload.get("schedule_status", "—")
        budget   = payload.get("budget_status", "—")
        h_color  = _health_color(health)

        # Bid stats
        bid = _q1("""
            SELECT COUNT(DISTINCT bp.id) as pkgs,
                   SUM(CASE WHEN be.bid_amount IS NOT NULL THEN 1 ELSE 0 END) as bids_in
            FROM bid_packages bp
            LEFT JOIN bid_entries be ON be.bid_package_id = bp.id
            WHERE bp.project_id = %s
        """, (pid,))
        coverage = "—"
        if bid.get("pkgs") and int(bid["pkgs"]) > 0:
            pct = round(100 * int(bid.get("bids_in") or 0) / int(bid["pkgs"]))
            coverage = f"{pct}% ({bid['bids_in']}/{bid['pkgs']})"

        # Open risks
        risk_count = _q1("SELECT COUNT(*) AS c FROM risks WHERE project_id=%s AND status='open'", (pid,))
        risk_n = risk_count.get("c", 0)

        # Top action item
        actions = payload.get("action_items", [])
        top_action = actions[0].get("item", "—")[:60] if actions else "—"

        health_badge = _badge(health.upper() if health != "—" else "NO REVIEW", h_color)

        rows_html += f"""
<tr style="border-bottom:1px solid #ddd">
  <td style="padding:8px 12px;font-weight:600">{p['name']}</td>
  <td style="padding:8px 12px">{health_badge}</td>
  <td style="padding:8px 12px">{sched}</td>
  <td style="padding:8px 12px">{budget}</td>
  <td style="padding:8px 12px">{coverage}</td>
  <td style="padding:8px 12px;color:{HCI_RED if risk_n > 2 else '#555'}">{risk_n}</td>
  <td style="padding:8px 12px;color:#666;font-size:12px">{top_action}</td>
</tr>"""

    table = f"""
<table style="border-collapse:collapse;width:100%;font-size:13px">
  <thead>
    <tr style="background:{HCI_BLUE};color:white">
      <th style="padding:8px 12px;text-align:left">Project</th>
      <th style="padding:8px 12px;text-align:left">Health</th>
      <th style="padding:8px 12px;text-align:left">Schedule</th>
      <th style="padding:8px 12px;text-align:left">Budget</th>
      <th style="padding:8px 12px;text-align:left">Bid Coverage</th>
      <th style="padding:8px 12px;text-align:left">Open Risks</th>
      <th style="padding:8px 12px;text-align:left">Top Action</th>
    </tr>
  </thead>
  <tbody>{rows_html}</tbody>
</table>"""

    today    = datetime.date.today()
    week_str = today.strftime("Week of %B %d, %Y")
    subject  = f"HCI Executive Project Health — {week_str}"
    html     = _email_wrapper(f"Executive Project Health — {week_str}", table)

    result = {"project_count": len(projects), "week": week_str}
    if send:
        try:
            send_email(subject=subject, html_body=html, to=[BUCK_EMAIL])
            result["status"]     = "sent"
            result["email_sent"] = True
        except Exception as e:
            result["status"] = "send_failed"
            result["error"]  = str(e)
    else:
        result["status"] = "preview"
        result["html"]   = html
    return result


# ── 4. Owner Summary ──────────────────────────────────────────────────────────

def owner_summary(project_number: str, send: bool = False) -> dict:
    """Clean owner-facing report — no vendor names, no internal cost data."""
    import re
    m = re.match(r'^(\d+)', str(project_number).upper())
    prefix = m.group(1) if m else project_number
    proj = _q1(
        "SELECT id, name, address, status, scope FROM projects "
        "WHERE name ILIKE %s OR address ILIKE %s LIMIT 1",
        (f"{prefix}%", f"{prefix}%")
    )
    if not proj:
        return {"status": "failed", "error": f"Project {project_number} not found"}
    pid = proj["id"]

    # Bid coverage summary (count only, no vendor names/amounts)
    bid = _q1("""
        SELECT COUNT(DISTINCT bp.id) as pkgs,
               SUM(CASE WHEN be.bid_amount IS NOT NULL THEN 1 ELSE 0 END) as bids_in
        FROM bid_packages bp
        LEFT JOIN bid_entries be ON be.bid_package_id = bp.id
        WHERE bp.project_id = %s
    """, (pid,))
    coverage_pct = 0
    if bid.get("pkgs") and int(bid["pkgs"]) > 0:
        coverage_pct = round(100 * int(bid.get("bids_in") or 0) / int(bid["pkgs"]))

    # Milestones from schedule_variance (owner-safe: activity name + date only)
    variance = _q("""
        SELECT activity_name, detected_at::date AS detected, risk_level, recovery_action
        FROM schedule_variance WHERE project_id = %s ORDER BY detected_at DESC LIMIT 5
    """, (pid,))

    # Upcoming milestones from daily logs lookahead
    lookaheads = _q("""
        SELECT log_date, lookahead FROM daily_logs
        WHERE project_id = %s AND lookahead IS NOT NULL
        ORDER BY log_date DESC LIMIT 3
    """, (pid,))

    # PM review for health (but not exposing financial/vendor details)
    pm = _q1("""
        SELECT payload FROM workflow_events
        WHERE workflow_id='WF-PM' AND project_id=%s AND event_type='daily_review_complete'
        ORDER BY created_at DESC LIMIT 1
    """, (pid,))
    payload = pm.get("payload") or {}
    if isinstance(payload, str):
        try: payload = json.loads(payload)
        except: payload = {}
    sched_status = payload.get("schedule_status", "not yet assessed")

    var_html_parts = []
    for v in variance:
        rec = f" · Recovery: {v['recovery_action']}" if v.get('recovery_action') else ''
        var_html_parts.append(
            f"<li>{v['detected']} — {v['activity_name']} "
            f"({_badge(v['risk_level'], _health_color(v['risk_level']))}){rec}</li>"
        )
    var_html = "".join(var_html_parts) or "<li>No schedule updates to report.</li>"

    look_html = "".join([
        f"<li><b>{l['log_date']}:</b> {l['lookahead']}</li>"
        for l in lookaheads
    ]) or "<li>No upcoming activities recorded yet.</li>"

    body = f"""
<h2 style="color:{HCI_BLUE}">{proj['name']}</h2>
<p style="color:#555">{proj.get('address','')} · Status: {proj.get('status','active').title()}</p>
{f'<p style="color:#555">{proj["scope"]}</p>' if proj.get("scope") else ""}
{_section('Schedule Status', HCI_DARK, f'<p style="margin:0">{sched_status.title()}</p>')}
{_section('Bidding Progress', HCI_DARK, f'<p style="margin:0">{coverage_pct}% of work packages have received bids.</p>')}
{_section('Recent Schedule Activity', HCI_DARK, f'<ul style="margin:0;padding-left:20px">{var_html}</ul>')}
{_section('Upcoming Milestones', HCI_DARK, f'<ul style="margin:0;padding-left:20px">{look_html}</ul>')}
<p style="margin-top:24px;color:#888;font-size:12px">
This summary is prepared by Hendrickson Construction and reflects current field and project management data.
</p>"""

    subject = f"Project Update — {proj['name']} — {datetime.date.today().strftime('%B %d, %Y')}"
    html    = _email_wrapper(f"Project Update — {proj['name']}", body)

    result = {"project": proj["name"], "coverage_pct": coverage_pct}
    if send:
        try:
            send_email(subject=subject, html_body=html, to=[BUCK_EMAIL])
            result["status"]     = "sent"
            result["email_sent"] = True
        except Exception as e:
            result["status"] = "send_failed"
            result["error"]  = str(e)
    else:
        result["status"] = "preview"
        result["html"]   = html
    return result


# ── 5. Weekly PM Email ────────────────────────────────────────────────────────

def weekly_pm_email(send: bool = False) -> dict:
    """Run WF-PM weekly_report() and email the compiled HTML to Buck."""
    sys.path.insert(0, os.path.dirname(__file__))
    from wf_pm import weekly_report, _review_to_html

    report = weekly_report()

    sections = ""
    for proj in report.get("projects", []):
        if proj.get("error"):
            sections += f"<p style='color:{HCI_RED}'>{proj['project']}: {proj['error']}</p>"
        else:
            sections += f"<h2 style='color:{HCI_BLUE}'>{proj['project']}</h2>"
            sections += (f"<p><b>Health:</b> {_badge(proj.get('health','?').upper(), _health_color(proj.get('health','')))}"
                         f" | <b>Schedule:</b> {proj.get('schedule_status','?')}"
                         f" | <b>Budget:</b> {proj.get('budget_status','?')}</p>")
            if proj.get("top_actions"):
                items = "".join(f"<li>[{a.get('priority','').upper()}] {a.get('item','')}</li>"
                                for a in proj["top_actions"])
                sections += f"<ul>{items}</ul>"
            if proj.get("decisions_needed"):
                decs = "".join(f"<li>{d}</li>" for d in proj["decisions_needed"])
                sections += f"<p><b>Decisions needed:</b></p><ul>{decs}</ul>"
            sections += "<hr style='border:none;border-top:1px solid #ddd;margin:16px 0'>"

    week_str = report.get("week_of", datetime.date.today().isoformat())
    subject  = f"HCI Weekly PM Report — Week of {week_str}"
    html     = _email_wrapper(f"Weekly PM Report — {week_str}", sections)

    result = {"week_of": week_str, "project_count": len(report.get("projects", []))}
    if send:
        try:
            send_email(subject=subject, html_body=html, to=[BUCK_EMAIL])
            result["status"]     = "sent"
            result["email_sent"] = True
        except Exception as e:
            result["status"] = "send_failed"
            result["error"]  = str(e)
    else:
        result["status"] = "preview"
        result["html"]   = html
    return result

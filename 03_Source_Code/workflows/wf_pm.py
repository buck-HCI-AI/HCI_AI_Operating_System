"""
WF-PM: Project Manager Daily Review and Weekly Report
Triggers:
  daily_review(project_number) — deep per-project controls review
  weekly_report()              — all active projects rolled up, run Fridays at 4 PM

Pulls from all intelligence services and synthesizes a PM checklist via Claude.
Writes checklist to workflow_events and optionally returns HTML for email.
"""
import sys, os, json, datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "integrations"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "services"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "services", "project_brain"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "services", "bid_intelligence"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "services", "procurement"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "services", "risk_intelligence"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "services", "schedule_intelligence"))

import psycopg2, psycopg2.extras
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

DB = dict(
    host=os.environ.get("POSTGRES_HOST", "localhost"),
    port=int(os.environ.get("POSTGRES_PORT", 5432)),
    dbname=os.environ.get("POSTGRES_DB", "hci_os"),
    user=os.environ.get("POSTGRES_USER", "hci_admin"),
    password=os.environ.get("POSTGRES_PASSWORD", ""),
)

PM_REVIEW_SYSTEM = """You are a construction project manager AI for Hendrickson Construction.
Given data from multiple systems (project status, bids, procurement, risks, schedule),
produce a concise PM checklist in valid JSON. Be specific and actionable.
Flag anything that needs Buck's decision or attention today."""


def _pg():
    return psycopg2.connect(**DB, cursor_factory=psycopg2.extras.RealDictCursor)


def _write_event(project_id, event_type, payload):
    try:
        conn = _pg()
        cur  = conn.cursor()
        cur.execute(
            "INSERT INTO workflow_events (workflow_id, project_id, event_type, payload) "
            "VALUES ('WF-PM', %s, %s, %s::jsonb)",
            (project_id, event_type, json.dumps(payload, default=str))
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def _gather_data(project_number: str) -> dict:
    """Pull data from all intelligence services for one project."""
    data = {"project_number": project_number}

    try:
        # No project_brain_svc module exists (dead import found 2026-07-02 - this
        # silently returned {"error": ...} for every single call, which is why every
        # PM review ever produced showed "project": "N/A" and generic placeholder
        # content regardless of how much real data existed). Pull the same fields
        # directly - name/status/contract value are all this prompt actually needs
        # from "brain" and don't require the full intelligence engine.
        conn = _pg()
        cur = conn.cursor()
        cur.execute(
            "SELECT name, status, scope, contract_value, hubspot_deal_id FROM projects "
            "WHERE name ILIKE %s LIMIT 1",
            (f"%{project_number.split()[0]}%",)
        )
        row = cur.fetchone()
        conn.close()
        if row:
            data["brain"] = {
                "project": {"name": row["name"]},
                "deal_stage": row["status"],
                "deal_amount": row["contract_value"],
            }
        else:
            data["brain"] = {"error": f"no project matched '{project_number}'"}
    except Exception as e:
        data["brain"] = {"error": str(e)}

    try:
        from bid_intelligence_svc import BidIntelligenceService
        data["bids"] = BidIntelligenceService.summary(project_number)
    except Exception as e:
        data["bids"] = {"error": str(e)}

    try:
        from procurement_svc import ProcurementService
        data["procurement"] = ProcurementService.procurement_status(project_number)
    except Exception as e:
        data["procurement"] = {"error": str(e)}

    try:
        from risk_intelligence_svc import RiskIntelligenceService
        data["risks"] = RiskIntelligenceService.project_risks(project_number)
    except Exception as e:
        data["risks"] = {"error": str(e)}

    try:
        from schedule_intelligence_svc import ScheduleIntelligenceService
        data["schedule"] = ScheduleIntelligenceService.project_schedule(project_number)
    except Exception as e:
        data["schedule"] = {"error": str(e)}

    return data


def _build_pm_prompt(data: dict) -> str:
    def _safe(d, *keys, default="N/A"):
        v = d
        for k in keys:
            if isinstance(v, dict):
                v = v.get(k, default)
            else:
                return default
        return v if v is not None else default

    brain    = data.get("brain", {})
    bids     = data.get("bids", {})
    proc     = data.get("procurement", {})
    risks    = data.get("risks", {})
    schedule = data.get("schedule", {})

    project_name = _safe(brain, "project", "name") or data["project_number"]
    deal_stage   = _safe(brain, "deal_stage")
    deal_amount  = _safe(brain, "deal_amount")

    open_pkgs    = _safe(bids, "open_packages")
    bid_exposure = _safe(bids, "total_bid_exposure")

    overdue_items    = _safe(proc, "overdue_items", default=[])
    at_risk_items    = _safe(proc, "at_risk_items", default=[])

    open_risks  = _safe(risks, "open_risks", default=[])
    high_risks  = [r for r in (open_risks if isinstance(open_risks, list) else [])
                   if isinstance(r, dict) and r.get("severity") in ("high", "critical")]

    recent_logs     = schedule.get("recent_progress", [])[:3] if isinstance(schedule, dict) else []
    recent_variance = schedule.get("recent_variance", [])[:3] if isinstance(schedule, dict) else []

    log_summary = "\n".join([
        f"  {l.get('log_date','?')}: {str(l.get('work_performed',''))[:120]}"
        for l in recent_logs
    ]) or "  No recent daily logs."

    variance_summary = "\n".join([
        f"  {v.get('activity_name','?')} — {v.get('risk_level','?')} risk — {v.get('cause','?')}"
        for v in recent_variance
    ]) or "  No recent schedule variance detected."

    return f"""PM DAILY REVIEW — {project_name}
Date: {datetime.date.today().isoformat()}

PROJECT STATUS
  Stage: {deal_stage}
  Contract value: {deal_amount}

BID STATUS
  Open packages: {open_pkgs}
  Total bid exposure: {bid_exposure}

PROCUREMENT
  Overdue items: {len(overdue_items) if isinstance(overdue_items, list) else overdue_items}
  At-risk items: {len(at_risk_items) if isinstance(at_risk_items, list) else at_risk_items}

OPEN RISKS (high/critical only, {len(high_risks)} total)
{chr(10).join(f"  - {r.get('description','')[:100]}" for r in high_risks[:5]) or '  None'}

RECENT FIELD ACTIVITY (last 3 logs)
{log_summary}

SCHEDULE VARIANCE
{variance_summary}

Return JSON only:
{{
  "project": "{project_name}",
  "review_date": "{datetime.date.today().isoformat()}",
  "overall_health": "green|yellow|red",
  "health_reason": "one sentence",
  "action_items": [
    {{"priority": "high|medium|low", "item": "...", "owner": "Buck|Subcontractor|...", "due": "today|this week|..."}}
  ],
  "decisions_needed": ["list of decisions Buck must make"],
  "schedule_status": "on track|at risk|delayed",
  "budget_status": "on track|at risk|over",
  "risks_summary": "one sentence",
  "next_week_priorities": ["list of 3-5 priorities"]
}}"""


def daily_review(project_number: str) -> dict:
    """Run a full PM controls review for one project. Returns structured checklist."""
    data = _gather_data(project_number)
    prompt = _build_pm_prompt(data)

    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "services"))
        from base import BaseIntelligenceService
        import re
        raw = BaseIntelligenceService.ask_claude(prompt, system=PM_REVIEW_SYSTEM, max_tokens=1200)
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        checklist = json.loads(match.group(0)) if match else {"raw": raw}
    except Exception as e:
        checklist = {"error": str(e), "project": project_number}

    # Resolve project_id for event logging
    try:
        conn = _pg()
        cur  = conn.cursor()
        cur.execute("SELECT id FROM projects WHERE name ILIKE %s LIMIT 1",
                    (f"%{project_number.split()[0]}%",))
        row = cur.fetchone()
        conn.close()
        project_id = row["id"] if row else None
    except Exception:
        project_id = None

    _write_event(project_id, "daily_review_complete", checklist)
    return checklist


def weekly_report(send_email: bool = False) -> dict:
    """Compile PM reviews for all active projects into a weekly summary.
    Pass send_email=True to also deliver via wf_report.weekly_pm_email()."""
    conn = _pg()
    cur  = conn.cursor()
    cur.execute("SELECT id, name FROM projects ORDER BY name")
    projects = cur.fetchall()
    conn.close()

    report = {
        "week_of":  datetime.date.today().isoformat(),
        "projects": [],
        "generated_at": datetime.datetime.utcnow().isoformat(),
    }

    for proj in projects:
        project_number = proj["name"]
        try:
            review = daily_review(project_number)
            report["projects"].append({
                "project": project_number,
                "health":  review.get("overall_health", "unknown"),
                "schedule_status": review.get("schedule_status", "unknown"),
                "budget_status":   review.get("budget_status", "unknown"),
                "top_actions": review.get("action_items", [])[:3],
                "decisions_needed": review.get("decisions_needed", []),
            })
        except Exception as e:
            report["projects"].append({"project": project_number, "error": str(e)})

    _write_event(None, "weekly_report_complete", {"project_count": len(projects)})

    if send_email:
        try:
            from wf_report import weekly_pm_email
            report["email_result"] = weekly_pm_email(send=True)
        except Exception as e:
            report["email_error"] = str(e)

    return report


def _review_to_html(checklist: dict) -> str:
    health_color = {"green": "#2e7d32", "yellow": "#f57f17", "red": "#b71c1c"}.get(
        checklist.get("overall_health", "yellow"), "#666"
    )
    actions = "".join([
        f'<li><b>[{a.get("priority","").upper()}]</b> {a.get("item","")} '
        f'<em>({a.get("owner","")}, {a.get("due","")})</em></li>'
        for a in checklist.get("action_items", [])
    ])
    decisions = "".join([f"<li>{d}</li>" for d in checklist.get("decisions_needed", [])])
    priorities = "".join([f"<li>{p}</li>" for p in checklist.get("next_week_priorities", [])])

    return f"""<h2 style='color:{health_color}'>
{checklist.get("project","Project")} — {checklist.get("overall_health","").upper()}
</h2>
<p>{checklist.get("health_reason","")}</p>
<p><b>Schedule:</b> {checklist.get("schedule_status","")} | <b>Budget:</b> {checklist.get("budget_status","")}</p>
<p><b>Risks:</b> {checklist.get("risks_summary","")}</p>
<h3>Action Items</h3><ul>{actions}</ul>
<h3>Decisions Needed</h3><ul>{decisions or "<li>None</li>"}</ul>
<h3>Next Week Priorities</h3><ul>{priorities}</ul>"""

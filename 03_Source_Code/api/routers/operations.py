"""
Job Operations Intelligence Layer — Sprint 3
Milestone 1: Operational Intelligence

Endpoints:
  GET /superintendent/{project_id}/today  — SS morning console
  GET /pm/{project_id}/weekly            — PM weekly console
  GET /leadership/dashboard              — Cross-job leadership view
  GET /reports/weekly/jobs               — All job reports (Friday)
  GET /reports/weekly/company            — Company executive summary
"""
import os, json
from datetime import datetime, timezone, date, timedelta
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

router = APIRouter()

# ── DB helpers ─────────────────────────────────────────────────────────────────

def _pg():
    import psycopg2, psycopg2.extras
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST","localhost"),
        port=int(os.environ.get("POSTGRES_PORT",5432)),
        dbname=os.environ.get("POSTGRES_DB","hci_os"),
        user=os.environ.get("POSTGRES_USER","hci_admin"),
        password=os.environ.get("POSTGRES_PASSWORD",""),
        cursor_factory=psycopg2.extras.RealDictCursor,
    )

def _q(sql, params=None):
    with _pg() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return [dict(r) for r in cur.fetchall()]

def _q1(sql, params=None):
    rows = _q(sql, params)
    return rows[0] if rows else {}

def _project_code(name: str) -> str:
    """Derive short code from project name."""
    codes = {
        "64 Eastwood": "64EW",
        "101 Francis": "101F",
        "1355 Riverside": "1355R",
        "83 Sagebrusch": "83SB",
    }
    return codes.get(name, name[:6].upper().replace(" ",""))

def _get_project(project_id: int) -> dict:
    p = _q1("SELECT * FROM projects WHERE id=%s", (project_id,))
    if not p:
        raise HTTPException(404, f"Project {project_id} not found")
    p["code"] = _project_code(p.get("name",""))
    return p

def _health_score(schedule_variance: int, budget_overrun_pct: float,
                  open_decisions_days: int, blockers: int) -> str:
    if (schedule_variance > 7 or budget_overrun_pct > 15 or
            open_decisions_days > 5 or blockers > 2):
        return "RED"
    if (schedule_variance > 3 or budget_overrun_pct > 5 or
            open_decisions_days > 2 or blockers > 0):
        return "YELLOW"
    return "GREEN"


# ── Superintendent Daily Console ───────────────────────────────────────────────

@router.get("/superintendent/{project_id}/today")
def superintendent_today(project_id: int):
    """SS morning console — what matters today on this job."""
    project = _get_project(project_id)
    today = date.today().isoformat()

    # Schedule items due today
    # houzz_schedule_items uses project_id (FK to houzz_projects.id, not houzz_projects.houzz_project_id)
    schedule_items = _q("""
        SELECT title, assignee, start_date, end_date, status, task_type
        FROM houzz_schedule_items
        WHERE project_id = (
            SELECT houzz_project_id FROM houzz_projects WHERE name ILIKE %s LIMIT 1
        ) AND (end_date::date = %s OR (start_date::date <= %s AND end_date::date >= %s))
        ORDER BY start_date
    """, (f"%{project.get('name','').split()[0]}%", today, today, today)) if _houzz_has_data() else []

    # Open tasks due within 3 days
    # houzz_tasks.assigned_to (not assignee); uses houzz_project_id
    open_tasks = _q("""
        SELECT title, assigned_to AS assignee, due_date, status, NULL::text AS task_type
        FROM houzz_tasks
        WHERE houzz_project_id = (
            SELECT houzz_project_id FROM houzz_projects WHERE name ILIKE %s LIMIT 1
        ) AND status NOT IN ('complete','completed')
          AND (due_date IS NULL OR due_date::date <= %s)
        ORDER BY due_date NULLS LAST, status
        LIMIT 15
    """, (f"%{project.get('name','').split()[0]}%", (date.today() + timedelta(days=3)).isoformat())) if _houzz_has_data() else []

    overdue_tasks = [t for t in open_tasks if t.get("due_date") and str(t["due_date"])[:10] < today]

    # Inspections today
    inspections = [t for t in open_tasks if "inspect" in str(t.get("task_type","")).lower()
                   or "inspect" in str(t.get("title","")).lower()]

    # Blockers
    blockers = [t for t in open_tasks if t.get("status") == "blocked"]

    # Open decisions in executive inbox for this project
    open_decisions = _q("""
        SELECT exec_id, title, deadline, confidence
        FROM executive_inbox
        WHERE status='pending' AND action_payload::text ILIKE %s
        ORDER BY deadline NULLS LAST
        LIMIT 5
    """, (f"%{project_id}%",))

    # Open bids / procurement
    open_bids = _q("""
        SELECT bp.package_name AS scope_name, bp.status, COUNT(be.id) as bid_count
        FROM bid_packages bp
        LEFT JOIN bid_entries be ON be.bid_package_id = bp.id
        WHERE bp.project_id = %s AND bp.status NOT IN ('awarded','cancelled')
        GROUP BY bp.package_name, bp.status
        LIMIT 5
    """, (project_id,))

    health = _health_score(
        schedule_variance=0,
        budget_overrun_pct=0.0,
        open_decisions_days=max((len(open_decisions) * 2), 0),
        blockers=len(blockers),
    )

    daily_log_draft = _build_daily_log_draft(project, open_tasks, schedule_items)

    return {
        "project_id": project_id,
        "project_code": project["code"],
        "project_name": project.get("name"),
        "address": project.get("address"),
        "date": today,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "health": health,
        "superintendent": project.get("super_name") or "Not assigned",
        "schedule": {
            "items_today": len(schedule_items),
            "items": _serialize(schedule_items),
            "data_status": "live" if schedule_items else "pending_houzz_sync",
        },
        "tasks": {
            "open_count": len(open_tasks),
            "overdue_count": len(overdue_tasks),
            "items": _serialize(open_tasks[:10]),
            "data_status": "live" if open_tasks else "pending_houzz_sync",
        },
        "inspections": {
            "required_today": len(inspections),
            "items": _serialize(inspections),
        },
        "vendor_arrivals": {
            "expected_count": 0,
            "items": [],
            "data_status": "pending_houzz_sync",
            "note": "Requires houzz_subcontractors data — run Browser extraction for this project",
        },
        "weather_risk": {
            "level": "UNKNOWN",
            "data_status": "pending_weather_integration",
            "note": "Weather API integration scheduled for Sprint 6",
        },
        "blockers": {
            "count": len(blockers),
            "items": _serialize(blockers),
        },
        "daily_log_draft": daily_log_draft,
        "photos_needed": {
            "count": len(inspections),
            "items": [{"title": i.get("title"), "reason": "inspection documentation"} for i in inspections],
        },
        "safety": {
            "toolbox_topic": _safety_topic_today(),
            "active_holds": [],
            "data_status": "static_rotation",
        },
        "open_decisions": {
            "count": len(open_decisions),
            "items": _serialize(open_decisions),
        },
        "procurement": {
            "open_bids": len(open_bids),
            "items": _serialize(open_bids),
        },
        "escalate_to_pm": {
            "count": len(overdue_tasks) + len(blockers),
            "items": [
                {"type": "overdue_task", "title": t.get("title"), "days_late": _days_late(t)}
                for t in overdue_tasks[:3]
            ] + [
                {"type": "blocker", "title": t.get("title")}
                for t in blockers[:2]
            ],
        },
    }


# ── PM Weekly Console ──────────────────────────────────────────────────────────

@router.get("/pm/{project_id}/weekly")
def pm_weekly(project_id: int):
    """PM weekly console — what to manage on this project this week."""
    project = _get_project(project_id)
    week_of = date.today().isoformat()
    next_week = (date.today() + timedelta(days=7)).isoformat()

    # Open RFIs — houzz_tasks uses assigned_to not assignee; filter by title since no task_type column
    rfis = _q("""
        SELECT title, assigned_to AS assignee, due_date, status,
               (CURRENT_DATE - due_date::date) AS days_overdue
        FROM houzz_tasks
        WHERE houzz_project_id = (
            SELECT houzz_project_id FROM houzz_projects WHERE name ILIKE %s LIMIT 1
        ) AND title ILIKE '%%RFI%%' AND status NOT IN ('complete','completed')
        ORDER BY due_date NULLS LAST
    """, (f"%{project.get('name','').split()[0]}%",)) if _houzz_has_data() else []

    # Open approvals
    open_approvals = _q("""
        SELECT exec_id, title, deadline, confidence, business_impact
        FROM executive_inbox
        WHERE status='pending'
        ORDER BY deadline NULLS LAST
        LIMIT 10
    """)

    # Bid packages
    bid_packages = _q("""
        SELECT bp.package_name AS scope_name, bp.status, bp.awarded_amount,
               COUNT(be.id) as bid_count,
               MIN(be.date_sent) as earliest_bid_date
        FROM bid_packages bp
        LEFT JOIN bid_entries be ON be.bid_package_id = bp.id
        WHERE bp.project_id = %s
        GROUP BY bp.package_name, bp.status, bp.awarded_amount
        ORDER BY bp.status, bp.package_name
    """, (project_id,))

    # Change orders — actual columns: co_number, title, description, status, amount, reason, submitted_date
    change_orders = _q("""
        SELECT co_number, title AS description, amount, status,
               submitted_date, approved_date
        FROM houzz_change_orders
        WHERE houzz_project_id = (
            SELECT houzz_project_id FROM houzz_projects WHERE name ILIKE %s LIMIT 1
        )
        ORDER BY submitted_date DESC
    """, (f"%{project.get('name','').split()[0]}%",)) if _houzz_has_data() else []

    co_approved = sum(float(c.get("amount") or 0) for c in change_orders if c.get("status") == "approved")
    co_pending = sum(float(c.get("amount") or 0) for c in change_orders if c.get("status") == "pending")

    # Budget — actual columns: budgeted_amount, actual_amount, committed_amount
    budget = _q("""
        SELECT category, budgeted_amount, committed_amount, actual_amount
        FROM houzz_budget
        WHERE houzz_project_id = (
            SELECT houzz_project_id FROM houzz_projects WHERE name ILIKE %s LIMIT 1
        )
        ORDER BY category
    """, (f"%{project.get('name','').split()[0]}%",)) if _houzz_has_data() else []

    total_budget = sum(float(b.get("budgeted_amount") or 0) for b in budget)
    total_actual = sum(float(b.get("actual_amount") or 0) for b in budget)
    budget_exposure = max(0, total_actual - total_budget)
    budget_pct = (budget_exposure / total_budget * 100) if total_budget > 0 else 0

    health = _health_score(
        schedule_variance=0,
        budget_overrun_pct=budget_pct,
        open_decisions_days=len(open_approvals),
        blockers=len([r for r in rfis if r.get("days_overdue", 0) > 5]),
    )

    # Priority synthesis
    priorities = _derive_pm_priorities(rfis, open_approvals, bid_packages, change_orders, budget_exposure)

    return {
        "project_id": project_id,
        "project_code": project["code"],
        "project_name": project.get("name"),
        "week_of": week_of,
        "next_week_end": next_week,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "health": health,
        "pm": project.get("pm_name") or "Not assigned",
        "schedule": {
            "variance_days": 0,
            "health": "GREEN",
            "data_status": "pending_houzz_sync",
            "note": "Schedule variance requires Houzz sync",
        },
        "budget": {
            "original": total_budget,
            "actual_cost": total_actual,
            "exposure": budget_exposure,
            "exposure_pct": round(budget_pct, 1),
            "health": "RED" if budget_pct > 15 else "YELLOW" if budget_pct > 5 else "GREEN",
            "by_category": _serialize(budget[:10]),
            "data_status": "live" if budget else "pending_houzz_sync",
        },
        "rfis": {
            "open_count": len(rfis),
            "overdue_count": len([r for r in rfis if r.get("days_overdue", 0) > 5]),
            "items": _serialize(rfis[:10]),
            "data_status": "live" if rfis else "pending_houzz_sync",
        },
        "approvals": {
            "pending_count": len(open_approvals),
            "items": _serialize(open_approvals[:5]),
        },
        "procurement": {
            "packages": len(bid_packages),
            "items": _serialize(bid_packages),
        },
        "change_orders": {
            "approved_total": co_approved,
            "pending_total": co_pending,
            "unsigned_count": len([c for c in change_orders if not c.get("approved_date")]),
            "items": _serialize(change_orders[:10]),
        },
        "vendor_risks": {
            "at_risk_count": 0,
            "items": [],
            "data_status": "pending_houzz_sync",
        },
        "client_comms": {
            "days_since_contact": None,
            "open_items": 0,
            "data_status": "pending_hubspot_sync",
            "note": "Requires HubSpot sync — run POST /connectors/hubspot/sync",
        },
        "outstanding_decisions": {
            "count": len(open_approvals),
            "items": _serialize(open_approvals[:5]),
        },
        "next_week_priorities": priorities,
    }


# ── Leadership Dashboard ───────────────────────────────────────────────────────

@router.get("/leadership/dashboard")
def leadership_dashboard():
    """Cross-job view — all active projects, open decisions, what needs Buck."""
    projects = _q("SELECT * FROM projects WHERE status='active' ORDER BY name")
    for p in projects:
        p["code"] = _project_code(p.get("name",""))

    # Pending owner decisions
    open_decisions = _q("""
        SELECT exec_id, title, deadline, confidence, business_impact,
               created_at,
               (CURRENT_DATE - created_at::date) AS days_waiting
        FROM executive_inbox
        WHERE status='pending'
        ORDER BY deadline NULLS LAST, days_waiting DESC
        LIMIT 10
    """)

    # Bid summary across all projects
    bids_expiring = _q("""
        SELECT bp.package_name AS scope_name, bp.project_id, p.name as project_name,
               bp.awarded_amount, MIN(be.date_sent) as earliest_bid
        FROM bid_packages bp
        JOIN projects p ON p.id = bp.project_id
        LEFT JOIN bid_entries be ON be.bid_package_id = bp.id
        WHERE bp.status NOT IN ('awarded','cancelled')
          AND bp.project_id IN (SELECT id FROM projects WHERE status='active')
        GROUP BY bp.package_name, bp.project_id, p.name, bp.awarded_amount
        HAVING COUNT(be.id) > 0
        ORDER BY earliest_bid NULLS LAST
        LIMIT 10
    """)

    # Per-project health (simplified until Houzz data populated)
    project_cards = []
    for p in projects:
        pd = open_decisions
        proj_decisions = [d for d in pd if str(p.get("id")) in str(d)]
        health = "YELLOW" if proj_decisions else "GREEN"
        project_cards.append({
            "project_id": p["id"],
            "project_code": p["code"],
            "project_name": p.get("name"),
            "address": p.get("address"),
            "health": health,
            "schedule_variance_days": 0,
            "budget_exposure": 0,
            "open_risks": 0,
            "open_decisions": len(proj_decisions),
            "pm": p.get("pm_name") or "TBD",
            "super": p.get("super_name") or "TBD",
            "data_status": "partial — awaiting Houzz sync for full health score",
        })

    # What needs Buck
    what_needs_me = _derive_what_needs_me(open_decisions, bids_expiring)

    # AI productivity
    mining_runs = _q1("SELECT COUNT(*) as cnt FROM mining_log WHERE created_at > NOW() - INTERVAL '24 hours'") if _table_exists("mining_log") else {}
    weekly_mining = _q1("SELECT COUNT(*) as cnt FROM mining_log WHERE created_at > NOW() - INTERVAL '7 days'") if _table_exists("mining_log") else {}

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "company_health": "YELLOW" if any(c["health"] in ("YELLOW","RED") for c in project_cards) else "GREEN",
        "active_projects": len(project_cards),
        "projects_needing_attention": len([c for c in project_cards if c["health"] != "GREEN"]),
        "open_owner_decisions": len(open_decisions),
        "projects": project_cards,
        "what_needs_me": what_needs_me,
        "open_decisions": _serialize(open_decisions[:5]),
        "bids_in_flight": len(bids_expiring),
        "bids": _serialize(bids_expiring[:5]),
        "ai_productivity": {
            "mining_runs_today": mining_runs.get("cnt", 0),
            "mining_runs_week": weekly_mining.get("cnt", 0),
            "connectors_active": 2,
            "workflows_built": 13,
        },
        "schedule_trends": {
            "avg_variance_days": 0,
            "data_status": "pending_houzz_sync",
        },
        "budget_exposure": {
            "total": 0,
            "data_status": "pending_houzz_sync",
        },
    }


# ── Weekly Reports ─────────────────────────────────────────────────────────────

@router.get("/reports/weekly/jobs")
def weekly_job_reports(project_id: int = None):
    """Generate weekly job report for one or all active projects."""
    if project_id:
        pids = [project_id]
    else:
        pids = [r["id"] for r in _q("SELECT id FROM projects WHERE status='active'")]

    reports = []
    for pid in pids:
        try:
            ss = superintendent_today(pid)
            pm = pm_weekly(pid)
            report = {
                "project_id": pid,
                "project_code": pm.get("project_code"),
                "project_name": pm.get("project_name"),
                "week_of": date.today().isoformat(),
                "health": pm.get("health"),
                "executive_summary": _build_job_executive_summary(ss, pm),
                "schedule": pm.get("schedule"),
                "budget": pm.get("budget"),
                "open_tasks": ss.get("tasks"),
                "rfis": pm.get("rfis"),
                "approvals_needed": pm.get("approvals"),
                "change_orders": pm.get("change_orders"),
                "procurement": pm.get("procurement"),
                "vendor_risks": pm.get("vendor_risks"),
                "blockers": ss.get("blockers"),
                "next_week_priorities": pm.get("next_week_priorities"),
                "ai_recommendations": _build_ai_recommendations(ss, pm),
            }
            reports.append(report)
        except Exception as e:
            reports.append({"project_id": pid, "error": str(e)})

    return {"week_of": date.today().isoformat(), "reports": reports, "count": len(reports)}


@router.get("/reports/weekly/company")
def weekly_company_report():
    """Company-level executive summary across all active projects."""
    dashboard = leadership_dashboard()
    job_reports = weekly_job_reports()

    projects_at_risk = [p for p in dashboard["projects"] if p["health"] != "GREEN"]
    total_exposure = sum(
        r.get("budget", {}).get("exposure", 0)
        for r in job_reports.get("reports", [])
        if "budget" in r
    )

    return {
        "week_of": date.today().isoformat(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "company_health": dashboard["company_health"],
        "active_projects": dashboard["active_projects"],
        "projects_at_risk": len(projects_at_risk),
        "projects": dashboard["projects"],
        "open_owner_decisions": dashboard["open_owner_decisions"],
        "top_5_decisions": dashboard["open_decisions"][:5],
        "budget_exposure": {
            "total": total_exposure,
            "by_project": [
                {
                    "project": r.get("project_name"),
                    "exposure": r.get("budget", {}).get("exposure", 0)
                }
                for r in job_reports.get("reports", []) if "budget" in r
            ],
        },
        "approval_bottlenecks": [
            d for d in dashboard["open_decisions"]
            if (d.get("days_waiting") or 0) > 3
        ],
        "ai_productivity": dashboard["ai_productivity"],
        "what_needs_me": dashboard["what_needs_me"],
        "recommendations": _build_company_recommendations(dashboard, job_reports),
        "bids_in_flight": dashboard.get("bids_in_flight", 0),
    }


# ── HTML Views ─────────────────────────────────────────────────────────────────

@router.get("/superintendent/{project_id}", response_class=HTMLResponse, include_in_schema=False)
def superintendent_html(project_id: int):
    data = superintendent_today(project_id)
    return _render_ss_html(data)


@router.get("/pm/{project_id}", response_class=HTMLResponse, include_in_schema=False)
def pm_html(project_id: int):
    data = pm_weekly(project_id)
    return _render_pm_html(data)


@router.get("/leadership", response_class=HTMLResponse, include_in_schema=False)
def leadership_html():
    data = leadership_dashboard()
    return _render_leadership_html(data)


# ── HTML Renderers ─────────────────────────────────────────────────────────────

def _health_color(h: str) -> str:
    return {"GREEN": "#22c55e", "YELLOW": "#eab308", "RED": "#ef4444"}.get(h, "#6b7280")

def _render_ss_html(d: dict) -> str:
    h = d.get("health","GREEN")
    color = _health_color(h)
    tasks = d.get("tasks", {})
    blockers = d.get("blockers", {})
    decisions = d.get("open_decisions", {})
    priorities = d.get("escalate_to_pm", {}).get("items", [])

    task_rows = "".join(
        f'<tr><td>{t.get("title","")}</td><td>{t.get("assignee","—")}</td><td>{str(t.get("due_date",""))[:10]}</td><td style="color:{"#ef4444" if t.get("status")=="blocked" else "#9ca3af"}">{t.get("status","")}</td></tr>'
        for t in d.get("tasks", {}).get("items", [])[:8]
    )
    decision_rows = "".join(
        f'<div style="background:#374151;border-radius:8px;padding:12px;margin:8px 0;"><b style="color:#f9fafb;">{dec.get("title","")}</b><br><small style="color:#9ca3af;">Due: {str(dec.get("deadline",""))[:10]} | Confidence: {dec.get("confidence","")}</small><br><a href="/api/v1/executive/approve/{dec.get("exec_id","")}?token=" style="background:#22c55e;color:white;padding:6px 12px;border-radius:6px;text-decoration:none;font-size:13px;margin-top:8px;display:inline-block;">Approve</a></div>'
        for dec in decisions.get("items", [])
    )
    escalate_rows = "".join(
        f'<div style="background:#451a03;border:1px solid #ef4444;border-radius:8px;padding:10px;margin:6px 0;font-size:13px;color:#fca5a5;">{e.get("type","").replace("_"," ").title()}: {e.get("title","")}</div>'
        for e in priorities[:5]
    )

    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SS Console — {d.get("project_name")} — {d.get("date")}</title>
<style>*{{box-sizing:border-box;margin:0;padding:0;}}body{{background:#111827;font-family:-apple-system,sans-serif;color:#f9fafb;padding:16px;max-width:480px;margin:0 auto;}}
h1{{font-size:22px;font-weight:700;}}h2{{font-size:15px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:.05em;margin:20px 0 8px;}}
.card{{background:#1f2937;border-radius:12px;padding:16px;margin:8px 0;}}
.badge{{display:inline-block;padding:4px 10px;border-radius:20px;font-size:12px;font-weight:700;}}
table{{width:100%;border-collapse:collapse;font-size:13px;}}td{{padding:6px 4px;border-bottom:1px solid #374151;color:#d1d5db;}}
.stat{{text-align:center;}}.stat .n{{font-size:28px;font-weight:700;}}.stat .l{{font-size:11px;color:#6b7280;}}
.grid{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin:8px 0;}}
</style></head><body>
<div class="card">
  <div style="display:flex;justify-content:space-between;align-items:center;">
    <div><h1>{d.get("project_name","")}</h1><p style="color:#9ca3af;font-size:13px;">{d.get("address","")}</p></div>
    <span class="badge" style="background:{color};color:{'#111827' if h=='GREEN' or h=='YELLOW' else '#fff'};">{h}</span>
  </div>
  <p style="color:#6b7280;font-size:12px;margin-top:8px;">{d.get("date","")} · Generated {d.get("generated_at","")[:16]}Z · SS: {d.get("superintendent","")}</p>
  <div class="grid" style="margin-top:12px;">
    <div class="card stat"><div class="n" style="color:{'#ef4444' if tasks.get('overdue_count',0)>0 else '#22c55e'}">{tasks.get("overdue_count",0)}</div><div class="l">Overdue</div></div>
    <div class="card stat"><div class="n">{blockers.get("count",0)}</div><div class="l">Blockers</div></div>
    <div class="card stat"><div class="n">{decisions.get("count",0)}</div><div class="l">Decisions</div></div>
  </div>
</div>
<h2>Open Tasks ({tasks.get("open_count",0)})</h2>
<div class="card" style="padding:0;overflow:hidden;">
  <table>{'<tr style="color:#6b7280;font-size:11px;"><td>Task</td><td>Who</td><td>Due</td><td>Status</td></tr>' if task_rows else ''}{task_rows or '<tr><td colspan="4" style="color:#6b7280;text-align:center;padding:16px;">No open tasks — Houzz sync pending</td></tr>'}</table>
</div>
{"<h2>Safety Today</h2><div class='card'><b style='color:#fbbf24;'>Toolbox Topic:</b> " + str(d.get("safety",{}).get("toolbox_topic","")) + "</div>" if d.get("safety",{}).get("toolbox_topic") else ""}
{"<h2>Decisions Needed (" + str(decisions.get("count",0)) + ")</h2>" + decision_rows if decisions.get("count",0) > 0 else ""}
{"<h2>Escalate to PM</h2>" + escalate_rows if escalate_rows else ""}
<div style="margin-top:24px;display:grid;grid-template-columns:1fr 1fr;gap:8px;">
  <a href="/pm/{d.get('project_id')}" style="display:block;text-align:center;background:#3b82f6;color:white;padding:12px;border-radius:8px;text-decoration:none;font-weight:600;">PM Console</a>
  <a href="/leadership" style="display:block;text-align:center;background:#374151;color:#f9fafb;padding:12px;border-radius:8px;text-decoration:none;font-weight:600;">All Jobs</a>
</div>
<p style="text-align:center;color:#4b5563;font-size:11px;margin-top:16px;">HCI AI · Milestone 1: Operational Intelligence</p>
</body></html>"""

def _render_pm_html(d: dict) -> str:
    h = d.get("health","GREEN")
    color = _health_color(h)
    budget = d.get("budget", {})
    approvals = d.get("approvals", {})
    rfis = d.get("rfis", {})

    approval_cards = "".join(
        f'<div style="background:#374151;border-radius:8px;padding:12px;margin:8px 0;"><b>{a.get("title","")}</b><br><small style="color:#9ca3af;">Due {str(a.get("deadline",""))[:10]}</small><br><a href="/api/v1/executive/approve/{a.get("exec_id","")}?token=" style="background:#22c55e;color:white;padding:6px 14px;border-radius:6px;text-decoration:none;font-size:13px;margin-top:8px;display:inline-block;">Approve</a><a href="/api/v1/executive/defer/{a.get("exec_id","")}?token=" style="background:#374151;border:1px solid #6b7280;color:#d1d5db;padding:6px 14px;border-radius:6px;text-decoration:none;font-size:13px;margin-top:8px;margin-left:6px;display:inline-block;">Defer</a></div>'
        for a in approvals.get("items", [])
    )
    priority_list = "".join(f"<li style='margin:6px 0;color:#d1d5db;'>{p}</li>" for p in d.get("next_week_priorities", []))

    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>PM Console — {d.get("project_name")} — Week of {d.get("week_of")}</title>
<style>*{{box-sizing:border-box;margin:0;padding:0;}}body{{background:#111827;font-family:-apple-system,sans-serif;color:#f9fafb;padding:16px;max-width:480px;margin:0 auto;}}
h1{{font-size:22px;font-weight:700;}}h2{{font-size:15px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:.05em;margin:20px 0 8px;}}
.card{{background:#1f2937;border-radius:12px;padding:16px;margin:8px 0;}}
.badge{{display:inline-block;padding:4px 10px;border-radius:20px;font-size:12px;font-weight:700;}}
.stat{{text-align:center;}}.stat .n{{font-size:28px;font-weight:700;}}.stat .l{{font-size:11px;color:#6b7280;}}
.grid{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin:8px 0;}}
</style></head><body>
<div class="card">
  <div style="display:flex;justify-content:space-between;align-items:center;">
    <div><h1>{d.get("project_name","")}</h1><p style="color:#9ca3af;font-size:13px;">Week of {d.get("week_of","")}</p></div>
    <span class="badge" style="background:{color};color:{'#111827' if h=='GREEN' or h=='YELLOW' else '#fff'};">{h}</span>
  </div>
  <div class="grid" style="margin-top:12px;">
    <div class="card stat"><div class="n" style="color:{'#ef4444' if (budget.get('exposure',0) or 0)>0 else '#22c55e'}">${int((budget.get('exposure',0) or 0)/1000)}k</div><div class="l">Exposure</div></div>
    <div class="card stat"><div class="n">{rfis.get("open_count",0)}</div><div class="l">Open RFIs</div></div>
    <div class="card stat"><div class="n">{approvals.get("pending_count",0)}</div><div class="l">Decisions</div></div>
  </div>
</div>
{"<h2>Approvals Needed (" + str(approvals.get('pending_count',0)) + ")</h2>" + approval_cards if approvals.get("pending_count",0) > 0 else ""}
<h2>Next Week Priorities</h2>
<div class="card"><ul style="list-style:none;padding:0;">{priority_list or '<li style="color:#6b7280;">Priorities auto-generate once Houzz data is synced</li>'}</ul></div>
<div style="margin-top:24px;display:grid;grid-template-columns:1fr 1fr;gap:8px;">
  <a href="/superintendent/{d.get('project_id')}" style="display:block;text-align:center;background:#3b82f6;color:white;padding:12px;border-radius:8px;text-decoration:none;font-weight:600;">SS Console</a>
  <a href="/leadership" style="display:block;text-align:center;background:#374151;color:#f9fafb;padding:12px;border-radius:8px;text-decoration:none;font-weight:600;">All Jobs</a>
</div>
<p style="text-align:center;color:#4b5563;font-size:11px;margin-top:16px;">HCI AI · PM Weekly · {d.get("pm","")}</p>
</body></html>"""

def _render_leadership_html(d: dict) -> str:
    h = d.get("company_health","GREEN")
    color = _health_color(h)
    decisions = d.get("open_decisions", [])

    _health_emoji = {"GREEN": "🟢", "YELLOW": "🟡", "RED": "🔴"}
    project_cards = "".join(
        (lambda p, emoji=_health_emoji.get(p.get("health","GREEN"),"⚪"), bc=_health_color(p.get("health","GREEN")):
        f'<div class="card" style="border-left:4px solid {bc};">'
        f'<div style="display:flex;justify-content:space-between;">'
        f'<div><b style="font-size:16px;">{p.get("project_name","")}</b><br><small style="color:#9ca3af;">{p.get("address","")}</small></div>'
        f'<span style="font-size:20px;">{emoji}</span>'
        f'</div>'
        f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:4px;margin-top:8px;font-size:12px;color:#9ca3af;">'
        f'<div>Variance: {p.get("schedule_variance_days",0)}d</div>'
        f'<div>Exposure: ${int((p.get("budget_exposure",0) or 0)/1000)}k</div>'
        f'<div>Decisions: {p.get("open_decisions",0)}</div>'
        f'</div>'
        f'<div style="margin-top:8px;display:flex;gap:8px;">'
        f'<a href="/superintendent/{p.get("project_id")}" style="font-size:12px;color:#60a5fa;text-decoration:none;">SS Today →</a>'
        f'<a href="/pm/{p.get("project_id")}" style="font-size:12px;color:#60a5fa;text-decoration:none;">PM Week →</a>'
        f'</div></div>')(p)
        for p in d.get("projects", [])
    )

    what_cards = "".join(
        f'<div style="background:#1f2937;border-radius:8px;padding:10px;margin:6px 0;font-size:13px;color:#d1d5db;">{i + 1}. {item}</div>'
        for i, item in enumerate(d.get("what_needs_me", [])[:5])
    )

    decision_cards = "".join(
        f'<div class="card" style="margin:6px 0;"><b>{dec.get("title","")}</b><br><small style="color:#9ca3af;">{dec.get("days_waiting",0)} days waiting · Due {str(dec.get("deadline",""))[:10]}</small><br><a href="/api/v1/executive/approve/{dec.get("exec_id","")}?token=" style="background:#22c55e;color:white;padding:5px 12px;border-radius:6px;text-decoration:none;font-size:12px;margin-top:8px;display:inline-block;">Approve</a></div>'
        for dec in decisions[:5]
    )

    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="60">
<title>HCI AI — Leadership Dashboard</title>
<style>*{{box-sizing:border-box;margin:0;padding:0;}}body{{background:#111827;font-family:-apple-system,sans-serif;color:#f9fafb;padding:16px;max-width:480px;margin:0 auto;}}
h1{{font-size:20px;font-weight:700;}}h2{{font-size:13px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:.05em;margin:20px 0 8px;}}
.card{{background:#1f2937;border-radius:12px;padding:14px;margin:8px 0;}}
.badge{{display:inline-block;padding:4px 10px;border-radius:20px;font-size:12px;font-weight:700;}}
.grid{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;}}
.stat{{text-align:center;background:#1f2937;border-radius:10px;padding:12px;}}.stat .n{{font-size:26px;font-weight:700;}}.stat .l{{font-size:11px;color:#6b7280;}}
</style></head><body>
<div class="card">
  <div style="display:flex;justify-content:space-between;align-items:center;">
    <div><h1>HCI AI Leadership</h1><p style="color:#6b7280;font-size:12px;">{d.get("generated_at","")[:16]}Z · Auto-refresh 60s</p></div>
    <span class="badge" style="background:{color};color:{'#111827' if h in ('GREEN','YELLOW') else '#fff'};">{h}</span>
  </div>
  <div class="grid" style="margin-top:12px;">
    <div class="stat"><div class="n">{d.get('active_projects',0)}</div><div class="l">Active Jobs</div></div>
    <div class="stat"><div class="n" style="color:{'#ef4444' if d.get('open_owner_decisions',0)>0 else '#22c55e'}">{d.get('open_owner_decisions',0)}</div><div class="l">Decisions</div></div>
    <div class="stat"><div class="n">{d.get('ai_productivity',{}).get('mining_runs_today',0)}</div><div class="l">AI Runs Today</div></div>
  </div>
</div>
{"<h2>What Needs Me?</h2>" + what_cards if d.get("what_needs_me") else ""}
<h2>All Jobs ({d.get('active_projects',0)})</h2>
{project_cards}
{"<h2>Open Decisions (" + str(d.get('open_owner_decisions',0)) + ")</h2>" + decision_cards if decisions else ""}
<div style="margin-top:16px;display:grid;grid-template-columns:1fr 1fr;gap:8px;">
  <a href="/executive" style="display:block;text-align:center;background:#3b82f6;color:white;padding:12px;border-radius:8px;text-decoration:none;font-weight:600;">Executive Inbox</a>
  <a href="/api/v1/reports/weekly/company" style="display:block;text-align:center;background:#374151;color:#f9fafb;padding:12px;border-radius:8px;text-decoration:none;font-weight:600;">Weekly Report</a>
</div>
<p style="text-align:center;color:#4b5563;font-size:11px;margin-top:16px;">HCI AI · Milestone 1: Operational Intelligence</p>
</body></html>"""


# ── Utility helpers ────────────────────────────────────────────────────────────

def _houzz_has_data() -> bool:
    try:
        r = _q1("SELECT COUNT(*) as cnt FROM houzz_projects")
        return (r.get("cnt") or 0) > 0
    except Exception:
        return False

def _table_exists(table: str) -> bool:
    try:
        _q1(f"SELECT 1 FROM {table} LIMIT 1")
        return True
    except Exception:
        return False

def _serialize(items):
    out = []
    for item in (items or []):
        row = {}
        for k, v in item.items():
            if hasattr(v, "isoformat"):
                row[k] = v.isoformat()
            elif v is None:
                row[k] = None
            else:
                try:
                    json.dumps(v)
                    row[k] = v
                except Exception:
                    row[k] = str(v)
        out.append(row)
    return out

def _days_late(task: dict) -> int:
    due = task.get("due_date")
    if not due:
        return 0
    try:
        if hasattr(due, "date"):
            due = due.date()
        elif isinstance(due, str):
            due = date.fromisoformat(str(due)[:10])
        return max(0, (date.today() - due).days)
    except Exception:
        return 0

_SAFETY_TOPICS = [
    "Fall Protection — inspect all harnesses before use",
    "Electrical Safety — lock-out/tag-out procedures",
    "Struck-By Hazards — hard hat zones, overhead work",
    "Trenching & Excavation — soil classification, shoring",
    "Scaffold Safety — capacity, access, fall protection",
    "Hand & Power Tool Safety — guards and PPE",
    "Heat Illness Prevention — hydration, shade, rest",
    "Housekeeping — clear walkways, remove trip hazards",
    "Chemical Safety (HAZCOM) — SDS locations, PPE",
    "Fire Prevention — extinguisher locations, hot work permits",
]

def _safety_topic_today() -> str:
    return _SAFETY_TOPICS[date.today().weekday() % len(_SAFETY_TOPICS)]

def _build_daily_log_draft(project: dict, tasks: list, schedule: list) -> dict:
    completed_items = [t for t in tasks if t.get("status") in ("complete","completed")]
    planned_items = [s.get("title","") for s in schedule if s.get("title")]
    return {
        "work_completed": ", ".join(t.get("title","") for t in completed_items[:5]) or "Enter work completed today",
        "planned_work": ", ".join(planned_items[:5]) or "Enter planned work for today",
        "issues": "",
        "note": "Pre-filled from Houzz task and schedule data. Review and complete before submitting.",
    }

def _derive_pm_priorities(rfis, approvals, bids, change_orders, budget_exposure) -> list:
    priorities = []
    if budget_exposure > 0:
        priorities.append(f"Resolve budget exposure of ${int(budget_exposure):,}")
    overdue_rfis = [r for r in rfis if (r.get("days_overdue") or 0) > 5]
    if overdue_rfis:
        priorities.append(f"Resolve {len(overdue_rfis)} overdue RFI(s) — oldest: {overdue_rfis[0].get('title','')}")
    expiring_bids = [b for b in bids if b.get("status") not in ("awarded","cancelled")]
    if expiring_bids:
        priorities.append(f"Award decision needed on {len(expiring_bids)} open bid package(s)")
    unsigned_cos = [c for c in change_orders if not c.get("approved_date")]
    if unsigned_cos:
        priorities.append(f"Sign {len(unsigned_cos)} outstanding change order(s)")
    if approvals:
        priorities.append(f"Review {len(approvals)} pending approval(s) in executive inbox")
    if not priorities:
        priorities.append("All tracked items on track — verify Houzz data is current")
    return priorities[:5]

def _derive_what_needs_me(decisions: list, bids: list) -> list:
    items = []
    for d in decisions[:3]:
        waiting = d.get("days_waiting") or 0
        items.append(f"{d.get('title','')} ({waiting}d waiting)")
    for b in bids[:2]:
        items.append(f"Bid decision: {b.get('scope_name','')} on {b.get('project_name','')} — {b.get('bid_count',0)} bid(s)")
    if not items:
        items.append("No immediate owner actions needed")
    return items

def _build_job_executive_summary(ss: dict, pm: dict) -> list:
    bullets = []
    health = pm.get("health","GREEN")
    if health == "GREEN":
        bullets.append("Project on track — no critical issues this week")
    elif health == "YELLOW":
        bullets.append("Watch items: review schedule and open decisions")
    else:
        bullets.append("Immediate attention required — multiple risk factors")
    if pm.get("budget", {}).get("exposure", 0) > 0:
        bullets.append(f"Budget exposure: ${int(pm['budget']['exposure']):,}")
    if ss.get("blockers", {}).get("count", 0) > 0:
        bullets.append(f"{ss['blockers']['count']} active blocker(s) — escalate to PM")
    return bullets[:3] or ["Insufficient data — run Houzz sync to populate job intelligence"]

def _build_ai_recommendations(ss: dict, pm: dict) -> list:
    recs = []
    if not _houzz_has_data():
        recs.append("Run Browser Claude extraction for this project to unlock full intelligence")
    if pm.get("client_comms", {}).get("days_since_contact") and pm["client_comms"]["days_since_contact"] > 7:
        recs.append("Client check-in overdue — schedule a call or send update")
    if pm.get("rfis", {}).get("overdue_count", 0) > 0:
        recs.append("Escalate overdue RFIs to architect/engineer — schedule delays risk")
    return recs or ["System monitoring — all tracked items within normal parameters"]

def _build_company_recommendations(dashboard: dict, job_reports: dict) -> list:
    recs = []
    if dashboard.get("open_owner_decisions", 0) > 3:
        recs.append(f"Decision queue has {dashboard['open_owner_decisions']} items — dedicate 30 min to batch review")
    if not _houzz_has_data():
        recs.append("Run Houzz Browser extraction for all 3 pilot projects to activate full intelligence")
    recs.append("Import 13 n8n workflow JSONs from 03_Source_Code/workflows/n8n/ to activate automation suite")
    return recs[:3]

"""
Cross-Project Intelligence Service — Phase 2, Priority 2
Continuously compares all active projects and generates company-wide insights.

Mounted at /api/v1/services/cross-project
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, timezone
from fastapi import APIRouter
from base import BaseIntelligenceService

router = APIRouter()


class CrossProjectIntelligence(BaseIntelligenceService):
    SERVICE_NAME = "cross_project_intelligence"

    def company_snapshot(self) -> dict:
        projects = self.pg_query("SELECT * FROM projects WHERE status='active' ORDER BY name")
        if not projects:
            return {"error": "No active projects found"}

        # Per-project intelligence from existing data. Each call is independent
        # (self.pg_query/pg_one are @staticmethods that open a fresh connection per
        # call, no shared mutable state on self) - found 2026-07-06 this sequential
        # per-project loop was a real contributor to company_snapshot's 1.2s+ latency.
        # Parallelizing is a pure orchestration change, not a logic change.
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(projects), 8)) as ex:
            project_cards = list(ex.map(lambda p: self._project_card(p["id"], p), projects))

        # Sort: RED first, then YELLOW, then GREEN
        sev_order = {"RED": 0, "YELLOW": 1, "GREEN": 2}
        project_cards.sort(key=lambda c: sev_order.get(c["health"], 3))

        company_health = "GREEN"
        if any(c["health"] == "RED" for c in project_cards):
            company_health = "RED"
        elif any(c["health"] == "YELLOW" for c in project_cards):
            company_health = "YELLOW"

        # Cross-project insights
        alerts = self._cross_project_alerts(project_cards)
        vendor_perf = self._vendor_performance_cross_project()
        procurement_summary = self._procurement_summary()
        schedule_trends = self._schedule_trends(project_cards)
        budget_exposure = self._budget_exposure(project_cards)

        # Persist snapshot
        self._persist_company_snapshot(company_health, project_cards, alerts)

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "company_health": company_health,
            "active_projects": len(project_cards),
            "projects_at_risk": len([c for c in project_cards if c["health"] != "GREEN"]),
            "projects": project_cards,
            "cross_project_alerts": alerts,
            "schedule_trends": schedule_trends,
            "budget_exposure": budget_exposure,
            "vendor_performance": vendor_perf,
            "procurement_summary": procurement_summary,
        }

    def _project_card(self, project_id: int, project: dict) -> dict:
        from intelligence import ProjectIntelligenceEngine
        codes = {1: "64EW", 2: "101F", 3: "1355R", 4: "83SB"}
        engine = ProjectIntelligenceEngine(project_id)
        try:
            h = engine.health()
            risks = engine.detect_risks()
            health = h.get("health", "GREEN")
            top_risk = risks[0]["title"] if risks else None
        except Exception:
            health = "UNKNOWN"
            top_risk = None
            h = {}

        # Reconcile against the real `risks` table - same fix already applied to
        # executive.py's mission-control on 2026-07-01 (that fix's own comment
        # documents the exact bug: ProjectIntelligenceEngine's algorithmic
        # detect_risks() can go stale relative to the persisted risks table, e.g.
        # 1355R showing GREEN/0 here while risks table has real open critical rows).
        # That reconciliation never propagated to this sibling endpoint - found
        # 2026-07-06 while verifying a performance change, confirmed reproducible
        # and unrelated to that change. Take the worse-of both signals, same logic
        # as executive.py's _reconcile_health.
        try:
            rr = self.pg_one("""
                SELECT COUNT(*) as open_risks,
                       COUNT(*) FILTER (WHERE severity='critical') as critical,
                       COUNT(*) FILTER (WHERE severity IN ('critical','high')) as high_or_critical
                FROM risks WHERE project_id=%s AND status='open'
            """, (project_id,))
            open_risks = int((rr or {}).get("open_risks") or 0)
            critical = int((rr or {}).get("critical") or 0)
            high_or_critical = int((rr or {}).get("high_or_critical") or 0)
            if high_or_critical > 0:
                health = "RED"
            elif open_risks > 0 and health == "GREEN":
                health = "YELLOW"
            # Keep the displayed counts consistent with the reconciled color - a card
            # reading "RED, 0 critical risks" would be as misleading as the bug just fixed.
            h["critical_risks"] = max(h.get("critical_risks", 0), critical)
            h["high_risks"] = max(h.get("high_risks", 0), high_or_critical - critical)
        except Exception:
            pass

        # Quick procurement stats
        proc = self.pg_one("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN status='awarded' THEN 1 ELSE 0 END) as awarded,
                   SUM(CASE WHEN status NOT IN ('awarded','cancelled') THEN 1 ELSE 0 END) as open
            FROM bid_packages WHERE project_id=%s
        """, (project_id,))

        # Pending approval queue items
        pending_aq = self.pg_one("""
            SELECT COUNT(*) as n FROM approval_queue
            WHERE project_id=%s AND status='pending'
        """, (project_id,))

        return {
            "project_id": project_id,
            "project_code": codes.get(project_id, f"P{project_id}"),
            "project_name": project.get("name"),
            "address": project.get("address"),
            "health": health,
            "health_factors": h.get("factors", []),
            "critical_risks": h.get("critical_risks", 0),
            "high_risks": h.get("high_risks", 0),
            "top_risk": top_risk,
            "pm": project.get("pm_name") or "TBD",
            "super": project.get("super_name") or "TBD",
            "bid_packages": {
                "total": int((proc or {}).get("total") or 0),
                "awarded": int((proc or {}).get("awarded") or 0),
                "open": int((proc or {}).get("open") or 0),
            },
            "pending_approvals": int((pending_aq or {}).get("n") or 0),
        }

    def _cross_project_alerts(self, cards: list) -> list:
        alerts = []

        # Projects with no SS assigned
        no_super = [c for c in cards if c.get("super") in (None, "TBD", "Not assigned")]
        if no_super:
            alerts.append({
                "type": "staffing",
                "severity": "medium",
                "message": f"{len(no_super)} project(s) have no superintendent assigned",
                "projects": [c["project_name"] for c in no_super],
            })

        # Projects with high pending approvals
        high_aq = [c for c in cards if c.get("pending_approvals", 0) > 50]
        if high_aq:
            alerts.append({
                "type": "approval_bottleneck",
                "severity": "high",
                "message": f"{len(high_aq)} project(s) have >50 items pending in approval queue",
                "projects": [f"{c['project_name']} ({c['pending_approvals']} pending)" for c in high_aq],
            })

        # Cross-vendor risks (vendors appearing on multiple projects with issues)
        vendor_overlap = self.pg_query("""
            SELECT v.company_name, COUNT(DISTINCT be.project_id) AS project_count,
                   array_agg(DISTINCT p.name) AS project_names
            FROM vendors v
            JOIN bid_entries be ON be.vendor_id = v.id
            JOIN projects p ON p.id = be.project_id
            WHERE p.status='active'
            GROUP BY v.company_name
            HAVING COUNT(DISTINCT be.project_id) > 1
            ORDER BY project_count DESC
            LIMIT 5
        """)
        if vendor_overlap:
            alerts.append({
                "type": "vendor_overlap",
                "severity": "info",
                "message": f"{len(vendor_overlap)} vendor(s) bidding on multiple active projects",
                "detail": [{"vendor": v["company_name"], "projects": v.get("project_names", [])} for v in vendor_overlap[:3]],
            })

        return alerts

    def _vendor_performance_cross_project(self) -> dict:
        # Vendors with most bids won vs submitted across all active projects
        top_vendors = self.pg_query("""
            SELECT v.company_name,
                   COUNT(be.id) as bids_submitted,
                   SUM(CASE WHEN be.status='awarded' THEN 1 ELSE 0 END) as bids_won,
                   AVG(be.bid_amount) as avg_bid
            FROM vendors v
            JOIN bid_entries be ON be.vendor_id = v.id
            JOIN projects p ON p.id = be.project_id
            WHERE p.status='active'
            GROUP BY v.company_name
            HAVING COUNT(be.id) >= 2
            ORDER BY bids_submitted DESC
            LIMIT 10
        """)

        return {
            "top_vendors_by_activity": [dict(v) for v in top_vendors[:5]],
            "total_vendors_active": len(top_vendors),
        }

    def _procurement_summary(self) -> dict:
        summary = self.pg_query("""
            SELECT p.name AS project_name,
                   COUNT(bp.id) as total_packages,
                   SUM(CASE WHEN bp.status='awarded' THEN 1 ELSE 0 END) as awarded,
                   SUM(CASE WHEN bp.status NOT IN ('awarded','cancelled') THEN 1 ELSE 0 END) as open,
                   SUM(bp.awarded_amount) as total_awarded
            FROM projects p
            LEFT JOIN bid_packages bp ON bp.project_id = p.id
            WHERE p.status='active'
            GROUP BY p.id, p.name
            ORDER BY p.name
        """)

        total_open = sum(int(s.get("open") or 0) for s in summary)
        total_awarded = sum(float(s.get("total_awarded") or 0) for s in summary)

        return {
            "by_project": [dict(s) for s in summary],
            "total_open_packages": total_open,
            "total_awarded_value": total_awarded,
        }

    def _schedule_trends(self, cards: list) -> dict:
        all_variance = self.pg_query("""
            SELECT sv.project_id, p.name, sv.variance_days, sv.risk_level
            FROM schedule_variance sv
            JOIN projects p ON p.id = sv.project_id
            WHERE p.status='active'
        """)

        avg_variance = 0
        if all_variance:
            avg_variance = sum(int(v.get("variance_days") or 0) for v in all_variance) / len(all_variance)

        return {
            "avg_variance_days": round(avg_variance, 1),
            "total_variance_items": len(all_variance),
            "projects_with_variance": len(set(v["project_id"] for v in all_variance)),
            "high_risk_items": [
                {"project": v["name"], "variance_days": v["variance_days"]}
                for v in all_variance if v.get("risk_level") in ("high","critical")
            ][:5],
            "data_status": "live" if all_variance else "pending_houzz_sync",
        }

    def _budget_exposure(self, cards: list) -> dict:
        cost_data = self.pg_query("""
            SELECT p.name, SUM(hcr.final_cost - hcr.awarded_amount) AS exposure
            FROM historical_cost_records hcr
            JOIN projects p ON p.id = hcr.project_id
            WHERE p.status='active' AND hcr.final_cost > hcr.awarded_amount
            GROUP BY p.name
        """)

        total = sum(float(c.get("exposure") or 0) for c in cost_data)

        return {
            "total_exposure": total,
            "by_project": [{"project": c["name"], "exposure": float(c.get("exposure") or 0)} for c in cost_data],
            "data_status": "live" if cost_data else "pending_houzz_sync",
        }

    def _persist_company_snapshot(self, health: str, cards: list, alerts: list):
        try:
            import psycopg2, json
            from dotenv import load_dotenv
            load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))
            conn = psycopg2.connect(
                host=os.environ.get("POSTGRES_HOST","localhost"),
                port=int(os.environ.get("POSTGRES_PORT",5432)),
                dbname=os.environ.get("POSTGRES_DB","hci_os"),
                user=os.environ.get("POSTGRES_USER","hci_admin"),
                password=os.environ.get("POSTGRES_PASSWORD",""),
            )
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO company_intelligence_snapshots
                    (snapshot_date, company_health, active_projects, open_decisions,
                     top_risks, cross_project_alerts)
                VALUES (CURRENT_DATE, %s, %s, %s, %s, %s)
                ON CONFLICT (snapshot_date) DO UPDATE SET
                    company_health = EXCLUDED.company_health,
                    active_projects = EXCLUDED.active_projects,
                    cross_project_alerts = EXCLUDED.cross_project_alerts
            """, (
                health, len(cards),
                sum(c.get("pending_approvals", 0) for c in cards),
                json.dumps([c["top_risk"] for c in cards if c.get("top_risk")][:5]),
                json.dumps(alerts),
            ))
            conn.close()
        except Exception:
            pass

    @staticmethod
    def info():
        return {
            "service": "cross_project_intelligence",
            "status": "active",
            "phase": 2,
            "endpoints": [
                "GET /company-snapshot — full cross-project intelligence",
                "GET /alerts — active cross-project alerts",
                "GET /vendor-performance — vendor activity across projects",
                "GET /procurement-summary — bid status by project",
                "GET /schedule-trends — variance trends across portfolio",
            ],
        }


# ── Routes ─────────────────────────────────────────────────────────────────────

@router.get("")
def service_info():
    return CrossProjectIntelligence.info()


@router.get("/company-snapshot")
def company_snapshot():
    """Full cross-project intelligence — health, alerts, vendor perf, procurement."""
    svc = CrossProjectIntelligence()
    return svc.company_snapshot()


@router.get("/alerts")
def cross_project_alerts():
    """Active alerts that span multiple projects."""
    svc = CrossProjectIntelligence()
    data = svc.company_snapshot()
    return {
        "generated_at": data.get("generated_at"),
        "company_health": data.get("company_health"),
        "alerts": data.get("cross_project_alerts", []),
    }


@router.get("/vendor-performance")
def vendor_performance():
    """Vendor bid activity and win rates across all active projects."""
    svc = CrossProjectIntelligence()
    return svc._vendor_performance_cross_project()


@router.get("/procurement-summary")
def procurement_summary():
    """Bid package status aggregated across all active projects."""
    svc = CrossProjectIntelligence()
    return svc._procurement_summary()


@router.get("/schedule-trends")
def schedule_trends():
    """Schedule variance trends across the project portfolio."""
    svc = CrossProjectIntelligence()
    return svc._schedule_trends([])


@router.get("/health-matrix")
def health_matrix():
    """Lightweight RED/YELLOW/GREEN matrix for all active projects."""
    svc = CrossProjectIntelligence()
    projects = svc.pg_query("SELECT id, name, pm_name, super_name FROM projects WHERE status='active' ORDER BY name")
    codes = {1: "64EW", 2: "101F", 3: "1355R", 4: "83SB"}
    cards = []
    for p in projects:
        from intelligence import ProjectIntelligenceEngine
        engine = ProjectIntelligenceEngine(p["id"])
        h = engine.health()
        cards.append({
            "project_id": p["id"],
            "project_code": codes.get(p["id"], f"P{p['id']}"),
            "project_name": p["name"],
            "health": h.get("health"),
            "critical_risks": h.get("critical_risks", 0),
            "high_risks": h.get("high_risks", 0),
        })
    company_health = "GREEN"
    if any(c["health"] == "RED" for c in cards):
        company_health = "RED"
    elif any(c["health"] == "YELLOW" for c in cards):
        company_health = "YELLOW"
    return {"company_health": company_health, "projects": cards}

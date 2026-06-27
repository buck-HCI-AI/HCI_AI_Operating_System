"""
Project Brain Intelligence Engine — Phase 2
Continuous health scoring, risk detection, AI synthesis, and action recommendations.
"""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, timezone, date, timedelta
from typing import Optional
from base import BaseIntelligenceService

AI_MODEL = "claude-haiku-4-5-20251001"

PROJECT_CODES = {1: "64EW", 2: "101F", 3: "1355R", 4: "83SB"}

INTELLIGENCE_SYSTEM_PROMPT = """You are the Project Brain AI for Hendrickson Construction, a high-end
residential remodeler in Aspen, Colorado. You synthesize all project data into clear, actionable
intelligence for the owner and project managers.

Be specific and concise. Reference actual numbers and dates from the data. Use contractor/construction
language. Format recommendations as numbered action items. 3 sentences maximum for summaries."""


class ProjectIntelligenceEngine(BaseIntelligenceService):
    SERVICE_NAME = "project_brain"

    def __init__(self, project_id: int):
        self.project_id = project_id
        self._project = None

    def _project_row(self) -> Optional[dict]:
        if not self._project:
            self._project = self.pg_one(
                "SELECT * FROM projects WHERE id=%s", (self.project_id,))
        return self._project

    # ── Public API ──────────────────────────────────────────────────────────────

    def intelligence(self, include_ai_summary: bool = True) -> dict:
        """Full Phase 2 intelligence snapshot."""
        project = self._project_row()
        if not project:
            return {"error": f"Project {self.project_id} not found"}

        risks = self.detect_risks()
        health, factors = self._compute_health(risks)
        decisions = self._open_decisions()
        open_questions = self._open_questions()
        missing = self._missing_information()
        timeline = self._timeline()
        procurement = self._procurement_status()
        data_completeness = self._data_completeness()

        ai_summary = ""
        next_actions = []
        if include_ai_summary:
            ai_summary = self._generate_summary(project, health, risks, decisions, procurement)
            next_actions = self._recommend_actions(risks, decisions, procurement)

        # Persist snapshot
        self._persist_snapshot(health, factors, risks, decisions, procurement)

        return {
            "project_id": self.project_id,
            "project_code": PROJECT_CODES.get(self.project_id, f"P{self.project_id}"),
            "project_name": project.get("name"),
            "address": project.get("address"),
            "pm": project.get("pm_name"),
            "super": project.get("super_name"),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "health": health,
            "health_factors": factors,
            "data_completeness_pct": data_completeness,
            "timeline": timeline,
            "risks": risks,
            "risk_summary": {
                "critical": len([r for r in risks if r["severity"] == "critical"]),
                "high": len([r for r in risks if r["severity"] == "high"]),
                "medium": len([r for r in risks if r["severity"] == "medium"]),
                "low": len([r for r in risks if r["severity"] == "low"]),
            },
            "decisions": decisions,
            "open_questions": open_questions,
            "missing_information": missing,
            "procurement": procurement,
            "ai_summary": ai_summary,
            "recommended_next_actions": next_actions,
            "data_sources": {
                "bid_packages": procurement.get("total_packages", 0),
                "schedule_variance_items": timeline.get("variance_items", 0),
                "open_decisions": len(decisions),
                "houzz_synced": self._houzz_has_data(),
                "hubspot_linked": bool(project.get("hubspot_deal_id")),
            },
        }

    def detect_risks(self) -> list:
        """Auto-detect risks from all available data sources."""
        risks = []
        risks.extend(self._procurement_risks())
        risks.extend(self._schedule_risks())
        risks.extend(self._decision_risks())
        risks.extend(self._budget_risks())
        risks.extend(self._data_gap_risks())
        # Sort by severity
        sev_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        risks.sort(key=lambda r: sev_order.get(r["severity"], 4))
        return risks

    def health(self) -> dict:
        """Lightweight health check — no AI, fast."""
        risks = self.detect_risks()
        h, factors = self._compute_health(risks)
        return {
            "project_id": self.project_id,
            "health": h,
            "factors": factors,
            "risk_count": len(risks),
            "critical_risks": len([r for r in risks if r["severity"] == "critical"]),
            "high_risks": len([r for r in risks if r["severity"] == "high"]),
            "as_of": datetime.now(timezone.utc).isoformat(),
        }

    def summary(self) -> dict:
        """AI-generated narrative summary of current project state."""
        project = self._project_row()
        if not project:
            return {"error": f"Project {self.project_id} not found"}
        risks = self.detect_risks()
        health, _ = self._compute_health(risks)
        decisions = self._open_decisions()
        procurement = self._procurement_status()
        summary_text = self._generate_summary(project, health, risks, decisions, procurement)
        actions = self._recommend_actions(risks, decisions, procurement)
        return {
            "project_id": self.project_id,
            "project_name": project.get("name"),
            "health": health,
            "ai_summary": summary_text,
            "recommended_next_actions": actions,
            "as_of": datetime.now(timezone.utc).isoformat(),
        }

    # ── Risk Detection ──────────────────────────────────────────────────────────

    def _procurement_risks(self) -> list:
        risks = []
        # Open bid packages with no bids received
        no_bids = self.pg_query("""
            SELECT bp.package_name, bp.csi_division, bp.status,
                   COUNT(be.id) AS bid_count,
                   EXTRACT(EPOCH FROM (NOW() - bp.created_at))/86400 AS age_days
            FROM bid_packages bp
            LEFT JOIN bid_entries be ON be.bid_package_id = bp.id
            WHERE bp.project_id = %s AND bp.status NOT IN ('awarded','cancelled')
            GROUP BY bp.id, bp.package_name, bp.csi_division, bp.status, bp.created_at
        """, (self.project_id,))

        no_response = [b for b in no_bids if int(b.get("bid_count") or 0) == 0]
        old_no_response = [b for b in no_response if float(b.get("age_days") or 0) > 14]

        if old_no_response:
            risks.append({
                "risk_code": "PROC-001",
                "risk_type": "procurement",
                "severity": "high" if len(old_no_response) > 5 else "medium",
                "title": f"{len(old_no_response)} bid packages open >14 days with no bids",
                "description": f"Packages: {', '.join(b['package_name'] for b in old_no_response[:5])}",
                "evidence": {"packages": [b["package_name"] for b in old_no_response[:5]], "age_days": [float(b.get("age_days") or 0) for b in old_no_response[:5]]},
                "confidence": 0.95,
                "mitigation": "Follow up with vendors; consider broadening bid list",
            })

        if no_response:
            risks.append({
                "risk_code": "PROC-002",
                "risk_type": "procurement",
                "severity": "medium",
                "title": f"{len(no_response)} open bid packages awaiting vendor response",
                "description": f"Total open packages: {len(no_bids)}, awaiting first bid: {len(no_response)}",
                "evidence": {"total_open": len(no_bids), "no_bids_yet": len(no_response)},
                "confidence": 0.9,
                "mitigation": "Review bid list, confirm vendors received invite",
            })

        # Pending approval queue items (bids awaiting Buck's approval)
        pending_bids = self.pg_one("""
            SELECT COUNT(*) as n,
                   MAX(EXTRACT(EPOCH FROM (NOW() - created_at))/86400) as max_age_days
            FROM approval_queue
            WHERE project_id=%s AND status='pending' AND action_type='db_write'
        """, (self.project_id,))
        if pending_bids and int(pending_bids.get("n") or 0) > 0:
            n = int(pending_bids["n"])
            age = float(pending_bids.get("max_age_days") or 0)
            risks.append({
                "risk_code": "PROC-003",
                "risk_type": "procurement",
                "severity": "high" if age > 7 else "medium",
                "title": f"{n} bid approval(s) pending in queue — oldest {int(age)}d",
                "description": "Bids received but not yet approved for import",
                "evidence": {"pending_count": n, "max_age_days": round(age, 1)},
                "confidence": 0.99,
                "mitigation": "Review approval queue at /api/v1/services/approval-queue",
            })
        return risks

    def _schedule_risks(self) -> list:
        risks = []
        variances = self.pg_query("""
            SELECT activity_name, variance_days, variance_pct, risk_level,
                   cause, decision_needed, recovery_action
            FROM schedule_variance
            WHERE project_id = %s AND ABS(variance_days) > 0
            ORDER BY ABS(variance_days) DESC
        """, (self.project_id,))

        high_var = [v for v in variances if abs(int(v.get("variance_days") or 0)) > 7]
        medium_var = [v for v in variances if 3 <= abs(int(v.get("variance_days") or 0)) <= 7]

        if high_var:
            risks.append({
                "risk_code": "SCHED-001",
                "risk_type": "schedule",
                "severity": "high",
                "title": f"Schedule variance >7 days on {len(high_var)} activit{'y' if len(high_var)==1 else 'ies'}",
                "description": high_var[0].get("cause", ""),
                "evidence": {"activities": [v["activity_name"] for v in high_var[:3]], "variance_days": [v["variance_days"] for v in high_var[:3]]},
                "confidence": 0.9,
                "mitigation": high_var[0].get("recovery_action", "Review with superintendent"),
            })
        if medium_var:
            risks.append({
                "risk_code": "SCHED-002",
                "risk_type": "schedule",
                "severity": "medium",
                "title": f"Schedule variance 3-7 days on {len(medium_var)} activit{'y' if len(medium_var)==1 else 'ies'}",
                "description": medium_var[0].get("cause", ""),
                "evidence": {"activities": [v["activity_name"] for v in medium_var[:3]]},
                "confidence": 0.85,
                "mitigation": "Monitor — no immediate action required",
            })

        # Check decisions needed from schedule variances
        decisions_needed = [v for v in variances if v.get("decision_needed")]
        if decisions_needed:
            risks.append({
                "risk_code": "SCHED-003",
                "risk_type": "schedule",
                "severity": "medium",
                "title": f"Schedule decisions needed on {len(decisions_needed)} item(s)",
                "description": decisions_needed[0].get("decision_needed", "")[:200],
                "evidence": {"items": [v["activity_name"] for v in decisions_needed[:3]]},
                "confidence": 0.88,
                "mitigation": "Review with PM and SS — decisions blocking schedule",
            })
        return risks

    def _decision_risks(self) -> list:
        risks = []
        stale = self.pg_query("""
            SELECT exec_id, title,
                   EXTRACT(EPOCH FROM (NOW() - created_at))/86400 AS age_days,
                   deadline, confidence
            FROM executive_inbox
            WHERE status='pending'
            ORDER BY age_days DESC
        """)
        stale_over_3 = [d for d in stale if float(d.get("age_days") or 0) > 3]
        if stale_over_3:
            risks.append({
                "risk_code": "DEC-001",
                "risk_type": "decision",
                "severity": "high" if any(float(d.get("age_days") or 0) > 7 for d in stale_over_3) else "medium",
                "title": f"{len(stale_over_3)} decision(s) waiting >3 days",
                "description": f"Oldest: {stale_over_3[0].get('title','')} ({int(float(stale_over_3[0].get('age_days',0)))}d)",
                "evidence": {"decisions": [{"title": d["title"], "age_days": int(float(d.get("age_days",0)))} for d in stale_over_3[:3]]},
                "confidence": 0.99,
                "mitigation": "Review executive inbox — approve, reject, or defer each item",
            })
        return risks

    def _budget_risks(self) -> list:
        risks = []
        # Historical cost variance on this project
        cost_rows = self.pg_query("""
            SELECT csi_division, awarded_amount, final_cost, variance_pct
            FROM historical_cost_records
            WHERE project_id = %s AND variance_pct IS NOT NULL
            ORDER BY ABS(variance_pct) DESC
        """, (self.project_id,))

        over_budget = [r for r in cost_rows if float(r.get("variance_pct") or 0) > 5]
        if over_budget:
            total_exposure = sum(
                (float(r.get("final_cost") or 0) - float(r.get("awarded_amount") or 0))
                for r in over_budget
                if r.get("final_cost") and r.get("awarded_amount")
            )
            risks.append({
                "risk_code": "BUDGET-001",
                "risk_type": "budget",
                "severity": "high" if total_exposure > 50000 else "medium",
                "title": f"Budget overrun detected on {len(over_budget)} scope(s)",
                "description": f"Total exposure: ${total_exposure:,.0f} across {len(over_budget)} CSI division(s)",
                "evidence": {"divisions": [r["csi_division"] for r in over_budget[:3]], "total_exposure": round(total_exposure, 2)},
                "confidence": 0.85,
                "mitigation": "Review with PM — consider contingency draw or change order",
            })

        # Houzz budget overruns (if data available)
        if self._houzz_has_data():
            houzz_budget = self.pg_query("""
                SELECT category, budgeted_amount, actual_amount, variance
                FROM houzz_budget
                WHERE houzz_project_id = (
                    SELECT houzz_project_id FROM houzz_projects WHERE name ILIKE %s LIMIT 1
                ) AND actual_amount > budgeted_amount
            """, (f"%{(self._project_row() or {}).get('name','').split()[0]}%",))

            if houzz_budget:
                total_houzz_exposure = sum(
                    float(b.get("actual_amount") or 0) - float(b.get("budgeted_amount") or 0)
                    for b in houzz_budget
                )
                risks.append({
                    "risk_code": "BUDGET-002",
                    "risk_type": "budget",
                    "severity": "high" if total_houzz_exposure > 25000 else "medium",
                    "title": f"Houzz budget overrun: ${total_houzz_exposure:,.0f} across {len(houzz_budget)} categor{'y' if len(houzz_budget)==1 else 'ies'}",
                    "description": f"Categories: {', '.join(b['category'] for b in houzz_budget[:3])}",
                    "evidence": {"categories": [b["category"] for b in houzz_budget[:3]], "total_exposure": round(total_houzz_exposure, 2)},
                    "confidence": 0.9,
                    "mitigation": "Issue change order or adjust scope to recover budget",
                })
        return risks

    def _data_gap_risks(self) -> list:
        risks = []
        completeness = self._data_completeness()
        if completeness < 40:
            risks.append({
                "risk_code": "DATA-001",
                "risk_type": "data_quality",
                "severity": "medium",
                "title": f"Project data completeness: {completeness:.0f}% — intelligence limited",
                "description": "Houzz sync required to unlock schedule, budget, and vendor intelligence",
                "evidence": {"completeness_pct": completeness, "missing": "Houzz schedule, budget, change orders, vendors"},
                "confidence": 0.99,
                "mitigation": "Run Browser Claude Houzz extraction for this project",
            })
        return risks

    # ── Supporting Computations ─────────────────────────────────────────────────

    def _compute_health(self, risks: list) -> tuple:
        factors = []
        has_critical = any(r["severity"] == "critical" for r in risks)
        has_high = any(r["severity"] == "high" for r in risks)

        if has_critical:
            health = "RED"
            for r in risks:
                if r["severity"] == "critical":
                    factors.append(r["title"])
        elif has_high:
            health = "YELLOW"
            for r in risks:
                if r["severity"] == "high":
                    factors.append(r["title"])
        else:
            health = "GREEN"
            if risks:
                factors.append(f"{len(risks)} low/medium risk(s) — all within normal parameters")

        return health, factors[:4]

    def _open_decisions(self) -> list:
        return self.pg_query("""
            SELECT exec_id, title, deadline, confidence, business_impact,
                   EXTRACT(EPOCH FROM (NOW() - created_at))/86400 AS days_waiting
            FROM executive_inbox
            WHERE status='pending'
            ORDER BY deadline NULLS LAST
            LIMIT 10
        """)

    def _open_questions(self) -> list:
        items = []
        # RFIs
        rfis = self.pg_query("""
            SELECT rfi_number, subject, status, submitted_date,
                   (CURRENT_DATE - submitted_date::date) AS age_days
            FROM rfis WHERE project_id=%s AND status NOT IN ('closed','resolved')
            ORDER BY submitted_date DESC LIMIT 5
        """, (self.project_id,))
        for r in rfis:
            items.append({"type": "RFI", "id": r.get("rfi_number"), "description": r.get("subject"), "age_days": r.get("age_days")})

        # Schedule decisions needed
        sched = self.pg_query("""
            SELECT activity_name, decision_needed, detected_at
            FROM schedule_variance WHERE project_id=%s AND decision_needed IS NOT NULL
            ORDER BY detected_at DESC LIMIT 3
        """, (self.project_id,))
        for s in sched:
            items.append({"type": "schedule_decision", "description": s.get("decision_needed"), "activity": s.get("activity_name")})

        return items[:8]

    def _missing_information(self) -> list:
        missing = []
        p = self._project_row() or {}

        if not self._houzz_has_data():
            missing.append({"category": "schedule", "item": "Houzz schedule data", "action": "Run Browser Claude extraction — unlocks schedule, tasks, budget"})
        if not p.get("super_name"):
            missing.append({"category": "team", "item": "Superintendent not assigned", "action": "Assign SS in projects table"})
        if not p.get("pm_name"):
            missing.append({"category": "team", "item": "PM not assigned", "action": "Assign PM in projects table"})
        if not p.get("hubspot_deal_id"):
            missing.append({"category": "crm", "item": "No HubSpot deal linked", "action": "Link HubSpot deal ID in projects table"})

        # Check for empty critical tables
        for table, name, action in [
            ("rfis", "RFIs", "Import RFIs from Houzz or email"),
            ("submittals", "Submittals tracker", "Import submittals log"),
            ("risks", "Risk register", "Add risks to risk register"),
        ]:
            row = self.pg_one(f"SELECT COUNT(*) AS n FROM {table} WHERE project_id=%s", (self.project_id,))
            if not row or int(row.get("n") or 0) == 0:
                missing.append({"category": "data", "item": f"No {name} on file", "action": action})

        return missing[:8]

    def _timeline(self) -> dict:
        variances = self.pg_query("""
            SELECT activity_name, variance_days, variance_pct, risk_level, detected_at
            FROM schedule_variance WHERE project_id=%s
            ORDER BY ABS(variance_days) DESC
        """, (self.project_id,))

        project = self._project_row() or {}
        return {
            "start_date": str(project.get("start_date", "Unknown")),
            "target_completion": str(project.get("end_date") or "Not set"),
            "variance_items": len(variances),
            "max_variance_days": max((int(v.get("variance_days") or 0) for v in variances), default=0),
            "at_risk_activities": [v["activity_name"] for v in variances if v.get("risk_level") in ("high","critical")][:5],
            "data_status": "live" if variances else "pending_houzz_sync",
        }

    def _procurement_status(self) -> dict:
        packages = self.pg_query("""
            SELECT bp.package_name, bp.csi_division, bp.status, bp.awarded_amount,
                   COUNT(be.id) AS bid_count
            FROM bid_packages bp
            LEFT JOIN bid_entries be ON be.bid_package_id = bp.id
            WHERE bp.project_id = %s
            GROUP BY bp.id, bp.package_name, bp.csi_division, bp.status, bp.awarded_amount
            ORDER BY bp.status, bp.csi_division
        """, (self.project_id,))

        awarded = [p for p in packages if p.get("status") == "awarded"]
        open_pkgs = [p for p in packages if p.get("status") not in ("awarded","cancelled")]
        no_bids = [p for p in open_pkgs if int(p.get("bid_count") or 0) == 0]

        total_awarded = sum(float(p.get("awarded_amount") or 0) for p in awarded)

        return {
            "total_packages": len(packages),
            "awarded": len(awarded),
            "open": len(open_pkgs),
            "no_bids_yet": len(no_bids),
            "total_awarded_value": total_awarded,
            "packages": [dict(p) for p in packages[:20]],
        }

    def _data_completeness(self) -> float:
        """Score 0-100 based on how many data sources are populated."""
        score = 0.0
        p = self._project_row() or {}
        checks = [
            (bool(p), 20),
            (bool(p.get("hubspot_deal_id")), 10),
            (self._houzz_has_data(), 30),
            (self.pg_one("SELECT 1 FROM bid_packages WHERE project_id=%s LIMIT 1", (self.project_id,)) is not None, 15),
            (self.pg_one("SELECT 1 FROM daily_logs WHERE project_id=%s LIMIT 1", (self.project_id,)) is not None, 10),
            (self.pg_one("SELECT 1 FROM schedule_variance WHERE project_id=%s LIMIT 1", (self.project_id,)) is not None, 15),
        ]
        for condition, weight in checks:
            if condition:
                score += weight
        return score

    def _houzz_has_data(self) -> bool:
        try:
            r = self.pg_one("SELECT COUNT(*) AS n FROM houzz_projects")
            return int(r.get("n") or 0) > 0
        except Exception:
            return False

    # ── AI Synthesis ────────────────────────────────────────────────────────────

    def _generate_summary(self, project: dict, health: str, risks: list,
                          decisions: list, procurement: dict) -> str:
        try:
            high_risks = [r for r in risks if r["severity"] in ("critical","high")]
            context = (
                f"PROJECT: {project.get('name')} — {project.get('address','')}\n"
                f"STATUS: {health}\n"
                f"OPEN BIDS: {procurement.get('open',0)} packages, {procurement.get('no_bids_yet',0)} with no bids\n"
                f"AWARDED: {procurement.get('awarded',0)} packages, ${procurement.get('total_awarded_value',0):,.0f}\n"
                f"HIGH RISKS: {'; '.join(r['title'] for r in high_risks[:3]) or 'None'}\n"
                f"DECISIONS PENDING: {len(decisions)}\n"
            )
            if risks:
                context += "TOP RISKS:\n" + "\n".join(f"- [{r['severity'].upper()}] {r['title']}" for r in risks[:4])

            prompt = f"{context}\n\nWrite a 3-sentence executive summary of this project's current state and top priority action."
            return self.ask_claude(prompt, system=INTELLIGENCE_SYSTEM_PROMPT, max_tokens=300)
        except Exception as e:
            return f"Summary unavailable: {e}"

    def _recommend_actions(self, risks: list, decisions: list, procurement: dict) -> list:
        actions = []
        for r in risks[:5]:
            if r.get("mitigation"):
                prefix = f"[{r['severity'].upper()}] {r['risk_type'].upper()}: "
                actions.append(prefix + r["mitigation"])
        if decisions:
            oldest = sorted(decisions, key=lambda d: float(d.get("days_waiting") or 0), reverse=True)[0]
            actions.append(f"[DECISION] Review '{oldest.get('title','')}' — {int(float(oldest.get('days_waiting',0)))}d waiting")
        if not actions:
            actions.append("No immediate actions required — monitor open bids and schedule")
        return actions[:6]

    # ── Persistence ─────────────────────────────────────────────────────────────

    def _persist_snapshot(self, health: str, factors: list, risks: list,
                          decisions: list, procurement: dict):
        try:
            import psycopg2
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
                INSERT INTO project_brain_snapshots
                    (project_id, snapshot_date, health, health_factors, risk_count,
                     open_decisions, open_bids, data_completeness_pct)
                VALUES (%s, CURRENT_DATE, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (project_id, snapshot_date) DO UPDATE SET
                    health = EXCLUDED.health,
                    health_factors = EXCLUDED.health_factors,
                    risk_count = EXCLUDED.risk_count,
                    open_decisions = EXCLUDED.open_decisions,
                    open_bids = EXCLUDED.open_bids,
                    data_completeness_pct = EXCLUDED.data_completeness_pct
            """, (
                self.project_id, health, json.dumps(factors),
                len(risks), len(decisions),
                procurement.get("open", 0),
                self._data_completeness()
            ))
            conn.close()
        except Exception:
            pass  # Non-fatal — snapshot persistence is best-effort

"""
Predictive Engine — Phase 2, Priority 3
Forward-looking risk predictions for schedule, budget, permits, procurement,
trade conflicts, cash flow, and inspections. Each prediction includes
supporting evidence and a confidence score.

Mounted at /api/v1/services/predictive-engine
"""
import os, sys, json
from datetime import datetime, timezone, date, timedelta
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter, HTTPException
from base import BaseIntelligenceService

router = APIRouter()

_CODES = {1: "64EW", 2: "101F", 3: "1355R", 4: "83SB"}
_RISK_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "CLEAR": 3}


def _f(v) -> float:
    """Safe float conversion from Decimal or None."""
    try:
        return float(v) if v is not None else 0.0
    except Exception:
        return 0.0


def _days_since(d) -> int:
    if d is None:
        return 0
    if isinstance(d, datetime):
        d = d.date()
    return (date.today() - d).days


def _days_until(d) -> int:
    if d is None:
        return 9999
    if isinstance(d, datetime):
        d = d.date()
    return (d - date.today()).days


class PredictiveEngine(BaseIntelligenceService):
    SERVICE_NAME = "predictive_engine"

    def __init__(self, project_id: int):
        self.project_id = project_id
        self._project = None

    def _get_project(self) -> dict:
        if self._project is None:
            row = self.pg_one("SELECT * FROM projects WHERE id=%s", (self.project_id,))
            if not row:
                raise HTTPException(status_code=404, detail=f"Project {self.project_id} not found")
            self._project = dict(row)
        return self._project

    def all_predictions(self) -> dict:
        p = self._get_project()
        predictions = [
            self.predict_schedule(),
            self.predict_budget(),
            self.predict_permits(),
            self.predict_procurement(),
            self.predict_trade_conflicts(),
            self.predict_cash_flow(),
            self.predict_inspections(),
        ]
        predictions.sort(key=lambda x: _RISK_ORDER.get(x["risk_level"], 9))
        high_count = sum(1 for p in predictions if p["risk_level"] == "HIGH")
        medium_count = sum(1 for p in predictions if p["risk_level"] == "MEDIUM")
        overall = "HIGH" if high_count > 0 else ("MEDIUM" if medium_count > 0 else "CLEAR")
        self._persist_predictions(predictions)
        return {
            "project_id": self.project_id,
            "project_code": _CODES.get(self.project_id, f"P{self.project_id}"),
            "project_name": p.get("name"),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "overall_risk": overall,
            "high_risk_count": high_count,
            "medium_risk_count": medium_count,
            "predictions": predictions,
        }

    # ── Schedule Risk ──────────────────────────────────────────────────────────

    def predict_schedule(self) -> dict:
        pid = self.project_id
        evidence = []
        confidence_factors = []

        # Current variance items
        variance = self.pg_query("""
            SELECT activity_name, variance_days, risk_level, cause, responsible_party
            FROM schedule_variance
            WHERE project_id=%s
            ORDER BY variance_days DESC
        """, (pid,))

        overdue_count = sum(1 for v in variance if (v.get("variance_days") or 0) > 0)
        high_risk_count = sum(1 for v in variance if v.get("risk_level") in ("high", "critical"))
        avg_variance = sum(_f(v.get("variance_days")) for v in variance) / max(len(variance), 1)

        if variance:
            confidence_factors.append(0.3)
            evidence.append({
                "item": f"{len(variance)} schedule variance items tracked; avg {avg_variance:.0f} days behind",
                "weight": "high" if high_risk_count > 0 else "medium"
            })
        if high_risk_count > 0:
            evidence.append({
                "item": f"{high_risk_count} items rated high/critical risk",
                "weight": "high"
            })
            confidence_factors.append(0.25)

        # Overdue submittals (blocking schedule)
        overdue_submittals = self.pg_query("""
            SELECT description, required_approval_date
            FROM submittals
            WHERE project_id=%s AND status NOT IN ('approved','rejected')
              AND required_approval_date < CURRENT_DATE
        """, (pid,))
        if overdue_submittals:
            evidence.append({
                "item": f"{len(overdue_submittals)} submittals past required approval date",
                "weight": "high"
            })
            confidence_factors.append(0.2)

        # Open RFIs older than 14 days
        stale_rfis = self.pg_query("""
            SELECT rfi_number, subject, submitted_date
            FROM rfis
            WHERE project_id=%s AND status='open'
              AND submitted_date < CURRENT_DATE - INTERVAL '14 days'
        """, (pid,))
        if stale_rfis:
            evidence.append({
                "item": f"{len(stale_rfis)} RFIs open >14 days without response",
                "weight": "medium"
            })
            confidence_factors.append(0.15)

        # Long lead items at risk
        at_risk_lli = self.pg_query("""
            SELECT item_name, required_on_site_date, lead_time_weeks
            FROM long_lead_items
            WHERE project_id=%s AND status NOT IN ('delivered','cancelled')
              AND required_on_site_date < CURRENT_DATE + INTERVAL '30 days'
        """, (pid,))
        if at_risk_lli:
            evidence.append({
                "item": f"{len(at_risk_lli)} long-lead items needed in next 30 days",
                "weight": "high"
            })
            confidence_factors.append(0.2)

        # Historical cost variance as proxy for schedule discipline
        hist = self.pg_one("""
            SELECT AVG(variance_pct) as avg_variance
            FROM historical_cost_records
            WHERE project_id=%s AND variance_pct IS NOT NULL
        """, (pid,))
        if hist and hist.get("avg_variance"):
            avg_hv = _f(hist["avg_variance"])
            if avg_hv > 10:
                evidence.append({
                    "item": f"Historical cost variance avg {avg_hv:.1f}%% — projects with cost overruns often have schedule overruns",
                    "weight": "medium"
                })
                confidence_factors.append(0.1)

        if not evidence:
            evidence.append({
                "item": "No schedule delay signals detected — schedule tracking current",
                "weight": "low"
            })

        confidence = min(0.85, sum(confidence_factors)) if confidence_factors else 0.25
        risk_level = self._risk_from_evidence(
            critical=high_risk_count > 2 or len(overdue_submittals) > 3 or len(at_risk_lli) > 2,
            elevated=high_risk_count > 0 or len(overdue_submittals) > 0 or len(stale_rfis) > 2,
            evidence_count=len(evidence)
        )
        predicted_impact = self._schedule_impact(avg_variance, high_risk_count)

        return self._prediction(
            "schedule", risk_level, confidence, evidence,
            title="Schedule slip risk — next 30 days",
            description=f"{overdue_count} activities behind baseline; {len(overdue_submittals)} submittals blocking progress",
            predicted_impact=predicted_impact,
            actions=self._schedule_actions(high_risk_count, overdue_submittals, stale_rfis, at_risk_lli),
            data_sources="schedule_variance, submittals, rfis, long_lead_items"
        )

    def _schedule_impact(self, avg_variance: float, high_count: int) -> str:
        if avg_variance > 21 or high_count > 3:
            return "30-60 day schedule slip probable"
        if avg_variance > 7 or high_count > 1:
            return "14-30 day schedule slip possible"
        if avg_variance > 0:
            return "7-14 day schedule slip possible"
        return "No significant schedule impact predicted"

    def _schedule_actions(self, high_count, submittals, rfis, lli) -> list:
        actions = []
        if high_count > 0:
            actions.append("Hold schedule recovery meeting with SS and subs — identify float and crash options")
        if submittals:
            actions.append(f"Escalate {len(submittals)} overdue submittals to architect/engineer today")
        if rfis:
            actions.append(f"Follow up on {len(rfis)} stale RFIs — consider substitution requests if delays persist")
        if lli:
            actions.append(f"Confirm delivery dates for {len(lli)} long-lead items due in 30 days")
        if not actions:
            actions.append("Continue current schedule management — no immediate action required")
        return actions

    # ── Budget Risk ────────────────────────────────────────────────────────────

    def predict_budget(self) -> dict:
        pid = self.project_id
        evidence = []
        confidence_factors = []

        # Current Houzz budget vs actual
        # houzz_budget links via houzz_project_id (text) → houzz_projects.houzz_project_id
        # houzz_projects matches to projects by name
        budget = self.pg_query("""
            SELECT hb.category, hb.budgeted_amount, hb.actual_amount, hb.committed_amount
            FROM houzz_budget hb
            JOIN houzz_projects hp ON hp.houzz_project_id = hb.houzz_project_id
            JOIN projects p ON p.name ILIKE hp.name
            WHERE p.id = %s
        """, (pid,))

        total_budgeted = sum(_f(b.get("budgeted_amount")) for b in budget)
        total_actual = sum(_f(b.get("actual_amount")) for b in budget)
        total_committed = sum(_f(b.get("committed_amount")) for b in budget)
        overrun_pct = ((total_actual - total_budgeted) / total_budgeted * 100) if total_budgeted > 0 else 0

        if budget:
            confidence_factors.append(0.3)
            if overrun_pct > 0:
                evidence.append({
                    "item": f"Current budget overrun: {overrun_pct:.1f}%% (${total_actual:,.0f} actual vs ${total_budgeted:,.0f} budget)",
                    "weight": "high" if overrun_pct > 10 else "medium"
                })

        # Change orders pending / not approved
        change_orders = self.pg_query("""
            SELECT hco.title, hco.amount, hco.status, hco.submitted_date
            FROM houzz_change_orders hco
            JOIN houzz_projects hp ON hp.houzz_project_id = hco.houzz_project_id
            JOIN projects p ON p.name ILIKE hp.name
            WHERE p.id = %s AND hco.approved_date IS NULL
        """, (pid,))
        pending_co_value = sum(_f(c.get("amount")) for c in change_orders)
        if change_orders:
            evidence.append({
                "item": f"{len(change_orders)} unsigned change orders totaling ${pending_co_value:,.0f}",
                "weight": "high" if pending_co_value > 50000 else "medium"
            })
            confidence_factors.append(0.25)

        # Open bid packages — unawarded scope = budget risk
        open_packages = self.pg_query("""
            SELECT package_name, SUM(be.bid_amount) as avg_bid
            FROM bid_packages bp
            LEFT JOIN bid_entries be ON be.bid_package_id = bp.id
            WHERE bp.project_id=%s AND bp.status NOT IN ('awarded','cancelled')
            GROUP BY bp.package_name
        """, (pid,))
        if open_packages:
            evidence.append({
                "item": f"{len(open_packages)} bid packages not yet awarded — budget exposure unresolved",
                "weight": "medium"
            })
            confidence_factors.append(0.2)

        # Historical cost overrun pattern
        hist_overruns = self.pg_query("""
            SELECT csi_division, variance_pct, final_cost - awarded_amount as overrun
            FROM historical_cost_records
            WHERE project_id=%s AND final_cost > awarded_amount
            ORDER BY (final_cost - awarded_amount) DESC
            LIMIT 5
        """, (pid,))
        if hist_overruns:
            total_hist_overrun = sum(_f(h.get("overrun")) for h in hist_overruns)
            evidence.append({
                "item": f"Historical overruns in {len(hist_overruns)} divisions; total exposure ${total_hist_overrun:,.0f}",
                "weight": "medium"
            })
            confidence_factors.append(0.2)

        # Committed vs budget ratio
        if total_budgeted > 0 and total_committed > 0:
            commit_ratio = total_committed / total_budgeted
            if commit_ratio > 0.9:
                evidence.append({
                    "item": f"Commitments at {commit_ratio*100:.0f}%% of budget — limited contingency remaining",
                    "weight": "high"
                })
                confidence_factors.append(0.15)

        if not evidence:
            evidence.append({
                "item": "No budget overrun signals detected — connect Houzz for real-time tracking",
                "weight": "low"
            })

        confidence = min(0.85, sum(confidence_factors)) if confidence_factors else 0.25
        risk_level = self._risk_from_evidence(
            critical=overrun_pct > 15 or pending_co_value > 100000,
            elevated=overrun_pct > 5 or pending_co_value > 25000 or len(open_packages) > 5,
            evidence_count=len(evidence)
        )
        projected_final = total_committed + (total_actual if total_actual > total_committed else 0)
        projected_overrun_pct = ((projected_final - total_budgeted) / total_budgeted * 100) if total_budgeted > 0 else 0

        return self._prediction(
            "budget", risk_level, confidence, evidence,
            title="Budget overrun risk",
            description=f"${pending_co_value:,.0f} in unsigned COs; {len(open_packages)} packages unawarded",
            predicted_impact=f"Projected overrun: {max(overrun_pct, projected_overrun_pct):.1f}%%" if any([total_budgeted, pending_co_value]) else "Insufficient budget data",
            actions=self._budget_actions(overrun_pct, change_orders, open_packages),
            data_sources="houzz_budget, houzz_change_orders, bid_packages, historical_cost_records"
        )

    def _budget_actions(self, overrun_pct, cos, open_pkgs) -> list:
        actions = []
        if overrun_pct > 5:
            actions.append(f"Investigate drivers of {overrun_pct:.1f}%% cost overrun — identify and stop cost bleed")
        if cos:
            actions.append(f"Prioritize approval of {len(cos)} pending change orders to lock in final scope")
        if open_pkgs:
            actions.append(f"Award or narrow {len(open_pkgs)} open bid packages to reduce budget exposure")
        if not actions:
            actions.append("Budget tracking current — continue monitoring committed vs budgeted ratio")
        return actions

    # ── Permit Risk ────────────────────────────────────────────────────────────

    def predict_permits(self) -> dict:
        pid = self.project_id
        evidence = []
        confidence_factors = []

        # Submittals pending approval (permit-adjacent)
        pending_submittals = self.pg_query("""
            SELECT submittal_number, description, submitted_date, required_approval_date,
                   CURRENT_DATE - submitted_date AS days_waiting
            FROM submittals
            WHERE project_id=%s AND status IN ('pending','submitted','under_review')
            ORDER BY days_waiting DESC
        """, (pid,))

        stale_submittals = [s for s in pending_submittals
                            if _days_since(s.get("submitted_date")) > 21]
        upcoming_deadline = [s for s in pending_submittals
                             if s.get("required_approval_date") and
                             _days_until(s.get("required_approval_date")) <= 14]

        if stale_submittals:
            evidence.append({
                "item": f"{len(stale_submittals)} submittals pending >21 days — potential permit pathway blockage",
                "weight": "high"
            })
            confidence_factors.append(0.3)

        if upcoming_deadline:
            evidence.append({
                "item": f"{len(upcoming_deadline)} submittals with approval deadlines in next 14 days",
                "weight": "high"
            })
            confidence_factors.append(0.25)

        # Executive inbox items about permits/inspections (no project_id in this table)
        permit_items = self.pg_query("""
            SELECT title, status,
                   CURRENT_DATE - created_at::date AS days_waiting
            FROM executive_inbox
            WHERE status = 'pending'
              AND (LOWER(title) LIKE '%%permit%%' OR LOWER(title) LIKE '%%inspect%%'
                   OR LOWER(title) LIKE '%%approval%%' OR LOWER(title) LIKE '%%city%%')
        """, ())
        if permit_items:
            evidence.append({
                "item": f"{len(permit_items)} open permit/inspection items in executive inbox",
                "weight": "medium"
            })
            confidence_factors.append(0.2)

        # Approval queue permit items
        aq_permits = self.pg_query("""
            SELECT target_description FROM approval_queue
            WHERE project_id=%s AND status='pending'
              AND (LOWER(workflow) LIKE '%%permit%%' OR LOWER(target_description) LIKE '%%permit%%'
                   OR LOWER(target_description) LIKE '%%city%%' OR LOWER(workflow) LIKE '%%inspect%%')
        """, (pid,))
        if aq_permits:
            evidence.append({
                "item": f"{len(aq_permits)} permit-related items pending in approval queue",
                "weight": "medium"
            })
            confidence_factors.append(0.15)

        if not evidence:
            evidence.append({
                "item": "No active permit/submittal delays detected from available data",
                "weight": "low"
            })

        confidence = min(0.75, sum(confidence_factors)) if confidence_factors else 0.2
        risk_level = self._risk_from_evidence(
            critical=len(stale_submittals) > 3 or len(upcoming_deadline) > 2,
            elevated=len(stale_submittals) > 0 or len(permit_items) > 1,
            evidence_count=len(evidence)
        )

        return self._prediction(
            "permit", risk_level, confidence, evidence,
            title="Permit and approval delay risk",
            description=f"{len(pending_submittals)} submittals pending; {len(stale_submittals)} stale >21 days",
            predicted_impact="7-21 day permit hold possible" if risk_level != "CLEAR" else "No permit delay predicted",
            actions=[
                f"Chase {len(stale_submittals)} stale submittals with architect/AHJ immediately" if stale_submittals else None,
                f"Expedite {len(upcoming_deadline)} submittals with deadlines in 14 days" if upcoming_deadline else None,
                "Review permit pathway for critical path activities" if risk_level == "HIGH" else None,
                "Permit tracking current — continue monitoring" if risk_level == "CLEAR" else None,
            ],
            data_sources="submittals, executive_inbox, approval_queue"
        )

    # ── Procurement Risk ───────────────────────────────────────────────────────

    def predict_procurement(self) -> dict:
        pid = self.project_id
        evidence = []
        confidence_factors = []

        # Open packages with no bids received
        no_bids = self.pg_query("""
            SELECT bp.package_name
            FROM bid_packages bp
            WHERE bp.project_id=%s AND bp.status NOT IN ('awarded','cancelled')
              AND NOT EXISTS (SELECT 1 FROM bid_entries be WHERE be.bid_package_id=bp.id)
        """, (pid,))
        if no_bids:
            evidence.append({
                "item": f"{len(no_bids)} bid packages have no bids received",
                "weight": "high"
            })
            confidence_factors.append(0.3)

        # Packages with only 1 bid (no competition)
        single_bid = self.pg_query("""
            SELECT bp.package_name, COUNT(be.id) as bid_count
            FROM bid_packages bp
            JOIN bid_entries be ON be.bid_package_id = bp.id
            WHERE bp.project_id=%s AND bp.status NOT IN ('awarded','cancelled')
            GROUP BY bp.id, bp.package_name
            HAVING COUNT(be.id) = 1
        """, (pid,))
        if single_bid:
            evidence.append({
                "item": f"{len(single_bid)} packages with only 1 bid — no competitive pricing",
                "weight": "medium"
            })
            confidence_factors.append(0.2)

        # Long-lead items at risk (ordered but not delivered)
        lli_at_risk = self.pg_query("""
            SELECT item_name, vendor, lead_time_weeks, required_on_site_date
            FROM long_lead_items
            WHERE project_id=%s AND status IN ('ordered','pending')
              AND required_on_site_date < CURRENT_DATE + INTERVAL '60 days'
        """, (pid,))
        if lli_at_risk:
            evidence.append({
                "item": f"{len(lli_at_risk)} long-lead items due in 60 days not yet delivered",
                "weight": "high" if len(lli_at_risk) > 2 else "medium"
            })
            confidence_factors.append(0.25)

        # Bids sent but no response >21 days
        stale_bids = self.pg_query("""
            SELECT be.id, bp.package_name, be.date_sent, v.company_name
            FROM bid_entries be
            JOIN bid_packages bp ON bp.id = be.bid_package_id
            JOIN vendors v ON v.id = be.vendor_id
            WHERE bp.project_id=%s AND be.status IN ('sent','invited')
              AND be.date_sent < CURRENT_DATE - INTERVAL '21 days'
        """, (pid,))
        if stale_bids:
            evidence.append({
                "item": f"{len(stale_bids)} bid invitations sent >21 days ago without response",
                "weight": "medium"
            })
            confidence_factors.append(0.15)

        if not evidence:
            evidence.append({
                "item": "Procurement tracking current — all packages have competitive bids or are awarded",
                "weight": "low"
            })

        confidence = min(0.8, sum(confidence_factors)) if confidence_factors else 0.3
        risk_level = self._risk_from_evidence(
            critical=len(no_bids) > 5 or len(lli_at_risk) > 3,
            elevated=len(no_bids) > 0 or len(lli_at_risk) > 0 or len(stale_bids) > 3,
            evidence_count=len(evidence)
        )

        return self._prediction(
            "procurement", risk_level, confidence, evidence,
            title="Procurement delay risk",
            description=f"{len(no_bids)} packages unbid; {len(lli_at_risk)} long-lead items at risk",
            predicted_impact="Potential 2-6 week construction delay from procurement gaps" if risk_level != "CLEAR" else "Procurement on track",
            actions=[
                f"Issue bid invitations for {len(no_bids)} packages immediately" if no_bids else None,
                f"Follow up on {len(stale_bids)} non-responsive bidders" if stale_bids else None,
                f"Confirm delivery schedule for {len(lli_at_risk)} long-lead items with vendors" if lli_at_risk else None,
                "Consider sole-source justification for critical single-bid packages" if single_bid else None,
                "Procurement tracking current" if risk_level == "CLEAR" else None,
            ],
            data_sources="bid_packages, bid_entries, long_lead_items, vendors"
        )

    # ── Trade Conflict Risk ────────────────────────────────────────────────────

    def predict_trade_conflicts(self) -> dict:
        pid = self.project_id
        evidence = []
        confidence_factors = []

        # Multiple trades with schedule overlap (from schedule_variance as proxy)
        concurrent_trades = self.pg_query("""
            SELECT responsible_party, COUNT(*) as items,
                   SUM(CASE WHEN risk_level IN ('high','critical') THEN 1 ELSE 0 END) as high_risk
            FROM schedule_variance
            WHERE project_id=%s AND responsible_party IS NOT NULL
            GROUP BY responsible_party
            HAVING COUNT(*) > 1
        """, (pid,))

        if len(concurrent_trades) > 3:
            evidence.append({
                "item": f"{len(concurrent_trades)} trades with multiple concurrent activities — overlap risk",
                "weight": "high"
            })
            confidence_factors.append(0.25)
        elif len(concurrent_trades) > 0:
            evidence.append({
                "item": f"{len(concurrent_trades)} trades with overlapping schedule activities",
                "weight": "medium"
            })
            confidence_factors.append(0.15)

        # Vendors with awarded packages but also pending bids on same project
        trade_overlap = self.pg_query("""
            SELECT v.company_name,
                   SUM(CASE WHEN bp.status='awarded' THEN 1 ELSE 0 END) as awarded_scopes,
                   SUM(CASE WHEN bp.status NOT IN ('awarded','cancelled') THEN 1 ELSE 0 END) as pending_scopes
            FROM bid_entries be
            JOIN bid_packages bp ON bp.id = be.bid_package_id
            JOIN vendors v ON v.id = be.vendor_id
            WHERE bp.project_id=%s
            GROUP BY v.company_name
            HAVING SUM(CASE WHEN bp.status='awarded' THEN 1 ELSE 0 END) > 0
               AND SUM(CASE WHEN bp.status NOT IN ('awarded','cancelled') THEN 1 ELSE 0 END) > 0
        """, (pid,))

        if trade_overlap:
            evidence.append({
                "item": f"{len(trade_overlap)} vendors managing multiple scopes concurrently — capacity risk",
                "weight": "medium"
            })
            confidence_factors.append(0.2)

        # Open RFIs that are coordination issues (multiple parties)
        coord_rfis = self.pg_one("""
            SELECT COUNT(*) as n FROM rfis
            WHERE project_id=%s AND status='open'
              AND (LOWER(subject) LIKE '%%coord%%' OR LOWER(subject) LIKE '%%conflict%%'
                   OR LOWER(subject) LIKE '%%clash%%' OR LOWER(subject) LIKE '%%sequence%%')
        """, (pid,))
        coord_n = int((coord_rfis or {}).get("n") or 0)
        if coord_n > 0:
            evidence.append({
                "item": f"{coord_n} open coordination/conflict RFIs",
                "weight": "high"
            })
            confidence_factors.append(0.2)

        if not evidence:
            evidence.append({
                "item": "No active trade conflict signals detected from current data",
                "weight": "low"
            })
            confidence_factors.append(0.05)

        confidence = min(0.65, sum(confidence_factors)) if confidence_factors else 0.2
        risk_level = self._risk_from_evidence(
            critical=coord_n > 3 or len(concurrent_trades) > 5,
            elevated=coord_n > 0 or len(trade_overlap) > 2,
            evidence_count=len(evidence)
        )

        return self._prediction(
            "trade_conflict", risk_level, confidence, evidence,
            title="Trade conflict and sequencing risk",
            description=f"{len(concurrent_trades)} trades with overlapping activities; {coord_n} coordination RFIs",
            predicted_impact="Trade congestion may add 5-15 days to critical path" if risk_level != "CLEAR" else "Trade sequencing appears manageable",
            actions=[
                "Hold three-week lookahead meeting with all active trades" if risk_level == "HIGH" else None,
                f"Resolve {coord_n} coordination RFIs before affected scopes begin" if coord_n > 0 else None,
                "Review vendor capacity for multi-scope subs — request foreman commitments" if trade_overlap else None,
                "Continue weekly lookahead coordination" if risk_level == "CLEAR" else None,
            ],
            data_sources="schedule_variance, bid_entries, bid_packages, rfis"
        )

    # ── Cash Flow Risk ─────────────────────────────────────────────────────────

    def predict_cash_flow(self) -> dict:
        pid = self.project_id
        evidence = []
        confidence_factors = []

        # Total committed vs total budget
        budget_summary = self.pg_one("""
            SELECT SUM(hb.budgeted_amount) as total_budget,
                   SUM(hb.actual_amount) as total_actual,
                   SUM(hb.committed_amount) as total_committed
            FROM houzz_budget hb
            JOIN houzz_projects hp ON hp.houzz_project_id = hb.houzz_project_id
            JOIN projects p ON p.name ILIKE hp.name
            WHERE p.id = %s
        """, (pid,))

        total_budget = _f((budget_summary or {}).get("total_budget"))
        total_actual = _f((budget_summary or {}).get("total_actual"))
        total_committed = _f((budget_summary or {}).get("total_committed"))

        if total_budget > 0:
            confidence_factors.append(0.3)
            burn_rate_pct = (total_actual / total_budget) * 100
            commit_pct = (total_committed / total_budget) * 100
            evidence.append({
                "item": f"Burn rate: {burn_rate_pct:.1f}%% of budget spent; {commit_pct:.1f}%% committed",
                "weight": "high" if burn_rate_pct > 80 else "medium"
            })
            if commit_pct > 95:
                evidence.append({
                    "item": "Commitments exceed 95%% of budget — contingency nearly exhausted",
                    "weight": "high"
                })
                confidence_factors.append(0.2)

        # Large unpaid change orders = cash flow strain
        unsigned_co_total = self.pg_one("""
            SELECT SUM(hco.amount) as total
            FROM houzz_change_orders hco
            JOIN houzz_projects hp ON hp.houzz_project_id = hco.houzz_project_id
            JOIN projects p ON p.name ILIKE hp.name
            WHERE p.id = %s AND hco.approved_date IS NULL AND hco.amount > 0
        """, (pid,))
        unsigned_co_val = _f((unsigned_co_total or {}).get("total"))
        if unsigned_co_val > 10000:
            evidence.append({
                "item": f"${unsigned_co_val:,.0f} in unsigned change orders affecting cash flow",
                "weight": "high" if unsigned_co_val > 50000 else "medium"
            })
            confidence_factors.append(0.2)

        # Pending approval queue items (can hold billing)
        pending_aq = self.pg_one("""
            SELECT COUNT(*) as n FROM approval_queue
            WHERE project_id=%s AND status='pending'
        """, (pid,))
        pending_n = int((pending_aq or {}).get("n") or 0) if pending_aq else 0
        if pending_n > 20:
            evidence.append({
                "item": f"{pending_n} items pending in approval queue — unresolved items delay billing",
                "weight": "medium"
            })
            confidence_factors.append(0.15)

        # Historical cost overruns are a cash flow risk indicator
        hist_overrun = self.pg_one("""
            SELECT COUNT(*) as n, SUM(final_cost - awarded_amount) as total_overrun
            FROM historical_cost_records
            WHERE project_id=%s AND final_cost > awarded_amount
        """, (pid,))
        if hist_overrun and hist_overrun.get("n", 0) > 0:
            overrun_total = _f(hist_overrun.get("total_overrun"))
            evidence.append({
                "item": f"Historical overruns: ${overrun_total:,.0f} across {hist_overrun['n']} line items",
                "weight": "medium"
            })
            confidence_factors.append(0.1)

        if not evidence:
            evidence.append({
                "item": "Insufficient financial data for cash flow prediction — connect Houzz for real-time tracking",
                "weight": "low"
            })

        confidence = min(0.8, sum(confidence_factors)) if confidence_factors else 0.2
        risk_level = self._risk_from_evidence(
            critical=unsigned_co_val > 100000 or (total_budget > 0 and total_committed / total_budget > 0.98),
            elevated=unsigned_co_val > 25000 or pending_n > 50,
            evidence_count=len(evidence)
        )

        return self._prediction(
            "cash_flow", risk_level, confidence, evidence,
            title="Cash flow risk",
            description=f"${unsigned_co_val:,.0f} in unsigned COs; {pending_n} pending approvals holding billing",
            predicted_impact="Cash flow stress in next 30-45 days" if risk_level != "CLEAR" else "Cash flow appears stable",
            actions=[
                f"Expedite approval of ${unsigned_co_val:,.0f} in change orders to release billing" if unsigned_co_val > 10000 else None,
                f"Clear {pending_n} approval queue items blocking invoicing" if pending_n > 20 else None,
                "Review billing schedule against completion milestones" if risk_level != "CLEAR" else None,
                "Cash flow tracking current" if risk_level == "CLEAR" else None,
            ],
            data_sources="houzz_budget, houzz_change_orders, approval_queue, historical_cost_records"
        )

    # ── Inspection Risk ────────────────────────────────────────────────────────

    def predict_inspections(self) -> dict:
        pid = self.project_id
        evidence = []
        confidence_factors = []

        # Submittals approaching approval deadline (inspection pre-reqs)
        near_deadline = self.pg_query("""
            SELECT submittal_number, description, required_approval_date
            FROM submittals
            WHERE project_id=%s AND status NOT IN ('approved','rejected')
              AND required_approval_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '21 days'
        """, (pid,))
        if near_deadline:
            evidence.append({
                "item": f"{len(near_deadline)} submittals must be approved in next 21 days for inspection readiness",
                "weight": "high"
            })
            confidence_factors.append(0.25)

        # Inspection-related executive inbox items (no project_id in this table)
        insp_items = self.pg_query("""
            SELECT title, CURRENT_DATE - created_at::date AS days_waiting
            FROM executive_inbox
            WHERE status = 'pending'
              AND (LOWER(title) LIKE '%%inspect%%' OR LOWER(title) LIKE '%%punch%%'
                   OR LOWER(title) LIKE '%%ahj%%' OR LOWER(title) LIKE '%%certificate%%'
                   OR LOWER(title) LIKE '%%final%%')
        """, ())
        if insp_items:
            evidence.append({
                "item": f"{len(insp_items)} open inspection/punch list items in executive inbox",
                "weight": "medium"
            })
            confidence_factors.append(0.2)

        # Approval queue inspection items
        insp_aq = self.pg_query("""
            SELECT target_description FROM approval_queue
            WHERE project_id=%s AND status='pending'
              AND (LOWER(workflow) LIKE '%%inspect%%' OR LOWER(target_description) LIKE '%%inspect%%'
                   OR LOWER(target_description) LIKE '%%punch%%' OR LOWER(target_description) LIKE '%%final%%')
        """, (pid,))
        if insp_aq:
            evidence.append({
                "item": f"{len(insp_aq)} inspection-related items in approval queue",
                "weight": "medium"
            })
            confidence_factors.append(0.15)

        # Schedule variance items with pending inspections
        insp_schedule = self.pg_query("""
            SELECT activity_name, variance_days FROM schedule_variance
            WHERE project_id=%s
              AND (LOWER(activity_name) LIKE '%%inspect%%' OR LOWER(activity_name) LIKE '%%final%%'
                   OR LOWER(cause) LIKE '%%inspect%%')
        """, (pid,))
        if insp_schedule:
            evidence.append({
                "item": f"{len(insp_schedule)} schedule activities affected by inspection delays",
                "weight": "high"
            })
            confidence_factors.append(0.2)

        # Pending RFIs on inspection-critical items
        insp_rfis = self.pg_query("""
            SELECT rfi_number FROM rfis
            WHERE project_id=%s AND status='open'
              AND (LOWER(subject) LIKE '%%inspect%%' OR LOWER(subject) LIKE '%%code%%'
                   OR LOWER(subject) LIKE '%%compliance%%')
        """, (pid,))
        if insp_rfis:
            evidence.append({
                "item": f"{len(insp_rfis)} open code compliance/inspection RFIs",
                "weight": "medium"
            })
            confidence_factors.append(0.15)

        if not evidence:
            evidence.append({
                "item": "No active inspection risk signals detected from current data",
                "weight": "low"
            })

        confidence = min(0.70, sum(confidence_factors)) if confidence_factors else 0.2
        risk_level = self._risk_from_evidence(
            critical=len(near_deadline) > 3 or len(insp_schedule) > 2,
            elevated=len(near_deadline) > 0 or len(insp_items) > 1,
            evidence_count=len(evidence)
        )

        return self._prediction(
            "inspection", risk_level, confidence, evidence,
            title="Inspection and code compliance risk",
            description=f"{len(near_deadline)} submittals needed for upcoming inspections; {len(insp_items)} open inspection items",
            predicted_impact="Inspection hold risk could delay CO by 2-4 weeks" if risk_level != "CLEAR" else "Inspection readiness on track",
            actions=[
                f"Fast-track approval of {len(near_deadline)} submittals before inspection windows" if near_deadline else None,
                f"Resolve {len(insp_rfis)} code compliance RFIs before inspections begin" if insp_rfis else None,
                "Prepare pre-inspection checklist with SS and subcontractors" if risk_level == "HIGH" else None,
                "Inspection tracking current — no immediate action required" if risk_level == "CLEAR" else None,
            ],
            data_sources="submittals, executive_inbox, approval_queue, schedule_variance, rfis"
        )

    # ── Helpers ────────────────────────────────────────────────────────────────

    @staticmethod
    def _risk_from_evidence(critical: bool, elevated: bool, evidence_count: int) -> str:
        if critical:
            return "HIGH"
        if elevated:
            return "MEDIUM"
        if evidence_count > 0:
            return "LOW"
        return "CLEAR"

    @staticmethod
    def _prediction(prediction_type: str, risk_level: str, confidence: float,
                    evidence: list, title: str, description: str,
                    predicted_impact: str, actions: list, data_sources: str) -> dict:
        return {
            "prediction_type": prediction_type,
            "risk_level": risk_level,
            "title": title,
            "description": description,
            "confidence": round(confidence, 2),
            "confidence_label": ("High" if confidence >= 0.7 else "Medium" if confidence >= 0.4 else "Low"),
            "evidence": evidence,
            "predicted_impact": predicted_impact,
            "recommended_actions": [a for a in actions if a],
            "data_sources": data_sources,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _persist_predictions(self, predictions: list):
        try:
            import psycopg2
            from dotenv import load_dotenv
            load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))
            conn = psycopg2.connect(
                host=os.environ.get("POSTGRES_HOST", "localhost"),
                port=int(os.environ.get("POSTGRES_PORT", 5432)),
                dbname=os.environ.get("POSTGRES_DB", "hci_os"),
                user=os.environ.get("POSTGRES_USER", "hci_admin"),
                password=os.environ.get("POSTGRES_PASSWORD", ""),
            )
            conn.autocommit = True
            cur = conn.cursor()
            for pred in predictions:
                cur.execute("""
                    INSERT INTO predictions_computed
                        (project_id, prediction_type, risk_level, confidence,
                         title, description, predicted_impact, evidence,
                         recommended_actions, data_sources)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (project_id, prediction_type) DO UPDATE SET
                        risk_level = EXCLUDED.risk_level,
                        confidence = EXCLUDED.confidence,
                        title = EXCLUDED.title,
                        description = EXCLUDED.description,
                        predicted_impact = EXCLUDED.predicted_impact,
                        evidence = EXCLUDED.evidence,
                        recommended_actions = EXCLUDED.recommended_actions,
                        generated_at = NOW()
                """, (
                    self.project_id,
                    pred["prediction_type"],
                    pred["risk_level"],
                    pred["confidence"],
                    pred["title"],
                    pred["description"],
                    pred["predicted_impact"],
                    json.dumps(pred["evidence"]),
                    json.dumps(pred["recommended_actions"]),
                    pred["data_sources"],
                ))
            conn.close()
        except Exception:
            pass


# ── Company-wide predictions ─────────────────────────────────────────────────

class CompanyPredictiveEngine(BaseIntelligenceService):
    SERVICE_NAME = "company_predictive_engine"

    def company_predictions(self) -> dict:
        projects = self.pg_query("SELECT id, name FROM projects WHERE status='active' ORDER BY name")

        # Each project's predictions are fully independent (own PredictiveEngine
        # instance, own DB connection via BaseIntelligenceService) - found 2026-07-06
        # this endpoint ran the same sequential per-project loop that made 4 dashboard
        # endpoints take 500ms-1.4s. Running them concurrently instead of one-at-a-time
        # is a pure orchestration change (identical per-project logic and output),
        # not a behavior change, so it carries far less regression risk than touching
        # the prediction methods themselves. executor.map preserves input order.
        def _one(p):
            try:
                engine = PredictiveEngine(p["id"])
                preds = engine.all_predictions()
                return {
                    "project_id": p["id"],
                    "project_name": p["name"],
                    "overall_risk": preds["overall_risk"],
                    "high_risk_count": preds["high_risk_count"],
                    "medium_risk_count": preds["medium_risk_count"],
                    "top_predictions": [
                        {"type": pr["prediction_type"], "risk": pr["risk_level"], "title": pr["title"]}
                        for pr in preds["predictions"] if pr["risk_level"] in ("HIGH", "MEDIUM")
                    ][:3],
                }
            except Exception as e:
                return {
                    "project_id": p["id"],
                    "project_name": p["name"],
                    "overall_risk": "UNKNOWN",
                    "error": str(e),
                }

        if projects:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(projects), 8)) as ex:
                results = list(ex.map(_one, projects))
        else:
            results = []

        high_projects = [r for r in results if r.get("overall_risk") == "HIGH"]
        company_risk = "HIGH" if high_projects else ("MEDIUM" if any(r.get("overall_risk") == "MEDIUM" for r in results) else "LOW")

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "company_risk": company_risk,
            "projects_at_high_risk": len(high_projects),
            "projects": results,
        }


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("")
def service_info():
    return {
        "service": "predictive_engine",
        "status": "active",
        "phase": 2,
        "endpoints": [
            "GET /{project_id}/predictions — all 7 predictions for a project",
            "GET /{project_id}/predictions/{type} — single prediction type",
            "GET /company/predictions — portfolio-level risk summary",
        ],
        "prediction_types": ["schedule", "budget", "permit", "procurement",
                             "trade_conflict", "cash_flow", "inspection"],
    }


@router.get("/company/predictions")
def company_predictions():
    """Portfolio-level predictive risk summary — all active projects."""
    svc = CompanyPredictiveEngine()
    return svc.company_predictions()


@router.get("/{project_id}/predictions")
def project_predictions(project_id: int):
    """All 7 predictive risk assessments for a project with evidence and confidence scores."""
    engine = PredictiveEngine(project_id)
    return engine.all_predictions()


@router.get("/{project_id}/predictions/{prediction_type}")
def single_prediction(project_id: int, prediction_type: str):
    """Single prediction type for a project."""
    engine = PredictiveEngine(project_id)
    engine._get_project()  # validates project exists
    handlers = {
        "schedule": engine.predict_schedule,
        "budget": engine.predict_budget,
        "permit": engine.predict_permits,
        "procurement": engine.predict_procurement,
        "trade_conflict": engine.predict_trade_conflicts,
        "cash_flow": engine.predict_cash_flow,
        "inspection": engine.predict_inspections,
    }
    if prediction_type not in handlers:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown prediction type. Valid: {list(handlers.keys())}"
        )
    return handlers[prediction_type]()

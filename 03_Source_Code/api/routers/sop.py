"""
SOP Execution Layer API Router
Exposes endpoints for SOP 04–30 (full preconstruction + field execution chain).
All endpoints follow the Universal Workflow Spine and enforce stop conditions.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "services", "sop_execution"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "services"))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Any

router = APIRouter(prefix="/sop", tags=["sop"])

# ── Import services ────────────────────────────────────────────────────────────
try:
    from sop_04_plan_review.sop_04_service import SOP04PlanReviewService
    from sop_05_construction_narrative.sop_05_service import SOP05ConstructionNarrativeService
    from sop_06_missing_info.sop_06_service import SOP06MissingInfoService
    from sop_07_rom_budget.sop_07_service import SOP07ROMBudgetService
    from sop_08_historical_cost.sop_08_service import SOP08HistoricalCostService
    from sop_09_budget_review.sop_09_service import SOP09BudgetReviewService
    from sop_10_allowances.sop_10_service import SOP10AllowancesService
    from sop_11_bid_package.sop_11_service import SOP11BidPackageService
    from sop_12_sub_crm.sop_12_service import SOP12SubCRMService
    from sop_13_bid_distribution.sop_13_service import SOP13BidDistributionService
    from sop_14_bid_followup.sop_14_service import SOP14BidFollowUpService
    from sop_15_bid_leveling.sop_15_service import SOP15BidLevelingService
    from sop_16_buyout.sop_16_service import SOP16BuyoutService
    from sop_19_subcontract_agreement.sop_19_service import SOP19SubcontractAgreementService
    from sop_17_project_schedule.sop_17_service import SOP17ProjectScheduleService
    from sop_18_long_lead.sop_18_service import SOP18LongLeadService
    from sop_20_contract_setup.sop_20_service import SOP20ContractSetupService
    from sop_21_compliance.sop_21_service import SOP21ComplianceService
    from sop_22_coi_w9_lien.sop_22_service import SOP22COIService
    from sop_23_project_startup.sop_23_service import SOP23ProjectStartupService
    from sop_24_super_dashboard.sop_24_service import SOP24SuperDashboardService
    from sop_25_daily_log.sop_25_service import SOP25DailyLogService
    from sop_26_field_coordination.sop_26_service import SOP26FieldCoordService
    from sop_27_quality_control.sop_27_service import SOP27QualityControlService
    from sop_28_qc_detail_card.sop_28_service import SOP28QCDetailCardService
    from sop_29_safety.sop_29_service import SOP29SafetyService
    from sop_30_inspection.sop_30_service import SOP30InspectionService
    _svc_loaded = True
except Exception as _e:
    _svc_loaded = False
    _svc_error = str(_e)


def _check_svc():
    if not _svc_loaded:
        raise HTTPException(503, f"SOP service not loaded: {_svc_error}")


# ──────────────────────────────────────────────────────────────────────────────
# SOP Registry
# ──────────────────────────────────────────────────────────────────────────────

@router.get("/registry")
def sop_registry():
    return {
        "sops": [
            {"sop_number": "04", "name": "Plan Review",
             "status": "active", "phase": "Preconstruction"},
            {"sop_number": "05", "name": "Construction Narrative",
             "status": "active", "phase": "Preconstruction"},
            {"sop_number": "06", "name": "Missing Information / Risk Log",
             "status": "active", "phase": "Preconstruction"},
            {"sop_number": "07", "name": "ROM Budget",
             "status": "active", "phase": "Estimating"},
            {"sop_number": "08", "name": "Historical Cost Database",
             "status": "active", "phase": "Estimating"},
            {"sop_number": "09", "name": "Budget Review",
             "status": "active", "phase": "Estimating"},
            {"sop_number": "10", "name": "Allowances / Alternates / Exclusions",
             "status": "active", "phase": "Preconstruction"},
            {"sop_number": "11", "name": "Bid Package Assembly",
             "status": "active", "phase": "Preconstruction / Bidding"},
            {"sop_number": "13", "name": "Bid Distribution",
             "status": "active", "phase": "Bidding"},
            {"sop_number": "14", "name": "Bid Follow-Up",
             "status": "active", "phase": "Bidding"},
            {"sop_number": "15", "name": "Bid Leveling",
             "status": "active", "phase": "Bidding / Buyout"},
            {"sop_number": "16", "name": "Buyout",
             "status": "active", "phase": "Buyout"},
            {"sop_number": "12", "name": "Subcontractor CRM",
             "status": "active", "phase": "Preconstruction / Bidding"},
            {"sop_number": "19", "name": "Subcontract Agreement",
             "status": "active", "phase": "Buyout / Contract Execution"},
            {"sop_number": "17", "name": "Project Schedule",
             "status": "active", "phase": "Preconstruction / Setup"},
            {"sop_number": "18", "name": "Long-Lead Procurement",
             "status": "active", "phase": "Preconstruction / Setup"},
            {"sop_number": "20", "name": "Contract Setup",
             "status": "active", "phase": "Setup"},
            {"sop_number": "21", "name": "Compliance",
             "status": "active", "phase": "Setup"},
            {"sop_number": "22", "name": "COI / W-9 / Lien Waiver",
             "status": "active", "phase": "Setup"},
            {"sop_number": "23", "name": "Project Startup",
             "status": "active", "phase": "Setup / Field"},
            {"sop_number": "24", "name": "Superintendent Daily Dashboard",
             "status": "active", "phase": "Field Execution"},
            {"sop_number": "25", "name": "Daily Log",
             "status": "active", "phase": "Field Execution"},
            {"sop_number": "26", "name": "Field Coordination",
             "status": "active", "phase": "Field Execution"},
            {"sop_number": "27", "name": "Quality Control",
             "status": "active", "phase": "Field Execution"},
            {"sop_number": "28", "name": "QC Detail Card",
             "status": "active", "phase": "Field Execution"},
            {"sop_number": "29", "name": "Safety",
             "status": "active", "phase": "Field Execution"},
            {"sop_number": "30", "name": "Inspection",
             "status": "active", "phase": "Field Execution"},
        ]
    }


# ──────────────────────────────────────────────────────────────────────────────
# SOP 04 — Plan Review
# ──────────────────────────────────────────────────────────────────────────────

class SOP04StartRequest(BaseModel):
    project_id: int
    owner_name: str
    plan_set_file: str
    plan_issue_date: str
    project_type: str


class SOP04SectionRequest(BaseModel):
    trade_code: str
    trade_name: str
    page_refs: List[str] = []
    scope_notes: str = ""
    gaps_found: List[str] = []
    conflicts_found: List[str] = []
    constructibility_issues: List[str] = []


class SOP04HandoffRequest(BaseModel):
    actor: str
    project_id: int
    owner_name: str
    project_type: str
    plan_issue_date: str


@router.post("/04/instances")
def sop04_create(req: SOP04StartRequest):
    _check_svc()
    try:
        return SOP04PlanReviewService.start_review(
            req.project_id, req.owner_name, req.plan_set_file,
            req.plan_issue_date, req.project_type
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/04/instances/{instance_id}")
def sop04_get(instance_id: int):
    _check_svc()
    result = SOP04PlanReviewService.get_full_status(instance_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.post("/04/instances/{instance_id}/sections")
def sop04_add_section(instance_id: int, req: SOP04SectionRequest,
                      actor: str = "pm"):
    _check_svc()
    return SOP04PlanReviewService.add_plan_section(instance_id, req.dict(), actor)


@router.post("/04/instances/{instance_id}/ai-analysis")
def sop04_ai_analysis(instance_id: int):
    _check_svc()
    return SOP04PlanReviewService.run_ai_analysis(instance_id)


@router.post("/04/instances/{instance_id}/pm-confirm")
def sop04_pm_confirm(instance_id: int, pm_name: str):
    _check_svc()
    try:
        return SOP04PlanReviewService.pm_confirm(instance_id, pm_name)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/04/instances/{instance_id}/hand-off-to-05")
def sop04_handoff(instance_id: int, req: SOP04HandoffRequest):
    _check_svc()
    try:
        return SOP04PlanReviewService.hand_off_to_sop05(
            instance_id, req.actor, req.project_id,
            req.owner_name, req.project_type, req.plan_issue_date
        )
    except Exception as e:
        raise HTTPException(400, str(e))


# ──────────────────────────────────────────────────────────────────────────────
# SOP 05 — Construction Narrative
# ──────────────────────────────────────────────────────────────────────────────

class SOP05StartRequest(BaseModel):
    project_id: int
    sop_04_instance_id: int
    owner_name: str
    project_type: str
    plan_issue_date: str


class SOP05SectionRequest(BaseModel):
    trade_code: str
    trade_name: str
    narrative_text: str
    inclusions: List[str] = []
    exclusions: List[str] = []
    allowances_noted: List[str] = []
    pm_notes: str = ""


class SOP05AIDraftRequest(BaseModel):
    trade_code: str
    trade_name: str
    scope_notes: str = ""
    pm_additions: str = ""


class SOP05HandoffRequest(BaseModel):
    actor: str
    project_id: int
    owner_name: str


@router.post("/05/instances")
def sop05_create(req: SOP05StartRequest):
    _check_svc()
    try:
        return SOP05ConstructionNarrativeService.start_narrative(
            req.project_id, req.sop_04_instance_id, req.owner_name,
            req.project_type, req.plan_issue_date
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/05/instances/{instance_id}")
def sop05_get(instance_id: int):
    _check_svc()
    result = SOP05ConstructionNarrativeService.get_full_status(instance_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.post("/05/instances/{instance_id}/sections")
def sop05_draft_section(instance_id: int, req: SOP05SectionRequest,
                        actor: str = "pm"):
    _check_svc()
    return SOP05ConstructionNarrativeService.draft_section(instance_id, req.dict(), actor)


@router.post("/05/instances/{instance_id}/ai-draft")
def sop05_ai_draft(instance_id: int, req: SOP05AIDraftRequest):
    """Layer 3: AI drafts a narrative section for a trade."""
    _check_svc()
    return SOP05ConstructionNarrativeService.run_ai_draft(
        instance_id, req.trade_code, req.trade_name,
        req.scope_notes, req.pm_additions
    )


@router.post("/05/instances/{instance_id}/confirm-section")
def sop05_confirm_section(instance_id: int, trade_code: str,
                          pm_name: str, pm_notes: str = ""):
    _check_svc()
    return SOP05ConstructionNarrativeService.confirm_section(
        instance_id, trade_code, pm_name, pm_notes
    )


@router.post("/05/instances/{instance_id}/completeness-check")
def sop05_completeness_check(instance_id: int):
    _check_svc()
    return SOP05ConstructionNarrativeService.run_completeness_check(instance_id)


@router.post("/05/instances/{instance_id}/pm-approve")
def sop05_pm_approve(instance_id: int, pm_name: str):
    _check_svc()
    try:
        return SOP05ConstructionNarrativeService.pm_approve(instance_id, pm_name)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/05/instances/{instance_id}/hand-off-to-06")
def sop05_handoff(instance_id: int, req: SOP05HandoffRequest):
    _check_svc()
    try:
        return SOP05ConstructionNarrativeService.hand_off_to_sop06(
            instance_id, req.actor, req.project_id, req.owner_name
        )
    except Exception as e:
        raise HTTPException(400, str(e))


# ──────────────────────────────────────────────────────────────────────────────
# SOP 06 — Missing Information / Risk Log
# ──────────────────────────────────────────────────────────────────────────────

class SOP06StartRequest(BaseModel):
    project_id: int
    sop_05_instance_id: int
    owner_name: str


class SOP06MissingInfoRequest(BaseModel):
    item_code: str
    description: str
    source: str = ""
    responsible_party: str = ""
    due_date: str = ""
    priority: str = "MEDIUM"


class SOP06RiskRequest(BaseModel):
    risk_code: str
    description: str
    probability: str = "MEDIUM"
    impact: str = "MEDIUM"
    mitigation: str = ""
    owner: str = "PM"


class SOP06HandoffRequest(BaseModel):
    actor: str
    project_id: int
    owner_name: str
    project_type: str
    gross_sf: float
    sop_05_instance_id: int


@router.post("/06/instances")
def sop06_create(req: SOP06StartRequest):
    _check_svc()
    try:
        return SOP06MissingInfoService.start_risk_log(
            req.project_id, req.sop_05_instance_id, req.owner_name
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/06/instances/{instance_id}")
def sop06_get(instance_id: int):
    _check_svc()
    result = SOP06MissingInfoService.get_full_status(instance_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.post("/06/instances/{instance_id}/missing-info")
def sop06_add_missing_info(instance_id: int, req: SOP06MissingInfoRequest,
                           actor: str = "pm"):
    _check_svc()
    return SOP06MissingInfoService.add_missing_info(instance_id, req.dict(), actor)


@router.post("/06/instances/{instance_id}/risks")
def sop06_add_risk(instance_id: int, req: SOP06RiskRequest, actor: str = "pm"):
    _check_svc()
    return SOP06MissingInfoService.add_risk(instance_id, req.dict(), actor)


@router.post("/06/instances/{instance_id}/resolve")
def sop06_resolve_item(instance_id: int, item_code: str,
                       resolution_note: str, actor: str = "pm"):
    _check_svc()
    return SOP06MissingInfoService.resolve_item(instance_id, item_code, resolution_note, actor)


@router.post("/06/instances/{instance_id}/ai-gap-check")
def sop06_ai_gap_check(instance_id: int):
    """AI pulls gaps from SOP 04/05 and auto-populates missing info and risks."""
    _check_svc()
    return SOP06MissingInfoService.run_ai_gap_check(instance_id)


@router.post("/06/instances/{instance_id}/close")
def sop06_close(instance_id: int, actor: str = "pm"):
    _check_svc()
    return SOP06MissingInfoService.close_log(instance_id, actor)


@router.post("/06/instances/{instance_id}/hand-off-to-07")
def sop06_handoff(instance_id: int, req: SOP06HandoffRequest):
    _check_svc()
    try:
        return SOP06MissingInfoService.hand_off_to_sop07(
            instance_id, req.actor, req.project_id, req.owner_name,
            req.project_type, req.gross_sf, req.sop_05_instance_id
        )
    except Exception as e:
        return {"status": "blocked", "message": str(e)}


# ──────────────────────────────────────────────────────────────────────────────
# SOP 07 — ROM Budget
# ──────────────────────────────────────────────────────────────────────────────

class SOP07StartRequest(BaseModel):
    project_id: int
    owner_name: str
    project_type: str
    gross_sf: float
    sop_05_instance_id: int
    sop_06_instance_id: Optional[int] = None
    owner_budget_target: float = 0


class SOP07LineItemRequest(BaseModel):
    trade_code: str
    trade_name: str
    description: str
    unit: str = "LS"
    quantity: float = 1.0
    unit_cost: float = 0.0
    basis: str = "pm_estimate"


class SOP07BuckApproveRequest(BaseModel):
    approver: str = "Buck Adams"
    conditions: Optional[str] = None


class SOP07HandoffRequest(BaseModel):
    actor: str
    project_id: int
    owner_name: str
    project_type: str


@router.post("/07/instances")
def sop07_create(req: SOP07StartRequest):
    _check_svc()
    try:
        return SOP07ROMBudgetService.start_rom(
            req.project_id, req.owner_name, req.project_type,
            req.gross_sf, req.sop_05_instance_id,
            req.sop_06_instance_id, req.owner_budget_target
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/07/instances/{instance_id}")
def sop07_get(instance_id: int):
    _check_svc()
    result = SOP07ROMBudgetService.get_full_status(instance_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.post("/07/instances/{instance_id}/line-items")
def sop07_add_line_item(instance_id: int, req: SOP07LineItemRequest,
                        actor: str = "pm"):
    _check_svc()
    return SOP07ROMBudgetService.add_line_item(instance_id, req.dict(), actor)


@router.post("/07/instances/{instance_id}/ai-estimate")
def sop07_ai_estimate(instance_id: int):
    """Layer 3: AI generates full ROM estimate from SOP 05 narrative sections."""
    _check_svc()
    return SOP07ROMBudgetService.run_ai_estimate(instance_id)


@router.post("/07/instances/{instance_id}/pm-review")
def sop07_pm_review(instance_id: int, pm_name: str):
    _check_svc()
    try:
        return SOP07ROMBudgetService.pm_review(instance_id, pm_name)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/07/instances/{instance_id}/buck-approve")
def sop07_buck_approve(instance_id: int, req: SOP07BuckApproveRequest):
    """Gate 07-C: Buck approves ROM > $500k."""
    _check_svc()
    try:
        return SOP07ROMBudgetService.buck_approve(instance_id, req.approver, req.conditions)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/07/instances/{instance_id}/hand-off-to-09")
def sop07_handoff(instance_id: int, req: SOP07HandoffRequest):
    _check_svc()
    try:
        return SOP07ROMBudgetService.hand_off_to_sop09(
            instance_id, req.actor, req.project_id,
            req.owner_name, req.project_type
        )
    except Exception as e:
        return {"status": "blocked", "message": str(e)}


# ──────────────────────────────────────────────────────────────────────────────
# SOP 08 — Historical Cost Database
# ──────────────────────────────────────────────────────────────────────────────

class SOP08StartRequest(BaseModel):
    project_id: int
    trade_code: str
    work_description: str
    project_type: str
    owner_name: str = "estimator"


class SOP08AddRecordRequest(BaseModel):
    project_id: int
    trade_code: str
    description: str
    unit: str
    unit_cost: float
    project_type: str
    year: int
    source_project_id: Optional[int] = None
    notes: str = ""


@router.post("/08/lookups")
def sop08_start_lookup(req: SOP08StartRequest):
    _check_svc()
    try:
        return SOP08HistoricalCostService.start_lookup(
            req.project_id, req.trade_code, req.work_description,
            req.project_type, req.owner_name
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/08/lookups/{instance_id}")
def sop08_get(instance_id: int):
    _check_svc()
    result = SOP08HistoricalCostService.get_full_status(instance_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.post("/08/lookups/{instance_id}/lookup-cost")
def sop08_lookup_cost(instance_id: int, unit: str = "SF",
                      actor: str = "estimator"):
    _check_svc()
    return SOP08HistoricalCostService.lookup_cost(instance_id, unit, actor)


@router.post("/08/lookups/{instance_id}/benchmark-sf")
def sop08_benchmark_sf(instance_id: int, gross_sf: float,
                       actor: str = "estimator"):
    _check_svc()
    return SOP08HistoricalCostService.benchmark_sf(instance_id, gross_sf, actor)


@router.post("/08/records")
def sop08_add_record(req: SOP08AddRecordRequest, actor: str = "pm"):
    """Add a new historical cost record (from completed project data)."""
    _check_svc()
    return SOP08HistoricalCostService.add_cost_record(
        req.project_id, req.trade_code, req.description, req.unit,
        req.unit_cost, req.project_type, req.year,
        req.source_project_id, req.notes, actor
    )


# ──────────────────────────────────────────────────────────────────────────────
# SOP 09 — Budget Review
# ──────────────────────────────────────────────────────────────────────────────

class SOP09StartRequest(BaseModel):
    project_id: int
    sop_07_instance_id: int
    owner_name: str
    project_type: str
    owner_budget_target: float = 0


class SOP09LineItemRequest(BaseModel):
    trade_code: str
    trade_name: str
    description: str
    rom_amount: float
    revised_amount: float = 0.0
    basis: str = ""
    pm_notes: str = ""


class SOP09BuckApproveRequest(BaseModel):
    approver: str = "Buck Adams"
    conditions: Optional[str] = None
    project_name: str = ""


class SOP09HandoffRequest(BaseModel):
    actor: str
    project_id: int
    owner_name: str


@router.post("/09/instances")
def sop09_create(req: SOP09StartRequest):
    _check_svc()
    try:
        return SOP09BudgetReviewService.start_review(
            req.project_id, req.sop_07_instance_id, req.owner_name,
            req.project_type, req.owner_budget_target
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/09/instances/{instance_id}")
def sop09_get(instance_id: int):
    _check_svc()
    result = SOP09BudgetReviewService.get_full_status(instance_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.post("/09/instances/{instance_id}/line-items")
def sop09_revise_line_item(instance_id: int, req: SOP09LineItemRequest,
                           actor: str = "pm"):
    _check_svc()
    return SOP09BudgetReviewService.revise_line_item(instance_id, req.dict(), actor)


@router.post("/09/instances/{instance_id}/ai-review")
def sop09_ai_review(instance_id: int):
    """AI compares ROM to revised budget and generates variance report."""
    _check_svc()
    return SOP09BudgetReviewService.run_ai_review(instance_id)


@router.post("/09/instances/{instance_id}/pm-approve")
def sop09_pm_approve(instance_id: int, pm_name: str):
    _check_svc()
    try:
        return SOP09BudgetReviewService.pm_approve(instance_id, pm_name)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/09/instances/{instance_id}/buck-approve")
def sop09_buck_approve(instance_id: int, req: SOP09BuckApproveRequest):
    """Gate 09-C: Buck approves final budget > $500k before proceeding to bid."""
    _check_svc()
    try:
        return SOP09BudgetReviewService.buck_approve(
            instance_id, req.approver, req.conditions, req.project_name
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/09/instances/{instance_id}/hand-off-to-10")
def sop09_handoff(instance_id: int, req: SOP09HandoffRequest):
    """Trigger SOP 10 (Allowances) from approved budget."""
    _check_svc()
    try:
        return SOP09BudgetReviewService.hand_off_to_sop10(
            instance_id, req.actor, req.project_id, req.owner_name
        )
    except Exception as e:
        return {"status": "blocked", "message": str(e)}


# ──────────────────────────────────────────────────────────────────────────────
# SOP 10 — Allowances / Alternates / Exclusions
# ──────────────────────────────────────────────────────────────────────────────

class SOP10StartRequest(BaseModel):
    project_id: int
    owner_name: str


class SOP10InputRequest(BaseModel):
    input_key: str
    value: str


class SOP10AllowanceRequest(BaseModel):
    allowance_code: str
    description: str
    allowance_type: str = "construction_allowance"
    amount: float
    trade_code: str = "GEN"
    basis: str = ""
    ai_suggested: bool = False
    notes: str = ""


class SOP10AlternateRequest(BaseModel):
    alternate_code: str
    description: str
    alternate_type: str = "additive"
    estimated_cost_impact: float = 0.0
    trade_code: str = "GEN"
    basis: str = ""
    included_in_base: bool = False


class SOP10ExclusionRequest(BaseModel):
    exclusion_code: str
    description: str
    trade_code: str = "GEN"
    excluded_party: str = "subcontractor"
    basis: str = ""


class SOP10AIReviewRequest(BaseModel):
    project_type: str
    scope_narrative: str


class SOP10BuckApproveRequest(BaseModel):
    approver: str = "Buck Adams"
    conditions: Optional[str] = None


class SOP10HandoffRequest(BaseModel):
    actor: str
    project_id: int
    owner_name: str
    target_issue_date: str
    bid_due_date: str


@router.post("/10/instances")
def sop10_create(req: SOP10StartRequest):
    _check_svc()
    try:
        return SOP10AllowancesService.start_allowances(req.project_id, req.owner_name)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/10/instances/{instance_id}")
def sop10_get(instance_id: int):
    _check_svc()
    result = SOP10AllowancesService.get_full_status(instance_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.post("/10/instances/{instance_id}/inputs")
def sop10_confirm_input(instance_id: int, req: SOP10InputRequest,
                        actor: str = "pm"):
    _check_svc()
    try:
        return SOP10AllowancesService.confirm_input(instance_id, req.input_key, req.value)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/10/instances/{instance_id}/validate-inputs")
def sop10_validate_inputs(instance_id: int):
    _check_svc()
    try:
        return SOP10AllowancesService.validate_inputs(instance_id)
    except Exception as e:
        return {"status": "blocked", "message": str(e)}


@router.post("/10/instances/{instance_id}/start-work")
def sop10_start_work(instance_id: int, actor: str = "pm"):
    _check_svc()
    try:
        return SOP10AllowancesService.start_work(instance_id, actor)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/10/instances/{instance_id}/allowances")
def sop10_add_allowance(instance_id: int, req: SOP10AllowanceRequest,
                        actor: str = "pm"):
    _check_svc()
    return SOP10AllowancesService.add_allowance(instance_id, req.dict(), actor)


@router.post("/10/instances/{instance_id}/alternates")
def sop10_add_alternate(instance_id: int, req: SOP10AlternateRequest,
                        actor: str = "pm"):
    _check_svc()
    return SOP10AllowancesService.add_alternate(instance_id, req.dict(), actor)


@router.post("/10/instances/{instance_id}/exclusions")
def sop10_add_exclusion(instance_id: int, req: SOP10ExclusionRequest,
                        actor: str = "pm"):
    _check_svc()
    return SOP10AllowancesService.add_exclusion(instance_id, req.dict(), actor)


@router.post("/10/instances/{instance_id}/ai-review")
def sop10_ai_review(instance_id: int, req: SOP10AIReviewRequest):
    _check_svc()
    return SOP10AllowancesService.run_ai_review(
        instance_id, req.project_type, req.scope_narrative
    )


@router.post("/10/instances/{instance_id}/pm-approve")
def sop10_pm_approve(instance_id: int, pm_name: str):
    _check_svc()
    try:
        return SOP10AllowancesService.pm_approve(instance_id, pm_name)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/10/instances/{instance_id}/buck-approve")
def sop10_buck_approve(instance_id: int, req: SOP10BuckApproveRequest):
    """Gate 10-C: Buck authorizes total allowance pool > $50,000."""
    _check_svc()
    try:
        return SOP10AllowancesService.buck_approve(instance_id, req.approver, req.conditions)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/10/instances/{instance_id}/hand-off-to-11")
def sop10_handoff(instance_id: int, req: SOP10HandoffRequest):
    """Trigger SOP 11 from SOP 10 completion."""
    _check_svc()
    try:
        return SOP10AllowancesService.hand_off_to_sop11(
            instance_id, req.actor, req.project_id, req.owner_name,
            req.target_issue_date, req.bid_due_date
        )
    except Exception as e:
        return {"status": "blocked", "message": str(e)}


# ──────────────────────────────────────────────────────────────────────────────
# SOP 11 — Bid Package
# ──────────────────────────────────────────────────────────────────────────────

class SOP11StartRequest(BaseModel):
    project_id: int
    owner_name: str
    target_issue_date: str
    bid_due_date: str


class SOP11InputConfirmRequest(BaseModel):
    input_key: str
    confirmed_by: str
    file_path: Optional[str] = None
    notes: Optional[str] = None


class SOP11ScopeSectionRequest(BaseModel):
    trade_code: str
    trade_name: str
    scope_text: str
    drawing_refs: List[str] = []
    spec_refs: List[str] = []
    allowances: List[dict] = []
    alternates: List[dict] = []
    exclusions: List[str] = []
    bid_bond_required: bool = False


class SOP11BuckApprovalRequest(BaseModel):
    approver: str = "Buck Adams"
    conditions: Optional[str] = None


class SOP11IssueRequest(BaseModel):
    actor: str
    recipient_list: List[str]


class SOP11RevisionRequest(BaseModel):
    reviewer_name: str
    comments: str


@router.post("/11/instances")
def sop11_create(req: SOP11StartRequest):
    _check_svc()
    try:
        return SOP11BidPackageService.start_bid_package(
            req.project_id, req.owner_name, req.target_issue_date, req.bid_due_date
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/11/instances/{instance_id}")
def sop11_get(instance_id: int):
    _check_svc()
    result = SOP11BidPackageService.get_full_status(instance_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.get("/11/instances")
def sop11_list(project_id: Optional[int] = None, status: Optional[str] = None):
    _check_svc()
    return {"instances": SOP11BidPackageService.list_instances(project_id, status)}


@router.post("/11/instances/{instance_id}/validate-inputs")
def sop11_validate_inputs(instance_id: int):
    _check_svc()
    try:
        return SOP11BidPackageService.validate_inputs(instance_id)
    except Exception as e:
        return {"status": "blocked", "message": str(e)}


@router.post("/11/instances/{instance_id}/inputs")
def sop11_confirm_input(instance_id: int, req: SOP11InputConfirmRequest):
    _check_svc()
    try:
        return SOP11BidPackageService.confirm_input(
            instance_id, req.input_key, req.confirmed_by, req.file_path, req.notes
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/11/instances/{instance_id}/start-work")
def sop11_start_work(instance_id: int, actor: str = "estimator"):
    """Transition Ready to Start → In Progress."""
    _check_svc()
    try:
        return SOP11BidPackageService.start_work(instance_id, actor)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/11/instances/{instance_id}/scope-sections")
def sop11_add_scope_section(instance_id: int, req: SOP11ScopeSectionRequest,
                            owner_name: str = "estimator"):
    _check_svc()
    return SOP11BidPackageService.add_scope_section(
        instance_id, req.dict(), owner_name
    )


@router.post("/11/instances/{instance_id}/ai-review")
def sop11_ai_review(instance_id: int):
    _check_svc()
    return SOP11BidPackageService.run_ai_review(instance_id)


@router.post("/11/instances/{instance_id}/submit-review")
def sop11_submit_review(instance_id: int, reviewer_name: str):
    _check_svc()
    try:
        return SOP11BidPackageService.submit_for_review(instance_id, reviewer_name)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/11/instances/{instance_id}/revision-required")
def sop11_revision_required(instance_id: int, req: SOP11RevisionRequest):
    _check_svc()
    try:
        return SOP11BidPackageService.revision_required(
            instance_id, req.reviewer_name, req.comments
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/11/instances/{instance_id}/request-approval")
def sop11_request_approval(instance_id: int, pm_name: str, summary: str = ""):
    _check_svc()
    try:
        return SOP11BidPackageService.request_buck_approval(instance_id, pm_name, summary)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/11/instances/{instance_id}/buck-approval")
def sop11_buck_approval(instance_id: int, req: SOP11BuckApprovalRequest):
    """Gate 11-C: Buck approves bid package for issue."""
    _check_svc()
    try:
        return SOP11BidPackageService.record_buck_approval(
            instance_id, req.approver, req.conditions
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/11/instances/{instance_id}/issue")
def sop11_issue(instance_id: int, req: SOP11IssueRequest):
    """Issue bid package to sub list. SC-04 and SC-07 enforced."""
    _check_svc()
    try:
        return SOP11BidPackageService.issue_bid_package(
            instance_id, req.actor, req.recipient_list
        )
    except Exception as e:
        return {"status": "blocked", "message": str(e)}


@router.post("/11/instances/{instance_id}/hand-off-to-15")
def sop11_handoff(instance_id: int, actor: str, project_id: int, owner_name: str):
    """Trigger SOP 15 from SOP 11 handoff."""
    _check_svc()
    try:
        return SOP11BidPackageService.hand_off_to_sop15(
            instance_id, actor, project_id, owner_name
        )
    except Exception as e:
        raise HTTPException(400, str(e))


# ──────────────────────────────────────────────────────────────────────────────
# SOP 15 — Bid Leveling
# ──────────────────────────────────────────────────────────────────────────────

class SOP15StartRequest(BaseModel):
    project_id: int
    sop_11_instance_id: int
    owner_name: str


class SOP15BidRequest(BaseModel):
    bidder_name: str
    bid_amount: float
    received_date: str
    bid_text: str = ""
    responsive: bool = True
    scope_summary: str = ""
    estimator_name: str = ""


class SOP15AdjustmentRequest(BaseModel):
    bidder_name: str
    description: str
    amount: float
    reason: str
    is_estimate: bool = False
    estimator_name: str = ""


class SOP15AwardRequest(BaseModel):
    awarded_sub: str
    award_amount: float
    scope_basis: str
    rationale: str
    risks_accepted: str = ""
    conditions: str = ""
    approver: str = "Buck Adams"


@router.post("/15/instances")
def sop15_create(req: SOP15StartRequest):
    _check_svc()
    try:
        return SOP15BidLevelingService.start_leveling(
            req.project_id, req.sop_11_instance_id, req.owner_name
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/15/instances/{instance_id}")
def sop15_get(instance_id: int):
    _check_svc()
    result = SOP15BidLevelingService.get_full_status(instance_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.post("/15/instances/{instance_id}/bids")
def sop15_log_bid(instance_id: int, req: SOP15BidRequest):
    _check_svc()
    try:
        return SOP15BidLevelingService.log_bid(
            instance_id, req.bidder_name, req.bid_amount,
            req.received_date, req.bid_text, req.responsive,
            req.scope_summary, req.estimator_name
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/15/instances/{instance_id}/adjustments")
def sop15_add_adjustment(instance_id: int, req: SOP15AdjustmentRequest):
    _check_svc()
    return SOP15BidLevelingService.add_bid_adjustment(
        instance_id, req.bidder_name, req.description,
        req.amount, req.reason, req.is_estimate, req.estimator_name
    )


@router.post("/15/instances/{instance_id}/ai-leveling")
def sop15_ai_leveling(instance_id: int, trade_name: str,
                      scope_summary: str = ""):
    _check_svc()
    try:
        return SOP15BidLevelingService.run_ai_leveling(
            instance_id, trade_name, scope_summary
        )
    except Exception as e:
        return {"status": "blocked", "message": str(e)}


@router.post("/15/instances/{instance_id}/submit-review")
def sop15_submit_review(instance_id: int, estimator_name: str):
    _check_svc()
    try:
        return SOP15BidLevelingService.submit_for_pm_review(instance_id, estimator_name)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/15/instances/{instance_id}/pm-approve")
def sop15_pm_approve(instance_id: int, pm_name: str):
    _check_svc()
    try:
        return SOP15BidLevelingService.pm_approve_leveling(instance_id, pm_name)
    except Exception as e:
        return {"status": "blocked", "message": str(e)}


@router.post("/15/instances/{instance_id}/award")
def sop15_buck_award(instance_id: int, req: SOP15AwardRequest):
    """Gate 15-C: Buck awards to a specific sub."""
    _check_svc()
    try:
        return SOP15BidLevelingService.record_buck_award(
            instance_id, req.awarded_sub, req.award_amount, req.scope_basis,
            req.rationale, req.risks_accepted, req.conditions, req.approver
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/15/instances/{instance_id}/hand-off-to-16")
def sop15_handoff(instance_id: int, actor: str, recipient_pm: str):
    _check_svc()
    try:
        return SOP15BidLevelingService.hand_off_to_sop16(
            instance_id, actor, recipient_pm
        )
    except Exception as e:
        return {"status": "blocked", "message": str(e)}


# ──────────────────────────────────────────────────────────────────────────────
# SOP 13 — Bid Distribution
# ──────────────────────────────────────────────────────────────────────────────

class SOP13StartRequest(BaseModel):
    project_id: int
    sop_11_instance_id: int
    owner_name: str
    bid_due_date: str


class SOP13LogSentRequest(BaseModel):
    sub_name: str
    trade_code: str
    contact_email: str
    method: str = "email"
    sent_date: str
    actor: str = "estimator"


class SOP13ConfirmReceiptRequest(BaseModel):
    sub_name: str
    confirmed_date: str
    actor: str = "estimator"


class SOP13CoverageCheckRequest(BaseModel):
    required_trades: List[str]


class SOP13HandoffRequest(BaseModel):
    actor: str
    project_id: int
    owner_name: str
    trade_name: str
    bid_due_date: str


@router.post("/13/instances")
def sop13_create(req: SOP13StartRequest):
    _check_svc()
    try:
        return SOP13BidDistributionService.start_distribution(
            req.project_id, req.sop_11_instance_id, req.owner_name, req.bid_due_date
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/13/instances/{instance_id}")
def sop13_get(instance_id: int):
    _check_svc()
    result = SOP13BidDistributionService.get_full_status(instance_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.post("/13/instances/{instance_id}/log-sent")
def sop13_log_sent(instance_id: int, req: SOP13LogSentRequest):
    _check_svc()
    return SOP13BidDistributionService.log_sub_sent(
        instance_id, req.sub_name, req.trade_code,
        req.contact_email, req.method, req.sent_date, req.actor
    )


@router.post("/13/instances/{instance_id}/confirm-receipt")
def sop13_confirm_receipt(instance_id: int, req: SOP13ConfirmReceiptRequest):
    _check_svc()
    return SOP13BidDistributionService.confirm_receipt(
        instance_id, req.sub_name, req.confirmed_date, req.actor
    )


@router.post("/13/instances/{instance_id}/ai-coverage-check")
def sop13_coverage_check(instance_id: int, req: SOP13CoverageCheckRequest):
    _check_svc()
    return SOP13BidDistributionService.run_ai_coverage_check(
        instance_id, req.required_trades
    )


@router.post("/13/instances/{instance_id}/flag-sub-risks")
def sop13_flag_risks(instance_id: int, trade_name: str):
    _check_svc()
    return SOP13BidDistributionService.flag_sub_risks(instance_id, trade_name)


@router.post("/13/instances/{instance_id}/pm-confirm")
def sop13_pm_confirm(instance_id: int, pm_name: str):
    _check_svc()
    try:
        return SOP13BidDistributionService.pm_confirm_distribution(instance_id, pm_name)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/13/instances/{instance_id}/hand-off-to-14")
def sop13_handoff(instance_id: int, req: SOP13HandoffRequest):
    """Trigger SOP 14 (Bid Follow-Up) from SOP 13 handoff."""
    _check_svc()
    try:
        return SOP13BidDistributionService.hand_off_to_sop14(
            instance_id, req.actor, req.project_id,
            req.owner_name, req.trade_name, req.bid_due_date
        )
    except Exception as e:
        raise HTTPException(400, str(e))


# ──────────────────────────────────────────────────────────────────────────────
# SOP 14 — Bid Follow-Up
# ──────────────────────────────────────────────────────────────────────────────

class SOP14StartRequest(BaseModel):
    project_id: int
    sop_13_instance_id: int
    owner_name: str
    trade_name: str
    bid_due_date: str


class SOP14LogFollowUpRequest(BaseModel):
    sub_name: str
    trade_code: str
    contact_email: str
    method: str = "email"
    follow_up_date: str
    actor: str = "estimator"


class SOP14UpdateResponseRequest(BaseModel):
    sub_name: str
    response_status: str
    response_date: str = ""
    notes: str = ""
    actor: str = "estimator"


class SOP14AISummaryRequest(BaseModel):
    trade_name: str
    bid_due_date: str


@router.post("/14/instances")
def sop14_create(req: SOP14StartRequest):
    _check_svc()
    try:
        return SOP14BidFollowUpService.start_followup(
            req.project_id, req.sop_13_instance_id,
            req.owner_name, req.trade_name, req.bid_due_date
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/14/instances/{instance_id}")
def sop14_get(instance_id: int):
    _check_svc()
    result = SOP14BidFollowUpService.get_full_status(instance_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.post("/14/instances/{instance_id}/follow-ups")
def sop14_log_follow_up(instance_id: int, req: SOP14LogFollowUpRequest):
    _check_svc()
    return SOP14BidFollowUpService.log_follow_up(
        instance_id, req.sub_name, req.trade_code,
        req.contact_email, req.method, req.follow_up_date, req.actor
    )


@router.post("/14/instances/{instance_id}/update-response")
def sop14_update_response(instance_id: int, req: SOP14UpdateResponseRequest):
    _check_svc()
    return SOP14BidFollowUpService.update_response_status(
        instance_id, req.sub_name, req.response_status,
        req.response_date, req.notes, req.actor
    )


@router.post("/14/instances/{instance_id}/ai-summary")
def sop14_ai_summary(instance_id: int, req: SOP14AISummaryRequest):
    _check_svc()
    return SOP14BidFollowUpService.run_ai_summary(
        instance_id, req.trade_name, req.bid_due_date
    )


@router.post("/14/instances/{instance_id}/close")
def sop14_close(instance_id: int, actor: str = "estimator"):
    _check_svc()
    return SOP14BidFollowUpService.close_followup(instance_id, actor)


@router.post("/14/instances/{instance_id}/hand-off-to-15")
def sop14_handoff(instance_id: int, actor: str,
                  sop_15_instance_id: Optional[int] = None):
    """Signal SOP 14 complete — ready for SOP 15 bid leveling."""
    _check_svc()
    try:
        return SOP14BidFollowUpService.hand_off_to_sop15(
            instance_id, actor, sop_15_instance_id
        )
    except Exception as e:
        return {"status": "blocked", "message": str(e)}


# ──────────────────────────────────────────────────────────────────────────────
# SOP 16 — Buyout
# ──────────────────────────────────────────────────────────────────────────────

class SOP16StartRequest(BaseModel):
    project_id: int
    sop_15_instance_id: int
    owner_name: str


class SOP16InputsRequest(BaseModel):
    awarded_sub: Optional[str] = None
    award_amount: Optional[float] = None
    scope_basis: Optional[str] = None
    trade_name: Optional[str] = None
    trade_code: Optional[str] = None
    subcontract_type: Optional[str] = None
    conditions: Optional[str] = None
    rationale: Optional[str] = None


class SOP16ConfirmScopeRequest(BaseModel):
    sub_scope_statement: str
    actor: str = "pm"


class SOP16InitiateSubcontractRequest(BaseModel):
    subcontract_type: str = "lump_sum"
    conditions: str = ""
    actor: str = "pm"


class SOP16HandoffRequest(BaseModel):
    actor: str
    recipient: str = "contracts_team"


@router.post("/16/instances")
def sop16_create(req: SOP16StartRequest):
    _check_svc()
    try:
        return SOP16BuyoutService.start_buyout(
            req.project_id, req.sop_15_instance_id, req.owner_name
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/16/instances/{instance_id}")
def sop16_get(instance_id: int):
    _check_svc()
    result = SOP16BuyoutService.get_full_status(instance_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.post("/16/instances/{instance_id}/inputs")
def sop16_set_inputs(instance_id: int, req: SOP16InputsRequest,
                     actor: str = "pm"):
    _check_svc()
    inputs = {k: v for k, v in req.dict().items() if v is not None}
    try:
        return SOP16BuyoutService.set_inputs(instance_id, inputs, actor)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/16/instances/{instance_id}/draft-award-memo")
def sop16_draft_memo(instance_id: int, actor: str = "pm"):
    """Layer 3: AI drafts the award memo. PM reviews before any issuance."""
    _check_svc()
    return SOP16BuyoutService.draft_award_memo(instance_id, actor)


@router.post("/16/instances/{instance_id}/confirm-scope")
def sop16_confirm_scope(instance_id: int, req: SOP16ConfirmScopeRequest):
    _check_svc()
    return SOP16BuyoutService.confirm_scope(
        instance_id, req.sub_scope_statement, req.actor
    )


@router.post("/16/instances/{instance_id}/initiate-subcontract")
def sop16_initiate_subcontract(instance_id: int, req: SOP16InitiateSubcontractRequest):
    _check_svc()
    try:
        return SOP16BuyoutService.initiate_subcontract(
            instance_id, req.subcontract_type, req.conditions, req.actor
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/16/instances/{instance_id}/pm-confirm")
def sop16_pm_confirm(instance_id: int, pm_name: str):
    """Gate 16-C: PM confirms buyout complete."""
    _check_svc()
    try:
        return SOP16BuyoutService.pm_confirm_buyout(instance_id, pm_name)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/16/instances/{instance_id}/hand-off-to-19")
def sop16_handoff(instance_id: int, req: SOP16HandoffRequest):
    """Hand off to SOP 19 (Subcontract Agreement)."""
    _check_svc()
    try:
        return SOP16BuyoutService.hand_off_to_sop19(
            instance_id, req.actor, req.recipient
        )
    except Exception as e:
        return {"status": "blocked", "message": str(e)}


# ──────────────────────────────────────────────────────────────────────────────
# SOP 12 — Subcontractor CRM
# ──────────────────────────────────────────────────────────────────────────────

class SOP12StartRequest(BaseModel):
    project_id: int
    trade_code: str
    trade_name: str
    sop_11_instance_id: int
    owner_name: str


class SOP12CandidateRequest(BaseModel):
    sub_name: str
    trade_code: str = ""
    contact_name: str = ""
    contact_email: str = ""
    contact_phone: str = ""
    license_number: str = ""
    bonded: bool = False
    insured: bool = False
    prequalified: bool = False
    performance_rating: str = "QUALIFIED"
    last_hci_project: str = ""
    notes: str = ""


class SOP12HandoffRequest(BaseModel):
    actor: str
    project_id: int
    owner_name: str
    bid_due_date: str
    sop_11_instance_id: int


@router.post("/12/bid-lists")
def sop12_create(req: SOP12StartRequest):
    _check_svc()
    try:
        return SOP12SubCRMService.start_bid_list(
            req.project_id, req.trade_code, req.trade_name,
            req.sop_11_instance_id, req.owner_name
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/12/bid-lists/{instance_id}")
def sop12_get(instance_id: int):
    _check_svc()
    result = SOP12SubCRMService.get_full_status(instance_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.post("/12/bid-lists/{instance_id}/candidates")
def sop12_add_candidate(instance_id: int, req: SOP12CandidateRequest,
                        actor: str = "estimator"):
    _check_svc()
    return SOP12SubCRMService.add_sub_candidate(instance_id, req.dict(), actor)


@router.post("/12/bid-lists/{instance_id}/ai-research")
def sop12_ai_research(instance_id: int, project_type: str = "commercial"):
    """Layer 3: AI searches vendor intelligence and auto-populates candidate list."""
    _check_svc()
    return SOP12SubCRMService.run_ai_research(instance_id, project_type)


@router.post("/12/bid-lists/{instance_id}/assess-candidate")
def sop12_assess_candidate(instance_id: int, sub_name: str):
    """AI qualification assessment for a specific sub candidate."""
    _check_svc()
    return SOP12SubCRMService.assess_sub(instance_id, sub_name)


@router.post("/12/bid-lists/{instance_id}/approve-sub")
def sop12_approve_sub(instance_id: int, sub_name: str, pm_name: str):
    """PM approves a single sub candidate for the bid list."""
    _check_svc()
    return SOP12SubCRMService.pm_approve_sub(instance_id, sub_name, pm_name)


@router.post("/12/bid-lists/{instance_id}/pm-approve")
def sop12_pm_approve_list(instance_id: int, pm_name: str):
    """PM finalizes and approves the complete bid list. Enforces MIN_BIDDERS (3)."""
    _check_svc()
    try:
        return SOP12SubCRMService.pm_approve_list(instance_id, pm_name)
    except Exception as e:
        return {"status": "blocked", "message": str(e)}


@router.post("/12/bid-lists/{instance_id}/hand-off-to-13")
def sop12_handoff(instance_id: int, req: SOP12HandoffRequest):
    """Trigger SOP 13 Distribution from approved sub list."""
    _check_svc()
    try:
        return SOP12SubCRMService.hand_off_to_sop13(
            instance_id, req.actor, req.project_id,
            req.owner_name, req.bid_due_date, req.sop_11_instance_id
        )
    except Exception as e:
        return {"status": "blocked", "message": str(e)}


# ──────────────────────────────────────────────────────────────────────────────
# SOP 19 — Subcontract Agreement
# ──────────────────────────────────────────────────────────────────────────────

class SOP19StartRequest(BaseModel):
    project_id: int
    sop_16_instance_id: int
    awarded_sub: str
    award_amount: float
    scope_basis: str
    trade_name: str
    trade_code: str
    owner_name: str


class SOP19DraftSectionRequest(BaseModel):
    section_type: str
    content: str = ""


class SOP19InsuranceRequest(BaseModel):
    general_liability: float = 0
    aggregate: float = 0
    workers_comp: float = 0
    auto_liability: float = 0


class SOP19ExecuteRequest(BaseModel):
    executed_by: str
    subcontract_number: str
    execution_date: Optional[str] = None


@router.post("/19/instances")
def sop19_create(req: SOP19StartRequest):
    _check_svc()
    try:
        return SOP19SubcontractAgreementService.start_agreement(
            req.project_id, req.sop_16_instance_id, req.awarded_sub,
            req.award_amount, req.scope_basis, req.trade_name,
            req.trade_code, req.owner_name
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/19/instances/{instance_id}")
def sop19_get(instance_id: int):
    _check_svc()
    result = SOP19SubcontractAgreementService.get_full_status(instance_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.post("/19/instances/{instance_id}/ai-draft")
def sop19_ai_draft_all(instance_id: int):
    """Layer 3: AI drafts all 7 standard contract sections at once."""
    _check_svc()
    return SOP19SubcontractAgreementService.run_ai_draft_all(instance_id)


@router.post("/19/instances/{instance_id}/sections")
def sop19_draft_section(instance_id: int, req: SOP19DraftSectionRequest,
                        actor: str = "pm"):
    """PM manually drafts or overrides a specific contract section."""
    _check_svc()
    return SOP19SubcontractAgreementService.draft_section(
        instance_id, req.section_type, req.content, actor
    )


@router.post("/19/instances/{instance_id}/confirm-section")
def sop19_confirm_section(instance_id: int, section_type: str, pm_name: str):
    """PM confirms a drafted section is acceptable."""
    _check_svc()
    return SOP19SubcontractAgreementService.confirm_section(
        instance_id, section_type, pm_name
    )


@router.post("/19/instances/{instance_id}/verify-insurance")
def sop19_verify_insurance(instance_id: int, req: SOP19InsuranceRequest):
    """Check sub insurance certificates against HCI minimums."""
    _check_svc()
    return SOP19SubcontractAgreementService.verify_insurance(
        instance_id, req.dict()
    )


@router.post("/19/instances/{instance_id}/ai-review")
def sop19_final_review(instance_id: int):
    """AI reviews all sections together for consistency before PM approval."""
    _check_svc()
    return SOP19SubcontractAgreementService.run_final_review(instance_id)


@router.post("/19/instances/{instance_id}/pm-approve")
def sop19_pm_approve(instance_id: int, pm_name: str):
    """PM routes complete subcontract draft to execution authority."""
    _check_svc()
    try:
        return SOP19SubcontractAgreementService.pm_approve(instance_id, pm_name)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/19/instances/{instance_id}/execute")
def sop19_execute(instance_id: int, req: SOP19ExecuteRequest):
    """Gate 19-C: Record subcontract execution. Principal or PM with written delegation required."""
    _check_svc()
    try:
        return SOP19SubcontractAgreementService.record_execution(
            instance_id, req.executed_by, req.subcontract_number, req.execution_date
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/19/instances/{instance_id}/archive")
def sop19_archive(instance_id: int, actor: str = "pm"):
    """Archive executed subcontract. Gate 19-C must be recorded first."""
    _check_svc()
    try:
        return SOP19SubcontractAgreementService.archive(instance_id, actor)
    except Exception as e:
        return {"status": "blocked", "message": str(e)}


# ──────────────────────────────────────────────────────────────────────────────
# SOP 17 — Project Schedule
# ──────────────────────────────────────────────────────────────────────────────

class SOP17StartRequest(BaseModel):
    project_id: int
    project_name: str
    project_type: str
    construction_start: str
    substantial_completion: str
    owner_name: str
    sop_23_instance_id: int = 0


class SOP17MilestoneRequest(BaseModel):
    milestone_code: str
    phase: str
    description: str
    planned_start: str
    planned_finish: str
    duration_days: int = 0
    float_days: int = 0
    critical_path: bool = False
    predecessor_codes: List[str] = []
    trade_codes: List[str] = []


class SOP17HandoffRequest(BaseModel):
    actor: str
    project_id: int
    owner_name: str


@router.post("/17/instances")
def sop17_create(req: SOP17StartRequest):
    _check_svc()
    try:
        return SOP17ProjectScheduleService.start_schedule(
            req.project_id, req.project_name, req.project_type,
            req.construction_start, req.substantial_completion,
            req.owner_name, req.sop_23_instance_id
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/17/instances/{instance_id}")
def sop17_get(instance_id: int):
    _check_svc()
    result = SOP17ProjectScheduleService.get_full_status(instance_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.post("/17/instances/{instance_id}/ai-schedule")
def sop17_ai_schedule(instance_id: int):
    """AI generates full schedule milestone list from project dates."""
    _check_svc()
    return SOP17ProjectScheduleService.run_ai_schedule(instance_id)


@router.post("/17/instances/{instance_id}/milestones")
def sop17_add_milestone(instance_id: int, req: SOP17MilestoneRequest, actor: str = "pm"):
    _check_svc()
    return SOP17ProjectScheduleService.add_milestone(instance_id, req.dict(), actor)


@router.post("/17/instances/{instance_id}/confirm-milestone")
def sop17_confirm_milestone(instance_id: int, milestone_code: str, pm_name: str):
    _check_svc()
    return SOP17ProjectScheduleService.pm_confirm_milestone(instance_id, milestone_code, pm_name)


@router.post("/17/instances/{instance_id}/pm-approve")
def sop17_pm_approve(instance_id: int, pm_name: str):
    _check_svc()
    try:
        return SOP17ProjectScheduleService.pm_approve(instance_id, pm_name)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/17/instances/{instance_id}/hand-off-to-18")
def sop17_handoff(instance_id: int, req: SOP17HandoffRequest):
    _check_svc()
    try:
        return SOP17ProjectScheduleService.hand_off_to_sop18(
            instance_id, req.actor, req.project_id, req.owner_name
        )
    except Exception as e:
        return {"status": "blocked", "message": str(e)}


# ──────────────────────────────────────────────────────────────────────────────
# SOP 18 — Long-Lead Procurement
# ──────────────────────────────────────────────────────────────────────────────

class SOP18StartRequest(BaseModel):
    project_id: int
    sop_17_instance_id: int
    owner_name: str
    project_type: str = ""
    construction_start: str = ""


class SOP18ItemRequest(BaseModel):
    item_code: str
    description: str
    trade_code: str = "GEN"
    lead_time_weeks: int = 4
    order_by_date: str = ""
    required_on_site: str = ""
    risk_level: str = "MEDIUM"
    notes: str = ""


@router.post("/18/instances")
def sop18_create(req: SOP18StartRequest):
    _check_svc()
    try:
        return SOP18LongLeadService.start_procurement_log(
            req.project_id, req.sop_17_instance_id, req.owner_name,
            req.project_type, req.construction_start
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/18/instances/{instance_id}")
def sop18_get(instance_id: int):
    _check_svc()
    result = SOP18LongLeadService.get_full_status(instance_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.post("/18/instances/{instance_id}/ai-identify")
def sop18_ai_identify(instance_id: int, narrative_summary: str = ""):
    """AI identifies long-lead items from project type and scope."""
    _check_svc()
    return SOP18LongLeadService.run_ai_identification(instance_id, narrative_summary)


@router.post("/18/instances/{instance_id}/items")
def sop18_add_item(instance_id: int, req: SOP18ItemRequest, actor: str = "pm"):
    _check_svc()
    return SOP18LongLeadService.add_long_lead_item(instance_id, req.dict(), actor)


@router.post("/18/instances/{instance_id}/update-status")
def sop18_update_status(instance_id: int, item_code: str, status: str, actor: str = "pm"):
    _check_svc()
    return SOP18LongLeadService.update_item_status(instance_id, item_code, status, actor)


@router.post("/18/instances/{instance_id}/pm-approve")
def sop18_pm_approve(instance_id: int, pm_name: str):
    _check_svc()
    try:
        return SOP18LongLeadService.pm_approve(instance_id, pm_name)
    except Exception as e:
        raise HTTPException(400, str(e))


# ──────────────────────────────────────────────────────────────────────────────
# SOP 20 — Contract Setup
# ──────────────────────────────────────────────────────────────────────────────

class SOP20StartRequest(BaseModel):
    project_id: int
    project_name: str
    contract_type: str
    owner_name_client: str
    gc_contract_value: float
    pm_name: str
    sop_19_instance_id: int = 0


class SOP20HandoffRequest(BaseModel):
    actor: str
    project_id: int
    owner_name: str
    jurisdiction: str


@router.post("/20/instances")
def sop20_create(req: SOP20StartRequest):
    _check_svc()
    try:
        return SOP20ContractSetupService.start_contract_setup(
            req.project_id, req.project_name, req.contract_type,
            req.owner_name_client, req.gc_contract_value,
            req.pm_name, req.sop_19_instance_id
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/20/instances/{instance_id}")
def sop20_get(instance_id: int):
    _check_svc()
    result = SOP20ContractSetupService.get_full_status(instance_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.post("/20/instances/{instance_id}/ai-checklist")
def sop20_ai_checklist(instance_id: int, scope_summary: str = ""):
    """AI generates contract setup checklist."""
    _check_svc()
    return SOP20ContractSetupService.run_ai_checklist(instance_id, scope_summary)


@router.post("/20/instances/{instance_id}/complete-item")
def sop20_complete_item(instance_id: int, item_code: str, actor: str = "pm"):
    _check_svc()
    return SOP20ContractSetupService.complete_item(instance_id, item_code, actor)


@router.post("/20/instances/{instance_id}/pm-approve")
def sop20_pm_approve(instance_id: int, pm_name: str):
    _check_svc()
    try:
        return SOP20ContractSetupService.pm_approve(instance_id, pm_name)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/20/instances/{instance_id}/hand-off-to-21")
def sop20_handoff(instance_id: int, req: SOP20HandoffRequest):
    _check_svc()
    try:
        return SOP20ContractSetupService.hand_off_to_sop21(
            instance_id, req.actor, req.project_id, req.owner_name, req.jurisdiction
        )
    except Exception as e:
        return {"status": "blocked", "message": str(e)}


# ──────────────────────────────────────────────────────────────────────────────
# SOP 21 — Compliance
# ──────────────────────────────────────────────────────────────────────────────

class SOP21StartRequest(BaseModel):
    project_id: int
    sop_20_instance_id: int
    owner_name: str
    jurisdiction: str
    project_type: str = ""


class SOP21PermitUpdateRequest(BaseModel):
    item_code: str
    status: str
    permit_number: str = ""


class SOP21HandoffRequest(BaseModel):
    actor: str
    project_id: int
    owner_name: str


@router.post("/21/instances")
def sop21_create(req: SOP21StartRequest):
    _check_svc()
    try:
        return SOP21ComplianceService.start_compliance_log(
            req.project_id, req.sop_20_instance_id, req.owner_name,
            req.jurisdiction, req.project_type
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/21/instances/{instance_id}")
def sop21_get(instance_id: int):
    _check_svc()
    result = SOP21ComplianceService.get_full_status(instance_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.post("/21/instances/{instance_id}/ai-identify")
def sop21_ai_identify(instance_id: int, scope_summary: str = "", contract_value: float = 0):
    """AI identifies compliance and permit requirements for jurisdiction."""
    _check_svc()
    return SOP21ComplianceService.run_ai_identification(instance_id, scope_summary, contract_value)


@router.post("/21/instances/{instance_id}/update-permit")
def sop21_update_permit(instance_id: int, req: SOP21PermitUpdateRequest, actor: str = "pm"):
    _check_svc()
    return SOP21ComplianceService.update_permit_status(
        instance_id, req.item_code, req.status, req.permit_number, actor
    )


@router.post("/21/instances/{instance_id}/pm-approve")
def sop21_pm_approve(instance_id: int, pm_name: str):
    _check_svc()
    try:
        return SOP21ComplianceService.pm_approve(instance_id, pm_name)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/21/instances/{instance_id}/hand-off-to-22")
def sop21_handoff(instance_id: int, req: SOP21HandoffRequest):
    _check_svc()
    try:
        return SOP21ComplianceService.hand_off_to_sop22(
            instance_id, req.actor, req.project_id, req.owner_name
        )
    except Exception as e:
        return {"status": "blocked", "message": str(e)}


# ──────────────────────────────────────────────────────────────────────────────
# SOP 22 — COI / W-9 / Lien Waiver
# ──────────────────────────────────────────────────────────────────────────────

class SOP22StartRequest(BaseModel):
    project_id: int
    sop_21_instance_id: int
    owner_name: str


class SOP22ChecklistRequest(BaseModel):
    subs: List[str]


class SOP22COIVerifyRequest(BaseModel):
    doc_code: str
    general_liability: float = 0
    aggregate: float = 0
    workers_comp: float = 0
    auto_liability: float = 0
    verifier: str


class SOP22HandoffRequest(BaseModel):
    actor: str
    project_id: int
    owner_name: str
    superintendent_name: str
    project_name: str
    project_type: str
    construction_start: str


@router.post("/22/instances")
def sop22_create(req: SOP22StartRequest):
    _check_svc()
    try:
        return SOP22COIService.start_doc_collection(
            req.project_id, req.sop_21_instance_id, req.owner_name
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/22/instances/{instance_id}")
def sop22_get(instance_id: int):
    _check_svc()
    result = SOP22COIService.get_full_status(instance_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.post("/22/instances/{instance_id}/generate-checklist")
def sop22_generate_checklist(instance_id: int, req: SOP22ChecklistRequest):
    """Generate COI/W-9/lien waiver checklist for all subs."""
    _check_svc()
    return SOP22COIService.generate_doc_checklist(instance_id, req.subs)


@router.post("/22/instances/{instance_id}/mark-received")
def sop22_mark_received(instance_id: int, doc_code: str, actor: str = "pm"):
    _check_svc()
    return SOP22COIService.mark_received(instance_id, doc_code, actor)


@router.post("/22/instances/{instance_id}/verify-coi")
def sop22_verify_coi(instance_id: int, req: SOP22COIVerifyRequest):
    """Verify COI coverage against HCI insurance minimums."""
    _check_svc()
    limits = {k: v for k, v in req.dict().items() if k not in ("doc_code", "verifier")}
    return SOP22COIService.verify_coi(instance_id, req.doc_code, limits, req.verifier)


@router.post("/22/instances/{instance_id}/pm-approve")
def sop22_pm_approve(instance_id: int, pm_name: str):
    _check_svc()
    try:
        return SOP22COIService.pm_approve(instance_id, pm_name)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/22/instances/{instance_id}/hand-off-to-23")
def sop22_handoff(instance_id: int, req: SOP22HandoffRequest):
    _check_svc()
    try:
        return SOP22COIService.hand_off_to_sop23(
            instance_id, req.actor, req.project_id, req.owner_name,
            req.superintendent_name, req.project_name,
            req.project_type, req.construction_start
        )
    except Exception as e:
        return {"status": "blocked", "message": str(e)}


# ──────────────────────────────────────────────────────────────────────────────
# SOP 23 — Project Startup
# ──────────────────────────────────────────────────────────────────────────────

class SOP23StartRequest(BaseModel):
    project_id: int
    sop_22_instance_id: int
    owner_name: str
    superintendent_name: str
    project_name: str
    project_type: str
    construction_start: str


class SOP23HandoffRequest(BaseModel):
    actor: str
    project_id: int
    owner_name: str


@router.post("/23/instances")
def sop23_create(req: SOP23StartRequest):
    _check_svc()
    try:
        return SOP23ProjectStartupService.start_startup(
            req.project_id, req.sop_22_instance_id, req.owner_name,
            req.superintendent_name, req.project_name,
            req.project_type, req.construction_start
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/23/instances/{instance_id}")
def sop23_get(instance_id: int):
    _check_svc()
    result = SOP23ProjectStartupService.get_full_status(instance_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.post("/23/instances/{instance_id}/ai-checklist")
def sop23_ai_checklist(instance_id: int):
    """AI generates full project startup checklist from project context."""
    _check_svc()
    return SOP23ProjectStartupService.run_ai_checklist(instance_id)


@router.post("/23/instances/{instance_id}/complete-item")
def sop23_complete_item(instance_id: int, item_code: str, actor: str = "superintendent"):
    _check_svc()
    return SOP23ProjectStartupService.complete_item(instance_id, item_code, actor)


@router.post("/23/instances/{instance_id}/pm-approve")
def sop23_pm_approve(instance_id: int, pm_name: str):
    _check_svc()
    try:
        return SOP23ProjectStartupService.pm_approve(instance_id, pm_name)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/23/instances/{instance_id}/hand-off-to-24")
def sop23_handoff(instance_id: int, req: SOP23HandoffRequest):
    _check_svc()
    try:
        return SOP23ProjectStartupService.hand_off_to_sop24(
            instance_id, req.actor, req.project_id, req.owner_name
        )
    except Exception as e:
        return {"status": "blocked", "message": str(e)}


# ──────────────────────────────────────────────────────────────────────────────
# SOP 24 — Superintendent Daily Dashboard
# ──────────────────────────────────────────────────────────────────────────────

class SOP24StartRequest(BaseModel):
    project_id: int
    sop_23_instance_id: int
    owner_name: str


class SOP24MetricRequest(BaseModel):
    metric_code: str
    label: str
    value: Any
    unit: str = ""
    category: str = "schedule"
    alert_level: str = "GREEN"
    date: str = ""
    notes: str = ""


@router.post("/24/instances")
def sop24_create(req: SOP24StartRequest):
    _check_svc()
    try:
        return SOP24SuperDashboardService.start_dashboard(
            req.project_id, req.sop_23_instance_id, req.owner_name
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/24/instances/{instance_id}")
def sop24_get(instance_id: int):
    _check_svc()
    result = SOP24SuperDashboardService.get_full_status(instance_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.post("/24/instances/{instance_id}/metrics")
def sop24_update_metric(instance_id: int, req: SOP24MetricRequest, actor: str = "superintendent"):
    _check_svc()
    return SOP24SuperDashboardService.update_metric(instance_id, req.dict(), actor)


@router.post("/24/instances/{instance_id}/daily-brief")
def sop24_daily_brief(instance_id: int, snap_date: str = ""):
    """AI generates daily brief from today's metrics."""
    _check_svc()
    return SOP24SuperDashboardService.generate_daily_brief(instance_id, snap_date)


# ──────────────────────────────────────────────────────────────────────────────
# SOP 25 — Daily Log
# ──────────────────────────────────────────────────────────────────────────────

class SOP25StartRequest(BaseModel):
    project_id: int
    sop_23_instance_id: int
    owner_name: str


class SOP25LogEntryRequest(BaseModel):
    log_date: str
    weather: str = "clear"
    temperature_high: Optional[int] = None
    temperature_low: Optional[int] = None
    total_workers: int = 0
    work_performed: str = ""
    materials_received: List[str] = []
    delays: List[str] = []
    safety_topics: List[str] = []
    incidents: List[str] = []
    rfis_submitted: List[str] = []
    inspectors_on_site: List[str] = []
    visitors: List[str] = []
    photos_taken: int = 0
    notes: str = ""


@router.post("/25/instances")
def sop25_create(req: SOP25StartRequest):
    _check_svc()
    try:
        return SOP25DailyLogService.start_log(
            req.project_id, req.sop_23_instance_id, req.owner_name
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/25/instances/{instance_id}")
def sop25_get(instance_id: int):
    _check_svc()
    result = SOP25DailyLogService.get_full_status(instance_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.post("/25/instances/{instance_id}/entries")
def sop25_create_entry(instance_id: int, req: SOP25LogEntryRequest,
                       actor: str = "superintendent"):
    """Create a daily log entry and run AI risk analysis."""
    _check_svc()
    return SOP25DailyLogService.create_entry(instance_id, req.dict(), actor)


@router.post("/25/instances/{instance_id}/close-day")
def sop25_close_day(instance_id: int, log_date: str, actor: str = "superintendent"):
    _check_svc()
    return SOP25DailyLogService.close_day(instance_id, log_date, actor)


@router.get("/25/instances/{instance_id}/weekly-summary")
def sop25_weekly_summary(instance_id: int, week_start: str):
    """AI-generated weekly progress summary."""
    _check_svc()
    return SOP25DailyLogService.get_weekly_summary(instance_id, week_start)


# ──────────────────────────────────────────────────────────────────────────────
# SOP 26 — Field Coordination
# ──────────────────────────────────────────────────────────────────────────────

class SOP26StartRequest(BaseModel):
    project_id: int
    sop_23_instance_id: int
    owner_name: str


class SOP26ItemRequest(BaseModel):
    item_code: str
    coord_type: str
    description: str
    priority: str = "NORMAL"
    trade_codes: List[str] = []
    drawing_refs: List[str] = []
    spec_refs: List[str] = []
    date_needed: str = ""
    notes: str = ""


@router.post("/26/instances")
def sop26_create(req: SOP26StartRequest):
    _check_svc()
    try:
        return SOP26FieldCoordService.start_coordination(
            req.project_id, req.sop_23_instance_id, req.owner_name
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/26/instances/{instance_id}")
def sop26_get(instance_id: int):
    _check_svc()
    result = SOP26FieldCoordService.get_full_status(instance_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.post("/26/instances/{instance_id}/items")
def sop26_add_item(instance_id: int, req: SOP26ItemRequest, actor: str = "pm"):
    _check_svc()
    return SOP26FieldCoordService.add_item(instance_id, req.dict(), actor)


@router.post("/26/instances/{instance_id}/draft-response")
def sop26_draft_response(instance_id: int, item_code: str):
    """AI drafts RFI response from historical and spec data."""
    _check_svc()
    return SOP26FieldCoordService.draft_response(instance_id, item_code)


@router.post("/26/instances/{instance_id}/close-item")
def sop26_close_item(instance_id: int, item_code: str, resolution: str = "", actor: str = "pm"):
    _check_svc()
    return SOP26FieldCoordService.close_item(instance_id, item_code, resolution, actor)


# ──────────────────────────────────────────────────────────────────────────────
# SOP 27 — Quality Control
# ──────────────────────────────────────────────────────────────────────────────

class SOP27StartRequest(BaseModel):
    project_id: int
    project_type: str
    sop_23_instance_id: int
    owner_name: str


class SOP27ResultRequest(BaseModel):
    item_code: str
    result: str
    inspector: str
    inspection_date: str
    deficiency_notes: str = ""
    severity: str = "MINOR"


@router.post("/27/instances")
def sop27_create(req: SOP27StartRequest):
    _check_svc()
    try:
        return SOP27QualityControlService.start_qc(
            req.project_id, req.project_type, req.sop_23_instance_id, req.owner_name
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/27/instances/{instance_id}")
def sop27_get(instance_id: int):
    _check_svc()
    result = SOP27QualityControlService.get_full_status(instance_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.post("/27/instances/{instance_id}/generate-checklist")
def sop27_generate_checklist(instance_id: int, trade_code: str, category: str, spec_section: str = ""):
    """AI generates QC inspection checklist for a trade/category."""
    _check_svc()
    return SOP27QualityControlService.generate_checklist(instance_id, trade_code, category, spec_section)


@router.post("/27/instances/{instance_id}/record-result")
def sop27_record_result(instance_id: int, req: SOP27ResultRequest):
    _check_svc()
    return SOP27QualityControlService.record_result(
        instance_id, req.item_code, req.result, req.inspector,
        req.inspection_date, req.deficiency_notes, req.severity
    )


# ──────────────────────────────────────────────────────────────────────────────
# SOP 28 — QC Detail Card
# ──────────────────────────────────────────────────────────────────────────────

class SOP28StartRequest(BaseModel):
    project_id: int
    trade_code: str
    trade_name: str
    sop_27_instance_id: int
    owner_name: str
    spec_sections: List[str] = []


@router.post("/28/instances")
def sop28_create(req: SOP28StartRequest):
    _check_svc()
    try:
        return SOP28QCDetailCardService.start_detail_card(
            req.project_id, req.trade_code, req.trade_name,
            req.sop_27_instance_id, req.owner_name, req.spec_sections
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/28/instances/{instance_id}")
def sop28_get(instance_id: int):
    _check_svc()
    result = SOP28QCDetailCardService.get_full_status(instance_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.post("/28/instances/{instance_id}/ai-draft")
def sop28_ai_draft(instance_id: int, project_type: str = "commercial", spec_sections: List[str] = []):
    """AI drafts QC detail card work items for a trade."""
    _check_svc()
    return SOP28QCDetailCardService.run_ai_draft(instance_id, project_type, spec_sections)


@router.post("/28/instances/{instance_id}/confirm-item")
def sop28_confirm_item(instance_id: int, work_item_code: str, pm_name: str):
    _check_svc()
    return SOP28QCDetailCardService.confirm_work_item(instance_id, work_item_code, pm_name)


@router.post("/28/instances/{instance_id}/pm-approve")
def sop28_pm_approve(instance_id: int, pm_name: str):
    _check_svc()
    try:
        return SOP28QCDetailCardService.pm_approve(instance_id, pm_name)
    except Exception as e:
        raise HTTPException(400, str(e))


# ──────────────────────────────────────────────────────────────────────────────
# SOP 29 — Safety
# ──────────────────────────────────────────────────────────────────────────────

class SOP29StartRequest(BaseModel):
    project_id: int
    project_type: str
    superintendent_name: str
    sop_23_instance_id: int
    owner_name: str
    scope_summary: str = ""


class SOP29ControlRequest(BaseModel):
    hazard_code: str
    controls: List[str]


@router.post("/29/instances")
def sop29_create(req: SOP29StartRequest):
    _check_svc()
    try:
        return SOP29SafetyService.start_safety_plan(
            req.project_id, req.project_type, req.superintendent_name,
            req.sop_23_instance_id, req.owner_name, req.scope_summary
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/29/instances/{instance_id}")
def sop29_get(instance_id: int):
    _check_svc()
    result = SOP29SafetyService.get_full_status(instance_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.post("/29/instances/{instance_id}/ai-safety-plan")
def sop29_ai_plan(instance_id: int, scope_summary: str = "", site_conditions: str = ""):
    """AI generates comprehensive safety hazard plan for project type."""
    _check_svc()
    return SOP29SafetyService.run_ai_safety_plan(instance_id, scope_summary, site_conditions)


@router.post("/29/instances/{instance_id}/control-hazard")
def sop29_control_hazard(instance_id: int, req: SOP29ControlRequest, actor: str = "superintendent"):
    _check_svc()
    return SOP29SafetyService.control_hazard(instance_id, req.hazard_code, req.controls, actor)


@router.post("/29/instances/{instance_id}/pm-approve")
def sop29_pm_approve(instance_id: int, pm_name: str):
    """Safety plan approval — blocks if CRITICAL hazards uncontrolled."""
    _check_svc()
    try:
        return SOP29SafetyService.pm_approve(instance_id, pm_name)
    except Exception as e:
        raise HTTPException(400, str(e))


# ──────────────────────────────────────────────────────────────────────────────
# SOP 30 — Inspection
# ──────────────────────────────────────────────────────────────────────────────

class SOP30StartRequest(BaseModel):
    project_id: int
    jurisdiction: str
    sop_21_instance_id: int
    owner_name: str


class SOP30ScheduleRequest(BaseModel):
    inspection_type: str
    permit_number: str
    scheduled_date: str
    description: str = ""


class SOP30ResultRequest(BaseModel):
    inspection_code: str
    result: str
    inspector_name: str
    inspection_date: str
    correction_items: List[str] = []


@router.post("/30/instances")
def sop30_create(req: SOP30StartRequest):
    _check_svc()
    try:
        return SOP30InspectionService.start_inspection_log(
            req.project_id, req.jurisdiction, req.sop_21_instance_id, req.owner_name
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/30/instances/{instance_id}")
def sop30_get(instance_id: int):
    _check_svc()
    result = SOP30InspectionService.get_full_status(instance_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.post("/30/instances/{instance_id}/schedule")
def sop30_schedule(instance_id: int, req: SOP30ScheduleRequest, actor: str = "pm"):
    """Schedule an inspection and generate AI prep checklist."""
    _check_svc()
    return SOP30InspectionService.schedule_inspection(
        instance_id, req.inspection_type, req.permit_number,
        req.scheduled_date, req.description, actor
    )


@router.post("/30/instances/{instance_id}/record-result")
def sop30_record_result(instance_id: int, req: SOP30ResultRequest, actor: str = "superintendent"):
    """Record inspection result. FAIL triggers SC-03 stop event."""
    _check_svc()
    return SOP30InspectionService.record_result(
        instance_id, req.inspection_code, req.result,
        req.inspector_name, req.inspection_date, req.correction_items, actor
    )


# ──────────────────────────────────────────────────────────────────────────────
# Cross-SOP: Approval Queue and Dashboard
# ──────────────────────────────────────────────────────────────────────────────

@router.get("/approvals/pending")
def pending_approvals(project_id: Optional[int] = None):
    """All SOP instances awaiting approval (status = 'Approval Required')."""
    _check_svc()
    try:
        import services.db as db
        params = ["Approval Required"]
        where = "WHERE status = %s"
        if project_id:
            where += " AND project_id = %s"
            params.append(project_id)
        rows = db.query(f"""
            SELECT id, project_id, sop_number, status, owner_name,
                   status_changed_at, target_issue_date
            FROM sop_instances {where}
            ORDER BY status_changed_at
        """, params)
        return {"pending_approvals": [dict(r) for r in rows]}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/stop-events/active")
def active_stop_events(project_id: Optional[int] = None):
    """All unresolved stop events across all projects."""
    _check_svc()
    try:
        import services.db as db
        params: list = []
        join = ""
        where = "WHERE se.resolved_at IS NULL"
        if project_id:
            join = "JOIN sop_instances si ON si.id = se.sop_instance_id"
            where += " AND si.project_id = %s"
            params.append(project_id)
        rows = db.query(f"""
            SELECT se.id, se.sop_instance_id, se.condition_code,
                   se.blocker_description, se.resolution_path, se.triggered_at
            FROM sop_stop_events se {join} {where}
            ORDER BY se.triggered_at
        """, params or None)
        return {"active_stop_events": [dict(r) for r in rows]}
    except Exception as e:
        raise HTTPException(500, str(e))

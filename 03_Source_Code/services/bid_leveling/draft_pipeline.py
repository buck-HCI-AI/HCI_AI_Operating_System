"""
Draft-mode bid leveling pipeline — Buck's decision 2026-07-16 ("draft-mode with
validation gates first"), resolving a real disagreement between BC (wire the
proven bid_extractor/bid_level_analyzer pipeline straight to WF-007 production)
and GBT (called that "the most dangerous recommendation" given the pipeline's
real failure history — wrong folder pointers, contamination, false completions
— and proposed draft-mode + hard validation gates instead).

This module is the connective tissue GBT described: given a project+division
with current is_latest bids in drive_bids, run them through the already-proven
extraction/leveling AI pipeline (bid_extractor.py, bid_level_analyzer.py — both
independently matched human judgment on real Div 03/Div 07 1355R bids the night
of 2026-07-15/16), apply hard validation gates, and either write a clearly
labeled DRAFT Google Doc or route to the approval queue with the specific
failure reason. Never writes to the canonical Google Sheet Bid Tracker — that
remains a human-reviewed, human-triggered action.
"""
import sys, os, re, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "integrations"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "drive_intelligence"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "plan_reading"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "approval_queue"))

import psycopg2, psycopg2.extras
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

from drive_bid_reader import _is_outbound_not_a_bid
from bid_extractor import extract_bid
from bid_level_analyzer import analyze_bid_leveling
from budget_generator import generate_bid_leveling_gold_standard
from drive_client import create_google_doc_from_markdown
from approval_queue_service import ApprovalQueueService

DB = dict(
    host=os.environ.get("POSTGRES_HOST", "localhost"),
    port=int(os.environ.get("POSTGRES_PORT", 5432)),
    dbname=os.environ.get("POSTGRES_DB", "hci_os"),
    user=os.environ.get("POSTGRES_USER", "hci_admin"),
    password=os.environ.get("POSTGRES_PASSWORD", ""),
)


def _pg():
    return psycopg2.connect(cursor_factory=psycopg2.extras.RealDictCursor, **DB)


def _gate_fail(reason: str, detail: dict, project_id: int, division_num: str) -> dict:
    """Every gate failure routes to the same approval queue built earlier
    tonight, rather than silently dropping or guessing - a human reviews the
    specific reason, not a raw error."""
    result = ApprovalQueueService.enqueue(
        workflow="draft_bid_pipeline", action_type="leveling_validation_failed",
        target_system="drive_bids", target_id=f"{project_id}:{division_num}",
        target_description=f"Draft leveling gate failed for division {division_num}: {reason}",
        proposed_payload={}, reason=reason, project_id=project_id,
        actor="draft_pipeline", priority="normal", source_data=detail,
    )
    return {"status": "gate_failed", "reason": reason, "detail": detail,
            "queue_id": result.get("queue_id")}


def generate_draft_leveling(project_id: int, division_num: str, division_folder_id: str,
                             division_name: str = None) -> dict:
    """
    Draft-mode, validation-gated: reads current is_latest bids for one
    division, runs the proven AI pipeline, and either writes a clearly
    labeled DRAFT Google Doc into division_folder_id or fails a gate and
    routes to the approval queue. Never touches the canonical Sheet tracker.
    """
    with _pg() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM projects WHERE id=%s", (project_id,))
            proj = cur.fetchone()
            if not proj:
                return {"status": "error", "reason": f"project {project_id} not found"}

            cur.execute("""
                SELECT id, division_num, division_name, vendor_name, file_id, file_name,
                       bid_amount, bid_date
                FROM drive_bids
                WHERE project_id=%s AND division_num=%s AND is_latest=TRUE
                ORDER BY vendor_name
            """, (project_id, division_num))
            bids = [dict(r) for r in cur.fetchall()]

    if not bids:
        return _gate_fail("no is_latest bids found for this project+division", {}, project_id, division_num)

    div_name = division_name or bids[0]["division_name"] or division_num

    # Gate 1 — contamination: every file must not match the known
    # not-a-bid filename pattern (the fix behind BL-DEFECT-05 tonight).
    contaminated = [b for b in bids if _is_outbound_not_a_bid(b["file_name"] or "")]
    if contaminated:
        return _gate_fail(
            "contamination gate failed - outbound/summary artifact classified as a vendor bid",
            {"contaminated_files": [b["file_name"] for b in contaminated]},
            project_id, division_num,
        )

    # Gate 2 — project/division match: every row must actually belong to
    # the requested project+division (defends against the cross-project
    # contamination pattern found earlier this session).
    mismatched = [b for b in bids if b["division_num"] != division_num]
    if mismatched:
        return _gate_fail(
            "project/division match gate failed - row division_num does not match requested division",
            {"mismatched": [{"file": b["file_name"], "division_num": b["division_num"]} for b in mismatched]},
            project_id, division_num,
        )

    # Gate 3 — source freshness: bid_date required and not implausible.
    today = datetime.date.today()
    stale_or_missing = [b for b in bids if not b["bid_date"] or b["bid_date"] > today]
    if stale_or_missing:
        return _gate_fail(
            "source freshness gate failed - missing or future-dated bid_date",
            {"files": [b["file_name"] for b in stale_or_missing]},
            project_id, division_num,
        )

    # Extraction — real AI calls, Gemini-primary/Claude-fallback, same
    # proven pipeline as the overnight 2026-07-15/16 run.
    extracted_bids = {}
    extraction_errors = []
    for b in bids:
        result = extract_bid(b["file_id"])
        if result.get("error") or "extracted" not in result:
            extraction_errors.append({"vendor": b["vendor_name"], "file": b["file_name"],
                                       "error": result.get("error")})
            continue
        ext = result["extracted"]
        if not ext.get("total_amount"):
            extraction_errors.append({"vendor": b["vendor_name"], "file": b["file_name"],
                                       "error": "extraction succeeded but total_amount is missing"})
            continue
        extracted_bids[b["vendor_name"]] = ext

    # Gate 4 — extraction completeness: every bid must extract cleanly.
    if extraction_errors:
        return _gate_fail(
            "extraction completeness gate failed",
            {"errors": extraction_errors, "extracted_ok": list(extracted_bids.keys())},
            project_id, division_num,
        )

    single_bidder = len(extracted_bids) == 1
    scope_matrix, rfis, exclusions = [], [], {}
    biggest_risk = {
        "question": "N/A — single bidder, no competitive comparison to derive a risk from.",
        "dollar_at_stake": "$0",
        "explanation": "Only one real bid exists for this division/package; a scope-gap risk finding "
                        "requires at least two bids to compare.",
    }

    if not single_bidder:
        analysis_result = analyze_bid_leveling(extracted_bids, div_name, div_name)
        if analysis_result.get("error") or "analysis" not in analysis_result:
            return _gate_fail(
                "leveling analysis gate failed",
                {"error": analysis_result.get("error")}, project_id, division_num,
            )
        analysis = analysis_result["analysis"]
        # Gate 5 — analysis completeness.
        if not analysis.get("scope_matrix") or not analysis.get("biggest_risk"):
            return _gate_fail(
                "analysis completeness gate failed - scope_matrix or biggest_risk missing",
                {"analysis_keys": list(analysis.keys())}, project_id, division_num,
            )
        scope_matrix = analysis["scope_matrix"]
        biggest_risk = analysis["biggest_risk"]
        rfis = analysis.get("rfis", [])
        exclusions = analysis.get("exclusions_by_bidder", {})

    bidders = [{"name": v, "total": d.get("total_amount")} for v, d in extracted_bids.items()]
    recommendation = {
        "text": "No award recommendation — pending human review.",
        "reasoning": "DRAFT — auto-generated, not yet reviewed. No award recommendation is made by this "
                     "pipeline; a human must review the scope matrix and biggest-risk finding before any "
                     "award decision." if not single_bidder else
                     "DRAFT — single bidder, no competitive comparison possible. Human review required "
                     "before treating this as a leveled package.",
    }

    markdown = generate_bid_leveling_gold_standard(
        project_name=proj["name"], division_num=division_num, division_name=div_name,
        bidders=bidders, scope_matrix=scope_matrix, biggest_risk=biggest_risk,
        rfis=rfis, recommendation=recommendation, exclusions=exclusions,
    )
    markdown = (f"**STATUS: DRAFT — AUTO-GENERATED {datetime.date.today().isoformat()} — "
                f"PENDING HUMAN REVIEW — NOT YET VALIDATED**\n\n" + markdown)

    doc_name = f"DRAFT_AUTO_Div{division_num}_{div_name}_{datetime.date.today().isoformat()}"
    doc_result = create_google_doc_from_markdown(doc_name, division_folder_id, markdown)

    return {
        "status": "draft_created", "project": proj["name"], "division_num": division_num,
        "division_name": div_name, "bidders": [b["name"] for b in bidders],
        "single_bidder": single_bidder, "gates_passed": 4 if single_bidder else 5,
        "doc_id": doc_result.get("id"), "doc_name": doc_result.get("name"),
        "doc_link": f"https://drive.google.com/file/d/{doc_result.get('id')}/view",
        "canonical_tracker_touched": False,
    }

"""
SOW and bid-invite email generation - general system capability, gap #5 from
GBT's pre-start gap review (msg b19308e3, 2026-07-15). Pure template/formatting
functions: given structured scope input, produce a properly formatted SOW
document and matching bid-invite email. Does not write to Drive or read plan
PDFs itself - scope content is supplied by the caller (e.g. from a
plan-derived scope register, once that pipeline exists - gap #3, not yet
built). This closes the "we have no way to generate a SOW at all" gap without
overreaching into "AI autonomously interprets construction plans," which is a
separate, larger, higher-risk capability not attempted here.
"""
from datetime import date


def generate_sow(project_name: str, package_name: str, send_to: str, purpose: str,
                  base_scope_items: list, clarifications: list = None,
                  exclusions: list = None, required_proposal_format: list = None,
                  division_num: str = None, division_name: str = None,
                  bid_due_date: str = None, special_notes: list = None) -> str:
    """
    Returns a formatted markdown Scope of Work document.

    Rewritten 2026-07-16 to match the real, verified narrative-SOW pattern
    found at 275 Sunnyside (275_Sunnyside_Open_Scope_ITB_SOWs.docx, authored
    by Chris Hendrickson) - the only genuinely human-authored SOW pattern
    found across 101 Francis, 1355 Riverside, and 275 Sunnyside; everything
    else matching "SOW" naming turned out to be AI-generated placeholders.
    That document's 12 trade SOWs are all structured identically: Send to /
    Purpose / Base Scope to Price / Clarifications Required in Proposal /
    Exclude Unless Specifically Included / Required Proposal Format. This
    function reproduces that exact section structure rather than the
    previous generic Scope Description/Inclusions/Exclusions layout, which
    didn't match anything real.

    project_name: e.g. "275 Sunnyside Lane"
    package_name: trade/scope name, e.g. "Fireplaces"
    send_to: who this SOW is addressed to, e.g. "Fireplace vendor / specialty hearth contractor"
    purpose: 1-2 sentence statement of what pricing is being requested and why
    base_scope_items: list of narrative scope description strings - the core
        of the SOW, as exhaustive as the real plan/spec content supports
    clarifications: list of questions the bidder must answer in their proposal
        (drives apples-to-apples comparison during bid leveling)
    exclusions: list of items explicitly NOT included unless stated otherwise
    required_proposal_format: list of what the proposal itself must contain
        (e.g. "Lump sum with detailed breakout by area/type", "Price by location")
    division_num, division_name: optional HCI division reference for the header
    bid_due_date: optional "YYYY-MM-DD" string
    special_notes: optional list of project-specific notes (access, phasing, etc)
    """
    clarifications = clarifications or []
    exclusions = exclusions or []
    required_proposal_format = required_proposal_format or []
    special_notes = special_notes or []
    today = date.today().isoformat()

    division_prefix = f"Division {division_num} {division_name} — " if division_num else ""
    lines = [
        f"# {project_name} — {division_prefix}{package_name}",
        "## Scope of Work",
        "",
        f"Send to: {send_to}",
        "",
        f"Purpose: {purpose}",
        "",
        f"**Issued:** {today}" + (f"  |  **Bid Due:** {bid_due_date}" if bid_due_date else ""),
        "",
        "## Base Scope to Price",
    ]
    for item in base_scope_items:
        lines.append(f"- {item}")

    if clarifications:
        lines += ["", "## Clarifications Required in Proposal"]
        lines += [f"- {c}" for c in clarifications]

    if exclusions:
        lines += ["", "## Exclude Unless Specifically Included"]
        lines += [f"- {e}" for e in exclusions]

    if special_notes:
        lines += ["", "### Notes"]
        lines += [f"- {n}" for n in special_notes]

    if required_proposal_format:
        lines += ["", "## Required Proposal Format"]
        lines += [f"- {r}" for r in required_proposal_format]

    return "\n".join(lines)


def generate_bid_invite_email(project_name: str, project_location: str, division_name: str,
                               package_name: str, vendor_name: str, reference_docs: list,
                               scope_items: list, bid_due_date: str = None,
                               inclusions_prompt: bool = True,
                               contact_name: str = "Buck Adams",
                               contact_title: str = "Superintendent",
                               contact_phone: str = "720-346-4654",
                               contact_email: str = "buck@hendricksoninc.com",
                               pm_cc_email: str = None) -> dict:
    """
    Returns {"subject": str, "body": str, "cc": list} for a bid-invite email.

    pm_cc_email: per HCI_HubSpot_Bidding_SOP.pdf (SOP-01, step 8) - "Ensure
    the Project Manager is CC'd on all emails" is a documented requirement,
    not optional. Pass the project's PM email to populate cc; omitted (None)
    leaves cc empty rather than guessing a PM.

    Rewritten 2026-07-16 to match the real, live pattern found across Buck's
    own sent bid-request emails (pulled via Graph API from Sent Items, not
    reconstructed from Drive templates - see Structural/Steel, Rough &
    Finish Carpentry, and Landscaping/Irrigation/Hardscape requests). Real
    structure, consistent across trades: one-line scope identification ->
    bulleted links to the actual bid documents -> a catch-all completeness
    clause -> an exhaustive trade-specific "specifically include, verify,
    and price" narrative -> bid instructions -> signature block. Previous
    version was a generic 4-line summary that didn't match anything Buck
    actually sends, and defaulted contact_email to the wrong domain
    (buck@ahmaspen.com instead of buck@hendricksoninc.com) - fixed here.

    reference_docs: list of {"label": str, "url": str} - the real bid
        folder, SOW doc/spreadsheet, plans, structural drawings, schedule,
        etc. (Buck links these directly rather than attaching everything).
    scope_items: list of detailed, trade-specific narrative strings - the
        "please specifically include, verify, and price" bullets. Should be
        as exhaustive as the real plan/spec content supports; this is the
        single biggest driver of bid quality/completeness in every real
        example found (a short vague scope list gets a weak first bid; a
        long specific one gets a strong one on the first pass).
    inclusions_prompt: append the standard ask for inclusions/exclusions,
        assumptions, alternates, lead times (present in every real example).
    """
    subject = f"{project_name} – Request for Bid – {package_name}"

    doc_lines = "\n".join(f"{d['label']}: {d['url']}" for d in reference_docs)
    scope_lines = "\n".join(f"- {item}" for item in scope_items)

    due_line = f"\n\nPlease submit your bid by {bid_due_date}." if bid_due_date else ""
    inclusions_block = (
        "\n\nPlease also confirm:\n"
        "- Inclusions and exclusions\n"
        "- Assumptions, allowances, and alternates\n"
        "- Lead times / material availability\n"
        "- Any RFIs or clarifications needed before finalizing"
        if inclusions_prompt else ""
    )

    body = (
        f"Hi {vendor_name},\n\n"
        f"Hendrickson Construction is requesting a bid for the {package_name} scope "
        f"for the {project_name} project in {project_location}.\n\n"
        f"Please review the following bid documents:\n{doc_lines}\n\n"
        f"Please provide pricing for all {package_name.lower()} scope shown, noted, "
        f"scheduled, specified, or reasonably inferred from the bid documents.\n\n"
        f"Please specifically include, verify, and price the following scope:\n{scope_lines}"
        f"{inclusions_block}"
        f"{due_line}\n\n"
        f"Please respond to this email directly to ensure our systems recognize it "
        f"has been received and route it to the correct place for leveling.\n\n"
        f"Thanks,\n{contact_name}\n{contact_title}\nHendrickson Construction, Inc.\n"
        f"Cell: {contact_phone}\n{contact_email}"
    )
    return {"subject": subject, "body": body, "cc": [pm_cc_email] if pm_cc_email else []}


def generate_potential_rfis_output(project_name: str, candidates: list) -> str:
    """
    Returns a formatted markdown document listing potential RFIs surfaced by
    a deep multi-document plan read - the first-pass deliverable from that
    step (BC's Template Build Audit item 2, format confirmed 2026-07-15 P0).
    This is NOT a real RFI yet - just the candidate list Buck reviews to
    decide which questions become actual RFIs (via the real RFI pipeline in
    rfi_workflow.py). Pure template/formatting function: the caller supplies
    the candidates (from the plan-read step, not yet built - gap #3).

    candidates: list of dicts, each with:
      division: str - division/discipline (e.g. "07 - Thermal & Moisture")
      source: str - plan sheet number or spec section the question came from
      question: str - the single clear question
      why_it_matters: str - what's ambiguous, conflicting, or missing
      confidence: str - "definite gap" or "worth flagging"
    """
    lines = [
        f"# Potential RFIs from Plan Read — {project_name}",
        "",
        "First-pass output from the deep multi-document plan read. These are "
        "NOT real RFIs — review and decide which become actual RFIs (built "
        "via the real RFI pipeline, one question per RFI, per HCI standard).",
        "",
        f"Generated: {date.today().isoformat()} | {len(candidates)} candidate(s)",
        "",
        "| # | Division | Source | Question | Why It Matters | Confidence |",
        "|---|----------|--------|----------|-----------------|------------|",
    ]
    for i, c in enumerate(candidates, 1):
        lines.append(
            f"| {i} | {c.get('division', '')} | {c.get('source', '')} | "
            f"{c.get('question', '')} | {c.get('why_it_matters', '')} | "
            f"{c.get('confidence', '')} |"
        )
    return "\n".join(lines)

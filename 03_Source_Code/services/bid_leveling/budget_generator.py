"""
Bid-leveling-to-budget pipeline - the connective layer Buck asked for
("we want it all to flow together"), modeled directly on the real, live
practice found at 275 Sunnyside Lane (HCI's largest project, run by Chris
Hendrickson - confirmed 2026-07-16 as the company's model to follow).

Real evidence this is built on:
- 275_Sunnyside_GMP_Bid_Leveling.xlsx: Div / Trade / Vendor / Quote # /
  Bid Date / Bid Amount / Recommended Carry / Notes-Key Risks. Chris does
  NOT auto-pick the lowest bid - e.g. Div 07 Roofing carried Green Point
  $909,599 over CQ Roofing's lower $472,065, flagged "not apples-to-apples."
  So this module never auto-selects a recommended_carry value; it's always
  a human judgment call supplied by the caller, matching both Chris's real
  practice and the standing rule that AI doesn't approve awards.
- 275_Sunnyside_Master_Budget_v4_1.xlsx: Cost Code / Description /
  Original Budget / Budget Modifications / Revised Budget, using 5-digit
  CSI MasterFormat cost codes (e.g. 03300, 07710).

Pure template/computation functions - no Drive/DB I/O, same design as
sow_generator.py. Caller supplies the data; this module formats and rolls
it up.
"""


def build_bid_leveling_row(division_num: str, trade: str, vendor: str,
                            bid_amount: float, quote_number: str = "",
                            bid_date: str = "", recommended_carry: float = None,
                            notes: str = "") -> dict:
    """
    One row matching Sunnyside's real bid-leveling column structure.

    recommended_carry: the amount to carry into the budget for this trade.
    Leave None until a human (PM/estimator) makes the call - do not default
    this to bid_amount or the lowest bid across vendors. Chris's real sheet
    shows carries that are NOT the lowest bid when scope isn't apples-to-
    apples; auto-picking low bid here would silently misrepresent that
    judgment call as automated when it isn't.
    """
    return {
        "division": division_num,
        "trade": trade,
        "vendor": vendor,
        "quote_number": quote_number,
        "bid_date": bid_date,
        "bid_amount": bid_amount,
        "recommended_carry": recommended_carry,
        "notes": notes,
    }


def flag_bid_spread(rows: list, threshold_pct: float = 25.0) -> list:
    """
    Given multiple bid_leveling rows for the SAME trade, flag when the
    spread between high and low bid exceeds threshold_pct - a real signal
    (seen in the Sunnyside data, e.g. Green Point vs CQ Roofing at ~93%
    spread) that scope may not be comparable and needs a clarification
    email before a recommended_carry is set. Does not set recommended_carry
    itself - only surfaces the flag for a human to act on.

    Returns the same rows with an added "spread_flag" key (str or None).
    """
    if len(rows) < 2:
        for r in rows:
            r["spread_flag"] = None
        return rows

    amounts = [r["bid_amount"] for r in rows if r.get("bid_amount")]
    if not amounts:
        return rows
    low, high = min(amounts), max(amounts)
    spread_pct = ((high - low) / low * 100) if low else 0

    for r in rows:
        r["spread_flag"] = (
            f"Spread {spread_pct:.0f}% across {len(rows)} bids - verify scope "
            f"alignment before treating low bid as apples-to-apples."
            if spread_pct > threshold_pct else None
        )
    return rows


def build_budget_line(cost_code: str, description: str, original_budget: float,
                       budget_modifications: float = 0.0) -> dict:
    """One row matching Sunnyside's real budget column structure. Revised
    Budget = Original Budget + Budget Modifications, exactly as in
    275_Sunnyside_Master_Budget_v4_1.xlsx (e.g. Div 02 Site Work
    $3.75M + $1.175M = $4.925M)."""
    return {
        "cost_code": cost_code,
        "description": description,
        "original_budget": original_budget,
        "budget_modifications": budget_modifications,
        "revised_budget": original_budget + budget_modifications,
    }


def carry_to_budget_modification(bid_leveling_row: dict, budget_line: dict) -> dict:
    """
    The actual crosswalk: takes a bid-leveling row with a human-set
    recommended_carry and applies it as a Budget Modification against the
    matching budget line, producing the updated Revised Budget. This is the
    mechanical version of what Chris currently reconciles by hand between
    his two separate spreadsheets.

    Raises if recommended_carry hasn't been set - this function should only
    run after a human has made the award/carry decision, never before.
    """
    carry = bid_leveling_row.get("recommended_carry")
    if carry is None:
        raise ValueError(
            f"No recommended_carry set for {bid_leveling_row.get('trade')} - "
            f"this is a human judgment call, not an automated one. Set it "
            f"before calling carry_to_budget_modification()."
        )
    new_modifications = carry - budget_line["original_budget"]
    return build_budget_line(
        budget_line["cost_code"], budget_line["description"],
        budget_line["original_budget"], new_modifications,
    )


def generate_bid_leveling_gold_standard(project_name: str, division_num: str, division_name: str,
                                         bidders: list, scope_matrix: list,
                                         biggest_risk: dict, rfis: list,
                                         recommendation: dict, exclusions: dict = None) -> str:
    """
    The REAL, Buck-approved bid-leveling format (2026-07-13, "BID LEVELING
    GOLD STANDARD - BUCK APPROVED FORMAT", marked P0, "Standard approved by
    Buck Adams. Effective immediately.") - found 2026-07-16 while checking
    whether the Sunnyside-based summary this file previously used actually
    matched what the team had already agreed on. It didn't; this replaces
    it. Real worked example on file: 1355R Div 03 Concrete, TJ Concrete
    $162,505 vs High Con $158,375 - TJ recommended despite being $4,130
    higher because High Con's proposal omits underpinning (a real $44,680
    scope gap), which the scope matrix below is built to catch.

    Rules from the approved standard, enforced by this function's shape
    (not just described in a docstring):
    - Never compare bids as equivalent when scope differs (Rule 1) - the
      scope_matrix parameter forces per-item inclusion/exclusion, not just
      a total.
    - Dollar-value every gap where possible (Rule 2).
    - biggest_risk is a required parameter, not optional (Rule 3).
    - recommendation must include reasoning, not just a vendor name (Rule 4)
      - this function does not compute a recommendation itself; the caller
      (a human, per the standing rule that AI doesn't approve awards) must
      supply the reasoning text.
    - rfis is a required list - the standard prohibits recommending award
      without first surfacing open questions (Rule 5).

    bidders: list of {"name": str, "total": float}
    scope_matrix: list of {"item": str, "bidder_status": {bidder_name: "included"|"excluded"|str qualifier},
                            "amount_by_bidder": {bidder_name: float or None}, "why_it_matters": str (optional)}
    biggest_risk: {"question": str, "dollar_at_stake": str, "explanation": str}
    rfis: list of question strings
    recommendation: {"text": str, "reasoning": str}
    """
    lines = [
        f"# {project_name} — Division {division_num} {division_name} — Bid Leveling",
        "",
        "**Status: DRAFT — FOR BUCK'S REVIEW — NO AWARDS COMMITTED**",
        "",
        "## 1. Executive Summary",
        "",
        "| Contractor | Total |",
        "|---|---|",
    ]
    for b in sorted(bidders, key=lambda x: x["total"]):
        lines.append(f"| {b['name']} | ${b['total']:,.2f} |")
    totals = [b["total"] for b in bidders]
    if len(totals) >= 2:
        diff = max(totals) - min(totals)
        lines.append(f"\n**Spread:** ${diff:,.2f}")
    lines.append(
        "\n**Apples-to-apples:** NOT apples-to-apples until the scope gaps below are "
        "resolved via the RFIs in Section 6." if scope_matrix else ""
    )

    lines += ["", "## 2. Scope Comparison Matrix", ""]
    bidder_names = [b["name"] for b in bidders]
    lines.append("| Item | " + " | ".join(bidder_names) + " |")
    lines.append("|---|" + "---|" * len(bidder_names))
    for row in scope_matrix:
        cells = []
        for name in bidder_names:
            status = row["bidder_status"].get(name, "?")
            amount = row.get("amount_by_bidder", {}).get(name)
            mark = "✅" if status == "included" else ("❌" if status == "excluded" else status)
            cells.append(f"{mark}" + (f" ${amount:,.0f}" if amount else ""))
        lines.append(f"| {row['item']} | " + " | ".join(cells) + " |")

    section_num = 3
    for name in bidder_names:
        others = [n for n in bidder_names if n != name]
        gaps = [r for r in scope_matrix if r["bidder_status"].get(name) == "included"
                and any(r["bidder_status"].get(o) == "excluded" for o in others)]
        if gaps:
            lines += ["", f"## {section_num}. Items {name} Includes That Others Do Not", ""]
            for g in gaps:
                amt = g.get("amount_by_bidder", {}).get(name)
                lines.append(f"- {g['item']}" + (f" — ${amt:,.2f}" if amt else "") +
                             (f" — {g['why_it_matters']}" if g.get("why_it_matters") else ""))
            section_num += 1

    exclusions = exclusions or {}
    if exclusions:
        lines += ["", f"## {section_num}. Exclusions — Each Bidder", ""]
        for name in bidder_names:
            items = exclusions.get(name, [])
            if items:
                lines.append(f"\n**{name}:**")
                lines += [f"- {e}" for e in items]
        section_num += 1

    lines += ["", f"## {section_num}. Biggest Risk", ""]
    lines.append(f"**{biggest_risk['question']}**")
    lines.append(f"\nDollars at stake: {biggest_risk['dollar_at_stake']}")
    lines.append(f"\n{biggest_risk['explanation']}")
    section_num += 1

    lines += ["", f"## {section_num}. RFIs to Send Before Award", ""]
    for i, rfi in enumerate(rfis, 1):
        # AI analysis sometimes returns {"bidder": ..., "question": ...} instead
        # of a plain string - handle both rather than print a raw dict repr.
        if isinstance(rfi, dict):
            bidder = rfi.get("bidder")
            question = rfi.get("question") or rfi.get("rfi") or rfi.get("text") or str(rfi)
            lines.append(f"{i}. [{bidder}] {question}" if bidder else f"{i}. {question}")
        else:
            lines.append(f"{i}. {rfi}")
    section_num += 1

    lines += ["", f"## {section_num}. Recommendation", ""]
    lines.append(recommendation["text"])
    lines.append(f"\n{recommendation['reasoning']}")

    return "\n".join(l for l in lines if l is not None)


def generate_division_bid_leveling_summary(project_name: str, division_num: str, division_name: str,
                                            bid_leveling_rows: list, budget_line: dict = None) -> str:
    """
    Real division-level bid-leveling summary output - what the bid-leveling
    exercise is actually supposed to produce (Buck, 2026-07-16): not just a
    vendor comparison table, but a narrative calling out real risks - like a
    bid range sitting far below/above the budget baseline, which usually
    means a scope mismatch, not real savings. Found live on 1355R Div 07
    Roofing: real bids ($153,900-$196,931) sat ~80% under the real ROM
    budget ($999,250) - too large a gap to be a normal buyout win, and
    exactly the kind of thing this function exists to catch and put in the
    actual summary doc rather than leaving it as a verbal aside.

    budget_line is optional - pass one (from build_budget_line) when a real
    baseline is known, to get the budget-comparison section; omit it for a
    plain bid comparison when no baseline exists yet.
    """
    lines = [
        f"# {project_name} — Division {division_num} {division_name} — Bid Leveling Summary",
        "",
        "## Bids Received",
        "",
        "| Vendor | Quote # | Bid Date | Amount |",
        "|---|---|---|---|",
    ]
    for r in sorted(bid_leveling_rows, key=lambda x: x["bid_amount"] or 0):
        lines.append(
            f"| {r['vendor']} | {r.get('quote_number','')} | {r.get('bid_date','')} | "
            f"${r['bid_amount']:,.2f} |"
        )

    amounts = [r["bid_amount"] for r in bid_leveling_rows if r.get("bid_amount")]
    if amounts:
        low, high = min(amounts), max(amounts)
        lines += ["", f"**Bid range:** ${low:,.2f} – ${high:,.2f}"]

    spread_flag = next((r.get("spread_flag") for r in bid_leveling_rows if r.get("spread_flag")), None)
    if spread_flag:
        lines += ["", f"**Risk flag:** {spread_flag}"]

    if budget_line and amounts:
        orig = budget_line["original_budget"]
        low, high = min(amounts), max(amounts)
        lines += [
            "",
            "## Budget Comparison",
            "",
            f"**Budget baseline ({budget_line['cost_code']}):** ${orig:,.2f}",
            f"**Bids vs. budget:** received bids range ${orig - high:,.2f} to "
            f"${orig - low:,.2f} {'under' if orig > high else 'relative to'} the baseline.",
        ]
        variance_pct = ((orig - low) / orig * 100) if orig else 0
        if abs(variance_pct) > 15:
            direction = "under" if orig > low else "over"
            lines.append(
                f"**Scope-gap risk:** bids sit {abs(variance_pct):.0f}% {direction} the "
                f"budget baseline - large enough to suggest a scope mismatch (missing "
                f"package items, an allowance not carried, or the budget overstated) "
                f"rather than a straightforward buyout win. Verify scope coverage against "
                f"the budget's line-item basis before treating this as savings."
            )

    lines += ["", "## Notes / Key Risks"]
    any_notes = [r["notes"] for r in bid_leveling_rows if r.get("notes")]
    lines += [f"- {n}" for n in any_notes] if any_notes else ["- None recorded yet."]

    return "\n".join(lines)


def generate_budget_summary_markdown(project_name: str, budget_lines: list) -> str:
    """
    Simple, readable markdown summary - per Buck's explicit principle: "still
    be simple enough to read for myself and other PMs making decisions."
    Not the full spreadsheet (that stays in Excel/Sheets); this is the quick
    scan version - one line per division, running total at the bottom.
    """
    total_original = sum(l["original_budget"] for l in budget_lines)
    total_revised = sum(l["revised_budget"] for l in budget_lines)
    variance = total_revised - total_original
    variance_pct = (variance / total_original * 100) if total_original else 0

    lines = [
        f"# {project_name} — Budget Summary",
        "",
        "| Cost Code | Description | Original | Modifications | Revised |",
        "|---|---|---|---|---|",
    ]
    for l in sorted(budget_lines, key=lambda x: x["cost_code"]):
        lines.append(
            f"| {l['cost_code']} | {l['description']} | "
            f"${l['original_budget']:,.0f} | ${l['budget_modifications']:+,.0f} | "
            f"${l['revised_budget']:,.0f} |"
        )
    lines += [
        "",
        f"**Total Original Budget:** ${total_original:,.0f}  ",
        f"**Total Revised Budget:** ${total_revised:,.0f}  ",
        f"**Variance:** ${variance:+,.0f} ({variance_pct:+.1f}%)",
    ]
    return "\n".join(lines)

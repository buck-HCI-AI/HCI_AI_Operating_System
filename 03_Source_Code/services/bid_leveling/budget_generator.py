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
                                         recommendation: dict, exclusions: dict = None,
                                         line_items_by_bidder: dict = None) -> str:
    """
    Format changed 2026-07-17 per Buck's direct request: he wants the clean,
    executive-scannable structure of his own reference doc
    (Copy of 1355_Riverside_Concrete_Bid_Leveling_Summary.pdf - status line,
    simple bid table, prose executive summary, itemized cost breakdown, $-
    valued scope grid). Same-day follow-up ("keep some of the old info too,
    just format to the new one - more info the better"): the numbered
    sections, the standalone Biggest Risk section (Question / Dollars at
    Stake / Explanation as distinct labeled fields, not folded into a single
    Executive Summary sentence), and the per-bidder "Items X Includes That
    Others Do Not" prose call-outs (with the why-it-matters context) all
    existed in the pre-2026-07-17 version and are restored here, merged into
    the new structure rather than replacing it - the goal is more real
    information, not a shorter document. Section numbers are computed here,
    not hardcoded by any caller - a stale hardcoded "Section 6" reference
    was a real bug fixed earlier this session and must not recur.
    The underlying safety rules are unchanged: scope gaps still get
    dollar-valued, biggest_risk and RFIs are still required, no award
    recommendation is computed by this function (a human supplies
    recommendation.reasoning, matching the standing rule that AI doesn't
    approve awards).

    bidders: list of {"name": str, "total": float}
    scope_matrix: list of {"item": str, "bidder_status": {bidder_name: "included"|"excluded"|str qualifier},
                            "amount_by_bidder": {bidder_name: float or None}, "why_it_matters": str (optional)}
    biggest_risk: {"question": str, "dollar_at_stake": str, "explanation": str}
    rfis: list of question strings
    recommendation: {"text": str, "reasoning": str}
    line_items_by_bidder: {bidder_name: [{"item": str, "amount": float, "unit_rate": str (optional)}, ...]}
        - real extracted line items per bidder, already produced by
          bid_extractor.py but not previously surfaced in the final doc.
    """
    bidder_names = [b["name"] for b in bidders]
    sorted_bidders = sorted(bidders, key=lambda x: x["total"])
    low_bidder = sorted_bidders[0]["name"] if sorted_bidders else None

    # Real scope-completeness signal per bidder, used for both the status
    # column and to decide the overall status line - not a fixed label.
    gap_count = {}
    for name in bidder_names:
        others = [n for n in bidder_names if n != name]
        missing = [r for r in scope_matrix if r["bidder_status"].get(name) == "excluded"
                   and any(r["bidder_status"].get(o) == "included" for o in others)]
        gap_count[name] = len(missing)

    # P0 audit fix 2026-07-21: an EMPTY scope_matrix means scope was never
    # analyzed (single bidder, or a fast/skip-extraction run) - it must NOT be
    # reported as "Complete Scope"/"Ready for Review". A completeness claim
    # requires real scope analysis to have happened.
    scope_analyzed = len(scope_matrix) > 0
    single_bidder = len(bidders) <= 1

    # P0 audit fix 2026-07-21: enforce financial reconciliation - a bidder whose
    # stated total does not match the sum of its own extracted line items is
    # surfaced, not silently accepted. Tolerance: $1 or 0.5% of the stated total.
    unreconciled = {}
    for b in bidders:
        items = line_items_by_bidder.get(b["name"]) or []
        li_sum = sum(li.get("amount") or 0 for li in items
                     if isinstance(li.get("amount"), (int, float)))
        if items and b.get("total") and abs(li_sum - b["total"]) > max(1.0, 0.005 * abs(b["total"])):
            unreconciled[b["name"]] = li_sum

    if single_bidder:
        overall_status = "Single Bid — No Competitive Comparison"  # precedence: nothing to compare, so "not analyzed" is misleading
    elif not scope_analyzed:
        overall_status = "Scope Not Analyzed — Review Required"
    elif any(gap_count.values()):
        overall_status = "Scope Clarification Required"
    else:
        overall_status = "Ready for Review"
    if unreconciled:
        overall_status += f" · {len(unreconciled)} bid(s) not reconciled to line items"

    # Section numbers are assigned as sections are actually emitted (below),
    # not fixed in advance - some sections (Itemized Cost Breakdown, RFIs,
    # Exclusions) are conditional on real data being present.
    section_num = [0]
    def heading(title: str) -> str:
        section_num[0] += 1
        return f"## {section_num[0]}. {title}"

    lines = [
        f"# {project_name}",
        f"## {division_name} Bid Leveling Summary",
        f"**Status:** {overall_status}",
        "",
        "*DRAFT — for review, no awards committed*",
        "",
        heading("Bid Summary"),
        "",
        "| Contractor | Bid Amount | Status |",
        "|---|---|---|",
    ]
    for b in sorted_bidders:
        if single_bidder:
            status = "Single bid — no comparison"
        elif not scope_analyzed:
            status = "Scope not analyzed"          # never claim completeness w/o analysis
        elif b["name"] == low_bidder and gap_count.get(b["name"]):
            status = "Lowest Bid*"
        elif gap_count.get(b["name"], 0) == 0:
            status = "Single bid" if single_bidder else "Complete Scope"
        else:
            status = f"{gap_count[b['name']]} scope gap(s)"
        if b["name"] in unreconciled:
            status += f" · ⚠ total ≠ line items (${unreconciled[b['name']]:,.2f})"
        lines.append(f"| {b['name']} | ${b['total']:,.2f} | {status} |")
    totals = [b["total"] for b in bidders]
    if len(totals) >= 2:
        lines.append(f"\n*Spread: ${max(totals) - min(totals):,.2f}*")
    if gap_count.get(low_bidder):
        lines.append("\n*Lowest price appears to have less defined scope and should be verified before award.*")

    lines += ["", heading("Executive Summary"), ""]
    # Kept tight and non-overlapping - found 2026-07-17 the first version of
    # this concatenated the low-bidder sentence AND the full biggest_risk
    # explanation, which itself often restates the same scope-gap details
    # (both talk about what the low bidder excludes) - read as repetitive.
    # Explanation goes in the Biggest Risk callout below instead of being
    # duplicated here; the exec summary states the question, not the reasoning.
    exec_parts = []
    if low_bidder:
        exec_parts.append(f"{low_bidder} submitted the apparent low bid at ${bidders[0]['total']:,.2f}."
                           if bidders[0]["name"] == low_bidder else
                           f"{low_bidder} submitted the apparent low bid.")
    complete = [n for n in bidder_names if gap_count.get(n, 0) == 0 and n != low_bidder]
    if complete:
        exec_parts.append(f"{', '.join(complete)} submitted proposals with more completely "
                           f"defined scope than the low bid.")
    if biggest_risk and biggest_risk.get("question"):
        exec_parts.append(f"Key open question before award: {biggest_risk['question']}")
    if any(gap_count.values()):
        exec_parts.append("Scope clarification is recommended before award — see the itemized "
                           "breakdown and comparison below.")
    lines.append(" ".join(exec_parts) if exec_parts else "No scope gaps identified across bidders.")

    if biggest_risk and (biggest_risk.get("question") or biggest_risk.get("explanation")):
        lines += ["", heading("Biggest Risk"), ""]
        if biggest_risk.get("question"):
            lines.append(f"**{biggest_risk['question']}**")
        lines.append(f"\nDollars at stake: {biggest_risk.get('dollar_at_stake', 'amount not quantified')}")
        if biggest_risk.get("explanation"):
            lines.append(f"\n{biggest_risk['explanation']}")

    if line_items_by_bidder:
        lines += ["", heading("Itemized Cost Breakdown"), ""]
        # Split base scope from priced alternates/adds - found 2026-07-17:
        # TJ Concrete's real line items included several "ADD:" optional
        # upgrade items that aren't part of their base bid total, so summing
        # every listed line item produced a number ($173,690) that didn't
        # match their actual bid ($162,505) - looked like an error even
        # though both numbers were individually correct. Alternates are real
        # information (an available upgrade and its price), just not part of
        # the number being compared against other bidders.
        for name in bidder_names:
            items = line_items_by_bidder.get(name) or []
            if not items:
                continue
            base_items = [it for it in items if not str(it.get("item", "")).strip().upper().startswith("ADD")]
            alt_items = [it for it in items if str(it.get("item", "")).strip().upper().startswith("ADD")]
            lines += [f"### {name}", "", "| Item | Amount |", "|---|---|"]
            for it in base_items:
                amt = it.get("amount")
                lines.append(f"| {it.get('item', '')} | " + (f"${amt:,.2f}" if amt is not None else "—") + " |")
            base_total = sum(it.get("amount") or 0 for it in base_items)
            lines.append(f"\n**Base scope total:** ${base_total:,.2f}")
            if alt_items:
                lines += ["", "**Alternates / Optional Adds (not included in base total above):**", ""]
                for it in alt_items:
                    amt = it.get("amount")
                    lines.append(f"- {it.get('item', '')}" + (f" — ${amt:,.2f}" if amt is not None else ""))
            lines.append("")

    lines += ["", heading("Scope Comparison"), "", "| Scope | " + " | ".join(bidder_names) + " |",
              "|---|" + "---|" * len(bidder_names)]
    for row in scope_matrix:
        cells = []
        for name in bidder_names:
            status = row["bidder_status"].get(name, "Not Listed")
            amount = row.get("amount_by_bidder", {}).get(name)
            if status == "included":
                cell = f"${amount:,.0f}" if amount else "Yes"
            elif status == "excluded":
                cell = "No"
            else:
                cell = status if isinstance(status, str) else "Not Listed"
            cells.append(cell)
        lines.append(f"| {row['item']} | " + " | ".join(cells) + " |")

    # Restored from the pre-2026-07-17 format at Buck's request ("keep the
    # old info too") - the Scope Comparison table shows WHAT differs; this
    # shows WHY it matters, per bidder, in prose. Real example: TJ Concrete
    # is the only bidder to price underpinning - the matrix row shows that,
    # this section explains the consequence of the other three omitting it.
    for name in bidder_names:
        others = [n for n in bidder_names if n != name]
        unique_items = [r for r in scope_matrix if r["bidder_status"].get(name) == "included"
                         and any(r["bidder_status"].get(o) == "excluded" for o in others)]
        if unique_items:
            lines += ["", f"### Items {name} Includes That Others Do Not", ""]
            for it in unique_items:
                amt = it.get("amount_by_bidder", {}).get(name)
                lines.append(f"- {it['item']}" + (f" — ${amt:,.2f}" if amt else "") +
                             (f" — {it['why_it_matters']}" if it.get("why_it_matters") else ""))

    if rfis:
        lines += ["", heading("RFIs to Send Before Award"), ""]
        for i, rfi in enumerate(rfis, 1):
            # AI analysis sometimes returns {"bidder": ..., "question": ...}
            # instead of a plain string - handle both rather than print a raw
            # dict repr.
            if isinstance(rfi, dict):
                bidder = rfi.get("bidder")
                question = rfi.get("question") or rfi.get("rfi") or rfi.get("text") or str(rfi)
                lines.append(f"{i}. [{bidder}] {question}" if bidder else f"{i}. {question}")
            else:
                lines.append(f"{i}. {rfi}")

    exclusions = exclusions or {}
    if exclusions:
        lines += ["", "## Exclusions — Each Bidder", ""]
        for name in bidder_names:
            items = exclusions.get(name, [])
            if items:
                lines.append(f"\n**{name}:**")
                lines += [f"- {e}" for e in items]

    lines += ["", "## Recommendation", ""]
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
    from collections import defaultdict
    # SUB-PACKAGE-AWARE (2026-07-21): a division like Electrical has distinct
    # sub-scopes (Electric power vs Low Voltage/AV) whose bids must NOT be lumped
    # into one range. Found live on 1355R Div 16: lumping made a $21k AV bid read
    # as a "10%-of-budget partial" next to $451k power bids. We group by `trade`
    # (the sub-package) and level WITHIN each, then reconcile a division "coverage"
    # (sum of lowest bid per sub-package) to the budget. Coverage is analysis only,
    # never an auto-carry (carries stay a human decision per build_bid_leveling_row).
    groups = defaultdict(list)
    for r in bid_leveling_rows:
        groups[r.get("trade") or division_name].append(r)
    multi = len(groups) > 1

    lines = [f"# {project_name} — Division {division_num} {division_name} — Bid Leveling Summary", ""]
    if multi:
        lines += [f"_This division has {len(groups)} sub-packages; bids are leveled within each "
                  f"(never compared across different scopes)._", ""]

    coverage_low = 0.0  # sum of lowest bid per sub-package = division coverage
    for sub in sorted(groups):
        rows = groups[sub]
        amounts = [r["bid_amount"] for r in rows if r.get("bid_amount")]
        lines += [(f"## {sub}" if multi else "## Bids Received"), "",
                  "| Vendor | Quote # | Bid Date | Amount |", "|---|---|---|---|"]
        for r in sorted(rows, key=lambda x: x["bid_amount"] or 0):
            lines.append(f"| {r['vendor']} | {r.get('quote_number','')} | {r.get('bid_date','')} | "
                         f"${(r['bid_amount'] or 0):,.2f} |")
        if amounts:
            low, high = min(amounts), max(amounts)
            coverage_low += low
            lines += ["", f"**Bid range:** ${low:,.2f} – ${high:,.2f}"]
            if len(amounts) > 1 and high > 0 and (high - low) / high * 100 > 25:
                lines.append(f"**Spread flag:** {((high-low)/high*100):.0f}% spread within this "
                             f"sub-package — verify scope comparability before an award.")
        sf = next((r.get("spread_flag") for r in rows if r.get("spread_flag")), None)
        if sf:
            lines += ["", f"**Risk flag:** {sf}"]
        lines.append("")

    if budget_line and coverage_low:
        orig = budget_line["original_budget"]
        pct = round(100 * coverage_low / orig) if orig else None
        lines += ["## Budget Comparison", "",
                  f"**Budget baseline ({budget_line['cost_code']}):** ${orig:,.2f}",
                  f"**Coverage (sum of lowest bid per sub-package):** ${coverage_low:,.2f}"
                  + (f" = {pct}% of budget" if pct is not None else "")]
        if orig:
            variance_pct = (orig - coverage_low) / orig * 100
            if variance_pct > 25:
                lines.append(f"**Coverage gap:** sub-package bids cover only {100 - variance_pct:.0f}% of "
                             f"the budget line — remaining sub-scopes likely not yet bid (need coverage), "
                             f"NOT savings. Do not treat as a buyout win.")
            elif variance_pct < -15:
                lines.append(f"**Over baseline:** coverage is {abs(variance_pct):.0f}% over the budget "
                             f"line — the budget cost-code may be a stub/under-set; verify against real bids.")
        lines.append("")

    lines += ["## Notes / Key Risks"]
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


def generate_rom_reconciliation_table(project_name: str, rom_source: str, rows: list) -> str:
    """
    Buck's explicit request, 2026-07-17: "a high & low column - with a notes
    section - just to see where we are compared to the original rom given."
    Turns the ad-hoc ROM-vs-actual comparison messages posted individually
    per division tonight (Div 03, 06, 09) into one reusable, structured
    table - the notes column is exactly where real scope caveats belong
    (e.g. a bidder's number being unverified, or covering a narrower/wider
    scope than the ROM line) instead of a wall of prose per division.

    rows: list of {
        "division": str, "rom_estimate": float,
        "low_bid": float, "low_bidder": str,
        "high_bid": float, "high_bidder": str,
        "notes": str,
    }
    No carry/award decision is made here - this is a real-numbers
    reconciliation view only, matching the standing rule that this system
    never picks a winning bid.

    Deliberately no auto-computed "spread vs ROM" column: found live while
    building this that a raw ROM-minus-low-bid number can be actively
    misleading when the low bid covers a narrower real scope than the ROM
    line (Div 09 Flooring: low bid is carpet-only, not comparable to the
    ROM's whole-house flooring estimate - a spread computed against it
    would read as huge real savings that aren't real). Whether a number is
    a fair comparison is exactly the judgment this system doesn't make -
    that context belongs in Notes, written by a human or by real, verified
    per-bid analysis, not derived by blindly subtracting the lowest number.
    """
    lines = [
        f"# {project_name} — ROM Reconciliation",
        f"*Comparing real received bids against {rom_source}. No carry or award decision made here.*",
        "",
        "| Division | ROM Estimate | Low Bid | High Bid | Notes |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['division']} | ${r['rom_estimate']:,.0f} | ${r['low_bid']:,.0f} ({r['low_bidder']}) | "
            f"${r['high_bid']:,.0f} ({r['high_bidder']}) | {r.get('notes', '')} |"
        )
    return "\n".join(lines)


def generate_stack_up_summary_table(project_name: str, plan_set_note: str, rows: list) -> str:
    """
    Modeled on 275 Sunnyside's real "Takeoff Summary" tab (275_Sunnyside_Workbook.xlsx) -
    Chris Hendrickson's practice of estimating each division as a Low/Mid/High
    range with a plain-language "Primary Scope Drivers" note, rather than a
    single-point figure. Real example from that tab: Div 06 Wood & Carpentry
    is $5.3M-$7.3M ("LVL/TJI/framing + Accoya cladding + oak trim + custom
    cabinets"), not a single number - the range itself is the real estimate,
    same as how 1355R's own REAL_ROM_2026-07-16 carries a Low/Target/High
    on its all-in total ($4.67M-$7.24M) even though its per-division detail
    section only ever gave point figures. This function extends that same
    range-based practice down to the division level, distinct from
    generate_rom_reconciliation_table() (which compares a single ROM point
    against real received bids, post-bids-in-hand). This one is for the
    pre-bid stack-up itself - what a PM publishes as the working estimate
    range before bids exist to compare against.

    rows: list of {
        "division": str, "description": str,
        "low": float, "mid": float, "high": float,
        "scope_drivers": str,
    }
    No carry/award decision, no fabricated single-point "true cost" - the
    range is the estimate. Totals are summed per column, not averaged,
    matching Sunnyside's own TOTAL row.
    """
    lines = [
        f"# {project_name} — Stack-Up Summary",
        f"*{plan_set_note}*",
        "",
        "| Div | Description | Low | Mid | High | Primary Scope Drivers |",
        "|---|---|---|---|---|---|",
    ]
    total_low = total_mid = total_high = 0.0
    for r in rows:
        total_low += r["low"]
        total_mid += r["mid"]
        total_high += r["high"]
        lines.append(
            f"| {r['division']} | {r['description']} | ${r['low']:,.0f} | ${r['mid']:,.0f} | "
            f"${r['high']:,.0f} | {r.get('scope_drivers', '')} |"
        )
    lines += [
        f"| **TOTAL** | | **${total_low:,.0f}** | **${total_mid:,.0f}** | **${total_high:,.0f}** | |",
    ]
    return "\n".join(lines)


def generate_pricing_scenarios_table(package_name: str, bidders: list) -> str:
    """
    Real gap found 2026-07-17: Buck shared 6 real 246 Gallo Way "Bid
    Leveling / Rebid Package" workbooks built by Mike Mount's own AI
    process. Their "Pricing Scenarios" tab does something ours never has -
    normalizes a bidder's raw submitted total by adding back specific,
    named allowances/exclusions that were priced out of the base number,
    so bidders who structured their number differently become comparable.
    Real example from that file: R&A Enterprises' raw $802,000 becomes
    $845,500 once solar/backup-AC ($25,000), box-walk ($4,000), light
    layout ($8,500), and light aiming ($6,000) allowances are added back.

    This function does the arithmetic only - it never invents which
    adjustments apply. The caller supplies each bidder's real raw total
    and a list of named, dollar-valued adjustments already identified from
    real exclusions/scope-gap data (e.g. from bid_level_analyzer.py's
    exclusions_by_bidder output or a human's own read of the bid). An
    adjustment with no real source shouldn't be added here - matches the
    standing rule that this system never fabricates a number to make bids
    look more comparable than the underlying data supports.

    bidders: list of {
        "name": str, "raw_total": float,
        "adjustments": list of {"label": str, "amount": float},
    }
    """
    all_labels = []
    for b in bidders:
        for adj in b.get("adjustments", []):
            if adj["label"] not in all_labels:
                all_labels.append(adj["label"])

    lines = [
        f"# {package_name} — Pricing Scenarios",
        "*Adjusted totals normalize raw submitted numbers by adding back real, "
        "named allowances/exclusions identified during scope-gap review - not "
        "a spread or savings calculation, and not a carry recommendation.*",
        "",
        "| Scenario | " + " | ".join(b["name"] for b in bidders) + " |",
        "|---|" + "---|" * len(bidders),
    ]
    lines.append(
        "| Raw submitted / stated total | "
        + " | ".join(f"${b['raw_total']:,.0f}" for b in bidders) + " |"
    )
    for label in all_labels:
        row = [f"Add: {label}"]
        for b in bidders:
            match = next((a["amount"] for a in b.get("adjustments", []) if a["label"] == label), None)
            row.append(f"${match:,.0f}" if match else "—")
        lines.append("| " + " | ".join(row) + " |")

    lines.append(
        "| **Adjusted comparable total** | "
        + " | ".join(
            f"**${b['raw_total'] + sum(a['amount'] for a in b.get('adjustments', [])):,.0f}**"
            for b in bidders
        ) + " |"
    )
    return "\n".join(lines)


def generate_decision_matrix(package_name: str, criteria: list, bidders: list) -> dict:
    """
    Real gap found 2026-07-17, same 246 Gallo Way source as
    generate_pricing_scenarios_table(). Mike's real "Decision Matrix" tabs
    score each bidder against weighted criteria (e.g. Scope completeness
    0.30, Pricing clarity 0.20, Project specificity 0.20, Commercial
    competitiveness 0.15, Risk of exclusions 0.15) with a 1-5 score per
    criterion AND a written rationale per score, rolling up to a weighted
    total. Real example (246GW Fire Protection): Integrity 2.75 vs KFS
    3.75, with the file's own stated recommendation still landing on
    "rebid before deciding" rather than auto-awarding the higher score -
    that pattern is preserved here on purpose.

    This function computes the weighted arithmetic only. It requires a
    rationale string for every score - a bare number with no stated reason
    isn't decision support, it's an unexplained black box, and this system
    doesn't produce those. It does NOT return a "winner" or set
    recommended_carry - the weighted total is informational context for a
    human decision, exactly matching carry_to_budget_modification()'s
    standing rule that award decisions are never made by this system.

    criteria: list of {"name": str, "weight": float} - weights should sum
    to ~1.0; a mismatch is flagged in the output rather than silently
    renormalized, since a bad weight sum usually means a real input error.
    bidders: list of {
        "name": str,
        "scores": {criterion_name: {"score": float (1-5), "rationale": str}},
    }
    """
    weight_sum = sum(c["weight"] for c in criteria)
    weight_warning = None
    if abs(weight_sum - 1.0) > 0.01:
        weight_warning = (
            f"Criteria weights sum to {weight_sum:.2f}, not 1.00 - check input "
            f"before treating the weighted totals below as meaningful."
        )

    lines = [
        f"# {package_name} — Decision Matrix",
        "*Weighted scores are informational context only - this system does not "
        "select a winning bid or set a recommended carry. Every score below has "
        "a stated rationale; there are no unexplained numbers.*",
    ]
    if weight_warning:
        lines.append(f"\n**⚠ {weight_warning}**")
    lines += [
        "",
        "| Criteria | Weight | " + " | ".join(b["name"] for b in bidders) + " | Rationale |",
        "|---|---|" + "---|" * len(bidders) + "---|",
    ]

    totals = {b["name"]: 0.0 for b in bidders}
    for c in criteria:
        row_scores, rationales = [], []
        for b in bidders:
            entry = b["scores"].get(c["name"], {})
            score = entry.get("score", 0)
            totals[b["name"]] += score * c["weight"]
            row_scores.append(f"{score}")
            if entry.get("rationale"):
                rationales.append(f"{b['name']}: {entry['rationale']}")
        lines.append(
            f"| {c['name']} | {c['weight']:.2f} | " + " | ".join(row_scores)
            + " | " + "; ".join(rationales) + " |"
        )
    lines.append(
        "| **Weighted Total** | | " + " | ".join(f"**{totals[b['name']]:.2f}**" for b in bidders) + " | |"
    )

    return {"markdown": "\n".join(lines), "weighted_totals": totals, "weight_warning": weight_warning}


def generate_rebid_request_log(package_name: str, requests: list) -> str:
    """
    Real gap found 2026-07-17, same source as the two functions above.
    Mike's real "Rebid Requests" tabs turn the exclusions/scope-gap
    findings into a structured, actionable follow-up log per bidder -
    Priority / Request / Why It Matters / Requested Response Format -
    rather than leaving scope ambiguity as a passive note in a comparison
    doc. This is the piece our pipeline was missing entirely: we extract
    real exclusions_by_bidder and generate RFI questions
    (bid_level_analyzer.py), but never turned them into a structured
    request log or the follow-up email itself (see generate_rebid_email()
    in sow_generator.py for the email side of this).

    requests: list of {
        "bidder": str, "priority": "High"|"Medium"|"Low", "topic": str,
        "request": str, "why_it_matters": str, "requested_format": str,
    }
    Caller supplies real requests - typically derived directly from a
    division's own exclusions_by_bidder/rfis output, not invented here.
    """
    lines = [
        f"# {package_name} — Clarification & Rebid Request Log",
        "",
        "| Bidder | Priority | Topic | Requested Clarification/Revision | Why It Matters | Requested Response Format |",
        "|---|---|---|---|---|---|",
    ]
    for r in requests:
        lines.append(
            f"| {r['bidder']} | {r['priority']} | {r['topic']} | {r['request']} | "
            f"{r['why_it_matters']} | {r.get('requested_format', '')} |"
        )
    return "\n".join(lines)

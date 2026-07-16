"""
Real AI-triggered bid-leveling analysis - Steps B-F of the Buck-approved
Gold Standard process (BROWSER_CLAUDE_BID_LEVELING_GOLD_STANDARD,
2026-07-13): build the scope matrix, dollar-value every gap, identify the
biggest risk, generate the RFI list, write the reasoning-based
recommendation. Takes the real extracted bid data from bid_extractor.py
(Step A) and produces the analysis - a genuine AI reasoning step, not a
formatting function. The output feeds directly into
budget_generator.generate_bid_leveling_gold_standard() for final formatting.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from multi_doc_reader import _parse_findings_json

import os
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent.parent / ".env")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

LEVELING_ANALYSIS_SYSTEM = """You are a construction bid-leveling analyst comparing multiple real, extracted subcontractor bids for the same scope of work on a luxury residential project in Aspen, CO, following Hendrickson Construction's approved Gold Standard bid-leveling methodology.

Given the extracted bid data for 2+ bidders (vendor, total, line items, inclusions, exclusions), produce:

1. scope_matrix: array of {item, bidder_status: {vendor_name: "included"|"excluded"|qualifier}, amount_by_bidder: {vendor_name: number|null}, why_it_matters: string} - union all real scope items across all bids, cross-referencing what one bidder includes that another appears to omit. Only include items with real evidence in the extracted data - do not invent scope.

2. biggest_risk: {question, dollar_at_stake, explanation} - the single highest-dollar ambiguous item, written as a direct question, with the real dollar amount at stake and why it matters. NEVER conclude "low bid wins" without addressing scope completeness first.

3. rfis: array of specific clarification questions to send bidders before award, addressing every real scope ambiguity found.

4. exclusions_by_bidder: {vendor_name: array of real exclusion strings} - pass through the real stated exclusions per bidder.

Base every finding on the actual extracted data provided - cite real dollar amounts and real stated inclusions/exclusions. Do not fabricate scope comparisons not supported by the data.

Return ONLY a JSON object with exactly these keys: scope_matrix, biggest_risk, rfis, exclusions_by_bidder."""


def analyze_bid_leveling_with_claude(extracted_bids: dict, division_name: str, package_name: str,
                                      model: str = "claude-sonnet-4-6") -> dict:
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    bidder_keys = list(extracted_bids.keys())
    prompt = (
        f"Division: {division_name}, Package: {package_name}\n\n"
        f"Real extracted bid data:\n{json.dumps(extracted_bids, indent=2)}\n\n"
        f"IMPORTANT: use exactly these bidder keys in scope_matrix.bidder_status, "
        f"scope_matrix.amount_by_bidder, and exclusions_by_bidder - {bidder_keys} - "
        f"not the full vendor name field inside the extracted data if it differs.\n\n"
        f"Produce the Gold Standard analysis per your instructions. Return the JSON object only."
    )
    try:
        resp = client.messages.create(
            model=model, max_tokens=12000, system=LEVELING_ANALYSIS_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as e:
        return {"error": str(e), "provider": "claude"}

    raw_text = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
    try:
        analysis = _parse_findings_json(raw_text)
    except Exception as e:
        return {"error": f"Could not parse JSON: {e}", "provider": "claude", "raw_response": raw_text}

    return {"analysis": analysis, "provider": "claude", "model": model}


def analyze_bid_leveling_with_gemini(extracted_bids: dict, division_name: str, package_name: str,
                                      model: str = None) -> dict:
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if not gemini_key:
        return {"error": "GEMINI_API_KEY not set", "provider": "gemini"}

    model = model or os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=gemini_key)

        bidder_keys = list(extracted_bids.keys())
        prompt = (
            f"Division: {division_name}, Package: {package_name}\n\n"
            f"Real extracted bid data:\n{json.dumps(extracted_bids, indent=2)}\n\n"
            f"IMPORTANT: use exactly these bidder keys in scope_matrix.bidder_status, "
            f"scope_matrix.amount_by_bidder, and exclusions_by_bidder - {bidder_keys} - "
            f"not the full vendor name field inside the extracted data if it differs.\n\n"
            f"Produce the Gold Standard analysis per your instructions. Return the JSON object only."
        )
        response = client.models.generate_content(
            model=model,
            config=types.GenerateContentConfig(system_instruction=LEVELING_ANALYSIS_SYSTEM),
            contents=[types.Part.from_text(text=prompt)],
        )
        raw_text = response.text.strip()
    except Exception as e:
        return {"error": str(e), "provider": "gemini"}

    try:
        analysis = _parse_findings_json(raw_text)
    except Exception as e:
        return {"error": f"Could not parse JSON: {e}", "provider": "gemini", "raw_response": raw_text}

    return {"analysis": analysis, "provider": "gemini", "model": model}


def analyze_bid_leveling(extracted_bids: dict, division_name: str, package_name: str,
                          model: str = "claude-sonnet-4-6") -> dict:
    """Gemini-primary, Claude-fallback - same contract as the rest of the pipeline."""
    result = analyze_bid_leveling_with_gemini(extracted_bids, division_name, package_name)
    if "error" not in result:
        result["error"] = None
        return result

    print(f"  Gemini failed ({result['error']}), falling back to Claude...", flush=True)
    fallback = analyze_bid_leveling_with_claude(extracted_bids, division_name, package_name, model=model)
    fallback["error"] = fallback.get("error")
    fallback["gemini_error"] = result["error"]
    return fallback

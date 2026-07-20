"""
Real AI-triggered bid-PDF extraction - Step A of the Buck-approved Gold
Standard bid-leveling process (BROWSER_CLAUDE_BID_LEVELING_GOLD_STANDARD,
2026-07-13): "Extract from each bid PDF: all line items with dollar
amounts, all scope inclusions, all exclusions, finish specifications,
pumping/mobilization/delivery treatment, any unit-rate items." This is the
missing extraction layer feeding services/bid_leveling/budget_generator.py's
generate_bid_leveling_gold_standard() formatting function - without this,
that function can only format hand-typed data, not real bid PDFs.

Same Gemini-primary/Claude-fallback contract as multi_doc_reader.py and
scope_synthesizer.py.
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

BID_EXTRACTION_SYSTEM = """You are a construction bid analyst extracting structured data from a real subcontractor bid proposal PDF for a luxury residential project in Aspen, CO.

Extract from this ONE bid document:
- vendor: the bidding company's name
- total_amount: the total bid amount as a number (no $ or commas)
- line_items: array of {item, amount, unit_rate (if shown)} - every priced line item
- inclusions: array of scope items explicitly stated as included
- exclusions: array of scope items explicitly stated as excluded
- finish_specs: array of any finish/material specifications called out (e.g. "hard trowel finish", specific product names)
- pumping_mobilization_delivery: how pumping, mobilization, and delivery are treated (included/excluded/separate line item, with dollar amount if shown)
- unit_rate_items: array of {item, unit_rate, unit} for anything priced per-unit (e.g. "sleeves @ $X each")
- assumptions_and_qualifications: array of any stated assumptions or qualifications

Return ONLY a JSON object with exactly these keys. Use null or empty array for anything not found in the document - do not invent data."""


def extract_bid_with_claude(file_id: str, model: str = "claude-sonnet-4-6") -> dict:
    import anthropic
    sys.path.insert(0, str(Path(__file__).parent.parent / "drive_intelligence"))
    from drive_client import download_binary, get_file_metadata
    import base64

    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    meta = get_file_metadata(file_id)
    content = download_binary(file_id)
    b64 = base64.standard_b64encode(content).decode()

    # Streaming, not create(): a large scanned/image PDF (base64-embedded,
    # requiring the model to effectively OCR it) can run past Anthropic's
    # 10-minute non-streaming limit and get rejected outright before any
    # response comes back - same real failure class found and fixed in
    # bid_level_analyzer.py the same day (Div 09 Stone).
    #
    # Real second bug, found 2026-07-17 investigating BFS's "unreadable" bid
    # at Buck's explicit push to actually try instead of writing it off as a
    # scanned image: it was never unreadable - it's a genuinely huge,
    # legitimate itemized lumber order (hundreds of real line items) that
    # hit the fixed 8000-token ceiling and got cut off mid-string. This
    # function never had the stop_reason-based retry-with-doubled-budget
    # fix that bid_level_analyzer.py already got for the same failure mode -
    # added here too instead of writing off large real bids as unextractable.
    budget = 8000
    last_error = None
    for attempt in range(3):
        try:
            with client.messages.stream(
                model=model, max_tokens=budget, system=BID_EXTRACTION_SYSTEM,
                messages=[{"role": "user", "content": [
                    {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": b64}},
                    {"type": "text", "text": "Extract the bid data per your instructions. Return the JSON object only."},
                ]}],
            ) as stream:
                resp = stream.get_final_message()
        except Exception as e:
            return {"error": str(e), "provider": "claude"}

        raw_text = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
        if resp.stop_reason == "max_tokens":
            last_error = f"response truncated at max_tokens={budget}"
            budget *= 2
            continue
        try:
            extracted = _parse_findings_json(raw_text)
        except Exception as e:
            return {"error": f"Could not parse JSON: {e}", "provider": "claude", "raw_response": raw_text}

        return {"extracted": extracted, "file_name": meta.get("name"), "provider": "claude", "model": model,
                "retries_used": attempt}

    return {"error": f"Still truncating after 3 attempts (final budget {budget // 2}): {last_error}",
            "provider": "claude", "file_name": meta.get("name")}


# Circuit-breaker (Buck 2026-07-20 "speed up gemini"): the genai SDK auto-retries
# a 429/rate-limit internally with a long backoff (~40-50s per call) before it
# finally errors and we fall back to Claude. When Gemini's daily quota is out or
# prepay isn't active, EVERY bid wastes ~47s in that backoff. This flag trips on
# the FIRST quota/rate-limit signal and skips Gemini for the rest of the process,
# turning "47s wasted x N bids" into "wasted once, then straight to Claude". Zero
# effect when Gemini is healthy. Resets per process (fresh run re-tries Gemini).
_GEMINI_DOWN = False


def _is_quota_error(msg: str) -> bool:
    m = (msg or "").lower()
    return any(k in m for k in ("429", "resource_exhausted", "quota", "depleted", "rate_limit", "rate limit"))


def extract_bid_with_gemini(file_id: str, model: str = None) -> dict:
    global _GEMINI_DOWN
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if not gemini_key:
        return {"error": "GEMINI_API_KEY not set", "provider": "gemini"}

    model = model or os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
    try:
        from google import genai
        from google.genai import types
        sys.path.insert(0, str(Path(__file__).parent.parent / "drive_intelligence"))
        from drive_client import download_binary, get_file_metadata

        client = genai.Client(api_key=gemini_key)
        meta = get_file_metadata(file_id)
        content = download_binary(file_id)

        response = client.models.generate_content(
            model=model,
            config=types.GenerateContentConfig(system_instruction=BID_EXTRACTION_SYSTEM),
            contents=[
                types.Part.from_bytes(data=content, mime_type="application/pdf"),
                types.Part.from_text(text="Extract the bid data per your instructions. Return the JSON object only."),
            ],
        )
        raw_text = response.text.strip()
    except Exception as e:
        if _is_quota_error(str(e)):
            _GEMINI_DOWN = True  # trip the breaker - stop wasting the ~47s SDK backoff on every remaining bid
        return {"error": str(e), "provider": "gemini"}

    try:
        extracted = _parse_findings_json(raw_text)
    except Exception as e:
        return {"error": f"Could not parse JSON: {e}", "provider": "gemini", "raw_response": raw_text}

    return {"extracted": extracted, "file_name": meta.get("name"), "provider": "gemini", "model": model}


def extract_bid(file_id: str, model: str = "claude-sonnet-4-6") -> dict:
    """Gemini-primary, Claude-fallback - same contract as the rest of the plan-reading pipeline."""
    if _GEMINI_DOWN:
        # circuit-breaker tripped earlier this run: skip Gemini's slow backoff, go straight to Claude
        fallback = extract_bid_with_claude(file_id, model=model)
        fallback["error"] = fallback.get("error")
        fallback["gemini_error"] = "skipped (gemini quota/rate-limit circuit-breaker tripped this run)"
        return fallback
    result = extract_bid_with_gemini(file_id)
    if "error" not in result:
        result["error"] = None
        return result

    print(f"  Gemini failed ({result['error']}), falling back to Claude...", flush=True)
    fallback = extract_bid_with_claude(file_id, model=model)
    fallback["error"] = fallback.get("error")
    fallback["gemini_error"] = result["error"]
    return fallback

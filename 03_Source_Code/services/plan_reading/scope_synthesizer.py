"""
Real AI-triggered SOW-content synthesis - the missing workflow layer Buck
flagged 2026-07-16: sow_generator.generate_sow() only formats content that's
handed to it, it doesn't write that content itself. This module is the real
workflow that reads the actual plan documents (via Gemini, same pattern as
multi_doc_reader.py) and produces the actual scope content for a specific
division/package - base_scope_items, clarifications, exclusions, required
proposal format - matching the structure generate_sow() expects.

Same Gemini-primary/Claude-fallback contract as multi_doc_reader.py. This is
a genuine AI workflow: the model reads the real source documents and writes
the scope content; nothing here is authored by the calling code or by a
human in the loop.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from multi_doc_reader import _pdf_block, _fetch_doc_meta_and_blocks_claude, _parse_findings_json

import os
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent.parent / ".env")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

SCOPE_SYNTHESIS_SYSTEM = """You are a construction scope-writing specialist producing a real Scope of Work for a luxury residential project in Aspen, CO.

You have been given real plan/spec documents. Your job is to write the actual SOW content for ONE specific trade/division package, matching the real structure Hendrickson Construction uses (modeled on their principal's own real SOW packets):

- base_scope_items: an exhaustive list of narrative scope description strings, as specific as the plans/specs allow (real sheet references, real material specs, real quantities where shown). This is the core deliverable - vague items produce weak bids.
- clarifications: questions the bidder must answer in their proposal to make bids comparable (apples-to-apples).
- exclusions: items explicitly NOT included unless the bidder states otherwise.
- required_proposal_format: what the bidder's proposal itself must contain (e.g. "Lump sum with breakout by area/type", "Price by location").

Cite real sheet numbers, spec sections, and document names for every scope item where the source documents support it. Do not invent scope not shown or implied by the documents.

Return ONLY a JSON object with exactly these keys: base_scope_items (array of strings), clarifications (array of strings), exclusions (array of strings), required_proposal_format (array of strings). No other text."""


def synthesize_sow_content_with_claude(file_ids: dict, division_name: str, package_name: str,
                                        model: str = "claude-sonnet-4-6") -> dict:
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    doc_meta, content_blocks = _fetch_doc_meta_and_blocks_claude(file_ids)
    content_blocks.append({
        "type": "text",
        "text": f"Write the real SOW content for the {package_name} scope "
                f"(Division: {division_name}) based on these documents. "
                f"Return the JSON object only."
    })
    try:
        resp = client.messages.create(
            model=model, max_tokens=8000, system=SCOPE_SYNTHESIS_SYSTEM,
            messages=[{"role": "user", "content": content_blocks}],
        )
    except Exception as e:
        return {"error": str(e), "provider": "claude"}

    raw_text = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
    try:
        content = _parse_findings_json(raw_text)
    except Exception as e:
        return {"error": f"Could not parse JSON: {e}", "provider": "claude", "raw_response": raw_text}

    return {"content": content, "documents": doc_meta, "provider": "claude", "model": model}


def synthesize_sow_content_with_gemini(file_ids: dict, division_name: str, package_name: str,
                                        model: str = None) -> dict:
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
        doc_meta = {}
        parts = []
        for label, file_id in file_ids.items():
            meta = get_file_metadata(file_id)
            doc_meta[label] = {"file_id": file_id, "name": meta.get("name"), "size": meta.get("size")}
            content = download_binary(file_id)
            parts.append(types.Part.from_text(text=f"--- Document: {label} ({meta.get('name')}) ---"))
            parts.append(types.Part.from_bytes(data=content, mime_type="application/pdf"))
        parts.append(types.Part.from_text(text=(
            f"Write the real SOW content for the {package_name} scope "
            f"(Division: {division_name}) based on these documents. "
            f"Return the JSON object only."
        )))

        response = client.models.generate_content(
            model=model,
            config=types.GenerateContentConfig(system_instruction=SCOPE_SYNTHESIS_SYSTEM),
            contents=parts,
        )
        raw_text = response.text.strip()
    except Exception as e:
        return {"error": str(e), "provider": "gemini"}

    try:
        content = _parse_findings_json(raw_text)
    except Exception as e:
        return {"error": f"Could not parse JSON: {e}", "provider": "gemini", "raw_response": raw_text}

    return {"content": content, "documents": doc_meta, "provider": "gemini", "model": model}


def synthesize_sow_content(file_ids: dict, division_name: str, package_name: str,
                            model: str = "claude-sonnet-4-6") -> dict:
    """
    Real AI-triggered workflow: Gemini-primary, Claude-fallback, same
    contract as cross_reference_documents(). Returns
    {"content": {...4 keys...}, "documents": {...}, "provider": str,
    "error": str|None} - content is ready to pass directly into
    sow_generator.generate_sow()'s base_scope_items/clarifications/
    exclusions/required_proposal_format params.
    """
    result = synthesize_sow_content_with_gemini(file_ids, division_name, package_name)
    if "error" not in result:
        result["error"] = None
        return result

    print(f"  Gemini failed ({result['error']}), falling back to Claude...", flush=True)
    fallback = synthesize_sow_content_with_claude(file_ids, division_name, package_name, model=model)
    fallback["error"] = fallback.get("error")
    fallback["gemini_error"] = result["error"]
    return fallback

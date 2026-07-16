"""
Multi-document plan-read cross-reference pipeline - Phase 2A of BC's Full
Build Order (2026-07-15 11:05 PM MT), the real gate before any greenfield
test can run. Buck's explicit requirement: read multiple plan documents
NOT sequentially/independently summarized, but genuinely cross-referenced,
specifically to catch things like appliance specs living in the spec book
but not the architectural set, or MEP scope hidden in mechanical plans.

Uses Claude's native PDF document support (not the older page-by-page image
conversion in tools/plan_reader.py) so multiple whole documents go into a
single call and the model can actually cross-reference between them in one
reasoning pass, rather than analyzing each document in isolation and hoping
a second pass catches cross-document gaps.
"""
import base64
import json
import sys
from pathlib import Path

import anthropic

sys.path.insert(0, str(Path(__file__).parent.parent / "drive_intelligence"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "api"))
from drive_client import download_binary, get_file_metadata

import os
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent.parent / ".env")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

CROSS_REF_SYSTEM = """You are a licensed construction document reviewer performing a cross-document scope and gap analysis for a luxury residential project in Aspen, CO.

You have been given MULTIPLE documents from the same project's plan set (architectural, structural, mechanical, and/or spec book). Your job is NOT to summarize each document separately - it is to CROSS-REFERENCE them against each other.

Specifically hunt for:
1. Items specified in ONE document that are absent, contradicted, or unclear in another (e.g. an appliance model called out in the spec book with no corresponding location/rough-in shown on the architectural or mechanical plans; a structural note referencing a condition not shown on the architectural sheets).
2. Scope that appears to fall between documents - not clearly assigned to any single trade/document.
3. Direct conflicts - the same item specified two different ways in two different documents.
4. Notes saying "see spec book", "by others", "coordinate with", "TBD", "verify in field" - and whether the referenced coordination actually resolves cleanly across the documents you have.

For EVERY finding, you MUST cite the specific document and location (sheet number/page or spec section) for BOTH sides of the cross-reference - a finding that only cites one document is not a cross-reference, it's a single-document note and does not satisfy this task.

Output a JSON array of findings, each with these exact fields:
{"division": "division/discipline", "source_a": "document + sheet/section", "source_b": "document + sheet/section (or null if this is a single-doc gap with no counterpart found anywhere)", "question": "the single clear question this raises", "why_it_matters": "what is ambiguous, conflicting, or missing", "confidence": "definite gap" or "worth flagging"}

Return ONLY the JSON array, no other text."""


def _pdf_block(file_id: str) -> dict:
    """Downloads a Drive PDF and returns it as a Claude API document content block."""
    content = download_binary(file_id)
    b64 = base64.standard_b64encode(content).decode()
    return {
        "type": "document",
        "source": {"type": "base64", "media_type": "application/pdf", "data": b64},
    }


def _parse_findings_json(raw_text: str):
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    return json.loads(cleaned.strip())


def _fetch_doc_meta_and_blocks_claude(file_ids: dict):
    doc_meta = {}
    content_blocks = []
    for label, file_id in file_ids.items():
        meta = get_file_metadata(file_id)
        doc_meta[label] = {"file_id": file_id, "name": meta.get("name"), "size": meta.get("size")}
        content_blocks.append({"type": "text", "text": f"--- Document: {label} ({meta.get('name')}) ---"})
        content_blocks.append(_pdf_block(file_id))
    content_blocks.append({
        "type": "text",
        "text": f"Cross-reference these {len(file_ids)} documents ({', '.join(file_ids.keys())}) per your instructions. Return the JSON array of findings only."
    })
    return doc_meta, content_blocks


def _cross_reference_with_claude(file_ids: dict, model: str = "claude-sonnet-4-6") -> dict:
    """Real fallback engine - same contract as the Gemini path, different provider/billing."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    doc_meta, content_blocks = _fetch_doc_meta_and_blocks_claude(file_ids)

    try:
        resp = client.messages.create(
            model=model, max_tokens=16000, system=CROSS_REF_SYSTEM,
            messages=[{"role": "user", "content": content_blocks}],
        )
    except Exception as e:
        return {"error": str(e), "provider": "claude"}

    raw_text = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
    try:
        findings = _parse_findings_json(raw_text)
    except Exception as e:
        return {"error": f"Could not parse JSON from model response: {e}",
                "provider": "claude", "raw_response": raw_text}

    return {
        "documents": doc_meta, "findings": findings, "raw_response": raw_text,
        "provider": "claude", "model": model,
        "usage": {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens},
    }


def _cross_reference_with_gemini(file_ids: dict, model: str = None) -> dict:
    """
    Primary engine per Buck's explicit test design (2026-07-16): use Gemini
    until the real free-tier quota (20 req/day project-wide, confirmed live
    2026-07-08) is hit, so the live test exercises the fallback path too, not
    just the happy path. Same PDF-native-document approach as Claude, via the
    google-genai SDK (see drive_bid_reader.py's extract_bid_with_gemini for
    the proven single-doc version of this pattern).
    """
    import os as _os
    gemini_key = _os.environ.get("GEMINI_API_KEY", "")
    if not gemini_key:
        return {"error": "GEMINI_API_KEY not set", "provider": "gemini"}

    model = model or _os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
    try:
        from google import genai
        from google.genai import types

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
            f"Cross-reference these {len(file_ids)} documents ({', '.join(file_ids.keys())}) "
            f"per your instructions. Return the JSON array of findings only."
        )))

        response = client.models.generate_content(
            model=model,
            config=types.GenerateContentConfig(system_instruction=CROSS_REF_SYSTEM),
            contents=parts,
        )
        raw_text = response.text.strip()
    except Exception as e:
        return {"error": str(e), "provider": "gemini"}

    try:
        findings = _parse_findings_json(raw_text)
    except Exception as e:
        return {"error": f"Could not parse JSON from model response: {e}",
                "provider": "gemini", "raw_response": raw_text}

    return {
        "documents": doc_meta, "findings": findings, "raw_response": raw_text,
        "provider": "gemini", "model": model,
    }


def cross_reference_documents(file_ids: dict, model: str = "claude-sonnet-4-6") -> dict:
    """
    file_ids: dict mapping a label (e.g. "architectural", "spec_book") to a
    Drive file ID. Tries Gemini first (primary, per Buck's test design);
    falls back to Claude on ANY Gemini failure (quota exhaustion, outage,
    parse failure) - same contract as drive_bid_reader.py's bid-extraction
    fallback, applied here. `model` param only affects the Claude fallback
    call; Gemini's model is controlled by GEMINI_MODEL in .env.

    Returns {"documents": {...}, "findings": [...], "raw_response": str,
    "provider": "gemini"|"claude", "error": str|None}.
    """
    result = _cross_reference_with_gemini(file_ids)
    if "error" not in result:
        result["error"] = None
        return result

    print(f"  Gemini failed ({result['error']}), falling back to Claude...", flush=True)
    fallback = _cross_reference_with_claude(file_ids, model=model)
    fallback["error"] = fallback.get("error")
    fallback["gemini_error"] = result["error"]
    return fallback


def cross_reference_folder(folder_id: str, model: str = "claude-sonnet-4-6",
                            min_size_bytes: int = 100_000, max_docs: int = 6) -> dict:
    """
    Field-callable entry point: reads a whole Drive folder (e.g. a project's
    04_Drawings) instead of requiring specific file IDs up front. Uses
    dedup.select_canonical_files() to skip Archived/duplicate copies, then
    cross-references the canonical PDFs found (largest first, capped at
    max_docs to keep a single call's cost/token usage bounded - Claude's
    per-request limits and practical cost make "every PDF in the folder in
    one call" impractical past a handful of large plan sets).
    """
    from dedup import select_canonical_files

    selection = select_canonical_files(folder_id, min_size_bytes)
    pdfs = [f for f in selection["canonical_files"] if f["name"].lower().endswith(".pdf")]
    pdfs_by_size = sorted(pdfs, key=lambda f: -int(f.get("size") or 0))[:max_docs]

    if len(pdfs_by_size) < 2:
        return {
            "folder_id": folder_id,
            "error": f"Only {len(pdfs_by_size)} canonical PDF(s) found - need at least 2 to cross-reference.",
            "canonical_file_count": selection["canonical_file_count"],
        }

    file_ids = {f["name"].rsplit(".", 1)[0][:40]: f["id"] for f in pdfs_by_size}
    result = cross_reference_documents(file_ids, model=model)
    result["folder_id"] = folder_id
    result["documents_skipped_over_cap"] = max(0, len(pdfs) - max_docs)
    return result

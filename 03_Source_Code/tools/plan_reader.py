#!/usr/bin/env python3
"""
HCI Plan Reader — Vision AI analysis of construction documents.

Downloads a PDF from Google Drive (by file ID), converts each page to an image,
and sends it to a vision model for forensic gap analysis.

Model routing:
  sonnet  — fast, affordable, good for routine reads (default)
  opus    — deep forensic review, on-demand only, NOT for automation loops
  gemini  — free tier, add GEMINI_API_KEY to .env (TODO)

Usage:
  python3 plan_reader.py <drive_file_id> [--model sonnet|opus] [--pages 1-3] [--scope structural|roofing|finishes|full]

Output:
  /tmp/hci_plan_analysis_<file_id>.json   — full structured findings
  Prints summary to stdout.
"""
import anthropic, argparse, base64, glob, json, os, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image

# Load env
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env")

ANTHROPIC_KEY  = os.environ.get("ANTHROPIC_API_KEY", "")
GEMINI_KEY     = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL   = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")   # update .env when Google releases new versions

MODEL_MAP = {
    "sonnet": "claude-sonnet-4-6",
    "opus":   "claude-opus-4-8",
}

PLAN_SYSTEM = """You are a licensed structural engineer and construction document reviewer analyzing drawings for a luxury residential project in Aspen, CO.

For each drawing sheet, extract and report:
1. SHEET INFO: Sheet number, title, scale, date, engineer/firm, revision status
2. SPECIFICATIONS FOUND: All material specs, dimensions, grades, loads, connection requirements — quote verbatim
3. OPEN ITEMS: Any notes saying "confirm", "verify", "TBD", "by others", "field verify", plus any visible markup flags or red circles
4. RFI CANDIDATES: Specific questions requiring SE/architect response before bidding or construction
5. SCOPE GAPS: What should be on this drawing that is absent or underspecified

Be exhaustive and forensic. Quote exact callouts, dimensions, and notes verbatim. Flag anything with a question mark or unresolved notation."""


def download_pdf_from_drive(file_id: str, out_path: str) -> bool:
    """Download PDF binary from Drive using saved base64 content tool output if available."""
    # Check if a recent tool-result download exists for this file
    tool_result_dir = Path.home() / ".claude" / "projects" / "-Users-buckadams"
    for f in sorted(tool_result_dir.rglob("mcp-claude_ai_Google_Drive-download_file_content*.txt"), reverse=True):
        try:
            with open(f) as fp:
                data = json.load(fp)
            if data.get("id") == file_id:
                pdf_bytes = base64.b64decode(data["content"])
                with open(out_path, "wb") as fp:
                    fp.write(pdf_bytes)
                print(f"  Loaded from cached download: {f.name}")
                return True
        except Exception:
            continue
    return False


def pdf_to_images(pdf_path: str, out_dir: str, pages: str = None, dpi: int = 150) -> list:
    """Convert PDF pages to PNG images. Returns sorted list of PNG paths."""
    page_args = []
    if pages:
        parts = pages.split("-")
        if len(parts) == 2:
            page_args = ["-f", parts[0], "-l", parts[1]]

    subprocess.run(
        ["pdftoppm", "-r", str(dpi), *page_args, pdf_path, os.path.join(out_dir, "page")],
        capture_output=True, check=False
    )

    ppm_files = sorted(glob.glob(os.path.join(out_dir, "page-*.ppm")))
    png_files = []
    for ppm in ppm_files:
        png = ppm.replace(".ppm", ".png")
        Image.open(ppm).save(png, "PNG", optimize=True)
        png_files.append(png)
    return png_files


def analyze_with_claude(pages: list, model: str, project_code: str = None, scope: str = "full") -> list:
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    model_id = MODEL_MAP.get(model, "claude-sonnet-4-6")
    findings = []

    for i, page_path in enumerate(pages, 1):
        print(f"  Page {i}/{len(pages)} → {model_id} ...", flush=True)
        with open(page_path, "rb") as f:
            img_b64 = base64.standard_b64encode(f.read()).decode()

        resp = client.messages.create(
            model=model_id,
            max_tokens=2000,
            system=PLAN_SYSTEM,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": img_b64}},
                    {"type": "text", "text": f"Sheet {i} of {len(pages)}. Project: {project_code or 'unknown'}. Scope focus: {scope}. Analyze completely."}
                ]
            }]
        )
        findings.append({"page": i, "file": Path(page_path).name, "model": model_id, "analysis": resp.content[0].text})

    return findings


def analyze_with_gemini(pages: list, project_code: str = None, scope: str = "full",
                        model_name: str = "gemini-3.5-flash") -> list:
    """Gemini vision — free tier. Flash=fast/pipeline, Pro=deep/on-demand. Requires GEMINI_API_KEY in .env."""
    try:
        import google.genai as genai
        from google.genai import types as genai_types
    except ImportError:
        print("  Gemini SDK not installed: pip install google-genai")
        return []

    if not GEMINI_KEY:
        print("  GEMINI_API_KEY not set in .env — get free key at ai.google.dev")
        return []

    client = genai.Client(api_key=GEMINI_KEY)
    findings = []

    for i, page_path in enumerate(pages, 1):
        print(f"  Page {i}/{len(pages)} → {model_name} ...", flush=True)
        with open(page_path, "rb") as f:
            img_bytes = f.read()

        resp = client.models.generate_content(
            model=model_name,
            contents=[
                genai_types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
                f"System: {PLAN_SYSTEM}\n\nSheet {i} of {len(pages)}. Project: {project_code or 'unknown'}. Scope: {scope}. Analyze completely."
            ]
        )
        findings.append({"page": i, "file": Path(page_path).name, "model": model_name, "analysis": resp.text})

    return findings


def main():
    parser = argparse.ArgumentParser(description="HCI Vision Plan Reader")
    parser.add_argument("file_id", help="Google Drive file ID")
    parser.add_argument("--model", default="sonnet", choices=["sonnet", "opus", "gemini", "gemini-pro"])
    parser.add_argument("--pages", default=None, help="Page range e.g. '1-5'")
    parser.add_argument("--scope", default="full", choices=["full", "structural", "roofing", "finishes"])
    parser.add_argument("--project", default=None, help="Project code e.g. 1355R")
    parser.add_argument("--dpi", default=150, type=int, help="Image DPI (150=good, 200=sharp)")
    args = parser.parse_args()

    print(f"\nHCI Plan Reader")
    print(f"  File ID : {args.file_id}")
    print(f"  Model   : {args.model}")
    print(f"  Scope   : {args.scope}")
    print(f"  Pages   : {args.pages or 'all'}")
    print()

    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = os.path.join(tmpdir, "plan.pdf")

        # Try cached download first
        if not download_pdf_from_drive(args.file_id, pdf_path):
            print("  No cached download found. Place the PDF manually:")
            print(f"    cp <your.pdf> {pdf_path}")
            print("  Or run the Drive MCP download from a Claude session and re-run.")
            sys.exit(1)

        print(f"  PDF loaded: {os.path.getsize(pdf_path):,} bytes")
        print(f"  Converting to images at {args.dpi} DPI ...")
        pages = pdf_to_images(pdf_path, tmpdir, args.pages, args.dpi)
        print(f"  {len(pages)} pages converted")
        print()

        if args.model in ("gemini", "gemini-pro"):
            findings = analyze_with_gemini(pages, args.project, args.scope, model_name=GEMINI_MODEL)
        else:
            findings = analyze_with_claude(pages, args.model, args.project, args.scope)

    # Save output
    out_path = f"/tmp/hci_plan_analysis_{args.file_id[:8]}.json"
    with open(out_path, "w") as f:
        json.dump({
            "file_id": args.file_id,
            "project": args.project,
            "model": args.model,
            "scope": args.scope,
            "pages_analyzed": len(findings),
            "findings": findings
        }, f, indent=2)

    print(f"\nSaved: {out_path}")
    print("\n" + "="*70)
    for f in findings:
        print(f"\n{'='*20} PAGE {f['page']} {'='*20}")
        print(f['analysis'])


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
HCI Project Plan Analysis — reusable flow for any project.

Finds the architectural permit drawing set in Drive, reads the full text content,
analyzes for gaps and RFIs using Claude, and sends a consolidated handoff to GBT.

Usage:
  python3 tools/project_plan_analysis.py --project 101F
  python3 tools/project_plan_analysis.py --project 1355R
  python3 tools/project_plan_analysis.py --project 64EW

The script:
  1. Searches Drive for "{project}" permit drawing PDFs
  2. Reads file content via MCP (text extraction)
  3. Sends to Claude Sonnet for gap analysis
  4. Posts consolidated RFI list to GBT inbox
  5. Saves findings to /tmp/hci_{project}_plan_analysis.json
"""
import argparse, json, os, sys, urllib.request, urllib.error
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env")

API_BASE = "http://localhost:8000"
API_KEY  = os.environ.get("HCI_API_KEY", "hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

ANALYSIS_PROMPT = """You are a licensed architect and construction document reviewer analyzing a permit drawing set for a luxury residential project in Aspen, CO.

Read the full drawing set text and produce a forensic gap analysis covering:

1. DRAWING SET OVERVIEW: Architect/firm, sheet list, project info, applicable codes
2. CONFIRMED SPECS (quote verbatim): Roofing assemblies, wall assemblies, floor assemblies, ceiling heights, window schedule, door schedule, mechanical equipment confirmed
3. OPEN ITEMS / TBDs: Every instance of TBD, verify, confirm, by others, NIC, VIF, owner to select, allowance — quote exact text
4. RFI CANDIDATES: Specific questions needing architect/engineer response before bidding — conflicts, missing specs, scope gaps
5. SCOPE GAPS BY TRADE: What is absent or underspecified for concrete, framing, roofing, windows, finishes, MEP
6. FINISH SCHEDULE STATUS: Does one exist? If not, list every room and what is missing

Be exhaustive. Quote exact drawing text verbatim. Flag anything that could cause a change order.
This is a $3M-$8M luxury remodel — gaps cost real money.

Drawing set content follows:
"""


def _api_call(method: str, path: str, body: dict = None) -> dict:
    url = f"{API_BASE}{path}"
    data = json.dumps(body).encode() if body else None
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def search_drive_for_permit_set(project_code: str) -> list:
    """Search Drive via gateway for permit drawing PDFs for this project."""
    resp = _api_call("GET", f"/gateway/drive/search?q={project_code}+permit+drawing+set")
    files = resp.get("payload", {}).get("files", [])
    pdfs = [f for f in files if "permit" in f.get("title", "").lower() or "drawing" in f.get("title", "").lower()]
    return pdfs


def analyze_with_claude(content: str, project_code: str) -> str:
    """Send drawing text to Claude Sonnet for gap analysis."""
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    # Truncate if very large — Sonnet context is 200K tokens
    max_chars = 150_000
    if len(content) > max_chars:
        content = content[:max_chars] + "\n\n[CONTENT TRUNCATED — first 150K chars analyzed]"

    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": f"{ANALYSIS_PROMPT}\n\nPROJECT: {project_code}\n\n{content}"
        }]
    )
    return "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")


def post_to_gbt_inbox(project_code: str, analysis: str, file_title: str) -> str:
    """Post consolidated findings as handoff to GBT inbox."""
    body = f"PLAN ANALYSIS COMPLETE — {project_code}\nSource: {file_title}\nAnalyzed: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n{analysis}"
    payload = {
        "source_agent": "claude_code",
        "destination_agent": "ChatGPT",
        "title": f"PLAN ANALYSIS: {project_code} — Gaps, RFIs, Confirmed Specs",
        "priority": "high",
        "summary": f"{project_code} architectural plan analysis: gaps, RFIs, and confirmed specs for SOWs",
        "body": body
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{API_BASE}/gateway/agent/handoff",
        data=data,
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        resp = json.loads(r.read())
    return resp["payload"]["filename"]


def main():
    parser = argparse.ArgumentParser(description="HCI Project Plan Analysis")
    parser.add_argument("--project", required=True, help="Project code: 101F, 1355R, 64EW")
    parser.add_argument("--file-id", default=None, help="Drive file ID if known (skips search)")
    parser.add_argument("--no-gbt", action="store_true", help="Skip GBT handoff (analysis only)")
    args = parser.parse_args()

    project = args.project.upper()
    out_path = f"/tmp/hci_{project}_plan_analysis.json"

    print(f"\nHCI Plan Analysis — {project}")
    print("="*50)

    # Step 1: Find the permit drawing set
    if args.file_id:
        file_id = args.file_id
        file_title = f"Manual file ID: {file_id}"
        print(f"  Using provided file ID: {file_id}")
    else:
        print(f"  Searching Drive for {project} permit drawing set...")
        files = search_drive_for_permit_set(project)
        if not files:
            print(f"  No permit drawing PDFs found for {project} in Drive search.")
            print("  Use --file-id <drive_file_id> to specify manually.")
            sys.exit(1)
        # Pick the largest / most recent PDF
        files.sort(key=lambda f: int(f.get("fileSize", 0)), reverse=True)
        chosen = files[0]
        file_id = chosen["id"]
        file_title = chosen.get("title", file_id)
        print(f"  Found: {file_title} ({int(chosen.get('fileSize',0))//1024//1024}MB)")

    # Step 2: Read file content via MCP gateway (text extraction)
    print(f"  Reading content via gateway drive reader...")
    try:
        resp = _api_call("GET", f"/gateway/drive/file/{file_id}/content")
        content = resp.get("payload", {}).get("content", "")
        if not content:
            raise ValueError("Empty content returned")
        print(f"  Content extracted: {len(content):,} characters")
    except Exception as e:
        print(f"  Gateway read failed: {e}")
        print("  Tip: The /gateway/drive/file/{id}/content endpoint may need to be added.")
        print("  Fallback: Use the MCP read_file_content tool directly from Claude Code session.")
        sys.exit(1)

    # Step 3: Analyze
    print(f"  Analyzing with Claude Sonnet...")
    analysis = analyze_with_claude(content, project)
    print(f"  Analysis complete ({len(analysis):,} chars)")

    # Step 4: Save
    result = {
        "project": project,
        "file_id": file_id,
        "file_title": file_title,
        "analyzed_at": datetime.now().isoformat(),
        "content_chars": len(content),
        "analysis": analysis
    }
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"  Saved: {out_path}")

    # Step 5: Send to GBT
    if not args.no_gbt:
        print(f"  Sending to GBT inbox...")
        fname = post_to_gbt_inbox(project, analysis, file_title)
        print(f"  GBT handoff: {fname}")

    print(f"\nDone. Analysis at: {out_path}\n")


if __name__ == "__main__":
    main()

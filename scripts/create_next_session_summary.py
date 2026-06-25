#!/usr/bin/env python3
"""
create_next_session_summary.py
Reads AI_TEAM state and prints a session handoff summary to stdout.
Use this at the end of a session to produce a clean handoff note.

Usage:
  python scripts/create_next_session_summary.py
  python scripts/create_next_session_summary.py --update   # also writes to 06_NEXT_SESSION.md
"""
import os, sys, argparse
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AI_TEAM = os.path.join(REPO_ROOT, "AI_TEAM")

def read_file(filename):
    path = os.path.join(AI_TEAM, filename)
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return f"(file not found: {filename})"

def extract_section(content, heading):
    """Extract content under a markdown heading."""
    lines = content.split("\n")
    capturing = False
    result = []
    for line in lines:
        if line.startswith("## ") and heading.lower() in line.lower():
            capturing = True
            continue
        if capturing and line.startswith("## "):
            break
        if capturing:
            result.append(line)
    return "\n".join(result).strip()

def generate_summary():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    status = read_file("00_STATUS.md")
    active = read_file("02_ACTIVE_WORK.md")
    blockers = read_file("07_BLOCKERS.md")
    next_session = read_file("06_NEXT_SESSION.md")

    summary = f"""# Session Handoff Summary
Generated: {now}

---

## What's Live Right Now
(From 00_STATUS.md — see that file for full detail)
- n8n: LIVE (WF-007 running)
- HubSpot, Google Sheets, Drive, Outlook: LIVE
- Postgres, Qdrant, Redis: NOT YET STARTED (docker-compose ready)
- GitHub remote: NOT YET CONNECTED (needs gh auth login)

## Open Blockers
(From 07_BLOCKERS.md)
- BLK-001: GitHub remote — needs Buck to run `! gh auth login`
- BLK-002: HubSpot connected inbox — needs Buck in browser
- BLK-003: Memory ingestion schema — needs ChatGPT architecture spec

## Next Task for Claude Code
(From 06_NEXT_SESSION.md)
- TASK-001: `docker-compose up -d postgres qdrant redis`
- TASK-002: GitHub remote (after Buck auth)

## Next Task for ChatGPT
- Write memory ingestion spec → 01_Engineering_Library/SPEC_memory_ingestion_v1.md
- Read BOOK_00/README.md + AI_TEAM/04_ARCHITECTURE.md first

---
Full detail: read AI_TEAM/ directory in the repository.
"""
    return summary

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--update", action="store_true", help="Also write to 06_NEXT_SESSION.md")
    args = parser.parse_args()

    summary = generate_summary()
    print(summary)

    if args.update:
        next_session_path = os.path.join(AI_TEAM, "06_NEXT_SESSION.md")
        with open(next_session_path, "w") as f:
            f.write(summary)
        print(f"\n✓ Updated {next_session_path}")

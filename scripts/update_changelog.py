#!/usr/bin/env python3
"""
update_changelog.py
Appends a new entry to AI_TEAM/08_CHANGELOG.md.

Usage:
  python scripts/update_changelog.py "Added memory ingestion pipeline for vendor_memory"
  python scripts/update_changelog.py --engineer "Claude Code" "Fixed WF-007 draft nodes"
"""
import sys, os, argparse
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHANGELOG_FILE = os.path.join(REPO_ROOT, "AI_TEAM", "08_CHANGELOG.md")

def append_entry(description: str, engineer: str = "Claude Code"):
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    entry = f"""
## {date_str} — {engineer}

### Changed
- {description}

"""
    with open(CHANGELOG_FILE, "r") as f:
        content = f.read()

    # Insert after the header block (after the first --- separator)
    insert_after = content.find("\n---\n") + 5
    new_content = content[:insert_after] + entry + content[insert_after:]

    with open(CHANGELOG_FILE, "w") as f:
        f.write(new_content)

    print(f"✓ Changelog updated: {description}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("description", help="What changed")
    parser.add_argument("--engineer", default="Claude Code", help="Who made the change")
    args = parser.parse_args()
    append_entry(args.description, args.engineer)

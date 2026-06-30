#!/usr/bin/env python3
"""
HCI AI Model Updater — keeps Gemini and Claude model IDs current automatically.

Queries the Gemini models API to find the latest available Flash and Pro models,
compares against what is set in .env, and updates if a newer version is available.

Run manually:  python3 tools/ai_model_updater.py
Run with flag: python3 tools/ai_model_updater.py --apply   (actually writes .env)
Scheduled:     called by n8n weekly workflow or cron
"""
import argparse, json, os, re, sys
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv

ENV_FILE = Path(__file__).parent.parent.parent / ".env"
load_dotenv(ENV_FILE)

GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")


def fetch_gemini_models() -> list:
    """List available Gemini models via google.genai SDK."""
    try:
        import google.genai as genai
    except ImportError:
        print("  google-genai not installed: pip install google-genai")
        return []
    try:
        client = genai.Client(api_key=GEMINI_KEY)
        models = list(client.models.list())
        return [{"name": f"models/{m.name}", "supportedGenerationMethods": ["generateContent"]} for m in models]
    except Exception as e:
        print(f"  Gemini model list error: {e}")
        return []


def _version_key(name: str) -> tuple:
    """
    Extract sortable version tuple from model name.
    'gemini-3.5-flash' → (3, 5, 0)
    'gemini-2.0-flash-exp' → (2, 0, 0)  — exp treated as 0 patch
    """
    nums = re.findall(r"(\d+)", name)
    ints = [int(n) for n in nums[:3]]
    while len(ints) < 3:
        ints.append(0)
    # demote experimental/preview models slightly
    if any(x in name for x in ("exp", "preview", "lite", "light")):
        ints[2] = -1
    return tuple(ints)


def best_model(models: list, family: str) -> str | None:
    """
    From the full model list, pick the highest stable version matching `family`.
    family = 'flash' or 'pro'
    Only matches standard gemini-X.Y-{family} pattern — excludes research/code/embedding variants.
    """
    candidates = []
    for m in models:
        name = m.get("name", "")   # e.g. "models/gemini-3.5-flash"
        short = name.split("/")[-1]
        # must start with gemini- and contain the family word as a distinct segment
        if not short.startswith("gemini-"):
            continue
        if family not in short.split("-"):
            continue
        # exclude specialized variants
        if any(x in short for x in ("lite", "light", "thinking", "code", "embedding", "aqa", "research", "vision", "nano")):
            continue
        # must support generateContent
        if "generateContent" not in m.get("supportedGenerationMethods", []):
            continue
        candidates.append(short)

    if not candidates:
        return None
    candidates.sort(key=_version_key, reverse=True)
    return candidates[0]


def update_env(key: str, value: str) -> bool:
    """Replace or append a key in .env. Returns True if value changed."""
    text = ENV_FILE.read_text()
    current_match = re.search(rf"^{key}=(.+)$", text, re.MULTILINE)
    current_val = current_match.group(1).strip() if current_match else None

    if current_val == value:
        return False

    if current_match:
        text = re.sub(rf"^{key}=.+$", f"{key}={value}", text, flags=re.MULTILINE)
    else:
        text = text.rstrip("\n") + f"\n{key}={value}\n"

    ENV_FILE.write_text(text)
    return True


def main():
    parser = argparse.ArgumentParser(description="HCI AI Model Updater")
    parser.add_argument("--apply", action="store_true", help="Write changes to .env (default: dry run)")
    parser.add_argument("--json", dest="as_json", action="store_true", help="Output JSON for n8n consumption")
    args = parser.parse_args()

    if not GEMINI_KEY:
        print("GEMINI_API_KEY not set — run Add_Gemini_Key.command on Desktop first")
        sys.exit(1)

    print(f"Querying Gemini model list...", flush=True)
    models = fetch_gemini_models()

    if not models:
        print("No models returned — check API key or network")
        sys.exit(1)

    print(f"  {len(models)} models available")

    flash_best = best_model(models, "flash")
    pro_best   = best_model(models, "pro")

    current_flash = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")
    current_pro   = os.environ.get("GEMINI_PRO_MODEL", "gemini-3.1-pro")

    result = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "current":   {"GEMINI_MODEL": current_flash, "GEMINI_PRO_MODEL": current_pro},
        "available": {"flash": flash_best, "pro": pro_best},
        "changes":   [],
        "applied":   args.apply,
    }

    if flash_best and flash_best != current_flash:
        result["changes"].append({"key": "GEMINI_MODEL", "from": current_flash, "to": flash_best})
    if pro_best and pro_best != current_pro:
        result["changes"].append({"key": "GEMINI_PRO_MODEL", "from": current_pro, "to": pro_best})

    if args.as_json:
        print(json.dumps(result, indent=2))
        return

    print(f"\n  Flash: {current_flash} → {flash_best or '(no change)'}")
    print(f"  Pro:   {current_pro} → {pro_best or '(no change)'}")

    if not result["changes"]:
        print("\n  Model IDs are current. No updates needed.")
        return

    if not args.apply:
        print(f"\n  DRY RUN: {len(result['changes'])} update(s) found. Re-run with --apply to write.")
        for c in result["changes"]:
            print(f"    {c['key']}: {c['from']} → {c['to']}")
        return

    for c in result["changes"]:
        changed = update_env(c["key"], c["to"])
        status = "UPDATED" if changed else "SKIPPED (already set)"
        print(f"  {c['key']}: {c['from']} → {c['to']}  [{status}]")

    print(f"\n  .env updated. Restart the API to apply: pkill -f 'uvicorn api.main' && nohup uvicorn api.main:app ... &")
    print("  Or run: curl -X POST http://localhost:8000/admin/reload (if hot-reload is enabled)")


if __name__ == "__main__":
    main()

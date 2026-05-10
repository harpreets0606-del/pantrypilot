"""
PATCH all .claude/bargain-chemist/templates/fixes/<id>.html into Klaviyo.

Uses Python's `requests` (different HTTP stack from curl on Windows — should not
hang the way curl.exe PATCH did). Each request has a hard 25s timeout and will
fall back to listing failures rather than hanging the script.

Usage (from repo root):
    python .claude/bargain-chemist/scripts/klaviyo_patch_templates.py
"""

import json
import os
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("ERROR: pip install requests   (then re-run)")

REPO = Path(__file__).resolve().parents[3]
FIXES_DIR = REPO / ".claude/bargain-chemist/templates/fixes"
ENV_FILE = REPO / ".env.local"


def load_key() -> str:
    if not ENV_FILE.exists():
        sys.exit(f"ERROR: {ENV_FILE} not found")
    # utf-8-sig strips BOM if present
    text = ENV_FILE.read_text(encoding="utf-8-sig")
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if line.startswith("KLAVIYO_PRIVATE_KEY"):
            _, _, val = line.partition("=")
            val = val.strip().strip('"').strip("'")
            if val:
                return val
    # Fallback: env var
    val = os.environ.get("KLAVIYO_PRIVATE_KEY", "").strip()
    if val:
        return val
    print("Lines seen in .env.local:", file=sys.stderr)
    for raw in text.splitlines():
        # mask any value
        if "=" in raw:
            k, _, _ = raw.partition("=")
            print(f"  {k.strip()!r}", file=sys.stderr)
    sys.exit("ERROR: KLAVIYO_PRIVATE_KEY not set in .env.local")


def main() -> int:
    key = load_key()
    headers_get = {
        "Authorization": f"Klaviyo-API-Key {key}",
        "revision": "2024-10-15",
        "Accept": "application/vnd.api+json",
    }
    headers_patch = dict(headers_get)
    headers_patch["Content-Type"] = "application/vnd.api+json"

    fixes = sorted(FIXES_DIR.glob("*.html"))
    if not fixes:
        sys.exit(f"ERROR: no .html files in {FIXES_DIR}")

    print(f"Found {len(fixes)} template fix files\n")

    ok, fail, skipped = [], [], []
    for path in fixes:
        tid = path.stem
        html = path.read_text(encoding="utf-8")
        body = {"data": {"type": "template", "id": tid, "attributes": {"html": html}}}

        url = f"https://a.klaviyo.com/api/templates/{tid}/"
        print(f"PATCH {tid} ({len(html)} chars) ... ", end="", flush=True)
        try:
            r = requests.patch(url, headers=headers_patch, json=body, timeout=25)
        except requests.RequestException as e:
            print(f"NETWORK FAIL: {e}")
            fail.append((tid, f"network: {e}"))
            continue

        if r.status_code == 200:
            print("200 OK")
            ok.append(tid)
        elif r.status_code == 404:
            print("404 (flow-attached, can't PATCH — UI paste required)")
            skipped.append(tid)
        else:
            preview = r.text[:200].replace("\n", " ")
            print(f"{r.status_code}  {preview}")
            fail.append((tid, f"{r.status_code}: {preview}"))
        time.sleep(0.3)  # polite

    print(f"\n=== DONE: {len(ok)} ok, {len(fail)} failed, {len(skipped)} flow-attached ===")
    if fail:
        print("\nFailed:")
        for tid, msg in fail:
            print(f"  {tid}: {msg}")
    if skipped:
        print("\nFlow-attached (apply via Klaviyo UI Source paste):")
        for tid in skipped:
            print(f"  https://www.klaviyo.com/template/{tid}")

    return 0 if not fail else 1


if __name__ == "__main__":
    raise SystemExit(main())

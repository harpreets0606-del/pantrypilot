"""Debug: print every action's action_type + relationships for each live flow.
Output goes to stdout AND to a file so we can inspect.
"""
import json
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("ERROR: pip install requests")

REPO = Path(__file__).resolve().parents[3]
ENV_FILE = REPO / ".env.local"
OUT = REPO / ".claude/bargain-chemist/snapshots/2026-05-07/flow-actions-raw.json"

LIVE_FLOWS = ["YdejKf", "RPQXaa", "Ua5LdS", "V9XmEm", "Ysj7sg"]
REVISION = "2025-10-15"


def load_key():
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
    sys.exit("ERROR: KLAVIYO_PRIVATE_KEY not found")


def gget(url, headers):
    r = requests.get(url, headers=headers, timeout=25)
    print(f"  GET {url} -> {r.status_code}")
    if r.status_code != 200:
        print(f"    body: {r.text[:300]}")
        return None
    return r.json()


def main():
    key = load_key()
    headers = {
        "Authorization": f"Klaviyo-API-Key {key}",
        "revision": REVISION,
        "Accept": "application/vnd.api+json",
    }
    raw = {}
    for fid in LIVE_FLOWS:
        flow = gget(f"https://a.klaviyo.com/api/flows/{fid}/?include=flow-actions", headers)
        if not flow:
            continue
        # Print ALL of `included` (these are the flow-action resources)
        included = flow.get("included", [])
        print(f"\n=== {fid} — {len(included)} included resources ===")
        for inc in included[:20]:
            t = inc.get("type")
            i = inc.get("id")
            attrs = inc.get("attributes", {}) or {}
            atype = attrs.get("action_type")
            print(f"  type={t} id={i} action_type={atype} attrs_keys={list(attrs.keys())[:8]}")
        raw[fid] = flow
    OUT.write_text(json.dumps(raw, indent=2))
    print(f"\nFull dump -> {OUT}")


if __name__ == "__main__":
    main()

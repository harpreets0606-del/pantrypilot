"""Pull FULL flow definition (triggers, profile_filter, actions, trigger-splits)
for every live flow. Uses the verified parameter `additional-fields[flow]=definition`
with revision 2025-10-15.

Output: snapshots/2026-05-07/flow-deep/<flowId>.json
"""
import json
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("ERROR: pip install requests")

REPO = Path(__file__).resolve().parents[3]
ENV_FILE = REPO / ".env.local"
OUT_DIR = REPO / ".claude/bargain-chemist/snapshots/2026-05-07/flow-deep"
OUT_DIR.mkdir(parents=True, exist_ok=True)

LIVE_FLOWS = ["RPQXaa", "T7pmf6", "Ua5LdS", "V9XmEm", "Y84ruV", "YdejKf", "Ysj7sg"]


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
    sys.exit("ERROR: KLAVIYO_PRIVATE_KEY missing")


def main():
    key = load_key()
    h = {
        "Authorization": f"Klaviyo-API-Key {key}",
        "revision": "2025-10-15",
        "Accept": "application/vnd.api+json",
    }
    for fid in LIVE_FLOWS:
        url = f"https://a.klaviyo.com/api/flows/{fid}/?additional-fields%5Bflow%5D=definition"
        try:
            r = requests.get(url, headers=h, timeout=30)
        except Exception as e:
            print(f"{fid}: NETWORK FAIL {e}")
            continue
        if r.status_code != 200:
            print(f"{fid}: HTTP {r.status_code}: {r.text[:200]}")
            continue
        body = r.json()
        out = OUT_DIR / f"{fid}.json"
        out.write_text(json.dumps(body, indent=2))
        defn = body.get("data", {}).get("attributes", {}).get("definition", {})
        triggers = defn.get("triggers", [])
        pf = defn.get("profile_filter", {})
        n_groups = len(pf.get("condition_groups", []))
        print(f"{fid}: {len(triggers)} trigger(s), profile_filter has {n_groups} condition group(s), {len(defn.get('actions',[]))} actions")
        time.sleep(0.2)
    print(f"\nDone. Saved to {OUT_DIR}")


if __name__ == "__main__":
    main()

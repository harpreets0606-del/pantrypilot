"""Try every Klaviyo API parameter combination to extract the FULL flow definition
including trigger filters, audience filters, and list bindings.

Tests:
1. additional-fields[flow]=definition  (returns full flow definition with trigger)
2. include=flow-actions,tags,trigger
3. revision 2025-10-15 vs 2024-10-15 (different versions expose different fields)
4. Whether trigger-split filters and audience filters are inside the flow-actions
   resource at deeper inspection
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
OUT_DIR = REPO / ".claude/bargain-chemist/snapshots/2026-05-07/flow-deep"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FLOWS_TO_TEST = ["Y84ruV", "V9XmEm"]


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


def hdrs(key, revision):
    return {
        "Authorization": f"Klaviyo-API-Key {key}",
        "revision": revision,
        "Accept": "application/vnd.api+json",
    }


def try_url(label, url, key, revision, save_name):
    print(f"\n--- {label} (rev {revision}) ---")
    print(f"    {url}")
    try:
        r = requests.get(url, headers=hdrs(key, revision), timeout=30)
    except Exception as e:
        print(f"    NETWORK FAIL: {e}")
        return None
    print(f"    HTTP {r.status_code}, body {len(r.text)} bytes")
    out = OUT_DIR / save_name
    try:
        out.write_text(json.dumps(r.json(), indent=2))
    except Exception:
        out.write_text(r.text)
    if r.status_code == 200:
        body = r.json()
        attrs = body.get("data", {}).get("attributes", {})
        print(f"    attribute keys: {list(attrs.keys())}")
        # Check if 'definition' is now populated
        if "definition" in attrs:
            defn = attrs["definition"]
            print(f"    DEFINITION keys: {list(defn.keys()) if isinstance(defn,dict) else type(defn).__name__}")
            print(f"    sample: {json.dumps(defn, indent=2)[:600]}")
        if "trigger" in attrs or "trigger_filters" in attrs or "audience_filter" in attrs or "smart_sending" in attrs:
            for k in ("trigger", "trigger_filters", "audience_filter", "smart_sending", "trigger_conditions"):
                if k in attrs:
                    print(f"    FOUND {k}: {json.dumps(attrs[k], indent=2)[:400]}")
        # Look in 'included' too for trigger details
        for inc in body.get("included", []):
            if inc.get("type") in ("flow-trigger", "list", "segment"):
                print(f"    INCLUDED {inc.get('type')} id={inc.get('id')}: {json.dumps(inc.get('attributes',{}), indent=2)[:300]}")
    else:
        print(f"    body: {r.text[:300]}")
    return r


def main():
    key = load_key()
    for fid in FLOWS_TO_TEST:
        print(f"\n========== {fid} ==========")

        # Test 1: Standard call (we already know this returns minimal data)
        try_url(f"{fid} basic", f"https://a.klaviyo.com/api/flows/{fid}/",
                key, "2025-10-15", f"{fid}-01-basic.json")

        # Test 2: Add additional-fields[flow]=definition
        try_url(f"{fid} additional-fields=definition",
                f"https://a.klaviyo.com/api/flows/{fid}/?additional-fields%5Bflow%5D=definition",
                key, "2025-10-15", f"{fid}-02-additional-definition.json")

        # Test 3: Older revision sometimes returns more
        try_url(f"{fid} additional-fields rev 2024-10-15",
                f"https://a.klaviyo.com/api/flows/{fid}/?additional-fields%5Bflow%5D=definition",
                key, "2024-10-15", f"{fid}-03-old-rev.json")

        # Test 4: include trigger
        try_url(f"{fid} include=trigger",
                f"https://a.klaviyo.com/api/flows/{fid}/?include=flow-actions,tags",
                key, "2025-10-15", f"{fid}-04-include-actions-tags.json")

        # Test 5: list trigger relationship endpoint
        try_url(f"{fid} relationships endpoint",
                f"https://a.klaviyo.com/api/flows/{fid}/relationships/tags/",
                key, "2025-10-15", f"{fid}-05-rels.json")


if __name__ == "__main__":
    main()

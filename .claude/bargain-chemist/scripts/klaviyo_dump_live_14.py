"""Dump current live HTML for the 14 templates that need editing.

Saves to .claude/bargain-chemist/templates/live/<id>.json
"""
import json
import os
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("ERROR: pip install requests")

REPO = Path(__file__).resolve().parents[3]
ENV_FILE = REPO / ".env.local"
OUT_DIR = REPO / ".claude/bargain-chemist/templates/live"

IDS = [
    "UpdhCT", "UVB5U8", "XgqKFQ",  # YdejKf Welcome Series
    "TgFsGf", "QRewz9",  # RPQXaa Cart Abandonment
    "VjuB7J", "WuTrZA", "U5svSu", "RDZzKn", "X3hegP", "SPqqDe",  # Ua5LdS Replenishment
    "SJwrxf", "YtcgUa",  # V9XmEm Flu Season
    "W2Sbja",  # Ysj7sg Back in Stock
]


def load_key() -> str:
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
    sys.exit("ERROR: KLAVIYO_PRIVATE_KEY not in .env.local")


def main() -> int:
    key = load_key()
    headers = {
        "Authorization": f"Klaviyo-API-Key {key}",
        "revision": "2024-10-15",
        "Accept": "application/vnd.api+json",
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fail = 0
    for tid in IDS:
        url = f"https://a.klaviyo.com/api/templates/{tid}/"
        try:
            r = requests.get(url, headers=headers, timeout=20)
        except requests.RequestException as e:
            print(f"{tid}: NETWORK FAIL {e}")
            fail += 1
            continue
        if r.status_code != 200:
            print(f"{tid}: HTTP {r.status_code}")
            fail += 1
            continue
        out = OUT_DIR / f"{tid}.json"
        out.write_text(r.text, encoding="utf-8")
        print(f"{tid}: saved ({len(r.text)} bytes)")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

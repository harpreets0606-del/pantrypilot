"""Verify Klaviyo Django supports {% elif %} for 3-way cart-value tier conditional.

Tests the same template HTML against 3 contexts (cart $value = 20, 50, 120)
and confirms expected output per tier.
"""
import json
import sys
import time
from datetime import date
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("ERROR: pip install requests")

REPO = Path(__file__).resolve().parents[3]
ENV_FILE = REPO / ".env.local"
OUT = REPO / f".claude/bargain-chemist/snapshots/{date.today():%Y-%m-%d}/probe-elif"
OUT.mkdir(parents=True, exist_ok=True)
TID = "UH72Vm"
REVISION = "2025-10-15"

TEMPLATE = """<html><body>
{% if event|lookup:'$value' < 30 %}TIER_A_SMALL{% elif event|lookup:'$value' < 79 %}TIER_B_GAP{% else %}TIER_C_QUALIFIED{% endif %}
</body></html>"""

CASES = [
    (20.0, "TIER_A_SMALL"),
    (50.0, "TIER_B_GAP"),
    (120.0, "TIER_C_QUALIFIED"),
]


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


def hdrs(key, content=False):
    h = {
        "Authorization": f"Klaviyo-API-Key {key}",
        "revision": REVISION,
        "Accept": "application/vnd.api+json",
    }
    if content:
        h["Content-Type"] = "application/vnd.api+json"
    return h


def main():
    key = load_key()
    # Snapshot rollback
    r = requests.get(f"https://a.klaviyo.com/api/templates/{TID}/",
                     headers=hdrs(key), timeout=20)
    r.raise_for_status()
    rollback = r.json()["data"]["attributes"]["html"]
    (OUT / "rollback.html").write_text(rollback, encoding="utf-8")

    # PATCH template with 3-tier elif test
    body = {"data": {"type": "template", "id": TID,
                     "attributes": {"html": TEMPLATE}}}
    r = requests.patch(f"https://a.klaviyo.com/api/templates/{TID}/",
                       headers=hdrs(key, content=True), json=body, timeout=20)
    r.raise_for_status()
    time.sleep(0.3)

    print("Testing 3-way elif with 3 cart values:")
    all_pass = True
    for value, expected in CASES:
        body = {"data": {"type": "template", "attributes": {
            "id": TID,
            "context": {
                "first_name": "Sam",
                "organization": {"full_address": "1 Test St"},
                "event": {"$value": value},
            }
        }}}
        r = requests.post("https://a.klaviyo.com/api/template-render/",
                          headers=hdrs(key, content=True), json=body, timeout=20)
        ok = r.status_code == 200 and expected in r.text
        result = "PASS" if ok else "FAIL"
        all_pass = all_pass and ok
        body_preview = r.text[:200].replace("\n", " ")
        print(f"  $value={value:>6.2f} expect={expected:<20}  {result}  http={r.status_code}")
        (OUT / f"v{int(value)}.json").write_text(
            json.dumps({"status": r.status_code, "expected": expected, "body": r.text[:2000]}, indent=2),
            encoding="utf-8")

    # Rollback
    body = {"data": {"type": "template", "id": TID,
                     "attributes": {"html": rollback}}}
    r = requests.patch(f"https://a.klaviyo.com/api/templates/{TID}/",
                       headers=hdrs(key, content=True), json=body, timeout=20)
    r.raise_for_status()

    print(f"\nResult: {'ALL TIERS RENDER CORRECTLY' if all_pass else 'FAILED — elif may not be supported'}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())

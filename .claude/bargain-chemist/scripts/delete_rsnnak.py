"""DELETE RSnNak (Browse Abandonment - Triple Pixel) — destructive, irreversible.

Why: RSnNak is a duplicate of RtiVC5. Both trigger on Viewed Product
(RSnNak via Triple Whale's YwbXgN, RtiVC5 via Klaviyo native XQ2zfW).
If both go LIVE, profiles get TWO emails per browse session — bad
subscriber experience. RtiVC5 is the canonical version (no third-party
dependency, faster delay, higher historical engagement).

This script:
  1. Confirms RSnNak exists + is DRAFT (refuses to delete LIVE flows)
  2. Prompts for explicit 'yes delete' confirmation (interactive)
  3. DELETEs /api/flows/RSnNak/
  4. Verifies the flow no longer appears in flow list

Run locally:
    python .claude/bargain-chemist/scripts/delete_rsnnak.py
"""
import json
import sys
from datetime import date
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("ERROR: pip install requests")

REPO = Path(__file__).resolve().parents[3]
ENV_FILE = REPO / ".env.local"
OUT = REPO / f".claude/bargain-chemist/snapshots/{date.today():%Y-%m-%d}/delete-rsnnak"
OUT.mkdir(parents=True, exist_ok=True)
TARGET = "RSnNak"
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
    sys.exit("ERROR: KLAVIYO_PRIVATE_KEY missing")


def hdrs(key):
    return {"Authorization": f"Klaviyo-API-Key {key}",
            "revision": REVISION,
            "Accept": "application/vnd.api+json"}


def main():
    key = load_key()
    print(f"=== DELETE flow {TARGET} ===")
    print(f"⚠️  IRREVERSIBLE. Cloned templates will orphan but stay in templates list.\n")

    # Verify current state
    r = requests.get(f"https://a.klaviyo.com/api/flows/{TARGET}/",
                     headers=hdrs(key), timeout=30)
    (OUT / "before.json").write_text(json.dumps({"status": r.status_code, "body": r.text[:3000]}, indent=2), encoding="utf-8")
    if r.status_code == 404:
        print(f"  Flow {TARGET} already gone (404). Nothing to do.")
        return 0
    if r.status_code != 200:
        sys.exit(f"❌ GET {TARGET}: HTTP {r.status_code}")
    attrs = r.json()["data"]["attributes"]
    status = attrs.get("status")
    name = attrs.get("name")
    print(f"  Name:   {name}")
    print(f"  Status: {status}")
    if status == "live":
        sys.exit(f"❌ Refusing to delete a LIVE flow. Set status=manual or draft first.")

    # Confirmation
    print(f"\n  About to DELETE '{name}' (id={TARGET}, status={status}).")
    print(f"  Reason: duplicate of RtiVC5 (both trigger on Viewed Product).")
    answer = input(f"  Type 'yes delete' to confirm: ").strip()
    if answer != "yes delete":
        print(f"  Aborted (you typed: {answer!r}).")
        return 1

    # Delete
    r = requests.delete(f"https://a.klaviyo.com/api/flows/{TARGET}/",
                        headers=hdrs(key), timeout=30)
    (OUT / "delete-response.json").write_text(json.dumps({"status": r.status_code, "body": r.text[:1000]}, indent=2), encoding="utf-8")
    if r.status_code in (200, 204):
        print(f"  ✅ DELETE HTTP {r.status_code} — {TARGET} deleted")
    else:
        sys.exit(f"❌ DELETE failed HTTP {r.status_code}\n{r.text[:500]}")

    # Verify
    r = requests.get(f"https://a.klaviyo.com/api/flows/{TARGET}/",
                     headers=hdrs(key), timeout=30)
    if r.status_code == 404:
        print(f"  ✅ Verified gone (HTTP 404)")
        return 0
    else:
        print(f"  ⚠️  unexpected — GET after DELETE returned HTTP {r.status_code}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

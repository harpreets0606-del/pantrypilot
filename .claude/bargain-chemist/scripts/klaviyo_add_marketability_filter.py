"""Add 'canReceiveMarketing: true' audience filter to flows that lack it.

Target flows (verified via API today):
  Y84ruV — Abandoned Checkout    — currently missing marketability gate
  Ua5LdS — Replenishment          — currently missing marketability gate
  T7pmf6 — Win-back               — currently missing marketability gate

Workflow per flow:
  1. GET /api/flows/{id}?additional-fields[flow]=definition  (rev 2025-10-15)
  2. Save current definition as rollback snapshot
  3. Build new definition: append condition_group with marketability filter
  4. PATCH /api/flows/{id}/  with the new definition
  5. GET back + verify the new group is present
  6. Report

Run with --dry-run to see what WOULD happen without sending the PATCH.
Run with --apply to actually apply.

NOTE: Klaviyo's PATCH /api/flows/{id} accepting `definition` may or may not be
supported — Klaviyo docs are inconsistent on this. If PATCH 4xx, the script
prints the response and stops; user can fall back to UI fix.
"""
import argparse
import copy
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
SNAP_DIR = REPO / f".claude/bargain-chemist/snapshots/{date.today():%Y-%m-%d}/audience-filter-fix"
SNAP_DIR.mkdir(parents=True, exist_ok=True)

REVISION = "2025-10-15"

TARGET_FLOWS = [
    ("Y84ruV", "Abandoned Checkout"),
    ("Ua5LdS", "Replenishment"),
    ("T7pmf6", "Win-back"),
]

# The condition group we're adding to each flow's profile_filter
MARKETABILITY_GROUP = {
    "conditions": [
        {
            "type": "profile-marketing-consent",
            "consent": {
                "channel": "email",
                "can_receive_marketing": True,
                "consent_status": {"subscription": "any", "filters": None},
            },
        }
    ]
}


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


def save(name, r):
    p = SNAP_DIR / name
    try: p.write_text(json.dumps(r.json(), indent=2))
    except Exception: p.write_text(r.text)


def has_marketability(profile_filter):
    """Detect if profile_filter already contains a marketing-consent condition."""
    if not profile_filter:
        return False
    for cg in profile_filter.get("condition_groups", []):
        for cond in cg.get("conditions", []):
            if cond.get("type") == "profile-marketing-consent":
                return True
    return False


def get_flow_definition(flow_id, key):
    url = f"https://a.klaviyo.com/api/flows/{flow_id}/?additional-fields%5Bflow%5D=definition"
    r = requests.get(url, headers=hdrs(key), timeout=30)
    save(f"{flow_id}-01-before.json", r)
    if r.status_code != 200:
        raise RuntimeError(f"GET {flow_id} HTTP {r.status_code}: {r.text[:200]}")
    return r.json()


def patch_flow_definition(flow_id, new_definition, key):
    body = {
        "data": {
            "type": "flow",
            "id": flow_id,
            "attributes": {"definition": new_definition},
        }
    }
    url = f"https://a.klaviyo.com/api/flows/{flow_id}/"
    r = requests.patch(url, headers=hdrs(key, content=True), json=body, timeout=30)
    save(f"{flow_id}-02-patch-response.json", r)
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Actually apply (default: dry-run)")
    args = ap.parse_args()

    key = load_key()
    print(f"Mode: {'APPLY' if args.apply else 'DRY-RUN'}")
    print(f"Snapshots -> {SNAP_DIR}\n")

    for flow_id, label in TARGET_FLOWS:
        print(f"\n=== {flow_id} — {label} ===")
        try:
            body = get_flow_definition(flow_id, key)
        except Exception as e:
            print(f"  GET fail: {e}")
            continue

        defn = body["data"]["attributes"]["definition"] or {}
        pf = defn.get("profile_filter") or {"condition_groups": []}

        if has_marketability(pf):
            print("  ALREADY HAS marketability filter — skipping")
            continue

        before_count = len(pf.get("condition_groups") or [])
        new_pf = copy.deepcopy(pf)
        new_pf.setdefault("condition_groups", []).append(MARKETABILITY_GROUP)
        new_defn = copy.deepcopy(defn)
        new_defn["profile_filter"] = new_pf
        after_count = len(new_pf["condition_groups"])
        print(f"  groups: {before_count} -> {after_count} (added marketability)")

        if not args.apply:
            print(f"  DRY-RUN: would PATCH /api/flows/{flow_id}/")
            continue

        r = patch_flow_definition(flow_id, new_defn, key)
        if r.status_code != 200:
            print(f"  PATCH FAIL HTTP {r.status_code}: {r.text[:400]}")
            print("  -> may need UI fix instead")
            continue
        print(f"  PATCH OK")

        # Verify
        time.sleep(0.5)
        try:
            verify = get_flow_definition(flow_id, key)
        except Exception as e:
            print(f"  VERIFY GET fail: {e}")
            continue
        save(f"{flow_id}-03-after.json", type("R", (), {"json": lambda self=verify: verify, "text": json.dumps(verify)})())
        new_pf2 = (verify["data"]["attributes"].get("definition") or {}).get("profile_filter") or {}
        if has_marketability(new_pf2):
            print(f"  VERIFIED: marketability filter is now live")
        else:
            print(f"  VERIFY FAIL: marketability not present after PATCH (review response)")

    print("\nDone.")
    if not args.apply:
        print("\nThis was a DRY-RUN. To apply, re-run with --apply")


if __name__ == "__main__":
    main()

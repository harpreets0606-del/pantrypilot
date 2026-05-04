"""
Reads back the definitions of the 3 rebuilt flows and prints a summary
of every conditional-split's profile_filter so we can confirm conditions
were saved correctly.

Usage:
    $env:KLAVIYO_API_KEY="pk_xxx"
    py verify_conditions.py
"""

import os, sys, json, requests, time

API_KEY  = os.environ.get("KLAVIYO_API_KEY", "")
REVISION = "2024-10-15.pre"
BASE_URL = "https://a.klaviyo.com/api"

HEADERS = {
    "Authorization": f"Klaviyo-API-Key {API_KEY}",
    "revision": REVISION,
    "Accept": "application/json",
}

FLOWS = {
    "UqpyKS": "[Z] Back in Stock",
    "Vvb9ik": "[Z] Post-Purchase Series",
    "XKmyJE": "[Z] Replenishment - Reorder Reminders",
}


def main():
    if not API_KEY:
        print("ERROR: Set KLAVIYO_API_KEY env var.")
        sys.exit(1)

    all_ok = True

    for flow_id, name in FLOWS.items():
        print(f"\n{'='*60}")
        print(f"{name} ({flow_id})")
        print('='*60)

        r = requests.get(
            f"{BASE_URL}/flows/{flow_id}",
            headers=HEADERS,
            params={"additional-fields[flow]": "definition"},
            timeout=15,
        )
        if not r.ok:
            print(f"  ERROR: {r.status_code} {r.text[:200]}")
            all_ok = False
            continue

        defn = r.json()["data"]["attributes"].get("definition", {})
        actions = defn.get("actions", [])
        splits = [a for a in actions if a.get("type") == "conditional-split"]

        print(f"  Total actions : {len(actions)}")
        print(f"  Splits found  : {len(splits)}")

        for i, split in enumerate(splits):
            pf = split.get("data", {}).get("profile_filter")
            split_id = split.get("id", "?")
            if pf is None:
                print(f"\n  [SPLIT {i+1}] id={split_id}  profile_filter: NULL (not set)")
                all_ok = False
            else:
                cgs = pf.get("condition_groups", [])
                if not cgs or not cgs[0].get("conditions"):
                    print(f"\n  [SPLIT {i+1}] id={split_id}  profile_filter: EMPTY (no conditions)")
                    all_ok = False
                else:
                    cond = cgs[0]["conditions"][0]
                    ctype = cond.get("type")
                    mid   = cond.get("metric_id", "?")
                    op    = cond.get("measurement_filter", {}).get("operator", "?")
                    val   = cond.get("measurement_filter", {}).get("value", "?")
                    tf    = cond.get("timeframe_filter", {}).get("operator", "?")
                    mf    = cond.get("metric_filters")
                    mf_str = ""
                    if mf:
                        kw = mf[0].get("filter", {}).get("value", "?")
                        mf_str = f"  item contains '{kw}'"
                    print(f"\n  [SPLIT {i+1}] id={split_id}")
                    print(f"    type       : {ctype}")
                    print(f"    metric_id  : {mid}")
                    print(f"    condition  : count {op} {val} since {tf}{mf_str}")

        time.sleep(0.2)

    print()
    print("=" * 60)
    if all_ok:
        print("PASS - All splits have configured conditions.")
    else:
        print("FAIL - Some splits are missing conditions.")
    print("=" * 60)


if __name__ == "__main__":
    main()

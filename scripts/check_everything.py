#!/usr/bin/env python3
"""
Comprehensive audit + cleanup:

1. Create probe segments to quantify undercount caused by missing
   retail sub-collections (_retail-import, _retail-fragrance,
   _retail-clearance).
2. Create probe for Cart Abandoners without the _retail filter on
   Checkout Started (which has been confirmed to inconsistently
   carry _retail).
3. Delete 4 leftover test segments from previous probes.
4. Report final state with all comparisons.

Run:
    KLAVIYO_API_KEY="pk_xxx" python3 scripts/check_everything.py
"""

import os
import sys
import time

import requests

KLAVIYO_BASE = "https://a.klaviyo.com/api"
REVISION = "2024-10-15"
PLACED_ORDER = "Sxnb5T"
CHECKOUT_STARTED = "VvcTue"

ALL_RETAIL_COLLECTIONS = ["_retail", "_retail-import", "_retail-fragrance", "_retail-clearance"]

CONSENT_GROUP = {
    "conditions": [
        {
            "type": "profile-marketing-consent",
            "consent": {
                "channel": "email",
                "can_receive_marketing": True,
                "consent_status": {"subscription": "subscribed", "filters": None},
            },
        }
    ]
}


def metric_cond(metric_id, op, value, days, metric_filters=None, range_op="in-the-last"):
    return {
        "conditions": [
            {
                "type": "profile-metric",
                "metric_id": metric_id,
                "measurement": "count",
                "measurement_filter": {"type": "numeric", "operator": op, "value": value},
                "timeframe_filter": {"type": "date", "operator": range_op, "unit": "day", "quantity": days},
                "metric_filters": metric_filters,
            }
        ]
    }


# -------- Probes to create --------
PROBES = [
    {
        "name": "PROBE — All Retail (all 4 retail collections, 1095d)",
        "compare_to": ("VvBRbu", 59_317),
        "condition_groups": [
            metric_cond(
                PLACED_ORDER, "greater-than", 0, 1095,
                metric_filters=[
                    {"property": "Collections", "filter": {"type": "list", "operator": "contains-any", "value": ALL_RETAIL_COLLECTIONS}}
                ],
            ),
            CONSENT_GROUP,
        ],
    },
    {
        "name": "PROBE — Cart Abandoners 30d NO retail filter on Checkout (control)",
        "compare_to": ("VrP6TT", 620),
        "condition_groups": [
            metric_cond(CHECKOUT_STARTED, "greater-than", 0, 30, metric_filters=None),
            metric_cond(
                PLACED_ORDER, "equals", 0, 30,
                metric_filters=[
                    {"property": "Collections", "filter": {"type": "list", "operator": "contains-any", "value": ALL_RETAIL_COLLECTIONS}}
                ],
            ),
            CONSENT_GROUP,
        ],
    },
    {
        "name": "PROBE — Cart Abandoners 30d with ALL retail collections on both conditions",
        "compare_to": ("VrP6TT", 620),
        "condition_groups": [
            metric_cond(
                CHECKOUT_STARTED, "greater-than", 0, 30,
                metric_filters=[
                    {"property": "Collections", "filter": {"type": "list", "operator": "contains-any", "value": ALL_RETAIL_COLLECTIONS}}
                ],
            ),
            metric_cond(
                PLACED_ORDER, "equals", 0, 30,
                metric_filters=[
                    {"property": "Collections", "filter": {"type": "list", "operator": "contains-any", "value": ALL_RETAIL_COLLECTIONS}}
                ],
            ),
            CONSENT_GROUP,
        ],
    },
]


# -------- Segments to DELETE (cleanup) --------
SEGMENTS_TO_DELETE = [
    ("Vbgzfa", "BC — New Retail Customers L30D v2 (equivalent to VQ8Sz4)"),
    ("X4jH73", "BC — High AOV Retail v2 ($45+) — broken (0 profiles)"),
    ("TkWFx7", "PROBE 1 — $value > 0.01"),
    ("V4KiGc", "PROBE 3 — Collections control"),
]


def headers(api_key):
    return {
        "Authorization": f"Klaviyo-API-Key {api_key}",
        "accept": "application/vnd.api+json",
        "revision": REVISION,
        "content-type": "application/vnd.api+json",
    }


def create_segment(api_key, name, condition_groups):
    body = {
        "data": {
            "type": "segment",
            "attributes": {"name": name, "definition": {"condition_groups": condition_groups}},
        }
    }
    return requests.post(f"{KLAVIYO_BASE}/segments/", headers=headers(api_key), json=body, timeout=30)


def poll_count(api_key, segment_id, max_attempts=15):
    for attempt in range(max_attempts):
        time.sleep(3)
        url = f"{KLAVIYO_BASE}/segments/{segment_id}/?additional-fields[segment]=profile_count"
        r = requests.get(url, headers=headers(api_key), timeout=30)
        if r.status_code != 200:
            continue
        attrs = r.json()["data"]["attributes"]
        if not attrs.get("is_processing") and attrs.get("profile_count") is not None:
            return attrs["profile_count"]
        print(f"  ...still processing (attempt {attempt + 1}/{max_attempts})")
    return None


def delete_segment(api_key, segment_id):
    return requests.delete(f"{KLAVIYO_BASE}/segments/{segment_id}/", headers=headers(api_key), timeout=30)


def main():
    api_key = os.environ.get("KLAVIYO_API_KEY")
    if not api_key:
        print("ERROR: KLAVIYO_API_KEY env var not set", file=sys.stderr)
        sys.exit(1)

    print("=" * 70)
    print("STEP 1: PROBE SEGMENTS (quantify undercount from missing collections)")
    print("=" * 70)

    probe_results = []
    for probe in PROBES:
        print(f"\n--- {probe['name']} ---")
        r = create_segment(api_key, probe["name"], probe["condition_groups"])
        if r.status_code not in (200, 201):
            print(f"  FAILED ({r.status_code}): {r.text[:500]}")
            probe_results.append({"name": probe["name"], "error": r.text[:200], "compare_to": probe["compare_to"]})
            continue
        new_id = r.json()["data"]["id"]
        print(f"  Created: {new_id}")
        count = poll_count(api_key, new_id)
        probe_results.append({"name": probe["name"], "id": new_id, "count": count, "compare_to": probe["compare_to"]})

    print("\n" + "=" * 70)
    print("STEP 2: CLEANUP — DELETE TEST/PROBE SEGMENTS")
    print("=" * 70)
    delete_results = []
    for seg_id, label in SEGMENTS_TO_DELETE:
        print(f"\n--- Deleting {seg_id} ({label}) ---")
        r = delete_segment(api_key, seg_id)
        ok = r.status_code in (200, 204)
        marker = "OK" if ok else f"FAIL {r.status_code}"
        print(f"  {marker}: {r.text[:200] if not ok else 'deleted'}")
        delete_results.append({"id": seg_id, "label": label, "ok": ok, "code": r.status_code})

    print("\n" + "=" * 70)
    print("FINAL REPORT")
    print("=" * 70)

    print("\nProbe results:")
    for r in probe_results:
        if "error" in r:
            print(f"  [FAIL]    {r['name']}: {r['error']}")
            continue
        baseline_id, baseline_count = r["compare_to"]
        cnt = r["count"]
        if cnt is None:
            print(f"  [TIMEOUT] {r['name']}: count not returned")
            continue
        delta = cnt - baseline_count
        pct = (100 * delta / baseline_count) if baseline_count else 0
        sign = "+" if delta >= 0 else ""
        print(f"  {r['name']}")
        print(f"    new={cnt:,}  baseline ({baseline_id})={baseline_count:,}  delta={sign}{delta:,} ({sign}{pct:.1f}%)")
        print(f"    new segment id: {r['id']}")

    print("\nDeletion results:")
    for d in delete_results:
        marker = "✓" if d["ok"] else f"✗ ({d['code']})"
        print(f"  {marker} {d['id']} — {d['label']}")

    print("\nNext steps suggested:")
    print("  - If 'All Retail with 4 collections' delta is large (e.g. +20%+), rebuild")
    print("    affected retail segments to use all 4 collections.")
    print("  - If Cart Abandoners probes show large delta, rebuild VrP6TT and Ti4FKX.")
    print("  - High AOV (WkwEvG) still requires Klaviyo UI build — API can't.")


if __name__ == "__main__":
    main()

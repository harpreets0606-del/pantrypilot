#!/usr/bin/env python3
"""
Diagnostic probe script: figure out the correct Klaviyo segment API
construct for filtering Placed Order events by $value.

Creates 3 probe segments testing different hypotheses about why
filtering by `$value` numeric property returns 0 profiles when
the data clearly exists (AOV ~$67 confirmed via aggregate API).

Run:
    KLAVIYO_API_KEY="pk_xxx" python3 scripts/probe_value_filter.py

The probes are named "PROBE — ..." so they're easy to delete after.
"""

import os
import sys
import time
import requests

KLAVIYO_BASE = "https://a.klaviyo.com/api"
REVISION = "2024-10-15"
PLACED_ORDER = "Sxnb5T"


def headers(api_key):
    return {
        "Authorization": f"Klaviyo-API-Key {api_key}",
        "accept": "application/vnd.api+json",
        "revision": REVISION,
        "content-type": "application/vnd.api+json",
    }


# --- 3 different hypotheses ---

# Hypothesis 1: replicate the failing pattern but with threshold > 0.01 (essentially any value)
# If this is also 0, the property filter on $value via metric_filters is broken regardless of threshold.
PROBE_1 = {
    "name": "PROBE 1 — $value > 0.01 via metric_filters",
    "condition_groups": [
        {
            "conditions": [
                {
                    "type": "profile-metric",
                    "metric_id": PLACED_ORDER,
                    "measurement": "count",
                    "measurement_filter": {"type": "numeric", "operator": "greater-than", "value": 0},
                    "timeframe_filter": {"type": "date", "operator": "in-the-last", "unit": "day", "quantity": 1095},
                    "metric_filters": [
                        {"property": "$value", "filter": {"type": "numeric", "operator": "greater-than", "value": 0.01}}
                    ],
                }
            ]
        }
    ],
}

# Hypothesis 2: use measurement="sum_value" with measurement_filter directly on the sum
# This is "profile's lifetime order revenue > $45" — different semantics from per-order $45,
# but it proves whether the value-based measurement engine works at all.
PROBE_2 = {
    "name": "PROBE 2 — sum_value > 45 in last 1095d",
    "condition_groups": [
        {
            "conditions": [
                {
                    "type": "profile-metric",
                    "metric_id": PLACED_ORDER,
                    "measurement": "sum_value",
                    "measurement_filter": {"type": "numeric", "operator": "greater-than", "value": 45},
                    "timeframe_filter": {"type": "date", "operator": "in-the-last", "unit": "day", "quantity": 1095},
                    "metric_filters": None,
                }
            ]
        }
    ],
}

# Hypothesis 3: control — known-working list-property filter on same metric
# This proves the metric_filters mechanism works for non-numeric properties on Placed Order.
PROBE_3 = {
    "name": "PROBE 3 — Collections contains _retail (control, should match ~59k)",
    "condition_groups": [
        {
            "conditions": [
                {
                    "type": "profile-metric",
                    "metric_id": PLACED_ORDER,
                    "measurement": "count",
                    "measurement_filter": {"type": "numeric", "operator": "greater-than", "value": 0},
                    "timeframe_filter": {"type": "date", "operator": "in-the-last", "unit": "day", "quantity": 1095},
                    "metric_filters": [
                        {
                            "property": "Collections",
                            "filter": {"type": "list", "operator": "contains-any", "value": ["_retail"]},
                        }
                    ],
                }
            ]
        }
    ],
}


PROBES = [PROBE_1, PROBE_2, PROBE_3]


def create_segment(api_key, name, condition_groups):
    body = {
        "data": {
            "type": "segment",
            "attributes": {
                "name": name,
                "definition": {"condition_groups": condition_groups},
            },
        }
    }
    r = requests.post(f"{KLAVIYO_BASE}/segments/", headers=headers(api_key), json=body, timeout=30)
    return r


def get_count(api_key, segment_id):
    url = f"{KLAVIYO_BASE}/segments/{segment_id}/?additional-fields[segment]=profile_count"
    r = requests.get(url, headers=headers(api_key), timeout=30)
    return r


def main():
    api_key = os.environ.get("KLAVIYO_API_KEY")
    if not api_key:
        print("ERROR: KLAVIYO_API_KEY env var not set", file=sys.stderr)
        sys.exit(1)

    results = []
    for probe in PROBES:
        print(f"\n=== {probe['name']} ===")
        r = create_segment(api_key, probe["name"], probe["condition_groups"])
        if r.status_code not in (200, 201):
            print(f"  CREATE FAILED ({r.status_code}): {r.text[:500]}")
            results.append({"name": probe["name"], "error": r.text[:500]})
            continue

        new_id = r.json()["data"]["id"]
        print(f"  Created: {new_id}")

        count = None
        for attempt in range(15):
            time.sleep(3)
            r2 = get_count(api_key, new_id)
            if r2.status_code == 200:
                attrs = r2.json()["data"]["attributes"]
                is_processing = attrs.get("is_processing", True)
                count = attrs.get("profile_count")
                if not is_processing and count is not None:
                    break
                print(f"  ...still processing (attempt {attempt + 1}/15)")

        results.append({"name": probe["name"], "id": new_id, "count": count})

    print("\n\n=== PROBE SUMMARY ===")
    for r in results:
        if "error" in r:
            print(f"  [FAIL]  {r['name']}: {r['error']}")
            continue
        cnt = f"{r['count']:,}" if r["count"] is not None else "?"
        print(f"  [{cnt:>8}]  {r['name']} (id={r['id']})")

    print("\nInterpretation guide:")
    print("  PROBE 1 = 0    -> $value numeric metric_filter is broken via API")
    print("  PROBE 1 > 0    -> filter works; original threshold was just too high (impossible if AOV $67)")
    print("  PROBE 2 ~ 50k  -> sum_value works; use it for High AOV (lifetime spend, not per-order)")
    print("  PROBE 2 = 0    -> value-based measurements broken via API; only UI-built segments work")
    print("  PROBE 3 ~ 59k  -> metric_filters mechanism is fine for list properties (control)")


if __name__ == "__main__":
    main()

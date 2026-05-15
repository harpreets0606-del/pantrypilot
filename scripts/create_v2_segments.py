#!/usr/bin/env python3
"""
Create the 3 v2 Klaviyo segments via direct Klaviyo REST API.

Reads the Klaviyo Private API key from the KLAVIYO_API_KEY env var.
POSTs each segment, then re-reads each with profile count to verify.

Usage:
    KLAVIYO_API_KEY="pk_xxx" python3 scripts/create_v2_segments.py
"""

import json
import os
import sys
import time

import requests

KLAVIYO_BASE = "https://a.klaviyo.com/api"
REVISION = "2024-10-15"

# Metric IDs verified live this session
METRIC = {
    "placed_order": "Sxnb5T",
    "opened_email": "SZ8GZJ",
    "clicked_email": "W3AFKt",
    "viewed_product": "XQ2zfW",
    "active_on_site": "UfaNeY",
    "received_email": "UMyAwd",
}


def make_metric_group(metric_id, op, value, days, metric_filters=None, range_op="in-the-last"):
    cond = {
        "type": "profile-metric",
        "metric_id": metric_id,
        "measurement": "count",
        "measurement_filter": {"type": "numeric", "operator": op, "value": value},
        "timeframe_filter": {"type": "date", "operator": range_op, "unit": "day", "quantity": days},
        "metric_filters": metric_filters,
    }
    return {"conditions": [cond]}


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

RETAIL_FILTER = [
    {"property": "Collections", "filter": {"type": "list", "operator": "contains-any", "value": ["_retail"]}}
]

HIGH_VALUE_FILTER = [
    {"property": "$value", "filter": {"type": "numeric", "operator": "greater-than", "value": 45}}
]


SEGMENTS = [
    {
        "name": "BC — High AOV Retail v2 ($45+)",
        "expected_range": (8_000, 15_000),
        "condition_groups": [
            make_metric_group(METRIC["placed_order"], "greater-than", 0, 1095, HIGH_VALUE_FILTER),
            make_metric_group(METRIC["placed_order"], "greater-than", 0, 1095, RETAIL_FILTER),
            CONSENT_GROUP,
        ],
    },
    {
        "name": "BC — New Retail Customers L30D v2",
        "expected_range": (1_500, 2_000),
        "condition_groups": [
            make_metric_group(METRIC["placed_order"], "greater-than", 0, 30, RETAIL_FILTER),
            make_metric_group(METRIC["placed_order"], "equals", 1, 1095, RETAIL_FILTER),
            CONSENT_GROUP,
        ],
    },
    {
        "name": "BC — Unengaged Subscribed 180D v2 (sunset)",
        "expected_range": (25_000, 32_000),
        "condition_groups": [
            make_metric_group(METRIC["opened_email"], "equals", 0, 180),
            make_metric_group(METRIC["clicked_email"], "equals", 0, 180),
            make_metric_group(METRIC["viewed_product"], "equals", 0, 180),
            make_metric_group(METRIC["active_on_site"], "equals", 0, 180),
            make_metric_group(METRIC["placed_order"], "equals", 0, 180),
            make_metric_group(METRIC["received_email"], "greater-than", 0, 180),
            CONSENT_GROUP,
        ],
    },
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
            "attributes": {
                "name": name,
                "definition": {"condition_groups": condition_groups},
            },
        }
    }
    r = requests.post(f"{KLAVIYO_BASE}/segments/", headers=headers(api_key), json=body, timeout=30)
    return r


def get_segment_with_count(api_key, segment_id):
    url = f"{KLAVIYO_BASE}/segments/{segment_id}/?additional-fields[segment]=profile_count"
    r = requests.get(url, headers=headers(api_key), timeout=30)
    return r


def main():
    api_key = os.environ.get("KLAVIYO_API_KEY")
    if not api_key:
        print("ERROR: KLAVIYO_API_KEY env var not set", file=sys.stderr)
        sys.exit(1)
    if not api_key.startswith("pk_"):
        print(f"WARNING: API key does not start with 'pk_' (got prefix {api_key[:3]!r}). "
              "Klaviyo private keys typically start with 'pk_'. Continuing anyway.", file=sys.stderr)

    results = []
    for seg in SEGMENTS:
        print(f"\n=== Creating: {seg['name']} ===")
        r = create_segment(api_key, seg["name"], seg["condition_groups"])
        if r.status_code not in (200, 201):
            print(f"  FAILED ({r.status_code}): {r.text[:500]}")
            results.append({"name": seg["name"], "status": "FAILED", "error": r.text[:500]})
            continue

        new_id = r.json()["data"]["id"]
        print(f"  Created: {new_id}")

        # Segment processing is async — Klaviyo computes count in the background.
        # Give it a moment, then poll.
        count = None
        for attempt in range(10):
            time.sleep(3)
            r2 = get_segment_with_count(api_key, new_id)
            if r2.status_code == 200:
                attrs = r2.json()["data"]["attributes"]
                is_processing = attrs.get("is_processing", True)
                count = attrs.get("profile_count")
                if not is_processing and count is not None:
                    break
                print(f"  ...still processing (attempt {attempt + 1}/10)")

        lo, hi = seg["expected_range"]
        ok = count is not None and lo <= count <= hi
        marker = "OK" if ok else ("UNDER" if count is not None and count < lo else "OVER")
        results.append({
            "name": seg["name"],
            "id": new_id,
            "count": count,
            "expected": f"{lo:,}–{hi:,}",
            "verdict": marker if count is not None else "TIMEOUT",
        })

    print("\n\n=== SUMMARY ===")
    for r in results:
        if "id" in r:
            cnt = f"{r['count']:,}" if r["count"] is not None else "?"
            print(f"  [{r['verdict']:8}] {r['name']}: {cnt} (expected {r['expected']}) — id={r['id']}")
        else:
            print(f"  [FAILED] {r['name']}: {r.get('error', 'unknown')}")


if __name__ == "__main__":
    main()

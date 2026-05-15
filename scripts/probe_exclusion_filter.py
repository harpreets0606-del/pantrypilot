#!/usr/bin/env python3
"""
Test if Klaviyo's segments API accepts a 'does-not-contain-any'
operator on metric_filters Collections — to build a clean retail-only
cart abandoners segment that captures the ~2,000 events missing the
_retail tag while still excluding pharmacy.

If Klaviyo accepts this filter, the resulting segment is the ideal
audience for Google Ads Customer Match: maximum retail coverage,
zero pharmacy contamination.

If Klaviyo rejects it (HTTP 400), we fall back to keeping VrP6TT at 620.

Run:
    KLAVIYO_API_KEY="pk_xxx" python3 scripts/probe_exclusion_filter.py
"""

import os
import sys
import time

import requests

KLAVIYO_BASE = "https://a.klaviyo.com/api"
REVISION = "2024-10-15"
PLACED_ORDER = "Sxnb5T"
CHECKOUT_STARTED = "VvcTue"

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


def headers(api_key):
    return {
        "Authorization": f"Klaviyo-API-Key {api_key}",
        "accept": "application/vnd.api+json",
        "revision": REVISION,
        "content-type": "application/vnd.api+json",
    }


# Try several operator names in case Klaviyo uses different syntax
EXCLUSION_OPERATORS_TO_TEST = [
    "does-not-contain-any",
    "not-contains-any",
    "contains-none",
    "excludes-any",
]


def make_probe(operator_name):
    return {
        "name": f"PROBE EXCL — Cart Aban 30d ({operator_name})",
        "definition": {
            "condition_groups": [
                # Group 1: Started a checkout in 30d, NOT pharmacy
                {
                    "conditions": [
                        {
                            "type": "profile-metric",
                            "metric_id": CHECKOUT_STARTED,
                            "measurement": "count",
                            "measurement_filter": {"type": "numeric", "operator": "greater-than", "value": 0},
                            "timeframe_filter": {"type": "date", "operator": "in-the-last", "unit": "day", "quantity": 30},
                            "metric_filters": [
                                {
                                    "property": "Collections",
                                    "filter": {
                                        "type": "list",
                                        "operator": operator_name,
                                        "value": ["_pharmacy-only", "_pharmacist-only"],
                                    },
                                }
                            ],
                        }
                    ]
                },
                # Group 2: Did NOT place a retail order in 30d
                {
                    "conditions": [
                        {
                            "type": "profile-metric",
                            "metric_id": PLACED_ORDER,
                            "measurement": "count",
                            "measurement_filter": {"type": "numeric", "operator": "equals", "value": 0},
                            "timeframe_filter": {"type": "date", "operator": "in-the-last", "unit": "day", "quantity": 30},
                            "metric_filters": [
                                {
                                    "property": "Collections",
                                    "filter": {
                                        "type": "list",
                                        "operator": "contains-any",
                                        "value": ["_retail", "_retail-import", "_retail-fragrance", "_retail-clearance"],
                                    },
                                }
                            ],
                        }
                    ]
                },
                CONSENT_GROUP,
            ]
        },
    }


def main():
    api_key = os.environ.get("KLAVIYO_API_KEY")
    if not api_key:
        print("ERROR: KLAVIYO_API_KEY env var not set", file=sys.stderr)
        sys.exit(1)

    print("Testing exclusion-filter operators on metric_filters...")
    print()

    winner = None
    winner_count = None
    winner_id = None

    for op in EXCLUSION_OPERATORS_TO_TEST:
        print(f"--- Operator: {op!r} ---")
        body = {"data": {"type": "segment", "attributes": make_probe(op)}}
        r = requests.post(f"{KLAVIYO_BASE}/segments/", headers=headers(api_key), json=body, timeout=30)

        if r.status_code in (200, 201):
            seg_id = r.json()["data"]["id"]
            print(f"  Accepted by API. Segment {seg_id} created. Polling count...")

            count = None
            for _ in range(15):
                time.sleep(3)
                url = f"{KLAVIYO_BASE}/segments/{seg_id}/?additional-fields[segment]=profile_count"
                r2 = requests.get(url, headers=headers(api_key), timeout=30)
                if r2.status_code != 200:
                    continue
                attrs = r2.json()["data"]["attributes"]
                if not attrs.get("is_processing") and attrs.get("profile_count") is not None:
                    count = attrs["profile_count"]
                    break
                print("    still processing...")

            print(f"  RESULT: {count:,} profiles" if count is not None else "  RESULT: timeout")
            if count is not None and count > 0:
                winner = op
                winner_count = count
                winner_id = seg_id
                break  # found a working operator — don't create more segments
            else:
                # Delete the zero-count segment to keep things clean
                requests.delete(f"{KLAVIYO_BASE}/segments/{seg_id}/", headers=headers(api_key), timeout=30)
        else:
            print(f"  REJECTED ({r.status_code}): {r.text[:300]}")
        print()

    print("=" * 60)
    print("FINAL")
    print("=" * 60)
    if winner:
        print(f"WORKING operator: {winner!r}")
        print(f"Segment id: {winner_id}")
        print(f"Profile count: {winner_count:,}")
        print()
        print("Comparison:")
        print(f"  VrP6TT (current, _retail filter)    : 620")
        print(f"  XF2frD (no Checkout filter, mixed)  : 2,657")
        print(f"  {winner_id} (this — exclusion)       : {winner_count:,}")
        print()
        print("If this number is ~1,500-2,000, the exclusion filter cleanly")
        print("captures retail-only cart abandoners. Use it for GAds CM.")
    else:
        print("No exclusion operator accepted by API.")
        print("Recommendation: keep VrP6TT at 620 for Google Ads use.")


if __name__ == "__main__":
    main()

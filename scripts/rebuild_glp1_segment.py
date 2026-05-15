#!/usr/bin/env python3
"""
Rebuild the GLP-1 segment with the COMPLETE Bargain Chemist catalog
of GLP-1 / weight-loss injectables — verified live from Shopify
on 2026-05-15.

Creates a new segment 'BC — GLP-1 Customers v2 (full catalog)'.
Does NOT touch the existing X2pdkD (24 profiles, undercounted).

NEVER sync this audience to Google Ads — prescription medication,
Google policy violation.

Run:
    KLAVIYO_API_KEY="pk_xxx" python3 scripts/rebuild_glp1_segment.py
"""

import os
import sys
import time
import requests

KLAVIYO_BASE = "https://a.klaviyo.com/api"
REVISION = "2024-10-15"
PLACED_ORDER = "Sxnb5T"

# Full GLP-1 catalog verified via Shopify MCP 2026-05-15
GLP1_PRODUCTS = [
    # Wegovy variants (7 SKUs)
    "Wegovy®(Pack of 4) orignal",   # DRAFT but historical orders may reference it
    "Wegovy FlexTouch Pen",
    "WEGOVY 0.25 MG FLEXTOUCH 1mg/1.5mL",
    "WEGOVY 0.5 MG FLEXTOUCH 2mg/1.5mL",
    "WEGOVY 1 MG FLEXTOUCH 4mg/3mL",
    "WEGOVY 1.7 MG FLEXTOUCH 6.8mg/3mL",
    "WEGOVY 2.4 MG FLEXTOUCH 9.6mg/3mL",
    # Mounjaro full titration (6 SKUs)
    "Mounjaro 2.5mg Kwikpen",
    "Mounjaro 5mg Kwikpen",
    "Mounjaro 7.5mg Kwikpen",
    "Mounjaro 10mg Kwikpen",
    "Mounjaro 12.5mg Kwikpen",
    "Mounjaro 15mg Kwikpen",
    # Saxenda (1 SKU)
    "Saxenda Injection 15ml (5 x 3 ml) - Liraglutide 18 mg/3 ml",
]


SEGMENT = {
    "name": "BC — GLP-1 Customers v2 (full catalog)",
    "definition": {
        "condition_groups": [
            {
                "conditions": [
                    {
                        "type": "profile-metric",
                        "metric_id": PLACED_ORDER,
                        "measurement": "count",
                        "measurement_filter": {
                            "type": "numeric", "operator": "greater-than", "value": 0
                        },
                        "timeframe_filter": {
                            "type": "date", "operator": "in-the-last", "unit": "day", "quantity": 1095
                        },
                        "metric_filters": [
                            {
                                "property": "Items",
                                "filter": {
                                    "type": "list",
                                    "operator": "contains-any",
                                    "value": GLP1_PRODUCTS,
                                },
                            }
                        ],
                    }
                ]
            },
            {
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
            },
        ]
    },
}


def headers(api_key):
    return {
        "Authorization": f"Klaviyo-API-Key {api_key}",
        "accept": "application/vnd.api+json",
        "revision": REVISION,
        "content-type": "application/vnd.api+json",
    }


def main():
    api_key = os.environ.get("KLAVIYO_API_KEY")
    if not api_key:
        print("ERROR: KLAVIYO_API_KEY env var not set", file=sys.stderr)
        sys.exit(1)

    body = {"data": {"type": "segment", "attributes": SEGMENT}}
    r = requests.post(f"{KLAVIYO_BASE}/segments/", headers=headers(api_key), json=body, timeout=30)

    if r.status_code not in (200, 201):
        print(f"FAILED ({r.status_code}): {r.text[:1000]}")
        sys.exit(1)

    new_id = r.json()["data"]["id"]
    print(f"Created GLP-1 v2 segment: {new_id}")
    print(f"Filter targets {len(GLP1_PRODUCTS)} product names (full catalog).")
    print()
    print("Polling profile count (Klaviyo computes segments async)...")

    count = None
    for attempt in range(15):
        time.sleep(3)
        url = f"{KLAVIYO_BASE}/segments/{new_id}/?additional-fields[segment]=profile_count"
        r2 = requests.get(url, headers=headers(api_key), timeout=30)
        if r2.status_code != 200:
            print(f"  GET failed: {r2.status_code}")
            continue
        attrs = r2.json()["data"]["attributes"]
        if not attrs.get("is_processing") and attrs.get("profile_count") is not None:
            count = attrs["profile_count"]
            break
        print(f"  ...still processing (attempt {attempt + 1}/15)")

    print()
    print(f"=== RESULT ===")
    print(f"  Segment ID:  {new_id}")
    print(f"  Profile count: {count if count is not None else 'TIMEOUT'}")
    print(f"  Previous (X2pdkD) count: 24")
    if count is not None and count > 24:
        print(f"  Net additional GLP-1 customers found: +{count - 24}")
    print()
    print("REMINDER: This audience is for Klaviyo-only flows (post-purchase, refill")
    print("reminders, dose-titration education). NEVER sync to Google Ads — Rx policy.")


if __name__ == "__main__":
    main()

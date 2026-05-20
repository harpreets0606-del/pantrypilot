#!/usr/bin/env python3
"""
Find where Smart Sending state actually lives in Klaviyo's API for flow messages.

The previous verification script returned 'Smart Sending: None' because it
looked for send_options.use_smart_sending — but that field isn't present
in the responses my script received. The Klaviyo UI clearly shows the
'Skip recently emailed profiles' toggle, so the data must be somewhere
in the API.

This script targets ONE known flow message (Search Abandonment V4 Email #1,
which the user confirmed shows the Smart Sending toggle in the UI) and:

1. Hits multiple Klaviyo endpoints and parameter variations
2. Recursively scans the full JSON response for any field that mentions
   'smart', 'skip', 'send option', etc.
3. Reports the exact JSON path where Smart Sending state lives

Once we know the path, the main verification script can be updated.

Run:
    KLAVIYO_API_KEY="pk_xxx" python3 scripts/probe_smart_sending.py
"""

import json
import os
import re
import sys

import requests

KLAVIYO_BASE = "https://a.klaviyo.com/api"
REVISIONS_TO_TRY = ["2024-10-15", "2024-07-15", "2024-05-15", "2023-10-15"]

# Search Abandonment V4 — the flow the user confirmed shows Smart Sending in UI
TARGET_FLOW_ID = "XbQiKg"
TARGET_ACTION_ID = "105487706"   # SEND_EMAIL action wrapping Email #1
TARGET_MESSAGE_ID = "RbxBBc"     # Flow message ID for Email #1


def headers(api_key, revision):
    return {
        "Authorization": f"Klaviyo-API-Key {api_key}",
        "accept": "application/vnd.api+json",
        "revision": revision,
    }


def fetch(url, api_key, revision):
    try:
        r = requests.get(url, headers=headers(api_key, revision), timeout=30)
        return r.status_code, r.text
    except Exception as e:
        return None, f"REQUEST ERROR: {e}"


def find_in_json(obj, pattern, path=""):
    """Walk the JSON tree and return every (path, value) where the key matches the pattern."""
    matches = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            current = f"{path}.{k}" if path else k
            if pattern.search(str(k)):
                matches.append((current, v))
            matches.extend(find_in_json(v, pattern, current))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            matches.extend(find_in_json(item, pattern, f"{path}[{i}]"))
    return matches


def short_value(v):
    if isinstance(v, (str, int, float, bool, type(None))):
        return repr(v)
    s = json.dumps(v)
    return s if len(s) <= 200 else s[:197] + "..."


def main():
    api_key = os.environ.get("KLAVIYO_API_KEY")
    if not api_key:
        print("ERROR: KLAVIYO_API_KEY env var not set", file=sys.stderr)
        sys.exit(1)

    # Match anything containing smart, skip-recent, send_option, use_smart, or
    # the actual UI label fragments
    pattern = re.compile(
        r"smart|skip[_-]?recent|send[_-]?option|use[_-]?smart",
        re.IGNORECASE,
    )

    endpoints = [
        ("Flow-message detail (default fields)",
         f"/flow-messages/{TARGET_MESSAGE_ID}/"),
        ("Flow-message detail (request send_options explicitly)",
         f"/flow-messages/{TARGET_MESSAGE_ID}/?additional-fields[flow-message]=send_options"),
        ("Flow-message detail (request many fields)",
         f"/flow-messages/{TARGET_MESSAGE_ID}/?fields[flow-message]=name,definition,send_options,send_strategy,send_filters,tracking_options,created,updated"),
        ("Flow-action detail (default)",
         f"/flow-actions/{TARGET_ACTION_ID}/"),
        ("Flow-action detail (with included flow-messages)",
         f"/flow-actions/{TARGET_ACTION_ID}/?include=flow-messages"),
        ("Flow with included flow-actions",
         f"/flows/{TARGET_FLOW_ID}/?include=flow-actions"),
        ("Flow-action with explicit settings field request",
         f"/flow-actions/{TARGET_ACTION_ID}/?additional-fields[flow-action]=settings"),
    ]

    for revision in REVISIONS_TO_TRY:
        print(f"\n{'#' * 78}")
        print(f"# REVISION {revision}")
        print('#' * 78)

        for label, endpoint in endpoints:
            url = f"{KLAVIYO_BASE}{endpoint}"
            print(f"\n--- {label} ---")
            print(f"    URL: {endpoint}")
            status, body = fetch(url, api_key, revision)
            print(f"    Status: {status}")

            if status != 200:
                preview = body[:250] if body else "no body"
                print(f"    Body preview: {preview}")
                continue

            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                print(f"    Body (non-JSON, first 200 chars): {body[:200]}")
                continue

            # Show top-level attribute keys for context (so we can see the shape)
            try:
                data_obj = data.get("data")
                if isinstance(data_obj, dict):
                    attr_keys = list((data_obj.get("attributes") or {}).keys())
                    if attr_keys:
                        print(f"    attribute keys: {attr_keys[:25]}")
                elif isinstance(data_obj, list) and data_obj:
                    first = data_obj[0]
                    if isinstance(first, dict):
                        attr_keys = list((first.get("attributes") or {}).keys())
                        if attr_keys:
                            print(f"    first-item attribute keys: {attr_keys[:25]}")
            except Exception:
                pass

            # Also show included-resource types if present
            if "included" in data and isinstance(data["included"], list):
                inc_types = sorted({item.get("type") for item in data["included"] if isinstance(item, dict)})
                if inc_types:
                    print(f"    included types: {inc_types}")

            # Recursive search for Smart Sending-related fields
            matches = find_in_json(data, pattern)
            if matches:
                print(f"    >>> FOUND {len(matches)} matching field(s):")
                for path, value in matches:
                    print(f"        {path} = {short_value(value)}")
            else:
                print(f"    (no field name matched the smart/skip/send_option pattern)")


if __name__ == "__main__":
    main()

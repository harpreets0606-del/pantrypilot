#!/usr/bin/env python3
"""
Probe Klaviyo's API to find:
  1. Where BOOLEAN_BRANCH filter criteria live (e.g., "did the customer buy
     Vitamins?" inside a Replenishment branch)
  2. Where flow-level profile filters / cross-flow exclusions live

The previous flow audit returned only `{"is_joined": false}` for every
boolean branch, which is a generic flag (not the actual condition). The
real filter logic must live somewhere in the API; this probe finds where.

Strategy: target the Replenishment flow (Ua5LdS) which has 10 boolean
branches, and target one specific BOOLEAN_BRANCH action. Dump full JSON
from many endpoints, search recursively for any field that could contain
filter criteria.

Run:
    KLAVIYO_API_KEY="pk_xxx" python3 scripts/probe_branch_and_filters.py
"""

import json
import os
import re
import sys

import requests

KLAVIYO_BASE = "https://a.klaviyo.com/api"
REVISIONS_TO_TRY = ["2024-10-15", "2024-07-15", "2024-05-15"]

# Replenishment flow has 10 boolean branches; pick the first one for probing
TARGET_FLOW_ID = "Ua5LdS"
TARGET_BRANCH_ACTION_ID = "105926045"  # First BOOLEAN_BRANCH in Replenishment


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
    """Walk a JSON object recursively, return list of (path, value)
    for every key matching the pattern."""
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
    return s if len(s) <= 300 else s[:297] + "..."


def main():
    api_key = os.environ.get("KLAVIYO_API_KEY")
    if not api_key:
        print("ERROR: KLAVIYO_API_KEY env var not set", file=sys.stderr)
        sys.exit(1)

    # Patterns that might indicate filter / condition logic
    filter_pattern = re.compile(
        r"filter|condit|criteria|branch|profile_filter|trigger_filter|"
        r"definition|rule|predicate|expression",
        re.IGNORECASE,
    )

    endpoints = [
        # Flow-level: trigger / profile filters
        ("Flow default (Replenishment)",
         f"/flows/{TARGET_FLOW_ID}/"),
        ("Flow with all default + relationships",
         f"/flows/{TARGET_FLOW_ID}/?include=flow-actions,tags"),
        ("Flow trying to request definition field",
         f"/flows/{TARGET_FLOW_ID}/?fields[flow]=name,status,trigger_type,trigger_filters,profile_filters,definition"),
        ("Flow trying additional-fields=definition",
         f"/flows/{TARGET_FLOW_ID}/?additional-fields[flow]=definition"),

        # Action-level: branch filter criteria
        ("Boolean-branch action default",
         f"/flow-actions/{TARGET_BRANCH_ACTION_ID}/"),
        ("Boolean-branch action requesting many fields",
         f"/flow-actions/{TARGET_BRANCH_ACTION_ID}/?fields[flow-action]=action_type,settings,filters,condition,criteria,profile_filters,definition,status,created,updated"),

        # Filters as relationships
        ("Boolean-branch with all relationships",
         f"/flow-actions/{TARGET_BRANCH_ACTION_ID}/?include=flow-messages,filters"),
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
                preview = body[:280] if body else "no body"
                print(f"    Body preview: {preview}")
                continue

            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                print(f"    Body (non-JSON, first 200 chars): {body[:200]}")
                continue

            # Show top-level attribute keys for context
            data_obj = data.get("data")
            if isinstance(data_obj, dict):
                attr_keys = list((data_obj.get("attributes") or {}).keys())
                rel_keys = list((data_obj.get("relationships") or {}).keys())
                if attr_keys:
                    print(f"    data.attributes keys: {attr_keys[:20]}")
                if rel_keys:
                    print(f"    data.relationships keys: {rel_keys[:15]}")

            # Note included resources by type
            if "included" in data and isinstance(data["included"], list):
                inc_types = sorted({
                    item.get("type")
                    for item in data["included"]
                    if isinstance(item, dict)
                })
                if inc_types:
                    print(f"    included types: {inc_types}")

            # Recursive search for filter-like keys
            matches = find_in_json(data, filter_pattern)
            # Dedupe: same key path with same value
            seen = set()
            unique = []
            for p, v in matches:
                k = (p, json.dumps(v)[:200] if not isinstance(v, (str, int, bool, type(None))) else v)
                if k in seen:
                    continue
                seen.add(k)
                unique.append((p, v))

            if unique:
                print(f"    >>> FOUND {len(unique)} matching field(s):")
                for path, value in unique[:25]:  # cap output
                    print(f"        {path} = {short_value(value)}")
                if len(unique) > 25:
                    print(f"        ... and {len(unique) - 25} more")
            else:
                print(f"    (no field name matched the filter/condition/branch pattern)")


if __name__ == "__main__":
    main()

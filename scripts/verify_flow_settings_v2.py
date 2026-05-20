#!/usr/bin/env python3
"""
Verify flow settings v2 — uses the CORRECT Klaviyo API path for Smart Sending.

Previous script (verify_flow_settings.py) looked at /flow-messages/{id}/ for
send_options.use_smart_sending. That endpoint doesn't expose those fields.

The probe (probe_smart_sending.py) found that Smart Sending state lives on
the FLOW-ACTION, not the flow-message:
    /flow-actions/{id}/ → data.attributes.send_options.use_smart_sending

This script walks every action in every manual flow and produces an accurate
audit: timing, action types, Smart Sending state.

Run:
    KLAVIYO_API_KEY="pk_xxx" python3 scripts/verify_flow_settings_v2.py
"""

import json
import os
import sys

import requests

KLAVIYO_BASE = "https://a.klaviyo.com/api"
REVISION = "2024-10-15"

MANUAL_FLOWS = [
    ("RDJQYM", "[Z] Post-Purchase Series"),
    ("RPQXaa", "[Z] Added to Cart Abandonment"),
    ("RtiVC5", "[Z] Browse Abandonment"),
    ("Sr3hxz", "[Z] Abandoned Checkout v3"),
    ("T7pmf6", "[Z] Win-back - Lapsed Customers"),
    ("Ua5LdS", "[Z] Replenishment - Category Based"),
    ("V9XmEm", "[Z] Flu Season - Winter Wellness"),
    ("XbQiKg", "[B] Search Abandonment V4"),
    ("YdejKf", "Welcome Series 2026 - No Coupon"),
    ("Ysj7sg", "[Z] Back in Stock"),
]


def headers(api_key):
    return {
        "Authorization": f"Klaviyo-API-Key {api_key}",
        "accept": "application/vnd.api+json",
        "revision": REVISION,
    }


def fetch(url, api_key):
    r = requests.get(url, headers=headers(api_key), timeout=30)
    if r.status_code != 200:
        return None, f"{r.status_code}: {r.text[:300]}"
    return r.json(), None


def human_delay(seconds):
    """Convert delay_seconds to a human-readable string."""
    if seconds is None:
        return "?"
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60} min"
    if seconds < 86400:
        hours = seconds / 3600
        return f"{int(hours)}h" if hours == int(hours) else f"{hours:.1f}h"
    days = seconds / 86400
    if days < 30:
        return f"{int(days)}d" if days == int(days) else f"{days:.1f}d"
    months = days / 30
    return f"~{int(months)} months ({int(days)}d)"


def main():
    api_key = os.environ.get("KLAVIYO_API_KEY")
    if not api_key:
        print("ERROR: KLAVIYO_API_KEY env var not set", file=sys.stderr)
        sys.exit(1)

    total_send_actions = 0
    smart_on = 0
    smart_off = 0
    smart_unknown = 0

    for flow_id, expected_name in MANUAL_FLOWS:
        print(f"\n{'=' * 78}")
        print(f"FLOW: {flow_id}  —  {expected_name}")
        print('=' * 78)

        # Step 1: Get the ordered list of actions in this flow
        list_resp, err = fetch(f"{KLAVIYO_BASE}/flows/{flow_id}/flow-actions/", api_key)
        if err:
            print(f"  ERROR getting actions list: {err}")
            continue

        actions = list_resp.get("data", [])
        print(f"  Status: {list_resp.get('data', [{}])[0].get('attributes', {}).get('status', '?') if actions else '?'}")
        print(f"  Total actions: {len(actions)}")
        print()

        for idx, action in enumerate(actions, 1):
            action_id = action["id"]
            attrs = action.get("attributes", {})
            atype = attrs.get("action_type") or attrs.get("type", "?")

            line = f"  [{idx}] {atype:18s} id={action_id}"

            if atype == "TIME_DELAY":
                settings = attrs.get("settings", {})
                delay = settings.get("delay_seconds")
                print(f"{line}  delay={human_delay(delay)}")
            elif atype == "BOOLEAN_BRANCH":
                print(f"{line}  (conditional split)")
            elif atype in ("SEND_EMAIL", "SEND_MESSAGE"):
                # Need to fetch action detail for send_options
                detail_resp, derr = fetch(
                    f"{KLAVIYO_BASE}/flow-actions/{action_id}/", api_key
                )
                if derr:
                    print(f"{line}  ERROR: {derr}")
                    smart_unknown += 1
                    total_send_actions += 1
                    continue

                d_attrs = detail_resp.get("data", {}).get("attributes", {})
                send_options = d_attrs.get("send_options") or {}
                use_smart = (
                    send_options.get("use_smart_sending")
                    if isinstance(send_options, dict)
                    else None
                )
                is_transactional = (
                    send_options.get("is_transactional")
                    if isinstance(send_options, dict)
                    else None
                )

                # Also pull the message name for context
                msgs_resp, _ = fetch(
                    f"{KLAVIYO_BASE}/flow-actions/{action_id}/flow-messages/",
                    api_key,
                )
                msg_name = "?"
                if msgs_resp:
                    msgs = msgs_resp.get("data", [])
                    if msgs:
                        msg_name = msgs[0].get("attributes", {}).get("name", "?")

                smart_str = "ON " if use_smart else ("OFF" if use_smart is False else "?")
                trans_str = " (transactional)" if is_transactional else ""

                print(f"{line}  Smart Sending: {smart_str}{trans_str}")
                print(f"       message: {msg_name}")

                total_send_actions += 1
                if use_smart is True:
                    smart_on += 1
                elif use_smart is False:
                    smart_off += 1
                else:
                    smart_unknown += 1
            else:
                print(f"{line}  (unknown type)")

    print(f"\n{'=' * 78}")
    print("SMART SENDING AUDIT SUMMARY")
    print('=' * 78)
    print(f"  Total SEND_EMAIL actions:    {total_send_actions}")
    print(f"  Smart Sending ON:            {smart_on}")
    print(f"  Smart Sending OFF:           {smart_off}")
    print(f"  Smart Sending unknown/null:  {smart_unknown}")


if __name__ == "__main__":
    main()

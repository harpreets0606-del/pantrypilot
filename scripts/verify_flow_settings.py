#!/usr/bin/env python3
"""
Verify the 4 unverified claims from the marketing-head reply by querying
Klaviyo's REST API for full flow + action + message detail.

For each of the 10 manual flows, this script reports:
  1. Trigger type and trigger filter (entry criteria)
  2. Profile filters (cross-flow / cross-flow-message exclusions)
  3. Every action in order, including:
     - TIME_DELAY: actual delay value (hours/days/minutes)
     - SEND_EMAIL: message name + whether Smart Sending is enabled
     - BOOLEAN_BRANCH / CONDITIONAL_SPLIT: branch criteria

This answers:
  - Is Smart Sending enabled on each flow message?
  - What's the actual time delay before Abandoned Checkout Email #1?
  - Does Win-back trigger on the right "lapsed" criteria?
  - Are there cross-flow exclusion filters between abandonment flows?
  - What's the action order in Post-Purchase (is there a gap where Email 1 was)?

Run:
    KLAVIYO_API_KEY="pk_xxx" python3 scripts/verify_flow_settings.py
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


def get_any(d, *keys, default=None):
    """Try multiple key names (snake / camel) and return the first match."""
    for k in keys:
        if k in d:
            return d[k]
    return default


def summarise_settings(action_type, attrs):
    """Pull a human-readable summary of a flow action's settings."""
    settings = get_any(attrs, "settings", "value", default={}) or {}
    if not isinstance(settings, dict):
        return str(settings)[:300]

    if action_type in {"TIME_DELAY", "time-delay", "delay"}:
        # Try common shape: { value: N, unit: 'hours' } or { delay_value, delay_units }
        value = get_any(settings, "value", "delay_value", "delayValue")
        unit = get_any(settings, "unit", "delay_units", "delayUnits", "units")
        if value is not None and unit:
            return f"{value} {unit}"
        # Fallback: try common Klaviyo shape with seconds/minutes/hours/days
        for u in ("seconds", "minutes", "hours", "days"):
            if u in settings:
                return f"{settings[u]} {u}"
        return f"settings={json.dumps(settings)[:200]}"

    if action_type in {"BOOLEAN_BRANCH", "conditional-branch", "boolean-branch"}:
        filt = get_any(settings, "filters", "filter", "condition", "criteria")
        if filt:
            return f"branch_filter={json.dumps(filt)[:400]}"
        return f"settings={json.dumps(settings)[:300]}"

    return json.dumps(settings)[:300]


def main():
    api_key = os.environ.get("KLAVIYO_API_KEY")
    if not api_key:
        print("ERROR: KLAVIYO_API_KEY env var not set", file=sys.stderr)
        sys.exit(1)

    for flow_id, expected_name in MANUAL_FLOWS:
        print(f"\n{'=' * 78}")
        print(f"FLOW: {flow_id}  —  {expected_name}")
        print('=' * 78)

        # 1) Flow metadata + trigger/profile filters if exposed
        flow_resp, err = fetch(f"{KLAVIYO_BASE}/flows/{flow_id}/", api_key)
        if err:
            print(f"  ERROR getting flow: {err}")
            continue

        attrs = flow_resp["data"]["attributes"]
        print(f"  Status:         {attrs.get('status')}")
        print(f"  Trigger type:   {get_any(attrs, 'trigger_type', 'triggerType')}")

        # Filter-related fields can live under various keys
        for key in ("trigger_filters", "triggerFilters", "profile_filters",
                    "profileFilters", "definition"):
            val = attrs.get(key)
            if val:
                preview = json.dumps(val)[:500]
                print(f"  {key}: {preview}")

        # 2) Pull all actions for this flow
        actions_resp, err = fetch(
            f"{KLAVIYO_BASE}/flows/{flow_id}/flow-actions/", api_key
        )
        if err:
            print(f"  ERROR getting actions: {err}")
            continue

        actions = actions_resp.get("data", [])
        print(f"\n  ACTIONS IN FLOW (total {len(actions)}):")

        for idx, action in enumerate(actions, 1):
            action_id = action["id"]
            a_attrs = action.get("attributes", {})
            action_type = get_any(a_attrs, "action_type", "actionType", "type", default="?")

            print(f"\n  [{idx}] action_id={action_id}  type={action_type}")

            # Print key configuration based on type
            summary = summarise_settings(action_type, a_attrs)
            if summary:
                print(f"      Config: {summary}")

            # SEND_EMAIL: dig further to get message + Smart Sending
            if action_type.upper() in {"SEND_EMAIL", "SEND-EMAIL", "SEND_MESSAGE"}:
                msgs_resp, m_err = fetch(
                    f"{KLAVIYO_BASE}/flow-actions/{action_id}/flow-messages/",
                    api_key,
                )
                if m_err:
                    print(f"      ERROR getting messages: {m_err}")
                    continue
                msgs = msgs_resp.get("data", [])
                for msg in msgs:
                    msg_id = msg["id"]
                    m_attrs = msg.get("attributes", {})
                    msg_name = m_attrs.get("name", "?")
                    channel = (
                        m_attrs.get("definition", {}).get("channel")
                        if isinstance(m_attrs.get("definition"), dict)
                        else None
                    )

                    # Inspect send_options for Smart Sending
                    send_options = get_any(m_attrs, "send_options", "sendOptions", default={}) or {}
                    use_smart = get_any(
                        send_options,
                        "use_smart_sending",
                        "useSmartSending",
                        default=None,
                    ) if isinstance(send_options, dict) else None

                    # Fall back: fetch the individual flow-message for fuller detail
                    if use_smart is None:
                        msg_detail, md_err = fetch(
                            f"{KLAVIYO_BASE}/flow-messages/{msg_id}/", api_key
                        )
                        if msg_detail and not md_err:
                            md_attrs = msg_detail["data"]["attributes"]
                            d_so = get_any(md_attrs, "send_options", "sendOptions", default={}) or {}
                            use_smart = get_any(
                                d_so, "use_smart_sending", "useSmartSending", default=None
                            )
                            # Also surface any per-message filters
                            msg_filters = get_any(
                                md_attrs, "send_filters", "sendFilters",
                                "filters", "profile_filters", default=None,
                            )
                            if msg_filters:
                                print(f"      Msg filters: {json.dumps(msg_filters)[:400]}")

                    print(f"      Message:        {msg_name}  (id={msg_id}, channel={channel})")
                    print(f"      Smart Sending:  {use_smart}")


if __name__ == "__main__":
    main()
